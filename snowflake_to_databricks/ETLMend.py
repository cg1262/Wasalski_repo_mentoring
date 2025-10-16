"""
ETLMend.py - ETL Module
Created automatically
"""

from Core.ELTMend.DatasourceMendClass import DatasourceMendClass

def main():
    datasourceApifyClass = DatasourceMendClass()
    datasourceApifyClass.bronzeprocessing()
    datasourceApifyClass.silverprocessing()
    datasourceApifyClass.goldprocessing()


if __name__ == "__main__":
    main()