#!/bin/bash
# Create all Kafka topics required by FactoryMind
# Usage: bash infrastructure/kafka/create-topics.sh [container_name]
KAFKA_CONTAINER=${1:-"factorymind-kafka-1"}

echo "Creating Kafka topics in container: $KAFKA_CONTAINER"

docker exec "$KAFKA_CONTAINER" kafka-topics \
  --bootstrap-server localhost:9092 --create --if-not-exists \
  --topic raw-inspections --partitions 6 --replication-factor 1 \
  --config retention.ms=86400000

docker exec "$KAFKA_CONTAINER" kafka-topics \
  --bootstrap-server localhost:9092 --create --if-not-exists \
  --topic processed-results --partitions 6 --replication-factor 1 \
  --config retention.ms=86400000

docker exec "$KAFKA_CONTAINER" kafka-topics \
  --bootstrap-server localhost:9092 --create --if-not-exists \
  --topic model-alerts --partitions 2 --replication-factor 1 \
  --config retention.ms=604800000

docker exec "$KAFKA_CONTAINER" kafka-topics \
  --bootstrap-server localhost:9092 --create --if-not-exists \
  --topic system-events --partitions 2 --replication-factor 1 \
  --config retention.ms=604800000

echo ""
echo "Topics created:"
docker exec "$KAFKA_CONTAINER" kafka-topics \
  --bootstrap-server localhost:9092 --list
