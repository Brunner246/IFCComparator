import collections
from typing import Tuple, List, Union, Mapping
from abc import ABC, abstractmethod


# class NumericFilter:
#     @staticmethod
#     def filter(values: collections.abc.Sequence) -> List[Union[int, float]]:
#         return [v for v in values if isinstance(v, (int, float))]

class NumericFilter:
    @staticmethod
    def filter(values: collections.abc.Sequence) -> List[Union[int, float]]:
        numeric_values = []
        for v in values:
            if isinstance(v, (int, float)):
                numeric_values.append(v)
            elif isinstance(v, collections.abc.Sequence) and not isinstance(v, str):
                numeric_values.extend(NumericFilter.filter(v))
        return numeric_values


class ListSorter:
    @staticmethod
    def sort(values: List[Union[int, float]]) -> List[Union[int, float]]:
        return sorted(values)


class ComparisonStrategy(ABC):
    @abstractmethod
    def compare(self, key: str, val1: collections.abc.Sequence, val2: collections.abc.Sequence) -> Tuple[List, List]:
        pass


class CoordinatesComparisonStrategy(ComparisonStrategy):
    def compare(self, key: str, val1: collections.abc.Sequence, val2: collections.abc.Sequence) -> Tuple[List, List]:
        if key != "Coordinates":
            return [], []
        numeric_list1 = NumericFilter.filter(val1)
        numeric_list2 = NumericFilter.filter(val2)

        sorted_list1 = ListSorter.sort(numeric_list1)
        sorted_list2 = ListSorter.sort(numeric_list2)

        return sorted_list1, sorted_list2


class CoordIndexComparisonStrategy(ComparisonStrategy):
    def compare(self, key: str, val1: collections.abc.Sequence, val2: collections.abc.Sequence) -> Tuple[List, List]:
        if "CoordIndex" != key:
            return [], []
        numeric_list1 = NumericFilter.filter(val1)
        numeric_list2 = NumericFilter.filter(val2)

        sorted_list1 = ListSorter.sort(numeric_list1)
        sorted_list2 = ListSorter.sort(numeric_list2)

        return sorted_list1, sorted_list2


class CoordListComparisonStrategy(ComparisonStrategy):
    def compare(self, key: str, val1: collections.abc.Sequence, val2: collections.abc.Sequence) -> Tuple[List, List]:
        if "CoordList" != key:
            return [], []
        numeric_list1 = NumericFilter.filter(val1)
        numeric_list2 = NumericFilter.filter(val2)

        sorted_list1 = ListSorter.sort(numeric_list1)
        sorted_list2 = ListSorter.sort(numeric_list2)

        return sorted_list1, sorted_list2


def preprocess_attributes(attributes):
    for key, value in attributes.items():
        if key == "Representation" and isinstance(value, dict):
            if "Representations" in value:
                if len(value) > 0:
                    for subKey, subValue in value["Representations"][0].items():
                        if "Items" == subKey:
                            print(subValue[0])
                            for item_key, item_value in subValue[0].items():
                                if "Coordinates" in item_key and "CoordList" in subValue[0]["Coordinates"].keys():
                                    coord_list = item_value["CoordList"]
                                    sorted_coord_list = [tuple(sorted(coord)) for coord in coord_list]
                                    sorted_coord_list = sorted(sorted_coord_list)
                                    item_value["CoordList"] = sorted_coord_list
                                if "Faces" == item_key and isinstance(item_value, (list, tuple)):
                                    for face in item_value:
                                        if "CoordIndex" in face:
                                            coord_index = face["CoordIndex"]
                                            sorted_coord_index = tuple(sorted(coord_index))
                                            face["CoordIndex"] = sorted_coord_index
    return attributes


def numeric_comparison_strategy(key: str, val1: Tuple | List, val2: Tuple | List) -> Tuple[List, List]:
    if (
            (key == "Coordinates" or "CoordIndex" in key)
            and isinstance(val1, (tuple, list))
            and isinstance(val2, (tuple, list))
    ):
        numeric_list1 = [v for v in val1 if isinstance(v, (int, float))]
        numeric_list2 = [v for v in val2 if isinstance(v, (int, float))]

        sorted_list1 = sorted(numeric_list1)
        sorted_list2 = sorted(numeric_list2)

        return sorted_list1, sorted_list2
    return [], []
