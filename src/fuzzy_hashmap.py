import math
from collections.abc import Mapping, Sequence


class FuzzyHashmap:
    """
    A dictionary-like structure for approximate comparisons of numerical values.
    Supports nested structures with floats, lists, and dictionaries.
    """

    def __init__(self, data, tolerance: float = 1e-5):
        """
        Initializes the FuzzyHashmap.

        :param data: The dictionary to wrap and compare.
        :param tolerance: The allowable numerical difference for floating-point comparisons.
        """
        if not isinstance(data, Mapping):
            raise TypeError("Input data must be a dictionary or a mapping-like object.")
        self.data = data
        self.tolerance = tolerance
        self._hash = self._calculate_hash()

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

    def __eq__(self, other):
        if not isinstance(other, FuzzyHashmap):
            return False

        def compare_values(val1, val2):
            if type(val1) != type(val2):
                return False
            if isinstance(val1, float):
                return abs(val1 - val2) <= self.tolerance
            elif isinstance(val1, Mapping):
                return FuzzyHashmap(val1, self.tolerance) == FuzzyHashmap(val2,
                                                                          self.tolerance)  # compare newly created FuzzyHashmaps for nested dictionaries
            elif isinstance(val1, Sequence) and not isinstance(val1, str):
                return len(val1) == len(val2) and all(
                    compare_values(v1, v2) for v1, v2 in zip(val1, val2)
                )
            else:
                return val1 == val2

        if set(self.data.keys()) != set(other.data.keys()):
            return False

        return all(
            compare_values(self.data[key], other.data[key]) for key in self.data
        )

    def __repr__(self):
        return f"FuzzyHashmap(data={self.data}, tolerance={self.tolerance})"
