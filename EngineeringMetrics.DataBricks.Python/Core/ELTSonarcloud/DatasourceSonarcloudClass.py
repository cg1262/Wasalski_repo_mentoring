"""
DatasourceSonarcloudClass.py - ETL Module
Created automatically
"""
from Core.AbstractDatasourceClass import AbstractDatasourceClass
from Core.ELTSonarcloud.ServicesSonarcloud.ServiceSonarcloudBronze import ServiceBronze
from Core.ELTSonarcloud.ServicesSonarcloud.ServiceSonarcloudSilver import ServiceSilver
from pyspark.sql import SparkSession

class DatasourceSonarcloudClass(AbstractDatasourceClass):
    def __init__(self, dbutils, spark):
        super().__init__()
        self.spark = SparkSession.builder.getOrCreate()
        self.bronze_service = ServiceBronze(dbutils, spark)
        self.silver_service = ServiceSilver(spark)
        self.catalog = 'engineering_metrics'
        self.db_bronze = 'bronze'
        self.db_silver = 'silver'
        self.prefix = 'sonarcloud_'
        

    def bronzeprocessing(self, data=None):
        """
        extracting raw data from Sonarcloud
        as return we will have dict of dataframes
        1.components
        2.metrics
        1. projects
        2. issues
        3. measures_component
        """

        dict_bronze = {
            # 'components': self.bronze_service.components,
            # 'metrics':self.bronze_service.metrics,
            # 'projects':self.bronze_service.projects,
            # 'issues':self.bronze_service.issues,
            'measures_component':self.bronze_service.measures_component
        }
        length_dict = len(dict_bronze)
        count = 1
        
        
        print("=" * 10)
        print("Sonarcloud bronze layer")
        print("=" * 15)


        for key, func in dict_bronze.items():
            # iterate over the dictionary, where key = endpoint name (e.g. 'services'),
            # func = reference to the function (e.g. get_services without parentheses)

            print(f"\nStarting  - {count} of {length_dict} datasets")
            print(f"Amount of function to call: {length_dict}")
            print(f"Calling function for key: {key}")

            # call the function (HERE we add parentheses) to get DataFrame from API
            # e.g. func() is like self.bronze_service.get_services and at the end we add () to call this function
            df = func()
            # save DataFrame to parquet file with prefix from self.prefix and key name
            # e.g. Sonarcloud_services.parquet
            # this will also be used later for upsert to the database
            count += 1
            # spark dataframe is being created in the service class
            
            # table_name = f"{self.catalog}.{self.db}.{self.prefix}{key}_test"
            # df.write.mode("overwrite").saveAsTable(f"{self.catalog}.{self.db}.{self.prefix}{key}_test")

            # print(f"created {self.catalog}.{self.db}.{self.prefix}{key}_test table")
            print(f"Upserted data to {self.catalog}.{self.db_bronze}.{self.prefix}{key}")
        return df
    



    def silverprocessing(self, data=None):
        """
        Process silver layer datasets and apply the specified update mode.
        """

        dict_silver = {
            'components': [self.silver_service.components, "merge"],
            'metrics': [self.silver_service.metrics,"merge"],
            'projects': [self.silver_service.projects,"merge"],
            'issues': [self.silver_service.issues,"merge"],
            'measures_component': [self.bronze_service.measures_component,"merge"]
        }

        length_dict = len(dict_silver)
        count = 1

        print("=" * 10)
        print("pagerduty silver layer")
        print("=" * 15)

        for key, (func, mode) in dict_silver.items():
            print(f"\nStarting  - {count} of {length_dict} datasets")
            print(f"Amount of function to call: {length_dict}")
            print(f"Calling function for key: {key}")

            df = func()
            count += 1
            print(f"Updated table {self.catalog}.{self.db_silver}.{self.prefix}{key}, type of update: {mode}")

        print("=" * 15)

    def goldprocessing(self, data=None):
        print("\n" + "=" * 15)
        print(f"Gold layer data:")
        print("=" * 10)

        print("\n" + "=" * 10)
        print("Done: Sonarcloud gold layer")
        print("=" * 15)