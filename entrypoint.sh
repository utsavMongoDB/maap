#!/bin/bash

# Start the cron service
echo "Starting cron service..."
service cron start

# Run the collection script once at startup to ensure we have fresh data
echo "Running initial data collection..."
cd /app && ./collect_github_traffic.sh
COLLECTION_RESULT=$?

# Check if data collection succeeded
if [ $COLLECTION_RESULT -ne 0 ]; then
    echo "WARNING: Initial data collection failed with exit code $COLLECTION_RESULT"
    echo "Check if there's a valid JSON file and GITHUB_TOKEN is set correctly"
    
    # Check if we have a valid JSON file - if not, create an empty one
    if [ ! -f "/app/github_traffic_daily.json" ]; then
        echo "Creating empty JSON data structure"
        echo '{"last_updated": "'$(date -Iseconds)'", "data": []}' > /app/github_traffic_daily.json
    fi
else
    echo "Initial data collection completed successfully"
fi

# Start the Streamlit application
echo "Starting Streamlit application..."
streamlit run app.py --server.address=0.0.0.0
