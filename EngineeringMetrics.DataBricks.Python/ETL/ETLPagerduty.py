"""
ETLPagerduty.py - ETL Module
Created automatically
"""

from Core.ELTPagerduty.DatasourcePagerdutyClass import DatasourcePagerdutyClass

def main():
    datasource = DatasourcePagerdutyClass(dbutils, spark)
    bronze = datasource.bronzeprocessing(dbutils)
    silver = datasource.silverprocessing(spark)
    gold = datasource.goldprocessing()

if __name__ == "__main__":
    main()