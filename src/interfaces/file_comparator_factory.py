import os
from abc import ABC, abstractmethod
from enum import Enum

from src.differences_collector import DifferencesCollector

class FileType(Enum):
    IFC = 1
    BTL = 2


class FileComparatorFactory(ABC):
    def __init__(self, file1_path: str, file2_path: str):
        self.file1_path = file1_path
        self.file2_path = file2_path

        if not self.file1_path:
            raise ValueError("file1_path cannot be None")
        if not self.file2_path:
            raise ValueError("file2_path cannot be None")
        if not os.path.exists(self.file1_path):
            raise FileNotFoundError(f"file1_path {self.file1_path} does not exist")
        if not os.path.exists(self.file2_path):
            raise FileNotFoundError(f"file2_path {self.file2_path} does not exist")

    @abstractmethod
    def create(self, file_type: FileType,
               collector: DifferencesCollector = None):  #TODO reafctor differences collector to interface
        pass
