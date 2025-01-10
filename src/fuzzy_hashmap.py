import math
from collections.abc import Mapping, Sequence


class FuzzyHashmap:
    """
    A dictionary-like structure for approximate comparisons of numerical values.
    Supports nested structures with floats, lists, and dictionaries.
    """

    def __init__(self, data, tolerance: float = 1e-5, collector=None):
        if not isinstance(data, Mapping):
            raise TypeError("Input data must be a dictionary or a mapping-like object.")
        self.data = data
        self.tolerance = tolerance
        self._hash = self._calculate_hash()
        self.collector = collector  # or DifferencesCollector()

    def _round_value(self, value):
        """
        Rounds a float or recursively processes nested data structures.
        """
        if isinstance(value, float):
            precision = -int(round(math.log10(self.tolerance)))  # log10(1e-5) = -5
            return round(value, precision)
        elif isinstance(value, Mapping):
            return tuple(sorted((key, self._round_value(val)) for key, val in value.items()))
        elif isinstance(value, Sequence) and not isinstance(value, str):
            return tuple(self._round_value(v) for v in value)
        else:
            return value

    def _calculate_hash(self):
        """
        Computes a hash for the dictionary based on rounded values.
        """
        rounded_data = self._round_value(self.data)
        return hash(rounded_data)

    def __hash__(self):
        return self._hash

    def compare_values(self, val1, val2, entity_name):
        if type(val1) != type(val2):
            self.collector.add_difference(entity_name, val1, val2)
            return False
        if isinstance(val1, float):
            print(val1, val2)
            if abs(val1 - val2) > self.tolerance:
                self.collector.add_difference(entity_name, val1, val2)
                return False
            return True
        elif isinstance(val1, Mapping):
            return FuzzyHashmap(val1, self.tolerance, self.collector)._compare(val2, entity_name)
        elif isinstance(val1, Sequence) and not isinstance(val1, str):
            if len(val1) != len(val2):
                self.collector.add_difference(entity_name, val1, val2)
                return False
            return all(self.compare_values(v1, v2, entity_name + [i]) for i, (v1, v2) in enumerate(zip(val1, val2)))
        else:
            if val1 != val2:
                self.collector.add_difference(entity_name, val1, val2)
                return False
            return True

    def __eq__(self, other):
        if not isinstance(other, FuzzyHashmap):
            return False

        if set(self.data.keys()) != set(other.data.keys()):
            self.collector.add_difference("keys", set(self.data.keys()), set(other.data.keys()))
            return False

        # all aborts on first False
        # return all(
        #     self.compare_values(self.data[pair], other.data[pair], pair)
        #     for pair in self.data
        # )
        marker = list()
        for pair in self.data:
            equals = self.compare_values(self.data[pair], other.data[pair], pair)
            marker.append(equals)
        return all(marker)

    def _compare(self, other, entity_name):
        """
        Compares dictionaries and tracks differences.
        """
        if not isinstance(other, Mapping):
            self.collector.add_difference(entity_name, self.data, other)
            return False
        keys1 = set(self.data.keys())
        keys2 = set(other.keys())

        for key in keys1 - keys2:
            self.collector.add_difference(entity_name + [key], self.data[key], None)

        for key in keys2 - keys1:
            self.collector.add_difference(entity_name + [key], None, other[key])

        for key in keys1 & keys2:
            val1 = self.data[key]
            val2 = other[key]
            new_path = entity_name + [key]
            if not self.compare_values(val1, val2, new_path):
                self.collector.add_difference(new_path, val1, val2)

        return len(self.collector.get_differences()) == 0

    def get_differences(self):
        return self.collector.get_differences()

    def __repr__(self):
        return f"FuzzyHashmap(data={self.data}, tolerance={self.tolerance})"
