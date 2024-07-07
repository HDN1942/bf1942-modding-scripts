import unittest
import bf1942.tests.util as testutil
from bf1942.testutil import write_image
from bf1942.pathmap.conversion import pathmap_to_image
from bf1942.pathmap.pathmap import Pathmap, PathmapHeader, PathmapTile
from bf1942.pathmap.processor import PathmapProcessor
from bf1942.pathmap.smallones import Smallones
from bf1942.pathmap.util import all_same

class PathmapProcessorTest(unittest.TestCase):
    def setUp(self):
        testutil.remove_dummy_files(self)

        self.root = testutil.create_dummy_files({})

        header = PathmapHeader([4, 4, 6, 0, 0, 2])
        tiles = [PathmapTile.new(PathmapTile.FLAG_DOGO) for _ in range(256)]
        self.pathmap = Pathmap(header, tiles)

        self.processor = PathmapProcessor()

    def tearDown(self):
        testutil.remove_dummy_files(self)

    def test_smallones_all_dogos(self):
        _, smallones, _ = self.processor.process(self.pathmap)

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
        self.processor._setup(self.pathmap)

        # valid index
        for y in range(16):
            for x in range(16):
                index = y * 16 + x
                result = self.processor._tile_above(index)

                if y == 0:
                    # no tile above for tiles in first row
                    self.assertIsNone(result)
                else:
                    # will have tile above
                    self.assertEqual(self.processor._tiles[index - 16], result)

        # invalid index
        with self.assertRaises(AssertionError):
            self.processor._tile_above(-1)

        with self.assertRaises(AssertionError):
            self.processor._tile_above(256)

    def test_tile_before(self):
        self.processor._setup(self.pathmap)

        # valid index
        for y in range(16):
            for x in range(16):
                index = y * 16 + x
                result = self.processor._tile_before(index)

                if x == 0:
                    # no tile before for tiles in first column
                    self.assertIsNone(result, f'Index: {index}')
                else:
                    # will have tile before
                    self.assertEqual(self.processor._tiles[index - 1], result)

        # invalid index
        with self.assertRaises(AssertionError):
            self.processor._tile_before(-1)

        with self.assertRaises(AssertionError):
            self.processor._tile_before(256)

    def test_find_areas_four_rectangles(self):
        self.processor._setup(self.pathmap)

        tile = self.processor._tiles[0]
        tile.pm.data = [False for _ in range(PathmapTile.UNPACKED_SIZE)]
        self._draw_rect(tile.pm.data, 31, 0, 4, 4)    # 31/0  34/3
        self._draw_rect(tile.pm.data, 0, 60, 10, 4)   #  0/60 9/63
        self._draw_rect(tile.pm.data, 10, 10, 10, 10) # 10/10 19/19
        self._draw_rect(tile.pm.data, 32, 32, 16, 16) # 32/32 47/47

        self.processor._find_areas(tile)

        self.assertRectangleInArea(tile.areas[3], 31, 0, 4, 4)
        self.assertRectangleInArea(tile.areas[2], 0, 60, 10, 4)
        self.assertRectangleInArea(tile.areas[1], 10, 10, 10, 10)
        self.assertRectangleInArea(tile.areas[0], 32, 32, 16, 16)

    def test_find_areas_two_lines(self):
        self.processor._setup(self.pathmap)

        tile = self.processor._tiles[0]
        tile.pm.data = [False for _ in range(PathmapTile.UNPACKED_SIZE)]

        area0 = [4095, 4094, 4030, 4029, 3965, 3964, 3900, 3899]
        area1 = [0, 1, 65, 66, 130, 131, 195, 196]

        for i in area0:
            tile.pm.data[i] = True

        for i in area1:
            tile.pm.data[i] = True

        self.processor._find_areas(tile)

        self.assertEqual(2, len(tile.areas))
        tileArea0 = self.lines_to_pathmap(tile.areas[0])
        tileArea1 = self.lines_to_pathmap(tile.areas[1])

        for i in range(PathmapTile.UNPACKED_SIZE):
            if i in area0:
                self.assertTrue(tileArea0[i])
            else:
                self.assertFalse(tileArea0[i])

        for i in range(PathmapTile.UNPACKED_SIZE):
            if i in area1:
                self.assertTrue(tileArea1[i])
            else:
                self.assertFalse(tileArea1[i])

    def test_find_areas_only_adds_four_largest_areas(self):
        self.processor._setup(self.pathmap)

        tile = self.processor._tiles[0]
        tile.pm.data = [False for _ in range(PathmapTile.UNPACKED_SIZE)]
        self._draw_rect(tile.pm.data, 31, 0, 4, 4)    #  16
        self._draw_rect(tile.pm.data, 0, 60, 10, 4)   #  40
        self._draw_rect(tile.pm.data, 10, 10, 10, 10) # 100
        self._draw_rect(tile.pm.data, 32, 32, 16, 16) # 256
        self._draw_rect(tile.pm.data, 0, 0, 2, 2)     #   4
        self._draw_rect(tile.pm.data, 8, 0, 4, 3)     #  12
        self._draw_rect(tile.pm.data, 61, 62, 3, 2)   #   6

        self.processor._find_areas(tile)

        self.assertEqual(4, len(tile.areas))
        self.assertRectangleInArea(tile.areas[3], 31, 0, 4, 4)
        self.assertRectangleInArea(tile.areas[2], 0, 60, 10, 4)
        self.assertRectangleInArea(tile.areas[1], 10, 10, 10, 10)
        self.assertRectangleInArea(tile.areas[0], 32, 32, 16, 16)

    def test_e2e_diamonds_four_way_connect(self):
        for y in range(16):
            for x in range(16):
                tile = self.pathmap.tiles[y * 16 + x]
                tile.flag = PathmapTile.FLAG_MIXED
                self._draw_diamond(tile.data)

        levels, smallones, infomap = self.processor.process(self.pathmap)

        for y in range(16):
            for x in range(16):
                tile_index = y * 16 + x
                tile = smallones.tiles[tile_index]
                active_wps = [x for x in tile.waypoints if x.active]
                num_active = sum([1 for x in active_wps])

                num_connected_bottom = 0
                num_connected_right = 0
                for wp in active_wps:
                    num_connected_bottom += sum([1 for x in wp.connected_bottom if x is True])
                    num_connected_right += sum([1 for x in wp.connected_right if x is True])

                self.assertEqual(4, num_active, f"Tile #{tile_index} at {x},{y} has {num_active} active")

                # connected:
                if y == 15:
                    if x == 15:
                        self.assertEqual(0, num_connected_bottom, f"Tile #{tile_index} at {x},{y} has {num_connected_bottom} connected bottom")
                        self.assertEqual(0, num_connected_right, f"Tile #{tile_index} at {x},{y} has {num_connected_right} connected right")
                    else:
                        self.assertEqual(0, num_connected_bottom, f"Tile #{tile_index} at {x},{y} has {num_connected_bottom} connected bottom")
                        self.assertEqual(2, num_connected_right, f"Tile #{tile_index} at {x},{y} has {num_connected_right} connected right")
                elif x == 15:
                    self.assertEqual(2, num_connected_bottom, f"Tile #{tile_index} at {x},{y} has {num_connected_bottom} connected bottom")
                    self.assertEqual(0, num_connected_right, f"Tile #{tile_index} at {x},{y} has {num_connected_right} connected right")
                else:
                    self.assertEqual(2, num_connected_bottom, f"Tile #{tile_index} at {x},{y} has {num_connected_bottom} connected bottom")
                    self.assertEqual(2, num_connected_right, f"Tile #{tile_index} at {x},{y} has {num_connected_right} connected right")

        # roundtrip save/load to test for file validity
        for i, level in enumerate(levels):
            level.save(self.root / f'level{i + 1}.raw')
            Pathmap.load(self.root / f'level{i + 1}.raw')

        smallones.save(self.root / 'smallones.raw')
        Smallones.load(self.root / 'smallones.raw')

        infomap.save(self.root / 'infomap.raw')
        Pathmap.load(self.root / 'infomap.raw')

    def _draw_rect(self, area, x, y, width, height):
        for iy in range(y, y + height):
            for ix in range(x, x + width):
                area[iy * 64 + ix] = True

    def _draw_diamond(self, area):
        for x in range(31, -1, -1):
            count = (32 - x) * 2
            top = 31 - x
            bottom = 32 + x

            for ix in range(x, x + count):
                area[top * 64 + ix] = False
                area[bottom * 64 + ix] = False

    def lines_to_pathmap(self, area):
        pm = [False for _ in range(PathmapTile.UNPACKED_SIZE)]

        for line in [l.coords for l in area.geom.geoms]:
            start_index = int(line[0][1] * PathmapTile.TILE_SIZE + line[0][0])
            end_index = int(line[0][1] * PathmapTile.TILE_SIZE + line[1][0])

            for i in range(start_index, end_index):
                pm[i] = True

        return pm

    def assertRectangleInArea(self, area, x, y, width, height):
        pm = self.lines_to_pathmap(area)

        for iy in range(PathmapTile.TILE_SIZE):
            for ix in range(PathmapTile.TILE_SIZE):
                index = iy * PathmapTile.TILE_SIZE + ix
                if iy >= y and iy < y + height and ix >= x and ix < x + width:
                    self.assertTrue(pm[index], f"For rectangle {x},{y} {width}x{height} expected {ix},{iy} to be True but it was False")
                else:
                    self.assertFalse(pm[index], f"For rectangle {x},{y} {width}x{height} expected {ix},{iy} to be False but it was True")

    def write_debug_images(self, tile):
        testutil.write_image('pm', tile.pm.data)
        testutil.write_image('area_0', self.lines_to_pathmap(tile.areas[0]))
        testutil.write_image('area_1', self.lines_to_pathmap(tile.areas[1]))
        testutil.write_image('area_2', self.lines_to_pathmap(tile.areas[2]))
        testutil.write_image('area_3', self.lines_to_pathmap(tile.areas[3]))

if __name__ == '__main__':
    unittest.main()
