"""主窗口：左侧导航 + 页面堆栈。"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QButtonGroup, QFrame, QHBoxLayout, QLabel,
                               QMainWindow, QPushButton, QStackedWidget,
                               QVBoxLayout, QWidget)

from .pages.compose_page import ComposePage
from .pages.extract_page import ExtractPage
from .pages.placeholder_page import PlaceholderPage
from .pages.settings_page import SettingsPage

_VERSION = "v0.1.0"

_NAV = [
    ("🎞", "抽帧提取"),
    ("🎬", "视频合成"),
    ("⏩", "智能补帧"),
    ("🔤", "字幕水印"),
    ("🧽", "智能擦除"),
    ("⚙", "设置"),
]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"帧界 FrameStudio {_VERSION} — 视频帧级处理平台")
        self.resize(1160, 760)
        self.setMinimumSize(980, 640)

        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        lay = QHBoxLayout(root)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        lay.addWidget(self._build_sidebar())
        lay.addWidget(self._build_stack(), 1)

    # ----------------------------------------------------------
    def _build_sidebar(self) -> QFrame:
        bar = QFrame()
        bar.setObjectName("sidebar")
        bar.setFixedWidth(218)
        lay = QVBoxLayout(bar)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(2)

        logo = QLabel("帧界")
        logo.setObjectName("logo")
        sub = QLabel("FrameStudio · 帧级处理")
        sub.setObjectName("logoSub")
        lay.addWidget(logo)
        lay.addWidget(sub)

        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self._nav_btns: list[QPushButton] = []
        for i, (icon, name) in enumerate(_NAV):
            btn = QPushButton(f"{icon}   {name}")
            btn.setProperty("nav", True)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, idx=i: self._switch(idx))
            self._group.addButton(btn, i)
            lay.addWidget(btn)
            self._nav_btns.append(btn)
        lay.addStretch(1)

        footer = QLabel(f"{_VERSION} · RJX Lab")
        footer.setObjectName("navFooter")
        lay.addWidget(footer)
        return bar

    def _build_stack(self) -> QStackedWidget:
        self.stack = QStackedWidget()
        self.stack.addWidget(ExtractPage())
        self.stack.addWidget(ComposePage())
        self.stack.addWidget(PlaceholderPage(
            "智能补帧", "对帧数进行自动补全：低帧率视频插值到丝滑高帧率，或填补抽帧缺口",
            ["RIFE 本地实时插帧（24→60/120fps，N 卡加速）",
             "云端 FILM 大运动插帧（火山引擎）",
             "帧序列缺口自动检测与补全",
             "补帧结果与原画逐帧对比预览"], "v0.2"))
        self.stack.addWidget(PlaceholderPage(
            "字幕水印", "批量为每帧叠加字幕、文字与图片水印，精确到帧级时间轴",
            ["SRT/ASS 字幕批量烧录（字体/描边/位置可调）",
             "文字水印：内容 / 透明度 / 九宫格位置 / 平铺",
             "图片 Logo 水印：缩放 / 旋转 / 时间段",
             "帧区间精确控制（第 N~M 帧生效）"], "v0.3"))
        self.stack.addWidget(PlaceholderPage(
            "智能擦除", "自定义擦除物品或人物，并自动补全 / 替换缺失处画面",
            ["三种选区方式：涂抹框选 / SAM 点选 / 文本描述识别",
             "ProPainter 视频修复（本地，时序一致不闪烁）",
             "火山引擎图像补全 API（云端备选）",
             "缺失区域 AI 替换：用描述文字生成新内容填补"], "v0.4"))
        self.stack.addWidget(SettingsPage())
        self._nav_btns[0].setChecked(True)
        return self.stack

    def _switch(self, idx: int):
        self.stack.setCurrentIndex(idx)
