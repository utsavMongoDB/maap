#!/bin/bash

# Start the cron service
echo "Starting cron service..."
service cron start

# Run the collection script once at startup to ensure we have fresh data
echo "Running initial data collection..."
cd /app && ./collect_github_traffic.sh

# Start the Streamlit application
echo "Starting Streamlit application..."
streamlit run app.py --server.address=0.0.0.0
