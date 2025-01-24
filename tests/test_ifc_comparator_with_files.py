import json
import os
import pprint
import unittest
from typing import TextIO

from src.file_comparator_factory_impl import IfcFileComparatorFactoryImpl
from src.list_differences_collector import ListDifferencesCollector
from src.interfaces.file_comparator_factory import FileType
from src.value_comparison_strategy_factory import StrategyFactory, ComparisonStrategyType


class TestIFCComparator(unittest.TestCase):
    def setUp(self):
        # self.file1_path = './new.ifc'
        # self.file2_path = './old.ifc'
        # self.file1_path = './materialLayer1.ifc'
        # self.file2_path = './materialLayer2.ifc'
        self.file1_path = './test_ifc_assembly_steel.ifc'
        self.file2_path = './test_ifc_assembly_steel_expected.ifc'
        # self.file1_path = './test_multi_layer_set.ifc'
        # self.file2_path = './test_multi_layer_set_expected.ifc'

        factory = IfcFileComparatorFactoryImpl(self.file1_path, self.file2_path)
        self.differences_collector = ListDifferencesCollector()
        self.comparator = factory.create(FileType.IFC, self.differences_collector)
        strategies = [StrategyFactory.create_strategy(st) for st in
                      [ComparisonStrategyType.COORDINATES,
                       ComparisonStrategyType.COORDINDEX,
                       ComparisonStrategyType.COORDLIST]]
        if strategies:
            self.comparator.set_comparison_strategy(strategies)
        self.comparator.set_keys_to_ignore(["CoordIndex"])

    def test_compare_files(self):
        result = self.comparator.compare_files()
        if not result:
            differences = list(self.differences_collector.get_differences())
            output_data = {"errors": differences}
            current_directory = os.getcwd()
            output_path = os.path.join(current_directory, 'differences.json')
            with open(output_path, 'w') as json_file:  # type: TextIO
                json.dump(output_data, json_file, indent=4)
            print(f"Differences written to {output_path}")
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
