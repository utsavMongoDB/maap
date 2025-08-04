import requests
import json
import os
from datetime import datetime
import streamlit as st
import pandas as pd

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
            'clones': self.get_clones(owner, repo),
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
    
    def get_clones(self, owner, repo):
        """Get repository clone statistics"""
        url = f"{self.base_url}/repos/{owner}/{repo}/traffic/clones"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching clones: {response.status_code} - {response.text}")
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
        
        if data['clones']:
            print(f"\nClones (last 14 days):")
            print(f"  Total clones: {data['clones']['count']}")
            print(f"  Unique cloners: {data['clones']['uniques']}")
        
        if data['referrers']:
            print(f"\nTop Referrers:")
            for ref in data['referrers'][:5]:  # Show top 5
                print(f"  {ref['referrer']}: {ref['count']} views")
        
        if data['paths']:
            print(f"\nPopular Paths:")
            for path in data['paths'][:5]:  # Show top 5
                print(f"  {path['path']}: {path['count']} views")


def run_streamlit_app():
    st.title("GitHub Repo Traffic Visualizer")
    st.markdown("Enter your GitHub token, owner, and repo to visualize traffic data.")

    with st.form("github_form"):
        token = st.text_input("GitHub Personal Access Token", type="password")
        owner = st.text_input("Repository Owner", value="mongodb-partners")
        repo = st.text_input("Repository Name", value="maap-framework")
        submit = st.form_submit_button("Get Traffic Data")

    if submit:
        if not token or not owner or not repo:
            st.error("Please provide all required fields.")
            return
        try:
            collector = GitHubTrafficCollector(token=token)
            st.info(f"Collecting traffic data for {owner}/{repo}...")
            traffic_data = collector.get_repo_traffic(owner, repo)
            st.success("Traffic data collected!")

            # Views Bar Graph
            if traffic_data['views'] and 'views' in traffic_data['views']:
                views_df = pd.DataFrame(traffic_data['views']['views'])
                views_df['date'] = pd.to_datetime(views_df['timestamp']).dt.date
                st.subheader("Repository Views (last 14 days)")
                st.bar_chart(views_df.set_index('date')[['count', 'uniques']])

            # Clones Bar Graph
            if traffic_data['clones'] and 'clones' in traffic_data['clones']:
                clones_df = pd.DataFrame(traffic_data['clones']['clones'])
                clones_df['date'] = pd.to_datetime(clones_df['timestamp']).dt.date
                st.subheader("Repository Clones (last 14 days)")
                st.bar_chart(clones_df.set_index('date')[['count', 'uniques']])

            # Optionally show summary
            st.subheader("Summary")
            st.write(f"**Repository:** {traffic_data['repository']}")
            st.write(f"**Collected At:** {traffic_data['collected_at']}")
            if traffic_data['views']:
                st.write(f"**Total Views:** {traffic_data['views']['count']}")
                st.write(f"**Unique Visitors:** {traffic_data['views']['uniques']}")
            if traffic_data['clones']:
                st.write(f"**Total Clones:** {traffic_data['clones']['count']}")
                st.write(f"**Unique Cloners:** {traffic_data['clones']['uniques']}")

        except Exception as e:
            st.error(f"Error collecting traffic data: {e}")

if __name__ == "__main__":
    run_streamlit_app()