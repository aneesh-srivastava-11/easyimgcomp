from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QRadioButton,
    QSlider,
    QLabel,
    QButtonGroup,
    QComboBox,
)
from PySide6.QtCore import Qt, Signal

from core.strategies import Mode, get_strategy, _oxipng_available


OXIPNG_SPEEDS = {
    2: "Fast (-o 2)",
    3: "Standard (-o 3)",
    9: "Max (-o max)",
}

OXIPNG_SPEED_TOOLTIPS = {
    2: (
        "Fast — limited compression trials.\n"
        "Quick, reasonable size reduction.\n"
        "Good for batch processing."
    ),
    3: (
        "Standard — oxipng default.\n"
        "Balanced speed and compression.\n"
        "Recommended for most users."
    ),
    9: (
        "Max — exhaustive compression trials.\n"
        "Best compression ratio, but VERY slow.\n"
        "⚠ High CPU usage per file. Use for archival."
    ),
}


class ModePanel(QWidget):
    mode_changed = Signal(Mode)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        header = QLabel("Compression mode")
        layout.addWidget(header)

        mode_row = QHBoxLayout()
        self.mode_group = QButtonGroup(self)

        entries = [
            ("Lossless (PNG)", Mode.LOSSLESS_PNG),
            ("Lossy (WebP)", Mode.WEBP),
            ("Lossy (JPEG)", Mode.JPEG),
        ]

        oxipng_avail = _oxipng_available()

        self._mode_widgets = {}
        for label, mode in entries:
            rb = QRadioButton(label)
            if mode == Mode.LOSSLESS_PNG and not oxipng_avail:
                rb.setEnabled(False)
                rb.setToolTip("Lossless PNG compression is unavailable because 'pyoxipng' is not installed.")
            else:
                rb.setToolTip(get_strategy(mode).tooltip())
            self.mode_group.addButton(rb)
            mode_row.addWidget(rb)
            self._mode_widgets[mode] = rb

        self._mode_widgets[Mode.WEBP].setChecked(True)
        mode_row.addStretch()

        self.png_notice = QLabel("Only affects .png files — others are skipped.")
        self.png_notice.setStyleSheet("color: #888; font-style: italic;")
        self.png_notice.hide()
        mode_row.addWidget(self.png_notice)

        self.mode_group.buttonToggled.connect(self._on_mode_toggled)
        layout.addLayout(mode_row)

        quality_row = QHBoxLayout()
        quality_row.addWidget(QLabel("Quality:"))
        self.quality_slider = QSlider(Qt.Horizontal)
        self.quality_slider.setRange(1, 100)
        self.quality_slider.setValue(85)
        self.quality_slider.setToolTip(
            "Higher = better quality, larger files.\n"
            "Lower = smaller files but visible artifacts.\n"
            "85 is the recommended default."
        )
        self.quality_label = QLabel("85%")
        quality_row.addWidget(self.quality_slider)
        quality_row.addWidget(self.quality_label)
        self.default_label = QLabel("Default: 85")
        self.default_label.setStyleSheet("color: #888; font-style: italic;")
        self.default_label.hide()
        quality_row.addWidget(self.default_label)
        quality_row.addStretch()
        layout.addLayout(quality_row)

        self.quality_slider.valueChanged.connect(self._on_quality_changed)

        speed_row = QHBoxLayout()
        speed_row.addWidget(QLabel("Speed:"))
        self.speed_combo = QComboBox()
        self.speed_combo.setToolTip(
            "Oxipng compression effort level.\n"
            "Fast: quick, reasonable savings.\n"
            "Standard: balanced, recommended.\n"
            "Max: best ratio, VERY slow and CPU-heavy."
        )
        for speed_val, speed_label in OXIPNG_SPEEDS.items():
            self.speed_combo.addItem(speed_label, speed_val)
        self.speed_combo.setCurrentIndex(1)
        for speed_val, tip in OXIPNG_SPEED_TOOLTIPS.items():
            idx = self.speed_combo.findData(speed_val)
            if idx >= 0:
                self.speed_combo.setItemData(idx, tip, Qt.ToolTipRole)
        speed_row.addWidget(self.speed_combo)
        speed_row.addStretch()
        self._speed_row_widgets = [speed_row.itemAt(0).widget(), self.speed_combo]
        speed_row.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(speed_row)

        self._on_mode_toggled()

    def _on_mode_toggled(self):
        current = self.selected_mode()
        is_lossless = current == Mode.LOSSLESS_PNG
        self.quality_slider.setVisible(not is_lossless)
        if is_lossless:
            self.quality_label.setText("Lossless (100%)")
            self.default_label.hide()
        else:
            self.quality_label.setText(f"{self.quality_slider.value()}%")
            self.default_label.setVisible(self.quality_slider.value() != 85)
        self.quality_label.setVisible(True)
        for w in self._speed_row_widgets:
            w.setVisible(is_lossless)
        self.png_notice.setVisible(is_lossless)
        self.mode_changed.emit(current)

    def _on_quality_changed(self, v: int):
        self.quality_label.setText(f"{v}%")
        self.default_label.setVisible(v != 85)

    def selected_mode(self) -> Mode:
        for mode, rb in self._mode_widgets.items():
            if rb.isChecked():
                return mode
        return Mode.WEBP

    def quality(self) -> int:
        return self.quality_slider.value()

    def oxipng_speed(self) -> int:
        return self.speed_combo.currentData()
