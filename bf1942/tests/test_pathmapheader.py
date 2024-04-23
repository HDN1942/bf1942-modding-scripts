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

    def test_derived(self):
        # 2048 level 0 map
        pm = PathmapHeader((5, 5, 6, 0, 0, 2))

        self.assertEqual(32, pm.tilesPerRow)
        self.assertEqual(32, pm.tilesPerCol)
        self.assertEqual(1024, pm.tiles)
        self.assertEqual(64, pm.rowsPerTile)
        self.assertEqual(8, pm.bytesPerRow)
        self.assertEqual(512, pm.bytesPerTile)

        # 2048 level 1 map
        pm = PathmapHeader((4, 4, 7, 1, 0, 2))

        self.assertEqual(16, pm.tilesPerRow)
        self.assertEqual(16, pm.tilesPerCol)
        self.assertEqual(256, pm.tiles)
        self.assertEqual(64, pm.rowsPerTile)
        self.assertEqual(8, pm.bytesPerRow)
        self.assertEqual(512, pm.bytesPerTile)

        # 2048 info map
        pm = PathmapHeader((5, 5, 6, 1, 1, 2))
        self.assertEqual(32, pm.tilesPerRow)
        self.assertEqual(32, pm.tilesPerCol)
        self.assertEqual(1024, pm.tiles)
        self.assertEqual(32, pm.rowsPerTile)
        self.assertEqual(8, pm.bytesPerRow)
        self.assertEqual(256, pm.bytesPerTile)

        # 4096 level 0 map
        pm = PathmapHeader((6, 6, 6, 0, 0, 2))

        self.assertEqual(64, pm.tilesPerRow)
        self.assertEqual(64, pm.tilesPerCol)
        self.assertEqual(4096, pm.tiles)
        self.assertEqual(64, pm.rowsPerTile)
        self.assertEqual(8, pm.bytesPerRow)
        self.assertEqual(512, pm.bytesPerTile)

        # 4096 level 2 map
        pm = PathmapHeader((4, 4, 8, 2, 0, 2))

        self.assertEqual(16, pm.tilesPerRow)
        self.assertEqual(16, pm.tilesPerCol)
        self.assertEqual(256, pm.tiles)
        self.assertEqual(64, pm.rowsPerTile)
        self.assertEqual(8, pm.bytesPerRow)
        self.assertEqual(512, pm.bytesPerTile)

        # 4096 info map
        pm = PathmapHeader((6, 6, 6, 1, 1, 2))
        self.assertEqual(64, pm.tilesPerRow)
        self.assertEqual(64, pm.tilesPerCol)
        self.assertEqual(4096, pm.tiles)
        self.assertEqual(32, pm.rowsPerTile)
        self.assertEqual(8, pm.bytesPerRow)
        self.assertEqual(256, pm.bytesPerTile)

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