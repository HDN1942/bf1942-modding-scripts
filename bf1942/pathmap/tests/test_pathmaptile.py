import unittest
from io import BytesIO
from bf1942.pathmap.pathmap import PathmapTile

class PathmapTileTest(unittest.TestCase):

    def test_from_data_sets_correct_flag(self):
        pt = PathmapTile.from_data([0 for _ in range(8)])
        self.assertEqual(PathmapTile.FLAG_DOGO, pt.flag)

        pt = PathmapTile.from_data([1 for _ in range(8)])
        self.assertEqual(PathmapTile.FLAG_NOGO, pt.flag)

        pt = PathmapTile.from_data([1, 0, 0, 0, 0, 0, 0, 0])
        self.assertEqual(PathmapTile.FLAG_MIXED, pt.flag)

    def test_from_data_packs_data(self):
        pt = PathmapTile.from_data([1, 0, 0, 0, 0, 0, 0, 1])
        self.assertEqual(1, len(pt.data))
        self.assertEqual(0x81, pt.data[0])

    def test_from_data_bad_data(self):
        with self.assertRaises(TypeError):
            PathmapTile.from_data(None)

        with self.assertRaises(AssertionError):
            PathmapTile.from_data("foobar")

        with self.assertRaises(TypeError):
            PathmapTile.from_data("foobar12")

        with self.assertRaises(TypeError):
            PathmapTile.from_data(1)

        with self.assertRaises(AssertionError):
            PathmapTile.from_data([])

        with self.assertRaises(AssertionError):
            PathmapTile.from_data([1])

    def test_from_file_sets_correct_flag(self):
        file = BytesIO(bytes([0, 0, 0, 0]))
        pm = PathmapTile.from_file(file, 1)
        self.assertEqual(PathmapTile.FLAG_DOGO, pm.flag)

        file = BytesIO(bytes([1, 0, 0, 0]))
        pm = PathmapTile.from_file(file, 1)
        self.assertEqual(PathmapTile.FLAG_NOGO, pm.flag)

        file = BytesIO(bytes([0xff, 0xff, 0xff, 0xff, 0x81]))
        pm = PathmapTile.from_file(file, 1)
        self.assertEqual(PathmapTile.FLAG_MIXED, pm.flag)
        self.assertEqual(1, len(pm.data))
        self.assertEqual(0x81, pm.data[0])

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

if __name__ == '__main__':
    unittest.main()