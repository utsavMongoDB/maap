import requests
import json
import os
from datetime import datetime
import streamlit as st
import pandas as pd
import dotenv
# Load environment variables from .env file
dotenv.load_dotenv()

class GitHubTrafficCollector:
    def __init__(self, token='None'):
        """
        Initialize the GitHub Traffic Collector
        
        Args:
            token (str): GitHub personal access token
        """
        self.token = token or os.environ.get('GITHUB_TOKEN')
        if not self.token:
            raise ValueError("GitHub token is required. Set GITHUB_TOKEN environment variable or pass token directly.")
        
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.base_url = 'https://api.github.com'
    
    def get_repo_traffic(self, owner, repo):
        """
        Collect all traffic data for a repository
        
        Args:
            owner (str): Repository owner
            repo (str): Repository name
            
        Returns:
            dict: Complete traffic data
        """
        traffic_data = {
            'repository': f"{owner}/{repo}",
            'collected_at': datetime.now().isoformat(),
            'views': self.get_views(owner, repo),
            'stars': self.get_stars(owner, repo),
            'referrers': self.get_referrers(owner, repo),
            'paths': self.get_popular_paths(owner, repo)
        }
        
        return traffic_data
    
    def get_views(self, owner, repo):
        """Get repository view statistics"""
        url = f"{self.base_url}/repos/{owner}/{repo}/traffic/views"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching views: {response.status_code} - {response.text}")
            return None
    
    def get_stars(self, owner, repo):
        """Get repository star statistics"""
        url = f"{self.base_url}/repos/{owner}/{repo}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'count': data.get('stargazers_count', 0),
                'uniques': data.get('stargazers_count', 0)
            }
        else:
            print(f"Error fetching stars: {response.status_code} - {response.text}")
            return None
    
    def get_referrers(self, owner, repo):
        """Get top referrers for the repository"""
        url = f"{self.base_url}/repos/{owner}/{repo}/traffic/popular/referrers"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching referrers: {response.status_code} - {response.text}")
            return None
    
    def get_popular_paths(self, owner, repo):
        """Get popular content paths"""
        url = f"{self.base_url}/repos/{owner}/{repo}/traffic/popular/paths"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching popular paths: {response.status_code} - {response.text}")
            return None
    
    def save_to_json(self, data, filename=None):
        """Save traffic data to JSON file"""
        if not filename:
            repo_name = data['repository'].replace('/', '_')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"github_traffic_{repo_name}_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Traffic data saved to {filename}")
        return filename
    

    
    def print_summary(self, data):
        """Print a summary of the traffic data"""
        print(f"\n=== Traffic Summary for {data['repository']} ===")
        print(f"Data collected at: {data['collected_at']}")
        
        if data['views']:
            print(f"\nViews (last 14 days):")
            print(f"  Total views: {data['views']['count']}")
            print(f"  Unique visitors: {data['views']['uniques']}")
        
        if data['stars']:
            print(f"\nStars:")
            print(f"  Total stars: {data['stars']['count']}")
        
        if data['referrers']:
            print(f"\nTop Referrers:")
            for ref in data['referrers'][:5]:  # Show top 5
                print(f"  {ref['referrer']}: {ref['count']} views")
        
        if data['paths']:
            print(f"\nPopular Paths:")
            for path in data['paths'][:5]:  # Show top 5
                print(f"  {path['path']}: {path['count']} views")


