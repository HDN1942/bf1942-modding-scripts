import struct

class SmallonesHeader:
    def __init__(self, data):
        self.tiles_per_row = data[0]
        '''Number of tiles per row.'''

        self.tiles_per_column = data[1]
        '''Number of tiles per column.'''

    def write(self, file):
        file.write(int(self.tiles_per_row).to_bytes(4, 'little'))
        file.write(int(self.tiles_per_column).to_bytes(4, 'little'))

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
