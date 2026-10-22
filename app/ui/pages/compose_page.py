"""视频合成页：帧序列 → 视频。"""
from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (QComboBox, QDoubleSpinBox, QHBoxLayout, QLabel,
                               QMessageBox, QProgressBar, QPushButton, QSpinBox,
                               QVBoxLayout, QWidget)

from ...core.ffmpeg import FFmpegJob
from ...modules.jobs import build_compose_args, detect_frame_pattern
from ..widgets import Card, FieldRow, PathPicker


class ComposePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._job: FFmpegJob | None = None
        self._frame_count = 0

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)

        title = QLabel("视频合成")
        title.setObjectName("pageTitle")
        desc = QLabel("将处理后的帧序列重新合成为视频（H.264 / 高兼容 yuv420p）")
        desc.setObjectName("pageDesc")
        root.addWidget(title)
        root.addWidget(desc)

        # ---- 帧序列卡片 ----
        src_card = Card("帧序列")
        self.src = PathPicker("选择帧图片所在目录…", is_file=False)
        self.src.edit.editingFinished.connect(self._detect)
        src_card.lay.addWidget(FieldRow("帧目录", self.src))
        self.detect_label = QLabel("未检测到帧序列")
        self.detect_label.setObjectName("pageDesc")
        src_card.lay.addWidget(self.detect_label)
        root.addWidget(src_card)

        # ---- 参数卡片 ----
        opt_card = Card("编码参数")
        self.fps = QDoubleSpinBox()
        self.fps.setRange(1, 240)
        self.fps.setValue(30.0)
        self.crf = QSpinBox()
        self.crf.setRange(0, 51)
        self.crf.setValue(18)
        self.crf.setToolTip("0=无损，18≈视觉无损，23=默认，28=高压缩")
        self.preset = QComboBox()
        for p in ("veryfast", "fast", "medium", "slow"):
            self.preset.addItem(p)
        self.preset.setCurrentText("medium")
        self.scale = QComboBox()
        self.scale.addItem("保持原始尺寸", None)
        self.scale.addItem("1920 × 1080", (1920, 1080))
        self.scale.addItem("1280 × 720", (1280, 720))
        self.scale.addItem("3840 × 2160", (3840, 2160))
        row = QHBoxLayout()
        row.addWidget(FieldRow("帧率", self.fps), 1)
        row.addWidget(FieldRow("CRF", self.crf), 1)
        row.addWidget(FieldRow("预设", self.preset), 1)
        opt_card.lay.addLayout(row)
        opt_card.lay.addWidget(FieldRow("分辨率", self.scale))

        self.out_file = PathPicker("输出视频文件…", is_file=True, save=True,
                                   file_filter="MP4 视频 (*.mp4)")
        opt_card.lay.addWidget(FieldRow("输出文件", self.out_file))
        root.addWidget(opt_card)

        # ---- 执行区 ----
        run_card = Card()
        btn_row = QHBoxLayout()
        self.run_btn = QPushButton("▶  开始合成")
        self.run_btn.setProperty("primary", True)
        self.run_btn.clicked.connect(self._run)
        self.stop_btn = QPushButton("取消")
        self.stop_btn.setProperty("danger", True)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._stop)
        btn_row.addWidget(self.run_btn)
        btn_row.addWidget(self.stop_btn)
        btn_row.addStretch(1)
        self.progress = QProgressBar()
        self.status = QLabel("就绪")
        self.status.setObjectName("pageDesc")
        run_card.lay.addLayout(btn_row)
        run_card.lay.addWidget(self.progress)
        run_card.lay.addWidget(self.status)
        root.addWidget(run_card)
        root.addStretch(1)

    # ----------------------------------------------------------
    def _detect(self):
        folder = Path(self.src.text())
        if not folder.is_dir():
            return
        pattern, count = detect_frame_pattern(folder)
        self._pattern = pattern
        self._frame_count = count
        if pattern:
            self.detect_label.setText(f"✅ 检测到 {count} 帧   ·   命名模式 {pattern}")
            if not self.out_file.text():
                self.out_file.setText(str(folder.parent / f"{folder.name}_out.mp4"))
        else:
            self.detect_label.setText("⚠ 未在该目录发现连续命名的帧图片（如 f_000001.png）")

    def _run(self):
        if not self.src.text():
            QMessageBox.warning(self, "缺少目录", "请先选择帧序列目录")
            return
        if not getattr(self, "_pattern", None):
            self._detect()
        if not getattr(self, "_pattern", None):
            QMessageBox.warning(self, "无帧序列", "该目录中没有可识别的帧序列")
            return
        out = self.out_file.text()
        if not out:
            QMessageBox.warning(self, "缺少输出", "请指定输出视频文件")
            return
        in_pattern = str(Path(self.src.text()) / self._pattern)
        args = build_compose_args(in_pattern, self.fps.value(), self.crf.value(),
                                  self.preset.currentText(), out,
                                  self.scale.currentData())
        self._set_running(True)
        self.status.setText(f"输出 → {out}")
        self._job = FFmpegJob(args=args, total_frames=self._frame_count)
        self._job.progressed.connect(self._on_progress)
        self._job.done.connect(self._on_done)
        self._job.start()

    def _stop(self):
        if self._job:
            self._job.stop()
        self.status.setText("正在取消…")

    def _on_progress(self, pct: int, text: str):
        self.progress.setValue(pct)
        self.status.setText(text)

    def _on_done(self, ok: bool, msg: str):
        self._set_running(False)
        self.progress.setValue(100 if ok else self.progress.value())
        self.status.setText(f"{'✅ ' if ok else '⚠ '}{msg}")

    def _set_running(self, running: bool):
        self.run_btn.setEnabled(not running)
        self.stop_btn.setEnabled(running)
