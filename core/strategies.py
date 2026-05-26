import os
import threading
from enum import Enum
from PIL import Image

try:
    import oxipng
    HAS_OXIPNG = hasattr(oxipng, "optimize")
except ImportError:
    oxipng = None
    HAS_OXIPNG = False


class Mode(Enum):
    LOSSLESS_PNG = "lossless_png"
    WEBP = "webp"
    JPEG = "jpeg"


class OutputBehavior(Enum):
    INPLACE_NEW_EXT = "inplace_new_ext"
    REPLACE = "replace"
    CUSTOM_FOLDER = "custom_folder"


def _oxipng_available() -> bool:
    return HAS_OXIPNG


class OxiPNGStrategy:
    def __init__(self, speed: int = 3):
        self.speed = speed

    def process(
        self,
        filepath: str,
        output_path: str,
        quality: int,
        cancel_event: threading.Event | None = None,
    ) -> tuple[int, int]:
        if not HAS_OXIPNG:
            raise RuntimeError("oxipng is not installed or available on this system.")
        before = os.path.getsize(filepath)

        # Mapping UI speed (2: Fast, 3: Standard, 9: Max) to pyoxipng level
        level = 6 if self.speed == 9 else self.speed

        try:
            oxipng.optimize(
                filepath,
                output_path,
                level=level,
                strip=oxipng.StripChunks.safe(),
            )
        except Exception as e:
            raise RuntimeError(f"oxipng failed: {e}")

        after = os.path.getsize(output_path)
        return before, after

    def needs_quality(self) -> bool:
        return False

    def output_extension(self) -> str:
        return ".png"

    def accepted_extensions(self) -> set[str]:
        return {".png"}

    def tooltip(self) -> str:
        return (
            "Lossless PNG compression using oxipng.\n"
            "Pixel-identical to the original.\n"
            "Saves 10-40% typically. CPU-intensive on large batches."
        )

    def name(self) -> str:
        return "Lossless (PNG)"

    def speed_name(self) -> str:
        if self.speed == 2:
            return "Fast"
        elif self.speed == 3:
            return "Standard"
        elif self.speed == 9:
            return "Max"
        return str(self.speed)


class WebPStrategy:
    def process(
        self,
        filepath: str,
        output_path: str,
        quality: int,
        cancel_event: threading.Event | None = None,
    ) -> tuple[int, int]:
        before = os.path.getsize(filepath)
        # Use context manager to release file handle immediately, avoiding Windows file locking.
        with Image.open(filepath) as img:
            img.load()  # Force load pixel data to prevent lazy-loading file read/write collision.
            if os.path.abspath(filepath) == os.path.abspath(output_path):
                temp_path = output_path + ".tmp"
                try:
                    img.save(temp_path, "WEBP", quality=quality)
                    os.replace(temp_path, output_path)
                except Exception as e:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    raise e
            else:
                img.save(output_path, "WEBP", quality=quality)
        after = os.path.getsize(output_path)
        return before, after

    def needs_quality(self) -> bool:
        return True

    def output_extension(self) -> str:
        return ".webp"

    def accepted_extensions(self) -> set[str]:
        return {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".tif"}

    def tooltip(self) -> str:
        return (
            "Lossy conversion to WebP format.\n"
            "Excellent compression — 60-80% smaller than PNG.\n"
            "Quality 85 is the recommended sweet spot."
        )

    def name(self) -> str:
        return "Lossy (WebP)"


class JPEGStrategy:
    def process(
        self,
        filepath: str,
        output_path: str,
        quality: int,
        cancel_event: threading.Event | None = None,
    ) -> tuple[int, int]:
        before = os.path.getsize(filepath)
        with Image.open(filepath) as img:
            img.load()
            if img.mode in ("RGBA", "P", "LA"):
                img = img.convert("RGB")
            if os.path.abspath(filepath) == os.path.abspath(output_path):
                temp_path = output_path + ".tmp"
                try:
                    img.save(temp_path, "JPEG", quality=quality)
                    os.replace(temp_path, output_path)
                except Exception as e:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    raise e
            else:
                img.save(output_path, "JPEG", quality=quality)
        after = os.path.getsize(output_path)
        return before, after

    def needs_quality(self) -> bool:
        return True

    def output_extension(self) -> str:
        return ".jpg"

    def accepted_extensions(self) -> set[str]:
        return {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".tif"}

    def tooltip(self) -> str:
        return (
            "Lossy conversion to JPEG format.\n"
            "Widely compatible, best for photos.\n"
            "Not ideal for screenshots or text (banding artifacts).\n"
            "Quality 85 is the recommended sweet spot."
        )

    def name(self) -> str:
        return "Lossy (JPEG)"


def get_strategy(mode: Mode, oxipng_speed: int = 3):
    if mode == Mode.LOSSLESS_PNG:
        return OxiPNGStrategy(speed=oxipng_speed)
    elif mode == Mode.WEBP:
        return WebPStrategy()
    elif mode == Mode.JPEG:
        return JPEGStrategy()
    raise ValueError(f"Unknown mode: {mode}")
