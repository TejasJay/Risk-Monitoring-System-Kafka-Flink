from elasticsearch import Elasticsearch
from kafka import KafkaConsumer
import json
import time
import uuid

es = Elasticsearch(["http://localhost:9200"])

index_mapping = {
    "settings":{"number_of_shards": 1, "number_of_replicas": 1},
    "mappings" : {
        "properties" : {
            "Name" : {"type" : "text", "fields" : { "raw": {"type" : "keyword"} } },
            "Account Number" : {"type" : "keyword"},
            "Current Transaction Amount" : {"type" : "double"},
            "Transaction ID" : {"type" : "keyword"},
            "Transaction Time" : {"type" : "keyword"},
            "Reason" : {"type" : "keyword"},
            "doc_id" : {"type": "keyword"},
        }
    }
}


if not es.indices.exists(index="blocked_customers"):
    es.indices.create(index="blocked_customers", body = index_mapping)

    print("✅ Index blocked_customers' created successfully.")
else:
    print("✅ Index blocked_customers' already exists!!!!!!!")


time.sleep(10)
     

consumer = KafkaConsumer(
    "blocked_customers",
    bootstrap_servers = "localhost:9092",           
    auto_offset_reset="earliest",
    group_id="fraud_alerts_reader",
    value_deserializer=lambda m: json.loads(m.decode("utf-8")) if m else None  # Handle None values

)
print("🔄 Listening for locked customers alerts from Kafka...")


# ✅ Step 3: Read messages from Kafka and send to Elasticsearch
for message in consumer:
    if message.value is None:
        # print("⚠️ Skipping empty Kafka message")
        continue
    
    try:
        blocked_data = message.value  # Extract JSON message
        # print(f"📬 Received:{ blocked_data}")

        # Extract fields safely
        doc = {
            "Name": blocked_data.get("Name", "Unknown"),
            "Account Number": blocked_data.get("Account Number", "Unknown"),
            "Current Transaction Amount": blocked_data.get("Current Transaction Amount", 0.0),
            "Transaction ID": blocked_data.get("Transaction ID", "Unknown"),
            "Transaction Time": blocked_data.get("Transaction Time", "Unknown"),
            "Reason": blocked_data.get("Reason", "Unknown"),
            "doc_id": str(uuid.uuid4())
        }

        # Index to Elasticsearch
        response = es.index(index="blocked_customers", document=doc)
        # print(f"✅ Indexed: {response['_id']} - {doc}")

    except Exception as e:
        print(f"❌ Error processing message: {e}")
