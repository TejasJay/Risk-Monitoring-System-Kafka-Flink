#!/bin/bash

# Function to check if a process is running
is_running() {
    pgrep -f "$1" > /dev/null 2>&1
}

# Start Zookeeper if not running
if is_running "QuorumPeerMain"; then
    echo "Zookeeper is already running."
else
    echo "Starting Zookeeper..."
    ~/kafka/bin/zookeeper-server-start.sh ~/kafka/config/zookeeper.properties & 
    sleep 20
fi

# Start Kafka Broker if not running
if is_running "kafka.Kafka"; then
    echo "Kafka Broker is already running."
else
    echo "Starting Kafka Broker..."
    ~/kafka/bin/kafka-server-start.sh ~/kafka/config/server.properties &
    sleep 20
fi

# List and delete all topics
for topic in $(~/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092); do
    echo "Deleting topic: $topic"
    ~/kafka/bin/kafka-topics.sh --delete --topic "$topic" --bootstrap-server localhost:9092
    sleep 1
done

sleep 10

# Create Kafka Topics if not present.
echo "Ensuring Kafka topics exist..."
~/kafka/bin/kafka-topics.sh --create --if-not-exists --topic bank_transactions --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
~/kafka/bin/kafka-topics.sh --create --if-not-exists --topic customer_risk --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
~/kafka/bin/kafka-topics.sh --create --if-not-exists --topic fraud_dashboard --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
~/kafka/bin/kafka-topics.sh --create --if-not-exists --topic blocked_customers --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1

sleep 20

# Start Flink if not running
if is_running "StandaloneSessionClusterEntrypoint"; then
    echo "Flink is already running."
else
    echo "Starting Flink Cluster..."
    ~/flink/bin/start-cluster.sh &
    sleep 10
fi

# Start Log Generators
for script in "transaction_producer.py" "fraud_alert_consumer.py" "fraud_webhook_server.py"; do
    if is_running "$script"; then
        echo "$script is already running."
    else
        echo "Starting $script..."
        python3 ~/kafka_flink/$script &
    fi
done

sleep 10

# Start Elasticsearch if not running
if is_running "org.elasticsearch.bootstrap.Elasticsearch"; then
    echo "Elasticsearch is already running."
else
    echo "Starting Elasticsearch..."
    ~/elasticsearch/bin/elasticsearch &

    # ✅ Wait for ES to actually be up
    echo "Waiting for Elasticsearch to become available..."
    until curl -s http://localhost:9200 >/dev/null; do
        echo "⏳ Still waiting for Elasticsearch..."
        sleep 5
    done
    echo "✅ Elasticsearch is up!"
fi


# 🛠️ Fix cluster health if needed
bash ~/kafka_flink/fix_cluster_health.sh &


# Check if Kibana is running
if is_running "kibana"; then
    echo "✅ Kibana is already running."
else
    echo "✅ Starting Kibana..."
    ~/kibana/bin/kibana &

    # Wait for Kibana to be available
    echo "✅ ✅ ✅ Waiting for Kibana to become available..."
    until curl -s http://localhost:5601 >/dev/null; do
        echo "⏳ Still waiting for Kibana..."
        sleep 5
    done
    echo "✅✅ ✅  Kibana is up!"
fi


# Import saved objects to Kibana
echo "📦✅ ✅  Importing Kibana visualizations..."
python3 ~/kafka_flink/import_kibana_visuals.py

# Submit Flink SQL Job
echo "✅ ✅ Starting Flink SQL client and executing SQL script..."
~/flink/bin/sql-client.sh -f ~/kafka_flink/fraud_sql_analytics.sql

sleep 20


# Start Email Alert Engine
if is_running "email_alert_engine.py"; then
    echo "Email Alert Engine already running."
else
    echo "Starting Email Alert Engine..."
    # python3 ~/kafka_flink/email_alert_engine.py &
fi



# Start Kafka to Elasticsearch ingestion scripts
for script in "to_elastic_customer_risk.py" "to_elastic_blocked_customers.py"; do
    if is_running "$script"; then
        echo "$✅ ✅ script is already running."
    else
        echo "✅ ✅ Starting $script..."
        python3 ~/kafka_flink/$script &
    fi
done




echo "✅ All required services are running!"
