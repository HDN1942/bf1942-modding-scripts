import unittest
from io import BytesIO
from struct import pack
from bf1942.pathmap.smallones import SmallonesTile

class SmallonesTileTest(unittest.TestCase):
    def test_from_file(self):
        data = pack(SmallonesTile.TILE_FORMAT, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14)
        file = BytesIO(data)

        tile = SmallonesTile.from_file(file)

        self.assertEqual(1, tile.has_lower)
        self.assertEqual(2, tile.has_right)
        self.assertEqual(3, tile.pt[0][0])
        self.assertEqual(4, tile.pt[0][1])
        self.assertEqual(5, tile.pt[1][0])
        self.assertEqual(6, tile.pt[1][1])
        self.assertEqual(7, tile.pt[2][0])
        self.assertEqual(8, tile.pt[2][1])
        self.assertEqual(9, tile.pt[3][0])
        self.assertEqual(10, tile.pt[3][1])
        self.assertEqual(11, tile.active)
        self.assertEqual(12, tile.unknown1)
        self.assertEqual(13, tile.unknown2)
        self.assertEqual(14, tile.unknown3)

    def test_write(self):
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
        tile = SmallonesTile(data)
        file = BytesIO()

        tile.write(file)
        file.seek(0, 0)

        data_bytes = bytes([1, 0, 2, 0, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14])
        self.assertSequenceEqual(data_bytes, file.read(16))

if __name__ == '__main__':
    unittest.main()
