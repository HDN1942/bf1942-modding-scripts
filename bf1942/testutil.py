import hashlib
from pathlib import Path
from bf1942.RFA import RefractorFlatArchive

def create_dummy_directory(test_file):
    file = Path(test_file)
    path = file.parent / f'__{file.stem}__'

    if not path.exists():
        path.mkdir()

    return path

def create_dummy_file(path, contents='foo'):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, 'w') as file:
        print(contents, file=file)
    
    return compute_hash(path)

def create_dummy_rfa(path, name, base=None):
    path = Path(path)
    base = name if base is None else base
    rfa = RefractorFlatArchive(path)
    rfa.addFileAsString(f'{base}/{name}.con', name)
    rfa.write(path / f'{name}.rfa')

def assert_rfa(tc, path, expectedFiles):
    rfa = RefractorFlatArchive(path)

    tc.assertTrue(rfa.success, 'Could not read RFA')
    tc.assertEqual(len(expectedFiles), len(rfa.fileList))
    tc.assertEqual(sorted(expectedFiles), sorted(rfa.getFileList()))

def assert_file_hash(tc, hash, file, has_changed=False):
    actual_hash = compute_hash(file)
    
    if (has_changed):
        tc.assertNotEqual(hash, actual_hash, 'File has not changed')
    else:
        tc.assertEqual(hash, actual_hash, 'File has changed')

def compute_hash(file):
    contents = Path(file).read_bytes()

    sha256 = hashlib.sha256(contents, usedforsecurity=False)
    return sha256.hexdigest()
