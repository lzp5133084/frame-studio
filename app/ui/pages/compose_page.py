"""视频合成页：帧序列 → 视频 / GIF / PPT。"""
from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (QComboBox, QDoubleSpinBox, QHBoxLayout, QLabel,
                               QMessageBox, QProgressBar, QPushButton, QSpinBox,
                               QVBoxLayout, QWidget)

from ...core.ffmpeg import FFmpegChain, FFmpegJob
from ...modules.jobs import (build_compose_args, build_gif_args,
                             detect_frame_pattern)
from ...modules.pptx_export import PptxJob
from ..terms import Term
from ..viewer import FrameViewer, collect_frames
from ..widgets import Card, FieldRow, PathPicker


class ComposePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._job: FFmpegJob | None = None
        self._frame_count = 0

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)

        title = QLabel("帧序列合成")
        title.setObjectName("pageTitle")
        desc = QLabel("将处理后的帧序列合成为 MP4 视频 / GIF 动图 / PPT 幻灯片")
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
        opt_card = Card("合成参数")

        # 输出格式（控制下方参数的显示）
        fmt_row = QHBoxLayout()
        self.out_fmt = QComboBox()
        self.out_fmt.addItem("MP4 视频（H.264，通用播放）", "mp4")
        self.out_fmt.addItem("GIF 动图（网页/聊天分享）", "gif")
        self.out_fmt.addItem("PPT 幻灯片（每帧一页，汇报演示）", "pptx")
        self.out_fmt.currentIndexChanged.connect(self._on_fmt_change)
        self.gif_width = QSpinBox()
        self.gif_width.setRange(0, 3840)
        self.gif_width.setValue(480)
        self.gif_width.setSingleStep(40)
        self.gif_width.setSpecialValueText("原始宽度")
        self.gif_width.setToolTip("GIF 画面宽度，高度按比例自动；越小文件越小")
        self._row_gifw = FieldRow("GIF 宽度", self.gif_width)
        self._row_gifw.setVisible(False)
        fmt_row.addWidget(FieldRow("输出格式", self.out_fmt), 2)
        fmt_row.addWidget(self._row_gifw, 1)
        opt_card.lay.addLayout(fmt_row)

        self.fps = QDoubleSpinBox()
        self.fps.setRange(1, 240)
        self.fps.setValue(30.0)
        self.crf = QSpinBox()
        self.crf.setRange(0, 51)
        self.crf.setValue(18)
        self.crf.setToolTip("0=无损，18≈视觉无损，23=默认，28=高压缩")
        self.preset = QComboBox()
        for label, key in (("极快", "veryfast"), ("较快", "fast"),
                           ("标准（推荐）", "medium"), ("较慢（更省体积）", "slow")):
            self.preset.addItem(label, key)
        self.preset.setCurrentIndex(2)
        self.scale = QComboBox()
        self.scale.addItem("保持原始尺寸", None)
        self.scale.addItem("1920 × 1080", (1920, 1080))
        self.scale.addItem("1280 × 720", (1280, 720))
        self.scale.addItem("3840 × 2160", (3840, 2160))
        row = QHBoxLayout()
        self._row_fps = FieldRow(Term("帧率", "fps"), self.fps)
        self._row_crf = FieldRow(Term("画质等级", "crf"), self.crf)
        self._row_preset = FieldRow(Term("编码速度", "preset"), self.preset)
        row.addWidget(self._row_fps, 1)
        row.addWidget(self._row_crf, 1)
        row.addWidget(self._row_preset, 1)
        opt_card.lay.addLayout(row)
        self._row_scale = FieldRow("分辨率", self.scale)
        opt_card.lay.addWidget(self._row_scale)

        self.out_file = PathPicker("输出文件…", is_file=True, save=True,
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
        self.view_btn = QPushButton("🔍 查看帧")
        self.view_btn.clicked.connect(self._view_frames)
        btn_row.addWidget(self.run_btn)
        btn_row.addWidget(self.stop_btn)
        btn_row.addWidget(self.view_btn)
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
    def _on_fmt_change(self):
        fmt = self.out_fmt.currentData()
        self._row_crf.setVisible(fmt == "mp4")
        self._row_preset.setVisible(fmt == "mp4")
        self._row_scale.setVisible(fmt == "mp4")
        self._row_fps.setVisible(fmt != "pptx")
        self._row_gifw.setVisible(fmt == "gif")
        self.out_file.edit.setPlaceholderText(f"输出文件（.{fmt}）…")
        # 已填输出路径 → 自动换成对应后缀
        cur = self.out_file.text()
        if cur:
            self.out_file.setText(str(Path(cur).with_suffix(f".{fmt}")))
        self.run_btn.setText({"mp4": "▶  开始合成", "gif": "▶  生成 GIF",
                              "pptx": "▶  生成 PPT"}[fmt])

    def _default_out(self, folder: Path) -> Path:
        fmt = self.out_fmt.currentData()
        return folder.parent / f"{folder.name}_out.{fmt}"

    def _view_frames(self):
        folder = Path(self.src.text())
        if not folder.is_dir() or not collect_frames(folder):
            QMessageBox.information(self, "没有帧", "该目录下没有可查看的图片帧")
            return
        FrameViewer(folder, self).exec()

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
                self.out_file.setText(str(self._default_out(folder)))
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
            QMessageBox.warning(self, "缺少输出", "请指定输出文件")
            return
        in_pattern = str(Path(self.src.text()) / self._pattern)
        fmt = self.out_fmt.currentData()

        self._palette = None
        if fmt == "mp4":
            args = build_compose_args(in_pattern, self.fps.value(), self.crf.value(),
                                      self.preset.currentData(), out,
                                      self.scale.currentData())
            self._job = FFmpegJob(args=args, total_frames=self._frame_count)
        elif fmt == "gif":
            palette = str(Path(out).parent / "_palette_tmp.png")
            self._palette = Path(palette)
            s1, s2 = build_gif_args(in_pattern, self.fps.value(),
                                    self.gif_width.value(), out, palette)
            self._job = FFmpegChain(steps=[(s1, self._frame_count), (s2, self._frame_count)],
                                    step_names=["生成调色板", "合成 GIF"])
        else:  # pptx
            frames = collect_frames(Path(self.src.text()))
            if not frames:
                QMessageBox.warning(self, "无帧", "该目录下没有图片帧")
                return
            self._job = PptxJob(frames, out, self)

        self._set_running(True)
        self.status.setText(f"输出 → {out}")
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
        # 清理 GIF 调色板临时文件
        pal = getattr(self, "_palette", None)
        if pal is not None:
            try:
                pal.unlink(missing_ok=True)
            except Exception:
                pass
            self._palette = None
        self.status.setText(f"{'✅ ' if ok else '⚠ '}{msg}")

    def _set_running(self, running: bool):
        self.run_btn.setEnabled(not running)
        self.stop_btn.setEnabled(running)
