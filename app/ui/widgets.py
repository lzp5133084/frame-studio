"""通用 UI 组件。"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QFileDialog, QFrame, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QVBoxLayout, QWidget)


class Card(QFrame):
    """圆角卡片容器。"""

    def __init__(self, title: str = "", parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("card")
        self.lay = QVBoxLayout(self)
        self.lay.setContentsMargins(18, 14, 18, 16)
        self.lay.setSpacing(10)
        if title:
            t = QLabel(title)
            t.setObjectName("cardTitle")
            self.lay.addWidget(t)


class PathPicker(QWidget):
    """路径选择行：输入框 + 浏览按钮。"""

    def __init__(self, placeholder: str, is_file: bool = True,
                 file_filter: str = "", save: bool = False,
                 parent: QWidget | None = None):
        super().__init__(parent)
        self._is_file, self._filter, self._save = is_file, file_filter, save
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)
        self.edit = QLineEdit()
        self.edit.setPlaceholderText(placeholder)
        btn = QPushButton("浏览…")
        btn.clicked.connect(self._pick)
        lay.addWidget(self.edit, 1)
        lay.addWidget(btn)

    def _pick(self):
        if self._is_file:
            if self._save:
                p, _ = QFileDialog.getSaveFileName(self, "选择保存位置", "", self._filter)
            else:
                p, _ = QFileDialog.getOpenFileName(self, "选择文件", "", self._filter)
        else:
            p = QFileDialog.getExistingDirectory(self, "选择目录")
        if p:
            self.edit.setText(p)

    def text(self) -> str:  # noqa: D102
        return self.edit.text().strip()

    def setText(self, v: str):  # noqa: D102
        self.edit.setText(v)


class FieldRow(QWidget):
    """表单行：左标签右控件。"""

    def __init__(self, label: str, widget: QWidget, parent: QWidget | None = None):
        super().__init__(parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lab = QLabel(label)
        lab.setObjectName("fieldLabel")
        lab.setFixedWidth(86)
        lab.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        lay.addWidget(lab)
        lay.addWidget(widget, 1)
