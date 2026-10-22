"""应用设置（QSettings 持久化）。"""
from __future__ import annotations

from PySide6.QtCore import QSettings

_ORG, _APP = "RJX", "FrameStudio"

# AI 推理模式
AI_LOCAL = "local"      # 本地模型
AI_CLOUD = "cloud"      # 云端 API（火山引擎）
AI_HYBRID = "hybrid"    # 混合（默认）


def _s() -> QSettings:
    return QSettings(_ORG, _APP)


def get(key: str, default: str = "") -> str:
    return str(_s().value(key, default))


def set(key: str, value: str) -> None:  # noqa: A001
    _s().setValue(key, value)


# ---- 常用键 ----
K_FFMPEG = "ffmpeg/path"
K_OUTDIR = "output/dir"
K_AI_MODE = "ai/mode"
K_ARK_KEY = "ark/api_key"


def ai_mode() -> str:
    return get(K_AI_MODE, AI_HYBRID)
