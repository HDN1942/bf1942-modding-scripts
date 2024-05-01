import math
from pathlib import Path
from PIL import Image, ImageDraw
from bf1942.pathmap.pathmap import Pathmap, PathmapHeader, PathmapTile
from bf1942.pathmap.smallones import SmallonesHeader

COLOR_DOGO = 0
COLOR_NOGO = 255

LEVEL0_RESOLUTION = 6

DEF_OFF = 48 # default offset? something binary?

def generate_smallones(pathmap):
    header = SmallonesHeader([pathmap.header.tiles_per_row, pathmap.header.tiles_per_column])

    for y in header.tile_length:
        for x in header.tile_length:
            tile_index = y * header.tile_length + x
            tile = pathmap.tiles[tile_index]

            if tile.flag == FLAG_NOGO:
                # nothing to do, tile can't have a waypoint
                pass
            elif tile.flag == FLAG_DOGO:
                set_point(pathmap, tile_index, 0, DEF_OFF, DEF_OFF)
            else:
                pass # findAreas

def set_point(pathmap, offset, level, col, row):
    pass

def pathmap_to_image(source_file):
    '''Convert a raw pathmap level 0 file to an image.'''

    pathmap = Pathmap.load(source_file)
    header = pathmap.header

    if header.compression_level > 0:
        raise ValueError('Pathmap is not a level 0 map')

    if header.is_info:
        raise ValueError('Pathmap is an info map')

    image = Image.new('1', (header.map_width, header.map_height))
    draw = ImageDraw.Draw(image)

    for y in range(header.tile_length):
        for x in range(header.tile_length):
            index = y * header.tile_length + x
            tile = pathmap.tiles[index]

            x1 = x * header.tile_size
            y1 = y * header.tile_size
            x2 = x1 + header.tile_size - 1
            y2 = y1 + header.tile_size - 1

            if tile.flag == PathmapTile.FLAG_DOGO:
                # DOGO is black, the default color
                pass
            elif tile.flag == PathmapTile.FLAG_NOGO:
                draw.rectangle([x1, y1, x2, y2], fill=COLOR_NOGO)
            else:
                draw_mixed(image, tile.data, x1, y1, header.tile_size)

    return image.transpose(Image.FLIP_TOP_BOTTOM)

def draw_mixed(image, data, x, y, tile_size):
    for tile_y in range(tile_size):
        for tile_x in range(tile_size):
            index = tile_y * tile_size + tile_x

            # DOGO is black, the default color
            dogo = data[index] == 0
            if dogo:
                continue

            pixel_x = x + tile_x
            pixel_y = y + tile_y

            image.putpixel((pixel_x, pixel_y), COLOR_NOGO)

def image_to_pathmap(source_file):
    src_path = Path(source_file)

    assert src_path.is_file()

    with Image.open(src_path) as image:
        header = pathmap_header_from_image(image)

        i = 0
        raw_tiles = [[] for _ in range(header.tile_total)]

        pixels_per_row = image.width

        for pixel in image.transpose(Image.FLIP_TOP_BOTTOM).getdata():
            pixel_y = math.floor(i / pixels_per_row)
            tile_y = math.floor(pixel_y / header.tile_size)
            tile_x = math.floor((i - pixel_y * pixels_per_row) / header.tile_size)

            tile_index = tile_y * header.tile_length + tile_x

            value = 1 if pixel > 0 else 0
            raw_tiles[tile_index].append(value)

            i += 1

    assert all(len(t) / 8 == header.tile_packed_size for t in raw_tiles)

    tiles = [PathmapTile.from_data(t) for t in raw_tiles]

    return Pathmap(header, tiles)

def pathmap_header_from_image(image):
    '''Create a PathmapHeader instance from an image.'''

    if image.width != image.height:
        raise ValueError('Image must be square')

    if image.width % 8 > 0:
        raise ValueError('Image must be evenly divisible by 8')

    level = 0
    resolution = LEVEL0_RESOLUTION + level
    tiles = image.width >> resolution
    ln2_tiles = int(tiles - 1).bit_length()

    return PathmapHeader((ln2_tiles, ln2_tiles, resolution, level, 0, 2))