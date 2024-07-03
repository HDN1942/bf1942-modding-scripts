#!/usr/bin/env python

import argparse
import logging
import sys
from bf1942.pathmap import detect_input_format, detect_output_format, convert_pathmap
from bf1942.shell import *

E_CONVERSION_ERROR = 100
E_INVALID_FORMAT = 101

logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser(description='Convert pathmaps to/from various formats')
parser.add_argument('source_path', help='Source path of file, or path to directory containing files to be converted')
parser.add_argument('destination_path', help='Destination path of file or directory for converted file(s)')
args = parser.parse_args()

in_format = detect_input_format(args.source_path)
if not in_format:
    eprint(f'Invalid input format')
    sys.exit(E_INVALID_FORMAT)

out_format = detect_output_format(in_format, args.destination_path)
if not out_format:
    eprint(f'Invalid output format')
    sys.exit(E_INVALID_FORMAT)

if not convert_pathmap(args.source_path, args.destination_path, in_format, out_format):
    sys.exit(E_CONVERSION_ERROR)

sys.exit(0)