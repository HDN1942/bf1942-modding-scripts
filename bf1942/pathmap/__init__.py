# Much of this module is based on genpathmaps by William Murphy <glyph@intergate.com>
#
# genpathmaps is released under GPL v2 or later,
# Copyright 2004 William Murphy
#
# Original source for genpathmaps is available here:
# https://github.com/HDN1942/genpathmaps

from .pathmap import *
from .smallones import *
from .conversion import convert_pathmap, pathmap_from_image, image_from_pathmap, image_from_textures, textures_from_image, generate_pathmap_files
from .shell import detect_input_format, detect_output_format
