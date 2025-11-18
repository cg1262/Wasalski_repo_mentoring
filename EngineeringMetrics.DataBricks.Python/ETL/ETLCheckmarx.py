"""
ETLCheckmarx.py - ETL Module
Created automatically
"""

from Core.ELTCheckmarx.DatasourceCheckmarxClass import DatasourceCheckmarxClass

def main():
    datasource = DatasourceCheckmarxClass(dbutils, spark)
    bronze = datasource.bronzeprocessing(dbutils)
    silver = datasource.silverprocessing(spark)
    gold = datasource.goldprocessing()

if __name__ == "__main__":
    main()