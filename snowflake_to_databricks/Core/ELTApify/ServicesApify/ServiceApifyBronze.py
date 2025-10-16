import requests
from requests.auth import HTTPBasicAuth
import pandas as pd
import json
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
import time

# in config file password are being stored, to be changed after deployment to databricks
from config import apify_secret
api_token = apify_secret

class ServiceBronze:
    """
    Interacting with Apify API
    """
    
    def __init__(self):
        """
        Initialize Apify client.
        
        Args:
            apify_secret: Apify API authentication token
            headers: Authorization headers
        """
        self.apify_secret = api_token
        self.headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.apify_secret}'
        }
    
    def get_actors(self):
        """
        All actors
        
        Returns:
            df
        """
        url = f"https://api.apify.com/v2/acts"
        headers = {
                'Accept': 'application/json',
                'Authorization': f'Bearer {self.apify_secret}'
            }
            
        response = requests.get(url, headers=headers)
        response.raise_for_status()
            
        items = response.json().get("data", {}).get("items", [])
        
        actors = pd.DataFrame(items)
        return actors
        
    
    def get_actor_runs(self):
        """
        All actor runs
        
        Returns:
            df
        """
        
        url = f"https://api.apify.com/v2/actor-runs"
        headers = {
                'Accept': 'application/json',
                'Authorization': f'Bearer {self.apify_secret}'
            }
            
        response = requests.get(url, headers=headers)
        response.raise_for_status()
            
        items = response.json().get('data', {}).get('items', [])
            
        actor_runs = pd.DataFrame(items)
        return actor_runs
        

    def get_unique_actor_runs(self):
        return self.get_actor_runs()['id'].unique().tolist()
    
    
    def get_actor_runs_details(self):
        def fetch_single_run(run_id):
            """ details for given run
            """
            url = f"https://api.apify.com/v2/actor-runs/{run_id}"
            headers = {
                'Accept': 'application/json',
                'Authorization': f'Bearer {self.apify_secret}'
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json().get('data', {})

        with ThreadPoolExecutor(max_workers=15) as executor:
            runs_detailed_list = list(executor.map(fetch_single_run, self.get_unique_actor_runs()))

        runs_detailed_df = pd.DataFrame(runs_detailed_list)
    
        runs_detailed_df['startedAt'] = pd.to_datetime(runs_detailed_df['startedAt'])
        runs_detailed_df['finishedAt'] = pd.to_datetime(runs_detailed_df['finishedAt'])
        
        runs_detailed_df['time_to_load_in_sec'] = (runs_detailed_df['finishedAt'] - runs_detailed_df['startedAt']).dt.total_seconds()
        runs_detailed_df['time_to_load_in_min'] = runs_detailed_df['time_to_load_in_sec'] / 60
        
        runs_detailed_df['pages_scraped'] = runs_detailed_df['usage'].apply(lambda x: x.get('DATASET_WRITES') if isinstance(x, dict) else None)
        runs_detailed_df['pages_scraped_per_sec'] = (runs_detailed_df['pages_scraped'] / runs_detailed_df['time_to_load_in_sec']).round(2)

        return runs_detailed_df