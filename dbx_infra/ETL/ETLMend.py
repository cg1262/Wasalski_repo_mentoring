"""
ETLMend.py - ETL Module
Created automatically
"""

from Core.ELTMend.DatasourceMendClass import DatasourceMendClass

def main():
    datasource = DatasourceMendClass(dbutils, spark)
    bronze = datasource.bronzeprocessing(dbutils)
    silver = datasource.silverprocessing(spark)
    gold = datasource.goldprocessing()

if __name__ == "__main__":
    main()