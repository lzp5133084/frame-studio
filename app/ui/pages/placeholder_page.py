"""AI 模块占位页（补帧 / 字幕水印 / 擦除 共用）。"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from ..widgets import Card


class PlaceholderPage(QWidget):
    def __init__(self, title: str, desc: str, plan: list[str], version: str,
                 parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)

        t = QLabel(title)
        t.setObjectName("pageTitle")
        d = QLabel(desc)
        d.setObjectName("pageDesc")
        root.addWidget(t)
        root.addWidget(d)

        card = Card("功能规划")
        for item in plan:
            lab = QLabel(f"•  {item}")
            lab.setObjectName("pageDesc")
            lab.setWordWrap(True)
            card.lay.addWidget(lab)
        badge = QLabel(f"🚧  开发中 · 计划 {version} 上线")
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setStyleSheet("color:#8B93A7; padding:14px; border:1px dashed #31405C;"
                            "border-radius:8px; margin-top:6px;")
        card.lay.addWidget(badge)
        root.addWidget(card)
        root.addStretch(1)
