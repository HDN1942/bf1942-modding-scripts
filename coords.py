#!/usr/bin/env python

import argparse
from bf1942.shell import *

def calc_points(x1, y1, x2, y2):
    x1 = float(x1)
    y1 = float(y1)
    x2 = float(x2)
    y2 = float(y2)
    xx1 = round(x1)
    yy1 = round(y1)
    xx2 = round((x2 - x1) / 2 + x1)
    yy2 = round((y2 - y1) / 2 + y1)
    return xx1, yy1, xx2, yy2

E_MISSING_X2_COORD = 81
E_MISSING_Y2_COORD = 82
E_MISSING_SIZE = 83

parser = argparse.ArgumentParser(description='Calculate strategic area coordinates for either a pair of real map coordinates or a center point and size')
parser.add_argument('mode', choices=['points', 'center'], help='Mode is either points or center')
parser.add_argument('--x1', required=True, help='x1 coordinate for points mode, x coordinate for center mode')
parser.add_argument('--y1', required=True, help='y1 coordinate for points mode, y coordinate for center mode')
parser.add_argument('--x2', help='x2 coordinate for points mode')
parser.add_argument('--y2', help='y2 coordinate for points mode')
parser.add_argument('-s', '--size', help='Size for center mode')
args = parser.parse_args()

if args.mode == 'points' and args.x2 is None:
    eprint(f'--x2 option is required for points mode')
    sys.exit(E_MISSING_X2_COORD)

if args.mode == 'points' and args.y2 is None:
    eprint(f'--y2 option is required for points mode')
    sys.exit(E_MISSING_Y2_COORD)

if args.mode == 'center' and args.size is None:
    eprint(f'--size option is required for center mode')
    sys.exit(E_MISSING_SIZE)

# TODO validate args are within range
# TODO choose mode based on options?

if args.mode == 'points':
    xx1, yy1, xx2, yy2 = calc_points(args.x1, args.y1, args.x2, args.y2)
else:
    x1 = float(args.x1) - float(args.size)
    y1 = float(args.y1) - float(args.size)
    x2 = float(args.x1) + float(args.size)
    y2 = float(args.y1) + float(args.size)
    xx1, yy1, xx2, yy2 = calc_points(x1, y1, x2, y2)

print(f'{xx1}/{yy1} {xx2}/{yy2}')

