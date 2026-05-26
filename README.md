# easyimgcomp

A Linux GUI utility for batch image compression. Shrink your images fast with a couple clicks.

Lossless PNG compression via [oxipng](https://github.com/shssoichiro/oxipng), and lossy WebP/JPEG conversion via Pillow.

## Features

- **Lossless PNG** -- pixel-identical compression using oxipng. Saves 10-40% with zero quality loss.
- **Lossy WebP** -- convert images to WebP. Typically 60-80% smaller than PNG.
- **Lossy JPEG** -- convert images to JPEG. Best for photos.
- **Recursive or flat** -- process subfolders or just the top level.
- **Quality slider** -- control the compression tradeoff. Defaults to 85.
- **Output options** -- keep originals next to new files, replace them, or write to a custom folder.
- **Drag-and-drop** -- just drag folders in, no file dialogs needed.
- **Parallel processing** -- multiple files handled at once (where it makes sense).

## Screenshots
![Showcase](showcase1.avif)


## Install

### Arch Linux (AUR)

```bash
yay -S easyimgcomp-git
```

### From source

```bash
git clone https://github.com/YOUR_USERNAME/easyimgcomp
cd easyimgcomp

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Run the app
python main.py
```

## Requirements

| Dependency | Purpose |
|-----------|---------|
| Python 3.9+ | Runtime |
| PySide6 | GUI framework (Qt 6) |
| Pillow | WebP and JPEG encoding |
| pyoxipng | Lossless PNG compression (Rust oxipng Python bindings) |

## Usage

1. Add folders (drag-and-drop, Ctrl+V paste, or the Add button).
2. Pick a mode: Lossless (PNG), Lossy (WebP), or Lossy (JPEG).
3. Set quality (lossy modes only) and output behavior.
4. Click Run. Results appear in the table with per-folder stats and total space saved.

## License

MIT
