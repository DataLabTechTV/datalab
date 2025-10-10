#!/bin/sh

echo "Initializing consumer: topic $TOPIC, group $GROUP"

docker exec datalab-kafka-1 /opt/kafka/bin/kafka-console-consumer.sh \
    --bootstrap-server localhost:29092 \
    --topic "$TOPIC" \
    --group "$GROUP" \
    --timeout-ms 5000
