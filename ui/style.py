DARK_THEME = """
/* MainWindow and overall styling */
QMainWindow {
    background-color: #121212;
}
QWidget {
    color: #e0e0e0;
    font-family: "Segoe UI", "Inter", sans-serif;
    font-size: 13px;
}
QToolTip {
    background-color: #2b2b2b;
    color: #ffffff;
    border: 1px solid #444444;
    padding: 5px;
    border-radius: 4px;
}

/* Push Buttons */
QPushButton {
    background-color: #262626;
    border: 1px solid #3d3d3d;
    border-radius: 6px;
    padding: 6px 16px;
    font-weight: 500;
    min-height: 20px;
}
QPushButton:hover {
    background-color: #333333;
    border-color: #00bcd4; /* teal highlight */
}
QPushButton:pressed {
    background-color: #1f1f1f;
}
QPushButton:disabled {
    background-color: #1a1a1a;
    border-color: #2c2c2c;
    color: #666666;
}

/* Flat Buttons (like title buttons) */
QPushButton[flat="true"] {
    background-color: transparent;
    border: none;
    padding: 0;
    font-weight: bold;
    font-size: 14px;
    color: #00bcd4;
    text-align: left;
}

/* List Widget & Table Widget */
QListWidget, QTableWidget {
    background-color: #1e1e1e;
    border: 1px solid #2d2d2d;
    border-radius: 8px;
    gridline-color: #2d2d2d;
    padding: 4px;
}
QListWidget::item, QTableWidget::item {
    padding: 6px;
    border-bottom: 1px solid #262626;
}
QListWidget::item:selected, QTableWidget::item:selected {
    background-color: #00bcd4;
    color: #121212;
    border-radius: 4px;
}
QHeaderView::section {
    background-color: #262626;
    color: #ffffff;
    padding: 6px;
    border: none;
    font-weight: bold;
}

/* Combo Box */
QComboBox {
    background-color: #262626;
    border: 1px solid #3d3d3d;
    border-radius: 6px;
    padding: 4px 12px;
    min-height: 20px;
}
QComboBox:hover {
    border-color: #00bcd4;
}
QComboBox::drop-down {
    border: none;
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 20px;
}
QComboBox QAbstractItemView {
    background-color: #262626;
    border: 1px solid #3d3d3d;
    selection-background-color: #00bcd4;
    selection-color: #121212;
}

/* Slider */
QSlider::groove:horizontal {
    height: 6px;
    background: #2a2a2a;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    background: #00bcd4;
    width: 16px;
    margin-top: -5px;
    margin-bottom: -5px;
    border-radius: 8px;
}
QSlider::handle:horizontal:hover {
    background: #00e5ff;
}

/* Progress Bar */
QProgressBar {
    border: 1px solid #2d2d2d;
    border-radius: 6px;
    background-color: #1e1e1e;
    text-align: center;
    color: #ffffff;
    font-weight: bold;
}
QProgressBar::chunk {
    background-color: #00bcd4;
    border-radius: 5px;
}

/* Custom spacing/margins for mode widgets and group layout */
QRadioButton, QCheckBox {
    spacing: 6px;
}
"""
