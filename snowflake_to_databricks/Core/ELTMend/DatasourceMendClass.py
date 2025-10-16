"""
DatasourceMendClass.py - ETL Module
Created automatically
"""

from Core.AbstractDatasourceClass import AbstractDatasourceClass
from Core.ELTMend.ServicesMend.ServiceMendBronze import ServiceBronze

class DatasourceMendClass(AbstractDatasourceClass):
    def __init__(self):
        super().__init__()
        self.bronze_service = ServiceBronze()

    def bronzeprocessing(self, data=None):
        """
        extracting raw data from Mend (WhiteSource)
        as return we will have dict of dataframes
        1. applications
        2. projects
        3. alert_types
        4. vulnerabilities_project
        5. alerts_severity
        6. labels
        7. alerts_per_library
        8. alerts_per_project
        9. libraries
        10. license_policy_violations
        11. project_due_diligence
        """

        bronze_data = {}

        print("=" * 10)
        print("Mend bronze layer")
        print("=" * 15)


        #########
        print("\nStarting applications - 1 of 11 datasets")
        bronze_data['applications'] = self.bronze_service.get_applications()
        print(f"Output: {len(bronze_data['applications'])} rows")
        #########
        print("\nStarting projects - 2 of 11 datasets")
        bronze_data['projects'] = self.bronze_service.get_projects()
        print(f"Output: {len(bronze_data['projects'])} rows")
        #########
        print("\nStarting alert types - 3 of 11 datasets")
        bronze_data['alert_types'] = self.bronze_service.get_alert_types()
        print(f"Output: {len(bronze_data['alert_types'])} rows")
        #########
        print("\nStarting vulnerabilities project - 4 of 11 datasets")
        bronze_data['vulnerabilities_project'] = self.bronze_service.get_vulnerabilities_project()
        print(f"Output: {len(bronze_data['vulnerabilities_project'])} rows")
        #########
        print("\nStarting alerts severity - 5 of 11 datasets")
        bronze_data['alerts_severity'] = self.bronze_service.get_alerts_severity()
        print(f"Output: {len(bronze_data['alerts_severity'])} rows")
        #########
        print("\nStarting labels - 6 of 11 datasets")
        bronze_data['labels'] = self.bronze_service.get_labels()
        print(f"Output: {len(bronze_data['labels'])} rows")
        #########
        print("\nStarting alerts per library - 7 of 11 datasets")
        bronze_data['alerts_per_library'] = self.bronze_service.get_alerts_per_library()
        print(f"Output: {len(bronze_data['alerts_per_library'])} rows")
        #########
        print("\nStarting alerts per project - 8 of 11 datasets")
        bronze_data['alerts_per_project'] = self.bronze_service.get_alerts_per_project()
        print(f"Output: {len(bronze_data['alerts_per_project'])} rows")
        #########
        print("\nStarting license policy violations - 9 of 11 datasets")
        bronze_data['license_policy_violations'] = self.bronze_service.get_license_policy_violations()
        print(f"Output: {len(bronze_data['license_policy_violations'])} rows")
        #########
        print("\nStarting project due diligence - 10 of 11 datasets")
        bronze_data['project_due_diligence'] = self.bronze_service.get_project_due_diligence()
        print(f"Output: {len(bronze_data['project_due_diligence'])} rows")
        #########
        print("\nStarting libraries - 11 of 11 datasets")
        bronze_data['libraries'] = self.bronze_service.get_libraries()
        print(f"Output: {len(bronze_data['libraries'])} rows")
        #########


        print("\n" + "=" * 15)
        print("Done: Mend bronze layer")
        print("=" * 10)

        return bronze_data

    def silverprocessing(self, data=None):
        print("\n" + "=" * 15)
        print(f"Silver layer data:")
        print("=" * 10)

        print("\n" + "=" * 10)
        print("Done: Mend silver layer")
        print("=" * 15)

    def goldprocessing(self, data=None):
        print("\n" + "=" * 15)
        print(f"Gold layer data:")
        print("=" * 10)

        print("\n" + "=" * 10)
        print("Done: Mend gold layer")
        print("=" * 15)