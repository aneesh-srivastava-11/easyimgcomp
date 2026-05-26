import os
import time
from collections import defaultdict

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QProgressBar,
    QLabel,
)
from PySide6.QtCore import Signal, QTimer

from core.utils import format_bytes


def _elapsed_str(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


class ResultsPanel(QWidget):
    run_clicked = Signal()
    cancel_clicked = Signal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        btn_row = QHBoxLayout()
        self.run_btn = QPushButton("Run")
        self.run_btn.setToolTip(
            "Start compressing all files in the selected folders."
        )
        self.run_btn.clicked.connect(self.run_clicked)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setToolTip("Stop after the current file finishes.")
        self.cancel_btn.clicked.connect(self._on_cancel_clicked)
        self.cancel_btn.hide()

        btn_row.addWidget(self.run_btn)
        btn_row.addWidget(self.cancel_btn)
        btn_row.addStretch()

        self.elapsed_label = QLabel("")
        self.elapsed_label.hide()
        btn_row.addWidget(self.elapsed_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        self.progress_label = QLabel("")
        self.progress_label.hide()

        progress_row = QHBoxLayout()
        progress_row.addWidget(self.progress_bar, 1)
        progress_row.addWidget(self.progress_label)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["Folder", "Files", "Before", "After", "Saved"]
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.hide()

        layout.addLayout(btn_row)
        layout.addLayout(progress_row)
        layout.addWidget(self.table, 1)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._start_time: float = 0

    def _tick(self):
        elapsed = time.monotonic() - self._start_time
        self.elapsed_label.setText(f"Elapsed: {_elapsed_str(elapsed)}")

    def _on_cancel_clicked(self):
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.setText("Cancelling...")
        self.cancel_clicked.emit()

    def set_progress(self, current: int, total: int, filename: str):
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        elapsed = time.monotonic() - self._start_time
        self.progress_label.setText(
            f"{current}/{total}  —  {filename}  —  {_elapsed_str(elapsed)}"
        )
        self._tick()

    def show_busy(self):
        self.run_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.cancel_btn.setText("Cancel")
        self.cancel_btn.show()
        self.progress_bar.show()
        self.progress_label.show()
        self.elapsed_label.hide()
        self._start_time = time.monotonic()
        self._timer.start(1000)

    def show_idle(self):
        self.run_btn.setEnabled(True)
        self.cancel_btn.hide()
        self.cancel_btn.setEnabled(True)
        self.cancel_btn.setText("Cancel")
        self.progress_bar.hide()
        self.progress_label.hide()
        self._timer.stop()

    def show_results(self, results: list, cancelled: bool = False):
        self._timer.stop()
        elapsed = time.monotonic() - self._start_time

        if cancelled:
            prefix = "Cancelled after "
        else:
            prefix = "Completed in "
        self.elapsed_label.setText(prefix + _elapsed_str(elapsed))
        self.elapsed_label.show()

        folders: dict[str, dict] = defaultdict(
            lambda: {"files": 0, "before": 0, "after": 0, "success": 0}
        )

        total_before = 0
        total_after = 0
        total_success = 0

        for r in results:
            folder = os.path.dirname(r.filepath)
            folders[folder]["files"] += 1
            if r.success:
                folders[folder]["before"] += r.before
                folders[folder]["after"] += r.after
                folders[folder]["success"] += 1
                total_before += r.before
                total_after += r.after
                total_success += 1

        n = len(folders)
        self.table.setRowCount(n + 1)

        for i, (folder, data) in enumerate(sorted(folders.items())):
            saved_pct = (
                (data["before"] - data["after"]) / data["before"] * 100
                if data["before"] > 0
                else 0
            )
            self.table.setItem(
                i, 0, QTableWidgetItem(os.path.basename(folder) or folder)
            )
            self.table.setItem(i, 1, QTableWidgetItem(str(data["success"])))
            self.table.setItem(i, 2, QTableWidgetItem(format_bytes(data["before"])))
            self.table.setItem(i, 3, QTableWidgetItem(format_bytes(data["after"])))
            self.table.setItem(i, 4, QTableWidgetItem(f"{saved_pct:.1f}%"))

        total_pct = (
            (total_before - total_after) / total_before * 100
            if total_before > 0
            else 0
        )
        self.table.setItem(n, 0, QTableWidgetItem("TOTAL"))
        self.table.setItem(n, 1, QTableWidgetItem(str(total_success)))
        self.table.setItem(n, 2, QTableWidgetItem(format_bytes(total_before)))
        self.table.setItem(n, 3, QTableWidgetItem(format_bytes(total_after)))
        self.table.setItem(n, 4, QTableWidgetItem(f"{total_pct:.1f}%"))

        self.table.show()
        self.show_idle()
