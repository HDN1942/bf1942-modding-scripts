import math
import re
from PIL import Image
from pathlib import Path

TILE_SIZE = 256

def textures_to_image(source_directory):
    assert source_directory is not None

    src_path = Path(source_directory)

    assert src_path.is_dir()

    tex_re = re.compile('tx(\d{2})x(\d{2})\.dds', re.IGNORECASE)

    textures = [f for f in src_path.iterdir() if f.is_file() and tex_re.match(f.name)]
    texture_count = len(textures)

    tile_count = math.isqrt(texture_count)
    if tile_count * tile_count != texture_count or tile_count % 4 > 0:
        raise FileNotFoundError('Invalid number of texture files')

    image_size = tile_count * TILE_SIZE

    merge = Image.new('1', (image_size, image_size))

    for texture in textures:
        match = tex_re.match(texture.name)
        x = int(match.group(1)) * TILE_SIZE
        y = int(match.group(2)) * TILE_SIZE

        with Image.open(texture) as tx:
            tx_half = tx.resize((TILE_SIZE, TILE_SIZE), Image.NEAREST)
            merge.paste(tx_half, (x, y))

    return merge.transpose(Image.FLIP_TOP_BOTTOM)
