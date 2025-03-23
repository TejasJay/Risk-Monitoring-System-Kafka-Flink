import time
from elasticsearch import Elasticsearch

# Connect to Elasticsearch
es = Elasticsearch(["http://localhost:9200"])

# Define the search query (fetch only "High Risk" customers)
query_search_after = {
    "query": {
        "term": {"Risk_Level": "High Risk"}
    },
    "sort": [
        {"Avg_Amount": {"order": "desc"}},  # Sort by highest transaction amount
        {"_id": "asc"}  # Unique tie-breaker sort field
    ],
    "size": 5
}

# Track the last document's sort values
last_sort = None

print("\n🚨 Monitoring High-Risk Customers in Real-Time...\n")

while True:
    # Add search_after parameter if it's not the first request
    if last_sort:
        query_search_after["search_after"] = last_sort

    # Execute the search query
    response = es.search(index="customer_risk", body=query_search_after)

    # If no new results, wait and check again
    if len(response["hits"]["hits"]) == 0:
        print("⏳ No new high-risk customers found. Checking again in 5 seconds...\n")
        time.sleep(5)
        continue

    # Print new results
    print("🔍 New High-Risk Customers Found:\n")
    for hit in response["hits"]["hits"]:
        source = hit["_source"]
        print(f"💰 {source['Name']} | Account: {source['Account Number']} | Avg Amount: ${source['Avg_Amount']:.2f} | Fraud Txns: {source['Fraud_Txns']}")

    # Get the last document's sort values (to avoid fetching duplicates)
    last_sort = response["hits"]["hits"][-1]["sort"]

    # Wait before the next iteration
    print("\n🔄 Checking for new records in 5 seconds...\n")
    time.sleep(5)
