#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PySide6 NavigationView：统一托管窗口加载的侧边栏导航组件。

特性：
- 顶层窗口：``class DemoWindow(NavigationView)`` 即可使用。
- 菜单项 / 折叠菜单 / 分隔描述符 / 1px 分隔线 / 内置设置项。
- Auto / Expanded / Compact / ForceCompact / Hide 五种形态，内联与 Flyout 两种展开方式。
- 250ms 侧边栏展开收起、折叠箭头、内容上滑、指示器两段位移、胶囊滚动条。
- 指示器 2×16，贴着菜单行左边界，与 fonticon 间距 10px。
- 内容区使用 glasskit 的 ``BUBBLE_BACKGROUND_NORMAL`` 全窗口玻璃。
- 侧边栏与 Flyout 使用 glasskit 玻璃材质；窄模式子菜单独立浮窗（220px 宽、
  内容 212px、8px 圆角），左边界位于主窗口左边界右侧 50px，并随主窗口移动。
- 配色、圆角、指示器尺寸可通过 ``NavigationView`` 的 ``qproperty-*`` 覆盖，
  默认值集中在 :data:`THEME_DEFAULTS`；Demo 的 QSS 见 :data:`DEMO_QSS`。

依赖：PySide6、expander.py（图标控件）、glasskit/（玻璃材质）。
"""

from __future__ import annotations

import math
import sys
import time
import warnings
from enum import Enum, auto
from typing import Callable

from PySide6.QtCore import (
    QAbstractAnimation,
    QEasingCurve,
    QEvent,
    QObject,
    QPoint,
    QPointF,
    QPropertyAnimation,
    QParallelAnimationGroup,
    QRect,
    QRectF,
    QSize,
    Qt,
    QTimer,
    QVariantAnimation,
    Property,
    Signal,
)
from PySide6.QtGui import (
    QColor,
    QFont,
    QFontMetrics,
    QImage,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
)
from PySide6.QtWidgets import (
    QAbstractButton,
    QApplication,
    QFrame,
    QLabel,
    QLayout,
    QScrollArea,
    QScrollBar,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from expander import FontIcon, fonticon
from glasskit import (
    BUBBLE_BACKGROUND_NORMAL,
    BUBBLE_SIDEBAR_NORMAL,
    FrostStyle,
    blur_qimage,
    paint_frost_overlay,
    rounded_path,
)
from glasskit.glass import GlassWindowBase


# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

APP_FONT = "Microsoft YaHei UI"

COMPACT_WIDTH = 48
EXPANDED_WIDTH = 312
ROW_HEIGHT = 36
ROW_MARGIN_X = 4
ROW_MARGIN_TOP = 4
TOP_INDENT = 16
CHILD_INDENT = 36

ICON_SIZE = 16
ICON_GAP = 18
TEXT_SIZE = 14
ARROW_SIZE = 12
ARROW_GLYPH = "\uE70D"

SEPARATOR_COLOR = "#cccccc"
SEPARATOR_SIZE = 12
SEPARATOR_TOP = 14
SEPARATOR_BOTTOM = 12

INDICATOR_COLOR = "#99ebff"
INDICATOR_W = 2
INDICATOR_H = 16
INDICATOR_GAP = 10
#: 指示器左边界贴着菜单行（按钮）左边界；菜单行左边距即 ROW_MARGIN_X。
INDICATOR_INSET = ROW_MARGIN_X
#: 图标相对按钮左边界的位置 = 指示器宽度 + 与 fonticon 的 10px 间距。
ROW_ICON_INDENT = INDICATOR_W + INDICATOR_GAP

ANIM_MS = 250
INDICATOR_STEP_MS = 125
SCROLLBAR_MS = 250
SCROLLBAR_MIN = 2
SCROLLBAR_MAX = 5
SCROLLBAR_HIT = 6
SCROLLBAR_COLOR = "#9f9f9f"

SELECTED_BG = "#2d2d2d"
SELECTED_HOVER_BG = "#292929"
SELECTED_PRESSED_BG = "#2d2d2d"
HOVER_BG = "#2d2d2d"
PRESSED_BG = "#292929"
TEXT_COLOR = "#ffffff"
PRESSED_TEXT = "#cfcfcf"

CORNER_RADIUS = 4
HEADER_BUTTON_SIZE = (36, 32)
HEADER_MARGIN = 4
SHADOW_MARGIN = 24
FLYOUT_OFFSET_X = 50
#: 折叠项子菜单 Flyout 的尺寸：整宽 220，左右各 4px Padding，内容宽 212。
FLYOUT_WIDTH = 220
FLYOUT_RADIUS = 8
FLYOUT_ITEM_RADIUS = 4
FLYOUT_ROW_HEIGHT = 40
FLYOUT_ITEM_GAP = 4
FLYOUT_PADDING_X = 4
FLYOUT_PADDING_Y = 6
FLYOUT_CONTENT_MARGIN = 12
HISTORY_LIMIT = 16
SETTINGS_GLYPH = "\uE713"
SETTINGS_DIVIDER_COLOR = "#313131"
SETTINGS_DIVIDER_HEIGHT = 1
SETTINGS_BOTTOM_MARGIN = 6
GEAR_PRESS_MS = 150
GEAR_SPIN_MS = 650

#: 侧边栏常态玻璃。
SIDEBAR_GLASS = BUBBLE_SIDEBAR_NORMAL.copy()

#: Flyout 玻璃：取自 glassdemo.py 的参数，圆角改为 4px。
FLYOUT_GLASS = FrostStyle(
    tint="#2e2e2e",
    opacity=58,
    blur=40,
    frost=18,
    noise=6,
    sheen=14,
    saturation=95,
    brightness=105,
    border=24,
    radius=4,
    vignette=6,
)

#: 折叠项子菜单 Flyout 专用玻璃。
FLYOUT_FOLD_GLASS = FrostStyle(
    tint="#202020",
    opacity=65,
    blur=30,
    frost=4,
    noise=2,
    sheen=3,
    saturation=95,
    brightness=105,
    border=24,
    radius=4,
    vignette=6,
)

#: 主题默认值：QSS 可通过 ``qproperty-*`` 覆盖，未覆盖时使用这里的配置。
THEME_DEFAULTS = {
    "selectedBg": QColor(SELECTED_BG),
    "selectedHoverBg": QColor(SELECTED_HOVER_BG),
    "selectedPressedBg": QColor(SELECTED_PRESSED_BG),
    "hoverBg": QColor(HOVER_BG),
    "pressedBg": QColor(PRESSED_BG),
    "textColor": QColor(TEXT_COLOR),
    "pressedText": QColor(PRESSED_TEXT),
    "separatorColor": QColor(SEPARATOR_COLOR),
    "dividerColor": QColor(SETTINGS_DIVIDER_COLOR),
    "indicatorColor": QColor(INDICATOR_COLOR),
    "indicatorWidth": INDICATOR_W,
    "indicatorHeight": INDICATOR_H,
    "navItemRadius": CORNER_RADIUS,
    "flyoutRadius": FLYOUT_RADIUS,
    "flyoutItemRadius": FLYOUT_ITEM_RADIUS,
}

_UNSET = object()
_QWIDGETSIZE_MAX = 16777215


def _theme_qcolor(name: str):
    def getter(self):
        return self._theme[name]

    def setter(self, value):
        color = QColor(value)
        if color != self._theme[name]:
            self._theme[name] = color
            self._refresh_theme()

    return Property(QColor, getter, setter)


def _theme_int(name: str):
    def getter(self):
        return self._theme[name]

    def setter(self, value):
        number = int(value)
        if number != self._theme[name]:
            self._theme[name] = number
            self._refresh_theme()

    return Property(int, getter, setter)


# ---------------------------------------------------------------------------
# 枚举
# ---------------------------------------------------------------------------


class PaneStateEnum(Enum):
    """侧边栏形态。"""

    Auto = auto()          # 使用窗口宽度阈值
    Expanded = auto()      # 强制展开
    Compact = auto()       # 仅图标
    ForceCompact = auto()  # 强制仅图标
    Hide = auto()          # 强制隐藏


class PaneShowInlineEnum(Enum):
    """展开呈现方式。"""

    Auto = auto()
    Inline = auto()
    Flyout = auto()


def _coerce_pane_state(value) -> PaneStateEnum:
    if isinstance(value, PaneStateEnum):
        return value
    if isinstance(value, str):
        key = value.strip().lower().replace("_", "").replace("-", "")
        for member in PaneStateEnum:
            if member.name.lower() == key:
                return member
    raise TypeError(f"无效的 PaneStateEnum: {value!r}")


def _coerce_show_inline(value) -> PaneShowInlineEnum:
    if isinstance(value, PaneShowInlineEnum):
        return value
    if isinstance(value, str):
        key = value.strip().lower().replace("_", "").replace("-", "")
        for member in PaneShowInlineEnum:
            if member.name.lower() == key:
                return member
    raise TypeError(f"无效的 PaneShowInlineEnum: {value!r}")


def _disconnect_signals(*signals) -> None:
    """静默断开（可能没有任何连接的）信号。"""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        for signal in signals:
            try:
                signal.disconnect()
            except (RuntimeError, TypeError):
                pass


# ---------------------------------------------------------------------------
# 缓动与按钮动画（汉堡 / 返回）
# ---------------------------------------------------------------------------


def cubic_bezier(x1: float, y1: float, x2: float, y2: float):
    """返回 CSS cubic-bezier 缓动函数 f(t), t∈[0,1]。"""

    def f(t: float) -> float:
        if t <= 0.0:
            return 0.0
        if t >= 1.0:
            return 1.0
        lo, hi = 0.0, 1.0
        for _ in range(22):
            u = (lo + hi) * 0.5
            x = 3.0 * (1.0 - u) ** 2 * u * x1 + 3.0 * (1.0 - u) * u * u * x2 + u ** 3
            if x < t:
                lo = u
            else:
                hi = u
        u = (lo + hi) * 0.5
        return 3.0 * (1.0 - u) ** 2 * u * y1 + 3.0 * (1.0 - u) * u * u * y2 + u ** 3

    return f


LINEAR = cubic_bezier(0.0, 0.0, 1.0, 1.0)
EASE_PRESS = cubic_bezier(0.167, 0.167, 0.0, 1.0)
EASE_HAMMER_OUT = cubic_bezier(0.85, 0.0, 0.75, 1.0)
EASE_HAMMER_SETTLE = cubic_bezier(0.35, 0.0, 0.0, 1.0)
EASE_BACK_TIP = cubic_bezier(0.85, 0.0, 0.75, 1.0)
EASE_BACK_STEM = cubic_bezier(0.55, 0.0, 0.75, 1.0)
EASE_BACK_SETTLE = cubic_bezier(0.35, 0.0, 0.0, 1.0)

HAMBURGER_W = 44.75
HAMBURGER_T = 2.75
HAMBURGER_YS = (-13.75, 0.41, 13.75)

BACK_TIP_X = -18.0
BACK_NOTCH_X = -12.0
BACK_STEM_RIGHT = 40.875
BACK_STEM_T = 2.25

ICON_COLOR = QColor("#ffffff")
ICON_COLOR_PRESSED = QColor(PRESSED_TEXT)
ICON_COLOR_DISABLED = QColor(255, 255, 255, 90)


class AnimatedIconButton(QAbstractButton):
    """汉堡 / 返回按钮：Fluent 风格按下、松开时间线动画。"""

    def __init__(self, kind: str, icon_size: int = 18,
                 button_size=HEADER_BUTTON_SIZE, parent=None):
        super().__init__(parent)
        assert kind in ("hamburger", "back")
        self._kind = kind
        self._icon_size = icon_size
        self.setFixedSize(*button_size)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setCursor(Qt.PointingHandCursor)
        self.setAttribute(Qt.WA_Hover, True)
        self.setAccessibleName({"hamburger": "菜单", "back": "返回"}[kind])

        self._hover = False
        self._pressed = False
        self._state = "normal"
        self._vals = self._default_vals()
        self._anim: dict | None = None

        self._timer = QTimer(self)
        self._timer.setTimerType(Qt.PreciseTimer)
        self._timer.setInterval(15)
        self._timer.timeout.connect(self._tick)

    # -- 状态参数 ---------------------------------------------------------
    def _default_vals(self) -> dict:
        if self._kind == "hamburger":
            return {"wf": 1.0, "ty": 1.0}
        return {"tip_dx": 0.0, "stem_right": BACK_STEM_RIGHT}

    # -- 状态机 -----------------------------------------------------------
    def _refresh_state(self) -> None:
        if not self.isEnabled():
            new_state = "normal"
        else:
            new_state = "pressed" if self._pressed else ("pointerover" if self._hover else "normal")
        if new_state == self._state:
            return
        old_state, self._state = self._state, new_state
        if new_state == "pressed":
            self._play_press()
        elif old_state == "pressed":
            self._play_release()
        self.update()

    def _play_press(self) -> None:
        if self._kind == "hamburger":
            self._start([(150.0, {"wf": EASE_PRESS, "ty": EASE_PRESS},
                          {"wf": 0.521, "ty": 1.0})])
        else:
            self._start([(150.0, {"tip_dx": EASE_PRESS, "stem_right": EASE_PRESS},
                          {"tip_dx": 9.0, "stem_right": 41.813})])

    def _play_release(self) -> None:
        if self._kind == "hamburger":
            self._start([
                (133.0, {"wf": EASE_HAMMER_OUT, "ty": EASE_HAMMER_OUT},
                 {"wf": 1.048, "ty": 0.9937}),
                (184.0, {"wf": EASE_HAMMER_SETTLE, "ty": EASE_HAMMER_SETTLE},
                 {"wf": 1.0, "ty": 1.0}),
            ])
        else:
            self._start([
                (167.0, {"tip_dx": EASE_BACK_TIP, "stem_right": EASE_BACK_STEM},
                 {"tip_dx": -4.016, "stem_right": 37.125}),
                (150.0, {"tip_dx": EASE_BACK_SETTLE, "stem_right": EASE_BACK_SETTLE},
                 {"tip_dx": 0.0, "stem_right": BACK_STEM_RIGHT}),
            ])

    # -- 时间线 -----------------------------------------------------------
    def _start(self, phases) -> None:
        self._anim = {
            "phases": phases,
            "i": 0,
            "t0": time.perf_counter(),
            "phase_from": dict(self._vals),
        }
        self._timer.start()

    def _finish(self) -> None:
        self._anim = None
        self._timer.stop()
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
                self.update()
                return
            self._vals.update(targets)
            elapsed -= duration
            anim["t0"] += duration / 1000.0
            anim["i"] += 1
            if anim["i"] < len(anim["phases"]):
                anim["phase_from"] = dict(self._vals)
        self._finish()

    # -- 鼠标 / 键盘 ------------------------------------------------------
    def mousePressEvent(self, event) -> None:
        if not self.isEnabled():
            return
        if event.button() == Qt.LeftButton:
            self._pressed = True
            self._refresh_state()
            event.accept()

    def mouseReleaseEvent(self, event) -> None:
        if not self.isEnabled() or event.button() != Qt.LeftButton or not self._pressed:
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
        if not self.isEnabled():
            return
        if event.key() == Qt.Key_Space and not event.isAutoRepeat():
            self._pressed = True
            self._refresh_state()
            event.accept()
            return
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event) -> None:
        if not self.isEnabled():
            return
        if event.key() == Qt.Key_Space and not event.isAutoRepeat() and self._pressed:
            self._pressed = False
            self._refresh_state()
            self.click()
            event.accept()
            return
        super().keyReleaseEvent(event)

    def changeEvent(self, event) -> None:
        if event.type() == QEvent.EnabledChange:
            self._pressed = False
            self._hover = self.rect().contains(self.mapFromGlobal(self.cursor().pos()))
            self._refresh_state()
            self.update()
        super().changeEvent(event)

    # -- 绘制 -------------------------------------------------------------
    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)

        enabled = self.isEnabled()
        if enabled and self._pressed:
            painter.fillPath(self._background_path(), QColor(PRESSED_BG))
        elif enabled and self._hover:
            painter.fillPath(self._background_path(), QColor(HOVER_BG))

        painter.translate(self.width() / 2.0, self.height() / 2.0)
        scale = self._icon_size / 48.0
        painter.scale(scale, scale)

        if not enabled:
            color = ICON_COLOR_DISABLED
        else:
            color = ICON_COLOR_PRESSED if self._pressed else ICON_COLOR
        if self._kind == "hamburger":
            self._paint_hamburger(painter, color)
        else:
            self._paint_back(painter, color)
        painter.end()

    def _background_path(self) -> QPainterPath:
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), CORNER_RADIUS, CORNER_RADIUS)
        return path

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

        pen = QPen(color, BACK_STEM_T)
        pen.setCapStyle(Qt.FlatCap)
        painter.setPen(pen)
        painter.drawLine(QPointF(stem_left, 0.0), QPointF(stem_right, 0.0))

        painter.setPen(Qt.NoPen)
        radius = BACK_STEM_T / 2.0
        painter.drawEllipse(QPointF(stem_right, 0.0), radius, radius)


# ---------------------------------------------------------------------------
# 胶囊滚动条
# ---------------------------------------------------------------------------


class _CapsuleScrollBar(QScrollBar):
    """2px 胶囊滚动条；鼠标悬浮时 250ms 动画到 5px。"""

    def __init__(self, parent=None):
        super().__init__(Qt.Vertical, parent)
        self.setFixedWidth(SCROLLBAR_HIT)
        self.setAutoFillBackground(False)
        self.setFocusPolicy(Qt.NoFocus)
        self.setCursor(Qt.ArrowCursor)
        self._bar_width = float(SCROLLBAR_MIN)
        self._bar_color = QColor(SCROLLBAR_COLOR)
        self._anim = QPropertyAnimation(self, b"barWidth", self)
        self._anim.setDuration(SCROLLBAR_MS)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)

    def get_bar_color(self) -> QColor:
        return self._bar_color

    def set_bar_color(self, color):
        color = QColor(color)
        if color != self._bar_color:
            self._bar_color = color
            self.update()

    barColor = Property(QColor, get_bar_color, set_bar_color)

    def get_bar_width(self) -> float:
        return self._bar_width

    def set_bar_width(self, value):
        value = float(value)
        if value != self._bar_width:
            self._bar_width = value
            self.update()

    barWidth = Property(float, get_bar_width, set_bar_width)

    def _animate_to(self, target: float) -> None:
        self._anim.stop()
        self._anim.setStartValue(self._bar_width)
        self._anim.setEndValue(float(target))
        self._anim.start()

    def enterEvent(self, event) -> None:
        self._animate_to(SCROLLBAR_MAX)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._animate_to(SCROLLBAR_MIN)
        super().leaveEvent(event)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(Qt.NoPen)

        span = self.maximum() - self.minimum()
        if span <= 0:
            return
        bar_width = max(1.0, self._bar_width)
        track = float(self.height())
        page = max(1, self.pageStep())
        handle = max(24.0, track * page / float(page + span))
        travel = max(0.0, track - handle)
        ratio = (self.value() - self.minimum()) / float(span)
        top = travel * ratio
        x = self.width() - bar_width
        painter.setBrush(self._bar_color)
        painter.drawRoundedRect(
            QRectF(x, top, bar_width, handle), bar_width / 2.0, bar_width / 2.0
        )
        painter.end()


# ---------------------------------------------------------------------------
# 数据模型
# ---------------------------------------------------------------------------


class NavItem(QObject):
    """普通菜单项（也用于折叠菜单的子项与内置设置项）。

    顶层项的 ``globalIndex`` 是导航选择索引；子项的 ``index`` 是兄弟局部索引，
    ``globalIndex`` 返回父折叠项的全局索引（选择 API 只按顶层/折叠项编号）。
    """

    clicked = Signal()
    pressed = Signal()
    released = Signal()
    stateChanged = Signal(bool)

    def __init__(self, navigation, fonticon: str, name: str, layout=None,
                 fold=None, settings: bool = False):
        super().__init__(navigation)
        self._nav = navigation
        self._fonticon = fonticon or ""
        self._name = name or ""
        self._layout = layout
        self._fold = fold
        self._settings = bool(settings)
        self._selected = False
        self._alive = True
        self._index = -1
        self._row: "_NavRow | None" = None
        self._wrapper: "QWidget | None" = None
        self._page: "_ContentPage | None" = None

    # -- 有效性 -----------------------------------------------------------
    def isValid(self) -> bool:
        return self._alive

    @property
    def deleted(self) -> bool:
        return not self._alive

    def _require_alive(self) -> None:
        if not self._alive:
            raise RuntimeError("该 NavItem 已被移除")

    # -- 属性 -------------------------------------------------------------
    @property
    def fonticon(self) -> str:
        return self._fonticon if self._alive else ""

    @fonticon.setter
    def fonticon(self, value: str):
        self._require_alive()
        self._fonticon = value or ""
        self._nav._refresh_item(self)

    @property
    def name(self) -> str:
        return self._name if self._alive else ""

    @name.setter
    def name(self, value: str):
        self._require_alive()
        self._name = value or ""
        self._nav._refresh_item(self)

    @property
    def layout(self):
        return self._layout if self._alive else None

    @layout.setter
    def layout(self, value):
        self._require_alive()
        self._nav._set_item_layout(self, value)

    @property
    def index(self) -> int:
        return self._index if self._alive else -1

    @property
    def globalIndex(self) -> int:
        if not self._alive:
            return -1
        if self._fold is not None:
            return self._fold.globalIndex
        return self._nav._global_index_of(self)

    @property
    def selected(self) -> bool:
        return self._selected if self._alive else False

    @property
    def isSettings(self) -> bool:
        return self._settings

    def select(self, animate: bool = False) -> None:
        """程序化选中本项（子项也可直接调用）。"""
        self._require_alive()
        if self._settings:
            self._nav._select_target(top=None, child=None, settings=True,
                                     animate=animate, record=False)
            return
        if self._fold is not None:
            self._nav._select_target(top=self._fold, child=self, settings=False,
                                     animate=animate, record=False)
        else:
            self._nav._select_target(top=self, child=None, settings=False,
                                     animate=animate, record=False)

    def _set_selected(self, value: bool) -> None:
        if not self._alive:
            return
        value = bool(value)
        if value == self._selected:
            return
        self._selected = value
        if self._row is not None:
            self._row.set_selected(value)
        self.stateChanged.emit(value)

    def _invalidate(self) -> None:
        if not self._alive:
            return
        self._alive = False
        self._selected = False
        self._layout = None
        self._index = -1
        if self._row is not None:
            self._row.deleteLater()
            self._row = None
        if self._wrapper is not None:
            self._wrapper.deleteLater()
            self._wrapper = None
        _disconnect_signals(self.clicked, self.pressed, self.released,
                            self.stateChanged)
        self.setParent(None)

    def __repr__(self) -> str:
        state = "deleted" if not self._alive else f"index={self._index}"
        return f"NavItem({self._name!r}, {state})"


class NavFoldItem(QObject):
    """可展开菜单项。内部只能添加普通子项，不能再嵌套折叠项。

    ``index`` 是折叠项内部的局部索引，``globalIndex`` 是顶层选择索引。
    ``selected`` 表示标题或任一子项被选中（分支选中）。
    """

    clicked = Signal()
    pressed = Signal()
    released = Signal()
    selectedChanged = Signal(int)
    foldStateChanged = Signal(bool)
    stateChanged = Signal(bool)

    def __init__(self, navigation, fonticon: str, name: str, layout=None):
        super().__init__(navigation)
        self._nav = navigation
        self._fonticon = fonticon or ""
        self._name = name or ""
        self._layout = layout
        self._selected = False
        self._expanded = False
        self._alive = True
        self._index = -1
        self._children: list[NavItem] = []
        self._last_child_selected: int | None = None
        self._row: "_FoldRow | None" = None
        self._group: "_FoldGroup | None" = None
        self._page: "_ContentPage | None" = None

    # -- 有效性 -----------------------------------------------------------
    def isValid(self) -> bool:
        return self._alive

    @property
    def deleted(self) -> bool:
        return not self._alive

    def _require_alive(self) -> None:
        if not self._alive:
            raise RuntimeError("该 NavFoldItem 已被移除")

    # -- 属性 -------------------------------------------------------------
    @property
    def fonticon(self) -> str:
        return self._fonticon if self._alive else ""

    @fonticon.setter
    def fonticon(self, value: str):
        self._require_alive()
        self._fonticon = value or ""
        self._nav._refresh_item(self)

    @property
    def name(self) -> str:
        return self._name if self._alive else ""

    @name.setter
    def name(self, value: str):
        self._require_alive()
        self._name = value or ""
        self._nav._refresh_item(self)

    @property
    def layout(self):
        return self._layout if self._alive else None

    @layout.setter
    def layout(self, value):
        self._require_alive()
        self._nav._set_item_layout(self, value)

    @property
    def index(self) -> int:
        return self._index if self._alive else -1

    @property
    def globalIndex(self) -> int:
        if not self._alive:
            return -1
        return self._nav._global_index_of(self)

    @property
    def selected(self) -> bool:
        return self._selected if self._alive else False

    @property
    def expanded(self) -> bool:
        return self._expanded if self._alive else False

    @expanded.setter
    def expanded(self, value: bool):
        self._require_alive()
        self._nav._set_fold_expanded(self, bool(value), animate=True)

    def children(self) -> list[NavItem]:
        return [child for child in self._children if child.isValid()]

    def select(self, animate: bool = False) -> None:
        self._require_alive()
        self._nav._select_target(top=self, child=None, settings=False,
                                 animate=animate, record=False)

    # -- 子项 -------------------------------------------------------------
    def addNavItem(self, fonticon: str, name: str, layout=None) -> NavItem:
        self._require_alive()
        return self._nav._add_child(self, fonticon, name, layout)

    def _set_selected(self, value: bool) -> None:
        if not self._alive:
            return
        value = bool(value)
        if value == self._selected:
            return
        self._selected = value
        self.stateChanged.emit(value)

    def _set_expanded(self, value: bool) -> None:
        if not self._alive:
            return
        value = bool(value)
        if value == self._expanded:
            return
        self._expanded = value
        self.foldStateChanged.emit(value)

    def _emit_child_selected(self, index: int) -> None:
        if not self._alive:
            return
        if index == self._last_child_selected:
            return
        self._last_child_selected = index
        self.selectedChanged.emit(index)

    def _invalidate(self) -> None:
        if not self._alive:
            return
        self._alive = False
        self._selected = False
        self._expanded = False
        self._nav._remembered_folds.discard(self)
        # 子项的控件由 _FoldGroup 统一销毁，这里只让模型失效。
        for child in self._children:
            child._alive = False
            child._selected = False
            child._layout = None
            child._index = -1
            child._row = None
            child._wrapper = None
            _disconnect_signals(child.clicked, child.pressed, child.released,
                                child.stateChanged)
            child.setParent(None)
        self._children = []
        self._layout = None
        self._index = -1
        if self._group is not None:
            self._group.deleteLater()
            self._group = None
        self._row = None
        _disconnect_signals(self.clicked, self.pressed, self.released,
                            self.selectedChanged, self.foldStateChanged,
                            self.stateChanged)
        self.setParent(None)

    def __repr__(self) -> str:
        state = "deleted" if not self._alive else f"index={self._index}"
        return f"NavFoldItem({self._name!r}, {state})"


class _SeparatorEntry:
    """内部：分隔描述符模型。"""

    def __init__(self, text: str):
        self.text = text or ""
        self.widget: "_SeparatorWidget | None" = None


class _LineEntry:
    """内部：``addSeparateLine()`` 添加的 1px 横线模型。"""

    def __init__(self):
        self.widget: "QWidget | None" = None


# ---------------------------------------------------------------------------
# 菜单行
# ---------------------------------------------------------------------------


def _wrap_row(row: QWidget) -> QWidget:
    """给一行加上 4px 上边距（左右/下边距由菜单布局提供）。"""
    wrapper = QWidget()
    wrapper.setFixedHeight(ROW_HEIGHT + ROW_MARGIN_TOP)
    layout = QVBoxLayout(wrapper)
    layout.setContentsMargins(0, ROW_MARGIN_TOP, 0, 0)
    layout.setSpacing(0)
    layout.addWidget(row)
    return wrapper


class _NavRow(QWidget):
    """自绘菜单行：背景、图标、文字、折叠箭头。"""

    clicked = Signal()
    pressed = Signal()
    released = Signal()

    def __init__(self, item, compact: bool = False, child: bool = False,
                 parent=None, content_margin: int | None = None):
        super().__init__(parent)
        self._item = item
        self._compact = bool(compact)
        self._child = bool(child)
        self._content_margin = content_margin
        self._selected = False
        self._hover = False
        self._pressed = False
        self._expanded = False
        self._fold = isinstance(item, NavFoldItem)

        self.setFixedHeight(ROW_HEIGHT)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setCursor(Qt.PointingHandCursor)
        self.setAttribute(Qt.WA_Hover, True)
        self.setAccessibleName(item.name)

        self._font = QFont(APP_FONT)
        self._font.setPixelSize(TEXT_SIZE)

        self._icon = FontIcon(item.fonticon, size=ICON_SIZE, parent=self)
        self._icon.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self._arrow: FontIcon | None = None
        if self._fold:
            self._arrow = fonticon(ARROW_GLYPH, size=ARROW_SIZE)
            self._arrow.setParent(self)
            self._arrow.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            self._arrow.set_angle(0.0)

        self._arrow_anim = QPropertyAnimation(self._arrow, b"angle", self) if self._arrow else None
        if self._arrow_anim is not None:
            self._arrow_anim.setDuration(ANIM_MS)
            self._arrow_anim.setEasingCurve(QEasingCurve.InOutCubic)

        # 内置“设置”项的齿轮：按下 -20°，松开转完整一圈（与旧版按钮动画一致）。
        self._gear_anim: QPropertyAnimation | None = None
        if getattr(item, "isSettings", False):
            self.pressed.connect(self._on_gear_press)
            self.released.connect(self._on_gear_release)

        self._apply_visual_state()
        self._layout_children()

    # -- 外部状态 ---------------------------------------------------------
    def set_selected(self, value: bool) -> None:
        value = bool(value)
        if value == self._selected:
            return
        self._selected = value
        self._apply_visual_state()
        self.update()

    def set_compact(self, compact: bool) -> None:
        compact = bool(compact)
        if compact == self._compact:
            return
        self._compact = compact
        self.setToolTip(self._item.name if compact else "")
        self._layout_children()
        self.update()

    def set_expanded(self, expanded: bool, animate: bool = True) -> None:
        if self._arrow is None:
            return
        expanded = bool(expanded)
        if expanded == self._expanded:
            return
        self._expanded = expanded
        target = 180.0 if expanded else 0.0
        if self._arrow_anim is not None and animate:
            self._arrow_anim.stop()
            self._arrow_anim.setStartValue(float(self._arrow.get_angle()))
            self._arrow_anim.setEndValue(target)
            self._arrow_anim.start()
        else:
            if self._arrow_anim is not None:
                self._arrow_anim.stop()
            self._arrow.set_angle(target)

    def refresh_content(self) -> None:
        self._icon.setText(self._item.fonticon)
        self.setAccessibleName(self._item.name)
        self.setToolTip(self._item.name if self._compact else "")
        self._layout_children()
        self.update()

    # -- 设置齿轮转圈 -----------------------------------------------------
    def _stop_gear_anim(self) -> None:
        if self._gear_anim is not None:
            self._gear_anim.stop()
            self._gear_anim = None

    def _on_gear_press(self) -> None:
        if not self._item.isSettings:
            return
        self._stop_gear_anim()
        start = float(self._icon.get_angle())
        anim = QPropertyAnimation(self._icon, b"angle", self)
        anim.setDuration(GEAR_PRESS_MS)
        anim.setEasingCurve(QEasingCurve.Linear)
        anim.setStartValue(start)
        anim.setEndValue(start - 20.0)
        self._gear_anim = anim
        anim.start()

    def _on_gear_release(self) -> None:
        if not self._item.isSettings:
            return
        self._stop_gear_anim()
        start = float(self._icon.get_angle())
        target = 360.0 if start <= 0.0 else 360.0 * math.ceil(start / 360.0)
        anim = QPropertyAnimation(self._icon, b"angle", self)
        anim.setDuration(GEAR_SPIN_MS)
        # 对应 cubic-bezier(0, 0, 0, 1) 的强 ease-out。
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.setStartValue(start)
        anim.setEndValue(target)
        anim.finished.connect(self._normalize_gear_angle)
        self._gear_anim = anim
        anim.start()

    def _normalize_gear_angle(self) -> None:
        self._gear_anim = None
        self._icon.set_angle(self._icon.get_angle() % 360.0)

    # -- 主题 -------------------------------------------------------------
    def _theme(self) -> dict:
        nav = getattr(self._item, "_nav", None)
        return getattr(nav, "_theme", THEME_DEFAULTS)

    def _item_radius(self) -> int:
        key = ("flyoutItemRadius" if self._content_margin is not None
               else "navItemRadius")
        return int(self._theme()[key])

    # -- 状态 -------------------------------------------------------------
    def _background_color(self) -> QColor | None:
        theme = self._theme()
        if self._pressed:
            key = "selectedPressedBg" if self._selected else "pressedBg"
            return QColor(theme[key])
        if self._hover:
            key = "selectedHoverBg" if self._selected else "hoverBg"
            return QColor(theme[key])
        if self._selected:
            return QColor(theme["selectedBg"])
        return None

    def _text_color(self) -> QColor:
        theme = self._theme()
        return QColor(theme["pressedText"] if self._pressed else theme["textColor"])

    def _apply_visual_state(self) -> None:
        color = self._text_color()
        self._icon.set_icon_color(color)
        if self._arrow is not None:
            self._arrow.set_icon_color(color)

    # -- 尺寸 -------------------------------------------------------------
    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._layout_children()

    def _layout_children(self) -> None:
        width = self.width()
        center_y = self.height() // 2
        has_icon = bool(self._item.fonticon)
        margin = (ROW_ICON_INDENT if self._content_margin is None
                  else self._content_margin)
        indent = margin + (CHILD_INDENT if self._child else 0)
        if self._compact:
            if has_icon:
                icon_x = max(0, (width - ICON_SIZE) // 2)
                self._icon.setGeometry(icon_x, center_y - ICON_SIZE // 2,
                                       ICON_SIZE, ICON_SIZE)
                self._icon.show()
            else:
                self._icon.hide()
            self._arrow and self._arrow.hide()
        else:
            if width <= 0:
                return
            if has_icon:
                self._icon.setGeometry(indent, center_y - ICON_SIZE // 2,
                                       ICON_SIZE, ICON_SIZE)
                self._icon.show()
            else:
                self._icon.hide()
            if self._arrow is not None:
                arrow_x = max(0, width - 16 - ARROW_SIZE)
                self._arrow.setGeometry(arrow_x, center_y - ARROW_SIZE // 2,
                                        ARROW_SIZE, ARROW_SIZE)
                self._arrow.show()
        self._apply_visual_state()
        self.update()

    def _text_rect(self) -> QRectF:
        margin = (ROW_ICON_INDENT if self._content_margin is None
                  else self._content_margin)
        left = margin + (CHILD_INDENT if self._child else 0)
        if self._item.fonticon:
            left += ICON_SIZE + ICON_GAP
        right = self.width() - (16 if self._content_margin is None else margin)
        if self._fold:
            right -= ARROW_SIZE + 8
        return QRectF(left, 0, max(0, right - left), self.height())

    # -- 绘制 -------------------------------------------------------------
    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)

        bg = self._background_color()
        if bg is not None:
            radius = self._item_radius()
            painter.setPen(Qt.NoPen)
            painter.setBrush(bg)
            painter.drawRoundedRect(QRectF(self.rect()), radius, radius)

        if not self._compact:
            painter.setPen(self._text_color())
            painter.setFont(self._font)
            text_rect = self._text_rect()
            metrics = QFontMetrics(self._font)
            text = metrics.elidedText(self._item.name, Qt.ElideRight,
                                      max(1, int(text_rect.width())))
            painter.drawText(text_rect, Qt.AlignVCenter | Qt.AlignLeft, text)
        painter.end()

    # -- 交互 -------------------------------------------------------------
    def enterEvent(self, event) -> None:
        self._hover = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._hover = False
        if not self._pressed:
            self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self._pressed = True
            self._apply_visual_state()
            self.update()
            self.pressed.emit()
            event.accept()

    def mouseReleaseEvent(self, event) -> None:
        if event.button() != Qt.LeftButton or not self._pressed:
            return
        inside = self.rect().contains(event.position().toPoint())
        self._pressed = False
        self._apply_visual_state()
        self.update()
        self.released.emit()
        if inside:
            self.clicked.emit()
        event.accept()


class _FoldRow(_NavRow):
    """折叠菜单标题行（与普通行同尺寸，额外显示箭头）。"""


class _FoldBody(QWidget):
    """折叠项的子项容器：maximumHeight 动画。"""

    heightChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self._expanded = False
        self.setMaximumHeight(0)
        self.setVisible(False)
        self._anim = QPropertyAnimation(self, b"maximumHeight", self)
        self._anim.setDuration(ANIM_MS)
        self._anim.setEasingCurve(QEasingCurve.InOutCubic)
        self._anim.valueChanged.connect(lambda _value: self.heightChanged.emit())
        self._anim.finished.connect(self._on_anim_finished)

    def add_wrapper(self, wrapper: QWidget) -> None:
        self._layout.addWidget(wrapper)
        if self._expanded:
            self.setMaximumHeight(self._natural_height())
            self.heightChanged.emit()

    def remove_wrapper(self, wrapper: QWidget) -> None:
        self._layout.removeWidget(wrapper)

    def _natural_height(self) -> int:
        return max(0, self._layout.sizeHint().height())

    def set_expanded(self, expanded: bool, animate: bool = True) -> None:
        expanded = bool(expanded)
        if expanded == self._expanded:
            if expanded:
                self.setMaximumHeight(self._natural_height())
            return
        self._expanded = expanded
        self._anim.stop()
        if expanded:
            self.setVisible(True)
            natural = self._natural_height()
            if animate:
                self.setMaximumHeight(0)
                self._anim.setStartValue(0)
                self._anim.setEndValue(natural)
                self._anim.start()
            else:
                self.setMaximumHeight(_QWIDGETSIZE_MAX if natural >= 0 else 0)
        else:
            if animate and self.height() > 0:
                self._anim.setStartValue(self.height())
                self._anim.setEndValue(0)
                self._anim.start()
            else:
                self.setMaximumHeight(0)
                self.setVisible(False)

    def _on_anim_finished(self) -> None:
        if self._expanded:
            self.setMaximumHeight(_QWIDGETSIZE_MAX)
        else:
            self.setVisible(False)
            self.setMaximumHeight(0)
        self.heightChanged.emit()


class _FoldGroup(QWidget):
    """折叠标题 + 子项容器的组合控件。"""

    def __init__(self, fold: NavFoldItem, header: _FoldRow, parent=None):
        super().__init__(parent)
        self._fold = fold
        self._header = header
        self._body = _FoldBody(self)
        self._header_wrapper = _wrap_row(header)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self._layout.addWidget(self._header_wrapper)
        self._layout.addWidget(self._body)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

    def header_wrapper(self) -> QWidget:
        return self._header_wrapper

    def body(self) -> _FoldBody:
        return self._body

    def add_child(self, row: _NavRow) -> None:
        self._body.add_wrapper(_wrap_row(row))

    def set_expanded(self, expanded: bool, animate: bool = True) -> None:
        self._header.set_expanded(expanded, animate=animate)
        self._body.set_expanded(expanded, animate=animate)


class _SeparatorWidget(QWidget):
    """加粗 #cccccc 的分隔描述符。"""

    heightChanged = Signal()

    def __init__(self, text: str, parent=None, navigation=None):
        super().__init__(parent)
        self._nav = navigation
        self._text = text or ""
        self._compact = False
        self._font = QFont(APP_FONT)
        self._font.setPixelSize(SEPARATOR_SIZE)
        self._font.setBold(True)
        metrics = QFontMetrics(self._font)
        self._natural = SEPARATOR_TOP + metrics.height() + SEPARATOR_BOTTOM
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMaximumHeight(self._natural)
        self._anim = QPropertyAnimation(self, b"maximumHeight", self)
        self._anim.setDuration(ANIM_MS)
        self._anim.setEasingCurve(QEasingCurve.InOutCubic)
        self._anim.valueChanged.connect(lambda _value: self.heightChanged.emit())
        self._anim.finished.connect(self._on_anim_finished)

    def set_text(self, text: str) -> None:
        self._text = text or ""
        self.update()

    def sizeHint(self) -> QSize:
        return QSize(0, self._natural)

    def minimumSizeHint(self) -> QSize:
        return QSize(0, 0)

    def set_compact(self, compact: bool, animate: bool = True) -> None:
        compact = bool(compact)
        if compact == self._compact and self.isVisible() == (not compact):
            return
        self._compact = compact
        self._anim.stop()
        if compact:
            if animate and self.isVisible():
                self._anim.setStartValue(self.height())
                self._anim.setEndValue(0)
                self._anim.start()
            else:
                self.setMaximumHeight(0)
                self.setVisible(False)
        else:
            self.setVisible(True)
            if animate:
                self.setMaximumHeight(0)
                self._anim.setStartValue(0)
                self._anim.setEndValue(self._natural)
                self._anim.start()
            else:
                self.setMaximumHeight(self._natural)

    def _on_anim_finished(self) -> None:
        if self._compact:
            self.setVisible(False)
            self.setMaximumHeight(0)
        else:
            self.setMaximumHeight(self._natural)
        self.heightChanged.emit()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.TextAntialiasing, True)
        theme = getattr(self._nav, "_theme", THEME_DEFAULTS)
        painter.setPen(QColor(theme["separatorColor"]))
        painter.setFont(self._font)
        metrics = QFontMetrics(self._font)
        rect = QRectF(TOP_INDENT, SEPARATOR_TOP, self.width() - TOP_INDENT * 2,
                      metrics.height())
        painter.drawText(rect, Qt.AlignLeft | Qt.AlignVCenter,
                         metrics.elidedText(self._text, Qt.ElideRight,
                                            max(1, int(rect.width()))))
        painter.end()


