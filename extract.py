#!/usr/bin/env python

import argparse
import logging
import os
import sys
from bf1942.path import path_join_insensitive
from bf1942.rfautil import *
from bf1942.shell import *

E_INVALID_ARCHIVE_OPTION = 100

logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser(description='Extract RFAs from a mod')
parser.add_argument('source_path', help='Path to RFA file to extract or path to mod in Battlefield 1942 directory (ie. "c:\Games\Battlefield 1942\Mods\MyMod") if either --levels or --mod option is specified')
parser.add_argument('destination_path', help='Destination path for extracted RFA(s)')
parser.add_argument('-l', '--levels', action='store_true', default=False, help='Extract all level RFAs in mod')
parser.add_argument('-m', '--mod', action='store_true', default=False, help='Extract all RFAs in mod')
parser.add_argument('--overwrite', action='store_true', default=False, help='Overwrite existing directory in destination path, otherwise RFA extraction will be skipped')
args = parser.parse_args()

test_dst_dir(args.destination_path)

if args.levels:
    levels_path = path_join_insensitive(args.source_path, Path(ARCHIVES_DIRECTORY, BF1942_DIRECTORY, LEVELS_DIRECTORY))
    test_src_dir(levels_path)
    extract_directory(levels_path, args.destination_path, args.overwrite)
elif args.mod:
    mod_path = path_join_insensitive(args.source_path, ARCHIVES_DIRECTORY)
    test_src_dir(mod_path)
    extract_mod(mod_path, args.destination_path, args.overwrite)
else:
    test_src_file(args.source_path)
    extract_rfa(args.source_path, args.destination_path, args.overwrite)

sys.exit(0)
