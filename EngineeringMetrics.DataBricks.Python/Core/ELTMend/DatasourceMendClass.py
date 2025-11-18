"""
DatasourceMendClass.py - ETL Module
Created automatically
"""
from Core.AbstractDatasourceClass import AbstractDatasourceClass
from Core.ELTMend.ServicesMend.ServiceMendBronze import ServiceBronze
from Core.ELTMend.ServicesMend.ServiceMendSilver import ServiceSilver
from pyspark.sql import SparkSession

class DatasourceMendClass(AbstractDatasourceClass):
    def __init__(self, dbutils, spark):
        super().__init__()
        self.spark = SparkSession.builder.getOrCreate()
        self.bronze_service = ServiceBronze(dbutils, spark)
        self.silver_service = ServiceSilver(spark)
        self.catalog = 'engineering_metrics'
        self.db_bronze = 'bronze'
        self.db_silver = 'silver'
        self.prefix = 'mend_'
        

    def bronzeprocessing(self, data=None):
        """
        extracting raw data from Mend
        as return we will have dict of dataframes
        1. applications
        2. projects
        3. alert_types
        4. vulnerabilities_project
        5. alerts_severity
        6. alerts_per_project
        7. libraries
        8. license_policy_violations
        9. project_due_diligence
        10. alerts_per_library

        """

        dict_bronze = {
            'applications': self.bronze_service.applications,
            'projects':self.bronze_service.projects,
            'alert_types':self.bronze_service.alert_types,
            'vulnerabilities_project':self.bronze_service.vulnerabilities_project,
            'alerts_severity':self.bronze_service.alerts_severity,
            'alerts_per_project':self.bronze_service.alerts_per_project,
            'libraries':self.bronze_service.libraries,
            'license_policy_violations':self.bronze_service.license_policy_violations,
            'project_due_diligence':self.bronze_service.project_due_diligence,
            'alerts_per_library':self.bronze_service.alerts_per_library,
            'labels':self.bronze_service.labels
        }
        length_dict = len(dict_bronze)
        count = 1
        
        
        print("=" * 10)
        print("Mend bronze layer")
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
            'products': [self.silver_service.products, "merge"],
            'projects': [self.silver_service.projects, "merge"],
            'alert_types': [self.silver_service.alert_types, "merge"],
            'alerts_severity': [self.silver_service.alerts_severity, "merge"],
            'security_alerts_per_library': [self.silver_service.security_alerts_per_library, "merge"],
            'project_due_diligence': [self.silver_service.project_due_diligence, "merge"],
            'vulnerabilities_project': [self.silver_service.vulnerabilities_project, "merge"],
            'labels': [self.silver_service.labels, "merge"],
            'security_alerts_per_project': [self.silver_service.security_alerts_per_project, "merge"],
            'libraries': [self.silver_service.libraries, "merge"],
            'license_policy_violations': [self.silver_service.license_policy_violations, "merge"],
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
        print("Done: Mend gold layer")
        print("=" * 15)