#!/bin/bash

# Check if .env file exists
if [ -f .env ]; then
  echo "Loading environment variables from .env"
  source .env
else
  echo "Warning: .env file not found. Make sure to pass GITHUB_TOKEN directly."
fi

# Check if GITHUB_TOKEN is set
if [ -z "$GITHUB_TOKEN" ]; then
  echo "Error: GITHUB_TOKEN environment variable not set."
  echo "Please set it in .env file or pass it directly."
  exit 1
fi

# Build Docker image using the scheduled Dockerfile
echo "Building Docker image..."
docker build -t maap-metrics-dashboard:scheduled -f Dockerfile.scheduled .

# Run the Docker container with environment variables
echo "Starting container..."
# Check if there's an existing data file to preserve
if [ -f "github_traffic_daily.json" ]; then
  echo "Found existing data file. Will mount it in the container."
  MOUNT_DATA="-v $(pwd)/github_traffic_daily.json:/app/github_traffic_daily.json"
else
  MOUNT_DATA=""
  echo "No existing data file found. A new one will be created."
fi

# Run the Docker container with environment variables and data persistence
docker run -d \
  -p 8501:8501 \
  --name maap-metrics-scheduled \
  -e GITHUB_TOKEN="$GITHUB_TOKEN" \
  $MOUNT_DATA \
  maap-metrics-dashboard:scheduled

echo "MAAP Metrics Dashboard is running at http://localhost:8501"
echo "Data will be automatically collected daily at midnight."
echo "To check the collection logs, run: docker exec maap-metrics-scheduled cat /var/log/cron.log"
