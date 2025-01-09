import unittest
from unittest.mock import MagicMock
from ifc_comparator import IFCComparator  # assuming the class is defined in a file named ifc_comparator.py

class TestIFCComparatorMocked(unittest.TestCase):
    def setUp(self):
        # Create mock IFC files
        self.file1 = MagicMock()
        self.file2 = MagicMock()

        # Create an instance of IFCComparator with the mock files
        self.comparator = IFCComparator('new.ifc', 'old.ifc')
        self.comparator.file1 = self.file1
        self.comparator.file2 = self.file2

    def test_get_attributes(self):
        # Create a mock element
        element = MagicMock()
        element.get_info.return_value = {
            'GlobalId': '1',
            'Name': 'Element1',
            'Description': 'Test Element'
        }

        attributes = self.comparator.get_attributes(element)
        expected_attributes = {
            'GlobalId': '1',
            'Name': 'Element1',
            'Description': 'Test Element'
        }

        self.assertEqual(attributes, expected_attributes)

    def test_get_geometry_hash(self):
        # Create a mock element with a representation
        element = MagicMock()
        element.Representation = "RepresentationData"

        geom_hash = self.comparator.get_geometry_hash(element)
        expected_hash = hash(str("RepresentationData"))

        self.assertEqual(geom_hash, expected_hash)

    def test_compare_elements_identical(self):
        # Create two identical mock elements
        element1 = MagicMock()
        element1.get_info.return_value = {
            'GlobalId': '1',
            'Name': 'Element1',
            'Description': 'Test Element'
        }
        element1.Representation = "RepresentationData"

        element2 = MagicMock()
        element2.get_info.return_value = {
            'GlobalId': '1',
            'Name': 'Element1',
            'Description': 'Test Element'
        }
        element2.Representation = "RepresentationData"

        result = self.comparator.compare_elements(element1, element2)
        self.assertTrue(result)

    def test_compare_elements_different_attributes(self):
        # Create two mock elements with different attributes
        element1 = MagicMock()
        element1.get_info.return_value = {
            'GlobalId': '1',
            'Name': 'Element1',
            'Description': 'Test Element'
        }
        element1.Representation = "RepresentationData"

        element2 = MagicMock()
        element2.get_info.return_value = {
            'GlobalId': '1',
            'Name': 'Element2',
            'Description': 'Test Element'
        }
        element2.Representation = "RepresentationData"

        result = self.comparator.compare_elements(element1, element2)
        self.assertFalse(result)

    def test_compare_elements_different_geometry(self):
        # Create two mock elements with different geometries
        element1 = MagicMock()
        element1.get_info.return_value = {
            'GlobalId': '1',
            'Name': 'Element1',
            'Description': 'Test Element'
        }
        element1.Representation = "RepresentationData1"

        element2 = MagicMock()
        element2.get_info.return_value = {
            'GlobalId': '1',
            'Name': 'Element1',
            'Description': 'Test Element'
        }
        element2.Representation = "RepresentationData2"

        result = self.comparator.compare_elements(element1, element2)
        self.assertFalse(result)

    def test_compare_files(self):
        # Mock elements for file1 and file2
        element1 = MagicMock()
        element1.GlobalId = '1'
        element1.get_info.return_value = {
            'GlobalId': '1',
            'Name': 'Element1',
            'Description': 'Test Element'
        }
        element1.Representation = "RepresentationData"

        element2 = MagicMock()
        element2.GlobalId = '1'
        element2.get_info.return_value = {
            'GlobalId': '1',
            'Name': 'Element1',
            'Description': 'Test Element'
        }
        element2.Representation = "RepresentationData"

        self.file1.by_type.return_value = [element1]
        self.file2.by_type.return_value = [element2]

        self.comparator.compare_elements = MagicMock(return_value=True)
        self.comparator.compare_files()

        self.comparator.compare_elements.assert_called_with(element1, element2)

if __name__ == '__main__':
    unittest.main()