import asyncio
import json
from dataclasses import asdict
from datetime import timedelta
from enum import Enum

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from loguru import logger as log

from ml.types import InferenceFeedback, InferenceProducerType, InferenceResult
from shared.lakehouse import Lakehouse
from shared.settings import env

# Kafka configuration
# ===================

KAFKA_BROKER_ENDPOINT = env.str("KAFKA_BROKER_ENDPOINT")
INFERENCE_RESULTS_TOPIC = "ml_inference_results"
INFERENCE_FEEDBACK_TOPIC = "ml_inference_feedback"
BATCH_SIZE = 1000
FLUSH_INTERVAL = timedelta(minutes=15)


# Producers
# =========


async def make_inference_producer(type_: InferenceProducerType) -> AIOKafkaProducer:
    match type_:
        case InferenceProducerType.RESULT:
            producer = AIOKafkaProducer(
                bootstrap_servers=KAFKA_BROKER_ENDPOINT,
                client_id="ml-inference-result-producer",
            )
        case InferenceProducerType.FEEDBACK:
            producer = AIOKafkaProducer(
                bootstrap_servers=KAFKA_BROKER_ENDPOINT,
                client_id="ml-inference-feedback-producer",
            )

    return producer


async def queue_inference_result(
    producer: AIOKafkaProducer,
    inference_result: InferenceResult,
):
    try:
        await producer.send_and_wait(
            INFERENCE_RESULTS_TOPIC,
            key=inference_result.inference_uuid.encode("utf-8"),
            value=json.dumps(asdict(inference_result)).encode("utf-8"),
        )
        log.info("Successfully delivered inference result")
    except Exception as e:
        log.error(f"Delivery failed for inference result: {e}")


async def queue_inference_feedback(
    producer: AIOKafkaProducer,
    inference_feedback: InferenceFeedback,
):
    try:
        await producer.send_and_wait(
            INFERENCE_FEEDBACK_TOPIC,
            key=inference_feedback.inference_uuid.encode("utf-8"),
            value=json.dumps(asdict(inference_feedback)).encode("utf-8"),
        )
        log.info("Successfully delivered inference feedback")
    except Exception as e:
        log.error(f"Delivery failed for inference feedback: {e}")


# Consumers
# =========

lakehouse = Lakehouse(in_memory=True)
inference_result_queue = asyncio.Queue(maxsize=BATCH_SIZE)
inference_feedback_queue = asyncio.Queue(maxsize=BATCH_SIZE)
inference_result_last_flush = asyncio.get_event_loop().time()
inference_feedback_last_flush = asyncio.get_event_loop().time()


async def flush_inference_result_queue(schema: str):
    global lakehouse

    inference_results = []

    while not inference_result_queue.empty():
        inference_results.append(inference_result_queue.get_nowait())

    if len(inference_results) > 0:
        lakehouse.ml_inference_insert_results(schema, inference_results)


async def flush_inference_feedback_queue(schema: str):
    global lakehouse

    inference_feedback = []

    while not inference_feedback_queue.empty():
        inference_feedback.append(inference_feedback_queue.get_nowait())

    if len(inference_feedback) > 0:
        lakehouse.ml_inference_append_feedback(schema, inference_feedback)


async def inference_result_consumer_loop(schema: str):
    global inference_result_last_flush

    consumer = AIOKafkaConsumer(
        INFERENCE_RESULTS_TOPIC,
        bootstrap_servers=KAFKA_BROKER_ENDPOINT,
        group_id="lakehouse-inference-result-consumer",
        auto_offset_reset="earliest",
    )

    await consumer.start()

    try:
        async for msg in consumer:
            payload = json.loads(msg.value.decode("utf-8"))
            await inference_result_queue.put(InferenceResult.from_dict(payload))

            now = asyncio.get_event_loop().time()
            if (
                inference_result_queue.full()
                or (now - inference_result_last_flush) >= FLUSH_INTERVAL.total_seconds()
            ):
                await flush_inference_result_queue(schema)
                inference_result_last_flush = now
    except asyncio.exceptions.CancelledError:
        log.info("Inference consumer loop cancelled")
    finally:
        await flush_inference_result_queue(schema)
        await consumer.stop()


async def inference_feedback_consumer_loop(schema: str):
    global inference_feedback_last_flush

    consumer = AIOKafkaConsumer(
        INFERENCE_FEEDBACK_TOPIC,
        bootstrap_servers=KAFKA_BROKER_ENDPOINT,
        group_id="lakehouse-inference-feedback-consumer",
        auto_offset_reset="earliest",
    )

    await consumer.start()

    try:
        async for msg in consumer:
            payload = json.loads(msg.value.decode("utf-8"))
            await inference_feedback_queue.put(InferenceFeedback(**payload))

            now = asyncio.get_event_loop().time()
            if (
                inference_feedback_queue.full()
                or (now - inference_feedback_last_flush)
                >= FLUSH_INTERVAL.total_seconds()
            ):
                await flush_inference_feedback_queue(schema)
                inference_feedback_last_flush = now
    except asyncio.exceptions.CancelledError:
        log.info("Inference consumer loop cancelled")
    finally:
        await flush_inference_feedback_queue(schema)
        await consumer.stop()
