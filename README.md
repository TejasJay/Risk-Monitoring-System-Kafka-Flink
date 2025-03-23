# 🛡️ Fraud Monitoring Pipeline Documentation

## 📂 Project Overview

This project simulates bank transactions, detects fraudulent activities, visualizes data in Kibana, and sends alerts for high-risk or blocked customers.

* * *

## ⚙️ Architecture Flow (Detailed Mermaid Diagram)

```mermaid
flowchart TD

  subgraph Simulator [Simulation Engine]
    A1[transaction_producer.py]\n(Faker + Randomizer)
    A1 -->|Produces JSON events| K1(Kafka Topic: bank_transactions)
  end

  subgraph Kafka [Kafka Topics]
    K1 -->|Consumed| F1[flink SQL Job: Transactions]
    K1 -->|Consumed| F2[fraud_alert_consumer.py]
    K1 -->|Consumed| F3[TransactionsWithEventTime - ETL]
    F1 --> K2(Kafka Topic: customer_risk)
    F1 --> K3(Kafka Topic: blocked_customers)
    F1 --> K4(Kafka Topic: fraud_dashboard)
  end

  subgraph Flink [Flink SQL Layer]
    F3 -->|Processed| F1
  end

  subgraph Consumers [Kafka Consumers]
    K2 -->|Consumes| E1[to_elastic_customer_risk.py]
    K3 -->|Consumes| E2[to_elastic_blocked_customers.py]
    K3 -->|Consumes| W1[fraud_webhook_server.py]
    K3 -->|Consumes| M1[email_alert_engine.py]
  end

  subgraph Webhook & Alerting
    W1 -->|Receives JSON| Web[Flask App: Webhook Server]\n/index.html & /get-blocked-customers
    M1 -->|Sends Email| Mail[SMTP Alert Engine]
  end

  subgraph ElasticStack
    E1 -->|Indexes JSON| ES1[Elasticsearch Index: customer_risk]
    E2 -->|Indexes JSON| ES2[Elasticsearch Index: blocked_customers]
    Kibana[Kibana Dashboard]\n(Fraud Monitoring)
    Kibana -->|Loads Saved Objects| VIS[import_kibana_visuals.py]
    Kibana -->|Visualizes| ES1
    Kibana -->|Visualizes| ES2
  end

  subgraph Automation
    Auto[automate.sh] -->|Starts| ZK[Zookeeper]
    Auto --> KF[Kafka Broker]
    Auto --> FL[Flink Cluster]
    Auto --> EL[Elasticsearch]
    Auto --> KB[Kibana]
    Auto --> SC[fix_cluster_health.sh]
    Auto --> VIS
    Auto --> FLJ[fraud_sql_analytics.sql]
    Auto --> E1
    Auto --> E2
    Auto --> M1
  end

  click Kibana href "http://localhost:5601" _blank
  click Web href "http://localhost:5001" _blank
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

