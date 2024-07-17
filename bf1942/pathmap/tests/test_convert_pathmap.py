import unittest
from PIL import Image, ImageDraw
import bf1942.tests.util as testutil
from bf1942.pathmap.conversion import convert_pathmap
from bf1942.pathmap.pathmap import Pathmap
from bf1942.pathmap.smallones import Smallones

class ConvertPathmapTest(unittest.TestCase):
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

    def test_convert_image_to_pathmap(self):
        with Image.new('1', (2048, 2048)) as im:
            draw = ImageDraw.Draw(im)
            draw.polygon([(0, 0), (2047, 2047), (0, 2047)], fill=255)
            im.save(self.root / 'Tank0Level0Map.bmp')

        convert_pathmap(self.root / 'Tank0Level0Map.bmp', self.root / 'dir1', 'bmp', 'raw')

        self.assertTrue((self.root / 'dir1' / 'Tank0Level0Map.raw').exists())
        self.assertTrue((self.root / 'dir1' / 'Tank0Level1Map.raw').exists())
        self.assertTrue((self.root / 'dir1' / 'Tank0Level2Map.raw').exists())
        self.assertTrue((self.root / 'dir1' / 'TankInfo.raw').exists())
        self.assertTrue((self.root / 'dir1' / 'Tank.raw').exists())

        pm = Pathmap.load(self.root / 'dir1' / 'Tank0Level0Map.raw')
        self.assertEqual(2048, pm.header.map_width)
        self.assertEqual(32, pm.header.tile_length)
        self.assertEqual(0, pm.header.compression_level)

        pm = Pathmap.load(self.root / 'dir1' / 'Tank0Level1Map.raw')
        self.assertEqual(2048, pm.header.map_width)
        self.assertEqual(16, pm.header.tile_length)
        self.assertEqual(1, pm.header.compression_level)

        pm = Pathmap.load(self.root / 'dir1' / 'Tank0Level2Map.raw')
        self.assertEqual(2048, pm.header.map_width)
        self.assertEqual(8, pm.header.tile_length)
        self.assertEqual(2, pm.header.compression_level)

        pm = Pathmap.load(self.root / 'dir1' / 'TankInfo.raw')
        self.assertEqual(2048, pm.header.map_width)
        self.assertEqual(32, pm.header.tile_length)
        self.assertEqual(1, pm.header.compression_level)
        self.assertEqual(1, pm.header.is_info)

        so = Smallones.load(self.root / 'dir1' / 'Tank.raw')
        self.assertEqual(32, so.header.tile_length)

    def test_convert_image_to_pathmap_boat(self):
        with Image.new('1', (512, 512)) as im:
            draw = ImageDraw.Draw(im)
            draw.polygon([(0, 0), (511, 511), (0, 511)], fill=255)
            im.save(self.root / 'Boat2Level2Map.bmp')

        convert_pathmap(self.root / 'Boat2Level2Map.bmp', self.root / 'dir1', 'bmp', 'raw')

        self.assertTrue((self.root / 'dir1' / 'Boat2Level2Map.raw').exists())
        self.assertTrue((self.root / 'dir1' / 'Boat2Level3Map.raw').exists())
        self.assertTrue((self.root / 'dir1' / 'Boat2Level4Map.raw').exists())
        self.assertTrue((self.root / 'dir1' / 'Boat2Level5Map.raw').exists())
        self.assertTrue((self.root / 'dir1' / 'BoatInfo.raw').exists())
        self.assertTrue((self.root / 'dir1' / 'Boat.raw').exists())

        pm = Pathmap.load(self.root / 'dir1' / 'Boat2Level2Map.raw')
        self.assertEqual(2048, pm.header.map_width)
        self.assertEqual(8, pm.header.tile_length)
        self.assertEqual(2, pm.header.compression_level)

        pm = Pathmap.load(self.root / 'dir1' / 'Boat2Level3Map.raw')
        self.assertEqual(2048, pm.header.map_width)
        self.assertEqual(4, pm.header.tile_length)
        self.assertEqual(3, pm.header.compression_level)

        pm = Pathmap.load(self.root / 'dir1' / 'Boat2Level4Map.raw')
        self.assertEqual(2048, pm.header.map_width)
        self.assertEqual(2, pm.header.tile_length)
        self.assertEqual(4, pm.header.compression_level)

        pm = Pathmap.load(self.root / 'dir1' / 'Boat2Level5Map.raw')
        self.assertEqual(2048, pm.header.map_width)
        self.assertEqual(1, pm.header.tile_length)
        self.assertEqual(5, pm.header.compression_level)

        pm = Pathmap.load(self.root / 'dir1' / 'BoatInfo.raw')
        self.assertEqual(2048, pm.header.map_width)
        self.assertEqual(8, pm.header.tile_length)
        self.assertEqual(3, pm.header.compression_level)
        self.assertEqual(1, pm.header.is_info)

        so = Smallones.load(self.root / 'dir1' / 'Boat.raw')
        self.assertEqual(8, so.header.tile_length)

if __name__ == '__main__':
    unittest.main()