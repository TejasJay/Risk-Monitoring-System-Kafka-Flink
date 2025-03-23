############################################ SEARCH AFTER ##########################################
# ✅ search_after is more efficient:

# Uses a sorting field (e.g., _id, timestamp) to fetch next results quickly.

import time
from elasticsearch import Elasticsearch

# Connect to Elasticsearch
es = Elasticsearch(["http://localhost:9200"])


# Define the search query
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

while True:
    print("\n🔄 Fetching next batch of results...\n")

    # Add search_after parameter if not first request
    if last_sort:
        query_search_after["search_after"] = last_sort

    # Execute the query
    response = es.search(index="customer_risk", body=query_search_after)

    # If no results, stop
    if len(response["hits"]["hits"]) == 0:
        print("✅ No more results.")
        break

    # Print results
    for hit in response["hits"]["hits"]:
        source = hit["_source"]
        print(f"💰 {source['Name']} | Account: {source['Account Number']} | Risk Level: {source['Risk_Level']} | Avg Amount: ${source['Avg_Amount']:.2f}")

    # Get the last document's sort values
    last_sort = response["hits"]["hits"][-1]["sort"]

    # Ask user whether to continue
    next_page = input("\n➡️  Fetch next page? (y/n): ")
    if next_page.lower() != "y":
        break
