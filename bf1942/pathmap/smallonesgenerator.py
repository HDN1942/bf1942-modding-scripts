from shapely import MultiLineString, Polygon
from .pathmap import PathmapTile
from .smallones import Smallones, SmallonesTile

class SmallonesGenerator:
    def __init__(self, pathmap):
        self._pathmap = pathmap
        self._tile_length = pathmap.header.tile_length
        self._tile_total = pathmap.header.tile_total
        self._tile_size = pathmap.header.tile_size
        self._tile_area = self._tile_size * self._tile_size
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
                    tile.areas.append(SmallonesArea.dogo(self._tile_size))
                    self._fill_areas(tile)
                    # genpathmaps uses 48 (top right corner) as the default position for a full DOGO tile.
                    # This implementation uses tile center (32) instead as that's how Dice did it in the original levels.
                    self._set_point(tile, 0, self._tile_size / 2, self._tile_size / 2)
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
                    if tile.areas[waypoint_index].data[top_y] and tile.above.areas[i].data[bottom_y]:
                        is_connected = True
                        break

                wp.connected_bottom[waypoint_index] = is_connected

        if tile.before:
            for i in range(SmallonesTile.WAYPOINT_COUNT):
                wp = tile.before.so.waypoints[i]
                if not wp.active:
                    continue

                is_connected = False

                for right_x in range(0, self._tile_area, self._tile_size):
                    left_x = right_x + self._tile_size - 1
                    if tile.areas[waypoint_index].data[right_x] and tile.before.areas[i].data[left_x]:
                        is_connected = True
                        break

                wp.connected_right[waypoint_index] = is_connected

    def _find_areas(self, tile):
        '''Find contiguous areas in a tile's pathmap.'''

        for y in range(self._tile_size):
            is_dogo = False

            for x in range(self._tile_size):
                pm_index = y * self._tile_size + x
                line_end = x

                if not is_dogo and tile.pm.data[pm_index]:
                    is_dogo = True
                    line_start = x
                elif is_dogo and not tile.pm.data[pm_index]:
                    self._add_line(tile, y, line_start, line_end)
                    is_dogo = False

            if is_dogo:
                line_end = self._tile_size
                self._add_line(tile, y, line_start, line_end)

        # convert collected lines into area objects
        tile.areas = [SmallonesArea.from_lines(a, self._tile_size) for a in tile.areas]

        # sort areas largest to smallest
        tile.areas.sort(key=lambda a: a.size)
        tile.areas.reverse()

        # drop any areas beyond WAYPOINT_COUNT
        tile.areas = tile.areas[0:4]

        self._set_waypoints(tile)

    def _fill_areas(self, tile):
        '''Add up to WAYPOINT_COUNT NOGO areas to tile.'''

        while len(tile.areas) < SmallonesTile.WAYPOINT_COUNT:
            tile.areas.append(SmallonesArea.nogo(self._tile_size))

    def _add_line(self, tile, y, start, end):
        '''Add a line to a connecting area if found or a new area if not found.'''

        for area in tile.areas:
            # on first row, won't connect to this area
            if y == 0:
                continue

            last_line = area[len(area) - 1]
            last_y = last_line[0][1]
            last_start = last_line[0][0]
            last_end = last_line[1][0]

            # if this line connects with the last line then append it to the area
            if last_y == y - 1 and start <= last_end and end >= last_start:
                    area.append([(start, y), (end, y)])
                    return

        # does not connect to existing areas, add a new one
        tile.areas.append([[(start, y), (end, y)]])

    def _set_waypoints(self, tile):
        '''Set waypoint for tile areas using centroid.'''

        for i in range(0, min(len(tile.areas), SmallonesTile.WAYPOINT_COUNT)):
            if tile.areas[i].size == 0:
                continue

            centroid = tile.areas[i].geom.centroid
            x = round(centroid.x)
            y = round(centroid.y)

            self._set_point(tile, i, x, y)

class SmallonesGeneratorTile:
    def __init__(self, generator, index):
        self.generator = generator
        self.index = index
        self.so = self.generator._smallones.tiles[index]
        self.pm = self.generator._pathmap.tiles[index]
        self.above = None
        self.before = None
        self.areas = []

class SmallonesArea:
    def __init__(self, geom, data):
        self.geom = geom
        self.data = data
        self.size = sum([1 for x in self.data if x is True])

    @classmethod
    def from_lines(cls, lines, tile_size):
        geom = MultiLineString(lines)
        data = [False for _ in range(tile_size * tile_size)]

        for line in [l.coords for l in geom.geoms]:
            start_index = int(line[0][1] * tile_size + line[0][0])
            end_index = int(line[0][1] * tile_size + line[1][0])

            for i in range(start_index, end_index):
                data[i] = True

        return SmallonesArea(geom, data)

    @classmethod
    def dogo(cls, tile_size):
        return cls._fill(True, tile_size)

    @classmethod
    def nogo(cls, tile_size):
        return cls._fill(False, tile_size)

    @classmethod
    def _fill(cls, value, tile_size):
        geom = Polygon([(0, 0), (tile_size, 0), (tile_size, tile_size), (0, tile_size), (0, 0)])
        data = [value for _ in range(tile_size * tile_size)]
        return SmallonesArea(geom, data)

def generate_smallones(pathmap):
    generator = SmallonesGenerator(pathmap)
    return generator.generate()