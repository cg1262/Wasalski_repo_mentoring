"""
DatasourceAzureDevopsClass.py - ETL Module
Created automatically
"""

from Core.AbstractDatasourceClass import AbstractDatasourceClass
from Core.ELTAzureDevops.ServicesAzureDevops.ServiceAzureDevopsBronze import ServiceBronze
from Core.ELTAzureDevops.ServicesAzureDevops.ServiceAzureDevopsSilver import ServiceSilver
from pyspark.sql import SparkSession

class DatasourceAzureDevopsClass(AbstractDatasourceClass):
    def __init__(self, dbutils, spark):
        super().__init__()
        self.spark = SparkSession.builder.getOrCreate()
        self.bronze_service = ServiceBronze(dbutils, spark)
        self.silver_service = ServiceSilver(spark)
        self.catalog = 'engineering_metrics'
        self.db_bronze = 'bronze'
        self.db_silver = 'silver'
        self.prefix = 'azure_devops_'


    def bronzeprocessing(self, data=None):
        """
        extracting raw data from Azure DevOps
        as return we will have dict of dataframes
        1. projects
        2. pipeline_runs
        3. approvals
        4. repos
        5. definitions
        6. pipelines
        7. source_providers
        8. builds
        9. pull_requests
        10. branches
        11. commits

        """

        dict_bronze = {
            'projects': self.bronze_service.projects,
            'pipeline_runs': self.bronze_service.pipeline_runs,
            'approvals': self.bronze_service.approvals,
            'repos': self.bronze_service.repos,
            'definitions': self.bronze_service.definitions,
            'pipelines': self.bronze_service.pipelines,
            'source_providers': self.bronze_service.source_providers,
            'builds': self.bronze_service.builds,
            'pull_requests': self.bronze_service.pull_requests,
            'branches': self.bronze_service.branches,
            'commits': self.bronze_service.commits
        }
        length_dict = len(dict_bronze)
        count = 1


        print("=" * 10)
        print("Azure DevOps bronze layer")
        print("=" * 15)


        for key, func in dict_bronze.items():

            print(f"\nStarting  - {count} of {length_dict} datasets")
            print(f"Amount of function to call: {length_dict}")
            print(f"Calling function for key: {key}")

            df = func()
            count += 1

            print(f"Upserted data to {self.catalog}.{self.db_bronze}.{self.prefix}{key}")
        return df


    def silverprocessing(self, data=None):
        """
        Process silver layer datasets and apply the specified update mode.
        """

        dict_silver = {
            'commits': [self.silver_service.commits, "overwrite"],
            'projects': [self.silver_service.projects, "overwrite"],
            'pipeline_runs': [self.silver_service.pipeline_runs, "overwrite"],
            'approvals': [self.silver_service.approvals, "overwrite"],
            'repos': [self.silver_service.repos, "overwrite"],
            'branches': [self.silver_service.branches, "overwrite"],
            'pipeline_runs_agg': [self.silver_service.pipeline_runs_agg, "overwrite"],
            'pipeline_runs_agg_minutes_env': [self.silver_service.pipeline_runs_agg_minutes_env, "merge"],
            'pipeline_runs_agg_minutes_issue_key': [self.silver_service.pipeline_runs_agg_minutes_issue_key, "merge"],
            'builds': [self.silver_service.builds, "merge"],
            'pull_requests': [self.silver_service.pull_requests, "merge"],
            'aged_pull_requests': [self.silver_service.aged_pull_requests, "merge"],

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
        print("Done: Azure DevOps gold layer")
        print("=" * 15)
