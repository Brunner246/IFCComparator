from abc import ABC, abstractmethod
from typing import List

from src.value_comparison_strategies import ComparisonStrategy


class FileComparator(ABC):
    @abstractmethod
    def compare_files(self) -> bool:
        pass

    @abstractmethod
    def compare_elements(self, entity_lhs, entity_rhs) -> bool:
        pass

    @abstractmethod
    def set_comparison_strategy(self, comparison_strategy: List[ComparisonStrategy]):
        pass

    @abstractmethod
    def set_keys_to_ignore(self, keys: List[str]):
        pass
