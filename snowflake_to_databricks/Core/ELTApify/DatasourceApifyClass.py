"""
DatasourceApifyClass.py - ETL Module
Created automatically
"""
from Core.AbstractDatasourceClass import AbstractDatasourceClass
from Core.ELTApify.ServicesApify.ServiceApifyBronze import ServiceBronze

class DatasourceApifyClass(AbstractDatasourceClass):
    def __init__(self):
        super().__init__()
        self.bronze_service = ServiceBronze()

    def bronzeprocessing(self, data=None):
        """
        extracting raw data from Apify
        as return we will have dict of dataframes
        1. actors
        2. actor_runs
        3. actor_runs_details
        """

        bronze_data = {}

        print("=" * 10)
        print("Apify bronze layer")
        print("=" * 15)


        #########
        print("\nStarting actors - 1 of 3 datasets")
        bronze_data['actors'] = self.bronze_service.get_actors()
        print(f"Output: {len(bronze_data['actors'])} rows")
        #########
        print("\nStarting actor runs - 2 of 3 datasets")
        bronze_data['actor_runs'] = self.bronze_service.get_actor_runs()
        print(f"Output: {len(bronze_data['actor_runs'])} rows")
        #########
        print("\nStarting detailed actor runs - 3 of 3 datasets")
        bronze_data['actor_runs_details'] = self.bronze_service.get_actor_runs_details()
        print(f"Output: {len(bronze_data['actor_runs_details'])} rows")
        #########


        print("\n" + "=" * 15)
        print("Done: Apify bronze laye")
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