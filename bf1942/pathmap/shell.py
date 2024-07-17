import re
from pathlib import Path

SUPPORTED_FORMATS = ['raw', 'bmp', 'png', 'dds']

def detect_input_format(path):
    '''Detect pathmap input format from path.'''

    path = Path(path)

    # if directory, assume dds
    if path.is_dir():
        return 'dds'

    if path.is_file():
        # if file, detect from suffix
        in_format = path.suffix[1:]
        if in_format in ['raw', 'bmp', 'png']:
            return in_format

    # invalid format
    return None

def detect_output_format(in_format, path):
    '''Detect pathmap output format from input format and path.'''

    # input format must be valid
    assert in_format in SUPPORTED_FORMATS

    path = Path(path)

    if path.is_dir():
        # if directory and input is raw, output is dds, otherwise output is raw
        return 'dds' if in_format == 'raw' else 'raw'

    else:
        # assume path is a file and detect from suffix
        out_format = path.suffix[1:]

        # input format must be raw and only bmp and png make sense as a file output format
        if in_format == 'raw' and out_format in ['bmp', 'png']:
            return out_format

    # invalid format
    return None

class ParsedPathmapFilename:
    '''Contains the result of parsing a pathmap's filename.'''

    PM_KNOWN_MAPS = {
        'Tank': 0,
        'Infantry': 1,
        'Boat': 2,
        'LandingCraft': 3,
        'Car': 4,
        'Amphibius': 4
    }

    PM_BOAT_MAPS = ['Boat', 'LandingCraft']

    def __init__(self, name, index, level):
        self.name = name
        '''Root name of pathmap, ie. Tank, Infantry, Boat.'''

        self.index = None
        '''Pathmap index, should be 0-4'''

        self.level = None
        '''Map level, should be 0-5.'''

        self.is_boat = name in self.PM_BOAT_MAPS
        '''Whether or not this pathmap is a boat pathmap.'''

        if index is None:
            if name in self.PM_KNOWN_MAPS:
                self.index = self.PM_KNOWN_MAPS[name]
            else:
                self.index = 0
        else:
            self.index = int(index)

        if level is None:
            self.level = 2 if self.is_boat else 0
        else:
            self.level = int(level)

PM_STANDARD_FORMAT = re.compile('(.*)(\d)Level(\d)Map')
PM_INFOMAP_FORMAT = re.compile('(.*)Info$')

def parse_pathmap_filename(filename):
    '''Get pathmap name, index, level from filename.'''

    assert filename != ''

    path = Path(filename)

    match = PM_STANDARD_FORMAT.match(path.stem)
    if match is not None:
        return ParsedPathmapFilename(match.group(1), match.group(2), match.group(3))

    match = PM_INFOMAP_FORMAT.match(path.stem)
    if match is not None:
        name = match.group(1)
        return ParsedPathmapFilename(match.group(1), None, None)

    return ParsedPathmapFilename(path.stem, None, None)
