import unittest
import bf1942.tests.util as testutil
from bf1942.pathmap.conversion import convert_pathmap

class ConvertPathmap(unittest.TestCase):
    def setUp(self):
        testutil.remove_dummy_files(self)

        self.root = testutil.create_dummy_files({
            'dir1': {},
            'dir2': {},
            'file1': '',
            'file2': ''
        })

    def tearDown(self):
        testutil.remove_dummy_files(self)

    def test_assert_on_invalid_in_format(self):
        with self.assertRaises(AssertionError):
            convert_pathmap(self.root / 'dir1', self.root / 'file1', 'foo', 'bmp')

    def test_assert_on_invalid_out_format(self):
        with self.assertRaises(AssertionError):
            convert_pathmap(self.root / 'dir1', self.root / 'file1', 'dds', 'foo')

    def test_assert_on_same_in_and_out_format(self):
        with self.assertRaises(AssertionError):
            convert_pathmap(self.root / 'dir1', self.root / 'dir2', 'dds', 'dds')

    def test_assert_on_neither_in_and_out_format_is_raw(self):
        with self.assertRaises(AssertionError):
            convert_pathmap(self.root / 'dir1', self.root / 'file1', 'dds', 'bmp')

        with self.assertRaises(AssertionError):
            convert_pathmap(self.root / 'dir1', self.root / 'file1', 'dds', 'png')

        with self.assertRaises(AssertionError):
            convert_pathmap(self.root / 'file1', self.root / 'dir1', 'bmp', 'dds')

        with self.assertRaises(AssertionError):
            convert_pathmap(self.root / 'file1', self.root / 'dir1', 'png', 'dds')

    def test_assert_on_invalid_source(self):
        with self.assertRaises(AssertionError):
            convert_pathmap(None, self.root / 'file1', 'raw', 'bmp')

    def test_assert_on_source_file_with_incompatible_format(self):
        with self.assertRaises(AssertionError):
            convert_pathmap(self.root / 'file1', self.root / 'dir1', 'dds', 'raw')

    def test_assert_on_source_dir_with_incompatible_format(self):
        with self.assertRaises(AssertionError):
            convert_pathmap(self.root / 'dir1', self.root / 'file1', 'raw', 'bmp')

        with self.assertRaises(AssertionError):
            convert_pathmap(self.root / 'dir1', self.root / 'dir2', 'bmp', 'raw')

        with self.assertRaises(AssertionError):
            convert_pathmap(self.root / 'dir1', self.root / 'dir2', 'png', 'raw')

    def test_assert_on_non_existent_source(self):
        with self.assertRaises(AssertionError):
            convert_pathmap(self.root / 'invalid', self.root / 'file1', 'raw', 'bmp')

        with self.assertRaises(AssertionError):
            convert_pathmap(self.root / 'invalid', self.root / 'dir2', 'dds', 'raw')

    def test_assert_on_invalid_destination(self):
        with self.assertRaises(AssertionError):
            convert_pathmap(self.root / 'file1', None, 'raw', 'bmp')

    def test_assert_on_destination_file_with_incompatible_format(self):
        with self.assertRaises(AssertionError):
            convert_pathmap(self.root / 'file1', self.root / 'file2', 'bmp', 'raw')

        with self.assertRaises(AssertionError):
            convert_pathmap(self.root / 'file1', self.root / 'file2', 'raw', 'dds')

    def test_assert_on_non_existent_destination_dir(self):
        with self.assertRaises(AssertionError):
            convert_pathmap(self.root / 'file1', self.root / 'invalid', 'bmp', 'raw')

        with self.assertRaises(AssertionError):
            convert_pathmap(self.root / 'file1', self.root / 'invalid', 'raw', 'dds')

    def test_assert_on_same_source_and_destination_file(self):
        with self.assertRaises(AssertionError):
            convert_pathmap(self.root / 'file1', self.root / 'file1', 'raw', 'bmp')

if __name__ == '__main__':
    unittest.main()