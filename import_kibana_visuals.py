import requests

headers = {
    "kbn-xsrf": "true"
}

file_path = "/home/tejasjay94/kafka_flink/export.ndjson"

with open(file_path, "rb") as f:
    response = requests.post(
        "http://localhost:5601/api/saved_objects/_import?overwrite=true",
        headers=headers,
        files={"file": f}
    )

print("✅ Kibana import complete")
print(response.status_code)
print(response.json())
