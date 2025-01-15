from src.interfaces.differences_collector import DifferencesCollector


class ListDifferencesCollector(DifferencesCollector):

    def __init__(self):
        self.differences = []

    def add_difference(self, title, val1, val2):
        self.differences.append([title, val1, val2])

    def get_differences(self):
        return self.differences

    def clear(self):
        self.differences.clear()
