"""
DatasourceAzureDevopsClass.py - ETL Module
Created automatically
"""

from Core.AbstractDatasourceClass import AbstractDatasourceClass
from Core.ELTAzureDevops.ServicesAzureDevops.ServiceAzureDevopsBronze import ServiceBronze

class DatasourceAzureDevopsClass(AbstractDatasourceClass):
    def __init__(self):
        super().__init__()
        self.bronze_service = ServiceBronze()

    def bronzeprocessing(self, data=None):
        """
        extracting raw data from Azure Devops API
        as return we will have dict of dataframes
        1. get_ado_projects
        2. get_pipeline_runs
        3. get_ado_approvals
        4. get_ado_definitions
        5. get_ado_pipelines
        6. get_ado_source_providers
        7. get_ado_repos
        """

        bronze_data = {}

        print("=" * 10)
        print("Azure DevOps bronze layer")
        print("=" * 15)


        #########
        print("\nStarting ADO projects - 1 of 7 datasets")
        bronze_data['ado_projects'] = self.bronze_service.get_ado_projects()
        print(f"Output: {len(bronze_data['ado_projects'])} rows")
        #########
        print("\nStarting pipeline runs - 2 of 7 datasets")
        bronze_data['pipeline_runs'] = self.bronze_service.get_pipeline_runs()
        print(f"Output: {len(bronze_data['pipeline_runs'])} rows")
        #########
        print("\nStarting ADO approvals - 3 of 7 datasets")
        bronze_data['ado_approvals'] = self.bronze_service.get_ado_approvals()
        print(f"Output: {len(bronze_data['ado_approvals'])} rows")
        #########
        print("\nStarting ADO definitions - 4 of 7 datasets")
        bronze_data['ado_definitions'] = self.bronze_service.get_ado_definitions()
        print(f"Output: {len(bronze_data['ado_definitions'])} rows")
        #########
        print("\nStarting ADO pipelines - 5 of 7 datasets")
        bronze_data['ado_pipelines'] = self.bronze_service.get_ado_pipelines()
        print(f"Output: {len(bronze_data['ado_pipelines'])} rows")
        #########
        print("\nStarting ADO source providers - 6 of 7 datasets")
        bronze_data['ado_source_providers'] = self.bronze_service.get_ado_source_providers()
        print(f"Output: {len(bronze_data['ado_source_providers'])} rows")
        #########
        print("\nStarting ADO repos - 7 of 7 datasets")
        bronze_data['ado_repos'] = self.bronze_service.get_ado_repos()
        print(f"Output: {len(bronze_data['ado_repos'])} rows")
        #########


        print("\n" + "=" * 15)
        print("Done: Azure DevOps bronze layer")
        print("=" * 10)

        return bronze_data

    def silverprocessing(self, data=None):
        print("\n" + "=" * 15)
        print(f"Silver layer data:")
        print("=" * 10)

        print("\n" + "=" * 10)
        print("Done: Apify silver layer")
        print("=" * 15)

    def goldprocessing(self, data=None):
        print("\n" + "=" * 15)
        print(f"Gold layer data:")
        print("=" * 10)

        print("\n" + "=" * 10)
        print("Done: Apify gold layer")
        print("=" * 15)