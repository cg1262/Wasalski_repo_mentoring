"""
DatasourceJiraClass.py - ETL Module
Created automatically
"""

from Core.AbstractDatasourceClass import AbstractDatasourceClass
from Core.ELTJira.ServicesJira.ServiceJiraBronze import ServiceBronze
from Core.ELTJira.ServicesJira.ServiceJiraSilver import ServiceSilver
from pyspark.sql import SparkSession

class DatasourceJiraClass(AbstractDatasourceClass):
    def __init__(self, dbutils, spark):
        super().__init__()
        self.spark = SparkSession.builder.getOrCreate()
        self.bronze_service = ServiceBronze(dbutils, spark)
        self.silver_service = ServiceSilver(spark)
        self.catalog = 'engineering_metrics'
        self.db_bronze = 'bronze'
        self.db_silver = 'silver'
        self.prefix = 'jira_'
        

    def bronzeprocessing(self, data=None):
        """
        extracting raw data from Jira
        as return we will have dict of dataframes
        1. boards
        2. issue_fields
        3. projects
        4. users
        8. project_versions
        9. sprints
        10. issues_projects

        """

        dict_bronze = {
            # 'boards':self.bronze_service.boards,
            # 'issue_fields':self.bronze_service.issue_fields,
            # 'projects':self.bronze_service.projects,
            # 'users':self.bronze_service.users,
            # 'project_versions':self.bronze_service.project_versions,
            # 'sprints':self.bronze_service.sprints,
            'issues_projects':self.bronze_service.issues_projects
        }
        length_dict = len(dict_bronze)
        count = 1
        
        
        print("=" * 10)
        print("Jira bronze layer")
        print("=" * 15)


        for key, func in dict_bronze.items():
            print(f"\nStarting  - {count} of {length_dict} datasets")
            print(f"Amount of function to call: {length_dict}")
            print(f"Calling function for key: {key}")
            df = func()
            count += 1
            # table_name = f"{self.catalog}.{self.db}.{self.prefix}{key}_test"
            # df.write.mode("overwrite").saveAsTable(f"{self.catalog}.{self.db}.{self.prefix}{key}_test")

            # print(f"created {self.catalog}.{self.db}.{self.prefix}{key}_test table")
            print(f"Upserted data to {self.catalog}.{self.db}.{self.prefix}{key}")
        return df
    


    def silverprocessing(self, data=None):
        """
        Process silver layer datasets and apply the specified update mode.
        """

        dict_silver = {
            'users': [self.silver_service.users, "merge"],
            'boards': [self.silver_service.boards, "merge"],
            'projects': [self.silver_service.projects, "merge"],
            'project_versions': [self.silver_service.project_versions, "merge"],
            'sprints': [self.silver_service.sprints, "merge"],
            'sprint_issues': [self.silver_service.sprint_issues, "merge"],
            'issues_projects': [self.silver_service.issues_projects, "merge"],
            'issues_changes': [self.silver_service.issues_changes, "merge"],
            'issue_changes_owner_team_tls': [self.silver_service.issue_changes_owner_team_tls, "merge"],
            'change_lead_time': [self.silver_service.change_lead_time, "merge"],
            'risk_types': [self.silver_service.risk_types, "merge"],
            'risk_manager': [self.silver_service.risk_manager, "merge"],


            # 'sprints': [self.silver_service.sprints, "merge"],
            # 'issues_projects': [self.silver_service.issues_projects, "merge"],
            #     'projects': [self.silver_service.projects, "merge"],
            # 'project_versions': [self.silver_service.project_versions, "merge"],
            # 'sprints': [self.silver_service.sprints, "merge"],
            # 'issues_projects': [self.silver_service.issues_projects, "merge"]
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
        print("Done: Jira gold layer")
        print("=" * 15)