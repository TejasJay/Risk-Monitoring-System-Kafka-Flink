# 🛡️ Fraud Monitoring Pipeline Documentation

## 📂 Project Overview

This project simulates bank transactions, detects fraudulent activities, visualizes data in Kibana, and sends alerts for high-risk or blocked customers.

* * *

## ⚙️ Architecture Flow (Detailed Mermaid Diagram)

```mermaid
flowchart TD
  %% GROUP: System Boot
  subgraph System_Startup
    A1[Start Script: automate.sh]
    A2[Start Zookeeper]
    A3[Start Kafka Broker]
    A4[Create/Delete Topics]
    A5[Start Flink Cluster]
    A6[Start Elasticsearch]
    A7[Fix Cluster Health]
    A8[Start Kibana]
    A9[Import Saved Visualizations]
  end

  %% GROUP: Kafka Input Pipeline
  subgraph Log_Generators [Transaction Simulation]
    B1[transaction_producer.py<br>Faker + Random]
    B2[Kafka Topic: bank_transactions]
  end

  %% GROUP: Flink SQL
  subgraph Flink_Analytics [Apache Flink]
    C1[fraud_sql_analytics.sql<br>Flink SQL Job]
    C2[Compute: Risk Matrix, Fraud Dashboard, Blocked Customers]
    C3[Kafka Topic: customer_risk]
    C4[Kafka Topic: fraud_dashboard]
    C5[Kafka Topic: blocked_customers]
  end

  %% GROUP: Elasticsearch Ingest
  subgraph Elastic_Consumers [Kafka → Elasticsearch]
    D1[to_elastic_customer_risk.py]
    D2[to_elastic_blocked_customers.py]
    D3[Index: customer_risk]
    D4[Index: blocked_customers]
  end

  %% GROUP: Alerting + Webhook
  subgraph Block Customer in Real-time
    E1[email_alert_engine.py<br>Email if Txn > $50K]
    E2[fraud_webhook_server.py<br>Flask + Deque]
    E3[GET /get-blocked-customers]
    E4[POST /block-customer]
  end

  %% GROUP: Kibana
  subgraph Kibana
    F1[Dashboard: Fraud Monitoring]
    F2[customer_risk Visuals]
    F3[blocked_customers Visuals]
  end

  %% Connections
  A1 --> A2 --> A3 --> A4 --> A5
  A1 --> A6 --> A7
  A1 --> A8 --> A9

  A1 --> B1 --> B2
  B2 --> C1 --> C2
  C2 --> C3 & C4 & C5

  C3 --> D1 --> D3 --> F2
  C5 --> D2 --> D4 --> F3
  D4 --> E1
  C5 --> E2 --> E4 & E3

  F2 & F3 --> F1

```



* * *

## 🛠️ Components Summary

### 1\. Kafka Topics:

-   `bank_transactions`: Main input stream of transactions.
-   `customer_risk`: Processed risk evaluations.
-   `fraud_dashboard`: Aggregated metrics for dashboard.
-   `blocked_customers`: Flagged users with high-risk patterns.

### 2\. Flink SQL:

-   Stream processing + SQL analytics
-   Evaluates fraud likelihood, computes metrics, flags accounts

### 3\. Elasticsearch:

-   Index: `customer_risk` for risk scoring
-   Index: `blocked_customers` for blocked profiles

### 4\. Kibana:

-   Dashboards: Real-time visualizations
-   Imported via: `import_kibana_visuals.py`

### 5\. Webhook Server (Flask):

-   Endpoint: `/block-customer` to collect blocked users
-   Endpoint: `/get-blocked-customers` returns JSON for UI

### 6\. Email Alert Engine:

-   Listens on `blocked_customers`
-   Sends email via SMTP if criteria met

### 7\. Automation Scripts:

-   `automate.sh`: Full system bootstrap
-   `fix_cluster_health.sh`: Recovers Elasticsearch to yellow/green
-   `firewall_allow.sh`: Sets GCP firewall rules
* * *

## 🧠 Working Logic

1.  **Producer** sends synthetic transactions to Kafka (`bank_transactions`).
2.  **Flink SQL** evaluates each event to determine risk & anomalies.
3.  **Metrics and flags** are streamed to other topics (`customer_risk`, `fraud_dashboard`, `blocked_customers`).
4.  **Elasticsearch consumers** index these events for Kibana.
5.  **Kibana dashboards** load saved objects and visualize the data.
6.  **Webhook server** and **Email alert engine** act on high-risk transactions.
* * *

## 📦 Directory Structure (Suggestion)

```
📁 kafka_flink/
├── automate.sh
├── fix_cluster_health.sh
├── firewall_allow.sh
├── fraud_sql_analytics.sql
├── import_kibana_visuals.py
├── email_alert_engine.py
├── to_elastic_customer_risk.py
├── to_elastic_blocked_customers.py
├── transaction_producer.py
├── transaction_consumer.py
├── fraud_alert_consumer.py
├── fraud_webhook_server.py
├── export.ndjson  # Saved Kibana dashboard
```

* * *

## 🚀 Run the Pipeline

```bash
bash automate.sh
```

-   Starts Zookeeper, Kafka, Flink, Elasticsearch, Kibana
-   Creates topics
-   Submits Flink SQL jobs
-   Starts consumers, producers, and email engine
-   Imports Kibana saved visualizations
* * *

