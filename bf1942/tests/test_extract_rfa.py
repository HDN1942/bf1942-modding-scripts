import unittest
from pathlib import Path
from bf1942.rfautil import *
from bf1942.testutil import *

class TestMethod(unittest.TestCase):
    def setUp(self):
        self.base = create_dummy_directory(__file__)

        create_dummy_file(self.base / Path('objects', 'objects.con'))
        create_dummy_file(self.base / Path('objects', 'objects2.con'))
        pack_directory(self.base / 'objects', str(self.base), False, self.base)
        shutil.rmtree(self.base / 'objects')

    def tearDown(self):
        shutil.rmtree(self.base)

    def test_correct_files_extracted(self):
        extract_rfa(self.base / 'objects.rfa', self.base, False)

        self.assertTrue(Path(self.base / 'objects' / 'objects.con').exists())
        self.assertTrue(Path(self.base / 'objects' / 'objects2.con').exists())

    def test_skips_extraction_if_directory_exists(self):
        existing_file = self.base / Path('objects', 'objects.con')
        expected_hash = create_dummy_file(existing_file, 'bar')

        extract_rfa(self.base / 'objects.rfa', self.base, False)

        assert_file_hash(self, expected_hash, existing_file)

    def test_overwrites_existing_directory_if_overwrite_is_true(self):
        existing_file = self.base / Path('objects', 'objects.con')
        expected_hash = create_dummy_file(existing_file, 'bar')

        extract_rfa(self.base / 'objects.rfa', self.base, True)

        assert_file_hash(self, expected_hash, existing_file, has_changed=True)
        self.assertTrue(Path(self.base / 'objects' / 'objects2.con').exists())