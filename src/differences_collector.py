# def handle_nested_differences(value, dict2_value, path, key):
#     differences = {}
#     for i, j in zip(value, dict2_value):
#         differences.update(find_differences(i, j, path + key + "."))
#     return differences
#
# def find_differences(dict1, dict2, path=""):
#     differences = {}
#
#     for key, value in dict1.items():
#         if key in dict2:
#             if isinstance(value, dict) and isinstance(dict2[key], dict):
#                 differences.update(handle_nested_differences(value, dict2[key], path, key))
#             elif isinstance(value, tuple) and isinstance(dict2[key], tuple):
#                 differences.update(handle_nested_differences(value, dict2[key], path, key))
#             else:
#                 if value != dict2[key]:
#                     differences[path + key] = (value, dict2[key])
#     return differences


class DifferencesCollector:
    def __init__(self):
        self.differences = set()

    def add_difference(self, key_path: str, val1, val2):
        # if isinstance(val1, dict) and isinstance(val2, dict):
        #     diff = find_differences(val1, val2)
        self.differences.add((key_path, str(val1), str(val2)))

    def get_differences(self):
        return self.differences

    def clear(self):
        self.differences.clear()
