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
python3 -m extract [-h]  [--levels] [--mod] [--overwrite] source_path destination_path
```

Positional arguments:
* `source_path`

  Path to RFA file to extract or path to mod in Battlefield 1942 directory (ie. `"c:\Games\Battlefield 1942\Mods\MyMod"`) if either `--levels` or `--mod` option is specified

* `destination_path`

  Destination path for extracted RFA(s)

Options:
* `-l`, `--levels`

  Extract all level RFAs in mod

* `-m`, `--mod`

  Extract all RFAs in mod

* `--overwrite`

  Overwrite existing directory in destination path, otherwise RFA extraction will be skipped

#### Pack one or more directories into RFA archives

```bash
python3 -m pack [-h] [--base-path] [--mod] [--overwrite] source_path destination_path
```

Positional arguments:
* `source_path`

  Source path to pack, assumed to be a single directory to pack unless the `--mod` option is specified, in which case each detected RFA will be packed

* `destination_path`

  Destination path for packed RFA(s). RFA file name will match final part of `source_path` if `destination_path` is a directory instead of a path to an RFA file.

Options:
* `-b`, `--base-path`

  Base path for RFA directory structure, default is parent of `source_path`, ignored when `--mod` option is used

* `-m`, `--mod`

  `source_path` is an extracted mod with the standard directory structure, all detected RFAs will be packed

* `-o`, `--overwrite`

  Overwrite any existing files in destination path, otherwise RFAs existing in the destination will be skipped

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
python3 -m pathmaps [-h] [--in-format FORMAT] [--out-format FORMAT] [--overwrite] source_path destination_path
```

Supported formats:
* `raw`

  Native Battlefield 1942 pathmap format (NOTE: not yet supported, use `genpathmaps` instead)

* `bmp`

  Uncompressed bitmap format

* `png`

   Portable Network Graphics format with lossless compression

Positional arguments:
* `source_path`

  Source directory containing files in the `--in-format` format

* `destination_path`

  Destination directory for converted files

Options:
* `-i`, `--in-format`

  Required, the input format

* `-o`, `--out-format`

  Required, the output format

* `--overwrite`

  Overwrite any existing files in destination path

#### Calculate strategic area coordinates from map coordinates

```bash
python3 -m coords [-h] --x1 --y1 [--x2] [--y2] [--size] {points,center}
```

Modes:
* `points`

  Calculate strategic area coordinates for a pair of map coordinates, requires `--x1`, `--y1`, `--x2` and `--y2` options

* `center`

  Calculate strategic area coordinates from a center point and size, requires `--x1`, `--y1` and `--size` options

## Development

#### Run tests

```bash
python3 -m unittest -b
```

## License

Released under GPL-3.0 license unless specified otherwise in source file.

## Credits

Ahrkylien for RFA.py - https://github.com/Ahrkylien/BF1942-Extraction-Readout-Scripts