class _SettingsDivider(QWidget):
    """1px 分割线：设置底栏上方与 ``addSeparateLine()`` 共用。"""

    def __init__(self, navigation=None, parent=None):
        super().__init__(parent)
        self._nav = navigation
        self.setFixedHeight(SETTINGS_DIVIDER_HEIGHT)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setAutoFillBackground(False)

    def paintEvent(self, event) -> None:
        theme = getattr(self._nav, "_theme", THEME_DEFAULTS)
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(theme["dividerColor"]))
        painter.end()


# ---------------------------------------------------------------------------
# 指示器
# ---------------------------------------------------------------------------


class _IndicatorOverlay(QWidget):
    """2×16 胶囊选中指示器，贴菜单行左边界，带两段 125ms 位移/拉伸动画。"""

    def __init__(self, pane, parent=None):
        super().__init__(parent or pane)
        self._pane = pane
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAutoFillBackground(False)
        self._row: QWidget | None = None
        self._anchor_row: QWidget | None = None
        self._top = 0.0
        self._bottom = 0.0
        self._edge = ""
        self._frozen_top = 0.0
        self._frozen_bottom = 0.0
        self._phase = 0
        self._new_row: QWidget | None = None
        self._above = True
        self._default_top = 0.0
        self._default_bottom = 0.0

        self._anim = QVariantAnimation(self)
        self._anim.setDuration(INDICATOR_STEP_MS)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self._anim.valueChanged.connect(self._on_anim_value)
        self._anim.finished.connect(self._on_anim_finished)

        self._slide_anim = QVariantAnimation(self)
        self._slide_anim.setDuration(INDICATOR_STEP_MS)
        self._slide_anim.setEasingCurve(QEasingCurve.OutCubic)
        self._slide_anim.valueChanged.connect(self._on_slide_value)
        self._slide_from_top = 0.0
        self._slide_from_bottom = 0.0
        self._slide_to_top = 0.0
        self._slide_to_bottom = 0.0
        self.hide()

    # -- 主题 -------------------------------------------------------------
    def _theme(self) -> dict:
        nav = getattr(self._pane, "_nav", None)
        return getattr(nav, "_theme", THEME_DEFAULTS)

    # -- 几何 -------------------------------------------------------------
    def _row_rect(self, row: QWidget) -> QRect:
        row_global = row.mapToGlobal(QPoint(0, 0))
        overlay_global = self.mapToGlobal(QPoint(0, 0))
        return QRect(row_global.x() - overlay_global.x(),
                     row_global.y() - overlay_global.y(),
                     row.width(), row.height())

    def _default_span(self, row: QWidget) -> tuple[float, float]:
        rect = self._row_rect(row)
        center = rect.center().y()
        height = float(self._theme()["indicatorHeight"])
        return center - height / 2.0, center + height / 2.0

    def _is_row_visible(self, row: QWidget) -> bool:
        if row is None or not row.isVisible():
            return False
        return self._pane.row_visible_for_indicator(row)

    # -- 对外接口 ---------------------------------------------------------
    def set_row(self, row: QWidget | None, animate: bool = True) -> None:
        self._anim.stop()
        self._anchor_row = row
        if row is None or not self._is_row_visible(row):
            self._row = None
            self.hide()
            return

        old_row = self._row
        if old_row is row:
            self._row = row
            self._top, self._bottom = self._default_span(row)
            self.show()
            self.raise_()
            self.update()
            return

        self.show()
        self.raise_()
        if old_row is None or not self._is_row_visible(old_row) or not animate:
            self._row = row
            self._top, self._bottom = self._default_span(row)
            self.update()
            return

        old_rect = self._row_rect(old_row)
        self._row = row
        self._new_row = row
        new_rect = self._row_rect(row)
        self._above = new_rect.center().y() < old_rect.center().y()
        self._default_top, self._default_bottom = self._default_span(row)
        self._frozen_top = self._top
        self._frozen_bottom = self._bottom
        self._phase = 0

        if self._above:
            self._edge = "top"
            self._start_edge(self._top, old_rect.top())
        else:
            self._edge = "bottom"
            self._start_edge(self._bottom, old_rect.bottom())

    def hide_indicator(self) -> None:
        self._anim.stop()
        self._slide_anim.stop()
        self._row = None
        self._anchor_row = None
        self.hide()

    def is_animating(self) -> bool:
        return (self._anim.state() == QAbstractAnimation.Running or
                self._slide_anim.state() == QAbstractAnimation.Running)

    def set_row_animated_from(self, row: QWidget | None, start_y: float) -> None:
        """把指示器从 start_y（本控件坐标）滑动到 row 的默认位置。"""
        self._anim.stop()
        self._slide_anim.stop()
        self._anchor_row = row
        if row is None or not self._is_row_visible(row):
            self._row = None
            self.hide()
            return
        self._row = row
        self._slide_to_top, self._slide_to_bottom = self._default_span(row)
        offset = float(start_y) - (self._slide_to_top + self._slide_to_bottom) / 2.0
        self._slide_from_top = self._slide_to_top + offset
        self._slide_from_bottom = self._slide_to_bottom + offset
        self._top = self._slide_from_top
        self._bottom = self._slide_from_bottom
        self.show()
        self.raise_()
        self.update()
        self._slide_anim.setStartValue(0.0)
        self._slide_anim.setEndValue(1.0)
        self._slide_anim.start()

    def _on_slide_value(self, value) -> None:
        value = float(value)
        self._top = self._slide_from_top + (self._slide_to_top - self._slide_from_top) * value
        self._bottom = self._slide_from_bottom + (
            self._slide_to_bottom - self._slide_from_bottom
        ) * value
        self.update()

    def refresh(self) -> None:
        anchor = self._anchor_row
        if anchor is None:
            self._row = None
            self.hide()
            return
        if self._anim.state() == QAbstractAnimation.Running:
            return
        if not self._is_row_visible(anchor):
            self._row = None
            self.hide()
            return
        self._row = anchor
        self._top, self._bottom = self._default_span(anchor)
        self.show()
        self.raise_()
        self.update()

    # -- 动画 -------------------------------------------------------------
    def _start_edge(self, start: float, end: float) -> None:
        self._anim.stop()
        self._anim.setStartValue(float(start))
        self._anim.setEndValue(float(end))
        self._anim.start()

    def _on_anim_value(self, value) -> None:
        value = float(value)
        if self._edge == "top":
            self._top = value
        else:
            self._bottom = value
        self.update()

    def _on_anim_finished(self) -> None:
        if self._phase == 0:
            self._phase = 1
            if self._above:
                self._top = self._default_top
                self._bottom = self._row_rect(self._new_row).bottom()
                self._edge = "bottom"
                self._start_edge(self._bottom, self._default_bottom)
            else:
                self._top = self._row_rect(self._new_row).top()
                self._bottom = self._default_bottom
                self._edge = "top"
                self._start_edge(self._top, self._default_top)
        else:
            self._phase = 2
            if self._row is not None:
                self._top, self._bottom = self._default_span(self._row)
            else:
                self._top = self._default_top
                self._bottom = self._default_bottom
            self.update()

    # -- 绘制 -------------------------------------------------------------
    def paintEvent(self, event) -> None:
        if self._row is None or self._bottom - self._top <= 0:
            return
        theme = self._theme()
        width = float(theme["indicatorWidth"])
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(theme["indicatorColor"]))
        painter.drawRoundedRect(
            QRectF(INDICATOR_INSET, self._top, width,
                   self._bottom - self._top),
            width / 2.0, width / 2.0,
        )
        painter.end()


