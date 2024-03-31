#!/usr/bin/env python

import argparse
import os
import sys
from pathlib import Path
from bf1942.shell import *
from bf1942.pathmap import convert_pathmap

E_CONVERSION_ERROR = 100
E_SAME_FORMAT = 101

SUPPORTED_FORMATS = ['raw', 'bmp', 'png']

parser = argparse.ArgumentParser(description='Convert pathmaps to/from various formats')
parser.add_argument('source_path', help='Source directory containing files in the --in-format format')
parser.add_argument('destination_path', help='Destination directory for converted files')
parser.add_argument('-i', '--in-format', dest='in_format', choices=SUPPORTED_FORMATS, required=True, help='Input format')
parser.add_argument('-o', '--out-format', dest='out_format', choices=SUPPORTED_FORMATS, required=True, help='Output format')
parser.add_argument('--overwrite', action='store_true', default=False, help='Overwrite any existing files in destination path')
args = parser.parse_args()

if args.out_format == args.in_format:
    eprint('Output format is the same as input format')
    sys.exit(E_SAME_FORMAT)

test_src_dir(args.source_path)
test_dst_dir(args.destination_path)

if convert_pathmap(args.source_path, args.destination_path, args.in_format, args.out_format, args.overwrite) is False:
    eprint(f'Error converting to {args.out_format} format')
    sys.exit(E_CONVERSION_ERROR)

sys.exit(0)