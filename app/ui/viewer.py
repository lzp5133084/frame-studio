"""帧查看器：目录内帧序列大图浏览。

点击图片在「适应窗口 ↔ 实际大小」间切换；← / → 翻前后帧；
Home / End 跳首尾；Esc 退出。
"""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent, QPixmap
from PySide6.QtWidgets import (QDialog, QHBoxLayout, QLabel, QScrollArea,
                               QVBoxLayout)

_IMG_EXT = (".png", ".jpg", ".jpeg", ".webp", ".bmp")


def collect_frames(folder: Path) -> list[Path]:
    """收集目录内全部图片帧，按文件名排序。"""
    if not folder.is_dir():
        return []
    return sorted((p for p in folder.iterdir()
                   if p.suffix.lower() in _IMG_EXT), key=lambda p: p.name)


class FrameViewer(QDialog):
    """帧序列查看器。"""

    def __init__(self, folder: Path, parent=None):
        super().__init__(parent)
        self._frames = collect_frames(folder)
        self._idx = 0
        self._fit = True  # True=适应窗口  False=实际大小(可滚动)

        self.setWindowTitle(f"帧查看 — {folder}")
        self.resize(1000, 680)
        self.setStyleSheet("QDialog { background:#0C0F15; }")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # 图片区（滚动容器，适应窗口时关闭滚动条）
        self._img = QLabel()
        self._img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._img.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._scroll = QScrollArea()
        self._scroll.setWidget(self._img)
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet("QScrollArea { border:none; background:#0C0F15; }")
        # 关键：滚动区默认会吞掉方向键用于滚动，必须禁用焦点让按键到达对话框
        self._scroll.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._scroll.viewport().setFocusPolicy(Qt.FocusPolicy.NoFocus)
        root.addWidget(self._scroll, 1)

        # 底部状态栏
        bar = QHBoxLayout()
        bar.setContentsMargins(14, 6, 14, 8)
        self._status = QLabel()
        self._status.setStyleSheet("color:#E9EDF5; font-size:13px;")
        hint = QLabel("点击图片放大/还原   ·   ← → 前后帧   ·   Home/End 首尾   ·   ESC 退出")
        hint.setStyleSheet("color:#8B93A7; font-size:12px;")
        bar.addWidget(self._status)
        bar.addStretch(1)
        bar.addWidget(hint)
        root.addLayout(bar)

        # 点击装在 viewport 上（含图片以外的空白区），切换 适应窗口/实际大小
        self._scroll.viewport().installEventFilter(self)
        if self._frames:
            self._show(0)
        else:
            self._status.setText("该目录没有可查看的图片帧")

    # ----------------------------------------------------------
    def _show(self, idx: int):
        self._idx = max(0, min(len(self._frames) - 1, idx))
        f = self._frames[self._idx]
        self._pix = QPixmap(str(f))
        self._render()
        self._status.setText(f"第 {self._idx + 1} / {len(self._frames)} 帧   ·   {f.name}")

    def _render(self):
        if self._pix.isNull():
            self._img.setText("无法加载该图片")
            return
        if self._fit:
            self._scroll.setWidgetResizable(True)
            size = self._scroll.viewport().size()
            self._img.setPixmap(self._pix.scaled(
                size, Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation))
        else:
            self._scroll.setWidgetResizable(False)
            self._img.setPixmap(self._pix)
            self._img.adjustSize()

    # ----------------------------------------------------------
    def keyPressEvent(self, e: QKeyEvent):  # noqa: N802
        k = e.key()
        if k == Qt.Key.Key_Escape:
            self.close()
        elif not self._frames:
            return
        elif k == Qt.Key.Key_Left:
            self._show(self._idx - 1)
        elif k == Qt.Key.Key_Right:
            self._show(self._idx + 1)
        elif k == Qt.Key.Key_Home:
            self._show(0)
        elif k == Qt.Key.Key_End:
            self._show(len(self._frames) - 1)
        else:
            super().keyPressEvent(e)

    def eventFilter(self, obj, ev):  # noqa: N802
        if obj is self._scroll.viewport() and ev.type() == ev.Type.MouseButtonPress:
            if self._frames:
                self._fit = not self._fit
                self._render()
            return True
        return super().eventFilter(obj, ev)

    def resizeEvent(self, e):  # noqa: N802
        super().resizeEvent(e)
        if getattr(self, "_pix", None) is not None and self._fit:
            self._render()