# ---------------------------------------------------------------------------
# 内容区
# ---------------------------------------------------------------------------


class _LayoutHost(QWidget):
    """承载用户 QLayout 的容器，向滚动区透传 heightForWidth。"""

    def heightForWidth(self, width: int) -> int:
        layout = self.layout()
        if layout is not None and layout.hasHeightForWidth():
            return layout.heightForWidth(width)
        return super().heightForWidth(width)

    def sizeHint(self) -> QSize:
        layout = self.layout()
        if layout is not None and layout.hasHeightForWidth() and self.width() > 0:
            return QSize(max(1, layout.sizeHint().width()),
                         max(1, layout.heightForWidth(self.width())))
        return super().sizeHint()


class _ContentPage(QScrollArea):
    """一个菜单项对应的内容页（自带胶囊滚动条）。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.NoFrame)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBar(_CapsuleScrollBar(self))
        self.setAutoFillBackground(False)
        self.viewport().setAutoFillBackground(False)
        self.viewport().setStyleSheet("background: transparent;")
        self._body = QWidget()
        self._body.setAutoFillBackground(False)
        self._body_layout = QVBoxLayout(self._body)
        self._body_layout.setContentsMargins(0, 0, 0, 0)
        self._body_layout.setSpacing(0)
        self.setWidget(self._body)
        self.setStyleSheet("QScrollArea { background: transparent; border: none; }")

    def body_layout(self) -> QVBoxLayout:
        return self._body_layout

    def add_host(self, host: QWidget) -> None:
        if host.parent() is not self._body:
            host.setParent(self._body)
        if self._body_layout.indexOf(host) < 0:
            self._body_layout.addWidget(host)

    def remove_host(self, host: QWidget) -> None:
        if self._body_layout.indexOf(host) >= 0:
            self._body_layout.removeWidget(host)


class _ContentHost(QWidget):
    """内容页容器：负责页面定位与 64px 上滑动画。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(False)
        self._pages: list[_ContentPage] = []
        self._current: _ContentPage | None = None
        self._anim = QPropertyAnimation(self, b"pos", self)

    def register_page(self, page: _ContentPage) -> None:
        if page not in self._pages:
            self._pages.append(page)
            page.setParent(self)
            page.hide()

    def pages(self) -> list[_ContentPage]:
        return list(self._pages)

    def remove_page(self, page: _ContentPage) -> None:
        if page in self._pages:
            self._pages.remove(page)
        if self._current is page:
            self._anim.stop()
            self._current = None
        page.hide()
        page.deleteLater()

    def current_page(self) -> _ContentPage | None:
        return self._current

    def show_page(self, page: _ContentPage | None, animate: bool = True) -> None:
        old = self._current
        if page is None:
            self._anim.stop()
            for candidate in self._pages:
                candidate.hide()
            self._current = None
            return
        if page is old:
            page.move(0, 0)
            page.show()
            page.raise_()
            return

        self.register_page(page)
        self._current = page
        for candidate in self._pages:
            if candidate is not page:
                candidate.hide()
        page.setGeometry(0, 0, self.width(), self.height())
        page.show()
        page.raise_()
        if animate:
            page.move(0, 64)
            self._anim.stop()
            self._anim.setTargetObject(page)
            self._anim.setPropertyName(b"pos")
            self._anim.setDuration(ANIM_MS)
            self._anim.setEasingCurve(QEasingCurve.OutCubic)
            self._anim.setStartValue(QPoint(0, 64))
            self._anim.setEndValue(QPoint(0, 0))
            self._anim.start()
        else:
            self._anim.stop()
            page.move(0, 0)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        for page in self._pages:
            page.setGeometry(0, 0, self.width(), self.height())
        if self._current is not None:
            self._current.move(0, 0)


