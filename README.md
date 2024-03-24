# Battlefield 1942 Modding Scripts

A set of Python 3 scripts to aid in Battlefield 1942 modding.

## Prerequisites

#### Debian Linux
```bash
sudo apt-get install liblzo2-dev
pip install -r rquirements.txt
```

#### MacOS
```bash
brew install python3 lzo pillow
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```

## Usage

#### Extract archives from mod directory

```bash
python3 extract.py [-h] [--archive ARCHIVE] [--overwrite] {full,levels,archive} mod_path destination_path
```

Extract choices:
* `full` - copy all mod content and extract all RFAs to target directory
* `levels` - extract all levels
* `archive` - extract a specific RFA with (partially) matching name, can be anywhere within the mod's directory tree

Options:
* `--archive` - RFA file name to match when using archive extract choice
* `--overwrite` - overwrite any existing files in destination path, otherwise files in the RFA that match an existing file will be skipped

#### Pack one or more directories into RFA archives

```bash
python3 pack.py [-h] [--base-path] [--mod] [--overwrite] source_path destination_path
```

Positional arguments:
* `source_path` - Source path to pack
* `destination_path` - Destination path for packed RFAs

Options:
* `-b`, `--base-path` - Base path for RFA directory structure, ignored when `--mod` option is used
* `-m`, `--mod` - `source_path` is an extracted mod with the standard directory structure, all detected RFAs will be packed
* `-o`, `--overwrite` - Overwrite any existing files in destination path, otherwise RFAs existing in the destination will be skipped

`source_path` is assumed to be a single directory to pack unless the `--mod` option is specified, in which case each detected RFA will be packed.

The standard mod directory structure is:

```bash
ai
aimeshes
animations
bf1942/
    game
    levels/*
font
menu
objects
shaders
sound
standardmesh
texture
treemesh
```

#### Convert pathmaps to/from various formats

```bash
python3 pathmaps.py [-h] [--in-format FORMAT] [--out-format FORMAT] [--overwrite] source_path destination_path
```

Supported formats:
* `raw` - Native Battlefield 1942 pathmap format (NOTE: not yet supported, use `genpathmaps` instead)
* `bmp` - Uncompressed bitmap format
* `png` - Portable Network Graphics format with lossless compression

Positional arguments:
* `source_path` - Source directory containing files in the `--in-format` format
* `destination_path` - Destination directory for converted files

#### Calculate strategic area coordinates from map coordinates

```bash
python3 pathmaps.py [-h] --x1 --y1 [--x2] [--y2] [--size] {points,center}
```

Modes:
* `points` - Calculate strategic area coordinates for a pair of map coordinates, requires `--x1`, `--y1`, `--x2` and `--y2` options
* `center` - Calculate strategic area coordinates from a center point and size, requires `--x1`, `--y1` and `--size` options

## Development

#### Run tests

```bash
python3 -m unittest -b
```

## License

Released under GPL-3.0 license unless specified otherwise in source file. 

## Credits

Ahrkylien for RFA.py - https://github.com/Ahrkylien/BF1942-Extraction-Readout-Scripts
