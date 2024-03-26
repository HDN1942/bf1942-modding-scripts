import os
import sys

# common error return codes
E_DESTINATION_DIRECTORY_NOT_WRITABLE = 81
E_SOURCE_DIRECTORY_NOT_READABLE = 82
E_SOURCE_FILE_NOT_READABLE = 83

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def test_src_dir(src):
    if os.access(src, os.R_OK) is False and os.path.isdir(src):
        eprint(f'Source directory "{src}" does not exist, is not a directory or does not have read permissions')
        sys.exit(E_SOURCE_DIRECTORY_NOT_READABLE)

def test_src_file(src):
    if os.access(src, os.R_OK) is False and os.path.isfile(src):
        eprint(f'Source file "{src}" does not exist, is not a file or does not have read permissions')
        sys.exit(E_SOURCE_FILE_NOT_READABLE)

def test_dst_dir(dst):
    if os.access(dst, os.W_OK) is False and os.path.isdir(dst):
        eprint(f'Destination directory "{dst}" does not exist, is not a directory or does not have write permissions')
        sys.exit(E_DESTINATION_DIRECTORY_NOT_WRITABLE)
