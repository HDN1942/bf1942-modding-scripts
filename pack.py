#!/usr/bin/env python

import argparse
import os
import sys
from lib import *

parser = argparse.ArgumentParser(description='Pack extracted RFAs from a mod')
parser.add_argument('pack', choices=['full', 'levels', 'archive'], help='Specifies which archives to pack, full - pack all RFAs and copy non-RFA files, levels - pack all level RFAs, archive - pack RFA with matching file name within the extracted mod\'s directory tree')
parser.add_argument('mod_path', help='Path to extracted mod')
parser.add_argument('destination_path', help='Destination path for packed mod contents')
parser.add_argument('--archive', help='File name of RFA to match when using archive pack choice')
parser.add_argument('--overwrite', action='store_true', default=False, help='Overwrite any existing files in destination path, otherwise mod files that match an existing file in the destination will be skipped')
args = parser.parse_args()

if os.access(args.mod_path, os.R_OK) is False:
    eprint(f'Mod directory "{args.mod_path}" does not exist or does not have read permissions')
    sys.exit(E_MOD_DIRECTORY_NOT_READABLE)

if os.access(args.destination_path, os.W_OK) is False:
    eprint(f'Destination directory "{args.destination_path}" does not exist or does not have write permissions')
    sys.exit(E_DESTINATION_DIRECTORY_NOT_WRITABLE)

if args.extract == 'archive':
    if args.archive is None:
        eprint('The --archive option must be specified when pack parameter is archive')
        sys.exit(E_INVALID_ARCHIVE_OPTION)
else:
    if args.archive is not None:
        eprint('The --archive option can only be specified when pack parameter is archive')
        sys.exit(E_INVALID_ARCHIVE_OPTION)

if args.extract == 'archive':
    pack_archive(args.mod_path, args.destination_path, args.overwrite, args.archive)
elif args.extract == 'levels':
    mod_levels_path = get_path_nocase(args.mod_path, LEVELS_SUB_PATH)
    if os.access(args.mod_path, os.R_OK) is False:
        eprint(f'Mod levels directory "{mod_levels_path}" does not exist or does not have read permissions')
        sys.exit(E_MOD_LEVELS_DIRECTORY_NOT_READABLE)

    pack_directory(args.mod_path, args.destination_path, args.overwrite, LEVELS_SUB_PATH)
else:
    pack_full(args.mod_path, args.destination_path, args.overwrite)

sys.exit(0)
