# MAAP Metrics Dashboard

An interactive dashboard that visualizes GitHub traffic analytics for MongoDB Application Acceleration Platform (MAAP) repositories. This tool collects views, clones, and other metrics from multiple repositories and presents them in a consolidated, user-friendly interface.

## Setup Instructions

### Local Setup

1. Clone the repository
```bash
git clone https://github.com/utsavMongoDB/maap.git
cd maap
```

2. Create a `.env` file with your GitHub token
```bash
echo "GITHUB_TOKEN=your_personal_access_token" > .env
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Run the Streamlit application
```bash
streamlit run app.py
```

### Docker Setup

For basic containerized deployment (Streamlit app only):

1. Build and run using the provided script
```bash
chmod +x run_docker.sh
./run_docker.sh
```

2. Or manually:
```bash
docker build -t maap-metrics-dashboard .
docker run -p 8501:8501 --env-file .env maap-metrics-dashboard
```

### Docker Setup with Automated Data Collection

For a complete solution that includes automated daily data collection:

1. Build and run using the scheduled Docker script
```bash
chmod +x run_docker_scheduled.sh
./run_docker_scheduled.sh
```

2. This will:
   - Build a container with both Streamlit and cron
   - Run the data collection script once at startup
   - Schedule the script to run daily at midnight
   - Start the Streamlit application

3. Check collection logs
```bash
docker exec maap-metrics-scheduled cat /var/log/cron.log
```

## Automated Data Collection

To automatically collect daily traffic data:

```bash
chmod +x collect_github_traffic.sh
./collect_github_traffic.sh
```

Add to crontab for daily execution:
```bash
0 0 * * * cd /path/to/maap-1 && ./collect_github_traffic.sh
```

The script stores a timestamp of when data was last collected, which is displayed on the dashboard to help users understand data freshness.

### Data Storage Format

The traffic data is stored in a JSON file (`github_traffic_daily.json`) with the following structure:

```json
{
  "last_updated": "2023-08-08T11:40:33+05:30",
  "data": [
    {
      "repository": "mongodb-partners/repo-name",
      "collected_at": "2023-08-08T11:40:34+05:30",
      "views": { /* view data */ },
      "clones": { /* clone data */ }
    },
    // More repositories...
  ]
}
```

## Access

Once running, access the dashboard at:
- Local: http://localhost:8501
- Docker: http://localhost:8501