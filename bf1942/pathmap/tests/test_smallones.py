import unittest
import bf1942.tests.util as testutil
from random import randrange
from bf1942.pathmap.smallones import Smallones, SmallonesHeader, SmallonesTile

class SmallonesTest(unittest.TestCase):
    def setUp(self):
        testutil.remove_dummy_files(self)

        self.root = testutil.create_dummy_files({})

    def tearDown(self):
        testutil.remove_dummy_files(self)

    def test_roundtrip_smallones(self):
        header = SmallonesHeader([16, 16])
        tiles = []
        for _ in range(256):
            tiles.append(self.random_smallones_tile())
        smallones = Smallones(header, tiles)

        smallones.save(self.root / 'test.raw')
        roundtrip = Smallones.load(self.root / 'test.raw')

        self.assert_smallones_equal(smallones, roundtrip)

    def random_smallones_tile(self):
        tile = SmallonesTile.new()

        for i in range(SmallonesTile.WAYPOINT_COUNT):
            active = randrange(0, 2)
            tile.waypoints[i].active = active

            if active:
                tile.waypoints[i].x = randrange(0, 65)
                tile.waypoints[i].y = randrange(0, 65)
                for j in range(SmallonesTile.WAYPOINT_COUNT):
                    tile.waypoints[i].connected_bottom[j] = bool(randrange(0, 2))
                    tile.waypoints[i].connected_right[j] = bool(randrange(0, 2))

        tile.unknown1 = randrange(0, 256)
        tile.unknown2 = randrange(0, 256)
        tile.unknown3 = randrange(0, 256)

        return tile

    def assert_smallones_equal(self, smallones1, smallones2):
        for i, tile in enumerate(smallones1.tiles):
            for j, value in enumerate(tile.waypoints):
                self.assertEqual(smallones2.tiles[i].waypoints[j].active, tile.waypoints[j].active)
                self.assertEqual(smallones2.tiles[i].waypoints[j].x, tile.waypoints[j].x)
                self.assertEqual(smallones2.tiles[i].waypoints[j].y, tile.waypoints[j].y)
                self.assertEqual(smallones2.tiles[i].waypoints[j].connected_bottom, tile.waypoints[j].connected_bottom)
                self.assertEqual(smallones2.tiles[i].waypoints[j].connected_right, tile.waypoints[j].connected_right)

            self.assertEqual(smallones2.tiles[i].unknown1, smallones1.tiles[i].unknown1)
            self.assertEqual(smallones2.tiles[i].unknown2, smallones1.tiles[i].unknown2)
            self.assertEqual(smallones2.tiles[i].unknown3, smallones1.tiles[i].unknown3)