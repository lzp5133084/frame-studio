"""底部帮助面板：程序原理 / 使用说明 / 操作说明，可折叠。"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QButtonGroup, QFrame, QHBoxLayout, QLabel,
                               QPushButton, QTextBrowser, QVBoxLayout, QWidget)

_PRINCIPLE = """
<h3 style="color:#E9EDF5;">程序原理</h3>
<p style="color:#8B93A7; line-height:1.7;">
视频的本质 = <b style="color:#5B7CFF;">连续帧序列</b> + 音频 + 元数据。
传统剪辑软件直接在封装好的视频文件上操作，AI 难以介入每一帧；
本软件采用<b style="color:#E9EDF5;">帧级流水线</b>架构——先把视频完整解码为图片序列，
让每一帧都暴露给 AI 与图像算法，处理完毕再重新编码合成为视频。
</p>
<p style="color:#8B93A7; font-family:Consolas,monospace; background:#0C0F15; padding:10px 14px; border-radius:8px;">
视频文件 ──FFmpeg 解码──▶ 帧序列 ──AI 逐帧处理（补帧 / 擦除 / 水印）──▶ 帧序列 ──FFmpeg 编码──▶ 视频文件
</p>
<table style="color:#8B93A7;" cellspacing="6">
<tr><td style="color:#E9EDF5;"><b>界面层</b></td><td>界面框架（Qt 6 / PySide6）深色商用主题，左侧导航 + 页面堆栈</td></tr>
<tr><td style="color:#E9EDF5;"><b>媒体内核</b></td><td>内置 FFmpeg 9：探测视频信息、解码抽帧、H.264 编码合成</td></tr>
<tr><td style="color:#E9EDF5;"><b>AI 推理</b></td><td>本地模型（补帧 RIFE / 智能分割 SAM / 视频修复 ProPainter）与火山引擎云端服务可切换</td></tr>
<tr><td style="color:#E9EDF5;"><b>质量控制</b></td><td>PNG 无损中间帧 + 画质等级 CRF 18 近无损重编码，画质损失趋近于零</td></tr>
</table>
"""

_USAGE = """
<h3 style="color:#E9EDF5;">使用说明</h3>
<ul style="color:#8B93A7; line-height:1.8;">
<li><b style="color:#E9EDF5;">环境要求</b>：Windows 10/11；开发运行需 Python 3.10+ 与 <code>pip install -r requirements.txt</code>；媒体引擎 FFmpeg 已内置，无需安装</li>
<li><b style="color:#E9EDF5;">工作目录</b>：默认输出到程序目录下 <code>workspace/</code>，可在"设置"页修改</li>
<li><b style="color:#E9EDF5;">设置页</b>：可指定自定义 FFmpeg 路径；AI 推理模式（本地 / 云端 / 混合）；火山引擎密钥 ARK Key（云端模式必填）</li>
<li><b style="color:#E9EDF5;">推荐工作流</b>：① 抽帧提取 → ② 对帧序列做处理（后续 AI 模块）→ ③ 视频合成</li>
<li><b style="color:#E9EDF5;">画质建议</b>：中间帧用 PNG 无损格式；合成时画质等级 CRF 取 18（视觉无损），追求小体积再调到 23</li>
</ul>
"""

_GUIDE = """
<h3 style="color:#E9EDF5;">操作说明</h3>
<p style="color:#E9EDF5;"><b>🎞 抽帧提取</b>（视频 → 帧序列）</p>
<ol style="color:#8B93A7; line-height:1.8;">
<li>浏览选择源视频，自动显示时长 / 分辨率 / 帧率（帧/秒） / 总帧数</li>
<li>选抽取模式：<code>全部帧</code> 逐帧拆解｜<code>按帧率</code> 如 5 帧/秒 采样｜<code>按间隔</code> 如每 2 秒 1 帧｜<code>按动态程度</code> 剔除静止画面、只留关键帧</li>
<li>动态程度模式（录屏演示专用）：静止讲解自动剔除，鼠标移动 / 翻页 / 滚动等关键操作自动保留；灵敏度越高，渐变等轻微变化也会保留</li>
<li>选输出目录（默认 工作目录/frames_&lt;视频名&gt;），点 <b style="color:#5B7CFF;">开始抽帧</b>，可随时取消</li>
<li>点 <b style="color:#5B7CFF;">查看帧</b> 浏览抽出的帧：点击图片放大/还原，← → 切换前后帧，ESC 退出</li>
</ol>
<p style="color:#E9EDF5;"><b>🎬 帧序列合成</b>（帧序列 → MP4 / GIF / PPT）</p>
<ol style="color:#8B93A7; line-height:1.8;">
<li>选择帧目录，自动识别命名模式（f_%06d.png）与帧数</li>
<li>选输出格式：<code>MP4 视频</code>（画质等级 CRF / 编码速度 / 分辨率可调）｜<code>GIF 动图</code>（宽度可调，越小文件越小）｜<code>PPT 幻灯片</code>（每帧一页，适合步骤汇报）</li>
<li>帧率（与原视频一致可避免变速；PPT 不需要）</li>
<li>指定输出文件，点 <b style="color:#5B7CFF;">开始合成</b></li>
</ol>
<p style="color:#E9EDF5;"><b>⚠ 注意</b></p>
<ul style="color:#8B93A7; line-height:1.8;">
<li>帧序列断号（缺 f_000005.png 之类）会导致合成中断 —— v0.2 智能补帧将自动补齐缺口</li>
<li>任务进行中切换页面不影响后台执行；关闭窗口前请先取消或等待任务完成</li>
</ul>
"""

_TABS = [("程序原理", _PRINCIPLE), ("使用说明", _USAGE), ("操作说明", _GUIDE)]


class HelpPanel(QFrame):
    """底部可折叠帮助栏：标签切换 + 一键展开/收起。"""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("helpPanel")
        self.setStyleSheet(
            "#helpPanel { background:#10131B; border-top:1px solid #242C3D; }")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ---- 顶部 bar ----
        bar = QWidget()
        bl = QHBoxLayout(bar)
        bl.setContentsMargins(16, 0, 16, 0)
        bl.setSpacing(4)
        icon = QLabel("📖")
        icon.setFixedHeight(36)
        bl.addWidget(icon)

        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        for i, (name, html) in enumerate(_TABS):
            btn = QPushButton(name)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(
                "QPushButton { border:none; border-radius:6px; padding:5px 12px;"
                " color:#8B93A7; background:transparent; }"
                "QPushButton:hover { color:#E9EDF5; }"
                "QPushButton:checked { color:#E9EDF5; background:#1C2331; }")
            btn.clicked.connect(lambda _, idx=i: self._show_tab(idx))
            self._group.addButton(btn, i)
            bl.addWidget(btn)
        bl.addStretch(1)

        self._toggle = QPushButton("展开 ▲")
        self._toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self._toggle.setStyleSheet(
            "QPushButton { border:none; color:#8B93A7; background:transparent; }"
            "QPushButton:hover { color:#E9EDF5; }")
        self._toggle.clicked.connect(self._toggle_body)
        bl.addWidget(self._toggle)
        root.addWidget(bar)

        # ---- 内容区 ----
        self._body = QTextBrowser()
        self._body.setOpenExternalLinks(True)
        self._body.setMinimumHeight(180)
        self._body.setMaximumHeight(240)
        self._body.setVisible(False)
        root.addWidget(self._body)

        self._cur = 0
        self._group.button(0).setChecked(True)
        self._body.setHtml(_TABS[0][1])

    def _show_tab(self, idx: int):
        self._cur = idx
        self._body.setHtml(_TABS[idx][1])
        if not self._body.isVisible():
            self._toggle_body()

    def _toggle_body(self):
        show = not self._body.isVisible()
        self._body.setVisible(show)
        self._toggle.setText("收起 ▼" if show else "展开 ▲")
