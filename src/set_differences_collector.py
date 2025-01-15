from src.interfaces.differences_collector import DifferencesCollector


class SetDifferencesCollector(DifferencesCollector):
    def __init__(self):
        self.differences = set()

    def add_difference(self, key_path: str, val1, val2):
        self.differences.add((key_path, str(val1), str(val2)))

    def get_differences(self):
        return self.differences

    def clear(self):
        self.differences.clear()