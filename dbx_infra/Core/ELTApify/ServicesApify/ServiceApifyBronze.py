from requests.auth import HTTPBasicAuth
import time
import pandas as pd
from pyspark.sql import SparkSession
from delta.tables import *
from Core.Services.ServiceSaveToDelta import upserting_data
from Core.Services.ServiceFetchingDataFromApi import ServiceResponseApi

class ServiceBronze:
    """
    Interacting with Apify API
    """
    
    def __init__(self, dbutils, spark):
        """
        Initialize Apify client.
        
        Args:
            apify_secret: Apify API authentication token

        """
        self.spark = spark
        self.basic_url = "https://api.apify.com/v2/"
        self.service = ServiceResponseApi(dbutils, spark)

    def actors(self, suffix:str = "acts", checking_data = None):
        """
        All actors
        
        Returns:
            df
        """

        dataframe_spark = self.service.response_data_apify(basic_url = self.basic_url, url_suffix = suffix)
        
        if checking_data != True:
            upserting_data(
                target_table_name = "apify_actors",
                source_dataframe = dataframe_spark,
                target_column = "id",
                source_column = "id")
        
        return dataframe_spark
            
    
    def actor_runs(self, suffix:str = "actor-runs", checking_data = None):
        """
        All actor runs
        
        Returns:
            df
        """
 
        
        dataframe_spark = self.service.response_data_apify(basic_url = self.basic_url, url_suffix = suffix)

        if checking_data != True:
            upserting_data(
                target_table_name = "apify_actor_runs",
                source_dataframe = dataframe_spark,
                target_column = "id",
                source_column = "id")

        return dataframe_spark
        

    def unique_actor_runs(self):
        return [row['id'] for row in self.actor_runs().select('id').distinct().collect()]
    
    
    def actor_runs_details(self, suffix:str = "actor-runs",checking_data = None):
        # def fetch_single_run(run_id):
        #     """ 
        #     details for given run
        #     """
        #     url = f"https://api.apify.com/v2/actor-runs/{run_id}"

            
        #     response = requests.get(url, headers=self.headers)
        #     return response.json().get('data', {})

        # with ThreadPoolExecutor(max_workers=15) as executor:
        #     runs_detailed_list = list(executor.map(fetch_single_run, self.unique_actor_runs()))

        # dataframe_pd = pd.DataFrame(runs_detailed_list)   

        # dataframe_spark = self.spark.createDataFrame(dataframe_pd)

        # for c in actors.columns:
        #     actors = actors.withColumn(c, col(c).cast("string"))

        dataframe_pd = self.service.response_data_loops_apify(basic_url = self.basic_url, url_suffix = suffix, list_of_unique_elements = self.unique_actor_runs())

        dataframe_pd['startedAt'] = pd.to_datetime(dataframe_pd['startedAt'])
        dataframe_pd['finishedAt'] = pd.to_datetime(dataframe_pd['finishedAt'])
        
        dataframe_pd['time_to_load_in_sec'] = (dataframe_pd['finishedAt'] - dataframe_pd['startedAt']).dt.total_seconds()
        dataframe_pd['time_to_load_in_min'] = dataframe_pd['time_to_load_in_sec'] / 60
        
        dataframe_pd['pages_scraped'] = dataframe_pd['usage'].apply(lambda x: x.get('DATASET_WRITES') if isinstance(x, dict) else None)
        dataframe_pd['pages_scraped_per_sec'] = (dataframe_pd['pages_scraped'] / dataframe_pd['time_to_load_in_sec']).round(2)

        def minutes_to_hhmmss_format(minutes):
            if pd.isna(minutes):
                return None
            
            total_seconds = int(minutes * 60)
            hours = total_seconds // 3600
            remaining_seconds = total_seconds % 3600
            mins = remaining_seconds // 60
            secs = remaining_seconds % 60
            
            return f"{hours:02d}:{mins:02d}:{secs:02d}"
        
        dataframe_pd['duration'] = dataframe_pd['time_to_load_in_min'].apply(minutes_to_hhmmss_format)

        dataframe_pd = dataframe_pd.apply(lambda x: x.astype(str))
        
        dataframe_spark = self.spark.createDataFrame(dataframe_pd)

        if checking_data != True:
            upserting_data(
                target_table_name = "apify_actor_runs_details",
                source_dataframe = dataframe_spark,
                target_column = "id",
                source_column = "id")

        return dataframe_spark
    

    
#     
# SELECT 
#     *,
#     -- Convert string timestamps to timestamp type
#     CAST(startedAt AS TIMESTAMP) AS startedAt_ts,
#     CAST(finishedAt AS TIMESTAMP) AS finishedAt_ts,
    
#     -- Calculate time to load in seconds
#     UNIX_TIMESTAMP(CAST(finishedAt AS TIMESTAMP)) - UNIX_TIMESTAMP(CAST(startedAt AS TIMESTAMP)) AS time_to_load_in_sec,
    
#     -- Calculate time to load in minutes
#     (UNIX_TIMESTAMP(CAST(finishedAt AS TIMESTAMP)) - UNIX_TIMESTAMP(CAST(startedAt AS TIMESTAMP))) / 60.0 AS time_to_load_in_min,
    
#     -- Extract DATASET_WRITES from usage JSON/struct column
#     usage.DATASET_WRITES AS pages_scraped,
    
#     -- Calculate pages scraped per second
#     ROUND(
#         usage.DATASET_WRITES / 
#         NULLIF(UNIX_TIMESTAMP(CAST(finishedAt AS TIMESTAMP)) - UNIX_TIMESTAMP(CAST(startedAt AS TIMESTAMP)), 0),
#         2
#     ) AS pages_scraped_per_sec,
    
#     -- Duration in HH:MM:SS format
#     CASE 
#         WHEN finishedAt IS NULL OR startedAt IS NULL THEN NULL
#         ELSE CONCAT(
#             LPAD(CAST(FLOOR((UNIX_TIMESTAMP(CAST(finishedAt AS TIMESTAMP)) - UNIX_TIMESTAMP(CAST(startedAt AS TIMESTAMP))) / 3600) AS STRING), 2, '0'), ':',
#             LPAD(CAST(FLOOR(((UNIX_TIMESTAMP(CAST(finishedAt AS TIMESTAMP)) - UNIX_TIMESTAMP(CAST(startedAt AS TIMESTAMP))) % 3600) / 60) AS STRING), 2, '0'), ':',
#             LPAD(CAST((UNIX_TIMESTAMP(CAST(finishedAt AS TIMESTAMP)) - UNIX_TIMESTAMP(CAST(startedAt AS TIMESTAMP))) % 60 AS STRING), 2, '0')
#         )
#     END AS duration


############## sql query for silver layer explanation ##############
# FROM engineering_metrics.bronze.apify_actor_runs_details
# Breaking down the duration calculation:
# FLOOR(seconds / 3600) → hours
# FLOOR((seconds % 3600) / 60) → minutes
# seconds % 60 → seconds
# LPAD(value, 2, '0') → pads with zeros to ensure 2 digits
# CONCAT() → combines into HH:MM:SS format
# Alternative simpler approach (if you don't need the exact HH:MM:SS string format and can work with intervals):
# -- Returns an interval type that displays nicely
# CAST((finishedAt_ts - startedAt_ts) AS STRING) AS duration
# This would give you output like INTERVAL '1 02:30:45' DAY TO SECOND which is more native to SQL but might not match your exact format requirements.