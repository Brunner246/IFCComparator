import unittest

from src.file_comparator_factory_impl import IfcFileComparatorFactoryImpl
from src.list_differences_collector import ListDifferencesCollector
from src.interfaces.file_comparator_factory import FileType


class TestIFCComparator(unittest.TestCase):
    def setUp(self):
        self.file1_path = './new.ifc'
        self.file2_path = './old.ifc'
        # self.file1_path = './materialLayer1.ifc'
        # self.file2_path = './materialLayer2.ifc'

        factory = IfcFileComparatorFactoryImpl(self.file1_path, self.file2_path)
        self.comparator = factory.create(FileType.IFC, ListDifferencesCollector())

    def test_compare_files(self):
        self.assertTrue(self.comparator.compare_files())


if __name__ == '__main__':
    unittest.main()
