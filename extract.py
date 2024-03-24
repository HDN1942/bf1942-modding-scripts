#!/usr/bin/env python

import argparse
import os
import sys
from bf1942.rfa_facade import *
from bf1942.shell import *

E_INVALID_ARCHIVE_OPTION = 100

parser = argparse.ArgumentParser(description='Extract RFAs from a mod')
parser.add_argument('extract', choices=['full', 'levels', 'archive'], help='Specifies which archives to extract, full - extract all RFAs and copy non-RFA files, levels - extract all level RFAs, archive - extract RFA with matching file name within the mod\'s directory tree')
parser.add_argument('mod_path', help='Path to mod in Battlefield 1942 directory, ie. c:\Games\Battlefield 1942\Mods\MyMod')
parser.add_argument('destination_path', help='Destination path for extracted RFA contents')
parser.add_argument('--archive', help='File name of RFA to match when using archive extract choice')
parser.add_argument('--overwrite', action='store_true', default=False, help='Overwrite any existing files in destination path, otherwise files in the mod that match an existing file, or extracted RFA, will be skipped')
args = parser.parse_args()

test_src_dir(args.mod_path)
test_dst_dir(args.destination_path)

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
    mod_levels_path = Path('archives', 'bf1942', 'levels')
    extract_directory(args.mod_path, args.destination_path, args.overwrite, str(mod_levels_path))
else:
    extract_full(args.mod_path, args.destination_path, args.overwrite)

sys.exit(0)
