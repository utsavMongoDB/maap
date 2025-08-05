#!/bin/bash

# Build Docker image
docker build -t maap-metrics-dashboard .

# Run the Docker container
docker run -d -p 8501:8501 --name maap-metrics maap-metrics-dashboard

echo "MAAP Metrics Dashboard is running at http://localhost:8501"