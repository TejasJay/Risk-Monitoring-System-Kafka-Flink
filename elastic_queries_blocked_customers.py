import time
from elasticsearch import Elasticsearch

# Connect to Elasticsearch
es = Elasticsearch(["http://localhost:9200"])


query = {
    "query": {
        "match_all": {}
    }
}

response = es.search(index="blocked_customers", body=query)
print(response["hits"]["hits"])

