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
        # self.file1_path = './test_ifc_assembly_steel.ifc'
        # self.file2_path = './test_ifc_assembly_steel_expected.ifc'
        # self.file1_path = './test_multi_layer_set.ifc'
        # self.file2_path = './test_multi_layer_set_expected.ifc'
        # self.file1_path = './test_ifc_mechanical_fastener.ifc'
        # self.file2_path = './test_ifc_mechanical_fastener_expected.ifc'
        # self.file1_path = './test_ifc_space.ifc'
        # self.file2_path = './test_ifc_space_expected.ifc'

        # self.file1_path = "C:\\Users\\MichaelBrunner\\Downloads\\IFC_Export_2025vsV30_comparison\\TEST-MBR.ifc"
        # self.file2_path = 'C:\\Users\\MichaelBrunner\\Downloads\\IFC_Export_2025vsV30_comparison\\MODIFIED_231018_Blumer_Lehmann_RFL_Demo-Element_v30.ifc'
        self.file1_path =  r"C:\source\Autotest\tests\IfcFileCompare\schema_2x3\test_ifc_stair\test_ifc_stair.ifc"
        self.file2_path =  r"C:\source\Autotest\tests\IfcFileCompare\schema_2x3\test_ifc_stair\test_ifc_stair_expected.ifc"

        factory = IfcFileComparatorFactoryImpl(self.file1_path, self.file2_path)
        self.differences_collector = ListDifferencesCollector()
        self.comparator = factory.create(FileType.IFC, self.differences_collector)

        self.comparator.set_keys_to_ignore(["CoordIndex"])

    def test_compare_files(self):
        result = self.comparator.compare_files()
        if not result:
            differences = list(self.differences_collector.get_differences())
            output_data = {"errors": differences}
            current_directory = os.getcwd()
            output_path = os.path.join(current_directory, 'differences.json')
            with open(output_path, 'w') as json_file:  # type: TextIO
                json.dump(output_data, json_file, indent=4) # type: ignore
            print(f"Differences written to {output_path}")
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
