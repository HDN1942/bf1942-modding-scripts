import unittest
import bf1942.tests.util as testutil
from random import randrange
from bf1942.pathmap.pathmap import Pathmap, PathmapHeader, PathmapTile, InfomapTile

class PathmapTest(unittest.TestCase):
    def setUp(self):
        testutil.remove_dummy_files(self)

        self.root = testutil.create_dummy_files({})

    def tearDown(self):
        testutil.remove_dummy_files(self)

    def test_roundtrip_pathmap(self):
        header = PathmapHeader([4, 4, 6, 0, 0, 2])
        tiles = []
        for _ in range(256):
            tiles.append(self.random_pathmap_tile())
        pathmap = Pathmap(header, tiles)

        pathmap.save(self.root / 'test.raw')
        roundtrip = Pathmap.load(self.root / 'test.raw')

        self.assert_pathmap_equal(pathmap, roundtrip)

    def test_roundtrip_infomap(self):
        header = PathmapHeader([4, 4, 6, 0, 1, 2])
        tiles = []
        for _ in range(256):
            tiles.append(self.random_infomap_tile())
        pathmap = Pathmap(header, tiles)

        pathmap.save(self.root / 'test.raw')
        roundtrip = Pathmap.load(self.root / 'test.raw')

        self.assert_pathmap_equal(pathmap, roundtrip)

    def random_pathmap_tile(self):
        flag = randrange(-1, 2)
        tile = PathmapTile.new(flag)

        if flag == PathmapTile.FLAG_MIXED:
            for i in range(len(tile.data)):
                tile.data[i] = bool(randrange(0, 2))

        return tile

    def random_infomap_tile(self):
        flag = randrange(-1, 2)
        tile = InfomapTile.new(flag)

        if flag == InfomapTile.FLAG_MIXED:
            for i in range(len(tile.data)):
                tile.data[i] = randrange(0, 4)

        return tile

    def assert_pathmap_equal(self, pathmap1, pathmap2):
        for i, tile in enumerate(pathmap1.tiles):
            self.assertEqual(pathmap2.tiles[i].flag, pathmap1.tiles[i].flag)
            for j, value in enumerate(tile.data):
                self.assertEqual(pathmap2.tiles[i].data[j], tile.data[j])

if __name__ == '__main__':
    unittest.main()