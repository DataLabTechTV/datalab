import asyncio
import tomllib
from contextlib import asynccontextmanager

import requests
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from loguru import logger as log

from ml.events import (
    flush_inference_feedback_queue,
    flush_inference_result_queue,
    inference_feedback_consumer_loop,
    inference_result_consumer_loop,
    make_inference_producer,
    queue_inference_feedback,
    queue_inference_result,
)
from ml.inference import ModelNotFound, predict
from ml.types import InferenceFeedback, InferenceProducerType, InferenceRequest

SERVER_NAME = "datalab-mlserver"
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8000

SCHEMAS = ("dd",)
models = {}


def server_is_healthy(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> bool:
    uri = f"http://{host}:{port}/health"
    response = requests.get(uri, timeout=15)

    try:
        response.raise_for_status()
        payload = response.json()
        return payload.get("name") == SERVER_NAME
    except:
        log.error("Server is down: {}", uri)
        return False


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Starting Kafka producers and consumers")

    inference_result_producer = await make_inference_producer(
        InferenceProducerType.RESULT
    )

    inference_feedback_producer = await make_inference_producer(
        InferenceProducerType.FEEDBACK
    )

    await inference_result_producer.start()
    await inference_feedback_producer.start()

    inference_result_consumer_tasks = []
    inference_feedback_consumer_tasks = []

    for i, schema in enumerate(SCHEMAS):
        inference_result_consumer_tasks.append(
            asyncio.create_task(
                inference_result_consumer_loop(schema),
                name=f"inference_result_consumer_loop_{i}",
            )
        )

        inference_feedback_consumer_tasks.append(
            asyncio.create_task(
                inference_feedback_consumer_loop(schema),
                name=f"inference_feedback_consumer_loop_{i}",
            )
        )

    app.state.inference_result_producer = inference_result_producer
    app.state.inference_feedback_producer = inference_feedback_producer

    yield

    log.info("Stopping Kafka producers and consumers")

    for consumer_task in inference_result_consumer_tasks:
        consumer_task.cancel()
        await consumer_task

    for consumer_task in inference_feedback_consumer_tasks:
        consumer_task.cancel()
        await consumer_task

    await inference_result_producer.stop()
    await inference_feedback_producer.stop()


app = FastAPI(
    lifespan=lifespan,
    swagger_ui_parameters=dict(tryItOutEnabled=True),
)


@app.get("/health")
async def health_check():
    payload = dict(name=SERVER_NAME)

    pyproject = tomllib.load(open("pyproject.toml", "rb"))
    version = pyproject.get("project", {}).get("version")

    if version is not None:
        payload["version"] = version

    return JSONResponse(payload, status_code=status.HTTP_200_OK)


@app.get("/inference/logs/flush")
async def inference_logs_flush():
    log.info("Flushing inference queues for schemas: {}", ", ".join(SCHEMAS))

    for schema in SCHEMAS:
        await flush_inference_result_queue(schema)
        await flush_inference_feedback_queue(schema)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post("/inference")
async def inference(inference_request: InferenceRequest, request: Request):
    try:
        inference_result = predict(inference_request)
    except ModelNotFound:
        return JSONResponse(
            {"error": "Model not found"},
            status_code=status.HTTP_404_NOT_FOUND,
        )

    if inference_request.log_to_lakehouse:
        log.info("Queuing lakehouse insertion for inference result")
        await queue_inference_result(
            request.app.state.inference_result_producer,
            inference_result,
        )

    return inference_result


@app.patch("/inference")
async def inference(inference_feedback: InferenceFeedback, request: Request):
    log.info("Queuing lakehouse append for inference feedback")

    await queue_inference_feedback(
        request.app.state.inference_feedback_producer,
        inference_feedback,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
