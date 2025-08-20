import asyncio
import random
from contextlib import asynccontextmanager
from uuid import uuid4

import mlflow
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from loguru import logger as log
from mlflow.exceptions import RestException

from ml.events import (
    flush_inference_insert_queue,
    flush_inference_update_queue,
    inference_insert_consumer_loop,
    inference_update_consumer_loop,
    make_inference_producer,
    queue_inference_insertion,
    queue_inference_update,
)
from ml.types import (
    InferenceFeedback,
    InferenceModel,
    InferenceProducerType,
    InferenceRequest,
    InferenceResult,
)

SCHEMAS = ("dd",)
models = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Starting Kafka producers and consumers")

    inference_result_producer = await make_inference_producer(
        InferenceProducerType.INSERT
    )

    inference_feedback_producer = await make_inference_producer(
        InferenceProducerType.UPDATE
    )

    await inference_result_producer.start()
    await inference_feedback_producer.start()

    inference_insert_consumer_tasks = []
    inference_update_consumer_tasks = []

    for i, schema in enumerate(SCHEMAS):
        inference_insert_consumer_tasks.append(
            asyncio.create_task(
                inference_insert_consumer_loop(schema),
                name=f"inference_insert_consumer_loop_{i}",
            )
        )

        inference_update_consumer_tasks.append(
            asyncio.create_task(
                inference_update_consumer_loop(schema),
                name=f"inference_update_consumer_loop_{i}",
            )
        )

    app.state.inference_result_producer = inference_result_producer
    app.state.inference_feedback_producer = inference_feedback_producer

    yield

    log.info("Stopping Kafka producers and consumers")

    for consumer_task in inference_insert_consumer_tasks:
        consumer_task.cancel()
        await consumer_task

    for consumer_task in inference_update_consumer_tasks:
        consumer_task.cancel()
        await consumer_task

    await inference_result_producer.stop()
    await inference_feedback_producer.stop()


app = FastAPI(lifespan=lifespan)


@app.get("/inference/logs/flush")
async def inference_logs_flush():
    log.info("Flushing inference queues for schemas: {}", ", ".join(SCHEMAS))

    for schema in SCHEMAS:
        await flush_inference_insert_queue(schema)
        await flush_inference_update_queue(schema)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post("/inference")
async def inference(inference_request: InferenceRequest, request: Request):
    if type(inference_request.models) is InferenceModel:
        inference_model = inference_request.models
    else:
        inference_model = random.choice(inference_request.models)

    model_uri = f"models:/{inference_model.name}/{inference_model.version}"

    if model_uri not in models:
        try:
            models[model_uri] = mlflow.sklearn.load_model(model_uri)
        except RestException:
            return JSONResponse(
                {"error": "Model not found"},
                status_code=status.HTTP_404_NOT_FOUND,
            )

    log.info("Running inference using {}", model_uri)

    data = inference_request.get_input()
    prediction = models[model_uri].predict_proba(data)[0, 0].item()

    inference_result = InferenceResult(
        inference_uuid=str(uuid4()),
        model=inference_model,
        data=inference_request.data,
        prediction=prediction,
    )

    if inference_request.log_to_lakehouse:
        log.info("Queuing inference result data lakehouse insertion")
        await queue_inference_insertion(
            request.app.state.inference_result_producer,
            inference_result,
        )

    return inference_result


@app.patch("/inference")
async def inference(inference_feedback: InferenceFeedback, request: Request):
    log.info("Queuing inference result data lakehouse insertion")

    await queue_inference_update(
        request.app.state.inference_feedback_producer,
        inference_feedback,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
