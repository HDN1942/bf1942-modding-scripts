import shutil
import unittest
from pathlib import Path
from bf1942.testing import *
from bf1942.rfa import pack_directory

class TestMethod(unittest.TestCase):
    def setUp(self):
        self.base = create_dummy_directory(__file__)
        self.src = self.base / 'src'
        self.dst = self.base / 'dst'

        create_dummy_file(self.src / 'foo.con')
        create_dummy_file(self.src / 'bar.con')
    
    def tearDown(self):
        shutil.rmtree(self.base)

    def test_something(self):
        pack_directory(str(self.src), str(self.dst), False, 'objects')

if __name__ == '__main__':
    unittest.main()