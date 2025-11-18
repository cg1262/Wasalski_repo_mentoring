"""
AbstractDatasourceClass.py - ETL Module
Created automatically
"""

from abc import ABC, abstractmethod

class AbstractDatasourceClass(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def bronzeprocessing(self, data=None):
        """Process Bronze layer"""
        pass

    @abstractmethod
    def silverprocessing(self, data=None):
        """Process Silver layer"""
        pass

    @abstractmethod
    def goldprocessing(self, data=None):
        """Process Gold layer"""
        pass