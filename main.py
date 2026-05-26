#!/usr/bin/env python3
import os
import sys

# Ensure the project root directory is in sys.path so imports work in any environment
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PySide6.QtWidgets import QApplication

from ui.window import MainWindow
from ui.style import DARK_THEME


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_THEME)
    app.setApplicationName("Easy Image Compressor")
    app.setOrganizationName("easyimgcomp")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
