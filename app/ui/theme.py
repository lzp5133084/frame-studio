"""2027 商用级深色主题。"""
from __future__ import annotations

ACCENT = "#5B7CFF"
ACCENT_2 = "#9B5BFF"
BG = "#0A0C10"
PANEL = "#10131B"
CARD = "#161B26"
BORDER = "#242C3D"
TEXT = "#E9EDF5"
TEXT_2 = "#8B93A7"

QSS = f"""
* {{
    font-family: "Segoe UI", "Microsoft YaHei UI", "PingFang SC", sans-serif;
    font-size: 13px;
    color: {TEXT};
    outline: none;
}}
QMainWindow, QWidget#root {{ background: {BG}; }}

/* ---------- 左侧导航 ---------- */
QFrame#sidebar {{
    background: {PANEL};
    border-right: 1px solid {BORDER};
}}
QLabel#logo {{
    font-size: 19px; font-weight: 700; letter-spacing: 1px;
    color: {TEXT}; padding: 22px 20px 4px 20px;
}}
QLabel#logoSub {{
    font-size: 11px; color: {TEXT_2}; padding: 0 20px 18px 20px;
}}
QPushButton[nav="true"] {{
    text-align: left; padding: 11px 16px; margin: 2px 10px;
    border: none; border-radius: 9px; color: {TEXT_2};
    background: transparent; font-weight: 500;
}}
QPushButton[nav="true"]:hover {{ background: #1A2030; color: {TEXT}; }}
QPushButton[nav="true"]:checked {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 rgba(91,124,255,0.22), stop:1 rgba(155,91,255,0.10));
    color: {TEXT}; font-weight: 600;
}}
QLabel#navFooter {{ color: #525B70; font-size: 11px; padding: 12px 20px; }}

/* ---------- 内容区 ---------- */
QFrame#card {{
    background: {CARD};
    border: 1px solid {BORDER};
    border-radius: 12px;
}}
QLabel#pageTitle {{ font-size: 20px; font-weight: 700; }}
QLabel#pageDesc {{ color: {TEXT_2}; }}
QLabel#cardTitle {{ font-size: 14px; font-weight: 600; }}
QLabel#fieldLabel {{ color: {TEXT_2}; }}
QLabel#infoValue {{ font-weight: 600; }}

/* ---------- 输入控件 ---------- */
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
    background: #0E1219; border: 1px solid {BORDER};
    border-radius: 8px; padding: 8px 10px; selection-background-color: {ACCENT};
}}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
    border: 1px solid {ACCENT};
}}
QComboBox::drop-down {{ border: none; width: 26px; }}
QComboBox QAbstractItemView {{
    background: #161B26; border: 1px solid {BORDER};
    selection-background-color: {ACCENT}; border-radius: 8px;
}}

/* ---------- 按钮 ---------- */
QPushButton {{
    background: #1C2331; border: 1px solid {BORDER};
    border-radius: 8px; padding: 9px 16px; font-weight: 500;
}}
QPushButton:hover {{ background: #242C3E; border-color: #31405C; }}
QPushButton:pressed {{ background: #171D29; }}
QPushButton:disabled {{ color: #525B70; background: #141924; }}
QPushButton[primary="true"] {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
        stop:0 {ACCENT}, stop:1 {ACCENT_2});
    border: none; color: white; font-weight: 600;
}}
QPushButton[primary="true"]:hover {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
        stop:0 #6C8AFF, stop:1 #A96FFF);
}}
QPushButton[danger="true"] {{ background: #3A1E28; border-color: #5C2A3A; color: #FF7A93; }}

/* ---------- 进度条 ---------- */
QProgressBar {{
    background: #0E1219; border: 1px solid {BORDER};
    border-radius: 7px; height: 14px; text-align: center;
    color: {TEXT_2}; font-size: 11px;
}}
QProgressBar::chunk {{
    border-radius: 6px;
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 {ACCENT}, stop:1 #4FD1FF);
}}

/* ---------- 其他 ---------- */
QTextEdit, QPlainTextEdit {{
    background: #0C0F15; border: 1px solid {BORDER}; border-radius: 8px;
    font-family: "Cascadia Code", Consolas, monospace; font-size: 12px;
    color: {TEXT_2}; padding: 6px;
}}
QScrollBar:vertical {{ background: transparent; width: 10px; margin: 2px; }}
QScrollBar::handle:vertical {{ background: #2A3347; border-radius: 5px; min-height: 30px; }}
QScrollBar::handle:vertical:hover {{ background: #3A4560; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QToolTip {{ background: #1C2331; border: 1px solid {BORDER}; color: {TEXT}; padding: 6px 8px; }}
"""
