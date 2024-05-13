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
        self._smallones = Smallones.new(self._tile_length)

    def generate(self):
        self._setup()
        self._generate()

        return self._smallones

    def _setup(self):
        for i in range(self._tile_total):
            so_tile = self._smallones.tiles[i]
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
                    tile.areas[0] = [True for _ in range(self._tile_size * self._tile_size)]
                    self._set_point(tile, 0, self.DEF_OFF, self.DEF_OFF)
                else:
                    self._find_areas(tile)

    def _set_point(self, tile, waypoint_index, x, y):
        '''Activate waypoint and connect areas.'''

        tile.so.waypoints[waypoint_index].x = x
        tile.so.waypoints[waypoint_index].y = y
        tile.so.waypoints[waypoint_index].active = True

        if tile.above:
            for i in range(SmallonesTile.WAYPOINT_COUNT):
                wp = tile.above.so.waypoints[i]
                if not wp.active:
                    continue

                is_connected = False

                for top_y in range(self._tile_size):
                    bottom_y = self._tile_size * (self._tile_size - 1) + top_y
                    if tile.areas[waypoint_index][top_y] and tile.above.areas[i][bottom_y]:
                        is_connected = True
                        break

                wp.connected_bottom[waypoint_index] = is_connected

        if tile.before:
            for i in range(SmallonesTile.WAYPOINT_COUNT):
                wp = tile.before.so.waypoints[i]
                if not wp.active:
                    continue

                is_connected = False

                for right_x in range(0, self._tile_size * self._tile_size, self._tile_size):
                    left_x = right_x + self._tile_size - 1
                    if tile.areas[waypoint_index][right_x] and tile.before.areas[i][left_x]:
                        is_connected = True
                        break

                wp.connected_right[waypoint_index] = is_connected

    def _find_areas(self, tile):
        for y in range(self._tile_size):
            is_dogo = False

            for x in range(self._tile_size):
                pm_index = y * self._tile_size + x
                line_end = x

                if not is_dogo and tile.pm.data[pm_index]:
                    is_dogo = True
                    line_start = x
                elif is_dogo and not tile.pm.data[pm_index]:
                    self._add_segment(tile, y, line_start, line_end)
                    is_dogo = False

            if is_dogo:
                line_end = self._tile_size
                self._add_segment(tile, y, line_start, line_end)

        # sort areas largest to smallest
        tile.areas.sort(key=lambda a: a.count(False))

        # addSmallOnes

    def _add_segment(self, tile, y, start, end):
        # TODO possible to incorrectly store smaller areas instead of larger ones if there are more than 4 areas
        for area in tile.areas:
            if True in area:
                # on first row, won't connect to this area
                if y == 0:
                    continue

                above_start_index = (y - 1) * self._tile_size + start

                # area has lines, check if this one connects
                for i in range(above_start_index, above_start_index + end):
                    # if this line connects with the above line then append it to the area
                    if area[i]:
                        self._append_line(area, y, start, end)
                        return
            else:
                # area is empty, add this line
                self._append_line(area, y, start, end)
                return

    def _append_line(self, area, y, start, end):
        start_index = y * self._tile_size + start
        end_index = y * self._tile_size + end

        for i in range(start_index, end_index):
            area[i] = True

class SmallonesGeneratorTile:
    def __init__(self, generator, index):
        self.generator = generator
        self.index = index
        self.so = self.generator._smallones.tiles[index]
        self.pm = self.generator._pathmap.tiles[index]
        self.above = None
        self.before = None
        self.areas = []

        tile_area = self.generator._tile_size * self.generator._tile_size

        for i in range(SmallonesTile.WAYPOINT_COUNT):
            self.areas.append([False for _ in range(tile_area)])

def generate_smallones(pathmap):
    return SmallonesGenerator.generate(pathmap)