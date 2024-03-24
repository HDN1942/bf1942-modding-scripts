import shutil
import unittest
from pathlib import Path
from bf1942.rfa_facade import pack_directory
from bf1942.testutil import *

class TestMethod(unittest.TestCase):
    def setUp(self):
        self.base = create_dummy_directory(__file__)
        self.src = self.base / 'src'
        self.src_rfa = self.base / 'src.rfa'

        create_dummy_file(self.src / 'foo.con')
        create_dummy_file(self.src / 'bar.con')

    def tearDown(self):
        shutil.rmtree(self.base)

    def test_correct_rfa_created(self):
        pack_directory(str(self.src), str(self.base), False, self.base)

        assert_rfa(self, self.base / 'src.rfa', [
            'src/foo.con',
            'src/bar.con'
        ])

    def test_skips_packing_if_file_exists(self):
        expected_hash = create_dummy_file(self.src_rfa)

        pack_directory(str(self.src), str(self.base), False, self.base)

        assert_file_hash(self, expected_hash, self.src_rfa)

    def test_overwrites_existing_file_if_overwrite_is_true(self):
        expected_hash = create_dummy_file(self.src_rfa)

        pack_directory(str(self.src), str(self.base), True, self.base)

        assert_file_hash(self, expected_hash, self.src_rfa, has_changed=True)

if __name__ == '__main__':
    unittest.main()