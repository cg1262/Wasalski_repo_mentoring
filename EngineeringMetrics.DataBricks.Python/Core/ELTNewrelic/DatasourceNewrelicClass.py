"""
DatasourceNewrelicClass.py - ETL Module
Created automatically
"""

from Core.AbstractDatasourceClass import AbstractDatasourceClass
from Core.ELTNewrelic.ServicesNewrelic.ServiceNewrelicBronze import ServiceBronze
from Core.Services.ServiceSaveToDelta import ServiceTables
from pyspark.sql import SparkSession

class DatasourceNewrelicClass(AbstractDatasourceClass):
    def __init__(self):
        super().__init__()
        self.spark = SparkSession.builder.getOrCreate()
        self.bronze_service = ServiceBronze()
        self.bronze_tables = ServiceTables()
        self.catalog = 'engineering_metrics'
        self.db = 'bronze'
        self.prefix = 'newrelic_'
        

    def bronzeprocessing(self, data=None):
        """
        Extracting raw data from New Relic.
        As return we will have a dict of DataFrames:
        1. test_billing
        2. nrql_percentage
        3. success_of_neuron_us
        4. success_of_neuron_eun
        5. documents_stuck_in_ai
        6. no_of_entered_documents
        7. avg_neuron_e2e_duration_us
        8. avg_neuron_e2e_duration_eun
        9. overall_succ_rate_of_vis_us
        10. overall_succ_rate_of_vis_eun
        11. documents_us_data
        12. documents_eun_data
        13. avg_duraiton_us
        14. avg_duraiton_eun
        15. documents_entered_us
        16. documents_entered_eun
        """

        dict_newrelic = {
            'test_billing': self.bronze_service.test_billing,
            'nrql_percentage': self.bronze_service.nrql_percentage,
            'success_of_neuron_us': self.bronze_service.success_of_neuron_us,
            'success_of_neuron_eun': self.bronze_service.success_of_neuron_eun,
            'documents_stuck_in_ai': self.bronze_service.documents_stuck_in_ai,
            'no_of_entered_documents': self.bronze_service.no_of_entered_documents,
            'avg_neuron_e2e_duration_us': self.bronze_service.avg_neuron_e2e_duration_us,
            'avg_neuron_e2e_duration_eun': self.bronze_service.avg_neuron_e2e_duration_eun,
            'overall_succ_rate_of_vis_us': self.bronze_service.overall_succ_rate_of_vis_us,
            'overall_succ_rate_of_vis_eun': self.bronze_service.overall_succ_rate_of_vis_eun,
            'documents_us_data': self.bronze_service.documents_us_data,
            'documents_eun_data': self.bronze_service.documents_eun_data,
            'avg_duraiton_us': self.bronze_service.avg_duraiton_us,
            'avg_duraiton_eun': self.bronze_service.avg_duraiton_eun,
            'documents_entered_us': self.bronze_service.documents_entered_us,
            'documents_entered_eun': self.bronze_service.documents_entered_eun
        }
        length_dict = len(dict_newrelic)
        count = 1
        
        
        print("=" * 10)
        print("newrelic bronze layer")
        print("=" * 15)


        for key, func in dict_newrelic.items():
            # iterate over the dictionary, where key = endpoint name (e.g. 'services'),
            # func = reference to the function (e.g. get_services without parentheses)

            print(f"\nStarting  - {count} of {length_dict} datasets")
            print(f"Amount of function to call: {length_dict}")
            print(f"Calling function for key: {key}")

            # call the function (HERE we add parentheses) to get DataFrame from API
            # e.g. func() is like self.bronze_service.get_services and at the end we add () to call this function

            df = func()

            # save DataFrame to parquet file with prefix from self.prefix and key name
            # e.g. newrelic_services.parquet
            # this will also be used later for upsert to the database

            count += 1

            # spark dataframe is being created in the service class

            table_name = f"{self.catalog}.{self.db}.{self.prefix}{key}_test"
            df.write.format("delta").mode("overwrite").saveAsTable(table_name)

            print(f"created {self.catalog}.{self.db}.{self.prefix}{key}_test table")
        return df
    



    def silverprocessing(self, data=None):
        print("\n" + "=" * 15)
        print(f"Silver layer data:")
        print("=" * 10)

        print("\n" + "=" * 10)
        print("Done: newrelic silver layer")
        print("=" * 15)

    def goldprocessing(self, data=None):
        print("\n" + "=" * 15)
        print(f"Gold layer data:")
        print("=" * 10)

        print("\n" + "=" * 10)
        print("Done: newrelic gold layer")
        print("=" * 15)