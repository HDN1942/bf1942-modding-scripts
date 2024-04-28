import inspect
import shutil
from pathlib import Path

def create_dummy_file(path, contents='foo'):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, 'w') as file:
        print(contents, file=file)

def create_dummy_child_files(parent, name, value):
    path = parent / name

    if isinstance(value, dict):
        if path.exists() and not path.is_dir():
            path.unlink()

        # create directory and descend
        path.mkdir(exist_ok=True)

        for key in value:
            create_dummy_child_files(path, key, value[key])
    else:
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()

        # create a dummy file
        if value is None:
            value = f'{name} dummy file'

        with open(path, 'w') as file:
            print(value, file=file)

def create_dummy_files(struc):
    file = Path(inspect.stack()[1].filename)
    root = file.parent / f'__{file.stem}__'

    root.mkdir(exist_ok=True)

    for key in struc:
        create_dummy_child_files(root, key, struc[key])

    return root

def remove_dummy_files(tc):
    if hasattr(tc, 'root') and tc.root is not None:
        shutil.rmtree(tc.root)
    tc.root = None
