from elasticsearch import Elasticsearch
import time

# ✅ Connect to Elasticsearch
es = Elasticsearch(["http://localhost:9200"])

# ✅ Define the search query for blocked customers (you can customize filters if needed)
query_search_after = {
    "query": {
        "match_all": {}  # No filter, fetch everything
    },
    "sort": [
        {"Current Transaction Amount": {"order": "desc"}},  # Sort newest first
        {"doc_id": "asc"}  # Tie-breaker to ensure uniqueness in `search_after`
    ],
    "size": 5  # Adjust batch size
}

# ✅ Track the last document's sort values
last_sort = None

print("\n🚨 Monitoring Blocked Customers in Real-Time...\n")

while True:
    # Add search_after if this is not the first request
    if last_sort:
        query_search_after["search_after"] = last_sort

    # ✅ Execute the search query
    response = es.search(index="blocked_customers", body=query_search_after)

    hits = response["hits"]["hits"]

    if not hits:
        print("⏳ No new blocked customers found. Checking again in 5 seconds...\n")
        time.sleep(5)
        continue

    print("🔍 New Blocked Customers Found:\n")
    for hit in hits:
        source = hit["_source"]
        print(f"{source['doc_id']} | {source['Name']} | Account: {source['Account Number']} | "
              f"Amount: ${source['Current Transaction Amount']:.2f} | "
              f"Reason: {source['Reason']} | Time: {source['Transaction Time']}")

    # ✅ Save the sort value of the last hit to avoid duplicates
    last_sort = hits[-1]["sort"]

    print("\n🔄 Checking again in 5 seconds...\n")
    time.sleep(5)
