# Much of this is based on genpathmaps by William Murphy <glyph@intergate.com>
#
# genpathmaps is released under GPL v2 or later,
# Copyright 2004 William Murphy
#
# Original source for genpathmaps is available here:
# https://github.com/HDN1942/genpathmaps

from pathlib import Path
from struct import calcsize, unpack
from PIL import Image, ImageDraw

TILE_SIZE = 64

COLOR_DOGO = 0
COLOR_NOGO = 255

class PathmapHeader:
    '''Header for a raw pathmap file.'''

    HEADER_FORMAT = '=iiiiii'

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

    @classmethod
    def from_file(cls, file):
        '''Read header from a file.'''

        header_bytes = file.read(calcsize(cls.HEADER_FORMAT))
        header_data = unpack(cls.HEADER_FORMAT, header_bytes)
        return PathmapHeader(header_data)

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

    @classmethod
    def from_file(cls, file, bytes_per_tile):
        '''Read tile data from a file.'''

        flag = int.from_bytes(file.read(4), 'little', signed=True)

        if flag not in [cls.FLAG_NOGO, cls.FLAG_DOGO, cls.FLAG_MIXED]:
            raise ValueError(f'Invalid tile flag: {flag}')

        if flag == cls.FLAG_MIXED:
            data = file.read(bytes_per_tile)
            if len(data) < bytes_per_tile:
                raise ValueError('Invalid tile data length')

            return PathmapTile(flag, data)
        else:
            return PathmapTile(flag)

def load_pathmap(source_file):
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

    return (header, tiles)

def pathmap_to_image(source_file):
    '''Convert a raw pathmap level 0 file to an image.'''

    header, tiles = load_pathmap(source_file)

    if header.compression_level > 0:
        raise ValueError('Pathmap is not a level 0 map')

    if header.is_info:
        raise ValueError('Pathmap is an info map')

    image = Image.new('1', (header.tile_count * 2, header.tile_count * 2))
    draw = ImageDraw.Draw(image)

    for row in range(header.tiles_per_row):
        for column in range(header.tiles_per_column):
            index = row * header.tiles_per_column + column
            tile = tiles[index]

            x1 = column * TILE_SIZE
            y1 = row * TILE_SIZE
            x2 = x1 + TILE_SIZE
            y2 = y1 + TILE_SIZE

            if tile.flag == PathmapTile.FLAG_DOGO:
                # DOGO is black, the default color
                pass
            elif tile.flag == PathmapTile.FLAG_NOGO:
                draw.rectangle([x1, y1, x2, y2], fill=COLOR_NOGO)
            else:
                draw_mixed(image, header, tile.data, x1, y1)

    return image.transpose(Image.FLIP_TOP_BOTTOM)

def draw_mixed(image, header, data, x, y):
    for tile_row in range(header.rows_per_tile):
        for row_byte in range(header.bytes_per_row):
            for bit in range(8):
                byte_index = tile_row * header.bytes_per_row + row_byte
                dogo = data[byte_index] & 1 << bit == 0
                if dogo:
                    # DOGO is black, the default color
                    continue

                pixel_x = x + row_byte * 8 + bit
                pixel_y = y + tile_row

                image.putpixel((pixel_x, pixel_y), COLOR_NOGO)
