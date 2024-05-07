import struct

class SmallonesHeader:
    def __init__(self, data):
        assert len(data) == 2
        assert data[0] == data[1]
        assert data[0] > 0
        assert data[0] % 8 == 0

        self.tile_length = data[0]
        '''Number of tiles across x/y axises.'''

        self.tile_total = self.tile_length * self.tile_length
        '''Total number of tiles.'''

    def write(self, file):
        file.write(int(self.tile_length).to_bytes(4, 'little'))
        file.write(int(self.tile_length).to_bytes(4, 'little'))

    @classmethod
    def from_file(cls, file):
        '''Read smallones header data from a file.'''

        data = []
        data.append(int.from_bytes(file.read(4), 'little'))
        data.append(int.from_bytes(file.read(4), 'little'))

        return SmallonesHeader(data)

class Waypoint:
    def __init__(self, x, y, active, connected_bottom, connected_right):
        self.x = x
        '''Waypoint x coordinate in tile.'''

        self.y = y
        '''Waypoint y coordinate in tile.'''

        self.active = active
        '''Whether the waypoint is active.'''

        self.connected_bottom = connected_bottom
        '''List of booleans indicating which waypoints in tile below (to the bottom) are connected to this waypoint.'''

        self.connected_right = connected_right
        '''List of booleans indicating which waypoints in tile after (to the right) are connected to this waypoint.'''

class SmallonesTile:
    WAYPOINT_COUNT = 4
    TILE_FORMAT = '=HHBBBBBBBBBBBB'

    def __init__(self, data):
        assert len(data) == 14

        connected_bottom = self._unpack_connections(data[0])
        connected_right = self._unpack_connections(data[1])

        points = []
        for i in range(2, 10, 2):
            points.append([data[i], data[i + 1]])

        self.waypoints = []
        '''List of waypoints in tile.'''

        for i in range(self.WAYPOINT_COUNT):
            # byte flag where 0x10, 0x20, 0x40 and 0x80 indicate active for waypoints 1-4
            active = data[10] & 1 << 4 + i > 0
            wp = Waypoint(points[i][0], points[i][1], active, connected_bottom[i], connected_right[i])
            self.waypoints.append(wp)

        self.unknown1 = data[11]
        '''Unknown field 1'''

        self.unknown2 = data[12]
        '''Unknown field 2'''

        self.unknown3 = data[13]
        '''Unknown field 3'''

    def write(self, file):
        data = [
            self._pack_connections([wp.connected_bottom for wp in self.waypoints]),
            self._pack_connections([wp.connected_right for wp in self.waypoints]),
        ]

        active = 0
        for i in range(self.WAYPOINT_COUNT):
            wp = self.waypoints[i]
            data.append(wp.x)
            data.append(wp.y)
            if wp.active:
                active |= 1 << 4 + i

        data.append(active)
        data.append(self.unknown1)
        data.append(self.unknown2)
        data.append(self.unknown3)

        packed_tile = struct.pack(self.TILE_FORMAT, *data)
        file.write(packed_tile)

    @classmethod
    def from_file(cls, file):
        '''Read smallones tile data from a file.'''

        tile_bytes = file.read(struct.calcsize(cls.TILE_FORMAT))
        tile_data = struct.unpack(cls.TILE_FORMAT, tile_bytes)
        return SmallonesTile(tile_data)

    def _unpack_connections(self, data):
        '''Unpack waypoint connections where data is a short (16 bits) and each bit indicates a connection between two waypoints.'''

        unpacked = []

        for my_wp in range(self.WAYPOINT_COUNT):
            unpacked.append([])
            for their_wp in range(self.WAYPOINT_COUNT):
                is_connected = data & 1 << my_wp + 4 * their_wp > 0
                unpacked[my_wp].append(is_connected)

        return unpacked

    def _pack_connections(self, connections):
        '''Pack waypoint connections into a short (16 bits) bitmap.'''

        packed = 0
        for my_wp in range(self.WAYPOINT_COUNT):
            for their_wp in range(self.WAYPOINT_COUNT):
                if connections[my_wp][their_wp]:
                    packed |= 1 << my_wp + 4 * their_wp

        return packed

class Smallones:
    '''A smallones map.'''

    def __init__(self, header, tiles):
        assert header.tile_total > 0
        assert len(tiles) == header.tile_total

        self.header = header
        self.tiles = tiles

    def save(self, destination_file):
        '''Save a smallones map file.'''

        with open(destination_file, 'wb') as file:
            self.header.write(file)
            for tile in self.tiles:
                tile.write(file)

    @classmethod
    def load(cls, source_file):
        '''Load a smallones map file.'''

        src_path = Path(source_file)

        assert src_path.is_file()

        with open(src_path, 'rb') as file:
            header = SmallonesHeader.from_file(file)

            tiles = []
            for _ in range(header.tile_total):
                tiles.append(SmallonesTile.from_file(file))

            # check we're at EOF
            if file.read(1) != b'':
                raise ValueError('Invalid data length')

        return Smallones(header, tiles)

    @classmethod
    def new(cls, tile_length):
        '''Create a blank smallones map.'''

        header = SmallonesHeader([tile_length, tile_length])

        tiles = []
        for _ in range(header.tile_total):
            tiles.append(SmallonesTile([0 for _ in range(14)]))

        return Smallones(header, tiles)
