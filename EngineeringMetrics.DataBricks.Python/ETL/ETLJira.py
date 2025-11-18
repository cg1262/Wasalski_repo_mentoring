"""
ETLJira.py - ETL Module
Created automatically
"""

from Core.ELTJira.DatasourceJiraClass import DatasourceJiraClass

def main():
    datasource = DatasourceJiraClass(dbutils, spark)
    # bronze = datasource.bronzeprocessing(dbutils)
    silver = datasource.silverprocessing(spark)
    gold = datasource.goldprocessing()

if __name__ == "__main__":
    main()