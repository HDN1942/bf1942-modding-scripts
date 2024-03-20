from pathlib import Path

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