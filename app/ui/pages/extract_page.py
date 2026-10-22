"""抽帧提取页：视频 → 帧序列。"""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QComboBox, QDoubleSpinBox, QHBoxLayout, QLabel,
                               QMessageBox, QProgressBar, QPushButton, QSlider,
                               QVBoxLayout, QWidget)

from ...core import settings
from ...core.ffmpeg import FFmpegJob, fmt_duration, fmt_size, probe_media
from ...core.paths import workspace_dir
from ...modules.jobs import M_ALL, M_FPS, M_INTERVAL, M_MOTION, build_extract_args
from ..terms import Term
from ..viewer import FrameViewer, collect_frames
from ..widgets import Card, FieldRow, PathPicker


class ExtractPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._job: FFmpegJob | None = None
        self._info: dict = {}

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)

        title = QLabel("抽帧提取")
        title.setObjectName("pageTitle")
        desc = QLabel("将视频拆解为逐帧图片序列，为单帧处理 / 补帧 / 擦除等后续工序提供输入")
        desc.setObjectName("pageDesc")
        root.addWidget(title)
        root.addWidget(desc)

        # ---- 源文件卡片 ----
        src_card = Card("源视频")
        self.src = PathPicker("选择视频文件…", is_file=True,
                              file_filter="视频文件 (*.mp4 *.mov *.mkv *.avi *.webm *.flv *.ts);;所有文件 (*)")
        self.src.edit.editingFinished.connect(self._refresh_info)
        src_card.lay.addWidget(FieldRow("视频文件", self.src))
        self.info_label = QLabel("未加载视频")
        self.info_label.setObjectName("pageDesc")
        src_card.lay.addWidget(self.info_label)
        root.addWidget(src_card)

        # ---- 参数卡片 ----
        opt_card = Card("抽取参数")
        self.mode = QComboBox()
        self.mode.addItem("全部帧（逐帧拆解）", M_ALL)
        self.mode.addItem("按帧率抽取（每秒帧数）", M_FPS)
        self.mode.addItem("按间隔抽取（秒/帧）", M_INTERVAL)
        self.mode.addItem("按动态程度（剔除静止画面）", M_MOTION)
        self.value = QDoubleSpinBox()
        self.value.setRange(0.1, 120)
        self.value.setValue(1.0)
        self.value.setSingleStep(0.5)
        self.value.setEnabled(False)

        # 灵敏度滑杆（动态程度模式专用）
        self.sens_box = QWidget()
        sl = QHBoxLayout(self.sens_box)
        sl.setContentsMargins(0, 0, 0, 0)
        sl.setSpacing(8)
        sl.addWidget(Term("灵敏度", "sensitivity"))
        self.sens = QSlider(Qt.Orientation.Horizontal)
        self.sens.setRange(0, 100)
        self.sens.setValue(70)
        self.sens_lab = QLabel("70")
        self.sens_lab.setObjectName("pageDesc")
        self.sens_lab.setFixedWidth(24)
        self.sens_lab.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.sens.valueChanged.connect(
            lambda v: self.sens_lab.setText(str(v)))
        sl.addWidget(self.sens, 1)
        sl.addWidget(self.sens_lab)
        self.sens_box.setVisible(False)

        self.mode.currentIndexChanged.connect(self._on_mode_change)
        self.fmt = QComboBox()
        self.fmt.addItem("PNG（无损，推荐）", "png")
        self.fmt.addItem("JPG（体积小）", "jpg")
        row = QHBoxLayout()
        row.addWidget(self.mode, 2)
        row.addWidget(self.value, 1)
        row.addWidget(self.sens_box, 1)
        row.addWidget(self.fmt, 2)
        opt_card.lay.addLayout(row)

        self.motion_hint = QLabel("自动剔除静止讲解画面，保留鼠标移动 / 翻页 / 滚动等关键操作；灵敏度越高，渐变等轻微变化也会保留")
        self.motion_hint.setObjectName("pageDesc")
        self.motion_hint.setVisible(False)
        opt_card.lay.addWidget(self.motion_hint)

        self.out_dir = PathPicker("输出目录（默认 工作目录/frames_<视频名>）…", is_file=False)
        opt_card.lay.addWidget(FieldRow("输出目录", self.out_dir))
        root.addWidget(opt_card)

        # ---- 执行区 ----
        run_card = Card()
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.status = QLabel("就绪")
        self.status.setObjectName("pageDesc")
        btn_row = QHBoxLayout()
        self.run_btn = QPushButton("▶  开始抽帧")
        self.run_btn.setProperty("primary", True)
        self.run_btn.clicked.connect(self._run)
        self.stop_btn = QPushButton("取消")
        self.stop_btn.setProperty("danger", True)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._stop)
        self.view_btn = QPushButton("🔍 查看帧")
        self.view_btn.setToolTip("浏览输出目录中的帧图片：点击放大，←→ 切换，ESC 退出")
        self.view_btn.clicked.connect(self._view_frames)
        btn_row.addWidget(self.run_btn)
        btn_row.addWidget(self.stop_btn)
        btn_row.addWidget(self.view_btn)
        btn_row.addStretch(1)
        run_card.lay.addLayout(btn_row)
        run_card.lay.addWidget(self.progress)
        run_card.lay.addWidget(self.status)
        root.addWidget(run_card)
        root.addStretch(1)

    # ----------------------------------------------------------
    def _on_mode_change(self):
        m = self.mode.currentData()
        self.value.setEnabled(m in (M_FPS, M_INTERVAL))
        self.value.setVisible(m != M_MOTION)
        self.sens_box.setVisible(m == M_MOTION)
        self.motion_hint.setVisible(m == M_MOTION)

    def _refresh_info(self):
        p = self.src.text()
        if not p or not Path(p).exists():
            return
        self._info = probe_media(p)
        if not self._info:
            self.info_label.setText("无法解析该文件（ffprobe 失败）")
            return
        i = self._info
        self.info_label.setText(
            f"时长 {fmt_duration(i['duration_ms'])}   ·   {i['width']}×{i['height']}   ·   "
            f"{i['fps']} 帧/秒   ·   约 {i['nb_frames']} 帧   ·   编码 {i['codec']}   ·   {fmt_size(i['size_bytes'])}")

    def _effective_outdir(self) -> Path:
        if self.out_dir.text():
            return Path(self.out_dir.text())
        stem = Path(self.src.text()).stem
        return workspace_dir() / f"frames_{stem}"

    def _run(self):
        video = self.src.text()
        if not video or not Path(video).exists():
            QMessageBox.warning(self, "缺少视频", "请先选择有效的视频文件")
            return
        if not self._info:
            self._refresh_info()
        out_dir = self._effective_outdir()
        out_dir.mkdir(parents=True, exist_ok=True)
        mode = self.mode.currentData()
        param = self.sens.value() if mode == M_MOTION else self.value.value()
        args, _ = build_extract_args(video, out_dir, mode, param,
                                     self.fmt.currentData(), "f_")
        total = self._info.get("nb_frames", 0)
        if mode == M_FPS and self.value.value() > 0 and self._info.get("fps"):
            total = int(total * self.value.value() / self._info["fps"])
        elif mode == M_INTERVAL and self.value.value() > 0:
            total = int(self._info.get("duration_ms", 0) / 1000 / self.value.value())
        elif mode == M_MOTION:
            total = 0  # 保留帧数取决于画面内容，无法预估

        self._set_running(True)
        # 动态模式帧数不可预知 → 进度条进入忙碌态
        self.progress.setRange(0, 0 if mode == M_MOTION else 100)
        self.status.setText(f"输出 → {out_dir}")
        self._job = FFmpegJob(args=args, total_frames=max(total, 0))
        self._job.progressed.connect(self._on_progress)
        self._job.done.connect(lambda ok, msg: self._on_done(ok, msg, out_dir))
        self._job.start()

    def _view_frames(self):
        out_dir = self._effective_outdir()
        if not out_dir.is_dir() or not collect_frames(out_dir):
            QMessageBox.information(self, "没有帧", "输出目录下还没有帧图片，请先执行抽帧")
            return
        FrameViewer(out_dir, self).exec()

    def _stop(self):
        if self._job:
            self._job.stop()
        self.status.setText("正在取消…")

    def _on_progress(self, pct: int, text: str):
        self.progress.setValue(pct)
        self.status.setText(text)

    def _on_done(self, ok: bool, msg: str, out_dir: Path):
        self._set_running(False)
        self.progress.setRange(0, 100)
        self.progress.setValue(100 if ok else self.progress.value())
        n = len(list(out_dir.glob("f_*"))) if out_dir.exists() else 0
        self.status.setText(f"{'✅ ' if ok else '⚠ '}{msg}   ·   已产出 {n} 个文件 → {out_dir}" if ok
                            else f"⚠ {msg}")

    def _set_running(self, running: bool):
        self.run_btn.setEnabled(not running)
        self.stop_btn.setEnabled(running)
