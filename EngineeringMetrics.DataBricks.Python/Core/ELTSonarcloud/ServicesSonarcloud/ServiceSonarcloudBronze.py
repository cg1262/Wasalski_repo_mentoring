import requests
import pandas as pd
import time
import datetime
# Start time
import time
from pyspark.sql import SparkSession
from delta.tables import *
from concurrent.futures import ThreadPoolExecutor, as_completed
from pyspark.sql import SparkSession

from Core.Services.ServiceSaveToDelta import upserting_data

class ServiceBronze:
    
    def __init__(self, dbutils, spark):

        self.spark = spark
        self.sonarcloud_secret = dbutils.secrets.get(scope = "engineering-metrics-keys", key = "sonarcloud-secret-key")

        self.headers = {"Authorization": f"Bearer {self.sonarcloud_secret}"}
        self.organization = 'phlexglobal'

        self.page_size = 500
        self.page_number = 1

        self.months = range(1,13)
        self.current_year = datetime.datetime.now().year

        self.basic_url = "https://sonarcloud.io/api/"
        self.metrics_keys = [
            'accepted_issues', 'files', 'ncloc', 'maintainability_issues', 'reliability_issues',
            'security_hotspots', 'security_issues', 'line_coverage',
            'duplicated_lines', 'duplicated_lines_density'
        ]
        
    def components(self, url = 'components/search', checking_data = None):
        params = {
                "organization": self.organization, 
                "ps": self.page_size, 
                "p": self.page_number    
        }
    
        all_components = [] 
    
        total_sonarcloud_api_key = 0 
    

        url_components = f"{self.basic_url}{url}"
        response_components = requests.get(f"{self.basic_url}{url}", headers=self.headers, params=params)
        components_data = response_components.json()

        total_sonarcloud_api_key = components_data['paging']['total']
        total_pages = (total_sonarcloud_api_key // params['ps']) + (1 if total_sonarcloud_api_key % params['ps'] > 0 else 0)
    

        all_components.extend(components_data['components'])
    
        while params["p"] < total_pages:
            params["p"] += 1 
            response_components = requests.get(url_components, headers=self.headers, params=params)
            components_data = response_components.json()
            
            all_components.extend(components_data['components'])
    
        dataframe_pd = pd.DataFrame(all_components)
        dataframe_pd = dataframe_pd.apply(lambda x: x.astype(str))
        dataframe_spark = self.spark.createDataFrame(dataframe_pd)

        if checking_data != True:
            upserting_data(
                target_table_name = "sonarcloud_components",
                source_dataframe = dataframe_spark,
                target_column = "key",
                source_column = "key")
        
        return dataframe_spark
        

    
    def unique_components(self):
        unique = (
            self.components()
            .select('key')
            .distinct()
            .collect()
        )
        return unique
        

    def measures_component(self, url='measures/component', checking_data=None):
        """
        Fetch SonarCloud measures - one row per component-metric combination.
        """

        url_labels = f"{self.basic_url}{url}"

        all_measures_component = []

        def fetch_single_metric(comp_id, metric):
            response = requests.get(
                url_labels,
                headers=self.headers,
                params={
                    "organization": self.organization,
                    "metricKeys": metric,
                    "component": comp_id
                },
                timeout=30
            )
            labels_data = response.json()
            component_data = labels_data.get('component', {})
            component_data['metric'] = metric  # Optionally add metric info
            return component_data

        # Get list of component keys
        components = [row['key'] for row in self.unique_components()]

        # Generate all (component, metric) combinations
        tasks = [(comp_id, metric) for comp_id in components for metric in self.metrics_keys]

        with ThreadPoolExecutor(max_workers=15) as executor:
            all_measures_component = list(
                executor.map(lambda args: fetch_single_metric(*args), tasks)
            )

        dataframe_pd = pd.DataFrame(all_measures_component)
        dataframe_pd['upsert_key'] = dataframe_pd['key'] + dataframe_pd['metric']
        dataframe_pd = dataframe_pd.apply(lambda x: x.astype(str))
        dataframe_spark = self.spark.createDataFrame(dataframe_pd)
        # Deduplicate on the merge keys before upsert
        dataframe_spark = dataframe_spark.dropDuplicates(['key', 'metric'])

        # Proceed with your upsert logic
        if checking_data != True:
            upserting_data(
                target_table_name="sonarcloud_measures_component",
                source_dataframe=dataframe_spark,
                target_column="upsert_key",
                source_column="upsert_key"
            )

        return dataframe_spark

    def issues(self, url='issues/search', checking_data=None):

            all_issues = []  
            year_tofind = 2022
            url_issues = f"{self.basic_url}{url}"
            # iterates through years starting from 2017 up to current year
            while year_tofind <= self.current_year:
                # iterates through all months (1-12) for each year
                for month in self.months:
                    params = {
                        "organization": self.organization, 
                        "ps": self.page_size,  
                        "p": self.page_number ,     
                        "createdBefore": f"{year_tofind}-{month+1:02d}-01",  
                        "createdAfter": f"{year_tofind}-{month:02d}-01",     
                    }

                    response_issues = requests.get(url_issues, headers=self.headers, params=params)

                    issues_data = response_issues.json()
        

                    total_sonarcloud_api_key = issues_data.get('paging', {}).get('total', 0)
        
                    # skip to next month if no sonarcloud_api_key found for current month
                    if total_sonarcloud_api_key == 0:
                        continue
        
                    # Calculate total number of pages based on total sonarcloud_api_key and page size
                    # If there's a remainder, add one more page
                    total_pages = (total_sonarcloud_api_key // params['ps']) + (1 if total_sonarcloud_api_key % params['ps'] > 0 else 0)
        
                    all_issues.extend(issues_data.get('issues', []))
        
                    # Pagination loop - fetch all remaining pages of sonarcloud_api_key
                    while params["p"] < total_pages:
                        params["p"] += 1 

                        response_issues = requests.get(url_issues, headers=self.headers, params=params)

                        issues_data = response_issues.json()

                        all_issues.extend(issues_data.get('issues', []))
        
                year_tofind += 1

            dataframe_pd = pd.DataFrame(all_issues)
            dataframe_pd['upsert_key'] = dataframe_pd['key'] + dataframe_pd['rule']
            dataframe_pd = dataframe_pd.apply(lambda x: x.astype(str))
            dataframe_spark = self.spark.createDataFrame(dataframe_pd)
            dataframe_spark = dataframe_spark.dropDuplicates(['key', 'rule'])
            if checking_data != True:
                upserting_data(
                    target_table_name="sonarcloud_issues",
                    source_dataframe=dataframe_spark,
                    target_column="upsert_key",
                    source_column="upsert_key"
                )

            return dataframe_spark
        
    def metrics(self, url='metrics/search', checking_data=None):
        url_metrics = f"{self.basic_url}{url}"
        params = {
            "organization": self.organization,
            "ps": self.page_size,  
            "p": self.page_number     
        }
    

        response_raw = requests.get(url_metrics, headers=self.headers, params=params)
        metrics_data = response_raw.json()['metrics']
    
        dataframe_pd = pd.DataFrame(metrics_data)
        dataframe_pd = dataframe_pd.apply(lambda x: x.astype(str))
        dataframe_spark = self.spark.createDataFrame(dataframe_pd)

        if checking_data != True:
                upserting_data(
                    target_table_name="sonarcloud_metrics",
                    source_dataframe=dataframe_spark,
                    target_column="id",
                    source_column="id"
                )


        return dataframe_spark

    def projects(self, url='projects/search', checking_data=None): 

        url_projects = f"{self.basic_url}{url}"
        params = {
            "organization": self.organization,
            "ps": self.page_size, 
            "p": self.page_number      
        }

        all_projects = [] 
        total_sonarcloud_api_key = 0 
    
        response_raw = requests.get(url_projects, headers=self.headers, params=params)
        labels_data = response_raw.json()

        total_sonarcloud_api_key = labels_data['paging']['total']
        total_pages = (total_sonarcloud_api_key // params['ps']) + (1 if total_sonarcloud_api_key % params['ps'] > 0 else 0)
    

        all_projects.extend(labels_data['components'])
    

        while params["p"] < total_pages:
            params["p"] += 1  # Go to the next page
            response_raw = requests.get(url_projects, headers=self.headers, params=params)
            labels_data = response_raw.json()
            
            all_projects.extend(labels_data['components'])
    
    
        dataframe_pd = pd.DataFrame(all_projects)
        dataframe_pd = dataframe_pd.apply(lambda x: x.astype(str))
        dataframe_spark = self.spark.createDataFrame(dataframe_pd)

        if checking_data != True:
                upserting_data(
                    target_table_name="sonarcloud_projects",
                    source_dataframe=dataframe_spark,
                    target_column="key",
                    source_column="key"
                )


        return dataframe_spark