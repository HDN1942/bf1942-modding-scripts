import unittest
import bf1942.testutil as testutil
from bf1942.pathmap.pathmap import Pathmap, PathmapHeader, PathmapTile
from bf1942.pathmap.smallonesgenerator import SmallonesGenerator
from bf1942.pathmap.util import all_same

class SmallonesGeneratorTest(unittest.TestCase):
    def setUp(self):
        header = PathmapHeader([4, 4, 6, 0, 0, 2])
        tiles = [PathmapTile.new(PathmapTile.FLAG_DOGO, 64) for _ in range(256)]
        pm = Pathmap(header, tiles)

        self.generator = SmallonesGenerator(pm)
        self.generator._setup()

    def test_generate_dogos(self):
        smallones = self.generator.generate()

        for x in range(16):
            for y in range(16):
                tile = smallones.tiles[y * 16 + x]

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

    def test_find_areas_four_rectangles(self):
        tile = self.generator._tiles[0]
        tile.pm.data = [False for _ in range(64 * 64)]
        self._draw_rect(tile.pm.data, 31, 0, 4, 4)    # 31/0  34/3
        self._draw_rect(tile.pm.data, 0, 60, 10, 4)   #  0/60 9/63
        self._draw_rect(tile.pm.data, 10, 10, 10, 10) # 10/10 19/19
        self._draw_rect(tile.pm.data, 32, 32, 16, 16) # 32/32 47/47

        self.generator._find_areas(tile)

        # testutil.write_image('pm', tile.pm.data)
        # testutil.write_image('area_0', tile.areas[0])
        # testutil.write_image('area_1', tile.areas[1])
        # testutil.write_image('area_2', tile.areas[2])
        # testutil.write_image('area_3', tile.areas[3])

        self.assertArea(tile.areas[3], 31, 0, 4, 4)
        self.assertArea(tile.areas[2], 0, 60, 10, 4)
        self.assertArea(tile.areas[1], 10, 10, 10, 10)
        self.assertArea(tile.areas[0], 32, 32, 16, 16)

    def _draw_rect(self, area, x, y, width, height):
        for iy in range(y, y + height):
            for ix in range(x, x + width):
                area[iy * 64 + ix] = True

    def assertArea(self, area, x, y, width, height):
        for iy in range(64):
            for ix in range(64):
                index = iy * 64 + ix
                if iy >= y and iy < y + height and ix >= x and ix < x + width:
                    self.assertTrue(area[index], f"For rectangle {x},{y} {width}x{height} expected {ix},{iy} to be True but it was False")
                else:
                    self.assertFalse(area[index], f"For rectangle {x},{y} {width}x{height} expected {ix},{iy} to be False but it was True")

if __name__ == '__main__':
    unittest.main()
