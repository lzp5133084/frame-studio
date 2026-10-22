# 帧界 FrameStudio

视频**帧级** AI 处理平台 —— 抽帧 → 逐帧处理（补帧 / 字幕水印 / 智能擦除）→ 重合成。

![Version](https://img.shields.io/badge/version-0.1.0-5B7CFF)

## 功能路线图

| 模块 | 状态 | 说明 |
|---|---|---|
| 抽帧提取 | ✅ v0.1 | 全帧 / 按帧率 / 按间隔三种模式，PNG/JPG 序列输出 |
| 视频合成 | ✅ v0.1 | 帧序列 → H.264 视频，CRF / 预设 / 分辨率可调 |
| 智能补帧 | 🚧 v0.2 | RIFE 本地插帧 + 火山引擎 FILM 云端，帧缺口自动补全 |
| 字幕水印 | 🚧 v0.3 | SRT/ASS 烧录、文字/图片水印，帧区间精确控制 |
| 智能擦除 | 🚧 v0.4 | 涂抹/SAM 点选/文本描述三种选区，ProPainter 修复 + AI 补全替换 |

## 快速开始

```bat
:: 1. 安装依赖（仅首次）
py -m pip install -r requirements.txt

:: 2. 下载内置 FFmpeg（仅首次，已含在仓库外发布包中可跳过）
powershell -ExecutionPolicy Bypass -File scripts\download_ffmpeg.ps1

:: 3. 启动
run.bat
```

## 技术栈

- **UI**：PySide6（Qt 6）+ 自研深色主题
- **媒体内核**：FFmpeg 9（内置 `tools/ffmpeg`，零外部依赖）
- **AI 推理**：本地（RIFE / SAM / ProPainter）与云端（火山引擎 ARK）可切换，见 `设置` 页

## 目录结构

```
app/
├── core/        # FFmpeg 封装、路径、设置
├── modules/     # 任务参数构建（抽帧 / 合成 / 后续 AI）
└── ui/          # 主题、主窗口、功能页
tools/ffmpeg/    # 内置 FFmpeg（不入库，脚本下载）
workspace/       # 默认工作目录（帧序列、输出）
docs/            # 使用说明、变更记录
```
