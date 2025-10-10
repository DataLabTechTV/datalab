#!/bin/sh

echo "Creating topic if not exists: $TOPIC"

docker exec datalab-kafka-1 /opt/kafka/bin/kafka-topics.sh \
    --bootstrap-server localhost:29092 \
    --create --if-not-exists --topic "$TOPIC" \
    --partitions 1 \
    --replication-factor 1
