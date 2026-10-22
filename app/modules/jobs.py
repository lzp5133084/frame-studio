"""任务参数构建：抽帧 / 合成。仅负责拼装 ffmpeg 参数，不执行。"""
from __future__ import annotations

import re
from pathlib import Path

# 抽帧模式
M_ALL = "all"        # 全部帧
M_FPS = "fps"        # 按帧率抽取
M_INTERVAL = "sec"   # 按间隔秒抽取
M_MOTION = "motion"  # 按动态程度（剔除静止画面）


def _mpdecimate_params(sensitivity: int) -> str:
    """灵敏度 0~100 → mpdecimate 阈值。越灵敏保留越多帧。

    录屏场景关键在 frac（差异块占比阈值）：鼠标指针移动仅产生 2~4 个
    差异块（1080p 全帧约 32400 块），frac 必须低到 0.0001 级才能保留；
    而大画面切换（翻页/滚动）涉及上千块，frac 0.02 即可。故 frac 走对数
    映射 0.02 → 0.0001；lo 随灵敏度下调以捕捉低对比变化，hi 保持默认。
    """
    s = max(0, min(100, sensitivity)) / 100.0
    frac = 0.02 * (0.005 ** s)        # 0.02(只留大切换) ~ 0.0001(鼠标移动也留)
    lo = int(64 * (5 - 2 * s))        # 320 ~ 192，编码噪声仍被过滤
    return f"mpdecimate=hi=768:lo={lo}:frac={frac:.5f}"


def build_extract_args(video: str, out_dir: Path, mode: str,
                       value: float, img_fmt: str, prefix: str) -> tuple[list, Path]:
    """返回 (ffmpeg参数, 输出模式路径)。输出为 prefix%06d.fmt 序列。"""
    pattern = out_dir / f"{prefix}%06d.{img_fmt}"
    args = ["-i", video]
    if mode == M_FPS and value > 0:
        args += ["-vf", f"fps={value}"]
    elif mode == M_INTERVAL and value > 0:
        args += ["-vf", f"fps=1/{value}"]
    elif mode == M_MOTION:
        # value 传灵敏度 0~100；vfr 防止 image2 按 CFR 复制帧填补丢帧空洞
        args += ["-vf", _mpdecimate_params(int(value)), "-fps_mode", "vfr"]
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


def build_gif_args(in_pattern: str, fps: float, width: int,
                   out_gif: str, palette: str) -> tuple[list, list]:
    """帧序列 → GIF，两步：① 生成调色板 ② 应用调色板（高质量抖动）。

    width ≤ 0 时保持原始宽度。返回 (第一步参数, 第二步参数)。
    """
    scale = f"scale={width}:-1:flags=lanczos," if width > 0 else ""
    step1 = ["-framerate", str(fps), "-i", in_pattern,
             "-vf", f"{scale}palettegen=max_colors=256:stats_mode=diff", "-y", palette]
    step2 = ["-framerate", str(fps), "-i", in_pattern, "-i", palette,
             "-lavfi", f"{scale}paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle",
             "-y", out_gif]
    return step1, step2
