"""术语表 + 术语组件：专业词语右上角小问号，点击弹大白话解释。"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

TERMS: dict[str, tuple[str, str]] = {
    "crf": ("画质等级（CRF）",
            "数字越小，画质越好、文件越大。18 几乎看不出压缩痕迹（推荐），23 是通用默认值，"
            "28 文件小但会明显模糊。填 0 就是无损，但文件会非常大。"),
    "fps": ("帧率",
            "每秒播放多少张画面。30 帧/秒就是每秒 30 张。数字越高越流畅，文件也越大。"
            "合成时与原视频帧率保持一致，可避免视频变快或变慢。"),
    "preset": ("编码速度",
               "压缩视频的速度档位：选「极快」出片快但同画质下文件略大；选「较慢」文件更小但更耗时间。"
               "日常用「标准」即可。"),
    "ffmpeg": ("媒体引擎（FFmpeg）",
               "全球通用的开源音视频处理引擎，本软件的解码、抽帧、合成全部由它在后台完成。"
               "软件已内置，一般无需修改。"),
    "ark": ("火山引擎密钥（ARK Key）",
            "火山引擎（字节跳动云服务）的访问钥匙。使用云端 AI 功能（智能擦除、云端补全）时"
            "需要它才能调用，粘贴到此处即可，只保存在你自己电脑上。"),
    "ai_mode": ("AI 推理模式",
                "选择 AI 计算在哪里运行：「本地」用你自己的显卡（离线可用、免费，需要 N 卡）；"
                "「云端」用火山引擎服务器（要联网、按量计费）；「混合」自动选择，推荐。"),
    "sensitivity": ("灵敏度",
                    "判断画面「算不算动了」的严格程度。越高越敏感，轻微变化也会保留；"
                    "越低越严格，只保留明显变化的画面。"),
    "workspace": ("工作目录",
                  "抽出的帧图片、合成的视频默认存放的位置，在程序目录下的 workspace 文件夹里。"),
    "rife": ("RIFE 插帧模型",
             "开源 AI 补帧模型：在两帧之间智能生成过渡画面，把低帧率视频变得丝滑流畅，"
             "本地显卡即可运行。"),
    "sam": ("SAM 智能分割",
            "Meta 开源的「点一下就选中」AI 模型：在画面上点一下人或物，自动圈出完整轮廓，"
            "省去手动描边。"),
    "propainter": ("ProPainter 视频修复",
                   "开源视频修复 AI：把被擦除的区域用周围画面自然填补，且前后帧连贯、不闪烁。"),
    "film": ("FILM 插帧模型",
             "谷歌的大幅度运动插帧模型，擅长运动剧烈的画面，走云端调用。"),
    "subtitle": ("字幕文件（SRT/ASS）",
                 "常见字幕文件格式，记录了每句台词的出现时间和文字内容，可批量烧录进画面。"),
}


def show_term_popup(anchor: QWidget, key: str):
    """在锚点附近弹出术语解释气泡（点击外部自动关闭）。"""
    title, text = TERMS.get(key, ("术语", "暂无解释"))
    pop = QFrame(anchor.window(), Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
    pop.setObjectName("termPop")
    pop.setStyleSheet(
        "#termPop { background:#1C2331; border:1px solid #5B7CFF; border-radius:10px; }")
    lay = QVBoxLayout(pop)
    lay.setContentsMargins(14, 10, 14, 12)
    lay.setSpacing(6)
    t = QLabel(title)
    t.setStyleSheet("font-weight:700; font-size:13px; color:#E9EDF5;")
    d = QLabel(text)
    d.setWordWrap(True)
    d.setFixedWidth(260)
    d.setStyleSheet("color:#8B93A7; font-size:12px; line-height:1.6;")
    lay.addWidget(t)
    lay.addWidget(d)
    pop.move(QCursor.pos().x() + 8, QCursor.pos().y() + 8)
    pop.show()
    anchor._term_pop = pop  # 防 GC


class Term(QWidget):
    """术语标签：中文名 + 右上角小问号图标，点击弹大白话解释。"""

    def __init__(self, text: str, key: str, parent: QWidget | None = None):
        super().__init__(parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(3)
        lab = QLabel(text)
        lab.setStyleSheet("color:#8B93A7;")
        btn = QPushButton("?")
        btn.setFixedSize(14, 14)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setToolTip("点击查看大白话解释")
        btn.setStyleSheet(
            "QPushButton { border-radius:7px; border:1px solid #31405C; background:#1A2030;"
            " color:#5B7CFF; font-size:9px; font-weight:700; padding:0; }"
            "QPushButton:hover { background:#5B7CFF; color:white; }")
        btn.clicked.connect(lambda: show_term_popup(self, key))
        lay.addWidget(lab)
        lay.addWidget(btn, 0, Qt.AlignmentFlag.AlignTop)
        lay.addStretch(1)
