import unittest
from bf1942.pathmap.pathmap import Pathmap, PathmapHeader, PathmapTile
from bf1942.pathmap.smallonesgenerator import SmallonesGenerator

class SmallonesGeneratorTest(unittest.TestCase):
    def setUp(self):
        header = PathmapHeader([4, 4, 6, 0, 0, 2])
        tiles = [PathmapTile(PathmapTile.FLAG_DOGO) for _ in range(256)]
        pm = Pathmap(header, tiles)

        self.generator = SmallonesGenerator(pm)

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
