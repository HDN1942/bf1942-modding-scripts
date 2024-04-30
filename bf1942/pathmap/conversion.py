import math
from pathlib import Path
from PIL import Image, ImageDraw
from bf1942.pathmap.pathmap import Pathmap, PathmapHeader, PathmapTile
from bf1942.pathmap.smallones import SmallonesHeader

TILE_SIZE = 64

COLOR_DOGO = 0
COLOR_NOGO = 255

def generate_smallones(pathmap):
    header = SmallonesHeader([pathmap.header.tiles_per_row, pathmap.header.tiles_per_column])

    for row in header.tiles_per_row:
        for column in header.tiles_per_column:
            tile_index = row * header.tiles_per_column + column
            tile = pathmap.tiles[tile_index]

            if tile.flag == FLAG_NOGO:
                pass
            elif tile.flag == FLAG_DOGO:
                pass # setPoint
            else:
                pass # findAreas

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