class HighLightPanel(QWidget):
    """内容卡片：默认透明，让窗口背板的 BUBBLE_BACKGROUND_NORMAL 透出。

    ``bg_color`` 仍可作为兜底纯色（QSS: ``qproperty-bg_color``）；默认透明时
    内容区直接使用 glasskit 的窗口玻璃。左上 8px 圆角仅在设置了底色时可见。
    """

    BG = QColor("#272727")
    RADIUS = 8
    PADDING = 36

    def __init__(self, parent=None):
        super().__init__(parent)
        self._bg_color = QColor(0, 0, 0, 0)
        self._radius = self.RADIUS
        self.setAutoFillBackground(False)
        self._layout = QVBoxLayout(self)
        self._base_top = self.PADDING - 6
        self._layout.setContentsMargins(
            self.PADDING, self._base_top, self.PADDING, self.PADDING - 3
        )
        self._layout.setSpacing(0)
        self._content_host = _ContentHost(self)
        self._layout.addWidget(self._content_host, 1)

    def set_top_clearance(self, clearance: int) -> None:
        """为 Hide 模式下浮在内容上的顶栏预留空间。"""
        top = self._base_top + max(0, int(clearance))
        margins = self._layout.contentsMargins()
        if margins.top() != top:
            self._layout.setContentsMargins(
                margins.left(), top, margins.right(), margins.bottom()
            )
            self._layout.activate()

    def content_host(self) -> _ContentHost:
        return self._content_host

    def setContent(self, widget: QWidget):
        """兼容旧 API：直接放入一个控件。"""
        self._layout.addWidget(widget)

    def get_bg_color(self) -> QColor:
        return self._bg_color

    def set_bg_color(self, color):
        color = QColor(color)
        if color != self._bg_color:
            self._bg_color = color
            self.update()

    bg_color = Property(QColor, get_bg_color, set_bg_color)

    def get_corner_radius(self) -> int:
        return self._radius

    def set_corner_radius(self, value):
        value = max(0, int(value))
        if value != self._radius:
            self._radius = value
            self.update()

    cornerRadius = Property(int, get_corner_radius, set_corner_radius)

    def paintEvent(self, event):
        if self._bg_color.alpha() <= 0:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        r = self._radius
        rect = QRectF(self.rect())
        path = QPainterPath()
        path.moveTo(rect.left() + r, rect.top())
        path.lineTo(rect.right(), rect.top())
        path.lineTo(rect.right(), rect.bottom())
        path.lineTo(rect.left(), rect.bottom())
        path.lineTo(rect.left(), rect.top() + r)
        path.quadTo(rect.left(), rect.top(), rect.left() + r, rect.top())
        path.closeSubpath()
        painter.fillPath(path, self._bg_color)
        painter.end()


# ---------------------------------------------------------------------------
# 侧边栏 / 根画布 / 顶栏
# ---------------------------------------------------------------------------


class _Pane(QWidget):
    """侧边栏玻璃面板：正常玻璃或 Flyout 玻璃。"""

    def __init__(self, navigation, parent=None):
        super().__init__(parent)
        self._nav = navigation
        self._flyout = False
        self._snapshot: QImage | None = None
        self._snapshot_origin = QPoint(0, 0)
        self._settings_wrapper: QWidget | None = None
        self._settings_row: _NavRow | None = None
        self._settings_divider: QWidget | None = None

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(ROW_MARGIN_X, 48 + ROW_MARGIN_TOP,
                                        ROW_MARGIN_X, 0)
        self._layout.setSpacing(0)

        self._scroll = QScrollArea(self)
        self._scroll.setFrameShape(QFrame.NoFrame)
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # 滚动条不占布局宽度：菜单行始终占满，滚动条作为覆盖层画在行上面。
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll.setAutoFillBackground(False)
        self._scroll.viewport().setAutoFillBackground(False)
        self._scroll.viewport().setStyleSheet("background: transparent;")
        self._scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        self._menu = QWidget()
        self._menu.setAutoFillBackground(False)
        self._menu_layout = QVBoxLayout(self._menu)
        self._menu_layout.setContentsMargins(0, 0, 0, 0)
        self._menu_layout.setSpacing(0)
        self._menu_layout.addStretch(1)
        self._scroll.setWidget(self._menu)
        self._layout.addWidget(self._scroll, 1)

        self._scrollbar_model = self._scroll.verticalScrollBar()
        self._scroll_overlay = _CapsuleScrollBar(self)
        self._scroll_overlay.setFocusPolicy(Qt.NoFocus)
        self._scroll_overlay.hide()
        self._scroll_syncing = False
        self._scrollbar_model.rangeChanged.connect(self._on_scroll_range_changed)
        self._scrollbar_model.valueChanged.connect(self._on_scroll_model_value)
        self._scroll_overlay.valueChanged.connect(self._on_scroll_overlay_value)

        self._indicator = _IndicatorOverlay(self, self)
        self._indicator.raise_()
        self._scrollbar_model.valueChanged.connect(self._indicator.refresh)

    # -- 菜单内容 ---------------------------------------------------------
    def add_menu_widget(self, widget: QWidget) -> None:
        index = max(0, self._menu_layout.count() - 1)
        self._menu_layout.insertWidget(index, widget)

    def remove_menu_widget(self, widget: QWidget) -> None:
        self._menu_layout.removeWidget(widget)

    def set_settings_widget(self, wrapper: QWidget, row: _NavRow) -> None:
        self._settings_wrapper = wrapper
        self._settings_row = row
        # 设置项固定在滚动区外：上方 1px 分割线，下方 6px 外边距。
        self._settings_divider = _SettingsDivider(self._nav, self)
        self._layout.addWidget(self._settings_divider)
        self._layout.addWidget(wrapper)
        margins = self._layout.contentsMargins()
        self._layout.setContentsMargins(
            margins.left(), margins.top(), margins.right(),
            SETTINGS_BOTTOM_MARGIN,
        )
        self._layout.activate()
        self._position_scroll_overlay()

    def settings_widget(self) -> QWidget | None:
        return self._settings_wrapper

    def set_header_height(self, height: int) -> None:
        margins = self._layout.contentsMargins()
        self._layout.setContentsMargins(margins.left(), height + ROW_MARGIN_TOP,
                                        margins.right(), margins.bottom())
        self._layout.activate()
        self._menu_layout.activate()
        self.updateGeometry()
        QTimer.singleShot(0, self._sync_scroll_overlay)

    # -- 覆盖式滚动条 -----------------------------------------------------
    def _sync_scroll_overlay(self) -> None:
        if not hasattr(self, "_scroll_overlay"):
            return
        model = self._scrollbar_model
        overlay = self._scroll_overlay
        self._scroll_syncing = True
        try:
            overlay.setRange(model.minimum(), model.maximum())
            overlay.setPageStep(model.pageStep())
            overlay.setSingleStep(model.singleStep())
            overlay.setValue(model.value())
        finally:
            self._scroll_syncing = False
        self._position_scroll_overlay()

    def _position_scroll_overlay(self) -> None:
        if not hasattr(self, "_scroll_overlay"):
            return
        top_left = self._scroll.mapTo(self, QPoint(0, 0))
        x = max(0, self.width() - ROW_MARGIN_X - SCROLLBAR_HIT)
        height = max(0, self._scroll.height())
        self._scroll_overlay.setGeometry(x, top_left.y(), SCROLLBAR_HIT, height)
        needed = self._scrollbar_model.maximum() > self._scrollbar_model.minimum()
        self._scroll_overlay.setVisible(bool(needed and self.isVisible()))
        if needed:
            self._scroll_overlay.raise_()

    def _on_scroll_range_changed(self, _minimum: int, _maximum: int) -> None:
        if self._scroll_syncing:
            return
        self._sync_scroll_overlay()

    def _on_scroll_model_value(self, value: int) -> None:
        if self._scroll_syncing:
            return
        self._scroll_syncing = True
        try:
            self._scroll_overlay.setValue(int(value))
        finally:
            self._scroll_syncing = False

    def _on_scroll_overlay_value(self, value: int) -> None:
        if self._scroll_syncing:
            return
        self._scrollbar_model.setValue(int(value))

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._sync_scroll_overlay()

    # -- 状态 -------------------------------------------------------------
    def set_flyout(self, flyout: bool) -> None:
        flyout = bool(flyout)
        if flyout == self._flyout:
            return
        self._flyout = flyout
        self.update()

    def set_snapshot(self, image: QImage | None, origin: QPoint) -> None:
        self._snapshot = image
        self._snapshot_origin = QPoint(origin)
        self.update()

    def shift_snapshot(self, dx: int, dy: int) -> None:
        if self._snapshot is not None:
            self._snapshot_origin += QPoint(int(dx), int(dy))
            self.update()

    def set_compact(self, compact: bool) -> None:
        if self._settings_row is not None:
            self._settings_row.set_compact(compact)

    def refresh_theme(self) -> None:
        self._indicator.refresh()
        self._indicator.update()
        if self._settings_divider is not None:
            self._settings_divider.update()
        if hasattr(self, "_scroll_overlay"):
            self._scroll_overlay.update()
        for widget in self._menu.findChildren(QWidget):
            if isinstance(widget, (_SeparatorWidget, _SettingsDivider)):
                widget.update()
        self.update()

    def menu_visible_rect(self) -> QRect:
        viewport = self._scroll.viewport()
        top_left = viewport.mapTo(self, QPoint(0, 0))
        return QRect(top_left, viewport.size())

    def row_visible_for_indicator(self, row: QWidget | None) -> bool:
        if row is None or not row.isVisible():
            return False
        if self._settings_wrapper is not None and (
                row is self._settings_wrapper or
                self._settings_wrapper.isAncestorOf(row)):
            return True
        visible_rect = self.menu_visible_rect()
        center_global = row.mapToGlobal(
            QPoint(row.width() // 2, row.height() // 2)
        )
        center = self.mapFromGlobal(center_global)
        return visible_rect.contains(center)

    def indicator(self) -> _IndicatorOverlay:
        return self._indicator

    # -- 绘制 -------------------------------------------------------------
    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        rect = QRectF(self.rect())

        if self._flyout:
            style = FLYOUT_GLASS
            path = rounded_path(rect, style.radius)
            painter.save()
            painter.setClipPath(path)
            base = QColor(style.tint)
            base.setAlpha(int(round(255 * style.opacity / 100.0)))
            painter.fillRect(rect, base)
            if self._snapshot is not None and not self._snapshot.isNull():
                dpr = float(self._snapshot.devicePixelRatio() or 1.0)
                our_global = self.mapToGlobal(QPoint(0, 0))
                offset = self._snapshot_origin - our_global
                target = QRectF(offset.x(), offset.y(),
                                self._snapshot.width() / dpr,
                                self._snapshot.height() / dpr)
                painter.drawImage(target, self._snapshot)
            painter.restore()
            paint_frost_overlay(painter, rect, style, radius=style.radius,
                                border=True, vignette=style.vignette)
        else:
            style = SIDEBAR_GLASS
            backdrop = self._nav.backdrop
            if backdrop is not None and self.isVisible():
                if backdrop.energy.active:
                    painter.fillRect(rect, QColor(style.tint))
                else:
                    global_rect = QRect(self.mapToGlobal(QPoint(0, 0)), self.size())
                    backdrop.paint_material(painter, rect, global_rect, style)
            else:
                paint_frost_overlay(painter, rect, style, radius=0, border=False)
        painter.end()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._indicator.setGeometry(self.rect())
        self._indicator.refresh()
        self._sync_scroll_overlay()


class _PaneShadow(QWidget):
    """侧边栏 Flyout 的柔和阴影层（预模糊，不压暗玻璃内部）。"""

    def __init__(self, parent=None, radius: int = CORNER_RADIUS):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAutoFillBackground(False)
        self._radius = int(radius)
        self._cache_key: tuple | None = None
        self._image: QImage | None = None

    def set_radius(self, radius: int) -> None:
        radius = max(0, int(radius))
        if radius != self._radius:
            self._radius = radius
            self._cache_key = None
            self.update()

    def _build_image(self) -> QImage | None:
        width, height = self.width(), self.height()
        if width <= 0 or height <= 0:
            return None
        dpr = float(self.devicePixelRatioF() or 1.0)
        key = (width, height, dpr, self._radius)
        if self._cache_key == key and self._image is not None:
            return self._image

        image = QImage(int(width * dpr), int(height * dpr),
                       QImage.Format.Format_RGBA8888)
        image.setDevicePixelRatio(dpr)
        image.fill(Qt.transparent)
        painter = QPainter(image)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0, 165))
        inner = QRectF(self.rect()).adjusted(
            SHADOW_MARGIN, SHADOW_MARGIN, -SHADOW_MARGIN, -SHADOW_MARGIN
        )
        painter.drawRoundedRect(inner, self._radius, self._radius)
        painter.end()

        blurred = blur_qimage(image, 12.0 * dpr)
        blurred.setDevicePixelRatio(dpr)
        # 挖掉面板内部，玻璃只叠在外侧柔和阴影上。
        erase = QPainter(blurred)
        erase.setRenderHint(QPainter.Antialiasing, True)
        erase.setCompositionMode(QPainter.CompositionMode_Clear)
        erase.setPen(Qt.NoPen)
        erase.setBrush(Qt.black)
        erase.drawRoundedRect(inner, self._radius, self._radius)
        erase.end()

        self._cache_key = key
        self._image = blurred
        return blurred

    def paintEvent(self, event) -> None:
        image = self._build_image()
        if image is None:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        painter.drawImage(0, 0, image)
        painter.end()


class _HeaderBar(QWidget):
    """汉堡 / 返回按钮容器；Compact 图标栏内纵向排列，其余横向排列。"""

    def __init__(self, buttons: list[AnimatedIconButton], parent=None):
        super().__init__(parent)
        self._buttons = buttons
        self._vertical = False
        self._initialized = False
        for button in buttons:
            button.setParent(self)
        self.setAutoFillBackground(False)
        self.set_vertical(False)

    def set_vertical(self, vertical: bool) -> None:
        vertical = bool(vertical)
        if self._initialized and vertical == self._vertical:
            return
        self._vertical = vertical
        self._initialized = True
        count = len(self._buttons)
        if count == 0:
            self.setFixedSize(0, 0)
            return
        width, height = HEADER_BUTTON_SIZE
        if vertical:
            for index, button in enumerate(self._buttons):
                button.move(HEADER_MARGIN,
                            HEADER_MARGIN + index * (height + HEADER_MARGIN))
            self.setFixedSize(HEADER_MARGIN * 2 + width,
                              HEADER_MARGIN * 2 + count * height +
                              (count - 1) * HEADER_MARGIN)
        else:
            for index, button in enumerate(self._buttons):
                button.move(HEADER_MARGIN + index * (width + HEADER_MARGIN),
                            HEADER_MARGIN)
            self.setFixedSize(HEADER_MARGIN * 2 + count * width +
                              (count - 1) * HEADER_MARGIN,
                              HEADER_MARGIN * 2 + height)

    def recommended_size(self) -> QSize:
        return self.size()


