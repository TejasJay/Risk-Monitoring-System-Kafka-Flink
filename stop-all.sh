#!/bin/bash
echo "Stopping Flink, Kafka, Zookeeper..."

pkill -f StandaloneSessionClusterEntrypoint
pkill -f TaskManagerRunner
pkill -f SqlClient
pkill -f Kafka
pkill -f QuorumPeerMain
pkill -f python3
pkill -f Elasticsearch
pkill -f kibana

echo "✅ All components stopped."
