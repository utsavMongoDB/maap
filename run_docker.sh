#!/bin/bash

# Build Docker image
docker build -t maap-metrics-dashboard .

# Run the Docker container with environment variables from .env file
docker run -d -p 8501:8501 --name maap-metrics --env-file .env maap-metrics-dashboard

echo "MAAP Metrics Dashboard is running at http://localhost:8501"