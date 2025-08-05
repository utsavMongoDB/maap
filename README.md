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

For containerized deployment:

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

## Access

Once running, access the dashboard at:
- Local: http://localhost:8501
- Docker: http://localhost:8501