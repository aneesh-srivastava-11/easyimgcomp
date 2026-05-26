import os
from urllib.parse import urlparse, unquote
from urllib.request import url2pathname

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QListWidget,
    QFileDialog,
    QCheckBox,
    QLabel,
    QApplication,
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QKeySequence


def _parse_paths(text: str) -> list[str]:
    paths = []
    if not text:
        return paths
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        # Strip leading/trailing double or single quotes (common in "Copy as path")
        if (line.startswith('"') and line.endswith('"')) or (line.startswith("'") and line.endswith("'")):
            line = line[1:-1].strip()
        if not line:
            continue
        if line.startswith("file://"):
            parsed = urlparse(line)
            line = url2pathname(parsed.path)
        if os.path.isdir(line) or os.path.isfile(line):
            paths.append(line)
    return paths


class DropListWidget(QListWidget):
    folder_dropped = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragDropMode(QListWidget.InternalMove)
        self.setToolTip(
            "Add folders containing images, or individual images to compress.\n"
            "You can also drag and drop folders/files from your file manager."
        )

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        elif event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if os.path.isdir(path) or os.path.isfile(path):
                    self.folder_dropped.emit(path)
        elif event.mimeData().hasText():
            for path in _parse_paths(event.mimeData().text()):
                self.folder_dropped.emit(path)
        event.acceptProposedAction()

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.Paste):
            for path in _parse_paths(QApplication.clipboard().text()):
                self.folder_dropped.emit(path)
        else:
            super().keyPressEvent(event)


class FolderListWidget(QWidget):
    folders_changed = Signal(list)

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        label_layout = QHBoxLayout()
        title = QPushButton("Folders/Files to process")
        title.setFlat(True)
        title.setEnabled(False)
        label_layout.addWidget(title)
        label_layout.addStretch()

        self.list_widget = DropListWidget()
        self.list_widget.folder_dropped.connect(self._on_folder_dropped)

        self.hint_label = QLabel("Drop folders/images here or Ctrl+V to paste paths")
        self.hint_label.setAlignment(Qt.AlignCenter)
        self.hint_label.setStyleSheet("color: #666; padding: 12px;")
        self.hint_label.setWordWrap(True)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add Folder")
        self.add_btn.setToolTip("Open a file picker to select a folder.")
        self.add_btn.clicked.connect(self.add_folder)

        self.add_file_btn = QPushButton("Add File")
        self.add_file_btn.setToolTip("Open a file picker to select individual images.")
        self.add_file_btn.clicked.connect(self.add_file)

        self.remove_btn = QPushButton("Remove Selected")
        self.remove_btn.setToolTip(
            "Remove the currently selected folder/file from the list."
        )
        self.remove_btn.clicked.connect(self.remove_selected)

        self.recursive_cb = QCheckBox("Recursive")
        self.recursive_cb.setChecked(True)
        self.recursive_cb.setToolTip(
            "Scan all subdirectories inside each folder.\n"
            "Uncheck to only process files directly inside the selected folders."
        )

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.add_file_btn)
        btn_layout.addWidget(self.remove_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.recursive_cb)

        layout.addLayout(label_layout)
        layout.addWidget(self.list_widget)
        layout.addWidget(self.hint_label)
        layout.addLayout(btn_layout)

        self._update_hint()

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls() or event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if os.path.isdir(path) or os.path.isfile(path):
                    self._on_folder_dropped(path)
        elif event.mimeData().hasText():
            for path in _parse_paths(event.mimeData().text()):
                self._on_folder_dropped(path)
        event.acceptProposedAction()

    def _update_hint(self):
        empty = self.list_widget.count() == 0
        self.hint_label.setVisible(empty)
        self.list_widget.setVisible(not empty)

    def _on_folder_dropped(self, path: str):
        for i in range(self.list_widget.count()):
            if self.list_widget.item(i).text() == path:
                return
        self.list_widget.addItem(path)
        self._update_hint()
        self.folders_changed.emit(self.folders())

    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if not folder:
            return
        for i in range(self.list_widget.count()):
            if self.list_widget.item(i).text() == folder:
                return
        self.list_widget.addItem(folder)
        self._update_hint()
        self.folders_changed.emit(self.folders())

    def add_file(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Images",
            "",
            "Images (*.png *.jpg *.jpeg *.webp *.bmp *.tiff *.tif);;All Files (*)"
        )
        if not files:
            return
        for file in files:
            self._on_folder_dropped(file)

    def remove_selected(self):
        for item in self.list_widget.selectedItems():
            self.list_widget.takeItem(self.list_widget.row(item))
        self._update_hint()
        self.folders_changed.emit(self.folders())

    def clear_all(self):
        self.list_widget.clear()
        self._update_hint()
        self.folders_changed.emit(self.folders())

    def folders(self) -> list[str]:
        return [
            self.list_widget.item(i).text()
            for i in range(self.list_widget.count())
        ]

    def is_recursive(self) -> bool:
        return self.recursive_cb.isChecked()
