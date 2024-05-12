import unittest
from bf1942.pathmap.pathmap import Pathmap, PathmapHeader, PathmapTile
from bf1942.pathmap.smallonesgenerator import SmallonesGenerator
from bf1942.pathmap.util import all_same

class SmallonesGeneratorTest(unittest.TestCase):
    def setUp(self):
        header = PathmapHeader([4, 4, 6, 0, 0, 2])
        tiles = [PathmapTile.new(PathmapTile.FLAG_DOGO, 64) for _ in range(256)]
        pm = Pathmap(header, tiles)

        self.generator = SmallonesGenerator(pm)

    def test_generate_dogos(self):
        for x in range(16):
            for y in range(16):
                tile = self.generator.smallones.tiles[y * 16 + x]

                self.assertTrue(tile.waypoints[0].active)
                self.assertFalse(tile.waypoints[1].active)
                self.assertFalse(tile.waypoints[2].active)
                self.assertFalse(tile.waypoints[3].active)

                if x == 15:
                    self.assertFalse(tile.waypoints[0].connected_right[0])
                    self.assertTrue(all_same(tile.waypoints[0].connected_right))
                else:
                    self.assertTrue(tile.waypoints[0].connected_right[0])
                    self.assertFalse(tile.waypoints[0].connected_right[1])
                    self.assertFalse(tile.waypoints[0].connected_right[2])
                    self.assertFalse(tile.waypoints[0].connected_right[3])

                if y == 15:
                    self.assertFalse(tile.waypoints[0].connected_bottom[0])
                    self.assertTrue(all_same(tile.waypoints[0].connected_bottom))
                else:
                    self.assertTrue(tile.waypoints[0].connected_bottom[0])
                    self.assertFalse(tile.waypoints[0].connected_bottom[1])
                    self.assertFalse(tile.waypoints[0].connected_bottom[2])
                    self.assertFalse(tile.waypoints[0].connected_bottom[3])

                self.assertFalse(tile.waypoints[1].connected_bottom[0])
                self.assertTrue(all_same(tile.waypoints[1].connected_bottom))
                self.assertFalse(tile.waypoints[1].connected_right[0])
                self.assertTrue(all_same(tile.waypoints[1].connected_right))

                self.assertFalse(tile.waypoints[2].connected_bottom[0])
                self.assertTrue(all_same(tile.waypoints[2].connected_bottom))
                self.assertFalse(tile.waypoints[2].connected_right[0])
                self.assertTrue(all_same(tile.waypoints[2].connected_right))

                self.assertFalse(tile.waypoints[3].connected_bottom[0])
                self.assertTrue(all_same(tile.waypoints[3].connected_bottom))
                self.assertFalse(tile.waypoints[3].connected_right[0])
                self.assertTrue(all_same(tile.waypoints[3].connected_right))

    def test_tile_above(self):
        # valid index
        for y in range(16):
            for x in range(16):
                index = y * 16 + x
                result = self.generator._tile_above(index)

                if y == 0:
                    # no tile above for tiles in first row
                    self.assertIsNone(result)
                else:
                    # will have tile above
                    self.assertEqual(self.generator._tiles[index - 16], result)

        # invalid index
        with self.assertRaises(AssertionError):
            self.generator._tile_above(-1)

        with self.assertRaises(AssertionError):
            self.generator._tile_above(256)

    def test_tile_before(self):
        # valid index
        for y in range(16):
            for x in range(16):
                index = y * 16 + x
                result = self.generator._tile_before(index)

                if x == 0:
                    # no tile before for tiles in first column
                    self.assertIsNone(result, f'Index: {index}')
                else:
                    # will have tile before
                    self.assertEqual(self.generator._tiles[index - 1], result)

        # invalid index
        with self.assertRaises(AssertionError):
            self.generator._tile_before(-1)

        with self.assertRaises(AssertionError):
            self.generator._tile_before(256)

if __name__ == '__main__':
    unittest.main()
