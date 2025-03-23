#!/bin/bash

# Replace this with your GCP project ID
PROJECT_ID="thermal-scene-446819-t2"
NETWORK_NAME="default"

echo "📡 Creating firewall rule for Kibana (port 5601)..."
gcloud compute firewall-rules create allow-kibana \
  --project=$PROJECT_ID \
  --network=$NETWORK_NAME \
  --allow=tcp:5601 \
  --direction=INGRESS \
  --priority=1000 \
  --target-tags=kibana-access \
  --source-ranges=0.0.0.0/0 \
  --description="Allow Kibana UI access from anywhere"

echo "📊 Creating firewall rule for Grafana (port 3000)..."
gcloud compute firewall-rules create allow-grafana \
  --project=$PROJECT_ID \
  --network=$NETWORK_NAME \
  --allow=tcp:3000 \
  --direction=INGRESS \
  --priority=1000 \
  --target-tags=grafana-access \
  --source-ranges=0.0.0.0/0 \
  --description="Allow Grafana UI access from anywhere"

echo "✅ Firewall rules created successfully!"
