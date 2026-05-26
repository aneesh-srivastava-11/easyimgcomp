# easyimgcomp

A cross-platform (Linux, Windows, macOS) desktop GUI utility for batch image compression. Shrink your images fast with a few clicks.

Lossless PNG compression via [oxipng](https://github.com/shssoichiro/oxipng), and lossy WebP/JPEG conversion via Pillow.

## Features

- **Lossless PNG** -- pixel-identical compression using oxipng. Saves 10-40% with zero quality loss.
- **Lossy WebP** -- convert images to WebP. Typically 60-80% smaller than PNG.
- **Lossy JPEG** -- convert images to JPEG. Best for photos.
- **Recursive or Flat scanning** -- scan folder structures recursively or just process files at the top level.
- **Quality Slider** -- control the compression tradeoff for lossy formats (WebP and JPEG).
- **Flexible Output Options** -- keep originals next to new files (with customized suffixes to avoid collisions), replace them in-place, or write to a custom folder (preserving subfolder structure, with robust cross-drive path handling).
- **Drag-and-Drop & Clipboard Paste** -- drag folders or images directly into the window, or use `Ctrl+V` to paste lists of paths (fully supports Windows "Copy as path" quoted format).
- **Parallel Processing** -- multi-threaded execution utilizing all available CPU cores to process files simultaneously.
- **Oxipng Speed Presets** -- choice of Fast, Standard, or Max compression presets depending on speed preference.
- **Optional Dependency Support** -- runs perfectly even if `pyoxipng` is missing. The UI gracefully disables PNG-specific settings while preserving WebP/JPEG encoding capabilities.
- **Real-Time Progress & Statistics** -- detailed progress indicators, live elapsed timer, and a summary table showing exact file counts, bytes saved, and percentages for each target folder.
- **Modern Dark Theme** -- stylized Qt6 interface designed for a sleek and consistent look across all operating systems.
- **Detailed Error reporting** -- comprehensive popup detailing any conversion failures or filesystem access errors for trouble-free debugging.

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
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On Windows Command Prompt (cmd):
venv\Scripts\activate.bat
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

1. Add files/folders (drag-and-drop, Ctrl+V paste, or the **Add Folder** / **Add File** buttons).
2. Pick a mode: Lossless (PNG), Lossy (WebP), or Lossy (JPEG).
3. Set quality (lossy modes only) and output behavior.
4. Click **Run**. Results appear in the table with per-folder stats and total space saved.

## License

MIT

