import os
import subprocess
import threading
import time
from enum import Enum
from PIL import Image


class Mode(Enum):
    LOSSLESS_PNG = "lossless_png"
    WEBP = "webp"
    JPEG = "jpeg"


class OutputBehavior(Enum):
    INPLACE_NEW_EXT = "inplace_new_ext"
    REPLACE = "replace"
    CUSTOM_FOLDER = "custom_folder"


def _oxipng_available() -> bool:
    try:
        subprocess.run(
            ["oxipng", "--version"],
            capture_output=True,
            check=True,
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


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
        before = os.path.getsize(filepath)
        speed_str = str(self.speed) if self.speed != 9 else "max"
        proc = subprocess.Popen(
            ["oxipng", "-o", speed_str, "--strip", "safe", filepath],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        while proc.poll() is None:
            if cancel_event and cancel_event.is_set():
                proc.kill()
                proc.wait()
                raise RuntimeError("Cancelled")
            time.sleep(0.1)
        if proc.returncode != 0:
            raise RuntimeError(f"oxipng exited with code {proc.returncode}")
        after = os.path.getsize(filepath)
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
        img = Image.open(filepath)
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
        img = Image.open(filepath)
        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")
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
