"""任务参数构建：抽帧 / 合成。仅负责拼装 ffmpeg 参数，不执行。"""
from __future__ import annotations

import re
from pathlib import Path

# 抽帧模式
M_ALL = "all"        # 全部帧
M_FPS = "fps"        # 按帧率抽取
M_INTERVAL = "sec"   # 按间隔秒抽取


def build_extract_args(video: str, out_dir: Path, mode: str,
                       value: float, img_fmt: str, prefix: str) -> tuple[list, Path]:
    """返回 (ffmpeg参数, 输出模式路径)。输出为 prefix%06d.fmt 序列。"""
    pattern = out_dir / f"{prefix}%06d.{img_fmt}"
    args = ["-i", video]
    if mode == M_FPS and value > 0:
        args += ["-vf", f"fps={value}"]
    elif mode == M_INTERVAL and value > 0:
        args += ["-vf", f"fps=1/{value}"]
    if img_fmt == "jpg":
        args += ["-q:v", "2"]
    args += [str(pattern)]
    return args, pattern


def detect_frame_pattern(folder: Path) -> tuple[str | None, int]:
    """探测目录内帧序列：返回 (printf风格模式如 %06d.png, 帧数)。无序列返回 (None, 0)。"""
    rx = re.compile(r"^(.*?)(\d+)\.(png|jpg|jpeg|webp)$", re.IGNORECASE)
    best: dict[tuple, list] = {}
    for f in folder.iterdir():
        m = rx.match(f.name)
        if not m:
            continue
        key = (m.group(1), len(m.group(2)), m.group(3).lower())
        best.setdefault(key, []).append(int(m.group(2)))
    if not best:
        return None, 0
    (prefix, width, ext), nums = max(best.items(), key=lambda kv: len(kv[1]))
    return f"{prefix}%0{width}d.{ext}", len(nums)


def build_compose_args(in_pattern: str, fps: float, crf: int,
                       preset: str, out_file: str,
                       scale: tuple[int, int] | None = None) -> list:
    """帧序列 → 视频（libx264，yuv420p 保证兼容性）。"""
    args = ["-framerate", str(fps), "-i", in_pattern]
    vf = ["format=yuv420p"]
    if scale:
        vf.insert(0, f"scale={scale[0]}:{scale[1]}")
    args += ["-vf", ",".join(vf), "-c:v", "libx264",
             "-crf", str(crf), "-preset", preset, "-pix_fmt", "yuv420p", out_file]
    return args
