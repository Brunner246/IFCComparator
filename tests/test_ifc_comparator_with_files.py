import unittest
import ifcopenshell
from ifc_comparator import IFCComparator  # assuming the class is defined in a file named ifc_comparator.py

class TestIFCComparator(unittest.TestCase):
    def setUp(self):
        # Paths to the test IFC files
        self.file1_path = './new.ifc'
        self.file2_path = './old.ifc'

        # Create an instance of IFCComparator with the test files
        self.comparator = IFCComparator(self.file1_path, self.file2_path)

    def test_get_attributes(self):
        # Open the first test file and get an element
        element = self.comparator.file1.by_type('IfcProduct')[0]

        # Get attributes using the comparator method
        attributes = self.comparator.get_attributes(element)

        # Check if the attributes dictionary is not empty
        self.assertTrue(bool(attributes))

    def test_get_geometry_hash(self):
        # Open the first test file and get an element
        element = self.comparator.file1.by_type('IfcProduct')[0]

        # Get geometry hash using the comparator method
        geom_hash = self.comparator.get_geometry_hash(element)

        # Check if the geometry hash is not None
        self.assertIsNotNone(geom_hash)

    def test_compare_elements_identical(self):
        # Open the first and second test files and get elements
        element1 = self.comparator.file1.by_type('IfcProduct')[0]
        element2 = self.comparator.file2.by_type('IfcProduct')[0]

        # Compare the elements using the comparator method
        result = self.comparator.compare_elements(element1, element2)

        # Check if the result is as expected (True or False based on your test files)
        self.assertTrue(result)  # or self.assertFalse(result) based on your test files

    def test_compare_files(self):
        # Run the compare_files method
        self.comparator.compare_files()

        # Since compare_files prints the differences, we can manually check the output
        # For an automated test, we would need to capture the output and assert on it

if __name__ == '__main__':
    unittest.main()