#!/usr/bin/env python

import argparse
import os
import sys
from lib import *

parser = argparse.ArgumentParser(description='Extract RFAs from a mod')
parser.add_argument('extract', choices=['full', 'levels', 'archive'], help='Specifies which archives to extract, full - extract all RFAs and copy non-RFA files, levels - extract all level RFAs, archive - extract RFA with matching file name within the mod\'s directory tree')
parser.add_argument('mod_path', help='Path to mod in Battlefield 1942 directory, ie. c:\Games\Battlefield 1942\Mods\MyMod')
parser.add_argument('destination_path', help='Destination path for extracted RFA contents')
parser.add_argument('--archive', help='File name of RFA to match when using archive extract choice')
parser.add_argument('--overwrite', action='store_true', default=False, help='Overwrite any existing files in destination path, otherwise files in the mod that match an existing file, or extracted RFA, will be skipped')
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
