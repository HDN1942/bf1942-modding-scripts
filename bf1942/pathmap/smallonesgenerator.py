from .pathmap import PathmapTile
from .smallones import Smallones, SmallonesTile

class SmallonesGenerator:
    DEF_OFF = 48 # default offset? something binary?

    def __init__(self, pathmap):
        self._pathmap = pathmap
        self._tile_length = pathmap.header.tile_length
        self._tile_total = pathmap.header.tile_total
        self._tile_size = pathmap.header.tile_size
        self._tiles = []

        self.smallones = Smallones.new(self._tile_length)

        self._setup()
        self._generate()

    @classmethod
    def generate(cls, pathmap):
        generator = SmallonesGenerator(pathmap)
        return generator.smallones

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

    def _set_point(self, tile_index, waypoint_index, x, y):
        tile = self._tiles[tile_index]

        # set waypoint for this level and mark it as active
        tile.activate(x, y, waypoint_index)

        if tile.above and tile.above.active:
            for i in range(SmallonesTile.WAYPOINT_COUNT):
                is_connected = False

                for top_y in range(self._tile_size):
                    bottom_y = self._tile_size * (self._tile_size - 1) + top_y
                    if tile.pm.data[top_y] and tile.above.pm.data[bottom_y]:
                        is_connected = True
                        break

                tile.above.so.waypoints[i].connected_bottom[waypoint_index] = is_connected

        if tile.before and tile.before.active:
            for i in range(SmallonesTile.WAYPOINT_COUNT):
                is_connected = False

                for right_x in range(0, self._tile_size * self._tile_size, self._tile_size):
                    left_x = right_x + self._tile_size - 1
                    if tile.pm.data[right_x] and tile.before.pm.data[left_x]:
                        is_connected = True
                        break

                tile.before.so.waypoints[i].connected_right[waypoint_index] = is_connected

class SmallonesGeneratorTile:
    def __init__(self, generator, index):
        self.generator = generator
        self.index = index
        self.so = self.generator.smallones.tiles[index]
        self.pm = self.generator._pathmap.tiles[index]
        self.above = None
        self.before = None
        self.active = False

    def activate(self, x, y, waypoint_index):
        wp = self.so.waypoints[waypoint_index]
        wp.x = x
        wp.y = y
        wp.active = True
        self.active = True

def generate_smallones(pathmap):
    return SmallonesGenerator.generate(pathmap)