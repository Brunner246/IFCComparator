from abc import ABC, abstractmethod

class DifferencesCollector(ABC):
    @abstractmethod
    def add_difference(self, title, val1, val2):
        pass

    @abstractmethod
    def get_differences(self):
        pass

    @abstractmethod
    def clear(self):
        pass