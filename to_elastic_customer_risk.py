from elasticsearch import Elasticsearch
from kafka import KafkaConsumer
import json
import time


# ✅ Step 1: Connect to Elasticsearch

es = Elasticsearch(["http://localhost:9200"])

# Define the index mapping
index_mapping = {
    "settings": {"number_of_shards": 1, "number_of_replicas": 1},
    "mappings": {
        "properties": {
            "Name" : {"type" : "text", "fields" : { "raw": {"type" : "keyword"} } },
            "Account_Number": {"type": "keyword"},
            "Total_Txns": {"type": "integer"},
            "Fraud_Txns": {"type": "integer"},
            "Avg_Amount": {"type": "double"},
            "Risk_Level": {"type": "keyword"},
        }
    }
}

# Create the index
if not es.indices.exists(index="customer_risk"):
    es.indices.create(index="customer_risk", body=index_mapping)

    print("✅ Index 'customer_risk' created successfully.")
else:
    print("✅ Index 'customer_risk' already exists!!!!!!!")


time.sleep(10)

# ✅ Step 2: Define Kafka Consumer
consumer = KafkaConsumer(
    "customer_risk",
    bootstrap_servers="localhost:9092",
    auto_offset_reset="earliest",
    group_id="fraud_alerts_reader",
    value_deserializer=lambda m: json.loads(m.decode("utf-8")) if m else None  # Handle None values

)

print("🔄 Listening for customer risk alerts from Kafka...")

# ✅ Step 3: Read messages from Kafka and send to Elasticsearch
for message in consumer:
    if message.value is None:
        # print("⚠️ Skipping empty Kafka message")
        continue
    
    try:
        risk_data = message.value  # Extract JSON message
        # print(f"📬 Received: {risk_data}")

        # Extract fields safely
        doc = {
            "Name": risk_data.get("Name", "Unknown"),
            "Account Number": risk_data.get("Account Number", "Unknown"),
            "Total_Txns": risk_data.get("Total_Txns", 0),
            "Fraud_Txns": risk_data.get("Fraud_Txns", 0),
            "Avg_Amount": risk_data.get("Avg_Amount", 0.0),
            "Risk_Level": risk_data.get("Risk_Level", "Unknown")
        }

        # Index to Elasticsearch
        response = es.index(index="customer_risk", document=doc)
        # print(f"✅ Indexed: {response['_id']} - {doc}")

    except Exception as e:
        print(f"❌ Error processing message: {e}")
