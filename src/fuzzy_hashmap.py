import collections
import math
from collections.abc import Mapping, Sequence
from typing import List, Tuple

from src.value_comparison_strategies import ComparisonStrategy


def is_sequence_but_not_str(obj):
    return isinstance(obj, Sequence) and not isinstance(obj, str)


def equals_values(val1, val2):
    return val1 == val2


def is_float_type(obj):
    return isinstance(obj, float)


def compare_numeric_elements(val1, val2, title, collector, equals):
    """
    Compare elements of two lists or tuples by collecting numeric items (int or float),
    sorting them, and then comparing.
    """
    if isinstance(val1, (tuple, list)) and isinstance(val2, (tuple, list)):
        numeric_list1 = [v for v in val1 if isinstance(v, (int, float))]
        numeric_list2 = [v for v in val2 if isinstance(v, (int, float))]

        sorted_list1 = sorted(numeric_list1)
        sorted_list2 = sorted(numeric_list2)

        if sorted_list1 != sorted_list2:
            collector.add_difference(f"{title}: Numeric lists differ", sorted_list1, sorted_list2)

        for i, (v1, v2) in enumerate(zip(val1, val2)):
            if not equals(v1, v2):
                collector.add_difference(f"{title}, index: {i}", v1, v2)


class FuzzyHashmap:
    """
    A dictionary-like structure for approximate comparisons of numerical values and strings.
    Supports nested structures with floats, lists, and dictionaries.
    """

    def __init__(self, data: Mapping, tolerance: float = 1e-5, collector=None,
                 comparison_strategies: List[ComparisonStrategy] = None):
        if not isinstance(data, Mapping):
            raise TypeError("Input data must be a dictionary or a mapping-like object.")
        self.data = data
        self.tolerance = tolerance
        self.mod = - int(round(math.log10(tolerance * 100)))
        self._hash = self._calculate_hash()
        self.collector = collector
        self.compare_numeric_lists: List[ComparisonStrategy] | None = comparison_strategies
        self.keys_to_ignore: List[str] = []

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        def equals(lhs, rhs):
            if type(lhs) != type(rhs): return False
            if isinstance(lhs, float):
                if abs(lhs - rhs) > self.tolerance:
                    return False
            elif isinstance(lhs, dict):
                fuzzy1 = FuzzyHashmap(lhs, self.tolerance, self.collector, self.compare_numeric_lists)
                fuzzy1.set_keys_to_ignore(self.keys_to_ignore)
                fuzzy2 = FuzzyHashmap(rhs, self.tolerance, self.collector, self.compare_numeric_lists)
                fuzzy2.set_keys_to_ignore(self.keys_to_ignore)
                if not (fuzzy1 == fuzzy2):
                    return False
            elif isinstance(lhs, (tuple, list)):
                if len(lhs) != len(rhs):
                    return False
                for a, b in zip(lhs, rhs):
                    if not equals(a, b):
                        return False
            else:
                if lhs != rhs:
                    return False
            return True

        if set(self.data.keys()) != set(other.data.keys()): return False

        differences = []
        for k in self.data:
            val1 = self.data[k]
            val2 = other.data[k]

            if k in self.keys_to_ignore:
                print(f"Ignoring key: {k}")
                continue

            processed: bool = False

            if self.compare_numeric_lists and is_sequence_but_not_str(val1) and is_sequence_but_not_str(val2):
                for strategy in self.compare_numeric_lists:
                    sorted_list1, sorted_list2 = strategy.compare(k, val1, val2)
                    if sorted_list1 == [] and sorted_list2 == []: continue
                    if sorted_list1 != sorted_list2:
                        differences.append(False)
                        title = f"Key: {k}, GlobalId: {self.data.get('GlobalId', 'None')}"
                        self.compare(title, sorted_list1, sorted_list2)
                        processed = True
                        break
                    else:
                        processed = True
                        break

            if not processed and not equals(val1, val2):
                differences.append(False)
                title = f"Key: {k}, GlobalId: {self.data.get('GlobalId')}"
                self.compare(title, val1, val2)
        return differences == []

    def get_differences(self):
        return self.collector.get_differences()

    def __repr__(self):
        return f"FuzzyHashmap(data={self.data}, tolerance={self.tolerance})"

    def _calculate_hash(self):
        def _round_value(value):
            if isinstance(value, float):
                return round(value, self.mod)
            elif isinstance(value, dict):
                return tuple(sorted((k, _round_value(v)) for k, v in value.items()))
            elif isinstance(value, (tuple, list, set)):
                return tuple(map(_round_value, value))
            else:
                return value

        return hash(_round_value(self.data))

    def compare_sequences(self, key: str, val1: Sequence, val2: Sequence):
        if is_sequence_but_not_str(val1) and is_sequence_but_not_str(val2):
            title = f"Key: {key}, GlobalId: {self.data.get('GlobalId')}"
            differences = []

            for i in range(min(len(val1), len(val2))):
                item1, item2 = val1[i], val2[i]

                if is_sequence_but_not_str(item1) and is_sequence_but_not_str(item2):
                    self.compare_sequences(f"{key}[{i}]", item1, item2)
                elif is_float_type(item1) and is_float_type(item2):
                    if not math.isclose(item1, item2, rel_tol=self.tolerance, abs_tol=self.tolerance):
                        differences.append([item1, item2])
                elif item1 != item2:
                    differences.append([item1, item2])

            if len(val1) > len(val2):
                for i in range(len(val2), len(val1)):
                    differences.append([val1[i], None])

            if len(val2) > len(val1):
                for i in range(len(val1), len(val2)):
                    differences.append([None, val2[i]])

            if differences:
                self.collector.add_difference(title, differences, None)

    def compare(self, k, val1, val2):
        if is_sequence_but_not_str(val1) and is_sequence_but_not_str(val2):
            self.compare_sequences(k, val1, val2)
        elif not equals_values(val1, val2):
            title = f"Key: {k}, GlobalId: {self.data.get('GlobalId')}"
            self.collector.add_difference(title, val1, val2)

    def set_keys_to_ignore(self, keys: List[str]):
        self.keys_to_ignore = keys
