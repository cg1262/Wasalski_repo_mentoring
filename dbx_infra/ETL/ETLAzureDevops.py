"""
ETLAzureDevops.py - ETL Module
Created automatically
"""

from Core.ELTAzureDevops.DatasourceAzureDevopsClass import DatasourceAzureDevopsClass

def main():
    datasource = DatasourceAzureDevopsClass(dbutils, spark)
    bronze = datasource.bronzeprocessing(dbutils)
    silver = datasource.silverprocessing(spark)
    gold = datasource.goldprocessing()

if __name__ == "__main__":
    main()