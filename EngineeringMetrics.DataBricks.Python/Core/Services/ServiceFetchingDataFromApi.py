import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor


class ServiceResponseApi:    
    """
    Interacting with APIs
    """
    def __init__(self, dbutils, spark):
        """
        Initialize API client.
        """
        self.spark = spark
        self.apify_secret = dbutils.secrets.get(scope = "engineering-metrics-keys", key = "apify-secret-key")
        self.apify_headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.apify_secret}'
        }


        self.pagerduty_secret = dbutils.secrets.get(scope = "engineering-metrics-keys", key = "pagerduty-secret-key")
        self.pagerduty_headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Token token={self.pagerduty_secret}"
            }
        self.pagerduty_basic_url = "https://api.pagerduty.com/"
        self.pagerduty_limit = 100
    def response_data_apify(self, basic_url: str, url_suffix:str, headers: dict = None):
            """
            Generic method to get data from Apify API
            
            Args:
                url: API endpoint URL
            Returns:
                df
            """

            response = requests.get(f"{basic_url}{url_suffix}", headers=self.apify_headers)
                
            items = response.json().get('data', {}).get('items', [])
            
            dataframe_pd = pd.DataFrame(items)   

            dataframe_pd = dataframe_pd.apply(lambda x: x.astype(str))
            dataframe_spark = self.spark.createDataFrame(dataframe_pd)

            return dataframe_spark
        
    def response_data_loops_apify(self, basic_url: str, url_suffix:str, list_of_unique_elements = []):
            """
            Generic method to get detailed data from Apify API for multiple runs in parallel
            
            Args:
                url: API endpoint URL (e.g., 'actor-runs')
            Returns:
                Spark DataFrame with detailed run information
            """
            
            def fetch_single_run(item_id):
                """ 
                Fetch details for a given run
                """
                full_url = f"{basic_url}{url_suffix}/{item_id}"
                response = requests.get(full_url, headers=self.apify_headers)
                return response.json().get('data', {})

            # Fetch all runs in parallel
            with ThreadPoolExecutor(max_workers=15) as executor:
                runs_detailed_list = list(executor.map(fetch_single_run, list_of_unique_elements))
            
            # Convert to DataFrame
            dataframe_pd = pd.DataFrame(runs_detailed_list)   
            
            # Convert to strings
            # dataframe_pd = dataframe_pd.apply(lambda x: x.astype(str))
            # dataframe_spark = self.spark.createDataFrame(dataframe_pd)

            return dataframe_pd
    
    def response_data_pagerduty(self, extend_value:int):
            offset = 0
            total_count = 0
            data_list = []
            
            while True:
                params = {
                    "limit": self.pagerduty_limit,
                    "offset": offset
                }

                response = requests.get(f"{self.pagerduty_basic_url}{extend_value}", headers=self.pagerduty_headers, params=params)
                data = response.json()
                data_list.extend(data[f"{extend_value}"])
                total_count += len(data[f"{extend_value}"])
                if not data.get('more', False):
                        break
                    
                offset += self.pagerduty_limit
                        # Convert to DataFrame

            dataframe_pd = pd.DataFrame(data_list)   
            
            # Convert to strings
            dataframe_pd = dataframe_pd.apply(lambda x: x.astype(str))
            dataframe_spark = self.spark.createDataFrame(dataframe_pd)
            
            return dataframe_spark