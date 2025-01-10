from abc import ABC, abstractmethod

class FileComparator(ABC):
    @abstractmethod
    def compare_files(self) -> bool:
        pass

    @abstractmethod
    def compare_elements(self, element1, element2) -> bool:
        pass