import unittest

from src.fuzzy_hashmap import FuzzyHashmap


class TestFuzzyHashmap(unittest.TestCase):
    def setUp(self):
        self.data1 = {'a': 1.00001, 'b': [1.00001, 2.00001], 'c': {'d': 3.00001}}
        self.data2 = {'a': 1.00002, 'b': [1.00002, 2.00002], 'c': {'d': 3.00002}}
        self.data3 = {'a': 1.1, 'b': [1.1, 2.1], 'c': {'d': 3.1}}
        self.tolerance = 1e-5

    def test_fuzzy_hashmap_equality(self):
        fmap1 = FuzzyHashmap(self.data1, self.tolerance)
        fmap2 = FuzzyHashmap(self.data2, self.tolerance)
        self.assertTrue(fmap1, fmap2)

    def test_fuzzy_hashmap_inequality(self):
        fmap1 = FuzzyHashmap(self.data1, self.tolerance)
        fmap3 = FuzzyHashmap(self.data3, self.tolerance)
        self.assertNotEqual(fmap1, fmap3)

    def test_fuzzy_hashmap_hash_consistency(self):
        fmap1 = FuzzyHashmap(self.data1, 1e-4)
        fmap2 = FuzzyHashmap(self.data2, 1e-4)
        self.assertEqual(hash(fmap1), hash(fmap2))

    def test_fuzzy_hashmap_type_error(self):
        with self.assertRaises(TypeError):
            FuzzyHashmap([1, 2, 3], self.tolerance)

    def test_fuzzy_hashmap_nested_structure(self):
        nested_data1 = {'a': {'b': {'c': 1.00001}}}
        nested_data2 = {'a': {'b': {'c': 1.00002}}}
        fmap1 = FuzzyHashmap(nested_data1, self.tolerance)
        fmap2 = FuzzyHashmap(nested_data2, self.tolerance)
        self.assertEqual(fmap1, fmap2)

if __name__ == '__main__':
    unittest.main()