class _RootCanvas(QWidget):
    """窗口根画布：内容卡片、侧边栏、阴影、顶栏全部手动定位。"""

    def __init__(self, navigation, parent=None):
        super().__init__(parent)
        self._nav = navigation
        self.setAutoFillBackground(False)
        self._content_card = HighLightPanel(self)
        self._shadow = _PaneShadow(self)
        self._pane = _Pane(navigation, self)
        self._header: _HeaderBar | None = None

        self._pane_w = float(EXPANDED_WIDTH)
        self._pane_x = 0.0
        self._pane_y = 0.0
        self._pane_h = 0.0
        self._content_x = float(EXPANDED_WIDTH)
        self._flyout_mode = False
        self._base_width = COMPACT_WIDTH

        self._anim_group: QParallelAnimationGroup | None = None
        self._finish_callback: Callable[[], None] | None = None

        self._shadow.hide()
        self._layout_children()

    # -- 属性动画 ---------------------------------------------------------
    def get_pane_width(self) -> float:
        return self._pane_w

    def set_pane_width(self, value):
        self._pane_w = float(value)
        self._layout_children()

    paneWidth = Property(float, get_pane_width, set_pane_width)

    def get_pane_x(self) -> float:
        return self._pane_x

    def set_pane_x(self, value):
        self._pane_x = float(value)
        self._layout_children()

    paneX = Property(float, get_pane_x, set_pane_x)

    def get_pane_y(self) -> float:
        return self._pane_y

    def set_pane_y(self, value):
        self._pane_y = float(value)
        self._layout_children()

    paneY = Property(float, get_pane_y, set_pane_y)

    def get_pane_height(self) -> float:
        return self._pane_h

    def set_pane_height(self, value):
        self._pane_h = float(value)
        self._layout_children()

    paneHeight = Property(float, get_pane_height, set_pane_height)

    def get_content_x(self) -> float:
        return self._content_x

    def set_content_x(self, value):
        self._content_x = float(value)
        self._layout_children()

    contentX = Property(float, get_content_x, set_content_x)

    # -- 对外 -------------------------------------------------------------
    def content_card(self) -> HighLightPanel:
        return self._content_card

    def pane(self) -> _Pane:
        return self._pane

    def shadow(self) -> _PaneShadow:
        return self._shadow

    def attach_header(self, header: _HeaderBar) -> None:
        self._header = header
        header.setParent(self)
        self._layout_children()

    def set_base_width(self, width: int) -> None:
        self._base_width = int(width)

    def base_width(self) -> int:
        return self._base_width

    def set_flyout_mode(self, flyout: bool) -> None:
        self._flyout_mode = bool(flyout)
        if self._flyout_mode:
            self._shadow.show()
            self._shadow.raise_()
            self._pane.raise_()
        else:
            self._shadow.hide()

    def animate_to(self, *, pane_width: float, pane_x: float, pane_y: float,
                   pane_height: float, content_x: float, duration: int,
                   flyout: bool, on_finished: Callable[[], None] | None = None) -> None:
        self.stop_animation()
        self.set_flyout_mode(flyout)
        targets = [
            ("paneWidth", self._pane_w, float(pane_width)),
            ("paneX", self._pane_x, float(pane_x)),
            ("paneY", self._pane_y, float(pane_y)),
            ("paneHeight", self._pane_h, float(pane_height)),
            ("contentX", self._content_x, float(content_x)),
        ]
        animations = []
        for name, start, end in targets:
            if abs(start - end) < 0.5:
                continue
            anim = QPropertyAnimation(self, name.encode("ascii"), self)
            anim.setDuration(max(0, int(duration)))
            anim.setEasingCurve(QEasingCurve.OutCubic)
            anim.setStartValue(start)
            anim.setEndValue(end)
            animations.append(anim)

        self._finish_callback = on_finished
        if not animations or duration <= 0:
            self._pane_w = float(pane_width)
            self._pane_x = float(pane_x)
            self._pane_y = float(pane_y)
            self._pane_h = float(pane_height)
            self._content_x = float(content_x)
            self._layout_children()
            self._run_finish_callback()
            return

        group = QParallelAnimationGroup(self)
        for anim in animations:
            group.addAnimation(anim)
        group.finished.connect(self._on_animation_finished)
        self._anim_group = group
        group.start()

    def stop_animation(self) -> None:
        if self._anim_group is not None:
            self._anim_group.stop()
            self._anim_group.deleteLater()
            self._anim_group = None
        self._finish_callback = None

    def _on_animation_finished(self) -> None:
        self._anim_group = None
        self._layout_children()
        self._run_finish_callback()

    def _run_finish_callback(self) -> None:
        callback, self._finish_callback = self._finish_callback, None
        if callback is not None:
            callback()

    # -- 布局 -------------------------------------------------------------
    def refresh_geometry(self) -> None:
        if self._pane_h <= 0:
            self._pane_h = float(self.height())
        self._layout_children()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if self._anim_group is None:
            self._pane_h = float(self.height())
            if self._flyout_mode:
                self._pane_y = 4.0
                self._pane_h = float(self.height() - 8)
            self._layout_children()

    def _layout_children(self) -> None:
        width = self.width()
        height = self.height()
        if height <= 0:
            return

        pane_w = max(0.0, min(self._pane_w, float(width)))
        pane_h = self._pane_h if self._pane_h > 0 else float(height)
        pane_h = max(0.0, min(pane_h, float(height)))
        self._pane.setGeometry(round(self._pane_x), round(self._pane_y),
                               round(pane_w), round(pane_h))
        if pane_w < 1:
            self._pane.hide()
        else:
            self._pane.show()

        content_x = max(0.0, min(self._content_x, float(width)))
        self._content_card.setGeometry(round(content_x), 0,
                                       max(0, width - round(content_x)), height)

        if self._flyout_mode:
            self._shadow.setGeometry(
                round(self._pane_x) - SHADOW_MARGIN,
                round(self._pane_y) - SHADOW_MARGIN,
                round(pane_w) + SHADOW_MARGIN * 2,
                round(pane_h) + SHADOW_MARGIN * 2,
            )
            self._shadow.show()
            self._shadow.raise_()
        else:
            self._shadow.hide()

        if self._header is not None:
            self._header.move(HEADER_MARGIN, HEADER_MARGIN)
            self._header.raise_()

        self._content_card.lower()
        if self._flyout_mode:
            self._shadow.raise_()
        self._pane.raise_()
        if self._header is not None:
            self._header.raise_()


# ---------------------------------------------------------------------------
# 窄模式子菜单 Flyout
# ---------------------------------------------------------------------------


