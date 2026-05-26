import os
from core.strategies import Mode, get_strategy


def scan_folders(
    folders: list[str], recursive: bool, mode: Mode
) -> list[str]:
    strategy = get_strategy(mode)
    exts = strategy.accepted_extensions()
    files: list[str] = []

    for folder in folders:
        folder = os.path.abspath(folder)
        if os.path.isfile(folder):
            if os.path.splitext(folder)[1].lower() in exts:
                files.append(folder)
            continue

        if not os.path.isdir(folder):
            continue

        if recursive:
            for root, _, filenames in os.walk(folder):
                for fname in filenames:
                    if os.path.splitext(fname)[1].lower() in exts:
                        files.append(os.path.join(root, fname))
        else:
            for fname in os.listdir(folder):
                fpath = os.path.join(folder, fname)
                if os.path.isfile(fpath) and os.path.splitext(fname)[1].lower() in exts:
                    files.append(fpath)

    return sorted(list(set(files)))

