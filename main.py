#!/usr/bin/env python3
import sys

from PySide6.QtWidgets import QApplication

from ui.window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Easy Image Compressor")
    app.setOrganizationName("easyimgcomp")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
