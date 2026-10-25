#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PySide6 复刻：WinUI / Windows App SDK NavigationView 的
汉堡按钮、返回按钮、设置（齿轮）按钮的按下/松开图标动画。

动画数值来自 Windows App SDK（microsoft-ui-xaml）源码中 LottieGen 生成的
Composition 关键帧（详见 调研.md），这里用 QPainter + 自定义时间线做近似复刻
（汉堡 / 返回的几何量各自动画，手绘；设置的齿轮直接用 Segoe Fluent Icons 的
\uE713 字形，由 FontIcon 控件负责原地旋转）：

- 汉堡：按下 150ms，三条杠水平收窄到 52%；松开 317ms，先过冲到 104.8% 再落回。
- 返回：按下 150ms，柄缩短、箭头随头部右移（右端圆帽几乎不动）；松开 317ms，越过静止位回弹。
- 设置：按下 150ms 转 -20°；松开 650ms 从 -20° 转到 360°（约一整圈）。

依赖：PySide6（必需）、Pillow（仅 --gif 模式需要）。

运行：
    python navview_buttons_pyside6.py

离屏渲染各状态快照（生成 window.png / window_open.png / states.png，不需要显示器）：
    python navview_buttons_pyside6.py --snapshot ./preview

生成动画 GIF 预览（需要 Pillow）：
    python navview_buttons_pyside6.py --gif ./preview/demo.gif
