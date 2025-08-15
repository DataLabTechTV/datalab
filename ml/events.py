import json
import random
import time

import duckdb
from confluent_kafka import Consumer, Producer
from loguru import logger as log

from shared.lakehouse import Lakehouse
from shared.settings import env

# -----------------------
# Kafka configuration
# -----------------------
KAFKA_BROKER_ENDPOINT = env.str("KAFKA_BROKER_ENDPOINT")
TOPIC = "ml_inference_results"

# -----------------------
# Producer
# -----------------------
producer_conf = {
    "bootstrap.servers": KAFKA_BROKER_ENDPOINT,
    "client.id": "ml-inference-producer",
}
producer = Producer(producer_conf)
MODELS = ["model_A", "model_B"]


def delivery_report(err, msg):
    if err:
        log.error("Delivery failed: {}", err)
    else:
        log.info(
            "Delivered message to {} [{}] offset {}",
            msg.topic(),
            msg.partition(),
            msg.offset(),
        )


def send_inference_result(user_id, features):
    model_used = random.choice(MODELS)
    prediction = random.random()
    payload = {
        "user_id": user_id,
        "features": features,
        "model": model_used,
        "prediction": prediction,
    }
    producer.produce(
        topic=TOPIC,
        key=str(user_id),
        value=json.dumps(payload),
        callback=delivery_report,
    )
    producer.poll(0)


def producer_loop():
    """Simulate sending inference results continuously"""
    user_id = 1
    while True:
        features = {"feature1": random.randint(0, 10), "feature2": random.randint(0, 5)}
        send_inference_result(user_id, features)
        user_id += 1
        time.sleep(1)  # simulate incoming requests


# -----------------------
# Consumer
# -----------------------
consumer_conf = {
    "bootstrap.servers": KAFKA_BROKER_ENDPOINT,
    "group.id": "ducklake-consumer",
    "auto.offset.reset": "earliest",
}
consumer = Consumer(consumer_conf)
consumer.subscribe([TOPIC])

# Connect to DuckLake / DuckDB
con = duckdb.connect(DB_PATH)

# Create table if it doesn't exist
con.execute(
    f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    user_id INTEGER,
    features JSON,
    model VARCHAR,
    prediction DOUBLE
)
"""
)

buffer = []
last_flush = time.time()


def flush_buffer():
    global buffer, last_flush
    if not buffer:
        return
    json_lines = "\n".join(json.dumps(msg) for msg in buffer)
    con.execute(
        f"""
        INSERT INTO {TABLE_NAME}
        SELECT * FROM read_json_auto(?)
    """,
        [json_lines],
    )
    print(f"Flushed {len(buffer)} records to DuckLake")
    buffer.clear()
    last_flush = time.time()


def consumer_loop():
    global buffer, last_flush
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            pass
        elif msg.error():
            print(f"Consumer error: {msg.error()}")
        else:
            buffer.append(json.loads(msg.value().decode("utf-8")))

        # Flush on batch size or time interval
        if len(buffer) >= BATCH_SIZE or (time.time() - last_flush) >= FLUSH_INTERVAL:
            flush_buffer()
