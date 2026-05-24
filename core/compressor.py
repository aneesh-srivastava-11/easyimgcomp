import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

from PySide6.QtCore import QThread, Signal

from core.strategies import Mode, OutputBehavior, get_strategy
from core.scanner import scan_folders


@dataclass
class FileResult:
    filepath: str
    before: int
    after: int
    success: bool
    error: str = ""


class CompressionThread(QThread):
    progress = Signal(int, int, str)
    file_result = Signal(str, int, int, bool, str)
    compression_finished = Signal()
    cancelled = Signal()

    def __init__(
        self,
        folders: list[str],
        recursive: bool,
        mode: Mode,
        quality: int,
        output_behavior: OutputBehavior,
        output_dir: str,
        oxipng_speed: int = 3,
    ):
        super().__init__()
        self.folders = folders
        self.recursive = recursive
        self.mode = mode
        self.quality = quality
        self.output_behavior = output_behavior
        self.output_dir = output_dir
        self.oxipng_speed = oxipng_speed
        self._cancel_event = threading.Event()

    def cancel(self):
        self._cancel_event.set()

    def run(self):
        files = scan_folders(self.folders, self.recursive, self.mode)
        total = len(files)
        if total == 0:
            self.compression_finished.emit()
            return

        strategy = get_strategy(self.mode, self.oxipng_speed)

        use_parallel = self.mode != Mode.LOSSLESS_PNG
        max_workers = max(1, os.cpu_count() or 4) if use_parallel else 1

        completed = 0

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}
            for filepath in files:
                if self._cancel_event.is_set():
                    break
                output_path, should_delete = self._resolve_output(filepath, strategy)
                futures[
                    executor.submit(
                        self._process_one,
                        filepath,
                        output_path,
                        strategy,
                        should_delete,
                        self._cancel_event,
                    )
                ] = filepath

            for future in as_completed(futures):
                result = future.result()
                completed += 1
                self.progress.emit(
                    completed, total, os.path.basename(result.filepath)
                )
                self.file_result.emit(
                    result.filepath,
                    result.before,
                    result.after,
                    result.success,
                    result.error,
                )

                if self._cancel_event.is_set():
                    executor.shutdown(wait=False, cancel_futures=True)
                    self.cancelled.emit()
                    return

        self.compression_finished.emit()

    def _resolve_output(self, filepath: str, strategy) -> tuple[str, bool]:
        base, _ = os.path.splitext(filepath)
        ext = strategy.output_extension()

        if self.output_behavior == OutputBehavior.CUSTOM_FOLDER and self.output_dir:
            rel = os.path.relpath(
                filepath,
                os.path.commonpath(self.folders)
                if self.folders
                else os.path.dirname(filepath),
            )
            rel_base, _ = os.path.splitext(rel)
            out = os.path.join(self.output_dir, rel_base + ext)
            os.makedirs(os.path.dirname(out), exist_ok=True)
            return out, False

        out = base + ext
        should_delete = self.output_behavior == OutputBehavior.REPLACE

        if self.output_behavior == OutputBehavior.INPLACE_NEW_EXT and ext != os.path.splitext(filepath)[1]:
            counter = 1
            while os.path.exists(out):
                out = f"{base}_{counter:02d}{ext}"
                counter += 1

        return out, should_delete

    def _process_one(
        self,
        filepath: str,
        output_path: str,
        strategy,
        should_delete: bool,
        cancel_event: threading.Event,
    ) -> FileResult:
        try:
            before, after = strategy.process(
                filepath, output_path, self.quality, cancel_event
            )
            if should_delete and filepath != output_path:
                os.remove(filepath)
            return FileResult(
                filepath=filepath, before=before, after=after, success=True
            )
        except Exception as e:
            return FileResult(
                filepath=filepath, before=0, after=0, success=False, error=str(e)
            )
