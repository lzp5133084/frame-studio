"""FFmpeg / FFprobe 封装：媒体信息探测 + 带进度的后台任务。"""
from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass, field

from PySide6.QtCore import QThread, Signal

from .paths import bundled_ffmpeg, bundled_ffprobe

_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def _exe(path) -> str:
    """内置工具优先，缺失时回退到系统 PATH。"""
    p = str(path)
    return p if os.path.exists(p) else os.path.basename(p)


def probe_media(path: str) -> dict:
    """探测视频信息。失败返回空 dict。

    返回键：duration_ms, width, height, fps, nb_frames, codec, size_bytes
    """
    cmd = [
        _exe(bundled_ffprobe()), "-v", "error", "-select_streams", "v:0",
        "-show_entries",
        "stream=width,height,r_frame_rate,nb_frames,codec_name:format=duration,size",
        "-of", "json", path,
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", creationflags=_NO_WINDOW)
        data = json.loads(r.stdout or "{}")
    except Exception:
        return {}
    st = (data.get("streams") or [{}])[0]
    fmt = data.get("format") or {}

    def _fps(raw: str) -> float:
        try:
            n, d = raw.split("/")
            return round(int(n) / max(int(d), 1), 3)
        except Exception:
            return 0.0

    duration_s = float(fmt.get("duration") or 0)
    fps = _fps(st.get("r_frame_rate", "0/1"))
    nb = st.get("nb_frames")
    return {
        "duration_ms": int(duration_s * 1000),
        "width": int(st.get("width") or 0),
        "height": int(st.get("height") or 0),
        "fps": fps,
        "nb_frames": int(nb) if nb and nb.isdigit() else int(duration_s * fps),
        "codec": st.get("codec_name", ""),
        "size_bytes": int(fmt.get("size") or 0),
    }


def fmt_duration(ms: int) -> str:
    s = ms // 1000
    return f"{s // 3600:02d}:{(s % 3600) // 60:02d}:{s % 60:02d}"


def fmt_size(n: int) -> str:
    for u in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {u}"
        n /= 1024
    return f"{n:.1f} TB"


@dataclass
class FFmpegJob(QThread):
    """后台执行一条 ffmpeg 命令，按帧数回报进度。"""

    progressed = Signal(int, str)          # 百分比, 状态文本
    log_line = Signal(str)                 # 原始输出行（可选展示）
    done = Signal(bool, str)               # 是否成功, 消息

    args: list = field(default_factory=list)
    total_frames: int = 0

    def __post_init__(self):
        super().__init__()
        self._proc: subprocess.Popen | None = None
        self._stopped = False

    def run(self):  # noqa: D102
        cmd = [_exe(bundled_ffmpeg()), "-hide_banner", "-y",
               *self.args, "-progress", "pipe:1", "-nostats"]
        try:
            self._proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding="utf-8", errors="replace", bufsize=1,
                creationflags=_NO_WINDOW)
            percent = 0
            assert self._proc.stdout is not None
            for raw in self._proc.stdout:
                if self._stopped:
                    break
                line = raw.strip()
                if line.startswith("frame="):
                    try:
                        frames = int(line.split("=", 1)[1].strip())
                    except ValueError:
                        continue
                    if self.total_frames > 0:
                        percent = min(99, frames * 100 // self.total_frames)
                    self.progressed.emit(percent, f"已处理 {frames} 帧")
                elif line == "progress=end":
                    percent = 100
                    self.progressed.emit(100, "完成")
                elif line:
                    self.log_line.emit(line)
            self._proc.wait()
            if self._stopped:
                self.done.emit(False, "已取消")
            elif self._proc.returncode == 0:
                self.done.emit(True, "任务完成")
            else:
                self.done.emit(False, f"ffmpeg 退出码 {self._proc.returncode}")
        except FileNotFoundError:
            self.done.emit(False, "未找到 ffmpeg，请检查 tools/ffmpeg 或系统 PATH")
        except Exception as exc:  # noqa: BLE001
            self.done.emit(False, str(exc))

    def stop(self):  # noqa: D102
        self._stopped = True
        if self._proc and self._proc.poll() is None:
            self._proc.kill()
