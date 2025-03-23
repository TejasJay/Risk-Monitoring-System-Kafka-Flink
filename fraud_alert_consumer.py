from kafka import KafkaConsumer
import requests
import json

# Connect to the 'blocked_customers' Kafka topic
consumer = KafkaConsumer(
    'blocked_customers',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    group_id='fraud_webhook_group',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

print("🔄 Listening for blocked customer alerts...")

for message in consumer:
    fraud_data = message.value
    # print(f"📬 Received fraud alert: {fraud_data}")

    try:
        # Send fraud alert to webhook
        response = requests.post("http://localhost:5001/block-customer", json=fraud_data)
        # print(f"✅ Webhook response: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Failed to send webhook: {e}")
