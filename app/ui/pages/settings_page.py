"""设置页：FFmpeg 路径 / 默认输出 / AI 推理模式 / 火山引擎 Key。"""
from __future__ import annotations

from PySide6.QtWidgets import (QComboBox, QLabel, QLineEdit, QMessageBox,
                               QPushButton, QVBoxLayout, QWidget)

from ...core import settings
from ...core.paths import bundled_ffmpeg, workspace_dir
from ..widgets import Card, FieldRow, PathPicker

_MODES = [
    ("混合模式（简单任务本地，重度 AI 走云端）— 推荐", settings.AI_HYBRID),
    ("本地模型（离线可用，需 NVIDIA 显卡）", settings.AI_LOCAL),
    ("云端 API（火山引擎，不依赖本地显卡）", settings.AI_CLOUD),
]


class SettingsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)

        title = QLabel("设置")
        title.setObjectName("pageTitle")
        desc = QLabel("引擎路径、输出位置与 AI 推理策略")
        desc.setObjectName("pageDesc")
        root.addWidget(title)
        root.addWidget(desc)

        # ---- 引擎 ----
        eng = Card("处理引擎")
        self.ffmpeg = PathPicker("留空则使用内置 tools/ffmpeg", is_file=True,
                                 file_filter="ffmpeg.exe")
        if settings.get(settings.K_FFMPEG):
            self.ffmpeg.setText(settings.get(settings.K_FFMPEG))
        eng.lay.addWidget(FieldRow("FFmpeg", self.ffmpeg))
        self.outdir = PathPicker(f"默认 {workspace_dir()}", is_file=False)
        if settings.get(settings.K_OUTDIR):
            self.outdir.setText(settings.get(settings.K_OUTDIR))
        eng.lay.addWidget(FieldRow("默认输出", self.outdir))
        root.addWidget(eng)

        # ---- AI ----
        ai = Card("AI 推理（补帧 / 擦除 / 补全）")
        self.mode = QComboBox()
        for label, key in _MODES:
            self.mode.addItem(label, key)
        cur = settings.ai_mode()
        self.mode.setCurrentIndex(max(0, [k for _, k in _MODES].index(cur)
                                    if cur in [k for _, k in _MODES] else 0))
        ai.lay.addWidget(FieldRow("推理模式", self.mode))

        self.ark = QLineEdit()
        self.ark.setEchoMode(QLineEdit.EchoMode.Password)
        self.ark.setPlaceholderText("火山引擎 ARK API Key（云端模式必填）")
        self.ark.setText(settings.get(settings.K_ARK_KEY))
        ai.lay.addWidget(FieldRow("ARK Key", self.ark))
        note = QLabel("本地模型（RIFE / SAM / ProPainter）将在对应模块首次使用时自动下载")
        note.setObjectName("pageDesc")
        ai.lay.addWidget(note)
        root.addWidget(ai)

        save_btn = QPushButton("保存设置")
        save_btn.setProperty("primary", True)
        save_btn.setFixedWidth(140)
        save_btn.clicked.connect(self._save)
        root.addWidget(save_btn)
        root.addStretch(1)

    def _save(self):
        settings.set(settings.K_FFMPEG, self.ffmpeg.text())
        settings.set(settings.K_OUTDIR, self.outdir.text())
        settings.set(settings.K_AI_MODE, self.mode.currentData())
        settings.set(settings.K_ARK_KEY, self.ark.text().strip())
        QMessageBox.information(self, "已保存", "设置已生效")
