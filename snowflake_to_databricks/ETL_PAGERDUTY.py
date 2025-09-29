# Databricks notebook source
secret = ''

# COMMAND ----------

try:
    import requests
    import pandas as pd
    import time

class PagerdutyApi:

    def __init__(self):
        self.secret = secret  
        self.headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Token token={self.secret}"
            }
    
    def get_services(self):
        
        url = "https://api.pagerduty.com/services"
        offset = 0
        total_count = 0
        limit = 100
        data_list = []
        
        while True:
            params = {
                "limit": limit,
                "offset": offset
            }
    
            response = requests.get(url, headers=self.headers, params=params)
            data = response.json()
            data_list.extend(data['services'])
            total_count += len(data['services'])
            if not data.get('more', False):
                    break
                    
            offset += limit
        data_df = pd.DataFrame(data_list) 
        return data_df
    

    
    def get_unique_services(self):
        
        data_unique = self.get_services()['id'].unique().tolist()     
        return data_unique
    
    def get_services_details(self):
    
        data_list = []
        total_count = 0
        offset = 0
        
        for i in self.get_unique_services():
            url = f"https://api.pagerduty.com/services/{i}"
    
    
            limit = 100
        
            while True:
                params = {
                    "limit": limit,
                    "offset": offset
                }
    
                response = requests.get(url, headers=self.headers, params=params)
                data = response.json()
                data_list.append(data['service'])
                total_count += len(data['service'])
                if not data.get('more', False):
                        break
                        
                offset += limit
        data_df =  pd.json_normalize(data_list)
     
        return data_df

    def get_incidents(self):
        
        url = "https://api.pagerduty.com/incidents"
        offset = 0
        total_count = 0
        limit = 100
        data_list = []
        
        while True:
            params = {
                "limit": limit,
                "offset": offset
            }
    
            response = requests.get(url, headers=self.headers, params=params)
            data = response.json()
            data_list.extend(data['incidents'])
            total_count += len(data['incidents'])
            if not data.get('more', False):
                    break
                    
            offset += limit
        data_df = pd.DataFrame(data_list) 
        return data_df

pagerduty = PagerdutyApi()
