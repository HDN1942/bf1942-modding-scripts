import os
import shutil
import sys
from pathlib import Path
from bf1942.RFA import RefractorFlatArchive
from bf1942.path import path_join_insensitive, path_equal_insensitive

ARCHIVES_DIRECTORY = 'archives'
BF1942_DIRECTORY = 'bf1942'
LEVELS_DIRECTORY = 'levels'

TOP_LEVEL_RFAS = set([
    'ai',
    'aimeshes',
    'animations',
    'font',
    'menu',
    'objects',
    'shaders',
    'sound',
    'standardmesh',
    'texture',
    'treemesh'
])

BF1942_LEVEL_RFAS = set([
    'game'
])

def get_common_root(dirs):
    dirs = list(set(dirs))

    root = None
    for dir in dirs:
        if root is None:
            root = dir
            continue

        if len(dir.parts) < len(root.parts):
            root = dir

    return root

def compare_dirs(root, compare, dirs):
    root_path = Path(root)
    dirs_lower = set([x.lower() for x in dirs])
    return [path_join_insensitive(root_path, x) for x in (compare & dirs_lower)]

def extract_rfa(src, dst, ovr):
    item = Path(src).name

    rfa = RefractorFlatArchive(src)

    root = get_common_root([Path(f.path).parent for f in rfa.fileList])
    if root is None:
        return

    dst_path = Path(dst) / root

    if dst_path.exists() and ovr is False:
        print(f'extract: skip: {item}')
        return

    if dst_path.exists():
        shutil.rmtree(dst_path)
        print(f'extract: overwrite: {root}')
    else:
        print(f'extract: process: {root}')

    # TODO could be problematic if there are casing differences between destination paths and stored paths
    rfa.extractAll(dst)

def extract_directory(src, dst, ovr):
    src_path = Path(src)
    rfas = [f for f in src_path.iterdir() if f.is_file() and f.suffix == '.rfa']

    for item in rfas:
        extract_rfa(item, dst, ovr)

def extract_mod(src, dst, ovr):
    src_path = Path(src)
    dst_path = Path(dst)
    bf1942_path = src_path / BF1942_DIRECTORY
    levels_path = bf1942_path / LEVELS_DIRECTORY

    for root, dirs, files in os.walk(src_path):
        root_path = Path(root)

        if root_path == src_path:
            paths = [Path(f) for f in files]
            rfas = [p for p in paths if p.suffix == '.rfa' and p.stem.lower() in TOP_LEVEL_RFAS]

            for rfa in rfas:
                extract_rfa(root_path / rfa, dst_path, ovr)

        elif path_equal_insensitive(root_path, bf1942_path):
            paths = [Path(f) for f in files]
            rfas = [p for p in paths if p.suffix == '.rfa' and p.stem.lower() in BF1942_LEVEL_RFAS]

            for rfa in rfas:
                extract_rfa(root_path / rfa, dst_path, ovr)

        elif path_equal_insensitive(root_path, levels_path):
            paths = [Path(f) for f in files]
            rfas = [p for p in paths if p.suffix == '.rfa']

            for rfa in rfas:
                extract_rfa(root_path / rfa, dst_path, ovr)

def pack_mod(src, dst, ovr):
    src_path = Path(src)
    dst_path = Path(dst)
    bf1942_path = src_path / BF1942_DIRECTORY
    levels_path = bf1942_path / LEVELS_DIRECTORY
    
    dst_path.mkdir(parents=True, exist_ok=True)

    for root, dirs, files in os.walk(src_path):
        root_path = Path(root)

        if root_path == src_path:
            items = compare_dirs(root_path, TOP_LEVEL_RFAS, dirs)
            for item in items:
                pack_directory(item, dst_path, ovr, src_path)

        elif path_equal_insensitive(root_path, bf1942_path):
            bf1942_dst_path = path_join_insensitive(dst_path, root_path.name)
            bf1942_dst_path.mkdir(parents=True, exist_ok=True)

            items = compare_dirs(root_path, BF1942_LEVEL_RFAS, dirs)
            for item in items:
                pack_directory(item, bf1942_dst_path, ovr, src_path)

        elif path_equal_insensitive(root_path, levels_path):
            levels_dst_path = path_join_insensitive(dst_path, Path(root_path.parent.name, root_path.name))
            levels_dst_path.mkdir(parents=True, exist_ok=True)

            for item in dirs:
                pack_directory(root_path / item, levels_dst_path, ovr, src_path)

def pack_directory(src, dst, ovr, base):
    src_path = Path(src)
    dst_path = Path(dst)
    rfa_name = f'{src_path.name}.rfa'
    dst_item = dst_path / rfa_name

    if dst_item.exists() and ovr is False:
        print(f'pack: skip: {rfa_name}')
        return

    if dst_item.exists():
        print(f'pack: overwrite: {rfa_name}')
    else:
        print(f'pack: process: {rfa_name}')

    rfa = RefractorFlatArchive(src_path)
    rfa.addDirectory(src_path, str(base))
    rfa.write(dst_item)
