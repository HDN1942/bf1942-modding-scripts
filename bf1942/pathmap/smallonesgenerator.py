from .pathmap import PathmapTile
from .smallones import Smallones

class SmallonesGenerator:
    DEF_OFF = 48 # default offset? something binary?

    def __init__(self, pathmap):
        self._pathmap = pathmap
        self._tile_length = pathmap.header.tile_length
        self._tile_total = pathmap.header.tile_total
        self._tiles = []

        self.smallones = Smallones.new(self._tile_length)

        self._setup()
        self._generate()

    def _setup(self):
        for i in range(self._tile_total):
            so_tile = self.smallones.tiles[i]
            pm_tile = self._pathmap.tiles[i]
            self._tiles.append(SmallonesGeneratorTile(self, i))

        for i in range(self._tile_total):
            tile = self._tiles[i]
            tile.above = self._tile_above(i)
            tile.before = self._tile_before(i)

    def _tile_above(self, index):
        '''Get the tile above the tile at index, if one exists.'''

        assert index >= 0
        assert index < self._tile_total

        new_index = index - self._tile_length
        return self._tiles[new_index] if new_index >= 0 else None

    def _tile_before(self, index):
        '''Get the tile before (to the left of) the tile at tile index, if one exists.'''

        assert index >= 0
        assert index < self._tile_total

        column = index % self._tile_length
        return self._tiles[index - 1] if column > 0 else None

    def _generate(self):
        for y in range(self._tile_length):
            for x in range(self._tile_length):
                index = y * self._tile_length + x
                tile = self._tiles[index]

                if tile.pm.flag == PathmapTile.FLAG_NOGO:
                    # nothing to do, tile can't have a waypoint
                    pass
                elif tile.pm.flag == PathmapTile.FLAG_DOGO:
                    self._set_point(index, 0, self.DEF_OFF, self.DEF_OFF)
                else:
                    pass # findAreas

    def _set_point(self, tile_index, level, x, y):
        tile = self._tiles[tile_index]

        # set waypoint for this level and mark it as active
        tile.activate(x, y, level)

        if tile.above and tile.above.so.active:
            pass

        if tile.before and tile.before.so.active:
            pass

class SmallonesGeneratorTile:
    def __init__(self, generator, index):
        self.generator = generator
        self.index = index
        self.so = self.generator.smallones.tiles[index]
        self.pm = self.generator._pathmap.tiles[index]
        self.above = None
        self.before = None

    def activate(self, x, y, level):
        self.so.pt[level][0] = x
        self.so.pt[level][1] = y
        self.so.active |= 1 << 4 + level
