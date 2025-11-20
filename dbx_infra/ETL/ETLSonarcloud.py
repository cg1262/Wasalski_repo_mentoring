"""
ETLSonarcloud.py - ETL Module
Created automatically
"""

from Core.ELTSonarcloud.DatasourceSonarcloudClass import DatasourceSonarcloudClass

def main():
    datasource = DatasourceSonarcloudClass(dbutils, spark)
    bronze = datasource.bronzeprocessing(dbutils)
    silver = datasource.silverprocessing(spark)
    gold = datasource.goldprocessing()

if __name__ == "__main__":
    main()