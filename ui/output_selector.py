from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QComboBox, QPushButton, QFileDialog
from core.strategies import OutputBehavior


class OutputSelector(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(QLabel("Output:"))

        OUTPUT_TOOLTIPS = {
            OutputBehavior.INPLACE_NEW_EXT:
                "Keep the original file and create a new file\n"
                "with the new extension next to it.\n"
                "Example: photo.png → photo.webp (both kept)",
            OutputBehavior.REPLACE:
                "Delete the original file after successful conversion.\n"
                "Example: photo.png → photo.webp (original deleted)",
            OutputBehavior.CUSTOM_FOLDER:
                "Write all converted files to a separate output folder,\n"
                "preserving the folder structure. Originals are untouched.",
        }

        self.combo = QComboBox()
        self.combo.addItem("In-place (new extension)", OutputBehavior.INPLACE_NEW_EXT)
        self.combo.addItem("Replace originals", OutputBehavior.REPLACE)
        self.combo.addItem("Custom folder...", OutputBehavior.CUSTOM_FOLDER)
        self.combo.setToolTip(
            "How to handle output files:\n"
            "- In-place: keep original, create new file with new extension\n"
            "- Replace: delete original after successful conversion\n"
            "- Custom folder: write all outputs to a separate directory"
        )
        for behavior, tip in OUTPUT_TOOLTIPS.items():
            idx = self.combo.findData(behavior)
            if idx >= 0:
                self.combo.setItemData(idx, tip, Qt.ToolTipRole)
        self.combo.currentIndexChanged.connect(self._on_combo_change)

        self.folder_btn = QPushButton("Browse...")
        self.folder_btn.setToolTip("Select the output directory.")
        self.folder_btn.hide()
        self.folder_btn.clicked.connect(self._browse_folder)

        self.folder_label = QLabel("")
        self.folder_label.hide()

        layout.addWidget(self.combo)
        layout.addWidget(self.folder_btn)
        layout.addWidget(self.folder_label)
        layout.addStretch()

        self._custom_folder = ""

    def _on_combo_change(self, index):
        is_custom = self.combo.currentData() == OutputBehavior.CUSTOM_FOLDER
        self.folder_btn.setVisible(is_custom)
        self.folder_label.setVisible(is_custom)

    def _browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self._custom_folder = folder
            self.folder_label.setText(folder)

    def selected_behavior(self) -> OutputBehavior:
        return self.combo.currentData()

    def custom_folder(self) -> str:
        return self._custom_folder
