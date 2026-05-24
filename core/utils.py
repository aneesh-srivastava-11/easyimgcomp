import os


def format_bytes(n: int) -> str:
    if n == 0:
        return "0 B"
    units = ("B", "KB", "MB", "GB", "TB")
    i = 0
    f = float(n)
    while abs(f) >= 1024 and i < len(units) - 1:
        f /= 1024
        i += 1
    return f"{f:.1f} {units[i]}"


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)
