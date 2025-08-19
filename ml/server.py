import asyncio
from contextlib import asynccontextmanager
from uuid import uuid4

import mlflow
import pandas as pd
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from loguru import logger as log
from mlflow.exceptions import RestException

from ml.events import inference_consumer_loop, make_inference_producer, send_inference
from ml.payloads import InferenceDataset, InferenceResultPayload

SCHEMAS = ("dd",)
models = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Starting Kafka producers and consumers")

    inference_producer = await make_inference_producer()
    await inference_producer.start()

    consumer_tasks = []

    for i, schema in enumerate(SCHEMAS):
        consumer_tasks.append(
            asyncio.create_task(
                inference_consumer_loop(schema),
                name=f"inference_consumer_loop_{i}",
            )
        )

    app.state.inference_producer = inference_producer

    yield

    log.info("Stopping Kafka producers and consumers")

    for consumer_task in consumer_tasks:
        consumer_task.cancel()
        await consumer_task

    await inference_producer.stop()


app = FastAPI(lifespan=lifespan)


@app.post("/inference/{model_name}/{model_version}")
async def predict(
    model_name: str,
    model_version: str,
    dataset: InferenceDataset,
    request: Request,
):
    model_uri = f"models:/{model_name}/{model_version}"

    if model_uri not in models:
        try:
            models[model_uri] = mlflow.pyfunc.load_model(model_uri)
        except RestException as e:
            return JSONResponse(
                {"error": "Model not found"},
                status_code=status.HTTP_404_NOT_FOUND,
            )

    data = pd.DataFrame(dataset.data, columns=dataset.columns)
    predictions = models[model_uri].predict(data)

    payload = InferenceResultPayload(
        inference_uuid=uuid4(),
        model_name=model_name,
        model_version=model_version,
        dataset=dataset,
        predictions=predictions,
    )

    send_inference(request.app.state.inference_producer, payload)

    return payload


# TODO: A/B testing request
