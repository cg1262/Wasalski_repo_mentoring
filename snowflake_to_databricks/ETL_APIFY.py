# Databricks notebook source
# to keyvault

apify_secret=''

# COMMAND ----------

import requests
import pandas as pd
import time
import os

class ApifyActors():
    def __init__(self):
        self.apify_secret = apify_secret
    def get_actors(self): 

        url =  f"https://api.apify.com/v2/acts"

        payload = {}
        headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {self.apify_secret}'
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        # response_data = response.json()
        items = response.json().get("data", {}).get("items", [])
        actors = pd.DataFrame(items)
        
        actors['total_runs'] = actors['stats'].apply(lambda x: x.get('totalRuns') if isinstance(x, dict) else None)
        actors['last_run_started_at'] = actors['stats'].apply(lambda x: x.get('lastRunStartedAt') if isinstance(x, dict) else None)
        actors = actors.rename(columns={'stats': 'raw_stats'})
        return actors
    
    def get_actor_runs(self):
        url = "https://api.apify.com/v2/actor-runs"
        payload = {}
        headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {self.apify_secret}'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        return pd.DataFrame(response.json().get('data', {}).get('items', []))
    
    def get_unique_actor_runs(self):
        return self.get_actor_runs()['id'].unique().tolist()

    def get_run(self):
        runs_list = []
        for i in self.get_unique_actor_runs():
            url = f"https://api.apify.com/v2/actor-runs/{i}"
            headers = {
                'Accept': 'application/json',
                'Authorization': f'Bearer {self.apify_secret}'
            }
            

            response = requests.get(url, headers=headers)  # Cleaner than requests.request
            response.raise_for_status()  # Raises exception for bad status codes
            data = response.json().get('data', {})
            runs_list.append(data)

            
        runs = pd.DataFrame(runs_list)
        
        runs['startedAt'] = pd.to_datetime(runs['startedAt'])
        runs['finishedAt'] = pd.to_datetime(runs['finishedAt'])
        
        runs['time_to_load_in_sec'] = (runs['finishedAt'] - runs['startedAt']).dt.total_seconds()
        runs['time_to_load_in_min'] = runs['time_to_load_in_sec'] / 60
        
        runs['pages_scraped'] = runs['usage'].apply(lambda x: x.get('DATASET_WRITES') if isinstance(x, dict) else None)
        runs['pages_scraped_per_sec'] = (runs['pages_scraped'] / runs['time_to_load_in_sec']).round(2)
        
        def minutes_to_hhmmss_format(minutes):
            if pd.isna(minutes):
                return None
            
            total_seconds = int(minutes * 60)
            hours = total_seconds // 3600
            remaining_seconds = total_seconds % 3600
            mins = remaining_seconds // 60
            secs = remaining_seconds % 60
            
            return f"{hours:02d}:{mins:02d}:{secs:02d}"
        
        runs['duration'] = runs['time_to_load_in_min'].apply(minutes_to_hhmmss_format)
        
        runs['startedAt'] = runs['startedAt'].dt.strftime('%Y-%m-%d %H:%M:%S')
        runs['finishedAt'] = runs['finishedAt'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        return runs
    
api = ApifyActors()

# COMMAND ----------

get_run = api.get_run()
display(get_run)

# COMMAND ----------

get_actor_runs = api.get_actor_runs()
display(get_actor_runs)

# COMMAND ----------

get_actors = api.get_actors()
display(get_actors)