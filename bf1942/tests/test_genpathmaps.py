import unittest
from bf1942.genpathmaps import genpathmaps
from bf1942.testutil import *

class TestMethod(unittest.TestCase):
    def setUp(self):
        self.base = create_dummy_directory(__file__)
        self.src = self.base / 'src'
        self.dst = self.base / 'dst'

        self.src.mkdir()
        self.dst.mkdir()

    def test_something(self):
        genpathmaps()

if __name__ == '__main__':
    unittest.main()