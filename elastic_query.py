from elasticsearch import Elasticsearch

# Connect to Elasticsearch
es = Elasticsearch(["http://localhost:9200"])



############################################ FILTER ##########################################


# Define the search query
query1 = {
    "query": {
        "match": {  # Use match query for flexible search
            "Risk_Level": "High Risk"
        }
    }
}


# Execute the search
response = es.search(index="customer_risk", body=query1)

# Print the results
print("🔍 High-Risk Customers Found:")
for hit in response["hits"]["hits"]:
    source = hit["_source"]
    print(f"💰 {source['Name']} | Account: {source['Account Number']} | Risk Level: {source['Risk_Level']} | Avg Amount: ${source['Avg_Amount']:.2f} |  Total Txns: {source['Total_Txns']} | Fraud Txns: ${source['Fraud_Txns']:.2f}")



############################################ SORT BY (AVG AMOUNT)  ##########################################




query2 = {
    "query": {
        "term": {
            "Risk_Level": "High Risk"  # Exact match for "High Risk"
        }
    },
    "sort": [
        {"Avg_Amount": {"order": "desc"}}  # Sort in descending order
    ]
}



# Execute the search
response = es.search(index="customer_risk", body=query2)

# Print the results
print("🔍High-Risk Customers (Sorted by Transaction Amount):")
for hit in response["hits"]["hits"]:
    source = hit["_source"]
    print(f"💰 {source['Name']} | Account: {source['Account Number']} | Risk Level: {source['Risk_Level']} | Avg Amount: ${source['Avg_Amount']:.2f} |  Total Txns: {source['Total_Txns']} | Fraud Txns: ${source['Fraud_Txns']:.2f}")



############################################ PAGINATION ##########################################

# Define pagination variables
page_size = 5  # Number of results per page
page_number = 0  # Start from page 0

while True:
    print(f"\n🔄 Fetching page {page_number + 1}...\n")

    query_paginated = {
        "query": {
            "term": {"Risk_Level": "High Risk"}
        },
        "sort": [
            {"Avg_Amount": {"order": "desc"}}
        ],
        "from": page_number * page_size,  # Offset
        "size": page_size  # Number of results per page
    }

    # Execute search
    response = es.search(index="customer_risk", body=query_paginated)

    # If no results, stop
    if len(response["hits"]["hits"]) == 0:
        print("✅ No more results.")
        break

    # Print results
    for hit in response["hits"]["hits"]:
        source = hit["_source"]
        print(f"💰 {source['Name']} | Account: {source['Account Number']} | Risk Level: {source['Risk_Level']} | Avg Amount: ${source['Avg_Amount']:.2f}")

    # Ask user whether to continue
    next_page = input("\n➡️  Fetch next page? (y/n): ")
    if next_page.lower() != "y":
        break

    page_number += 1  # Move to next page

