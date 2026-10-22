"""路径解析：兼容源码运行与 PyInstaller 打包。"""
from __future__ import annotations

import os
import sys
from pathlib import Path


def app_root() -> Path:
    """项目根目录（打包后为 exe 所在目录）。"""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


def _tool(name: str) -> Path:
    exe = f"{name}.exe" if os.name == "nt" else name
    return app_root() / "tools" / "ffmpeg" / "bin" / exe


def bundled_ffmpeg() -> Path:
    return _tool("ffmpeg")


def bundled_ffprobe() -> Path:
    return _tool("ffprobe")


def workspace_dir() -> Path:
    """默认工作目录（抽帧输出等）。"""
    p = app_root() / "workspace"
    p.mkdir(parents=True, exist_ok=True)
    return p
