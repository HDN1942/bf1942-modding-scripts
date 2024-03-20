import shutil
import unittest
from pathlib import Path
from bf1942.path import path_join_insensitive
from bf1942.testing import *

class TestMethod(unittest.TestCase):
    def setUp(self):
        self.base = create_dummy_directory(__file__)
    
    def tearDown(self):
        shutil.rmtree(self.base)

    def test_non_exitant_path(self):
        non_existant = self.base / 'foo'

        expected = non_existant / 'bar'
        actual = path_join_insensitive(non_existant, 'bar')

        self.assertEqual(expected, actual)

    def test_partial_existant_path(self):
        parts = ['foo', 'bar', 'baz', 'qux']
        existant = self.base / Path(*parts[0:2])
        existant.mkdir(parents=True)

        expected = existant / Path(*parts[2:])
        actual = path_join_insensitive(self.base, Path(*parts))

        self.assertEqual(expected, actual)

    def test_case_insensitive_match(self):
        parts = ['fOo', 'bar', 'BAZ']
        existant = self.base / Path(*parts)
        existant.mkdir(parents=True)

        parts_lower = [p.lower() for p in parts]

        expected = existant
        actual = path_join_insensitive(self.base, Path(*parts_lower))

        self.assertEqual(expected, actual)

if __name__ == '__main__':
    unittest.main()