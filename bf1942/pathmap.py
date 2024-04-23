# Much of this is based on genpathmaps by William Murphy <glyph@intergate.com>
#
# genpathmaps is released under GPL v2 or later,
# Copyright 2004 William Murphy
#
# Original source for genpathmaps is available here:
# https://github.com/HDN1942/genpathmaps

from struct import calcsize, unpack
from pathlib import Path

class PathmapHeader:
    HEADER_FORMAT = '=iiiiii'

    def __init__(self, data):
        assert len(data) == 6

        self.ln2TilesPerRow = data[0]
        self.ln2TilesPerCol = data[1]
        self.ln2TileRes = data[2]
        self.compLevel = data[3]
        self.isInfo = data[4]
        self.dataOffset = data[5]

    def is_valid(self):
        return self.ln2TilesPerRow == self.ln2TilesPerCol and \
            self.ln2TilesPerRow <= 8 and \
            self.ln2TileRes >= 6 and \
            self.ln2TileRes <= 12 and \
            (self.isInfo == 0 or self.isInfo == 1) and \
            (self.dataOffset == 0 or self.dataOffset == 2)

    @classmethod
    def from_file(cls, file):
        header_bytes = file.read(calcsize(cls.HEADER_FORMAT))
        header_data = unpack(cls.HEADER_FORMAT, header_bytes)
        return PathmapHeader(header_data)

    # TODO debug friendly str method


def load_pathmap(source_file):
    src_path = Path(source_file)

    assert src_path.is_file()

    with open(src_path, 'rb') as file:
        header = PathmapHeader.from_file(file)

    return header
