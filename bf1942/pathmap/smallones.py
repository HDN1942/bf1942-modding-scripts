import struct

class SmallonesHeader:
    def __init__(self, data):
        assert len(data) == 2
        assert data[0] == data[1]

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

class SmallonesTile:
    TILE_FORMAT = '=HHBBBBBBBBBBBB'

    def __init__(self, data):
        assert len(data) == 14

        self.has_lower = data[0]
        '''Smallone has a lower neighbor?'''

        self.has_right = data[1]
        '''Smallone has a right neighbor?'''

        self.pt = []

        for i in range(2, 10, 2):
            self.pt.append((data[i], data[i + 1]))

        self.active = data[10]

        self.unknown1 = data[11]
        '''Unknown field 1'''

        self.unknown2 = data[12]
        '''Unknown field 2'''

        self.unknown3 = data[13]
        '''Unknown field 3'''

    def write(self, file):
        data = [
            self.has_lower,
            self.has_right,
        ]

        for a, b in self.pt:
            data.append(a)
            data.append(b)

        data.append(self.active)
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
    def new(cls, tile_length):
        '''Create a blank smallones map.'''

        header = SmallonesHeader([tile_length, tile_length])

        tiles = []
        for _ in range(header.tile_total):
            tiles.append(SmallonesTile([0 for _ in range(14)]))

        return Smallones(header, tiles)

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
