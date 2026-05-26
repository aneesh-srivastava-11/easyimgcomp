import os
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QMessageBox

from core.compressor import CompressionThread, FileResult
from core.strategies import Mode, OutputBehavior
from ui.folder_list import FolderListWidget
from ui.mode_panel import ModePanel
from ui.output_selector import OutputSelector
from ui.results_panel import ResultsPanel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Easy Image Compressor")
        self.setMinimumSize(800, 650)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(12)

        self.folder_list = FolderListWidget()
        self.mode_panel = ModePanel()
        self.output_selector = OutputSelector()
        self.results_panel = ResultsPanel()

        layout.addWidget(self.folder_list)
        layout.addWidget(self.mode_panel)
        layout.addWidget(self.output_selector)
        layout.addStretch()
        layout.addWidget(self.results_panel)

        self.mode_panel.mode_changed.connect(self._on_mode_changed)
        self.results_panel.run_clicked.connect(self.start_compression)
        self.results_panel.cancel_clicked.connect(self.cancel_compression)
        self._thread = None

    def _on_mode_changed(self, mode: Mode):
        self.output_selector.setVisible(True)

    def start_compression(self):
        folders = self.folder_list.folders()
        if not folders:
            QMessageBox.warning(
                self, "No input", "Add at least one folder or file first."
            )
            return

        recursive = self.folder_list.is_recursive()
        mode = self.mode_panel.selected_mode()
        quality = self.mode_panel.quality()
        oxipng_speed = self.mode_panel.oxipng_speed()
        behavior = self.output_selector.selected_behavior()
        custom_folder = self.output_selector.custom_folder()

        if (
            behavior == OutputBehavior.CUSTOM_FOLDER
            and not custom_folder
        ):
            QMessageBox.warning(
                self, "No output folder", "Select an output folder first."
            )
            return

        self.results_panel.show_busy()

        self._thread = CompressionThread(
            folders,
            recursive,
            mode,
            quality,
            behavior,
            custom_folder,
            oxipng_speed,
        )
        self._thread.progress.connect(self.results_panel.set_progress)
        self._thread.file_result.connect(self._on_file_result)
        self._thread.compression_finished.connect(self._on_finished)
        self._thread.cancelled.connect(self._on_cancelled)
        self._thread.start()

        self._results = []

    def cancel_compression(self):
        if self._thread:
            self._thread.cancel()

    def _on_file_result(self, filepath, before, after, success, error):
        self._results.append(
            FileResult(filepath, before, after, success, error)
        )

    def _on_finished(self):
        self.results_panel.show_results(self._results, cancelled=False)
        self.folder_list.clear_all()
        
        failures = [r for r in self._results if not r.success]
        if failures:
            error_details = "\n".join(
                f"• {os.path.basename(r.filepath)}: {r.error}"
                for r in failures[:10]
            )
            if len(failures) > 10:
                error_details += f"\n... and {len(failures) - 10} more files."
            
            QMessageBox.warning(
                self,
                "Compression Warnings",
                f"{len(failures)} file(s) failed to compress:\n\n{error_details}"
            )
            
        self._thread = None

    def _on_cancelled(self):
        self.results_panel.show_results(self._results, cancelled=True)
        self.folder_list.clear_all()
        self._thread = None
