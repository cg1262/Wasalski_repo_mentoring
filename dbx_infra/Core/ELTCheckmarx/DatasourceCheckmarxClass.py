"""
DatasourceCheckmarxClass.py - ETL Module
Created automatically
"""
from Core.AbstractDatasourceClass import AbstractDatasourceClass
from Core.ELTCheckmarx.ServicesCheckmarx.ServiceCheckmarxBronze import ServiceBronze
from Core.ELTCheckmarx.ServicesCheckmarx.ServiceCheckmarxSilver import ServiceSilver
from pyspark.sql import SparkSession

class DatasourceCheckmarxClass(AbstractDatasourceClass):
    def __init__(self, dbutils, spark):
        super().__init__()
        self.spark = SparkSession.builder.getOrCreate()
        self.bronze_service = ServiceBronze(dbutils, spark)
        self.silver_service = ServiceSilver(spark)
        self.catalog = 'engineering_metrics'
        self.db_bronze = 'bronze'
        self.db_silver = 'silver'
        self.prefix = 'checkmarx_'
        

    def bronzeprocessing(self, data=None):
        """
        extracting raw data from checkmarx
        as return we will have dict of dataframes
        1. applications
        2. scans
        """

        dict_bronze = {

            # 'applications': self.bronze_service.applications,
            'scans':self.bronze_service.scans

        }
        length_dict = len(dict_bronze)
        count = 1
        
        
        print("=" * 10)
        print("checkmarx bronze layer")
        print("=" * 15)


        for key, func in dict_bronze.items():

            print(f"\nStarting  - {count} of {length_dict} datasets")
            print(f"Amount of function to call: {length_dict}")
            print(f"Calling function for key: {key}")
            df = func()
            count += 1

            print(f"Upserted data to {self.catalog}.{self.db}.{self.prefix}{key}")
        return df
    


    def silverprocessing(self, data=None):
        """
        Process silver layer datasets and apply the specified update mode.
        """
        dict_silver = {
            'scans': [self.silver_service.scans, "merge"],
            # 'labels': [self.silver_service.labels, "merge"],
        }

        length_dict = len(dict_silver)
        count = 1

        print("=" * 10)
        print("mend silver layer")
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
        print("Done: checkmarx gold layer")
        print("=" * 15)