#!/bin/bash

# Fix Elasticsearch cluster health by adjusting disk watermark settings

echo "🔧 Updating Elasticsearch cluster disk allocation thresholds..."

curl -X PUT "localhost:9200/_cluster/settings" -H 'Content-Type: application/json' -d'
{
  "transient": {
    "cluster.routing.allocation.disk.watermark.low": "95%",
    "cluster.routing.allocation.disk.watermark.high": "97%",
    "cluster.routing.allocation.disk.watermark.flood_stage": "99%",
    "cluster.info.update.interval": "1m"
  }
}'

echo "✅ Disk watermark settings updated."
echo "🔍 Checking cluster health every 5 seconds..."

# Wait for cluster to turn yellow or green
while true; do
  status=$(curl -s "localhost:9200/_cluster/health" | grep '"status"' | awk -F '"' '{print $4}')
  
#  echo "⏳ Current cluster status: $status"
  
  if [[ "$status" == "yellow" || "$status" == "green" ]]; then
    echo "✅ Elasticsearch cluster is healthy!"
    break
  fi
  
  sleep 5
done

# Optionally restart Kibana if not running
if pgrep -f "kibana" > /dev/null; then
    echo "ℹ️  Kibana is already running."
else
    echo "🚀 Starting Kibana..."
    ~/kibana/bin/kibana > ~/kibana/kibana.log 2>&1 &
    echo "✅ Kibana started and logging to ~/kibana/kibana.log"
fi
