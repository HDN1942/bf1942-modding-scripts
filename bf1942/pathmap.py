# Much of this is based on genpathmaps by William Murphy <glyph@intergate.com>
#
# genpathmaps is released under GPL v2 or later,
# Copyright 2004 William Murphy
#
# Original source for genpathmaps is available here:
# https://github.com/HDN1942/genpathmaps

import math
import struct
from pathlib import Path
from PIL import Image, ImageDraw

TILE_SIZE = 64

COLOR_DOGO = 0
COLOR_NOGO = 255

LEVEL0_RESOLUTION = 6

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

        resolution = LEVEL0_RESOLUTION + level
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

def all_same(items):
    assert items is not None
    assert hasattr(items, '__len__')

    if len(items) == 0:
        return True

    return len(set(items)) == 1

def pack_data(data):
    if not all(x >= 0 and x <= 1 for x in data):
        raise ValueError(f'Invalid data, values must be 0 or 1')

    packed_data = []
    bit = 0
    byte = 0

    for go in data:
        byte |= go << bit

        if bit == 7:
            packed_data.append(byte)
            bit = 0
            byte = 0
        else:
            bit += 1

    # data length not a multiple of 8, weird, but that's ok
    if bit > 0:
        packed_data.append(byte)

    return packed_data

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

def pathmap_to_image(source_file):
    '''Convert a raw pathmap level 0 file to an image.'''

    pathmap = Pathmap.load(source_file)

    if pathmap.header.compression_level > 0:
        raise ValueError('Pathmap is not a level 0 map')

    if pathmap.header.is_info:
        raise ValueError('Pathmap is an info map')

    image = Image.new('1', (pathmap.header.map_width, pathmap.header.map_height))
    draw = ImageDraw.Draw(image)

    for row in range(pathmap.header.tiles_per_row):
        for column in range(pathmap.header.tiles_per_column):
            index = row * pathmap.header.tiles_per_column + column
            tile = pathmap.tiles[index]

            x1 = column * TILE_SIZE
            y1 = row * TILE_SIZE
            x2 = x1 + TILE_SIZE - 1
            y2 = y1 + TILE_SIZE - 1

            if tile.flag == PathmapTile.FLAG_DOGO:
                # DOGO is black, the default color
                pass
            elif tile.flag == PathmapTile.FLAG_NOGO:
                draw.rectangle([x1, y1, x2, y2], fill=COLOR_NOGO)
            else:
                draw_mixed(image, pathmap.header, tile.data, x1, y1)

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

def image_to_pathmap(source_file):
    src_path = Path(source_file)

    assert src_path.is_file()

    with Image.open(src_path) as image:
        header = PathmapHeader.from_image(image)

        i = 0
        raw_tiles = [[] for _ in range(header.tile_count)]

        pixels_per_row = image.width

        for pixel in image.transpose(Image.FLIP_TOP_BOTTOM).getdata():
            pixel_row = math.floor(i / pixels_per_row)
            tile_row = math.floor(pixel_row / TILE_SIZE)
            tile_column = math.floor((i - pixel_row * pixels_per_row) / TILE_SIZE)

            tile_index = tile_row * header.tiles_per_row + tile_column

            value = 1 if pixel > 0 else 0
            raw_tiles[tile_index].append(value)

            i += 1

    assert all(len(t) / 8 == header.bytes_per_tile for t in raw_tiles)

    tiles = [PathmapTile.from_data(t) for t in raw_tiles]

    return Pathmap(header, tiles)
