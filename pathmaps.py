#!/usr/bin/env python

import argparse
import logging
import os
import sys
from PIL import Image
from pathlib import Path
from bf1942.shell import *

def convert_image(source_file, destination_file):
    try:
        with Image.open(source_file) as im:
            im.save(destination_file)
    except OSError:
        return False
    return True

E_CONVERSION_ERROR = 100
E_SAME_FORMAT = 101

SUPPORTED_FORMATS = ['raw', 'bmp', 'png']

logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser(description='Convert pathmaps to/from various formats')
parser.add_argument('source_path', help='Source directory containing files in the --in-format format')
parser.add_argument('destination_path', help='Destination directory for converted files')
parser.add_argument('-i', '--in-format', dest='in_format', choices=SUPPORTED_FORMATS, required=True, help='Input format')
parser.add_argument('-o', '--out-format', dest='out_format', choices=SUPPORTED_FORMATS, required=True, help='Output format')
parser.add_argument('--overwrite', action='store_true', default=False, help='Overwrite any existing files in destination path')
args = parser.parse_args()

# TODO add raw conversion support through genpathmaps
if args.out_format not in ['png', 'bmp'] or args.in_format not in ['png', 'bmp']:
    eprint('Script currently only supports converting png to bmp and vice-versa')
    sys.exit(1)

if args.out_format == args.in_format:
    eprint('Output format is the same as input format')
    sys.exit(E_SAME_FORMAT)

test_src_dir(args.source_path)
test_dst_dir(args.destination_path)

source_path = Path(args.source_path)
destination_path = Path(args.destination_path)

for src_item in source_path.iterdir():
    if not src_item.is_file() or src_item.suffix != f'.{args.in_format}':
        continue

    dst_item = destination_path / f'{src_item.stem}.{args.out_format}'

    if dst_item.exists() and args.overwrite is False:
        logger.info(f'pathmap: skip {dst_item.name}')
        continue

    if dst_item.exists():
        logger.info(f'pathmap: overwrite {dst_item.name}')
    else:
        logger.info(f'pathmap: convert {dst_item.name}')

    if convert_image(src_item, dst_item) is False:
        eprint(f'Error converting "{src_item}" to {args.out_format} format')
        sys.exit(E_CONVERSION_ERROR)

sys.exit(0)