"""
ETLApify.py - ETL Module
Created automatically
"""

from Core.ELTApify.DatasourceApifyClass import DatasourceApifyClass

def main():
    datasourceApifyClass = DatasourceApifyClass()
    datasourceApifyClass.bronzeprocessing()
    datasourceApifyClass.silverprocessing()
    datasourceApifyClass.goldprocessing()


if __name__ == "__main__":
    main()