import asyncio
import json
from dataclasses import asdict

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from loguru import logger as log

from ml.types import InferenceResult
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


async def send_inference(producer: AIOKafkaProducer, inference_result: InferenceResult):
    try:
        await producer.send_and_wait(
            TOPIC,
            key=inference_result.inference_uuid.encode("utf-8"),
            value=json.dumps(asdict(inference_result)).encode("utf-8"),
        )
        log.info("Kafka: Successfully delivered inference result")
    except Exception as e:
        log.error(f"Kafka: Delivery failed for inference result: {e}")


# Consumers
# =========

lakehouse = None
queue = asyncio.Queue(maxsize=BATCH_SIZE)
last_flush = asyncio.get_event_loop().time()


async def flush_inference_buffer(schema: str):
    log.info(f"Kafka: Flushing {queue.qsize()} messages")

    if lakehouse is None:
        lakehouse = Lakehouse()

    inference_results = []

    while not queue.empty():
        inference_results.append(queue.get_nowait())

    if len(inference_results) > 0:
        lakehouse.log_inferences(schema, inference_results)


async def inference_consumer_loop(schema: str):
    consumer = AIOKafkaConsumer(
        TOPIC,
        bootstrap_servers=KAFKA_BROKER_ENDPOINT,
        group_id="lakehouse-inference-consumer",
        auto_offset_reset="earliest",
    )

    await consumer.start()

    try:
        async for msg in consumer:
            inference_result = InferenceResult(**json.loads(msg.value.decode("utf-8")))
            queue.put(inference_result)

            now = asyncio.get_event_loop().time()
            if queue.full() or (now - last_flush) >= FLUSH_INTERVAL_SEC:
                await flush_inference_buffer(schema)
                last_flush = now
    except asyncio.exceptions.CancelledError:
        log.info("Inference consumer loop cancelled")
    finally:
        await flush_inference_buffer(schema)
        await consumer.stop()
