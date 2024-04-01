import shutil
import unittest
from pathlib import Path
from bf1942.rfautil import *
from bf1942.testutil import *

class TestMethod(unittest.TestCase):
    def setUp(self):
        self.base = create_dummy_directory(__file__)
        self.src = self.base / 'src'
        self.dst = self.base / 'dst'

        self.src.mkdir()
        self.dst.mkdir()

        create_dummy_rfa(self.src, 'Level1')
        create_dummy_rfa(self.src, 'Level2')
        create_dummy_file(self.src / 'foo.con')
        (self.src / 'bar').mkdir()

    def tearDown(self):
        shutil.rmtree(self.base)

    def test_extracts_rfas_in_directory(self):
        extract_directory(self.src, self.dst, False)

        self.assertTrue(Path(self.dst / 'Level1' / 'Level1.con').exists())
        self.assertTrue(Path(self.dst / 'Level2' / 'Level2.con').exists())

if __name__ == '__main__':
    unittest.main()