def run_streamlit_app():
    st.markdown(
        """
        <style>
        .main-title {font-size: 3.2em; font-weight: 700; color: #13aa52; margin-bottom: 0.2em; text-align: center;}
        .subtitle {font-size: 1.4em; color: #666; margin-bottom: 2em; text-align: center; font-weight: 300;}
        .metric-box {background: linear-gradient(to right, #f8f9fa, #ffffff); border-radius: 15px; padding: 1.5em; margin-bottom: 1.5em; box-shadow: rgba(0, 0, 0, 0.1) 0px 4px 12px;}
        .stMetric {background: linear-gradient(to bottom right, #ffffff, #f5f5f5); border-radius: 10px; padding: 15px; box-shadow: rgba(0, 0, 0, 0.05) 0px 1px 7px;}
        div[data-testid="stMetricValue"] {font-size: 1.8em !important; font-weight: 600 !important; color: #13aa52 !important;}
        div[data-testid="stMetricLabel"] {font-size: 1em !important; font-weight: 500 !important;}
        .stDataFrame {border-radius: 10px !important;}
        .chart-header {text-align: center; color: #333; font-weight: 600; margin-bottom: 1em; border-bottom: 1px solid #eee; padding-bottom: 0.5em;}
        .dashboard-container {padding: 1em; max-width: 1200px; margin: 0 auto;}
        </style>
        """,
        unsafe_allow_html=True
    )
    st.markdown('<div class="dashboard-container">', unsafe_allow_html=True)
    st.markdown('<div class="main-title">MAAP Metrics Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Visualizing GitHub Traffic Analytics for MAAP Repositories</div>', unsafe_allow_html=True)

    json_file = "github_traffic_daily.json"
    try:
        with open(json_file, "r") as f:
            json_content = json.load(f)
            
        # Handle both old and new JSON formats
        if isinstance(json_content, dict) and "data" in json_content:
            # New format with timestamp
            traffic_list = json_content.get("data", [])
            last_updated_timestamp = json_content.get("last_updated", "Unknown")
        else:
            # Old format (direct list)
            traffic_list = json_content
            last_updated_timestamp = "Unknown"
            
        summary_data = []

        for traffic_data in traffic_list:
            repo_full = traffic_data.get("repository", "")
            repo = repo_full.replace("mongodb-partners/", "")
            views = traffic_data.get("views", {})
            stars = traffic_data.get("stars", {})
            views_count = views.get("count", 0)
            views_uniques = views.get("uniques", 0)
            stars_count = stars.get("count", 0)
            summary_data.append({
                "Repository": repo,
                "Views": views_count,
                "Unique Visitors": views_uniques,
                "Stars": stars_count
            })

        df = pd.DataFrame(summary_data)
        df_sorted = df.sort_values(by="Views", ascending=False)

        # Show top metrics in columns
        total_views = int(df_sorted["Views"].sum())
        total_stars = int(df_sorted["Stars"].sum())
        total_unique_visitors = int(df_sorted["Unique Visitors"].sum())

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Views", f"{total_views:,}")
        with col2:
            st.metric("Total Unique Visitors", f"{total_unique_visitors:,}")
        with col3:
            st.metric("Total Stars", f"{total_stars:,}")

        # Add a separator
        st.markdown("<hr style='margin: 2em 0; opacity: 0.3;'>", unsafe_allow_html=True)
        
        # Display last updated timestamp
        try:
            if last_updated_timestamp != "Unknown":
                # Try to parse the ISO timestamp and format it nicely
                try:
                    dt = datetime.fromisoformat(last_updated_timestamp.replace('Z', '+00:00'))
                    local_dt = dt.astimezone()  # Convert to local timezone
                    formatted_time = local_dt.strftime("%Y-%m-%d %H:%M:%S %Z")
                    last_updated = formatted_time
                except:
                    last_updated = last_updated_timestamp
            else:
                last_updated = "Unknown"
        except Exception as e:
            last_updated = "Unknown"
            
        st.markdown(f"<div style='text-align: right; color: #666; font-size: 0.9em; margin-bottom: 1em;'>Last updated: {last_updated}</div>", unsafe_allow_html=True)
        
        # First box - Consolidated Traffic Summary
        st.markdown('<div class="metric-box"><div class="chart-header">Consolidated Traffic Summary</div>', unsafe_allow_html=True)
        st.dataframe(df_sorted.set_index("Repository"), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Second box - Total Views and Stars by Repository
        st.markdown('<div class="metric-box"><div class="chart-header">Total Views and Stars by Repository</div>', unsafe_allow_html=True)
        chart_df = df_sorted.set_index("Repository")[["Views", "Stars"]]
        st.bar_chart(chart_df, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Third box - Total Unique Visitors by Repository
        st.markdown('<div class="metric-box"><div class="chart-header">Total Unique Visitors by Repository</div>', unsafe_allow_html=True)
        chart_df2 = df_sorted.set_index("Repository")[["Unique Visitors"]]
        st.bar_chart(chart_df2, use_container_width=True)
        st.markdown('</div></div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error loading or visualizing data: {e}")

if __name__ == "__main__":
    run_streamlit_app()