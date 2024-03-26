from pathlib import Path

def path_join_insensitive(base, path):
    path = Path(path)
    result = Path(base)

    if not result.exists():
        return result / path
        
    for index, part in enumerate(path.parts):
        dirs = [d for d in result.iterdir() if d.is_dir()]

        # exact match
        if part in [d.name for d in dirs]:
            result /= part
            continue

        candidates = [d.name for d in dirs if d.name.lower() == part.lower()]

        if len(candidates) > 0:
            # one or more candidates, pick first
            result /= candidates[0]
        else:
            # no candidates, no point in continuing walk, concat rest and bail
            result /= Path(*path.parts[index:])
            break

    return result

def path_equal_insensitive(path1, path2):
    return str(path1).lower() == str(path2).lower()