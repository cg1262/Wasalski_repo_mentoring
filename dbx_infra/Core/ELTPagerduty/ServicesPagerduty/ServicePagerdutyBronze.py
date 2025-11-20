import requests
import pandas as pd
# Start time
import time
from pyspark.sql import SparkSession
from Core.Services.ServiceFetchingDataFromApi import ServiceResponseApi
from Core.Services.ServiceSaveToDelta import upserting_data


class ServiceBronze:
    
    def __init__(self, dbutils, spark):
        self.spark = spark
        self.service = ServiceResponseApi(dbutils, spark)

    def incidents(self, extend_value = 'incidents', checking_data = True):
    
        dataframe_spark = self.service.response_data_pagerduty(
            extend_value = extend_value)
        
        if checking_data:
            upserting_data(
                target_table_name = "pagerduty_incidents",
                source_dataframe = dataframe_spark,
                target_column = "incident_number",
                source_column = "incident_number")
            
        return dataframe_spark


###########################

    # def services(self):
        
    #     url = "https://api.pagerduty.com/services"
    #     offset = 0
    #     total_count = 0
    #     limit = 100
    #     data_list = []
        
    #     while True:
    #         params = {
    #             "limit": limit,
    #             "offset": offset
    #         }
    
    #         response = requests.get(url, headers=self.headers, params=params)
    #         data = response.json()
    #         data_list.extend(data['services'])
    #         total_count += len(data['services'])
    #         if not data.get('more', False):
    #                 break
                    
    #         offset += limit
    #     data_df = pd.DataFrame(data_list) 
    #     data_df = data_df.drop(columns = ['addons','auto_resolve_timeout'])
    #     df_spark = self.spark.createDataFrame(data_df)
    #     return df_spark
    

    
    # def unique_services(self):
        
    #     data_unique = self.services()['id'].unique().tolist()
    #     # services = self.services()
    #     # data_unique = services.select("id").distinct().collect()

    #     return data_unique
    
    # def services_details(self):
    
    #     data_list = []
    #     total_count = 0
    #     offset = 0
        
    #     for i in self.unique_services():
    #         url = f"https://api.pagerduty.com/services/{i}"
    
    
    #         limit = 100
        
    #         while True:
    #             params = {
    #                 "limit": limit,
    #                 "offset": offset
    #             }
    
    #             response = requests.get(url, headers=self.headers, params=params)
    #             data = response.json()
    #             data_list.append(data['service'])
    #             total_count += len(data['service'])
    #             if not data.get('more', False):
    #                     break
                        
    #             offset += limit
    #     data_df =  pd.json_normalize(data_list)
    #     df_spark = self.spark.createDataFrame(data_df)
    #     return df_spark


