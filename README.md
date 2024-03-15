# Battlefield 1942 Modding Scripts

A set of Python 3 scripts to aid in Battlefield 1942 modding.

## Prerequisites

```bash
sudo apt-get install liblzo2-dev

pip install -r requirements.txt
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

## License

Code is released under GPL-3.0 license, except for RFA.py which has no specific license.

## Credits

Ahrkylien for RFA.py - https://github.com/Ahrkylien/BF1942-Extraction-Readout-Scripts
