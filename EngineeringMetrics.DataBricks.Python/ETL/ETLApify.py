"""
ETLApify.py - ETL Module
Created automatically
"""

from Core.ELTApify.DatasourceApifyClass import DatasourceApifyClass

def main():
    datasource = DatasourceApifyClass(dbutils, spark)
    bronze = datasource.bronzeprocessing(dbutils)
    silver = datasource.silverprocessing(spark)
    gold = datasource.goldprocessing()

if __name__ == "__main__":
    main()