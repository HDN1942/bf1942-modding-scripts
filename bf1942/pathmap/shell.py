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

    # if file, detect from suffix
    if path.is_file():
        out_format = path.suffix[1:]

        # input format must be raw and only bmp and png make sense as a file output format
        if in_format == 'raw' and out_format in ['bmp', 'png']:
            return out_format

    elif path.is_dir():
        # if directory and input is raw, output is dds, otherwise output is raw
        return 'dds' if in_format == 'raw' else 'raw'

    # invalid format
    return None

