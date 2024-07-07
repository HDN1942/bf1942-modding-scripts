from shapely import MultiLineString, Polygon
from .pathmap import InfomapTile, Pathmap, PathmapHeader, PathmapTile
from .smallones import Smallones, SmallonesTile
from .util import all_same

class PathmapProcessor:
    '''Processes a pathmap, producing compressed levels, smallones and infomap files.'''

    def process(self, pathmap):
        self._setup(pathmap)
        self._generate_smallones()
        self._generate_info()
        self._generate_compressed_maps()

        return (self._levels, self._smallones, self._info)

    def _setup(self, pathmap):
        self._pathmap = pathmap
        self._tile_length = pathmap.header.tile_length
        self._tile_total = pathmap.header.tile_total
        self._tiles = []
        self._levels = []
        self._smallones = Smallones.new(self._tile_length)
        self._info = None

        for i in range(self._tile_total):
            so_tile = self._smallones.tiles[i]
            pm_tile = self._pathmap.tiles[i]
            self._tiles.append(Tile(self, i))

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

    def _generate_smallones(self):
        for y in range(self._tile_length):
            for x in range(self._tile_length):
                index = y * self._tile_length + x
                tile = self._tiles[index]

                if tile.pm.flag == PathmapTile.FLAG_NOGO:
                    # nothing to do, tile can't have a waypoint
                    pass
                elif tile.pm.flag == PathmapTile.FLAG_DOGO:
                    tile.areas.append(Area.dogo())
                    # genpathmaps uses 48 (top right corner) as the default position for a full DOGO tile.
                    # This implementation uses tile center (32) instead as that's how Dice did it in the original levels.
                    self._set_point(tile, 0, PathmapTile.TILE_SIZE // 2, PathmapTile.TILE_SIZE // 2)
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

                for top_y in range(PathmapTile.TILE_SIZE):
                    bottom_y = PathmapTile.TILE_SIZE * (PathmapTile.TILE_SIZE - 1) + top_y
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

                for right_x in range(0, PathmapTile.UNPACKED_SIZE, PathmapTile.TILE_SIZE):
                    left_x = right_x + PathmapTile.TILE_SIZE - 1
                    if tile.areas[waypoint_index].data[right_x] and tile.before.areas[i].data[left_x]:
                        is_connected = True
                        break

                wp.connected_right[waypoint_index] = is_connected

    def _find_areas(self, tile):
        '''Find contiguous areas in a tile's pathmap.'''

        for y in range(PathmapTile.TILE_SIZE):
            is_dogo = False

            for x in range(PathmapTile.TILE_SIZE):
                pm_index = y * PathmapTile.TILE_SIZE + x
                line_end = x

                if not is_dogo and tile.pm.data[pm_index]:
                    is_dogo = True
                    line_start = x
                elif is_dogo and not tile.pm.data[pm_index]:
                    self._add_line(tile, y, line_start, line_end)
                    is_dogo = False

            if is_dogo:
                line_end = PathmapTile.TILE_SIZE
                self._add_line(tile, y, line_start, line_end)

        # convert collected lines into area objects
        tile.areas = [Area.from_lines(a) for a in tile.areas]

        # sort areas largest to smallest
        tile.areas.sort(key=lambda a: a.size)
        tile.areas.reverse()

        # drop any areas beyond WAYPOINT_COUNT
        tile.areas = tile.areas[0:4]

        self._set_waypoints(tile)

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

    def _generate_info(self):
        # TODO level is 3 for sea vehicles
        # - can get from pathmap?
        level = 1

        info_header = PathmapHeader([
            self._pathmap.header.ln2_tiles_per_row,
            self._pathmap.header.ln2_tiles_per_column,
            self._pathmap.header.ln2_tile_resolution,
            level,
            1, # infomap flag
            2  # standard data offset (2 DWORDs)
        ])

        info_tiles = []

        for tile in self._tiles:
            if tile.pm.flag != PathmapTile.FLAG_MIXED:
                info_tiles.append(InfomapTile.new(tile.pm.flag))
                continue

            info_data = []

            # infomap is half size of top level pathmap
            for y in range(0, PathmapTile.TILE_SIZE, 2):
                for x in range(0, PathmapTile.TILE_SIZE, 2):
                    is_dogo = False
                    area_index = 0

                    # infomap constructed from active areas only
                    for area in tile.areas:
                        # if there is a dogo in this 2x2 block mark the area in the infomap
                        for iy in range(2):
                            for ix in range(2):
                                data_index = (y + iy) * PathmapTile.TILE_SIZE + x + ix

                                if area.data[data_index]:
                                    info_data.append(area_index)
                                    is_dogo = True
                                    break # ix

                            if is_dogo:
                                break # iy

                        if is_dogo:
                            break # area

                        area_index += 1

                        if area_index == 3:
                            # last area is not included in infomap
                            break

                    if not is_dogo:
                        info_data.append(3) # 3 indicates nogo

            if all_same(info_data):
                info_tile = InfomapTile.new(InfomapTile.FLAG_NOGO) if info_tile.data[0] == 3 else InfomapTile.new(InfomapTile.FLAG_DOGO)
            else:
                info_tile = InfomapTile(InfomapTile.FLAG_MIXED, info_data)

            info_tiles.append(info_tile)

        self._info = Pathmap(info_header, info_tiles)

    def _generate_compressed_maps(self):
        pass

class Tile:
    def __init__(self, processor, index):
        self.processor = processor
        self.index = index
        self.so = self.processor._smallones.tiles[index]
        self.pm = self.processor._pathmap.tiles[index]
        self.above = None
        self.before = None
        self.areas = []

class Area:
    def __init__(self, geom, data):
        self.geom = geom
        self.data = data
        self.size = sum([1 for x in self.data if x is True])

    @classmethod
    def from_lines(cls, lines):
        geom = MultiLineString(lines)
        data = [False for _ in range(PathmapTile.UNPACKED_SIZE)]

        for line in [l.coords for l in geom.geoms]:
            start_index = int(line[0][1] * PathmapTile.TILE_SIZE + line[0][0])
            end_index = int(line[0][1] * PathmapTile.TILE_SIZE + line[1][0])

            for i in range(start_index, end_index):
                data[i] = True

        return Area(geom, data)

    @classmethod
    def dogo(cls):
        return cls._fill(True)

    @classmethod
    def nogo(cls):
        return cls._fill(False)

    @classmethod
    def _fill(cls, value):
        geom = Polygon([(0, 0), (PathmapTile.TILE_SIZE, 0), (PathmapTile.TILE_SIZE, PathmapTile.TILE_SIZE), (0, PathmapTile.TILE_SIZE), (0, 0)])
        data = [value for _ in range(PathmapTile.UNPACKED_SIZE)]
        return Area(geom, data)
