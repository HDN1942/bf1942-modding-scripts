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
        self.bf1942_path = self.src / BF1942_DIRECTORY
        self.levels_path = self.bf1942_path / LEVELS_DIRECTORY
        self.levels = ['Level1', 'Level2']

        self.src.mkdir()
        self.dst.mkdir()
        self.bf1942_path.mkdir()
        self.levels_path.mkdir()

        for directory in TOP_LEVEL_RFAS:
            create_dummy_rfa(self.src, directory)

        for directory in BF1942_LEVEL_RFAS:
            create_dummy_rfa(self.bf1942_path, directory, f'{BF1942_DIRECTORY}/{directory}')

        for directory in self.levels:
            create_dummy_rfa(self.levels_path, directory, f'{BF1942_DIRECTORY}/{LEVELS_DIRECTORY}/{directory}')

        (self.src / 'bar').mkdir()
        create_dummy_rfa(self.src, 'foo')
        create_dummy_rfa(self.src / 'bar', 'baz')

    def tearDown(self):
        shutil.rmtree(self.base)

    def test_extracts_all_known_rfas(self):
        extract_mod(self.src, self.dst, False)

        for directory in TOP_LEVEL_RFAS:
            self.assertTrue((self.dst / directory / f'{directory}.con').exists())

        for directory in BF1942_LEVEL_RFAS:
            self.assertTrue((self.dst / BF1942_DIRECTORY / directory / f'{directory}.con').exists())

        for directory in self.levels:
            self.assertTrue((self.dst / BF1942_DIRECTORY / LEVELS_DIRECTORY / directory / f'{directory}.con').exists())

        self.assertFalse((self.dst / 'foo' / 'foo.con').exists())
        self.assertFalse((self.dst / 'bar' / 'baz' / 'baz.con').exists())

if __name__ == '__main__':
    unittest.main()