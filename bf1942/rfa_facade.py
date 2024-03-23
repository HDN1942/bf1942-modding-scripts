import os
import shutil
import sys
from pathlib import Path
from bf1942.RFA import RefractorFlatArchive
from bf1942.path import path_join_insensitive

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

# TODO replace implementation with os.walk?
def tree(target):
    root = Path(target)
    return sub_tree(root, root)

def sub_tree(root, item):
    directories = []
    non_rfas = []
    rfas = []

    for item in item.iterdir():
        sub_path = item.relative_to(root)

        if item.is_dir():
            if item.name == 'Logs':
                continue

            t = sub_tree(root, item)
            directories += t[0]
            non_rfas += t[1]
            rfas += t[2]

            directories.append(sub_path)
        else:
            if item.suffix == '.rfa':
                rfas.append(sub_path)
            else:
                non_rfas.append(sub_path)

    return directories, non_rfas, rfas

def extract_rfa(src, dst, ovr, item):
    src_item = src / item
    dst_item = dst / item.with_name(item.name)

    if dst_item.exists() and ovr is False:
        print(f'extract: skip: {item}')
        return
    
    if dst_item.exists():
        shutil.rmtree(dst_item)
        print(f'extract: overwrite: {item}')
    else:
        print(f'extract: process: {item}')
   
    rfa = RefractorFlatArchive(src_item)
    rfa.extractAll(dst_item)

def extract_archive(src, dst, ovr, name):
    _, _, rfas = tree(src)
    target_rfas = [x for x in rfas if x.stem.lower().find(name) > -1]

    for item in target_rfas:
        extract_rfa(src, dst, ovr, item)

def extract_directory(src, dst, ovr, path):
    _, _, rfas = tree(src)
    level_rfas = [x for x in rfas if str(x).lower().startswith(path.lower())]

    for item in level_rfas:
        extract_rfa(src, dst, ovr, item)

def extract_full(src, dst, ovr):
    directories, non_rfas, rfas = tree(src)

    dst_path = Path(dst)
    for item in directories:
        src_item = src / item
        dst_item = dst / item
        if dst_item.exists() is False:
            os.makedirs(dst_item)

    for item in non_rfas:
        src_item = src / item
        dst_item = dst / item
        if dst_item.exists():
            if ovr is True:
                print(f'extract: overwrite: {item}')
                shutil.copyfile(src_item, dst_item)
            else:
                print(f'extract: skip: {item}')
        else:
            print(f'extract: copy: {item}')
            shutil.copyfile(src_item, dst_item)

    for item in rfas:
        extract_rfa(src, dst, ovr, item)

def compare_dirs(root, compare, dirs):
    root_path = Path(root)
    dirs_lower = set([x.lower() for x in dirs])
    return [path_join_insensitive(root_path, x) for x in (compare & dirs_lower)]

def pack_mod(src, dst, ovr):
    src_path = Path(src)
    dst_path = Path(dst)
    bf1942_path = src_path / BF1942_DIRECTORY
    levels_path = bf1942_path / LEVELS_DIRECTORY
    
    for root, dirs, files in os.walk(src_path):
        root_path = Path(root)

        if root_path == src_path:
            items = compare_dirs(root_path, TOP_LEVEL_RFAS, dirs)
            for item in items:
                pack_directory(item, dst_path, ovr, root)

        elif root_path == bf1942_path:
            bf1942_dst_path = path_join_insensitive(dst_path, BF1942_DIRECTORY)
            bf1942_dst_path.mkdir(exist_ok=True)

            items = compare_dirs(root_path, BF1942_LEVEL_RFAS, dirs)
            for item in items:
                pack_directory(item, bf1942_dst_path, ovr, bf1942_path)

        elif root_path == levels_path:
            levels_dst_path = path_join_insensitive(dst_path, Path(BF1942_DIRECTORY / LEVELS_DIRECTORY))
            levels_dst_path.mkdir(exist_ok=True)

            for item in dirs:
                pack_directory(item, levels_dst_path, ovr, levels_path)

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