"""

from __future__ import annotations

import math
import os
import sys
import time

from PySide6.QtCore import (
    QEasingCurve,
    QParallelAnimationGroup,
    QPointF,
    QPropertyAnimation,
    QRectF,
    Qt,
    QTimer,
    QRect,
    Property,
    QPoint,
    QEvent
)
from PySide6.QtGui import QColor, QFont, QImage, QPainter, QPainterPath, QPalette, QPen, QPixmap
from PySide6.QtTest import QTest
from PySide6.QtWidgets import (
    QAbstractButton,
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
    QSizePolicy,
)

from typing import Optional

def set_style(widget, class_name: str):
    '''
    设置按钮的class属性并刷新样式
    '''
    # 1. 设置class属性
    widget.setProperty('class', class_name)

    # 2. 强制样式刷新
    widget.style().unpolish(widget)
    widget.style().polish(widget)

    # 3. 触发重绘
    widget.update()

_FONT_FAMILIES = ["Segoe Fluent Icons", "Segoe MDL2 Assets"]

class FontIcon(QLabel):
    """图标字体标签（Segoe Fluent Icons / Segoe MDL2 Assets），支持原地旋转。

    angle 属性可直接交给 QPropertyAnimation 做旋转动画。
    icon_color / icon_size 也可由 qss 用 qproperty-* 覆盖。

    配色由 qss 决定：默认取 `.FontIcon`（或全局文字色）的 color；
    需要单独配色的位置在 qss 里用自己的 class 声明 color（如 `.ExpanderArrow`），
    代码只在显式传入 color 时才把颜色写进控件自身样式表。

    字号通过「控件自身样式表」设置：全局样式表里的 `* { font-size: ... }`
    会覆盖 setFont()，但覆盖不了控件自身样式表，因此图标字号不会被带跑。

    示例：
        icon = FontIcon("\uE713", size=24)                    # 设置齿轮；颜色交给 qss 的 .FontIcon
        icon = FontIcon("\uE70D", size=12, color="#F7F7F7")   # 单独配色
        icon.set_angle(90)                                    # 原地旋转 90°
        # angle 是 Qt Property，可直接交给 QPropertyAnimation 做动画
    """

    STYLE_CLASS = "FontIcon"

    def __init__(self, icon="", size: int = 20, color: Optional[str] = None, parent=None):
        super().__init__(icon, parent)

        self._color = QColor(color) if color is not None else None
        self._icon_size = int(size)
        self._angle = 0.0
        self._pixmap = None
        self._pixmap_key = None

        self.setAlignment(Qt.AlignCenter)
        self.setMinimumWidth(0)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        self._apply_style()
        set_style(self, self.STYLE_CLASS)

    def _apply_style(self):
        """把字号写进控件自身样式表（优先级高于全局 `*` 规则）。

        只有显式指定颜色时才写入 color，否则交给 qss 的 `.FontIcon` 决定。
        """
        f = self.font()
        f.setPixelSize(self._icon_size)
        f.setFamilies(_FONT_FAMILIES)
        self.setFont(f)
        # 不在这里写 background：背景交给样式表按层级（level）决定
        css = f"font-size: {self._icon_size}px;"
        if self._color is not None:
            css += f" color: {self._color.name()};"
        self.setStyleSheet(css)
        self.updateGeometry()

    def _effective_color(self) -> QColor:
        """当前生效的图标颜色：显式颜色优先，否则取 qss 设置的前景色。"""
        if self._color is not None:
            return self._color
        return self.palette().color(self.foregroundRole())

    # --------------------------- 原地旋转 ---------------------------
    def get_angle(self) -> float:
        return self._angle

    def set_angle(self, angle: float):
        angle = float(angle)
        if angle != self._angle:
            self._angle = angle
            self.update()

    angle = Property(float, get_angle, set_angle)

    # --------------------------- 配色 / 字号 ---------------------------
    def get_icon_color(self) -> QColor:
        return self._effective_color()

    def set_icon_color(self, color):
        new_color = QColor(color) if color is not None else QColor()
        if not new_color.isValid():
            new_color = None
        if new_color != self._color:
            self._color = new_color
            # 旋转时由 _effective_color() 自绘；未旋转时 QLabel 取样式表的颜色
            self._apply_style()

    def get_icon_size(self) -> int:
        return self._icon_size

    def set_icon_size(self, size: int):
        size = int(size)
        if size != self._icon_size:
            self._icon_size = size
            self._apply_style()

    icon_color = Property(QColor, get_icon_color, set_icon_color)
    icon_size = Property(int, get_icon_size, set_icon_size)

    def _icon_pixmap(self) -> QPixmap:
        """先把图标按 0° 渲染成 pixmap，再整体旋转绘制。

        直接把文字交给旋转后的 painter 画，在部分平台上不会输出任何像素，
        因此这里始终先渲染成位图再旋转。
        """
        color = self._effective_color()
        dpr = self.devicePixelRatioF()
        key = (self.size(), self.text(), self.font().key(), color.rgba(), dpr)
        if self._pixmap is None or self._pixmap_key != key:
            pm = QPixmap(int(self.width() * dpr), int(self.height() * dpr))
            pm.setDevicePixelRatio(dpr)
            pm.fill(Qt.transparent)

            painter = QPainter(pm)
            painter.setRenderHint(QPainter.Antialiasing, True)
            painter.setRenderHint(QPainter.TextAntialiasing, True)
            painter.setPen(color)
            painter.setFont(self.font())
            painter.drawText(QRect(QPoint(0, 0), self.size()), Qt.AlignCenter, self.text())
            painter.end()

            self._pixmap = pm
            self._pixmap_key = key
        return self._pixmap

    def changeEvent(self, event):
        # 主题 / 样式变化会改变 qss 决定的颜色，缓存的旋转位图必须失效
        if event.type() in (QEvent.PaletteChange, QEvent.StyleChange, QEvent.FontChange):
            self._pixmap = None
            self._pixmap_key = None
        super().changeEvent(event)

    def paintEvent(self, event):
        # 未旋转时走 QLabel 默认绘制，保证与普通图标标签完全一致
        if self._angle % 360.0 == 0.0:
            super().paintEvent(event)
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        rect = QRectF(self.rect())
        painter.translate(rect.center())
        painter.rotate(self._angle)
        painter.translate(-rect.center())
        painter.drawPixmap(0, 0, self._icon_pixmap())

# ---------------------------------------------------------------------------
# 缓动函数：源码里的关键帧全部是 CSS 风格的 cubic-bezier(x1,y1,x2,y2)
# ---------------------------------------------------------------------------

def cubic_bezier(x1: float, y1: float, x2: float, y2: float):
    """返回 CSS cubic-bezier 缓动函数 f(t), t∈[0,1]。"""

    def f(t: float) -> float:
        if t <= 0.0:
            return 0.0
        if t >= 1.0:
            return 1.0
        # 二分求解 x(u) = t，再返回 y(u)
        lo, hi = 0.0, 1.0
        for _ in range(22):
            u = (lo + hi) * 0.5
            x = 3.0 * (1.0 - u) ** 2 * u * x1 + 3.0 * (1.0 - u) * u * u * x2 + u**3
            if x < t:
                lo = u
            else:
                hi = u
        u = (lo + hi) * 0.5
        return 3.0 * (1.0 - u) ** 2 * u * y1 + 3.0 * (1.0 - u) * u * u * y2 + u**3

    return f


LINEAR = cubic_bezier(0.0, 0.0, 1.0, 1.0)

# 按下：强 ease-out（Lottie 中所有 press 段共用的曲线）
EASE_PRESS = cubic_bezier(0.167, 0.167, 0.0, 1.0)
# 汉堡松开：先冲向过冲点，再落回
EASE_HAMMER_OUT = cubic_bezier(0.85, 0.0, 0.75, 1.0)
EASE_HAMMER_SETTLE = cubic_bezier(0.35, 0.0, 0.0, 1.0)
# 返回松开：柄与头部各用一条不同的回弹曲线
EASE_BACK_TIP = cubic_bezier(0.85, 0.0, 0.75, 1.0)
EASE_BACK_STEM = cubic_bezier(0.55, 0.0, 0.75, 1.0)
EASE_BACK_SETTLE = cubic_bezier(0.35, 0.0, 0.0, 1.0)
# 设置松开：cubic-bezier(0,0)-(0,1)，smoothstep 型的强 ease-out
EASE_GEAR_SPIN = cubic_bezier(0.0, 0.0, 0.0, 1.0)

# 三个按钮在 48×48 设计画布上的“正常态”参数
HAMBURGER_W = 44.75       # 三条杠的总宽（设计单位）
HAMBURGER_T = 2.75        # 杠的粗细
HAMBURGER_YS = (-13.75, 0.41, 13.75)   # 相对图标中心的 y（原设计为 10.25 / 24.4125 / 37.75）

BACK_TIP_X = -18.0        # 箭尖（设计画布 6 - 24）
BACK_NOTCH_X = -12.0      # 箭头内侧凹口（12 - 24）
BACK_STEM_RIGHT = 40.875  # 柄的右端（含圆帽圆心）
BACK_STEM_T = 2.25        # 柄的粗细 / 圆帽直径 2.25

# 设置图标不再手绘，直接用 Segoe Fluent Icons 的 Setting 字形（\uE713）。
# 字形墨迹几乎占满 em 框，因此按“设计画布上的齿轮外径 42.2 / 48”换算字号，
# 视觉尺寸与原来的手绘齿轮一致。
SETTINGS_GLYPH = "\uE713"
SETTINGS_GLYPH_RATIO = 42.2 / 48.0

ICON_COLOR = QColor("#ffffff")
ICON_COLOR_PRESSED = QColor("#cfcfcf")


# ---------------------------------------------------------------------------
# 通用动画按钮
# ---------------------------------------------------------------------------

class AnimatedIconButton(QAbstractButton):
    """三种按钮共用的“状态机 + 时间线”基类。

    状态：normal / pointerover / pressed
    时间线：按下、松开各自是一串 phase；每个 phase 对若干 track 做插值，
            每条 track 可以有自己的缓动曲线（对应 Lottie 中不同属性的关键帧）。

    绘制方式：
    - 汉堡 / 返回：按 Lottie 路径手绘（按下时各几何量独立变化，字体图标做不到）。
    - 设置：图标交给 FontIcon 子控件，用 Segoe Fluent Icons 的 \uE713 字形，
      而按下/松开只需要旋转，正好由 FontIcon 的 angle 属性承担。
    """

    def __init__(self, kind: str, icon_size: int = 28, button_size=(48, 44), parent=None):
        super().__init__(parent)
        assert kind in ("hamburger", "back", "settings")
        self._kind = kind
        self._icon_size = icon_size
        self.setFixedSize(*button_size)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setCursor(Qt.PointingHandCursor)
        self.setAttribute(Qt.WA_Hover, True)
        self.setAccessibleName({"hamburger": "菜单", "back": "返回", "settings": "设置"}[kind])

        self._hover = False
        self._pressed = False
        self._state = "normal"
        self._vals = self._default_vals()
        self._anim: dict | None = None

        # 设置按钮的图标：真实 Fluent 字形，只做原地旋转，交给 FontIcon
        self._glyph: FontIcon | None = None
        if kind == "settings":
            self._glyph = FontIcon(
                SETTINGS_GLYPH,
                size=self._glyph_size(),
                color=ICON_COLOR.name(),
                parent=self,
            )
            self._glyph.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            self._glyph.setGeometry(self.rect())
            self._sync_glyph()

        self._timer = QTimer(self)
        self._timer.setTimerType(Qt.PreciseTimer)
        self._timer.setInterval(15)
        self._timer.timeout.connect(self._tick)

    # -- 状态参数 ---------------------------------------------------------
    def _default_vals(self) -> dict:
        if self._kind == "hamburger":
            return {"wf": 1.0, "ty": 1.0}
        if self._kind == "back":
            return {"tip_dx": 0.0, "stem_right": BACK_STEM_RIGHT}
        return {"rot": 0.0}

    # -- 设置图标（FontIcon） ---------------------------------------------
    def _glyph_size(self) -> int:
        """齿轮字形的字号：让字形外径等于设计画布上原齿轮的外径。"""
        return max(1, int(round(self._icon_size * SETTINGS_GLYPH_RATIO)))

    def _sync_glyph(self) -> None:
        """把当前旋转角 / 配色同步给 FontIcon 子控件。"""
        if self._glyph is None:
            return
        self._glyph.set_angle(self._vals["rot"])
        color = ICON_COLOR_PRESSED if self._pressed else ICON_COLOR
        if self._glyph.get_icon_color() != color:
            self._glyph.set_icon_color(color)

    # -- 状态机 -----------------------------------------------------------
    def _refresh_state(self) -> None:
        new_state = "pressed" if self._pressed else ("pointerover" if self._hover else "normal")
        if new_state == self._state:
            return
        old_state, self._state = self._state, new_state
        if new_state == "pressed":
            self._play_press()
        elif old_state == "pressed":
            self._play_release()
        self._sync_glyph()
        self.update()

    def _play_press(self) -> None:
        if self._kind == "hamburger":
            self._start([(150.0, {"wf": EASE_PRESS, "ty": EASE_PRESS}, {"wf": 0.521, "ty": 1.0})])
        elif self._kind == "back":
            self._start(
                [
                    (
                        150.0,
                        {"tip_dx": EASE_PRESS, "stem_right": EASE_PRESS},
                        {"tip_dx": 9.0, "stem_right": 41.813},
                    )
                ]
            )
        else:
            # 按下旋转在源码中是线性曲线；从当前角度再转 -20°
            start = self._vals["rot"]
            self._start([(150.0, {"rot": LINEAR}, {"rot": start - 20.0})])

    def _play_release(self) -> None:
        if self._kind == "hamburger":
            self._start(
                [
                    (
                        133.0,
                        {"wf": EASE_HAMMER_OUT, "ty": EASE_HAMMER_OUT},
                        {"wf": 1.048, "ty": 0.9937},
                    ),
                    (
                        184.0,
                        {"wf": EASE_HAMMER_SETTLE, "ty": EASE_HAMMER_SETTLE},
                        {"wf": 1.0, "ty": 1.0},
                    ),
                ]
            )
        elif self._kind == "back":
            self._start(
                [
                    (
                        167.0,
                        {"tip_dx": EASE_BACK_TIP, "stem_right": EASE_BACK_STEM},
                        {"tip_dx": -4.016, "stem_right": 37.125},
                    ),
                    (
                        150.0,
                        {"tip_dx": EASE_BACK_SETTLE, "stem_right": EASE_BACK_SETTLE},
                        {"tip_dx": 0.0, "stem_right": BACK_STEM_RIGHT},
                    ),
                ]
            )
        else:
            # 从按下角（例如 -20°）转到 360°，即“完整转一圈”
            start = self._vals["rot"]
            target = 360.0 if start <= 0.0 else 360.0 * math.ceil(start / 360.0)
            self._start([(650.0, {"rot": EASE_GEAR_SPIN}, {"rot": target})], normalize_rotation=True)

    # -- 时间线 -----------------------------------------------------------
    def _start(self, phases, normalize_rotation: bool = False) -> None:
        self._anim = {
            "phases": phases,
            "i": 0,
            "t0": time.perf_counter(),
            "phase_from": dict(self._vals),
            "normalize_rotation": normalize_rotation,
        }
        self._timer.start()

    def _finish(self) -> None:
        anim, self._anim = self._anim, None
        self._timer.stop()
        if self._kind == "settings" and anim is not None and anim.get("normalize_rotation"):
            # 松开结束时 360° 与 0° 等价，归一化以便下一次按下重新从 0° 开始
            self._vals["rot"] = self._vals["rot"] % 360.0
        self._sync_glyph()
        self.update()

    def _tick(self) -> None:
        anim = self._anim
        if anim is None:
            return
        now = time.perf_counter()
        elapsed = (now - anim["t0"]) * 1000.0
        while anim["i"] < len(anim["phases"]):
            duration, eases, targets = anim["phases"][anim["i"]]
            if elapsed < duration:
                p = elapsed / duration
                for key, target in targets.items():
                    start = anim["phase_from"][key]
                    self._vals[key] = start + (target - start) * eases[key](p)
                self._sync_glyph()
                self.update()
                return
            # 当前 phase 结束
            self._vals.update(targets)
            elapsed -= duration
            anim["t0"] += duration / 1000.0
            anim["i"] += 1
            if anim["i"] < len(anim["phases"]):
                anim["phase_from"] = dict(self._vals)
        self._finish()

    # -- 鼠标 / 键盘 ------------------------------------------------------
    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self._pressed = True
            self._refresh_state()
            event.accept()

    def mouseReleaseEvent(self, event) -> None:
        if event.button() != Qt.LeftButton or not self._pressed:
            return
        self._pressed = False
        self._hover = self.rect().contains(event.position().toPoint())
        self._refresh_state()
        if self._hover:
            self.click()
        event.accept()

    def enterEvent(self, event) -> None:
        self._hover = True
        if not self._pressed:
            self._refresh_state()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._hover = False
        if not self._pressed:
            self._refresh_state()
        super().leaveEvent(event)

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key_Space and not event.isAutoRepeat():
            self._pressed = True
            self._refresh_state()
            event.accept()
            return
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event) -> None:
        if event.key() == Qt.Key_Space and not event.isAutoRepeat() and self._pressed:
            self._pressed = False
            self._refresh_state()
            self.click()
            event.accept()
            return
        super().keyReleaseEvent(event)

    # -- 绘制 -------------------------------------------------------------
    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)

        # 按钮底：hover / pressed 的淡白色叠加
        if self._pressed:
            painter.fillRect(self.rect(), QColor(255, 255, 255, 16))
        elif self._hover:
            painter.fillRect(self.rect(), QColor(255, 255, 255, 24))

        if self._kind == "settings":
            # 设置图标是 FontIcon 子控件，由它自己按 angle 绘制（含旋转）
            return

        painter.translate(self.width() / 2.0, self.height() / 2.0)
        scale = self._icon_size / 48.0
        painter.scale(scale, scale)

        color = ICON_COLOR_PRESSED if self._pressed else ICON_COLOR
        if self._kind == "hamburger":
            self._paint_hamburger(painter, color)
        else:
            self._paint_back(painter, color)

    def _paint_hamburger(self, painter: QPainter, color: QColor) -> None:
        width = HAMBURGER_W * self._vals["wf"]
        thickness = HAMBURGER_T * self._vals["ty"]
        painter.setPen(Qt.NoPen)
        painter.setBrush(color)
        radius = thickness / 2.0
        for y in HAMBURGER_YS:
            rect = QRectF(-width / 2.0, y - thickness / 2.0, width, thickness)
            painter.drawRoundedRect(rect, radius, radius)

    def _paint_back(self, painter: QPainter, color: QColor) -> None:
        dx = self._vals["tip_dx"]
        stem_right = self._vals["stem_right"] - 24.0
        stem_left = BACK_NOTCH_X + dx

        # 箭头头部：按原 Lottie 路径（Geometry_2）的轮廓折算到 48 画布坐标后填充
        # 外尖 (-18,0)，两臂末端 (-1.88,±15.45)，内侧凹口 (-12,±1.13)
        head_points = [
            (-1.88, 15.45),
            (-0.37, 13.79),
            (-14.24, 1.12),
            (-11.99, 1.10),
            (-11.99, -1.15),
            (-14.24, -1.13),
            (-0.37, -13.79),
            (-1.88, -15.45),
            (-17.44, -1.25),
            (BACK_TIP_X, 0.0),
            (-17.44, 1.25),
        ]
        head = QPainterPath(QPointF(head_points[0][0] + dx, head_points[0][1]))
        for x, y in head_points[1:]:
            head.lineTo(QPointF(x + dx, y))
        head.closeSubpath()

        painter.setPen(Qt.NoPen)
        painter.setBrush(color)
        painter.drawPath(head)

        # 柄：从凹口处向右画一条直线，右端补一个圆帽
        pen = QPen(color, BACK_STEM_T)
        pen.setCapStyle(Qt.FlatCap)
        painter.setPen(pen)
        painter.drawLine(QPointF(stem_left, 0.0), QPointF(stem_right, 0.0))

        painter.setPen(Qt.NoPen)
        radius = BACK_STEM_T / 2.0
        painter.drawEllipse(QPointF(stem_right, 0.0), radius, radius)

    def resizeEvent(self, event) -> None:
        # 设置图标铺满按钮，旋转中心与按钮中心重合
        if self._glyph is not None:
            self._glyph.setGeometry(self.rect())
        super().resizeEvent(event)

    # -- 快照辅助 ---------------------------------------------------------
    def preview(self, overrides: dict) -> None:
        """停止动画并直接设置视觉参数（用于离屏截图）。"""
        self._timer.stop()
        self._anim = None
        self._pressed = False
        self._hover = False
        self._state = "normal"
        self._vals = self._default_vals()
        self._vals.update(overrides)
        self._sync_glyph()
        self.update()


# ---------------------------------------------------------------------------
# 演示窗口
# ---------------------------------------------------------------------------

PANE_CLOSED = 48
PANE_OPEN = 320


class DemoWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 复刻 · NavigationView 汉堡 / 返回 / 设置按钮动画")
        self.resize(960, 580)
        self._pane_open = False

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # 左侧栏 ----------------------------------------------------------
        self.pane = QFrame(self)
        self.pane.setObjectName("pane")
        self.pane.setFixedWidth(PANE_CLOSED)
        pane_layout = QVBoxLayout(self.pane)
        pane_layout.setContentsMargins(4, 4, 4, 4)
        pane_layout.setSpacing(4)

        top_row = QHBoxLayout()
        top_row.setSpacing(4)
        self.hamburger = AnimatedIconButton("hamburger", icon_size=18, button_size=(38, 38), parent=self.pane)
        self.pane_title = QLabel("导航", self.pane)
        self.pane_title.setObjectName("paneTitle")
        self.pane_title.setVisible(False)
        top_row.addWidget(self.hamburger)
        top_row.addWidget(self.pane_title)
        top_row.addStretch(1)
        pane_layout.addLayout(top_row)

        self.back = AnimatedIconButton("back", icon_size=18, button_size=(38, 38), parent=self.pane)
        pane_layout.addWidget(self.back)
        pane_layout.addStretch(1)

        self.settings = AnimatedIconButton("settings", icon_size=18, button_size=(38, 38), parent=self.pane)
        pane_layout.addWidget(self.settings)

        # 右侧内容 --------------------------------------------------------
        content = QWidget(self)
        content.setObjectName("content")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(36, 30, 36, 26)
        content_layout.setSpacing(14)

        title = QLabel("侧边栏按钮图标动画（PySide6 近似复刻）", content)
        title.setObjectName("title")
        subtitle = QLabel(
            "数据来自 Windows App SDK / WinUI 3 源码中 LottieGen 生成的 Composition 关键帧。"
            "按住按钮观察按下动画，松开观察回弹与旋转。",
            content,
        )
        subtitle.setObjectName("subtitle")
        subtitle.setWordWrap(True)

        hints = QLabel(
            "• 汉堡按钮：按下 150 ms 收窄到 55%，松开 317 ms 先过冲再落回；同时开合左侧面板。\n"
            "• 返回按钮：按下 150 ms 柄缩短、箭头向右压缩（右端基本不动）；松开 317 ms 越过原位回弹。\n"
            "• 设置按钮：按下 150 ms 转 −20°；松开 650 ms 从 −20° 转到 360°（约一整圈）。\n"
            "• 悬停只改变按钮底色，图标本身不移动（与源码一致）。",
            content,
        )
        hints.setObjectName("hint")
        hints.setWordWrap(True)

        self.status = QLabel("侧边栏：收起", content)
        self.status.setObjectName("status")

        footer = QLabel(
            "动画参数：AnimatedGlobalNavigationButtonVisualSource / AnimatedBackVisualSource / "
            "AnimatedSettingsVisualSource（Windows App SDK 源码）· 本程序为演示用近似实现",
            content,
        )
        footer.setObjectName("footer")
        footer.setWordWrap(True)

        content_layout.addWidget(title)
        content_layout.addWidget(subtitle)
        content_layout.addSpacing(8)
        content_layout.addWidget(hints)
        content_layout.addSpacing(10)
        content_layout.addWidget(self.status)
        content_layout.addStretch(1)
        content_layout.addWidget(footer)

        root.addWidget(self.pane, 0)
        root.addWidget(content, 1)

        self.setStyleSheet(
            """
            QWidget#content { background: #1f1f1f; }
            QFrame#pane { background: #272727; border-right: 1px solid #383838; }
            QLabel { color: #e8e8e8; }
            QLabel#title { font-size: 21px; font-weight: 600; color: #ffffff; }
            QLabel#subtitle { color: #a9a9a9; font-size: 13px; }
            QLabel#hint { color: #c6c6c6; font-size: 13px; }
            QLabel#status { color: #8ab4f8; font-size: 13px; }
            QLabel#paneTitle { color: #f0f0f0; font-size: 13px; font-weight: 600; }
            QLabel#footer { color: #7a7a7a; font-size: 11px; }
            """
        )

        # 侧边栏宽度动画
        self._pane_group = QParallelAnimationGroup(self)
        self._pane_min = QPropertyAnimation(self.pane, b"minimumWidth", self)
        self._pane_max = QPropertyAnimation(self.pane, b"maximumWidth", self)
        for anim in (self._pane_min, self._pane_max):
            anim.setDuration(220)
            anim.setEasingCurve(QEasingCurve.OutCubic)
            self._pane_group.addAnimation(anim)

        self.hamburger.clicked.connect(self._toggle_pane)
        self.back.clicked.connect(lambda: self.status.setText("返回按钮被点击（演示）"))
        self.settings.clicked.connect(lambda: self.status.setText("设置按钮被点击（演示）"))

    def _toggle_pane(self) -> None:
        self._pane_open = not self._pane_open
        target = PANE_OPEN if self._pane_open else PANE_CLOSED
        self.pane_title.setVisible(self._pane_open)
        self.status.setText("侧边栏：展开" if self._pane_open else "侧边栏：收起")
        self._pane_group.stop()
        for anim in (self._pane_min, self._pane_max):
            anim.setStartValue(self.pane.width())
            anim.setEndValue(target)
        self._pane_group.start()


# ---------------------------------------------------------------------------
# 离屏快照（--snapshot）
# ---------------------------------------------------------------------------

SNAPSHOT_ROWS = [
    (
        "hamburger",
        "汉堡",
        "按下 150ms / 松开 317ms",
        [("正常", {}), ("按下", {"wf": 0.521}), ("松开过冲", {"wf": 1.048, "ty": 0.9937}), ("回位", {})],
    ),
    (
        "back",
        "返回",
        "按下 150ms / 松开 317ms",
        [
            ("正常", {}),
            ("按下", {"tip_dx": 9.0, "stem_right": 41.813}),
            ("松开过冲", {"tip_dx": -4.016, "stem_right": 37.125}),
            ("回位", {}),
        ],
    ),
    (
        "settings",
        "设置",
        "按下 150ms / 松开 650ms",
        [("正常", {"rot": 0.0}), ("按下", {"rot": -20.0}), ("松开中段", {"rot": 180.0}), ("回位", {"rot": 360.0})],
    ),
]


def _pixmap_to_pil(pixmap: QPixmap):
    from PIL import Image

    image = pixmap.toImage().convertToFormat(QImage.Format_RGBA8888)
    width, height = image.width(), image.height()
    stride = image.bytesPerLine()
    data = image.bits().tobytes()
    if stride != width * 4:
        data = b"".join(data[y * stride : y * stride + width * 4] for y in range(height))
    return Image.frombytes("RGBA", (width, height), data).convert("RGB")


class GifBoard(QWidget):
    """给 GIF 预览用的三按钮面板。"""

    def __init__(self):
        super().__init__()
        self.setFixedSize(620, 250)
        self.setStyleSheet("background: #1f1f1f;")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(24)
        self.buttons = {}
        specs = [
            ("hamburger", "汉堡", "按下 150 ms / 松开 317 ms"),
            ("back", "返回", "按下 150 ms / 松开 317 ms"),
            ("settings", "设置", "按下 150 ms / 松开 650 ms"),
        ]
        for kind, title, subtitle in specs:
            column = QVBoxLayout()
            column.setSpacing(4)
            button = AnimatedIconButton(kind, icon_size=88, button_size=(150, 130), parent=self)
            title_label = QLabel(title, self)
            title_label.setAlignment(Qt.AlignHCenter)
            title_label.setStyleSheet("color:#f0f0f0; font-size:13px; font-weight:600;")
            subtitle_label = QLabel(subtitle, self)
            subtitle_label.setAlignment(Qt.AlignHCenter)
            subtitle_label.setStyleSheet("color:#8f8f8f; font-size:10px;")
            column.addWidget(button, 0, Qt.AlignHCenter)
            column.addWidget(title_label)
            column.addWidget(subtitle_label)
            layout.addLayout(column)
            self.buttons[kind] = button


def make_gif(path: str) -> None:
    board = GifBoard()
    board.show()
    QApplication.processEvents()
    frames = []

    def snap() -> None:
        QApplication.processEvents()
        frames.append(_pixmap_to_pil(board.grab()))

    snap()
    snap()
    for kind, release_ms in (("hamburger", 317), ("back", 317), ("settings", 650)):
        button = board.buttons[kind]
        # 按下
        button._pressed = True
        button._refresh_state()
        for _ in range(max(2, 150 // 33)):
            snap()
            QTest.qWait(33)
        # 松开（回弹 / 旋转）
        button._pressed = False
        button._hover = True
        button._refresh_state()
        for _ in range(max(3, release_ms // 33)):
            snap()
            QTest.qWait(33)
        button._hover = False
        button._refresh_state()
        for _ in range(6):
            snap()
            QTest.qWait(33)

    from PIL import Image

    pal_frames = [frame.quantize(colors=128) for frame in frames]
    pal_frames[0].save(
        path,
        save_all=True,
        append_images=pal_frames[1:],
        duration=33,
        loop=0,
        optimize=True,
        disposal=2,
    )
    print(f"gif written: {os.path.abspath(path)}  ({len(frames)} frames, {Image.open(path).size[0]}x{Image.open(path).size[1]})")



def make_snapshots(out_dir: str) -> None:
    os.makedirs(out_dir, exist_ok=True)

    # 主窗口
    window = DemoWindow()
    window.resize(960, 580)
    window.show()
    QApplication.processEvents()
    window.grab().save(os.path.join(out_dir, "window.png"))

    # 展开侧边栏后的主窗口
    window._toggle_pane()
    QTest.qWait(320)
    window.grab().save(os.path.join(out_dir, "window_open.png"))
    window._toggle_pane()
    QTest.qWait(320)

    # 状态拼图
    cell_w, cell_h = 160, 190
    left = 150
    top = 84
    width = left + cell_w * 4 + 24
    height = top + cell_h * len(SNAPSHOT_ROWS) + 20
    pixmap = QPixmap(width, height)
    pixmap.fill(QColor("#1f1f1f"))

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing, True)
    painter.setRenderHint(QPainter.TextAntialiasing, True)

    painter.setPen(QColor("#ffffff"))
    title_font = QFont("Microsoft YaHei UI", 15)
    title_font.setBold(True)
    painter.setFont(title_font)
    painter.drawText(24, 36, "三种按钮的状态快照（数值取自 Lottie 关键帧）")

    label_font = QFont("Microsoft YaHei UI", 10)
    painter.setFont(label_font)
    painter.setPen(QColor("#bdbdbd"))
    column_titles = [item[0] for item in SNAPSHOT_ROWS[0][3]]
    for col, caption in enumerate(column_titles):
        x = left + col * cell_w
        painter.drawText(QRectF(x, top - 26, cell_w, 22), Qt.AlignHCenter | Qt.AlignVCenter, caption)

    for row, (kind, row_title, durations, states) in enumerate(SNAPSHOT_ROWS):
        y = top + row * cell_h
        painter.setPen(QColor("#ffffff"))
        row_font = QFont("Microsoft YaHei UI", 12)
        row_font.setBold(True)
        painter.setFont(row_font)
        painter.drawText(QRectF(20, y + 50, 120, 24), Qt.AlignLeft | Qt.AlignVCenter, row_title)
        painter.setPen(QColor("#8f8f8f"))
        painter.setFont(QFont("Microsoft YaHei UI", 9))
        painter.drawText(QRectF(20, y + 76, 120, 40), Qt.TextWordWrap, durations)

        for col, (caption, overrides) in enumerate(states):
            button = AnimatedIconButton(kind, icon_size=64, button_size=(104, 104))
            button.preview(overrides)
            button.resize(104, 104)
            button.setAttribute(Qt.WA_TranslucentBackground, True)
            shot = QPixmap(104, 104)
            shot.fill(QColor("#1f1f1f"))
            button.render(shot)
            x = left + col * cell_w + (cell_w - 104) // 2
            painter.drawPixmap(x, y, shot)
            painter.setPen(QColor("#c9c9c9"))
            painter.setFont(QFont("Microsoft YaHei UI", 10))
            painter.drawText(QRectF(left + col * cell_w, y + 114, cell_w, 20), Qt.AlignHCenter, caption)
            button.deleteLater()

    painter.end()
    pixmap.save(os.path.join(out_dir, "states.png"))

    print(f"snapshots written to: {os.path.abspath(out_dir)}")
    print("  - window.png / window_open.png")
    print("  - states.png")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def _apply_app_style(app: QApplication) -> None:
    palette = app.palette()
    for role in (QPalette.Window, QPalette.Base):
        palette.setColor(role, QColor("#1f1f1f"))
    palette.setColor(QPalette.WindowText, QColor("#e8e8e8"))
    palette.setColor(QPalette.Text, QColor("#e8e8e8"))
    app.setPalette(palette)
    app.setFont(QFont("Microsoft YaHei UI", 10))


def main() -> int:
    mode = None
    target = None
    args = sys.argv[1:]
    if args and args[0] == "--snapshot":
        mode, target = "snapshot", (args[1] if len(args) > 1 else "preview")
    elif args and args[0] == "--gif":
        mode, target = "gif", (args[1] if len(args) > 1 else "demo.gif")

    if mode:
        # 离屏渲染：--snapshot / --gif 都不需要真实显示器
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        # offscreen 插件默认找 PySide6/lib/fonts，这里指向 Windows 字体目录
        os.environ.setdefault("QT_QPA_FONTDIR", os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts"))

    app = QApplication(sys.argv)
    app.setApplicationName("NavigationView button animations (PySide6)")
    _apply_app_style(app)

    if mode == "snapshot":
        make_snapshots(target)
        return 0
    if mode == "gif":
        make_gif(target)
        return 0

    window = DemoWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
