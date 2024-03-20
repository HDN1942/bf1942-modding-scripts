#!/usr/bin/env python

import argparse
import os
import sys
from bf1942.rfa import *
from bf1942.shell import *

E_INVALID_BASE_PATH = 100

parser = argparse.ArgumentParser(description='Pack one or more directories into RFA archives')
parser.add_argument('source_path', help='Source path to pack')
parser.add_argument('destination_path', help='Destination path for packed RFAs')
parser.add_argument('-b', '--base-path', dest='base_path', help='Base path for RFA directory structure, ignored when --mod option is used')
parser.add_argument('-m', '--mod', action='store_true', default=False, help='source_path is an extracted mod with the standard directory structure, all detected RFAs will be packed')
parser.add_argument('-o', '--overwrite', action='store_true', default=False, help='Overwrite any existing files in destination path, otherwise RFAs existing in the destination will be skipped')
args = parser.parse_args()

test_src_dir(args.source_path)
test_dst_dir(args.destination_path)

# if base path is set, check it is relative to source_path
if args.mod is None and args.base_path is not None and args.source_path.startswith(args.base_path) is False:
    eprint(f'Base path "{args.base_path}" must be relative to source directory "{args.source_path}"')
    sys.exit(E_INVALID_BASE_PATH)

if args.mod:
    pack_mod(args.source_path, args.destination_path, args.overwrite)
else:
    pack_directory(args.source_path, args.destination_path, args.overwrite, args.base_path)

sys.exit(0)
