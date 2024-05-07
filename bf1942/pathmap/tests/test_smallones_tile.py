import unittest
from io import BytesIO
from struct import pack
from bf1942.pathmap.smallones import SmallonesTile

class SmallonesTileTest(unittest.TestCase):
    def test_from_file(self):
        data = pack(SmallonesTile.TILE_FORMAT, 0xffff, 0xffff, 3, 4, 5, 6, 7, 8, 9, 10, 0xf0, 12, 13, 14)
        file = BytesIO(data)

        tile = SmallonesTile.from_file(file)

        self.assertEqual(3, tile.waypoints[0].x)
        self.assertEqual(4, tile.waypoints[0].y)
        self.assertTrue(tile.waypoints[0].active)
        self.assertEqual([True, True, True, True], tile.waypoints[0].connected_bottom)
        self.assertEqual([True, True, True, True], tile.waypoints[0].connected_right)

        self.assertEqual(5, tile.waypoints[1].x)
        self.assertEqual(6, tile.waypoints[1].y)
        self.assertTrue(tile.waypoints[1].active)
        self.assertEqual([True, True, True, True], tile.waypoints[1].connected_bottom)
        self.assertEqual([True, True, True, True], tile.waypoints[1].connected_right)

        self.assertEqual(7, tile.waypoints[2].x)
        self.assertEqual(8, tile.waypoints[2].y)
        self.assertTrue(tile.waypoints[2].active)
        self.assertEqual([True, True, True, True], tile.waypoints[2].connected_bottom)
        self.assertEqual([True, True, True, True], tile.waypoints[2].connected_right)

        self.assertEqual(9, tile.waypoints[3].x)
        self.assertEqual(10, tile.waypoints[3].y)
        self.assertTrue(tile.waypoints[3].active)
        self.assertEqual([True, True, True, True], tile.waypoints[3].connected_bottom)
        self.assertEqual([True, True, True, True], tile.waypoints[3].connected_right)

        self.assertEqual(12, tile.unknown1)
        self.assertEqual(13, tile.unknown2)
        self.assertEqual(14, tile.unknown3)

    def test_write(self):
        data = [0xffff, 0xffff, 3, 4, 5, 6, 7, 8, 9, 10, 0xf0, 12, 13, 14]
        tile = SmallonesTile(data)
        file = BytesIO()

        tile.write(file)
        file.seek(0, 0)

        data_bytes = bytes([0xff, 0xff, 0xff, 0xff, 3, 4, 5, 6, 7, 8, 9, 10, 0xf0, 12, 13, 14])
        self.assertSequenceEqual(data_bytes, file.read(16))

if __name__ == '__main__':
    unittest.main()
