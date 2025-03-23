# Project Notes: Real-Time Fraud Detection System

## Overview

This project is a real-time fraud detection and monitoring system built using the following technologies:

-   Apache Kafka (for real-time messaging)
-   Apache Flink (for stream processing and analytics)
-   Elasticsearch (for indexing and querying risk/alert data)
-   Kibana (for dashboard visualization)
-   Python (for producers, consumers, and auxiliary scripts)
-   Flask (for exposing webhook endpoints)

It simulates real-world bank transactions, detects fraud using Flink analytics, blocks high-risk accounts, and pushes data to Elasticsearch for visualization.

* * *

## System Architecture Overview

### Data Flow:

1.  **Python Log Generator**: `transaction_producer.py` sends transaction data to Kafka (`bank_transactions` topic).
2.  **Apache Flink**:
    -   Reads transactions.
    -   Computes risk metrics (Risk Matrix, Fraud Dashboard).
    -   Sends results to Kafka topics: `customer_risk`, `fraud_dashboard`, `blocked_customers`.
3.  **Python Consumers**:
    -   `to_elastic_customer_risk.py`: reads `customer_risk` and indexes to Elasticsearch.
    -   `to_elastic_blocked_customers.py`: reads `blocked_customers` and indexes to Elasticsearch.
4.  **Kibana**:
    -   Visualizes indexed data via dashboards.
5.  **Email Alerts**:
    -   `email_alert_engine.py`: listens to `blocked_customers` and sends alerts.
6.  **Webhook Server**:
    -   `fraud_webhook_server.py` listens for blocked customer alerts and stores latest entries.
* * *

## Setup Instructions

### 1\. Environment Setup (Manual or Scripted)

-   Install:
    -   Kafka + Zookeeper
    -   Flink
    -   Elasticsearch (with JVM 17)
    -   Kibana (ensure compatible version with Elasticsearch)
    -   Python libraries: kafka-python, faker, flask, elasticsearch, requests

### 2\. Scripts and Automation

-   **Primary Startup Script**: `automate.sh` or `automate_new.sh`
    -   Starts Zookeeper, Kafka, Flink, Elasticsearch, Kibana
    -   Creates Kafka topics
    -   Runs Flink SQL job (`fraud_sql_analytics.sql`)
    -   Starts log producers and Kafka consumers
    -   Fixes cluster health if required (via `fix_cluster_health.sh`)
    -   Imports Kibana visualizations (via `import_kibana_visuals.py`)
* * *

## Issues Encountered & Solutions

### 1\. Elasticsearch Cluster Health = RED

**Problem**: Kibana failed to boot or migrate saved objects due to RED cluster. **Solution**:

-   Adjusted Elasticsearch disk watermark thresholds in `fix_cluster_health.sh`
-   Waited until cluster became YELLOW or GREEN before proceeding.

### 2\. Port 5601 Already in Use

**Problem**: Kibana process already running. **Solution**:

-   Killed existing process using `pkill -f kibana` or `kill -9 <pid>`.
-   Ensured Kibana was only started once in `automate.sh`.

### 3\. Kibana Import Failure (Saved Objects)

**Problem**: File upload to `/api/saved_objects/_import` failed. **Solution**:

-   Used correct API headers: `kbn-xsrf: true`
-   Used `import_kibana_visuals.py` to automate import of `.ndjson` export.

### 4\. Kibana Index Mapping Issues

**Problem**: Sorting on text fields or full-text fields failed. **Solution**:

-   Updated index mappings to use `"text"` with `"raw"` keyword subfields for `Name`.
-   Used `"keyword"` for all sortable/aggregated fields.
* * *



## 🧩 Kibana Integration & Troubleshooting

### Kibana Setup

-   **Installation Directory:** `~/kibana`
-   **Startup Command:**

    ```bash
    ~/kibana/bin/kibana &
    ```

-   **Check Availability:**
    Kibana runs on `http://<vm-ip>:5601`

### Firewall Rule for Kibana

```bash
gcloud compute firewall-rules create allow-kibana \
  --project=PROJECT_ID \
  --network=default \
  --allow=tcp:5601 \
  --direction=INGRESS \
  --priority=1000 \
  --target-tags=kibana-access \
  --source-ranges=0.0.0.0/0 \
  --description="Allow Kibana UI access"
```

### Issues Faced

-   **Port 5601 already in use**: Resolved by killing existing Kibana processes using `pkill -f kibana`.
-   **“Kibana server is not ready yet”**: Elasticsearch cluster was in `red` state.
-   **Cluster Health**: Many saved object migrations were failing.

### Solution

-   Implemented `fix_cluster_health.sh` to fix disk watermark thresholds and wait until cluster health turns `yellow` or `green`.
* * *

## 📊 Saved Kibana Visualizations

### Import Script

```python
# import_kibana_visuals.py
import requests

headers = {"kbn-xsrf": "true"}
with open("/home/tejasjay94/kafka_flink/export.ndjson", "rb") as f:
    response = requests.post(
        "http://localhost:5601/api/saved_objects/_import?overwrite=true",
        headers=headers,
        files={"file": f}
    )
print(response.status_code)
print(response.json())
```

### Common Issues

-   `text` fields in mappings do not allow sorting or aggregations by default.
-   **Solution**: Used `"type": "text", "fields": { "raw": { "type": "keyword" } }` for fields like `Name`.
* * *

## 📬 Email Alert Engine

### Purpose

Send alert emails for any blocked customer whose transaction exceeds a defined threshold.

### Components

-   **Kafka Consumer** for `blocked_customers` topic
-   **SMTP-based Email Sender**
-   Uses `.env` file for credentials:

    ```
    SMTP_SERVER=smtp.gmail.com
    SMTP_PORT=587
    EMAIL_FROM=your_email@gmail.com
    EMAIL_PASSWORD=your_password
    EMAIL_TO=recipient@example.com
    ```

### Problems Faced

-   Connection errors when credentials were missing.
-   Fix: Used `dotenv` to securely load sensitive environment variables.
* * *

## 🔍 Real-Time Monitoring Web App

### `/fraud_webhook_server.py`

-   Built with Flask
-   Provides:
    -   `GET /get-blocked-customers`: Returns the latest blocked customers (stored in a queue).
    -   `POST /block-customer`: Receives alerts and updates the queue.

### Hosted On

-   Runs on `http://<vm-ip>:5001`
-   Auto-started in `automate.sh`
* * *


* * *

## 📊 Kibana Dashboard Setup (Tips)

You already have the saved objects for the `customer_risk` and `blocked_customers` indices. Here's how to expand and refine your dashboard:

### Visual Suggestions for `customer_risk` Index

| Visualization Type | Description |
| --- | --- |
| Pie Chart | Distribution of Risk Levels (High, Moderate, Low) |
| Bar Chart | Avg. Transaction Amount per Risk Level |
| Table | Top 10 Customers by Fraud\_Txns |
| Heatmap | Risk Level vs. Total Transactions |

### Visual Suggestions for `blocked_customers` Index

| Visualization Type | Description |
| --- | --- |
| Data Table | List of Recently Blocked Customers |
| Metric | Total Blocked Customers (Count) |
| Time Series | Blocked Customers over Time (per Minute) |

### Creating Visuals

1.  Navigate to **Kibana → Visualize Library**
2.  Click **"Create Visualization" → Lens**
3.  Choose the right index (e.g., `customer_risk`)
4.  Drag-and-drop fields like `Risk_Level`, `Total_Txns`, or `Avg_Amount` to configure your chart
5.  Save → Pin to `Fraud Monitoring` dashboard
* * *
