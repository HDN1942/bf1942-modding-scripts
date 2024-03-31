import shutil
import subprocess
from PIL import Image
from pathlib import Path
from tempfile import TemporaryDirectory
from bf1942.shell import eprint

PATHMAP_TYPES = [
    'Tank0Level0Map',
    'Infantry1Level0Map',
    'Boat2Level2Map',
    'LandingCraft3Level0Map',
    'Car4Level0Map'
]

GENPATHMAPS_RAW_MODE = 'raw'
GENPATHMAPS_BMP_MODE = 'bmp'

def genpathmaps(src, dst):
    src_path = Path(src)
    dst_path = Path(dst)

    mode = GENPATHMAPS_BMP_MODE if src_path.suffix == '.raw' else GENPATHMAPS_RAW_MODE
    mode_switches = ['-B'] if mode == GENPATHMAPS_BMP_MODE else ['-M', '-I', '-S']

    exe_path = Path(__file__).parent.parent / 'tools' / 'genpathmaps'

    with TemporaryDirectory() as tmp:
        if src_path.suffix == '.png':
            tmp_src_path = Path(tmp) / (src_path.stem + '.bmp')
            convert_image(src_path, tmp_src_path)
            src_path = tmp_src_path

        ret = subprocess.run([exe_path, '-v', *mode_switches, src_path, tmp], capture_output=True, text=True)
        if ret.returncode > 0:
            return False

        if dst_path.suffix == '.raw':
            dst_path = dst_path.parent
            raw_files = [f for f in Path(tmp).iterdir() if f.suffix == '.raw']
            for file in raw_files:
                shutil.copy(file, dst_path)
        else:
            out_path = Path(tmp) / (src_path.stem + '.bmp')
            if dst_path.suffix == '.png':
                convert_image(out_path, dst_path)
            elif dst_path.suffix == '.bmp':
                shutil.copyfile(out_path, dst_path)

    return True

def convert_image(source_file, destination_file):
    try:
        with Image.open(source_file) as im:
            im.save(destination_file)
    except OSError:
        return False
    return True

def convert_pathmap(src, dst, in_fmt, out_fmt, ovr):
    source_path = Path(src)
    destination_path = Path(dst)

    pm_types = [f'{f}.{in_fmt}' for f in PATHMAP_TYPES]
    in_pms = [f for f in source_path.iterdir() if f.is_file() and f.name in pm_types]

    for in_pm in in_pms:
        dst_item = destination_path / f'{in_pm.stem}.{out_fmt}'

        if dst_item.exists() and ovr is False:
            print(f'pathmap: skip: {dst_item.name}')
            continue

        if dst_item.exists():
            print(f'pathmap: overwrite: {dst_item.name}')
        else:
            print(f'pathmap: convert: {dst_item.name}')

        if genpathmaps(in_pm, dst_item) is False:
            eprint(f'pathmap: error converting "{in_pm}"')
