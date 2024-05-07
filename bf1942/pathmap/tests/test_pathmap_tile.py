import unittest
from io import BytesIO
from bf1942.pathmap.pathmap import PathmapTile
from bf1942.pathmap.util import all_same

class PathmapTileTest(unittest.TestCase):

    def test_from_data_sets_correct_flag(self):
        tile = PathmapTile.from_data([0 for _ in range(8)])
        self.assertEqual(PathmapTile.FLAG_DOGO, tile.flag)

        tile = PathmapTile.from_data([1 for _ in range(8)])
        self.assertEqual(PathmapTile.FLAG_NOGO, tile.flag)

        tile = PathmapTile.from_data([1, 0, 0, 0, 0, 0, 0, 0])
        self.assertEqual(PathmapTile.FLAG_MIXED, tile.flag)

    def test_from_data_bad_data(self):
        with self.assertRaises(TypeError):
            PathmapTile.from_data(None)

        with self.assertRaises(AssertionError):
            PathmapTile.from_data("foobar")

        with self.assertRaises(AssertionError):
            PathmapTile.from_data("foobar12")

        with self.assertRaises(TypeError):
            PathmapTile.from_data(1)

        with self.assertRaises(AssertionError):
            PathmapTile.from_data([])

    def test_from_file_sets_correct_flag(self):
        file = BytesIO(bytes([0, 0, 0, 0]))
        tile = PathmapTile.from_file(file, 2)
        self.assertEqual(PathmapTile.FLAG_DOGO, tile.flag)
        self.assertEqual(16, len(tile.data))
        self.assertEqual(True, tile.data[0])
        self.assertTrue(all_same(tile.data))

        file = BytesIO(bytes([1, 0, 0, 0]))
        tile = PathmapTile.from_file(file, 2)
        self.assertEqual(PathmapTile.FLAG_NOGO, tile.flag)
        self.assertEqual(16, len(tile.data))
        self.assertEqual(False, tile.data[0])
        self.assertTrue(all_same(tile.data))

        file = BytesIO(bytes([0xff, 0xff, 0xff, 0xff, 0x81, 0x18]))
        tile = PathmapTile.from_file(file, 2)
        self.assertEqual(PathmapTile.FLAG_MIXED, tile.flag)
        self.assertEqual(16, len(tile.data))
        self.assertEqual([
            False, True, True, True,  True,  True, True, False,
            True,  True, True, False, False, True, True, True
        ], tile.data)

    def test_from_file_bad_data(self):
        with self.assertRaises(ValueError, msg='Invalid tile flag: 5'):
            file = BytesIO(bytes([0, 1, 0, 1]))
            PathmapTile.from_file(file, 1)

        with self.assertRaises(ValueError, msg='Invalid tile data length: 0'):
            file = BytesIO(bytes([0xff, 0xff, 0xff, 0xff]))
            PathmapTile.from_file(file, 1)

        with self.assertRaises(ValueError, msg='Invalid tile data length: 1'):
            file = BytesIO(bytes([0xff, 0xff, 0xff, 0xff, 0x81]))
            PathmapTile.from_file(file, 2)

    def test_new(self):
        tile = PathmapTile.new(PathmapTile.FLAG_DOGO, 8)
        self.assertEqual(64, len(tile.data))
        self.assertEqual(True, tile.data[0])
        self.assertTrue(all_same(tile.data))

        tile = PathmapTile.new(PathmapTile.FLAG_NOGO, 16)
        self.assertEqual(256, len(tile.data))
        self.assertEqual(False, tile.data[0])
        self.assertTrue(all_same(tile.data))

        tile = PathmapTile.new(PathmapTile.FLAG_MIXED, 32)
        self.assertEqual(1024, len(tile.data))
        self.assertEqual(True, tile.data[0])
        self.assertTrue(all_same(tile.data))

        with self.assertRaises(ValueError, msg='Invalid tile flag: 5'):
            PathmapTile.new(5, 16)

if __name__ == '__main__':
    unittest.main()