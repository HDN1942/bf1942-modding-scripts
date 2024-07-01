import math
import struct
from pathlib import Path
from bf1942.pathmap.util import all_same, pack_data, unpack_data, pack_data2b, unpack_data2b

class PathmapHeader:
    '''Header for a raw pathmap file.'''

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
        '''Whether this is an infomap or not, 1 - info, 0 - not info. Infomaps use 2 bits to record nogo or dogo area 0-3 per point in the map.'''

        self.data_offset = data[5]
        '''Number of DWORDs (32 bits) to seek after header to get to data start. Value must be 0 or 2.'''

        # attributes derived from above

        self.tile_length = None
        '''Number of tiles across x/y axises.'''

        self.tile_total = None
        '''Total number of tiles.'''

        self.tile_size = None
        '''Number of DOGO/NOGO values across tile x/y axises, will be 64 for regular pathmaps and 32 for infomaps.'''

        self.tile_packed_size = None
        '''Packed size of the tile data in bytes, will be 512 (64 ^ 2 / 8) for regular pathmaps and 256 (32 ^ 2 * 2 / 8) for infomaps.'''

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

        if self.is_info:
            self.tile_size = InfomapTile.TILE_SIZE
            self.tile_packed_size = InfomapTile.PACKED_SIZE
        else:
            self.tile_size = PathmapTile.TILE_SIZE
            self.tile_packed_size = PathmapTile.PACKED_SIZE

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

    TILE_SIZE = 64
    UNPACKED_SIZE = 4096
    PACKED_SIZE = 512

    FLAG_MIXED = -1
    FLAG_DOGO = 0
    FLAG_NOGO = 1

    def __init__(self, flag, data):
        self.flag = flag
        '''Flag indicating type of tile, one of FLAG_DOGO, FLAG_NOGO or FLAG_MIXED.'''

        self.data = data
        '''Tile data as a list of booleans, length is 4096 (TILE_SIZE ^ 2).'''

    def write(self, file):
        file.write(int(self.flag).to_bytes(4, 'little', signed=True))

        if self.flag == self.FLAG_MIXED:
            ints = [int(not x) for x in self.data]
            file.write(bytes(pack_data(ints)))

    @classmethod
    def from_file(cls, file):
        '''Read tile data from a file.'''

        flag = int.from_bytes(file.read(4), 'little', signed=True)

        if flag not in [cls.FLAG_NOGO, cls.FLAG_DOGO, cls.FLAG_MIXED]:
            raise ValueError(f'Invalid tile flag: {flag}')

        if flag == cls.FLAG_MIXED:
            packed_data = file.read(cls.PACKED_SIZE)
            if len(packed_data) < cls.PACKED_SIZE:
                raise ValueError(f'Invalid tile data length: {len(packed_data)}')

            data = [not bool(x) for x in unpack_data(packed_data)]
            return PathmapTile(flag, data)
        else:
            return PathmapTile.new(flag)

    @classmethod
    def from_data(cls, unpacked_data):
        '''Create tile from a list of ints.'''

        assert len(unpacked_data) == cls.UNPACKED_SIZE
        assert all([isinstance(x, int) for x in unpacked_data])

        data = [not bool(x) for x in unpacked_data]

        if not all_same(data):
            return PathmapTile(cls.FLAG_MIXED, data)
        else:
            flag = cls.FLAG_DOGO if data[0] == True else cls.FLAG_NOGO
            return PathmapTile(flag, data)

    @classmethod
    def new(cls, flag):
        if flag not in [cls.FLAG_NOGO, cls.FLAG_DOGO, cls.FLAG_MIXED]:
            raise ValueError(f'Invalid tile flag: {flag}')

        if flag == cls.FLAG_NOGO:
            return PathmapTile(flag, [False for _ in range(cls.UNPACKED_SIZE)])
        else:
            return PathmapTile(flag, [True for _ in range(cls.UNPACKED_SIZE)])

class InfomapTile:
    '''Represents a tile within a raw infomap file.'''

    TILE_SIZE = 32
    UNPACKED_SIZE = 1024
    PACKED_SIZE = 256

    FLAG_MIXED = -1
    FLAG_DOGO = 0
    FLAG_NOGO = 1

    POINT_AREA_0 = 0
    POINT_AREA_1 = 1
    POINT_AREA_2 = 2
    POINT_NOGO = 3

    def __init__(self, flag, data):
        self.flag = flag
        '''Flag indicating type of tile, one of FLAG_DOGO, FLAG_NOGO or FLAG_MIXED.'''

        self.data = data
        '''Tile data as a list of 2-bit integers, length is determined by tile_size attribute of PathmapHeader.'''

    def write(self, file):
        file.write(int(self.flag).to_bytes(4, 'little', signed=True))

        if self.flag == self.FLAG_MIXED:
            file.write(bytes(pack_data2b(self.data)))

    @classmethod
    def from_file(cls, file):
        '''Read infomap tile from a file.'''

        flag = int.from_bytes(file.read(4), 'little', signed=True)

        if flag not in [cls.FLAG_NOGO, cls.FLAG_DOGO, cls.FLAG_MIXED]:
            raise ValueError(f'Invalid tile flag: {flag}')

        if flag == cls.FLAG_MIXED:
            packed_data = file.read(cls.PACKED_SIZE)
            if len(packed_data) < cls.PACKED_SIZE:
                raise ValueError(f'Invalid tile data length: {len(packed_data)}')

            return InfomapTile(flag, unpack_data2b(packed_data))
        else:
            return InfomapTile.new(flag)

    @classmethod
    def new(cls, flag):
        if flag not in [cls.FLAG_NOGO, cls.FLAG_DOGO, cls.FLAG_MIXED]:
            raise ValueError(f'Invalid tile flag: {flag}')

        if flag == cls.FLAG_NOGO:
            return InfomapTile(flag, [3 for _ in range(cls.UNPACKED_SIZE)])
        else:
            return InfomapTile(flag, [0 for _ in range(cls.UNPACKED_SIZE)])

class Pathmap:
    '''A raw pathmap.'''

    def __init__(self, header, tiles):
        self.header = header
        '''The pathmap header.'''

        self.tiles = tiles
        '''Tiles within the pathmap. Will be instances of PathmapTile for normal pathmaps or InfomapTile for infomaps.'''

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
                if header.is_info:
                    tiles.append(InfomapTile.from_file(file))
                else:
                    tiles.append(PathmapTile.from_file(file))

            # check we're at EOF
            if file.read(1) != b'':
                raise ValueError('Invalid data length')

        return Pathmap(header, tiles)
