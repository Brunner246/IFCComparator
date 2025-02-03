import math
from collections.abc import Mapping, Sequence


def is_sequence_but_not_str(obj):
    return isinstance(obj, Sequence) and not isinstance(obj, str)


def equals_values(val1, val2):
    return val1 == val2


def is_float_type(obj):
    return isinstance(obj, float)


def equals_float(lhs, rhs, tolerance=1e-5):
    return False if abs(lhs - rhs) > tolerance else True


class FuzzyHashmap:
    """
    A dictionary-like structure for approximate comparisons of numerical values and strings.
    Supports nested structures with floats, lists, and dictionaries.
    """

    def __init__(self, data: Mapping, tolerance: float = 1e-5, collector=None):
        if not isinstance(data, Mapping):
            raise TypeError("Input data must be a dictionary or a mapping-like object.")
        self.data = data
        self.tolerance = tolerance
        self.mod = - int(round(math.log10(tolerance * 100)))
        self._hash = self._calculate_hash()
        self.collector = collector
        self.parent_entity_guid: str = ""

    def __hash__(self):
        return self._hash

    def __eq__(self, other):

        def equal(lhs, rhs):
            if type(lhs) != type(rhs):
                return False
            if is_float_type(lhs):
                if abs(lhs - rhs) > self.tolerance:
                    self.collector.add_difference(
                        f"Guid {self.parent_entity_guid} > as tolerance: {type(lhs)} != {type(rhs)}", lhs, rhs)
                    return False
            elif isinstance(lhs, dict):
                fuzzy1, fuzzy2 = self.setup_fuzzy_hashmap_from_dict(lhs, rhs)
                if not (fuzzy1 == fuzzy2):
                    return False
            elif isinstance(lhs, (tuple, list)):
                if len(lhs) != len(rhs): return False
                for a, b in zip(lhs, rhs):
                    if not equal(a, b):
                        return False
            else:
                if lhs != rhs:
                    self.collector.add_difference(
                        f"Guid {self.parent_entity_guid} Value mismatch: {type(lhs)} != {type(rhs)}", lhs, rhs)
                    return False
            return True

        if set(self.data.keys()) != set(other.data.keys()): return

        data_gen = ((self.data[k], other.data[k]) for k in self.data)
        for v1, v2 in data_gen:
            if not equal(v1, v2):
                return False

        return True

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

    def set_parent_entity_guid(self, guid: str):
        self.parent_entity_guid = guid

    def setup_fuzzy_hashmap_from_dict(self, lhs, rhs):
        fuzzy1 = FuzzyHashmap(lhs, self.tolerance, self.collector)
        fuzzy1.set_parent_entity_guid(self.parent_entity_guid)
        fuzzy2 = FuzzyHashmap(rhs, self.tolerance, self.collector)
        fuzzy2.set_parent_entity_guid(self.parent_entity_guid)
        return fuzzy1, fuzzy2
