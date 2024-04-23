import io
import unittest
from struct import pack
from bf1942.pathmap import PathmapHeader

class PathmapHeaderTest(unittest.TestCase):
    def test_init(self):
        pm = PathmapHeader((1, 2, 3, 4, 5, 6))

        self.assertEqual(1, pm.ln2TilesPerRow)
        self.assertEqual(2, pm.ln2TilesPerCol)
        self.assertEqual(3, pm.ln2TileRes)
        self.assertEqual(4, pm.compLevel)
        self.assertEqual(5, pm.isInfo)
        self.assertEqual(6, pm.dataOffset)

    def test_from_file(self):
        data = pack(PathmapHeader.HEADER_FORMAT, 1, 2, 3, 4, 5, 6)
        file = io.BytesIO(data)

        pm = PathmapHeader.from_file(file)

        self.assertEqual(1, pm.ln2TilesPerRow)
        self.assertEqual(2, pm.ln2TilesPerCol)
        self.assertEqual(3, pm.ln2TileRes)
        self.assertEqual(4, pm.compLevel)
        self.assertEqual(5, pm.isInfo)
        self.assertEqual(6, pm.dataOffset)

    def test_is_valid(self):
        # valid data
        pm = PathmapHeader((5, 5, 6, 0, 0, 2))
        self.assertTrue(pm.is_valid())

        # invalid ln2TilesPerRow/ln2TilesPerCol
        pm = PathmapHeader((5, 4, 6, 0, 0, 2))
        self.assertFalse(pm.is_valid())

        pm = PathmapHeader((4, 5, 6, 0, 0, 2))
        self.assertFalse(pm.is_valid())

        pm = PathmapHeader((9, 9, 6, 0, 0, 2))
        self.assertFalse(pm.is_valid())

        # invalid ln2TileRes
        pm = PathmapHeader((5, 5, 5, 0, 0, 2))
        self.assertFalse(pm.is_valid())

        pm = PathmapHeader((5, 5, 13, 0, 0, 2))
        self.assertFalse(pm.is_valid())

        # invalid isInfo
        pm = PathmapHeader((5, 5, 6, 0, -1, 2))
        self.assertFalse(pm.is_valid())

        pm = PathmapHeader((5, 5, 6, 0, 2, 2))
        self.assertFalse(pm.is_valid())

        # invalid dataOffset
        pm = PathmapHeader((5, 5, 6, 0, 0, 1))
        self.assertFalse(pm.is_valid())

        pm = PathmapHeader((5, 5, 6, 0, 0, 3))
        self.assertFalse(pm.is_valid())

if __name__ == '__main__':
    unittest.main()