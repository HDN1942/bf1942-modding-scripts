import math
import struct
from pathlib import Path
from bf1942.pathmap.util import all_same, pack_data, unpack_data

class PathmapHeader:
    '''Header for a raw pathmap file.'''

    INFO_TILE_SIZE = 32
    MAP_TILE_SIZE = 64

    HEADER_FORMAT = '=iiiiii'

    def __init__(self, data):
        assert len(data) == 6

        # attributes read from file

        self.ln2_tiles_per_row = data[0]
        '''Number of tiles per row as a power of 2.'''

        self.ln2_tiles_per_column = data[1]
        '''Number of tiles per column as a power of 2.'''

        self.ln2_tile_resolution = data[2]
        '''Tile resolution as a power of 2.'''

        self.compression_level = data[3]
        '''Compression level between 0-3 for land vehicles, 2-5 for sea.'''

        self.is_info = data[4]
        '''Whether this is an info map or not, 1 - info, 0 - not info.'''

        self.data_offset = data[5]
        '''Number of DWORDs (32 bits) to seek after header to get to data start. Value must be 0 or 2.'''

        # attributes derived from above

        self.tile_length = None
        '''Number of tiles across x/y axises.'''

        self.tile_total = None
        '''Total number of tiles.'''

        self.tile_size = None
        '''Number of DOGO/NOGO values across tile x/y axises, will be 32 for info maps, 64 for all other types.'''

        self.tile_packed_size = None
        '''Packed size of the tile data in bytes.'''

        self.map_width = None
        '''Width of map, same as image width when converting pathmap to image.'''

        self.map_height = None
        '''Height of map, same as image height when converting pathmap to image.'''

        if self.is_valid():
            self._compute_derived()

    def is_valid(self):
        '''Check whether header appears to be valid.'''

        return self.ln2_tiles_per_row == self.ln2_tiles_per_column and \
            self.ln2_tiles_per_row <= 8 and \
            self.ln2_tile_resolution >= 6 and \
            self.ln2_tile_resolution <= 12 and \
            (self.is_info == 0 or self.is_info == 1) and \
            (self.data_offset == 0 or self.data_offset == 2)

    def _compute_derived(self):
        self.tile_length = 1 << self.ln2_tiles_per_row
        self.tile_total = self.tile_length * self.tile_length
        self.tile_size = self.INFO_TILE_SIZE if self.is_info > 0 else self.MAP_TILE_SIZE
        self.tile_packed_size = self.tile_size * 8

        tile_resolution = 1 << self.ln2_tile_resolution

        self.map_height = self.map_width = self.tile_length * tile_resolution

    def write(self, file):
        packed_header = struct.pack(self.HEADER_FORMAT,
            self.ln2_tiles_per_row,
            self.ln2_tiles_per_column,
            self.ln2_tile_resolution,
            self.compression_level,
            self.is_info,
            self.data_offset
        )
        file.write(packed_header)

        if self.data_offset == 2:
            file.write(bytes([0, 0, 0, 0, 0xff, 0xff, 0xff, 0xff]))

    @classmethod
    def from_file(cls, file):
        '''Read header from a file.'''

        header_bytes = file.read(struct.calcsize(cls.HEADER_FORMAT))
        header_data = struct.unpack(cls.HEADER_FORMAT, header_bytes)
        return PathmapHeader(header_data)

class PathmapTile:
    '''Represents a tile within a raw pathmap file.'''

    FLAG_MIXED = -1
    FLAG_DOGO = 0
    FLAG_NOGO = 1

    def __init__(self, flag, data):
        self.flag = flag
        '''Flag indicating type of tile, one of FLAG_DOGO, FLAG_NOGO or FLAG_MIXED.'''

        self.data = data
        '''Tile data as a list of booleans, length is determined by tile_size attribute of PathmapHeader.'''

    def write(self, file):
        file.write(int(self.flag).to_bytes(4, 'little', signed=True))

        if self.flag == self.FLAG_MIXED:
            ints = [int(not x) for x in self.data]
            file.write(bytes(pack_data(ints)))

    @classmethod
    def from_file(cls, file, packed_size):
        '''Read tile data from a file.'''

        assert packed_size > 0

        flag = int.from_bytes(file.read(4), 'little', signed=True)

        if flag not in [cls.FLAG_NOGO, cls.FLAG_DOGO, cls.FLAG_MIXED]:
            raise ValueError(f'Invalid tile flag: {flag}')

        if flag == cls.FLAG_MIXED:
            packed_data = file.read(packed_size)
            if len(packed_data) < packed_size:
                raise ValueError(f'Invalid tile data length: {len(packed_data)}')

            data = [not bool(x) for x in unpack_data(packed_data)]
            return PathmapTile(flag, data)
        else:
            tile_size = math.isqrt(packed_size * 8)
            return PathmapTile.new(flag, tile_size)

    @classmethod
    def from_data(cls, unpacked_data):
        '''Create tile from a list of ints.'''

        assert len(unpacked_data) > 0
        assert all([isinstance(x, int) for x in unpacked_data])

        data = [not bool(x) for x in unpacked_data]

        if not all_same(data):
            return PathmapTile(cls.FLAG_MIXED, data)
        else:
            flag = cls.FLAG_DOGO if data[0] == True else cls.FLAG_NOGO
            return PathmapTile(flag, data)

    @classmethod
    def new(cls, flag, tile_size):
        if flag not in [cls.FLAG_NOGO, cls.FLAG_DOGO, cls.FLAG_MIXED]:
            raise ValueError(f'Invalid tile flag: {flag}')

        if flag == cls.FLAG_NOGO:
            return PathmapTile(flag, [False for _ in range(tile_size * tile_size)])
        else:
            return PathmapTile(flag, [True for _ in range(tile_size * tile_size)])

class Pathmap:
    '''A raw pathmap.'''

    def __init__(self, header, tiles):
        self.header = header
        self.tiles = tiles

    def save(self, destination_file):
        '''Save a raw pathmap file.'''

        with open(destination_file, 'wb') as file:
            self.header.write(file)
            for tile in self.tiles:
                tile.write(file)

    @classmethod
    def load(cls, source_file):
        '''Load a raw pathmap file.'''

        src_path = Path(source_file)

        assert src_path.is_file()

        with open(src_path, 'rb') as file:
            header = PathmapHeader.from_file(file)

            if not header.is_valid():
                raise ValueError('Invalid header')

            file.seek(header.data_offset * 4, 1)

            tiles = []
            for _ in range(header.tile_total):
                tiles.append(PathmapTile.from_file(file, header.tile_packed_size))

            # check we're at EOF
            if file.read(1) != b'':
                raise ValueError('Invalid data length')

        return Pathmap(header, tiles)
