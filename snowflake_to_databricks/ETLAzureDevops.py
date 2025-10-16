"""
ETLAzureDevops.py - ETL Module
Created automatically
"""

from Core.ELTAzureDevops.DatasourceAzureDevopsClass import DatasourceAzureDevopsClass

def main():
    datasourceApifyClass = DatasourceAzureDevopsClass()
    datasourceApifyClass.bronzeprocessing()
    datasourceApifyClass.silverprocessing()
    datasourceApifyClass.goldprocessing()


if __name__ == "__main__":
    main()