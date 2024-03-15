#!/usr/bin/env python

import argparse
import os
import shutil
import sys
from pathlib import Path
from RFA import RefractorFlatArchive

E_MOD_DIRECTORY_NOT_READABLE = 81
E_MOD_LEVELS_DIRECTORY_NOT_READABLE = 82
E_DESTINATION_DIRECTORY_NOT_WRITABLE = 83
E_INVALID_ARCHIVE_OPTION = 84

LEVELS_SUB_PATH = 'Archives/bf1942/levels'

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def get_path_nocase(root, path):
    # TODO implement me!
    # for each path starting from mod root
    #   get directories under path
    #   for each directory
    #     lower case basename and compare against each lower case expected path part
    f'{root}/{path}'

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
        print(f'RFA: Skip: {item}')
        return
    
    if dst_item.exists():
        shutil.rmtree(dst_item)
        print(f'RFA: Overwrite: {item}')
    else:
        print(f'RFA: Extract: {item}')
   
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
            print(f'Directory: Create: {item}')
            os.makedirs(dst_item)
        else:
            print(f'Directory: Skip: {item}')

    for item in non_rfas:
        src_item = src / item
        dst_item = dst / item
        if dst_item.exists():
            if ovr is True:
                print(f'File: Overwrite: {item}')
                shutil.copyfile(src_item, dst_item)
            else:
                print(f'File: Skip: {item}')
        else:
            print(f'File: Copy: {item}')
            shutil.copyfile(src_item, dst_item)

    for item in rfas:
        extract_rfa(src, dst, ovr, item)

parser = argparse.ArgumentParser(description='Extract RFAs from a mod')
parser.add_argument('extract', choices=['full', 'levels', 'archive'], help='Specifies which archives to extract, full - extract all RFAs and copy non-RFA files, levels - extract all level RFAs, match - extract RFA with matching file name within the mod\'s directory tree')
parser.add_argument('mod_path', help='Path to mod in Battlefield 1942 directory, ie. c:\Games\Battlefield 1942\Mods\MyMod')
parser.add_argument('destination_path', help='Destination path for extracted RFA contents')
parser.add_argument('--archive', help='File name of RFA to match when using archive extract choice')
parser.add_argument('--overwrite', action='store_true', default=False, help='Overwrite any existing files in destination path, otherwise files in the RFA that match an existing file will be skipped')
args = parser.parse_args()

if os.access(args.mod_path, os.R_OK) is False:
    eprint(f'Mod directory "{args.mod_path}" does not exist or does not have read permissions')
    sys.exit(E_MOD_DIRECTORY_NOT_READABLE)

if os.access(args.destination_path, os.W_OK) is False:
    eprint(f'Destination directory "{args.destination_path}" does not exist or does not have write permissions')
    sys.exit(E_DESTINATION_DIRECTORY_NOT_WRITABLE)

if args.extract == 'archive':
    if args.archive is None:
        eprint('The --archive option must be specified when extract parameter is archive')
        sys.exit(E_INVALID_ARCHIVE_OPTION)
else:
    if args.archive is not None:
        eprint('The --archive option can only be specified when extract parameter is archive')
        sys.exit(E_INVALID_ARCHIVE_OPTION)

if args.extract == 'archive':
    extract_archive(args.mod_path, args.destination_path, args.overwrite, args.archive)
elif args.extract == 'levels':
    mod_levels_path = get_path_nocase(args.mod_path, LEVELS_SUB_PATH)
    if os.access(args.mod_path, os.R_OK) is False:
        eprint(f'Mod levels directory "{mod_levels_path}" does not exist or does not have read permissions')
        sys.exit(E_MOD_LEVELS_DIRECTORY_NOT_READABLE)

    extract_directory(args.mod_path, args.destination_path, args.overwrite, LEVELS_SUB_PATH)
else:
    extract_full(args.mod_path, args.destination_path, args.overwrite)

sys.exit(0)
