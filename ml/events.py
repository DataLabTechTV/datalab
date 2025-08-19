import asyncio
import json
import time
from dataclasses import asdict

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from loguru import logger as log

from ml.payloads import InferenceResultPayload
from shared.lakehouse import Lakehouse
from shared.settings import env

# Kafka configuration
# ===================

KAFKA_BROKER_ENDPOINT = env.str("KAFKA_BROKER_ENDPOINT")
TOPIC = "ml_inference_results"
BATCH_SIZE = 100
FLUSH_INTERVAL_SEC = 5


# Producers
# =========


async def make_inference_producer() -> AIOKafkaProducer:
    inference_producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_BROKER_ENDPOINT,
        client_id="ml-inference-producer",
    )

    return inference_producer


async def send_inference(producer: AIOKafkaProducer, payload: InferenceResultPayload):
    try:
        await producer.send_and_wait(
            TOPIC,
            key=payload.inference_uuid.encode("utf-8"),
            value=json.dumps(asdict(payload)).encode("utf-8"),
        )
        log.info("Kafka: Successfully delivered inference result")
    except Exception as e:
        log.error(f"Kafka: Delivery failed for inference result: {e}")


# Consumers
# =========

lh = Lakehouse()


async def flush_inference_buffer(schema: str, queue: asyncio.Queue):
    log.info(f"Kafka: Flushing {queue.qsize()} messages")

    inference_results = []

    while not queue.empty():
        inference_results.append(queue.get_nowait())

    if len(inference_results) > 0:
        lh.log_inference(schema, inference_results)


async def inference_consumer_loop(schema: str):
    consumer = AIOKafkaConsumer(
        TOPIC,
        bootstrap_servers=KAFKA_BROKER_ENDPOINT,
        group_id="lakehouse-inference-consumer",
        auto_offset_reset="earliest",
    )

    await consumer.start()

    queue = asyncio.Queue(maxsize=BATCH_SIZE)
    last_flush = asyncio.get_event_loop().time()

    try:
        async for msg in consumer:
            payload = InferenceResultPayload(**json.loads(msg.value.decode("utf-8")))
            queue.put(payload)

            now = asyncio.get_event_loop().time()
            if queue.full() or (now - last_flush) >= FLUSH_INTERVAL_SEC:
                await flush_inference_buffer(schema, queue)
                last_flush = now
    except asyncio.exceptions.CancelledError:
        log.info("Inference consumer loop cancelled")
    finally:
        await flush_inference_buffer(schema, queue)
        await consumer.stop()
