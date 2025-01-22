import math
from collections.abc import Mapping, Sequence
from typing import List

from src.value_comparison_strategies import ComparisonStrategy


def is_sequence_but_not_str(obj):
    return isinstance(obj, Sequence) and not isinstance(obj, str)


def equals_values(val1, val2):
    return val1 == val2


def is_float_type(obj):
    return isinstance(obj, float)


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
        self.parent_entity_guid: str = ""

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        def equals(lhs, rhs):
            if type(lhs) != type(rhs): return False
            if isinstance(lhs, float):
                if abs(lhs - rhs) > self.tolerance:
                    return False
            elif isinstance(lhs, dict):
                fuzzy1, fuzzy2 = self.setup_fuzzy_hashmap_from_dict(lhs, rhs)
                if not (fuzzy1 == fuzzy2):
                    return False
            elif isinstance(lhs, (tuple, list)):
                if len(lhs) != len(rhs):
                    return False
                for a, b in zip(lhs, rhs):
                    if isinstance(a, dict):
                        fuzzy1, fuzzy2 = self.setup_fuzzy_hashmap_from_dict(a, b)
                        if not (fuzzy1 == fuzzy2):
                            return False
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

            processed: bool = False

            if self.compare_numeric_lists and is_sequence_but_not_str(val1) and is_sequence_but_not_str(val2):
                for strategy in self.compare_numeric_lists:
                    sorted_list1, sorted_list2 = strategy.compare(k, val1, val2)
                    if sorted_list1 == [] and sorted_list2 == []: continue
                    if sorted_list1 != sorted_list2:
                        differences.append(False)
                        title = f"{k}, GlobalId: {self.data.get('GlobalId', self.parent_entity_guid)}"
                        self.compare(title, sorted_list1, sorted_list2)
                        processed = True
                        break
                    else:
                        processed = True
                        break

            if not processed and not equals(val1, val2):
                differences.append(False)
                title = f"Key: {k}, GlobalId: {self.data.get('GlobalId', self.parent_entity_guid)}"
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
        differences = []
        # title = f"Key: {key}, GlobalId: {self.data.get('GlobalId', self.parent_entity_guid)}"
        if is_sequence_but_not_str(val1) and is_sequence_but_not_str(val2):

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

        # if differences:
        #     self.collector.add_difference(title, differences, None)

    def compare(self, key: str, val1: Sequence, val2: Sequence):
        title = f"{key}, GlobalId: {self.data.get('GlobalId', self.parent_entity_guid)}"
        if is_sequence_but_not_str(val1) and is_sequence_but_not_str(val2):
            self.compare_sequences(key, val1, val2)
        elif not equals_values(val1, val2):
            if isinstance(val1, list):
                self.collector.add_difference(
                    f"{title}: Numeric lists differ",
                    val1[:10] + (['...'] if len(val1) > 10 else []),
                    val2[:10] + (['...'] if len(val2) > 10 else [])
                )
            if isinstance(val1, dict) and isinstance(val2, dict):
                truncated_val1 = {k: val1[k] for k in list(val1.keys())[:2]}
                truncated_val2 = {k: val2[k] for k in list(val2.keys())[:2]}
                for key in truncated_val1:
                    truncated_val1[key] = truncated_val1[key][:3] if isinstance(truncated_val1[key], (list, tuple)) else \
                        truncated_val1[key]
                for key in truncated_val2:
                    truncated_val2[key] = truncated_val2[key][:3] if isinstance(truncated_val2[key], (list, tuple)) else \
                        truncated_val2[key]
                self.collector.add_difference(title, truncated_val1, truncated_val2)
            else:
                self.collector.add_difference(title, val1, val2)

    def set_parent_entity_guid(self, guid: str):
        self.parent_entity_guid = guid

    def setup_fuzzy_hashmap_from_dict(self, lhs, rhs):
        fuzzy1 = FuzzyHashmap(lhs, self.tolerance, self.collector, self.compare_numeric_lists)
        fuzzy1.set_parent_entity_guid(self.parent_entity_guid)
        fuzzy2 = FuzzyHashmap(rhs, self.tolerance, self.collector, self.compare_numeric_lists)
        fuzzy2.set_parent_entity_guid(self.parent_entity_guid)
        return fuzzy1, fuzzy2
