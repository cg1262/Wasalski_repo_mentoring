"""
ETLNewrelic.py - ETL Module
Created automatically
"""

from Core.ELTNewrelic.DatasourceNewrelicClass import DatasourceNewrelicClass

def main():
    datasourceNewrelicClass = DatasourceNewrelicClass()
    datasourceNewrelicClass.bronzeprocessing()
    datasourceNewrelicClass.silverprocessing()
    datasourceNewrelicClass.goldprocessing()

if __name__ == "__main__":
    main()