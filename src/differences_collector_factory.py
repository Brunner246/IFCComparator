from enum import Enum

from src.interfaces.differences_collector import DifferencesCollector
from src.list_differences_collector import ListDifferencesCollector
from src.set_differences_collector import SetDifferencesCollector


class CollectionType(Enum):
    LIST = 1
    SET = 2

class DifferencesCollectorFactory:
    @staticmethod
    def create(collection_type: CollectionType) -> DifferencesCollector:
        match collection_type:
            case CollectionType.LIST:
                return ListDifferencesCollector()
            case CollectionType.SET:
                return SetDifferencesCollector()
            case _:
                raise ValueError(f"Unsupported file type: {collection_type}")
