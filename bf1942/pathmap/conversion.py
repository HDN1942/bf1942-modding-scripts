import math
from pathlib import Path
from PIL import Image, ImageDraw
from bf1942.pathmap.pathmap import Pathmap, PathmapHeader, PathmapTile
from bf1942.pathmap.shell import SUPPORTED_FORMATS, parse_pathmap_filename

COLOR_DOGO = 0
COLOR_NOGO = 255

LEVEL0_RESOLUTION = 6 # ln2 value, 64 in base 10

DDS_TILE_SIZE = 256

def convert_pathmap(source, destination, in_format, out_format, compression_level=0):
    '''Convert pathmap to/from raw and image formats.'''

    assert source is not None
    assert destination is not None
    assert in_format in SUPPORTED_FORMATS
    assert out_format in SUPPORTED_FORMATS
    assert in_format != out_format
    assert in_format == 'raw' or out_format == 'raw'

    source_path = Path(source)
    destination_path = Path(destination)

    if source_path.is_file():
        assert in_format in ['raw', 'bmp', 'png']
    else:
        assert in_format == 'dds' and source_path.is_dir()

    if out_format in ['dds', 'raw']:
        assert destination_path.is_dir()

    assert source_path.is_dir() or source_path != destination_path

    if destination_path.is_dir() and out_format in ['bmp', 'png']:
        destination_path /= f'{source_path.stem}.{out_format}'

    if in_format == 'raw':
        if out_format == 'dds':
            pathmap_to_textures(source_path, destination_path)
        else:
            pathmap_to_image(source_path, destination_path)
    else:
        if in_format == 'dds':
            textures_to_pathmap(source_path, destination_path, compression_level)
        else:
            image_to_pathmap(source_path, destination_path)

def pathmap_to_image(source, destination):
    '''Convert a pathmap raw file to an image file.'''

    pathmap = Pathmap.load(source)

    with image_from_pathmap(pathmap) as image:
        image.save(destination)

def image_to_pathmap(source, destination):
    '''Convert an image file to pathmap raw files.'''

    info = parse_pathmap_filename(source)
    compression_level = 2 if info.is_boat else 0

    with Image.open(source) as image:
        pathmap = pathmap_from_image(image, compression_level)

    generate_pathmap_files(pathmap, source, destination)

def textures_to_pathmap(source, destination, compression_level=0):
    '''Convert DDS textures to pathmap raw files.'''

    with image_from_textures(source) as image:
        if compression_level > 0:
            size = image.width >> compression_level
            resized = image.resize((size, size), Image.NEAREST)
            pathmap = pathmap_from_image(resized, compression_level)
        else:
            pathmap = pathmap_from_image(image)

    generate_pathmap_files(pathmap, source, destination)

def pathmap_to_textures(source, destination):
    '''Convert a pathmap raw file to DDS textures.'''

    pathmap = Pathmap.load(source)

    with image_from_pathmap(pathmap) as image:
        if pathmap.header.compression_level > 0:
            # image must be resized to map size if compressed
            size = image.width << pathmap.header.compression_level
            resized = image.resize((size, size), Image.NEAREST)
            textures_from_image(resized, destination)
        else:
            textures_from_image(image, destination)

def pathmap_from_image(image, compression_level=0):
    '''Convert a PIL Image to a Pathmap object.'''

    header = pathmap_header_from_image(image, compression_level)

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

def image_from_pathmap(pathmap):
    '''Convert a Pathmap object to a PIL image.'''

    header = pathmap.header

    if header.is_info:
        raise ValueError('Pathmap is an infomap')

    size = header.map_width >> header.compression_level
    image = Image.new('1', (size, size))
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

def pathmap_header_from_image(image, compression_level):
    '''Create a PathmapHeader instance from an image.'''

    if image.width != image.height:
        raise ValueError('Image must be square')

    if image.width % 8 > 0:
        raise ValueError('Image must be evenly divisible by 8')

    resolution = LEVEL0_RESOLUTION + compression_level
    # image size is already compressed
    tiles = image.width >> LEVEL0_RESOLUTION
    ln2_tiles = int(tiles - 1).bit_length()

    return PathmapHeader((ln2_tiles, ln2_tiles, resolution, compression_level, 0, 2))

def draw_mixed(image, data, x, y, tile_size):
    for tile_y in range(tile_size):
        for tile_x in range(tile_size):
            index = tile_y * tile_size + tile_x

            # DOGO (True) is black, the default color
            if data[index]:
                continue

            pixel_x = x + tile_x
            pixel_y = y + tile_y

            image.putpixel((pixel_x, pixel_y), COLOR_NOGO)

def image_from_textures(source):
    '''Convert a directory containing DDS textures to an image.'''

    source_path = Path(source)

    tex_re = re.compile(r'tx(\d{2})x(\d{2})\.dds', re.IGNORECASE)

    textures = [f for f in source_path.iterdir() if f.is_file() and tex_re.match(f.name)]
    texture_count = len(textures)

    tile_count = math.isqrt(texture_count)
    if tile_count * tile_count != texture_count or tile_count % 4 > 0:
        raise FileNotFoundError('Invalid number of texture files')

    image_size = tile_count * DDS_TILE_SIZE
    merge = Image.new('1', (image_size, image_size))

    for texture in textures:
        match = tex_re.match(texture.name)
        x = int(match.group(1)) * DDS_TILE_SIZE
        y = int(match.group(2)) * DDS_TILE_SIZE

        with Image.open(texture) as tx:
            tx_half = tx.resize((DDS_TILE_SIZE, DDS_TILE_SIZE), Image.NEAREST)
            merge.paste(tx_half, (x, y))

    return merge.transpose(Image.FLIP_TOP_BOTTOM)

def textures_from_image(image, destination):
    '''Convert an image into a series of DDS textures.'''

    destination_path = Path(destination)

    tile_count = image.width / DDS_TILE_SIZE
    if image.width != image.height or tile_count % 4 > 0:
        raise FileNotFoundError('Invalid image size')

    for iy in range(0, image.height, DDS_TILE_SIZE):
        for ix in range(0, image.width, DDS_TILE_SIZE):
            file = destination_path / f'tx{iy // DDS_TILE_SIZE:02}x{ix // DDS_TILE_SIZE:02}.dds'

            image.crop((ix, iy, ix + DDS_TILE_SIZE, iy + DDS_TILE_SIZE)) \
                .resize((DDS_TILE_SIZE * 2, DDS_TILE_SIZE * 2), Image.NEAREST) \
                .transpose(Image.FLIP_TOP_BOTTOM) \
                .convert(mode='RGB') \
                .save(file) # TODO requires DXT1/BC1 non-alpha mode, but it's not supported (yet)

def generate_pathmap_files(pathmap, source, destination):
    info = parse_pathmap_filename(source)

    pathmap.save(destination / f'{info.name}{info.index}Level{pathmap.header.compression_level}Map.raw')

    from bf1942.pathmap.processor import PathmapProcessor
    processor = PathmapProcessor()
    levels, smallones, infomap = processor.process(pathmap)

    for i, level in enumerate(levels):
        level.save(destination / f'{info.name}{info.index}Level{level.header.compression_level}Map.raw')

    smallones.save(destination / f'{info.name}.raw')
    infomap.save(destination / f'{info.name}Info.raw')
