import math
import pprint
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
        self.mod = - int(round(math.log10(tolerance * 100)))
        self._hash = self._calculate_hash()
        self.collector = collector  # or DifferencesCollector()

    # def _round_value(self, value):
    #     """
    #     Rounds a float or recursively processes nested data structures.
    #     """
    #     mod = - int(round(math.log10(self.tolerance * 100)))  # log10(1e-5) = -5
    #     if isinstance(value, float):
    #         # print "round(%r, %r) = %r" % (v, mod, round(v, mod))
    #         return round(value, mod)
    #     elif isinstance(value, Mapping):
    #         return tuple(sorted((key, self._round_value(val)) for key, val in value.items()))
    #     elif isinstance(value, Sequence) and not isinstance(value, str):
    #         return tuple(self._round_value(v) for v in value)
    #     else:
    #         return value
    #
    # def _calculate_hash(self):
    #     """
    #     Computes a hash for the dictionary based on rounded values.
    #     """
    #     return hash(self._round_value(self.data))

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        def equals(lhs, rhs):
            if type(lhs) != type(rhs): return False
            if isinstance(lhs, float):
                if abs(lhs - rhs) > self.tolerance:
                    return False
            elif isinstance(lhs, dict):
                if not (FuzzyHashmap(lhs, self.tolerance, self.collector)
                        == FuzzyHashmap(rhs, self.tolerance, self.collector)):
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

            if not equals(val1, val2):
                differences.append(False)
                title = f"Key: {k}, GlobalId: {self.data.get('GlobalId')}"
                self.collector.add_difference(title, val1, val2)
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
            elif isinstance(value, (tuple, list)):
                return type(value)(map(_round_value, value))
            else:
                return value

        return hash(_round_value(self.data))
