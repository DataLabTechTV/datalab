import asyncio
import random
from contextlib import asynccontextmanager
from uuid import uuid4

import mlflow
import pandas as pd
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from loguru import logger as log
from mlflow.exceptions import RestException

from ml.events import (
    flush_inference_buffer,
    inference_consumer_loop,
    make_inference_producer,
    send_inference,
)
from ml.types import InferenceModel, InferenceRequest, InferenceResult

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


@app.get("/inference/logs/flush")
async def inference_logs_flush():
    log.info("Flushing inference logs for schemas: {}", ", ".join(SCHEMAS))
    for schema in SCHEMAS:
        flush_inference_buffer(schema)


@app.post("/inference")
async def inference(inference_request: InferenceRequest, request: Request):
    if type(inference_request.models) is InferenceModel:
        model = inference_request.models
    else:
        model = random.choice(inference_request.models)

    model_uri = f"models:/{model.name}/{model.version}"

    if model_uri not in models:
        try:
            models[model_uri] = mlflow.pyfunc.load_model(model_uri)
        except RestException:
            return JSONResponse(
                {"error": "Model not found"},
                status_code=status.HTTP_404_NOT_FOUND,
            )

    log.info("Running inference using {}", model_uri)

    dataset = pd.DataFrame(
        inference_request.dataset.data,
        columns=inference_request.dataset.columns,
    )
    predictions = models[model_uri].predict(dataset)

    inference_result = InferenceResult(
        inference_uuid=uuid4(),
        model_name=model.name,
        model_version=model.version,
        dataset=inference_request.dataset,
        predictions=predictions,
    )

    if inference_request.log_to_lakehouse:
        log.info("Logging inference to data lakehouse")
        send_inference(request.app.state.inference_producer, inference_result)

    return inference_result
