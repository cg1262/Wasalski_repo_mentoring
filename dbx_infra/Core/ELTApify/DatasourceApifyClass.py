"""
DatasourceApifyClass.py - ETL Module
Created automatically
"""
from Core.AbstractDatasourceClass import AbstractDatasourceClass
from Core.ELTApify.ServicesApify.ServiceApifyBronze import ServiceBronze
from Core.ELTApify.ServicesApify.ServiceApifySilver import ServiceSilver
from pyspark.sql import SparkSession

class DatasourceApifyClass(AbstractDatasourceClass):
    def __init__(self, dbutils, spark):
        super().__init__()
        self.spark = SparkSession.builder.getOrCreate() #theoretically i should get rid of this line in dbx
        self.bronze_service = ServiceBronze(dbutils, spark)
        self.silver_service = ServiceSilver(spark)
        self.catalog = 'engineering_metrics'
        self.db_bronze = 'bronze'
        self.db_silver = 'silver'
        self.prefix = 'apify_'


    def bronzeprocessing(self, data=None):
        """
        extracting raw data from apify
        as return we will have dict of dataframes
        1. actors
        2. actor_runs
        3. actor_runs_details
        """

        dict_bronze = {

            # without parentheses it's just a reference to the function, with parentheses it's a function call
            # here calling it would be redundant because it would execute immediately and assign to the key
            # instead we will call the function in the loop below
            'actors': self.bronze_service.actors,
            'actor_runs':self.bronze_service.actor_runs,
            'actor_runs_details':self.bronze_service.actor_runs_details
        }
        length_dict = len(dict_bronze)
        count = 1
                
        print("=" * 10)
        print("apify bronze layer")
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
            # e.g. apify_services.parquet
            # this will also be used later for upsert to the database
            count += 1
            # spark dataframe is being created in the service class
            
            # test_table_name = f"{self.catalog}.{self.db}.{self.prefix}{key}_test"
            # df.write.mode("overwrite").saveAsTable(test_table_name)

            # table_name = f"{self.catalog}.{self.db}.{self.prefix}{key}"
            # df.write.format('delta').option('mergeSchema','true').mode("append").saveAsTable(table_name)
            # print(f"created {table_name} table")

            # Upsert logic is now handled in ServiceApifyBronze methods
            # Each method (actors, actor_runs, actor_runs_details) does the merge internally
        print(f"Upserted data to {self.catalog}.{self.db_bronze}.{self.prefix}{key}")
    
        print("=" * 15)

    def silverprocessing(self, data=None):
        """
        Process silver layer datasets and apply the specified update mode.
        """

        dict_silver = {
            'actors': [self.silver_service.actors, "overwrite"],
            'actor_runs': [self.silver_service.actor_runs, "overwrite"],
            'actor_runs_details': [self.bronze_service.actor_runs_details, "overwrite"]
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
        print("Done: Apify gold layer")
        print("=" * 15)