from kafka import KafkaConsumer
import json

# Kafka Consumer Configuration
consumer = KafkaConsumer(
    "bank_transactions",
    bootstrap_servers="localhost:9092",
    auto_offset_reset="earliest",
    value_deserializer=lambda v: json.loads(v.decode("utf-8"))
)

# Read messages from Kafka
print("Listening for transactions...")
for message in consumer:
    print(f"Received: {message.value}")
