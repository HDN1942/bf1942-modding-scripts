import struct
from pathlib import Path
from bf1942.pathmap.util import all_same, pack_data

class PathmapHeader:
    '''Header for a raw pathmap file.'''

    HEADER_FORMAT = '=iiiiii'
    LEVEL0_RESOLUTION = 6

    def __init__(self, data):
        assert len(data) == 6

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

        self.tiles_per_row = None
        '''Number of tiles per row.'''

        self.tiles_per_column = None
        '''Number of tiles per column.'''

        self.tile_count = None
        '''Total number of tiles.'''

        self.rows_per_tile = None
        '''Number of rows per tile.'''

        self.bytes_per_row = None
        '''Number of bytes per row.'''

        self.bytes_per_tile = None
        '''Number of bytes per tile.'''

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
        self.tiles_per_row = 1 << self.ln2_tiles_per_row
        self.tiles_per_column = 1 << self.ln2_tiles_per_column
        self.tile_count = self.tiles_per_row * self.tiles_per_column
        self.rows_per_tile = 1 << self.ln2_tile_resolution - self.compression_level
        self.bytes_per_row = self.rows_per_tile >> 3 - self.is_info
        self.bytes_per_tile = self.rows_per_tile * self.bytes_per_row
        self.map_width = self.tiles_per_column * self.rows_per_tile
        self.map_height = self.tiles_per_row * self.rows_per_tile

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

    @classmethod
    def from_image(cls, image, level=0):
        '''Create a header from an image.'''

        if image.width != image.height:
            raise ValueError('Image must be square')

        if image.width % 8 > 0:
            raise ValueError('Image must be evenly divisible by 8')

        resolution = cls.LEVEL0_RESOLUTION + level
        tiles = image.width >> resolution
        ln2_tiles = int(tiles - 1).bit_length()

        return PathmapHeader((ln2_tiles, ln2_tiles, resolution, level, 0, 2))

class PathmapTile:
    '''Represents a tile within a raw pathmap file.'''

    FLAG_MIXED = -1
    FLAG_DOGO = 0
    FLAG_NOGO = 1

    def __init__(self, flag, data=None):
        self.flag = flag
        '''Flag indicating type of tile, one of FLAG_DOGO, FLAG_NOGO or FLAG_MIXED.'''

        self.data = data
        '''Tile data, size is determined by bytes_per_tile attribute of PathmapHeader, only set when flag is FLAG_MIXED.'''

    def write(self, file):
        file.write(int(self.flag).to_bytes(4, 'little', signed=True))

        if self.flag == self.FLAG_MIXED:
            file.write(bytes(self.data))

    @classmethod
    def from_file(cls, file, bytes_per_tile):
        '''Read tile data from a file.'''

        flag = int.from_bytes(file.read(4), 'little', signed=True)

        if flag not in [cls.FLAG_NOGO, cls.FLAG_DOGO, cls.FLAG_MIXED]:
            raise ValueError(f'Invalid tile flag: {flag}')

        if flag == cls.FLAG_MIXED:
            data = file.read(bytes_per_tile)
            if len(data) < bytes_per_tile:
                raise ValueError(f'Invalid tile data length: {len(data)}')

            return PathmapTile(flag, data)
        else:
            return PathmapTile(flag)

    @classmethod
    def from_data(cls, data):
        '''Create tile from a list of ints.'''

        assert len(data) > 0
        assert len(data) % 8 == 0, 'Expected data to be a multiple of 8'

        if not all_same(data):
            return PathmapTile(cls.FLAG_MIXED, pack_data(data))
        else:
            flag = cls.FLAG_NOGO if data[0] == 1 else cls.FLAG_DOGO
            return PathmapTile(flag)

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
            for _ in range(header.tile_count):
                tiles.append(PathmapTile.from_file(file, header.bytes_per_tile))

            # check we're at EOF
            if file.read(1) != b'':
                raise ValueError('Invalid data length')

        return Pathmap(header, tiles)
