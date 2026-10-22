"""应用入口。"""
from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from .ui.main_window import MainWindow
from .ui.theme import QSS


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("FrameStudio")
    app.setOrganizationName("RJX")
    app.setStyleSheet(QSS)
    win = MainWindow()
    win.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