class _FlyoutSurface(QWidget):
    """Flyout 玻璃表面 + 子菜单行 + 指示器。"""

    def __init__(self, navigation, parent=None):
        super().__init__(parent)
        self._nav = navigation
        self._snapshot: QImage | None = None
        self._snapshot_origin = QPoint(0, 0)
        self.setAutoFillBackground(False)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(
            FLYOUT_PADDING_X, FLYOUT_PADDING_Y,
            FLYOUT_PADDING_X, FLYOUT_PADDING_Y,
        )
        self._layout.setSpacing(FLYOUT_ITEM_GAP)
        self._layout.addStretch(1)
        self._rows: list[_NavRow] = []
        self._indicator = _IndicatorOverlay(self, self)
        self._indicator.raise_()

    def add_row(self, row: _NavRow) -> None:
        self._rows.append(row)
        row.setParent(self)
        row.setFixedHeight(FLYOUT_ROW_HEIGHT)
        self._layout.insertWidget(max(0, self._layout.count() - 1), row)

    def refresh_theme(self) -> None:
        self._indicator.refresh()
        self._indicator.update()
        for row in self._rows:
            row.refresh_content()
        self.update()

    def set_snapshot(self, image: QImage | None, origin: QPoint) -> None:
        self._snapshot = image
        self._snapshot_origin = QPoint(origin)
        self.update()

    def shift_snapshot(self, dx: int, dy: int) -> None:
        """主窗口移动时同步玻璃快照的全局原点。"""
        if self._snapshot is not None:
            self._snapshot_origin += QPoint(int(dx), int(dy))
            self.update()

    def menu_visible_rect(self) -> QRect:
        return self.rect()

    def row_visible_for_indicator(self, row: QWidget | None) -> bool:
        if row is None or not row.isVisible():
            return False
        center_global = row.mapToGlobal(
            QPoint(row.width() // 2, row.height() // 2)
        )
        return self.rect().contains(self.mapFromGlobal(center_global))

    def indicator(self) -> _IndicatorOverlay:
        return self._indicator

    def sizeHint(self) -> QSize:
        hint = self._layout.sizeHint()
        return QSize(FLYOUT_WIDTH, max(1, hint.height()))

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        rect = QRectF(self.rect())
        style = FLYOUT_FOLD_GLASS
        radius = float(self._nav._theme["flyoutRadius"])
        path = rounded_path(rect, radius)
        painter.save()
        painter.setClipPath(path)
        base = QColor(style.tint)
        base.setAlpha(int(round(255 * style.opacity / 100.0)))
        painter.fillRect(rect, base)

        # Flyout 可能伸出主窗口：先用桌面/壁纸玻璃铺底，
        # 窗口内的部分再由主窗口快照覆盖，避免左侧出现纯色条。
        backdrop = self._nav.backdrop
        our_global = self.mapToGlobal(QPoint(0, 0))
        if backdrop is not None:
            global_rect = QRect(our_global, self.size())
            try:
                image, target = backdrop.source.processed_region(
                    global_rect, style.blur, style.brightness, style.saturation
                )
            except Exception:
                image, target = None, QRectF()
            if image is not None and not image.isNull():
                target = target.translated(-our_global.x(), -our_global.y())
                painter.drawImage(target, image)

        if self._snapshot is not None and not self._snapshot.isNull():
            dpr = float(self._snapshot.devicePixelRatio() or 1.0)
            offset = self._snapshot_origin - our_global
            target = QRectF(offset.x(), offset.y(),
                            self._snapshot.width() / dpr,
                            self._snapshot.height() / dpr)
            painter.drawImage(target, self._snapshot)
        painter.restore()
        paint_frost_overlay(painter, rect, style, radius=radius,
                            border=True, vignette=style.vignette)
        painter.end()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._indicator.setGeometry(self.rect())
        self._indicator.refresh()


class _SubmenuFlyout(QWidget):
    """窄模式下的子菜单浮窗：渐显 + 右移；失焦/点击外部关闭。"""

    def __init__(self, navigation, fold: NavFoldItem):
        super().__init__(None)
        self._nav = navigation
        self._fold = fold
        self.setWindowFlags(
            Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint |
            Qt.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)

        self._shadow = _PaneShadow(
            self, radius=int(navigation._theme["flyoutRadius"])
        )
        self._surface = _FlyoutSurface(navigation, self)
        self._surface.raise_()
        self._row_by_child: dict[NavItem, _NavRow] = {}
        for child in fold.children():
            # 子菜单不叠加 CHILD_INDENT，按顶层菜单的 12px 内容边距排版。
            row = _NavRow(child, compact=False, child=False,
                          content_margin=FLYOUT_CONTENT_MARGIN,
                          parent=self._surface)
            row.pressed.connect(child.pressed.emit)
            row.released.connect(child.released.emit)
            row.clicked.connect(
                lambda child=child: self._on_child_clicked(child)
            )
            self._surface.add_row(row)
            self._row_by_child[child] = row

        self._anim_pos: QPropertyAnimation | None = None
        self._anim_opacity: QPropertyAnimation | None = None
        self._closing = False

    def surface(self) -> _FlyoutSurface:
        return self._surface

    def refresh_theme(self) -> None:
        self._shadow.set_radius(int(self._nav._theme["flyoutRadius"]))
        self._surface.refresh_theme()

    def fold(self) -> NavFoldItem:
        return self._fold

    def row_for(self, child: NavItem) -> _NavRow | None:
        return self._row_by_child.get(child)

    def _on_child_clicked(self, child: NavItem) -> None:
        child.clicked.emit()
        self._nav._activate_child(child, from_submenu=True)

    # -- 展示 -------------------------------------------------------------
    def _final_geometry(self) -> QRect:
        surface_hint = self._surface.sizeHint()
        panel_w = FLYOUT_WIDTH
        panel_h = max(FLYOUT_ROW_HEIGHT + FLYOUT_PADDING_Y * 2,
                      surface_hint.height())
        window_w = panel_w + SHADOW_MARGIN * 2
        window_h = panel_h + SHADOW_MARGIN * 2

        main_global = self._nav.mapToGlobal(QPoint(0, 0))
        # 玻璃面板左边界 = 主窗口左边界 + 50px（外层窗口还要再让出阴影边距）。
        target_x = main_global.x() + FLYOUT_OFFSET_X - SHADOW_MARGIN

        # 第一个列表项的中线与展开项的中线对齐；空间不足时也不自动挪位置。
        first_center = FLYOUT_PADDING_Y + FLYOUT_ROW_HEIGHT / 2.0
        row = self._fold._row
        if row is not None:
            row_center = row.mapToGlobal(QPoint(0, row.height() // 2)).y()
            surface_top = row_center - first_center
            target_y = round(surface_top) - SHADOW_MARGIN
        else:
            target_y = main_global.y() + 8 - SHADOW_MARGIN

        return QRect(target_x, target_y, window_w, window_h)

    def _layout_children(self) -> None:
        self._shadow.setGeometry(self.rect())
        self._surface.setGeometry(SHADOW_MARGIN, SHADOW_MARGIN,
                                  self.width() - SHADOW_MARGIN * 2,
                                  self.height() - SHADOW_MARGIN * 2)
        self._shadow.lower()
        self._surface.raise_()

    def show_flyout(self) -> None:
        for anim in (self._anim_pos, self._anim_opacity):
            if anim is not None:
                anim.stop()
        snapshot = self._nav._grab_window_snapshot(FLYOUT_FOLD_GLASS)
        if snapshot is not None:
            self._surface.set_snapshot(snapshot[0], snapshot[1])
        final = self._final_geometry()
        self.setGeometry(final)
        self._layout_children()
        self.setWindowOpacity(0.0)
        self.move(final.x() - FLYOUT_OFFSET_X, final.y())
        self.show()
        self.raise_()

        self._closing = False
        self._anim_pos = QPropertyAnimation(self, b"pos", self)
        self._anim_pos.setDuration(ANIM_MS)
        self._anim_pos.setEasingCurve(QEasingCurve.OutCubic)
        self._anim_pos.setStartValue(QPoint(final.x() - FLYOUT_OFFSET_X, final.y()))
        self._anim_pos.setEndValue(final.topLeft())
        self._anim_pos.start()

        self._anim_opacity = QPropertyAnimation(self, b"windowOpacity", self)
        self._anim_opacity.setDuration(ANIM_MS)
        self._anim_opacity.setStartValue(0.0)
        self._anim_opacity.setEndValue(1.0)
        self._anim_opacity.start()

        self._setup_indicator()

    def _setup_indicator(self) -> None:
        self._surface.indicator().hide_indicator()
        if self._fold.layout is not None:
            return
        child = self._nav._selected_child
        if child is None or child._fold is not self._fold:
            return
        row = self._row_by_child.get(child)
        if row is None:
            return
        self._surface.indicator().set_row_animated_from(row, self._fold_row_y())

    def _fold_row_y(self) -> float:
        row = self._fold._row
        if row is None:
            return 0.0
        top_left = row.mapToGlobal(QPoint(0, 0))
        surface_top = self._surface.mapToGlobal(QPoint(0, 0))
        return float(top_left.y() - surface_top.y() + row.height() // 2)

    def close_flyout(self, animate: bool = True) -> None:
        if not self.isVisible() or self._closing:
            return
        self._closing = True
        for anim in (self._anim_pos, self._anim_opacity):
            if anim is not None:
                anim.stop()
        if not animate:
            self.hide()
            self._nav._on_submenu_closed(self)
            return
        start = self.geometry()
        self._anim_pos = QPropertyAnimation(self, b"pos", self)
        self._anim_pos.setDuration(INDICATOR_STEP_MS)
        self._anim_pos.setEasingCurve(QEasingCurve.InCubic)
        self._anim_pos.setStartValue(start.topLeft())
        self._anim_pos.setEndValue(QPoint(start.x() - FLYOUT_OFFSET_X, start.y()))
        self._anim_pos.start()

        self._anim_opacity = QPropertyAnimation(self, b"windowOpacity", self)
        self._anim_opacity.setDuration(INDICATOR_STEP_MS)
        self._anim_opacity.setStartValue(self.windowOpacity())
        self._anim_opacity.setEndValue(0.0)
        self._anim_opacity.finished.connect(self._finish_close)
        self._anim_opacity.start()

    def _finish_close(self) -> None:
        self.hide()
        self._nav._on_submenu_closed(self)

    def contains_widget(self, widget: QWidget | None) -> bool:
        if widget is None:
            return False
        return widget is self or self.isAncestorOf(widget)

    def move_with_window(self, dx: int, dy: int) -> None:
        """主窗口拖动时，Flyout 保持相对位置一起移动。"""
        if not self.isVisible() or self._closing or (not dx and not dy):
            return
        if (self._anim_pos is not None and
                self._anim_pos.state() == QAbstractAnimation.Running):
            self._anim_pos.stop()
            self._anim_pos = None
        self.move(self.pos() + QPoint(int(dx), int(dy)))
        self._surface.shift_snapshot(dx, dy)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._layout_children()


# ---------------------------------------------------------------------------
# NavigationView
# ---------------------------------------------------------------------------


class NavigationView(GlassWindowBase):
    """统一托管整个窗口的导航视图。

    ``show_pane`` 控制汉堡按钮（需求中 pane 指代汉堡按钮，而不是侧栏显隐）；
    ``show_back`` 控制返回按钮；``show_settings`` 控制内置设置项。

    示例::

        class DemoWindow(NavigationView):
            def __init__(self):
                super().__init__()
                self.addNavItem("\\uE80F", "主页", layout)
                self.setSelectedNavItem(0)
    """

    selectedChanged = Signal(int)
    paneStateChanged = Signal(bool, object, object, bool)

    # -- QSS 可覆盖的主题（默认值见 THEME_DEFAULTS） ---------------------
    selectedBg = _theme_qcolor("selectedBg")
    selectedHoverBg = _theme_qcolor("selectedHoverBg")
    selectedPressedBg = _theme_qcolor("selectedPressedBg")
    hoverBg = _theme_qcolor("hoverBg")
    pressedBg = _theme_qcolor("pressedBg")
    textColor = _theme_qcolor("textColor")
    pressedText = _theme_qcolor("pressedText")
    separatorColor = _theme_qcolor("separatorColor")
    dividerColor = _theme_qcolor("dividerColor")
    indicatorColor = _theme_qcolor("indicatorColor")
    indicatorWidth = _theme_int("indicatorWidth")
    indicatorHeight = _theme_int("indicatorHeight")
    navItemRadius = _theme_int("navItemRadius")
    flyoutRadius = _theme_int("flyoutRadius")
    flyoutItemRadius = _theme_int("flyoutItemRadius")

    def __init__(self, show_pane: bool = True, show_back: bool = True,
                 show_settings: bool = True, hide_threshold: int = 700,
                 compact_threshold: int = 1000, MinWidth: int = 0,
                 MaxWidth: int = 0, MinHeight: int = 0, MaxHeight: int = 0):
        super().__init__()
        # 内容区使用 glasskit 自带的全窗口玻璃；侧边栏/飞窗各自覆盖。
        self.setBrush(BUBBLE_BACKGROUND_NORMAL)
        self.setWindowTitle("NavigationView")
        self._theme = dict(THEME_DEFAULTS)
        self._ready = False

        self._show_pane = bool(show_pane)
        self._show_back = bool(show_back)
        self._show_settings = bool(show_settings)
        self._hide_threshold = max(0, int(hide_threshold))
        self._compact_threshold = max(0, int(compact_threshold))
        if self._compact_threshold < self._hide_threshold:
            warnings.warn("compact_threshold 小于 hide_threshold，已按 hide_threshold 处理",
                          RuntimeWarning, stacklevel=2)
            self._compact_threshold = self._hide_threshold

        # -- 模型与状态 ---------------------------------------------------
        self._menu_entries: list = []
        self._nav_items: list[NavItem] = []
        self._fold_items: list[NavFoldItem] = []
        self._selected_top = None
        self._selected_child = None
        self._settings_selected = False
        self._last_selected_index = -1
        self._last_selected_key = None
        self._history: list[dict] = []
        self._history_limit = HISTORY_LIMIT
        self._remembered_folds: set[NavFoldItem] = set()

        self._pane_state = PaneStateEnum.Auto
        self._show_inline = PaneShowInlineEnum.Auto
        self._effective_state: PaneStateEnum | None = None
        self._presentation_flyout = False
        self._last_base: PaneStateEnum | None = None
        self._last_state_tuple: tuple | None = None
        self._was_visually_expanded: bool | None = None
        self._pane_open_inline = True
        self._pane_flyout_open = False

        self._submenu: _SubmenuFlyout | None = None
        self._app_filter_installed = False
        self._content_revision = 0
        self._last_clearance = 0
        self._pane_snapshot_cache: tuple | None = None
        self._window_snapshot_cache: tuple | None = None
        self._last_window_pos = QPoint(0, 0)
        self._pane_snapshot_timer = QTimer(self)
        self._pane_snapshot_timer.setSingleShot(True)
        self._pane_snapshot_timer.setInterval(ANIM_MS + 30)
        self._pane_snapshot_timer.timeout.connect(
            self._capture_pane_snapshot_if_needed
        )

        self._layout_owner: dict[int, object] = {}
        self._layout_registry: dict[int, tuple[object, QWidget]] = {}
        self._layout_pool = QWidget(self)
        self._layout_pool.hide()

        # -- 界面 ---------------------------------------------------------
        self._root = _RootCanvas(self)
        self.content_layout.addWidget(self._root)
        self._content_card = self._root.content_card()
        self._content_host = self._content_card.content_host()
        self._pane = self._root.pane()

        buttons: list[AnimatedIconButton] = []
        self._hamburger: AnimatedIconButton | None = None
        self._back: AnimatedIconButton | None = None
        if self._show_pane:
            self._hamburger = AnimatedIconButton("hamburger", parent=self._root)
            self._hamburger.clicked.connect(self._toggle_pane)
            buttons.append(self._hamburger)
        if self._show_back:
            self._back = AnimatedIconButton("back", parent=self._root)
            self._back.clicked.connect(self._go_back)
            self._back.setEnabled(False)
            buttons.append(self._back)
        self._header = _HeaderBar(buttons, self._root)
        self._root.attach_header(self._header)
        if not buttons:
            self._header.hide()

        self._settings_item: NavItem | None = None
        self._settings_row: _NavRow | None = None
        if self._show_settings:
            self._settings_item = NavItem(self, SETTINGS_GLYPH, "设置",
                                          layout=None, settings=True)
            self._settings_item.clicked.connect(self._activate_settings)
            self._settings_row = self._create_row(self._settings_item, child=False)
            wrapper = _wrap_row(self._settings_row)
            self._pane.set_settings_widget(wrapper, self._settings_row)

        self._apply_size_limits(MinWidth, MaxWidth, MinHeight, MaxHeight)
        self._sync_app_filter()

        self.resize(1180, 760)
        self._ready = True
        self._reset_open_flags()
        self._apply_pane_state(manual=False, animate=False, force=True)
        self._update_back_enabled()

    # ------------------------------------------------------------------
    # 构造辅助
    # ------------------------------------------------------------------
    def _apply_size_limits(self, min_w: int, max_w: int,
                           min_h: int, max_h: int) -> None:
        min_w = max(0, int(min_w))
        max_w = max(0, int(max_w))
        min_h = max(0, int(min_h))
        max_h = max(0, int(max_h))
        if max_w > 0 and min_w > max_w:
            warnings.warn("MinWidth 大于 MaxWidth，已夹紧", RuntimeWarning, stacklevel=2)
            min_w = max_w
        if max_h > 0 and min_h > max_h:
            warnings.warn("MinHeight 大于 MaxHeight，已夹紧", RuntimeWarning, stacklevel=2)
            min_h = max_h
        self.setMinimumWidth(min_w)
        self.setMaximumWidth(max_w if max_w > 0 else _QWIDGETSIZE_MAX)
        self.setMinimumHeight(min_h)
        self.setMaximumHeight(max_h if max_h > 0 else _QWIDGETSIZE_MAX)

    def _refresh_theme(self) -> None:
        """QSS 主题变化后刷新所有自绘控件。"""
        if not hasattr(self, "_theme"):
            return
        for item in getattr(self, "_nav_items", ()):
            if getattr(item, "isValid", lambda: False)() and item._row is not None:
                item._row.refresh_content()
        for fold in getattr(self, "_fold_items", ()):
            if not getattr(fold, "isValid", lambda: False)():
                continue
            if fold._row is not None:
                fold._row.refresh_content()
            for child in fold._children:
                if child.isValid() and child._row is not None:
                    child._row.refresh_content()
        if getattr(self, "_settings_row", None) is not None:
            self._settings_row.refresh_content()
        pane = getattr(self, "_pane", None)
        if pane is not None:
            pane.refresh_theme()
        card = getattr(self, "_content_card", None)
        if card is not None:
            card.update()
        submenu = getattr(self, "_submenu", None)
        if submenu is not None:
            submenu.refresh_theme()

    def _create_row(self, item, child: bool = False) -> _NavRow:
        row: _NavRow
        if isinstance(item, NavFoldItem):
            row = _FoldRow(item, compact=not self._visually_expanded(), child=child)
        else:
            row = _NavRow(item, compact=not self._visually_expanded(), child=child)
        row.pressed.connect(item.pressed.emit)
        row.released.connect(item.released.emit)
        row.clicked.connect(item.clicked.emit)
        item._row = row
        return row

    def _build_top_item(self, item) -> None:
        if isinstance(item, NavFoldItem):
            row = self._create_row(item)
            group = _FoldGroup(item, row)
            item._group = group
            group.body().heightChanged.connect(self._on_layout_shifted)
            item.clicked.connect(lambda item=item: self._activate_fold(item))
            self._pane.add_menu_widget(group)
        else:
            row = self._create_row(item)
            wrapper = _wrap_row(row)
            item._wrapper = wrapper
            item.clicked.connect(lambda item=item: self._activate_nav_item(item))
            self._pane.add_menu_widget(wrapper)
        item._row.set_compact(not self._visually_expanded())

    # ------------------------------------------------------------------
    # 公共 API：添加 / 修改 / 删除
    # ------------------------------------------------------------------
    def addNavItem(self, fonticon: str, name: str, layout=None) -> NavItem:
        """添加普通菜单项；返回 NavItem。"""
        item = NavItem(self, fonticon, name, layout=None)
        self._nav_items.append(item)
        self._menu_entries.append(item)
        self._build_top_item(item)
        self._set_item_layout(item, layout)
        self._refresh_indices()
        return item

    def addNavFoldItem(self, fonticon: str, name: str, layout=None) -> NavFoldItem:
        """添加折叠菜单项；layout 可选，有 layout 时点击标题会同时展开并切换内容。"""
        fold = NavFoldItem(self, fonticon, name, layout=None)
        self._fold_items.append(fold)
        self._menu_entries.append(fold)
        self._build_top_item(fold)
        self._set_item_layout(fold, layout)
        self._refresh_indices()
        return fold

    def _add_child(self, fold: NavFoldItem, fonticon: str, name: str,
                   layout) -> NavItem:
        if not fold.isValid():
            raise RuntimeError("该 NavFoldItem 已被移除")
        if fold._group is None:
            raise RuntimeError("折叠菜单尚未完成构建")
        child = NavItem(self, fonticon, name, layout=None, fold=fold)
        fold._children.append(child)
        row = self._create_row(child, child=True)
        child.clicked.connect(lambda child=child: self._activate_child(child))
        fold._group.add_child(row)
        self._set_item_layout(child, layout)
        self._refresh_indices()
        return child

    def addSeparator(self, text: str):
        entry = _SeparatorEntry(text)
        widget = _SeparatorWidget(text, navigation=self)
        entry.widget = widget
        widget.heightChanged.connect(self._on_layout_shifted)
        self._menu_entries.append(entry)
        self._pane.add_menu_widget(widget)
        widget.set_compact(not self._visually_expanded(), animate=False)
        return widget

    def addSeparateLine(self):
        """添加一条与设置项上方同款的 1px 分割线。"""
        entry = _LineEntry()
        line = _SettingsDivider(self)
        wrapper = QWidget()
        wrapper.setFixedHeight(SETTINGS_DIVIDER_HEIGHT + ROW_MARGIN_TOP * 2)
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(0, ROW_MARGIN_TOP, 0, ROW_MARGIN_TOP)
        layout.setSpacing(0)
        layout.addWidget(line)
        entry.widget = wrapper
        wrapper.setVisible(self._visually_expanded())
        self._menu_entries.append(entry)
        self._pane.add_menu_widget(wrapper)
        return line

    def setSelectedNavItem(self, index: int) -> None:
        """按全局选择索引选中（含折叠项）；-1 清空；程序化选中不播放点击动画。"""
        index = int(index)
        if index == -1:
            self._close_submenu(animate=False)
            self._clear_selection()
            return
        entries = self._selectable_entries()
        if index < 0 or index >= len(entries):
            raise IndexError(f"导航索引越界: {index}（共 {len(entries)} 项）")
        entry = entries[index]
        self._close_submenu(animate=False)
        self._select_target(top=entry, child=None, settings=False,
                            animate=False, record=False)

    def setNavItem(self, index: int, fonticon=_UNSET, name=_UNSET,
                   layout=_UNSET) -> None:
        """按普通项内部索引修改；只更新传入的参数，layout=None 表示清空。"""
        index = int(index)
        if index < 0 or index >= len(self._nav_items):
            raise IndexError(f"普通菜单索引越界: {index}")
        item = self._nav_items[index]
        if not item.isValid():
            raise RuntimeError("该 NavItem 已被移除")
        if fonticon is not _UNSET:
            item.fonticon = fonticon
        if name is not _UNSET:
            item.name = name
        if layout is not _UNSET:
            self._set_item_layout(item, layout)
        self._refresh_item(item)

    def setSettingLayout(self, layout) -> None:
        if self._settings_item is None:
            raise RuntimeError("show_settings=False，当前没有设置菜单项")
        self._set_item_layout(self._settings_item, layout)

    def removeNavItem(self, index: int) -> None:
        """按普通项内部索引删除，并使对应 NavItem 逻辑失效。"""
        index = int(index)
        if index < 0 or index >= len(self._nav_items):
            raise IndexError(f"普通菜单索引越界: {index}")
        self._close_submenu(animate=False)
        item = self._nav_items[index]
        if self._selected_top is item:
            self._clear_selection(notify=False)
        self._unmount_layout(item)
        self._drop_page(item)
        if item._wrapper is not None:
            self._pane.remove_menu_widget(item._wrapper)
        item._invalidate()
        self._nav_items.pop(index)
        if item in self._menu_entries:
            self._menu_entries.remove(item)
        self._sanitize_history()
        self._refresh_indices()
        self._update_back_enabled()
        self._update_indicator(animate=False)
        self._notify_selected_changed()

    def removeNavFoldItem(self, index: int) -> None:
        """按折叠项内部索引删除（连同子项），相关模型全部逻辑失效。"""
        index = int(index)
        if index < 0 or index >= len(self._fold_items):
            raise IndexError(f"折叠菜单索引越界: {index}")
        self._close_submenu(animate=False)
        fold = self._fold_items[index]
        involved = (self._selected_top is fold or
                    (self._selected_child is not None and
                     self._selected_child._fold is fold))
        if involved:
            self._clear_selection(notify=False)
        for child in list(fold._children):
            self._unmount_layout(child)
            self._drop_page(child)
        self._unmount_layout(fold)
        self._drop_page(fold)
        if fold._group is not None:
            self._pane.remove_menu_widget(fold._group)
        fold._invalidate()
        self._fold_items.pop(index)
        if fold in self._menu_entries:
            self._menu_entries.remove(fold)
        self._sanitize_history()
        self._refresh_indices()
        self._update_back_enabled()
        self._update_indicator(animate=False)
        self._notify_selected_changed()

    def CleatNavItems(self) -> None:
        """清空普通项、折叠项与分隔符（保留设置项）。"""
        self._close_submenu(animate=False)
        self._clear_selection(notify=False)
        for item in list(self._nav_items):
            self._unmount_layout(item)
            self._drop_page(item)
            if item._wrapper is not None:
                self._pane.remove_menu_widget(item._wrapper)
            item._invalidate()
        for fold in list(self._fold_items):
            for child in list(fold._children):
                self._unmount_layout(child)
                self._drop_page(child)
            self._unmount_layout(fold)
            self._drop_page(fold)
            if fold._group is not None:
                self._pane.remove_menu_widget(fold._group)
            fold._invalidate()
        for entry in list(self._menu_entries):
            if isinstance(entry, (_SeparatorEntry, _LineEntry)) and entry.widget is not None:
                self._pane.remove_menu_widget(entry.widget)
                entry.widget.deleteLater()
        self._nav_items.clear()
        self._fold_items.clear()
        self._menu_entries.clear()
        self._remembered_folds.clear()
        self._history.clear()
        self._update_back_enabled()
        self._update_indicator(animate=False)
        self._notify_selected_changed()

    def clearNavItems(self) -> None:
        self.CleatNavItems()

    # ------------------------------------------------------------------
    # 公共 API：形态 / 查询
    # ------------------------------------------------------------------
    def setPaneState(self, state) -> None:
        state = _coerce_pane_state(state)
        if state is self._pane_state:
            return
        self._pane_state = state
        self._reset_open_flags()
        self._apply_pane_state(manual=False, animate=True, force=True)

    def setExpandedShowInline(self, mode) -> None:
        mode = _coerce_show_inline(mode)
        if mode is self._show_inline:
            return
        self._show_inline = mode
        self._reset_open_flags()
        self._apply_pane_state(manual=False, animate=True, force=True)

    def paneState(self) -> PaneStateEnum:
        return self._pane_state

    def expandedShowInline(self) -> PaneShowInlineEnum:
        return self._show_inline

    def effectivePaneState(self) -> PaneStateEnum | None:
        return self._effective_state

    def usesFlyout(self) -> bool:
        return self._presentation_flyout

    def indexOf(self, item) -> int:
        if item is None:
            return -1
        fold = getattr(item, "_fold", None)
        if fold is not None:
            return fold.globalIndex
        return self._global_index_of(item)

    def currentSelection(self):
        """当前选中的 NavItem / NavFoldItem；设置项返回内置设置 NavItem。"""
        return self._current_target()

    def setHistoryLimit(self, limit: int) -> None:
        self._history_limit = max(0, int(limit))
        while len(self._history) > self._history_limit:
            self._history.pop(0)
        self._update_back_enabled()

    def historyLimit(self) -> int:
        return self._history_limit

    # ------------------------------------------------------------------
    # 选择模型
    # ------------------------------------------------------------------
    def _selectable_entries(self) -> list:
        return [entry for entry in self._menu_entries
                if isinstance(entry, (NavItem, NavFoldItem))]

    def _global_index_of(self, item) -> int:
        index = 0
        for entry in self._menu_entries:
            if isinstance(entry, (NavItem, NavFoldItem)):
                if entry is item:
                    return index
                index += 1
        return -1

    def _selection_index(self) -> int:
        if self._settings_selected:
            return -1
        if self._selected_child is not None:
            return self._selected_child._fold.globalIndex
        if self._selected_top is not None:
            return self._selected_top.globalIndex
        return -1

    def _selection_key(self):
        if self._settings_selected:
            return ("settings", None)
        if self._selected_child is not None:
            return ("child", self._selected_child)
        if self._selected_top is not None:
            return ("top", self._selected_top)
        return None

    def _current_target(self):
        if self._settings_selected:
            return self._settings_item
        if self._selected_child is not None:
            return self._selected_child
        return self._selected_top

    def _visually_expanded(self) -> bool:
        return self._effective_state is PaneStateEnum.Expanded

    def _refresh_indices(self) -> None:
        for index, item in enumerate(self._nav_items):
            item._index = index if item.isValid() else -1
        for index, fold in enumerate(self._fold_items):
            fold._index = index if fold.isValid() else -1
            for child_index, child in enumerate(fold._children):
                child._index = child_index if child.isValid() else -1

    def _sync_selection_models(self) -> None:
        for item in self._nav_items:
            if item.isValid():
                item._set_selected(
                    self._selected_top is item and self._selected_child is None
                )
        for fold in self._fold_items:
            if not fold.isValid():
                continue
            branch = (self._selected_top is fold or
                      (self._selected_child is not None and
                       self._selected_child._fold is fold))
            fold._set_selected(branch)
            for child in fold._children:
                if child.isValid():
                    child._set_selected(self._selected_child is child)
            if (self._selected_child is not None and
                    self._selected_child._fold is fold and
                    self._selected_child in fold._children):
                child_index = fold._children.index(self._selected_child)
            else:
                child_index = -1
            if branch or fold._last_child_selected is not None:
                fold._emit_child_selected(child_index)
        if self._settings_item is not None:
            self._settings_item._set_selected(self._settings_selected)

    def _notify_selected_changed(self) -> None:
        key = self._selection_key()
        value = self._selection_index()
        if key == self._last_selected_key and value == self._last_selected_index:
            return
        self._last_selected_key = key
        self._last_selected_index = value
        self.selectedChanged.emit(value)

    def _push_history(self) -> None:
        snapshot = {
            "top": self._selected_top,
            "child": self._selected_child,
            "settings": self._settings_selected,
            "folds": {fold: fold._expanded for fold in self._fold_items
                      if fold.isValid()},
        }
        self._history.append(snapshot)
        while len(self._history) > self._history_limit:
            self._history.pop(0)
        self._update_back_enabled()

    def _update_back_enabled(self) -> None:
        if self._back is not None:
            self._back.setEnabled(bool(self._history))

    def _sanitize_history(self) -> None:
        """结构性删除后移除失效目标，保留仍然可用的返回步骤。"""
        cleaned = []
        for snapshot in self._history:
            top = snapshot.get("top")
            child = snapshot.get("child")
            if top is not None and not getattr(top, "isValid", lambda: False)():
                continue
            if child is not None:
                if not getattr(child, "isValid", lambda: False)():
                    continue
                if not getattr(child._fold, "isValid", lambda: False)():
                    continue
            folds = {}
            for fold, expanded in snapshot.get("folds", {}).items():
                if getattr(fold, "isValid", lambda: False)():
                    folds[fold] = expanded
            snapshot["folds"] = folds
            cleaned.append(snapshot)
        self._history = cleaned
        self._update_back_enabled()

    def _select_target(self, *, top, child, settings: bool,
                       animate: bool, record: bool) -> None:
        new_top = None if settings else top
        new_child = None if settings else child
        if (settings == self._settings_selected and
                new_top is self._selected_top and
                new_child is self._selected_child):
            return
        if record:
            self._push_history()
        self._settings_selected = bool(settings)
        self._selected_top = new_top
        self._selected_child = new_child

        if (new_child is not None and self._visually_expanded() and
                not new_child._fold._expanded):
            self._set_fold_expanded(new_child._fold, True,
                                    animate=animate, sync_indicator=False)

        self._sync_selection_models()
        self._update_indicator(animate=animate)
        self._show_content_for(self._current_target(), animate=animate)
        self._notify_selected_changed()
        self._update_back_enabled()

    def _clear_selection(self, notify: bool = True) -> None:
        if (self._selected_top is None and self._selected_child is None and
                not self._settings_selected):
            return
        self._selected_top = None
        self._selected_child = None
        self._settings_selected = False
        self._sync_selection_models()
        self._update_indicator(animate=False)
        self._show_content_for(None, animate=False)
        if notify:
            self._notify_selected_changed()

    def _go_back(self) -> None:
        if not self._history:
            return
        snapshot = self._history.pop()
        self._close_submenu(animate=False)

        folds = snapshot.get("folds", {})
        if self._visually_expanded():
            for fold, expanded in folds.items():
                if isinstance(fold, NavFoldItem) and fold.isValid():
                    self._set_fold_expanded(fold, bool(expanded),
                                            animate=True, sync_indicator=False)
        else:
            self._remembered_folds = {
                fold for fold, expanded in folds.items()
                if expanded and isinstance(fold, NavFoldItem) and fold.isValid()
            }

        top = snapshot.get("top")
        child = snapshot.get("child")
        settings = bool(snapshot.get("settings"))
        if top is not None and not getattr(top, "isValid", lambda: False)():
            top = None
        if child is not None and not getattr(child, "isValid", lambda: False)():
            child = None
        if child is not None:
            parent = child._fold
            if not parent.isValid():
                child = None
            elif top is not parent:
                top = parent
        if settings and self._settings_item is not None:
            self._selected_top = None
            self._selected_child = None
            self._settings_selected = True
        else:
            self._settings_selected = False
            self._selected_top = top
            self._selected_child = child
        if (self._selected_child is not None and self._visually_expanded() and
                not self._selected_child._fold._expanded):
            self._set_fold_expanded(self._selected_child._fold, True,
                                    animate=True, sync_indicator=False)

        self._sync_selection_models()
        self._update_indicator(animate=True)
        self._show_content_for(self._current_target(), animate=True)
        self._notify_selected_changed()
        self._update_back_enabled()

    # ------------------------------------------------------------------
    # 交互入口
    # ------------------------------------------------------------------
    def _activate_nav_item(self, item: NavItem) -> None:
        if not item.isValid():
            return
        self._close_submenu(animate=False)
        if item._fold is not None:
            self._activate_child(item)
            return
        self._select_target(top=item, child=None, settings=False,
                            animate=True, record=True)

    def _activate_fold(self, fold: NavFoldItem) -> None:
        if not fold.isValid():
            return
        if not self._visually_expanded():
            if fold.layout is not None:
                self._select_target(top=fold, child=None, settings=False,
                                    animate=True, record=True)
            self._toggle_submenu(fold)
            return

        self._close_submenu(animate=False)
        self._set_fold_expanded(fold, not fold._expanded, animate=True)
        if fold.layout is not None:
            self._select_target(top=fold, child=None, settings=False,
                                animate=True, record=True)

    def _activate_child(self, child: NavItem, from_submenu: bool = False) -> None:
        if not child.isValid():
            return
        self._select_target(top=child._fold, child=child, settings=False,
                            animate=True, record=True)
        if from_submenu:
            self._close_submenu(animate=True)

    def _activate_settings(self) -> None:
        if self._settings_item is None or not self._settings_item.isValid():
            return
        self._close_submenu(animate=False)
        self._select_target(top=None, child=None, settings=True,
                            animate=True, record=True)

    # ------------------------------------------------------------------
    # 折叠 / 指示器 / 内容
    # ------------------------------------------------------------------
    def _set_fold_expanded(self, fold: NavFoldItem, expanded: bool,
                           animate: bool = True,
                           sync_indicator: bool = True) -> None:
        if not fold.isValid():
            return
        expanded = bool(expanded)
        if expanded and not self._visually_expanded():
            # 压缩/隐藏时只记住状态，展开分类时再恢复。
            self._remembered_folds.add(fold)
            return
        if (not expanded and not self._visually_expanded() and
                not fold._expanded):
            self._remembered_folds.discard(fold)
            return
        if fold._expanded == expanded:
            if fold._group is not None:
                fold._group.set_expanded(expanded, animate=False)
            return
        fold._set_expanded(expanded)
        if fold._group is not None:
            fold._group.set_expanded(expanded, animate=animate)
        if sync_indicator:
            self._update_indicator(animate=animate)

    def _indicator_target(self):
        if self._settings_selected:
            return self._settings_item
        if self._selected_child is not None:
            fold = self._selected_child._fold
            if (self._submenu is not None and fold.layout is None and
                    self._submenu.fold() is fold):
                return None
            if self._visually_expanded() and fold._expanded:
                return self._selected_child
            return fold
        return self._selected_top

    def _update_indicator(self, animate: bool = True, retry: bool = True) -> None:
        target = self._indicator_target()
        row = target._row if target is not None else None
        indicator = self._pane.indicator()
        indicator.set_row(row, animate=animate)
        for fold in self._fold_items:
            if fold.isValid() and fold._row is not None:
                fold._row.set_selected(target is fold)
        self._update_submenu_selection()
        # 刚添加到滚动区、尚未完成布局的行会暂时不可见；下一轮事件循环再刷新一次。
        if retry and row is not None and indicator._row is None:
            QTimer.singleShot(0, lambda: self._update_indicator(False, retry=False))

    def _update_submenu_selection(self) -> None:
        if self._submenu is None:
            return
        for child in self._submenu.fold().children():
            row = self._submenu.row_for(child)
            if row is not None:
                row.set_selected(self._selected_child is child)

    def _on_layout_shifted(self) -> None:
        if self._pane.indicator().is_animating():
            return
        self._update_indicator(animate=False)

    def _ensure_page(self, item: NavItem | NavFoldItem) -> _ContentPage | None:
        if item is None or not item.isValid() or item.layout is None:
            return None
        page = item._page
        if page is None:
            page = _ContentPage()
            self._content_host.register_page(page)
            item._page = page
        key = id(item.layout)
        entry = self._layout_registry.get(key)
        if entry is None or entry[0] is not item.layout:
            return None
        host = entry[1]
        self._detach_host_from_pages(host)
        page.add_host(host)
        host.show()
        return page

    def _show_content_for(self, target, animate: bool) -> None:
        if (target is None or
                not getattr(target, "isValid", lambda: True)() or
                getattr(target, "layout", None) is None):
            if self._content_host.current_page() is not None:
                self._content_host.show_page(None, False)
                self._content_revision += 1
            return
        page = self._ensure_page(target)
        if page is None:
            return
        changed = self._content_host.current_page() is not page
        self._content_host.show_page(page, animate if changed else False)
        if changed:
            self._content_revision += 1
            self._schedule_pane_snapshot()

    def _drop_page(self, item) -> None:
        page = getattr(item, "_page", None)
        if page is not None:
            self._content_host.remove_page(page)
            item._page = None

    def _detach_host_from_pages(self, host: QWidget) -> None:
        for page in self._content_host.pages():
            page.remove_host(host)

    # ------------------------------------------------------------------
    # Layout 所有权
    # ------------------------------------------------------------------
    def _make_host(self, layout) -> QWidget:
        if isinstance(layout, QWidget):
            return layout
        if not isinstance(layout, QLayout):
            raise TypeError("layout 必须是 QLayout 或 QWidget")
        parent_widget = layout.parentWidget()
        if parent_widget is not None and parent_widget.layout() is layout:
            return parent_widget
        if layout.parent() is not None:
            raise ValueError("layout 不能是另一个布局的子布局")
        host = _LayoutHost()
        host.setAutoFillBackground(False)
        host.setLayout(layout)
        return host

    def _host_for_layout(self, layout) -> QWidget:
        key = id(layout)
        entry = self._layout_registry.get(key)
        if entry is not None and entry[0] is layout:
            return entry[1]
        host = self._make_host(layout)
        self._layout_registry[key] = (layout, host)
        return host

    def _park_host(self, host: QWidget) -> None:
        self._detach_host_from_pages(host)
        host.hide()
        host.setParent(self._layout_pool)

    def _unmount_layout(self, item) -> None:
        layout = getattr(item, "_layout", None)
        if layout is None:
            return
        key = id(layout)
        item._layout = None
        if self._layout_owner.get(key) is item:
            self._layout_owner.pop(key, None)
        entry = self._layout_registry.get(key)
        if entry is not None:
            self._park_host(entry[1])
        if self._current_target() is item:
            self._show_content_for(None, animate=False)

    def _set_item_layout(self, item, layout) -> None:
        if not item.isValid():
            raise RuntimeError("目标菜单项已被移除")
        if layout is item._layout:
            return
        if item._layout is not None:
            self._unmount_layout(item)

        if layout is None:
            if self._current_target() is item:
                self._show_content_for(None, animate=False)
            self._content_revision += 1
            self._schedule_pane_snapshot()
            return

        existing = self._layout_owner.get(id(layout))
        if existing is not None and existing is not item:
            warnings.warn(
                f"layout 已挂载在 {existing!r}，后挂载的 {item!r} 生效，"
                "前一个菜单项已取消挂载",
                RuntimeWarning, stacklevel=3,
            )
            if getattr(existing, "_layout", None) is layout:
                existing._layout = None
                self._layout_owner.pop(id(layout), None)
                entry = self._layout_registry.get(id(layout))
                if entry is not None:
                    self._park_host(entry[1])
                if self._current_target() is existing:
                    self._show_content_for(None, animate=False)

        host = self._host_for_layout(layout)
        self._layout_owner[id(layout)] = item
        item._layout = layout
        page = self._ensure_page(item)
        if page is not None:
            self._detach_host_from_pages(host)
            page.add_host(host)
            host.show()
        if self._current_target() is item:
            self._show_content_for(item, animate=False)
        self._content_revision += 1
        self._schedule_pane_snapshot()

    def _schedule_pane_snapshot(self) -> None:
        if (self._effective_state is PaneStateEnum.Expanded and
                self._presentation_flyout):
            self._pane_snapshot_timer.start(ANIM_MS + 30)

    def _refresh_item(self, item) -> None:
        row = getattr(item, "_row", None)
        if row is not None:
            row.refresh_content()
        if self._submenu is not None and isinstance(item, NavItem):
            flyout_row = self._submenu.row_for(item)
            if flyout_row is not None:
                flyout_row.refresh_content()

    # ------------------------------------------------------------------
    # 形态计算
    # ------------------------------------------------------------------
    def _base_state(self) -> PaneStateEnum:
        state = self._pane_state
        width = max(1, self.width())
        if state is PaneStateEnum.Auto:
            if width > self._compact_threshold:
                return PaneStateEnum.Expanded
            if width < self._hide_threshold:
                return PaneStateEnum.Hide
            return PaneStateEnum.Compact
        if state is PaneStateEnum.Expanded:
            return PaneStateEnum.Expanded
        if state in (PaneStateEnum.Compact, PaneStateEnum.ForceCompact):
            return PaneStateEnum.Compact
        return PaneStateEnum.Hide

    def _is_flyout_presentation(self) -> bool:
        mode = self._show_inline
        if mode is PaneShowInlineEnum.Inline:
            return False
        if mode is PaneShowInlineEnum.Flyout:
            return True
        if self._pane_state in (PaneStateEnum.Compact, PaneStateEnum.Expanded):
            return False
        if self._pane_state in (PaneStateEnum.ForceCompact, PaneStateEnum.Hide):
            return True
        return self.width() <= self._compact_threshold

    def _reset_open_flags(self) -> None:
        base = self._base_state()
        flyout = self._is_flyout_presentation()
        self._last_base = base
        if base is PaneStateEnum.Expanded:
            self._pane_flyout_open = flyout
            self._pane_open_inline = not flyout
        else:
            self._pane_flyout_open = False
            self._pane_open_inline = False

    def _compute_effective(self) -> tuple[PaneStateEnum, bool]:
        base = self._base_state()
        flyout = self._is_flyout_presentation()
        if base is PaneStateEnum.Expanded:
            opened = self._pane_flyout_open if flyout else self._pane_open_inline
            return (PaneStateEnum.Expanded if opened else PaneStateEnum.Compact), flyout
        if base is PaneStateEnum.Compact:
            opened = self._pane_flyout_open if flyout else self._pane_open_inline
            return (PaneStateEnum.Expanded if opened else PaneStateEnum.Compact), flyout
        opened = self._pane_flyout_open if flyout else self._pane_open_inline
        return (PaneStateEnum.Expanded if opened else PaneStateEnum.Hide), flyout

    def _target_geometry(self) -> dict:
        base = self._base_state()
        rail = 0 if base is PaneStateEnum.Hide else COMPACT_WIDTH
        height = float(max(1, self.height()))
        effective = self._effective_state or base
        if effective is PaneStateEnum.Expanded:
            if self._presentation_flyout:
                return {
                    "pane_width": float(EXPANDED_WIDTH), "pane_x": 4.0,
                    "pane_y": 4.0, "pane_height": max(0.0, height - 8),
                    "content_x": float(rail), "flyout": True,
                }
            return {
                "pane_width": float(EXPANDED_WIDTH), "pane_x": 0.0,
                "pane_y": 0.0, "pane_height": height,
                "content_x": float(EXPANDED_WIDTH), "flyout": False,
            }
        if effective is PaneStateEnum.Compact:
            return {
                "pane_width": float(rail), "pane_x": 0.0,
                "pane_y": 0.0, "pane_height": height,
                "content_x": float(rail), "flyout": False,
            }
        return {
            "pane_width": 0.0, "pane_x": 0.0, "pane_y": 0.0,
            "pane_height": height, "content_x": 0.0, "flyout": False,
        }

    def _apply_pane_state(self, manual: bool, animate: bool = True,
                          force: bool = False) -> None:
        base = self._base_state()
        presentation = self._is_flyout_presentation()
        effective, _ = self._compute_effective()
        old_effective = self._effective_state
        old_presentation = self._presentation_flyout
        was_flyout_visible = (old_effective is PaneStateEnum.Expanded and
                              old_presentation)

        new_tuple = (effective, presentation)
        if (not force and old_effective is not None and
                new_tuple == self._last_state_tuple):
            self._sync_geometry()
            return

        if (effective is not PaneStateEnum.Compact and
                self._submenu is not None):
            self._close_submenu(animate=False)

        self._effective_state = effective
        self._presentation_flyout = presentation
        self._last_base = base
        self._root.set_base_width(0 if base is PaneStateEnum.Hide else COMPACT_WIDTH)

        expanded = effective is PaneStateEnum.Expanded
        flyout_visual = ((expanded and presentation) or
                         (not expanded and was_flyout_visible and animate))
        self._pane.set_flyout(flyout_visual)
        self._update_header(expanded)
        if expanded and presentation:
            self._capture_pane_snapshot_if_needed()
        self._apply_visual_expansion(expanded, animate=animate)
        self._pane.set_compact(not expanded)

        target = self._target_geometry()
        duration = ANIM_MS if animate and self.isVisible() else 0

        def finish() -> None:
            if not expanded or not presentation:
                self._pane.set_flyout(False)
                self._root.set_flyout_mode(False)
            if expanded and presentation:
                self._capture_pane_snapshot_if_needed()

        self._root.animate_to(
            pane_width=target["pane_width"],
            pane_x=target["pane_x"],
            pane_y=target["pane_y"],
            pane_height=target["pane_height"],
            content_x=target["content_x"],
            duration=duration,
            flyout=flyout_visual,
            on_finished=finish,
        )

        if old_effective is not None and new_tuple != self._last_state_tuple:
            self.paneStateChanged.emit(manual, old_effective, effective,
                                       presentation)
        self._last_state_tuple = new_tuple
        self._sync_app_filter()

    def _sync_geometry(self) -> None:
        if self._effective_state is None:
            return
        target = self._target_geometry()
        self._root.animate_to(
            pane_width=target["pane_width"],
            pane_x=target["pane_x"],
            pane_y=target["pane_y"],
            pane_height=target["pane_height"],
            content_x=target["content_x"],
            duration=0,
            flyout=target["flyout"],
        )
        if target["flyout"]:
            self._pane_snapshot_timer.start(0)
            self._pane.set_flyout(True)
        else:
            self._pane.set_flyout(False)
        self._update_header(self._visually_expanded())

    def _apply_visual_expansion(self, expanded: bool, animate: bool) -> None:
        previous = self._was_visually_expanded
        if expanded:
            if previous is not True:
                restore = set(self._remembered_folds)
                if self._selected_child is not None:
                    restore.add(self._selected_child._fold)
                for fold in list(restore):
                    if (isinstance(fold, NavFoldItem) and fold.isValid() and
                            not fold._expanded):
                        self._set_fold_expanded(fold, True, animate=animate,
                                                sync_indicator=False)
            self._set_rows_compact(False)
            for separator in self._separators():
                separator.set_compact(False, animate=animate)
            for line in self._lines():
                line.setVisible(True)
        else:
            if previous is True:
                self._remembered_folds = {
                    fold for fold in self._fold_items
                    if fold.isValid() and fold._expanded
                }
                for fold in list(self._fold_items):
                    if fold.isValid() and fold._expanded:
                        self._set_fold_expanded(fold, False, animate=animate,
                                                sync_indicator=False)
            self._set_rows_compact(True)
            for separator in self._separators():
                separator.set_compact(True, animate=animate)
            for line in self._lines():
                line.setVisible(False)
        self._was_visually_expanded = expanded
        self._update_indicator(animate=animate)

    def _set_rows_compact(self, compact: bool) -> None:
        for item in self._nav_items:
            if item.isValid() and item._row is not None:
                item._row.set_compact(compact)
                item._row.refresh_content()
        for fold in self._fold_items:
            if fold.isValid() and fold._row is not None:
                fold._row.set_compact(compact)
                fold._row.refresh_content()
            for child in fold._children:
                if child.isValid() and child._row is not None:
                    child._row.set_compact(compact)
                    child._row.refresh_content()
        if self._settings_row is not None:
            self._settings_row.set_compact(compact)
            self._settings_row.refresh_content()

    def _separators(self) -> list[_SeparatorWidget]:
        return [entry.widget for entry in self._menu_entries
                if isinstance(entry, _SeparatorEntry) and entry.widget is not None]

    def _lines(self) -> list[QWidget]:
        return [entry.widget for entry in self._menu_entries
                if isinstance(entry, _LineEntry) and entry.widget is not None]

    def _update_header(self, expanded: bool) -> None:
        if self._header is None:
            return
        vertical = (not expanded and
                    self._effective_state is PaneStateEnum.Compact)
        self._header.set_vertical(vertical)
        self._header.setVisible(self._header.width() > 0)
        if self._header.width() > 0:
            self._pane.set_header_height(self._header.height())
        clearance = 0
        if (self._effective_state is PaneStateEnum.Hide and
                self._header.width() > 0):
            clearance = self._header.height() + 4
        if clearance != self._last_clearance:
            self._last_clearance = clearance
            self._content_revision += 1
        self._content_card.set_top_clearance(clearance)

    # ------------------------------------------------------------------
    # 汉堡 / Flyout / 事件
    # ------------------------------------------------------------------
    def _toggle_pane(self) -> None:
        self._close_submenu(animate=False)
        presentation = self._is_flyout_presentation()
        if self._effective_state is PaneStateEnum.Expanded:
            if presentation:
                self._pane_flyout_open = False
            else:
                self._pane_open_inline = False
        else:
            if presentation:
                self._pane_flyout_open = True
                self._pane_open_inline = False
            else:
                self._pane_open_inline = True
                self._pane_flyout_open = False
        self._apply_pane_state(manual=True, animate=True, force=True)

    def _toggle_submenu(self, fold: NavFoldItem) -> None:
        if self._submenu is not None and self._submenu.fold() is fold:
            self._close_submenu(animate=True)
            return
        if not fold.children():
            return
        self._open_submenu(fold)

    def _open_submenu(self, fold: NavFoldItem) -> None:
        self._close_submenu(animate=False)
        flyout = _SubmenuFlyout(self, fold)
        self._submenu = flyout
        flyout.show_flyout()
        # 某些平台上 Tool 窗口首次 show 后需要再抬一次，避免被主窗口盖住。
        QTimer.singleShot(0, self._raise_submenu)
        self._update_indicator(animate=False)
        self._sync_app_filter()

    def _raise_submenu(self) -> None:
        if self._submenu is not None and self._submenu.isVisible():
            self._submenu.raise_()

    def _close_submenu(self, animate: bool = True) -> None:
        flyout = self._submenu
        if flyout is None:
            return
        flyout.close_flyout(animate=animate)
        if not animate:
            self._submenu = None
            self._update_indicator(animate=False)
        self._sync_app_filter()

    def _on_submenu_closed(self, flyout: _SubmenuFlyout) -> None:
        if self._submenu is flyout:
            self._submenu = None
        flyout.deleteLater()
        self._update_indicator(animate=False)
        self._sync_app_filter()

    def _widget_in_pane(self, widget: QWidget | None) -> bool:
        if widget is None:
            return False
        return widget is self._pane or self._pane.isAncestorOf(widget)

    def _widget_in_header(self, widget: QWidget | None) -> bool:
        if widget is None or self._header is None:
            return False
        return widget is self._header or self._header.isAncestorOf(widget)

    def _handle_outside_press(self, widget: QWidget | None) -> None:
        if self._submenu is not None and self._submenu.isVisible():
            if not self._submenu.contains_widget(widget):
                trigger_row = self._submenu.fold()._row
                on_trigger = (widget is trigger_row or
                              (trigger_row is not None and
                               trigger_row.isAncestorOf(widget)))
                if not on_trigger:
                    self._close_submenu(animate=True)
                    return
        if (self._pane_flyout_open and self._presentation_flyout and
                self._effective_state is PaneStateEnum.Expanded):
            if not (self._widget_in_pane(widget) or
                    self._widget_in_header(widget)):
                self._pane_flyout_open = False
                self._apply_pane_state(manual=True, animate=True, force=True)

    def eventFilter(self, obj, event) -> bool:
        if not self.isVisible():
            return False
        event_type = event.type()
        if event_type == QEvent.Type.MouseButtonPress:
            try:
                position = event.globalPosition().toPoint()
            except AttributeError:
                position = None
            if position is not None:
                self._handle_outside_press(QApplication.widgetAt(position))
            return False
        if event_type == QEvent.Type.KeyPress and event.key() == Qt.Key_Escape:
            if self._submenu is not None:
                self._close_submenu(animate=True)
                return True
            if (self._pane_flyout_open and self._presentation_flyout and
                    self._effective_state is PaneStateEnum.Expanded):
                self._pane_flyout_open = False
                self._apply_pane_state(manual=True, animate=True, force=True)
                return True
        return False

    def _install_app_filter(self) -> None:
        app = QApplication.instance()
        if app is not None and not self._app_filter_installed:
            app.installEventFilter(self)
            self._app_filter_installed = True

    def _remove_app_filter(self) -> None:
        app = QApplication.instance()
        if app is not None and self._app_filter_installed:
            app.removeEventFilter(self)
            self._app_filter_installed = False

    def _sync_app_filter(self) -> None:
        """只在有 Flyout 打开时监听全局点击，避免无谓的全局事件过滤。"""
        needed = (self.isVisible() and
                  (self._submenu is not None or
                   (self._pane_flyout_open and self._presentation_flyout and
                    self._effective_state is PaneStateEnum.Expanded)))
        if needed:
            self._install_app_filter()
        else:
            self._remove_app_filter()

    # ------------------------------------------------------------------
    # 快照
    # ------------------------------------------------------------------
    def _blurred_grab(self, widget: QWidget, cache_attr: str,
                      style: FrostStyle = FLYOUT_GLASS):
        origin = widget.mapToGlobal(QPoint(0, 0))
        dpr_hint = float(widget.devicePixelRatioF() or 1.0)
        key = (widget.width(), widget.height(), origin.x(), origin.y(),
               dpr_hint, self._content_revision,
               style.blur, style.brightness, style.saturation)
        cached = getattr(self, cache_attr, None)
        if cached is not None and cached[0] == key:
            return cached[1]
        if widget.width() <= 0 or widget.height() <= 0:
            return None
        pixmap = widget.grab()
        if pixmap.isNull():
            return None
        image = pixmap.toImage()
        dpr = float(image.devicePixelRatio() or dpr_hint)
        blurred = blur_qimage(
            image,
            style.blur * dpr,
            style.brightness,
            style.saturation,
        )
        blurred.setDevicePixelRatio(dpr)
        result = (blurred, origin)
        setattr(self, cache_attr, (key, result))
        return result

    def _grab_window_snapshot(self, style: FrostStyle = FLYOUT_GLASS):
        return self._blurred_grab(self, "_window_snapshot_cache", style)

    def _capture_pane_snapshot_if_needed(self) -> None:
        if not self.isVisible():
            return
        if not (self._effective_state is PaneStateEnum.Expanded and
                self._presentation_flyout):
            return
        # 抓窗口时临时隐藏浮层，避免把 Flyout 自身画进快照；
        # 同时让快照覆盖侧边栏所在的窄条，消除玻璃接缝。
        hidden = []
        for widget in (self._pane, self._root.shadow(), self._header):
            if widget is not None and widget.isVisible():
                hidden.append(widget)
                widget.setVisible(False)
        try:
            snapshot = self._blurred_grab(self, "_pane_snapshot_cache")
        finally:
            for widget in hidden:
                widget.setVisible(True)
        self._last_window_pos = self.mapToGlobal(QPoint(0, 0))
        if snapshot is None:
            self._pane.set_snapshot(None, QPoint(0, 0))
        else:
            self._pane.set_snapshot(snapshot[0], snapshot[1])

    # ------------------------------------------------------------------
    # 窗口事件
    # ------------------------------------------------------------------
    def showEvent(self, event) -> None:
        super().showEvent(event)
        if self._ready:
            self._last_window_pos = self.mapToGlobal(QPoint(0, 0))
            self._content_revision += 1
            self._sync_geometry()
            self._update_indicator(animate=False)
            QTimer.singleShot(0, lambda: self._update_indicator(animate=False))
            self._sync_app_filter()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if not self._ready:
            return
        self._content_revision += 1
        if self._submenu is not None:
            self._close_submenu(animate=False)
        if self._pane_state is PaneStateEnum.Auto:
            base = self._base_state()
            if base is not self._last_base:
                self._reset_open_flags()
                self._apply_pane_state(manual=False, animate=True, force=True)
                return
        self._sync_geometry()

    def moveEvent(self, event) -> None:
        super().moveEvent(event)
        if not self._ready:
            return
        position = self.mapToGlobal(QPoint(0, 0))
        delta = position - self._last_window_pos
        self._last_window_pos = position
        if delta.x() or delta.y():
            self._pane.shift_snapshot(delta.x(), delta.y())
            if self._submenu is not None:
                self._submenu.move_with_window(delta.x(), delta.y())

    def _handle_activation_change(self) -> None:
        if self._submenu is None:
            return
        if self.isActiveWindow():
            return
        flyout = self._submenu
        active = QApplication.activeWindow()
        if (flyout.isActiveWindow() or active is flyout or
                (active is not None and flyout.isAncestorOf(active))):
            return
        self._close_submenu(animate=False)

    def changeEvent(self, event) -> None:
        if event.type() in (QEvent.Type.WindowDeactivate,
                            QEvent.Type.ActivationChange):
            self._handle_activation_change()
        super().changeEvent(event)

    def event(self, event):
        if event.type() == QEvent.Type.WindowDeactivate:
            self._handle_activation_change()
        return super().event(event)

    def hideEvent(self, event) -> None:
        if self._submenu is not None:
            self._close_submenu(animate=False)
        self._remove_app_filter()
        super().hideEvent(event)

    def closeEvent(self, event) -> None:
        self._close_submenu(animate=False)
        self._pane_snapshot_timer.stop()
        self._remove_app_filter()
        self._root.stop_animation()
        super().closeEvent(event)


__all__ = [
    "NavigationView",
    "NavItem",
    "NavFoldItem",
    "PaneStateEnum",
    "PaneShowInlineEnum",
    "HighLightPanel",
    "FontIcon",
    "DemoWindow",
    "DEMO_QSS",
]


# ==== DEMO ====


#: Demo 用的 QSS：数值与 THEME_DEFAULTS / 当前常量保持一致，可在这里改主题。
DEMO_QSS = """
NavigationView {
    qproperty-selectedBg: #2d2d2d;
    qproperty-selectedHoverBg: #292929;
    qproperty-selectedPressedBg: #2d2d2d;
    qproperty-hoverBg: #2d2d2d;
    qproperty-pressedBg: #292929;
    qproperty-textColor: #ffffff;
    qproperty-pressedText: #cfcfcf;
    qproperty-separatorColor: #cccccc;
    qproperty-dividerColor: #313131;
    qproperty-indicatorColor: #99ebff;
    qproperty-indicatorWidth: 2;
    qproperty-indicatorHeight: 16;
    qproperty-navItemRadius: 4;
    qproperty-flyoutRadius: 8;
    qproperty-flyoutItemRadius: 4;
}

HighLightPanel {
    qproperty-cornerRadius: 8;
}

_CapsuleScrollBar {
    qproperty-barColor: #9f9f9f;
}
"""


def _page(title: str, text: str) -> QVBoxLayout:
    """Demo 用的简单页面布局。"""
    box = QVBoxLayout()
    head = QLabel(title)
    head.setStyleSheet("font-size: 22px; font-weight: 600; color: #ffffff;")
    body = QLabel(text)
    body.setWordWrap(True)
    body.setStyleSheet("color: #bdbdbd; font-size: 14px;")
    box.addWidget(head)
    box.addWidget(body)
    box.addStretch(1)
    return box


class DemoWindow(NavigationView):
    """最短用法示例。"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("NavigationView Demo")
        self.resize(1180, 760)

        self.addNavItem("\uE80F", "主页", _page("主页", "欢迎使用 NavigationView。"))
        self.addNavItem("\uE8A5", "文档", _page("文档", "这里是文档内容。"))
        self.addSeparator("资源")

        dev = self.addNavFoldItem("\uE713", "开发")
        dev.addNavItem("\uE774", "网络", _page("网络", "网络相关设置。"))
        dev.addNavItem("\uE703", "蓝牙", _page("蓝牙", "蓝牙相关设置。"))

        help = self.addNavFoldItem("\uE897", "帮助", _page("帮助", "帮助与反馈。"))
        help.addNavItem("\uE939", "反馈", _page("反馈", "反馈与建议。"))
        help.addNavItem("\uE946", "关于", _page("关于", "NavigationView 示例。"))
        self.setSettingLayout(_page("设置", "应用设置。"))
        self.setSelectedNavItem(0)


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("NavigationView")
    app.setStyleSheet(DEMO_QSS)
    window = DemoWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())



