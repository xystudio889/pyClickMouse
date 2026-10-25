"""Windows 11 风格自定义标题栏（保留 Windows 原生视觉效果）。

特点
----
* 窗口阴影、Windows 11 圆角、最小化/最大化/还原的 DWM 动画全部保留；
* 拖动标题栏移动窗口、双击最大化/还原、右键标题栏弹出系统菜单；
* Aero Snap、Win + 方向键贴靠、任务栏预览照常工作；
* 最大化按钮悬停时出现 Windows 11 的“贴靠布局”悬浮面板
  （按钮走原生 HTMINBUTTON / HTMAXBUTTON / HTCLOSE 命中测试）；
* 按钮点击由组件自己 SetCapture + WM_SYSCOMMAND 完成：最小化/最大化可靠，
  也不会出现 DefWindowProc 画出来的“白底原生按钮”残影；
* 标题、图标、深/浅色主题可换，窗口变窄时标题自动省略；
* 窗口无边框，但 Qt 的 resize()/move() 仍然按客户区精确生效。

用法
----
继承 ``TitleBarWindow``（QVBoxLayout + 内容区）::

    class MyWindow(TitleBarWindow):
        def __init__(self):
            super().__init__(title="我的应用", icon=QIcon("app.ico"))
            self.body_layout.addWidget(QTextEdit())

或者继承 ``TitleBarMainWindow``（QMainWindow，标题栏固定在顶部，
菜单栏会显示在标题栏下方）::

    class MyWindow(TitleBarMainWindow):
        def __init__(self):
            super().__init__(title="我的应用")
            self.setCentralWidget(QTextEdit())

注意
----
* 仅在 Windows 上启用原生效果；其他平台退化为普通窗口。
* 如果不需要“原生按钮”（例如想自己拦截最小化/关闭），可以传
  ``native_caption=False``，此时按钮由 Qt 处理、没有贴靠布局面板。
* 窗口被系统最大化时，Qt 可能因为“无边框 + 铺满屏幕”而同时报告
  ``WindowFullScreen``，判断状态请用 ``isMaximized()``。
"""

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

import ctypes
import ctypes.wintypes as wt
import sys
import traceback

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


# =============================================================================
# Windows 原生窗口效果（DWM 阴影 / 最小化最大化动画 / 圆角 / 贴靠布局）
# =============================================================================
#
# 核心做法（与 Chromium / Electron 的隐藏标题栏方案一致）：
#   1. 窗口本身仍然是一个“带边框”的普通 Win32 窗口（WS_OVERLAPPEDWINDOW），
#      因此 DWM 会照常提供：窗口阴影、最小化/最大化动画、Aero Snap、
#      Win+方向键贴靠、右键系统菜单、任务栏预览等原生效果；
#   2. 用 WM_NCCALCSIZE 把非客户区“算成 0”，让客户区铺满整个窗口，
#      从而把原生标题栏藏起来，由我们自己画；
#   3. 用 WM_NCHITTEST 把标题栏映射成 HTCAPTION，把三个按钮映射成
#      HTMINBUTTON / HTMAXBUTTON / HTCLOSE —— 这样点击、拖动、双击最大化、
#      右侧系统菜单、Windows 11 最大化按钮的“贴靠布局”悬浮面板全是系统行为；
#   4. 用 DWM 属性给窗口加圆角，并在系统主题变化时同步深/浅色。
#
# 注意：为了让 Qt 认为窗口没有边框（resize()/move() 不产生偏差），
#       窗口以 Qt.FramelessWindowHint 创建，随后再把原生边框样式补回去。
#       这是本文件里唯一“非标准”的一步，所有 DWM 效果都由补回样式保证。

_IS_WINDOWS = sys.platform == "win32"

# ------------------------------- Win32 常量 -------------------------------
WM_NCCALCSIZE = 0x0083
WM_NCHITTEST = 0x0084
WM_NCACTIVATE = 0x0086
WM_NCMOUSEMOVE = 0x00A0
WM_NCLBUTTONDOWN = 0x00A1
WM_NCLBUTTONUP = 0x00A2
WM_NCLBUTTONDBLCLK = 0x00A3
WM_NCMOUSELEAVE = 0x02A2
WM_MOUSEMOVE = 0x0200
WM_LBUTTONUP = 0x0202
WM_CAPTURECHANGED = 0x0215
WM_CANCELMODE = 0x001F
WM_SYSCOMMAND = 0x0112
WM_SETTINGCHANGE = 0x001A
WM_GETMINMAXINFO = 0x0024
WM_SIZE = 0x0005
WM_STYLECHANGED = 0x007D

SC_MINIMIZE = 0xF020
SC_MAXIMIZE = 0xF030
SC_RESTORE = 0xF120
WM_CLOSE = 0x0010

HTCLIENT = 1
HTCAPTION = 2
HTMINBUTTON = 8
HTMAXBUTTON = 9
HTCLOSE = 20
HTLEFT = 10
HTRIGHT = 11
HTTOP = 12
HTTOPLEFT = 13
HTTOPRIGHT = 14
HTBOTTOM = 15
HTBOTTOMLEFT = 16
HTBOTTOMRIGHT = 17

GWL_STYLE = -16
GWL_EXSTYLE = -20
WS_POPUP = 0x80000000
WS_OVERLAPPEDWINDOW = 0x00CF0000  # WS_OVERLAPPED|WS_CAPTION|WS_SYSMENU|WS_THICKFRAME|WS_MINIMIZEBOX|WS_MAXIMIZEBOX
WS_SYSMENU = 0x00080000
WS_MINIMIZEBOX = 0x00020000
WS_MAXIMIZEBOX = 0x00010000
WS_EX_APPWINDOW = 0x00040000
WS_EX_TOOLWINDOW = 0x00000080

SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SWP_NOZORDER = 0x0004
SWP_NOACTIVATE = 0x0010
SWP_FRAMECHANGED = 0x0020

SM_CXSIZEFRAME = 32
SM_CYSIZEFRAME = 33
SM_CXPADDEDBORDER = 92

DWMWA_USE_IMMERSIVE_DARK_MODE = 20
DWMWA_USE_IMMERSIVE_DARK_MODE_OLD = 19
DWMWA_WINDOW_CORNER_PREFERENCE = 33
DWMWCP_ROUND = 2

TME_LEAVE = 0x00000002
TME_NONCLIENT = 0x00000010

QWIDGETSIZE_MAX = 16777215


class _NCCALCSIZE_PARAMS(ctypes.Structure):
    _fields_ = [("rgrc", wt.RECT * 3), ("lppos", ctypes.c_void_p)]


class _MONITORINFO(ctypes.Structure):
    _fields_ = [("cbSize", wt.DWORD), ("rcMonitor", wt.RECT),
                ("rcWork", wt.RECT), ("dwFlags", wt.DWORD)]


class _MINMAXINFO(ctypes.Structure):
    _fields_ = [("ptReserved", wt.POINT), ("ptMaxSize", wt.POINT),
                ("ptMaxPosition", wt.POINT), ("ptMinTrackSize", wt.POINT),
                ("ptMaxTrackSize", wt.POINT)]


class _TRACKMOUSEEVENT(ctypes.Structure):
    _fields_ = [("cbSize", wt.DWORD), ("dwFlags", wt.DWORD),
                ("hwndTrack", wt.HWND), ("dwHoverTime", wt.DWORD)]


if _IS_WINDOWS:
    _user32 = ctypes.WinDLL("user32", use_last_error=True)
    _dwmapi = ctypes.WinDLL("dwmapi", use_last_error=True)

    _user32.GetWindowLongPtrW.restype = ctypes.c_ssize_t
    _user32.GetWindowLongPtrW.argtypes = [wt.HWND, ctypes.c_int]
    _user32.SetWindowLongPtrW.restype = ctypes.c_ssize_t
    _user32.SetWindowLongPtrW.argtypes = [wt.HWND, ctypes.c_int, ctypes.c_ssize_t]
    _user32.SetWindowPos.restype = wt.BOOL
    _user32.SetWindowPos.argtypes = [wt.HWND, wt.HWND, ctypes.c_int, ctypes.c_int,
                                     ctypes.c_int, ctypes.c_int, wt.UINT]
    _user32.DefWindowProcW.restype = ctypes.c_ssize_t
    _user32.DefWindowProcW.argtypes = [wt.HWND, wt.UINT, wt.WPARAM, wt.LPARAM]
    _user32.IsZoomed.restype = wt.BOOL
    _user32.IsZoomed.argtypes = [wt.HWND]
    _user32.GetClientRect.restype = wt.BOOL
    _user32.GetClientRect.argtypes = [wt.HWND, ctypes.POINTER(wt.RECT)]
    _user32.ScreenToClient.restype = wt.BOOL
    _user32.ScreenToClient.argtypes = [wt.HWND, ctypes.POINTER(wt.POINT)]
    _user32.MonitorFromWindow.restype = wt.HANDLE
    _user32.MonitorFromWindow.argtypes = [wt.HWND, wt.DWORD]
    _user32.GetMonitorInfoW.restype = wt.BOOL
    _user32.GetMonitorInfoW.argtypes = [wt.HANDLE, ctypes.POINTER(_MONITORINFO)]
    _user32.TrackMouseEvent.restype = wt.BOOL
    _user32.TrackMouseEvent.argtypes = [ctypes.POINTER(_TRACKMOUSEEVENT)]
    _user32.GetSystemMetrics.restype = ctypes.c_int
    _user32.GetSystemMetrics.argtypes = [ctypes.c_int]
    _user32.SetCapture.restype = wt.HWND
    _user32.SetCapture.argtypes = [wt.HWND]
    _user32.ReleaseCapture.restype = wt.BOOL
    _user32.ReleaseCapture.argtypes = []
    _user32.GetCapture.restype = wt.HWND
    _user32.GetCapture.argtypes = []
    _user32.GetCursorPos.restype = wt.BOOL
    _user32.GetCursorPos.argtypes = [ctypes.POINTER(wt.POINT)]
    _user32.PostMessageW.restype = wt.BOOL
    _user32.PostMessageW.argtypes = [wt.HWND, wt.UINT, wt.WPARAM, wt.LPARAM]
    _dwmapi.DwmSetWindowAttribute.restype = ctypes.c_long
    _dwmapi.DwmSetWindowAttribute.argtypes = [wt.HWND, wt.DWORD, ctypes.c_void_p, wt.DWORD]

    try:  # Windows 10 1607+
        _user32.GetDpiForWindow.restype = wt.UINT
        _user32.GetDpiForWindow.argtypes = [wt.HWND]
        _user32.GetSystemMetricsForDpi.restype = ctypes.c_int
        _user32.GetSystemMetricsForDpi.argtypes = [ctypes.c_int, wt.UINT]
        _HAS_DPI_API = True
    except AttributeError:
        _HAS_DPI_API = False
else:
    _user32 = None
    _dwmapi = None
    _HAS_DPI_API = False


def _signed_lparam(lparam):
    """把 lParam 拆成屏幕坐标 (x, y)（考虑 16 位有符号）。"""
    lparam = int(lparam) & 0xFFFFFFFF
    x = lparam & 0xFFFF
    y = (lparam >> 16) & 0xFFFF
    if x >= 0x8000:
        x -= 0x10000
    if y >= 0x8000:
        y -= 0x10000
    return x, y


def _screen_point(lparam):
    x, y = _signed_lparam(lparam)
    return wt.POINT(x, y)


def _system_metrics_for_dpi(hwnd, index):
    """按窗口所在显示器的 DPI 取系统尺寸，保证 125%/150% 缩放下边框比例正确。"""
    dpi = 96
    if _HAS_DPI_API:
        try:
            dpi = _user32.GetDpiForWindow(hwnd) or 96
        except OSError:
            dpi = 96
    if _HAS_DPI_API:
        try:
            return _user32.GetSystemMetricsForDpi(index, dpi)
        except OSError:
            pass
    return _user32.GetSystemMetrics(index)


def _resize_border_size(hwnd):
    """返回 (左右, 上下) 的可缩放边框厚度（物理像素）。"""
    fx = (_system_metrics_for_dpi(hwnd, SM_CXSIZEFRAME)
          + _system_metrics_for_dpi(hwnd, SM_CXPADDEDBORDER))
    fy = (_system_metrics_for_dpi(hwnd, SM_CYSIZEFRAME)
          + _system_metrics_for_dpi(hwnd, SM_CXPADDEDBORDER))
    return max(fx, 1), max(fy, 1)


def _dwm_set_int(hwnd, attribute, value):
    """DwmSetWindowAttribute 的 int 版本；旧系统不支持时静默失败。"""
    if not _IS_WINDOWS:
        return False
    data = ctypes.c_int(value)
    try:
        hr = _dwmapi.DwmSetWindowAttribute(
            wt.HWND(hwnd), attribute, ctypes.byref(data), ctypes.sizeof(data))
    except OSError:
        return False
    return hr == 0


def _apply_dwm_effects(hwnd, dark: bool, rounded: bool = True):
    """把 Win11 的深色标题栏与圆角交给 DWM（阴影/动画本来就是 DWM 的默认行为）。"""
    if not _IS_WINDOWS:
        return
    if not _dwm_set_int(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, 1 if dark else 0):
        # Windows 10 1903 ~ 20H1 之间的属性编号是 19
        _dwm_set_int(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE_OLD, 1 if dark else 0)
    if rounded:
        _dwm_set_int(hwnd, DWMWA_WINDOW_CORNER_PREFERENCE, DWMWCP_ROUND)


def _inject_native_frame_styles(hwnd):
    """把 Qt 的无边框窗口“变成”普通带边框窗口。

    Qt 创建 FramelessWindowHint 窗口时会用 WS_POPUP；这里补回
    WS_OVERLAPPEDWINDOW，DWM 才会给窗口阴影、动画和贴靠行为。
    WM_NCCALCSIZE 会把新增的非客户区全部算进客户区，所以视觉上依旧无边框。
    """
    if not _IS_WINDOWS:
        return
    style = _user32.GetWindowLongPtrW(wt.HWND(hwnd), GWL_STYLE)
    style = (style & ~(WS_POPUP | WS_OVERLAPPEDWINDOW)) | WS_OVERLAPPEDWINDOW
    _user32.SetWindowLongPtrW(wt.HWND(hwnd), GWL_STYLE, style)

    ex_style = _user32.GetWindowLongPtrW(wt.HWND(hwnd), GWL_EXSTYLE)
    ex_style = (ex_style | WS_EX_APPWINDOW) & ~WS_EX_TOOLWINDOW
    _user32.SetWindowLongPtrW(wt.HWND(hwnd), GWL_EXSTYLE, ex_style)

    # 让 Windows 重新计算窗口边框（不改变位置和大小）
    _user32.SetWindowPos(wt.HWND(hwnd), wt.HWND(0), 0, 0, 0, 0,
                         SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER
                         | SWP_NOACTIVATE | SWP_FRAMECHANGED)


def _monitor_work_area(hwnd):
    """窗口所在显示器的工作区（物理像素，已排除任务栏）。"""
    monitor = _user32.MonitorFromWindow(wt.HWND(hwnd), 2)  # MONITOR_DEFAULTTONEAREST
    info = _MONITORINFO()
    info.cbSize = ctypes.sizeof(_MONITORINFO)
    if not _user32.GetMonitorInfoW(monitor, ctypes.byref(info)):
        return None
    return info.rcWork


def system_is_dark() -> bool:
    """当前 Windows 系统是深色模式吗？（“个性化 → 颜色 → 应用模式”）"""
    if not _IS_WINDOWS:
        return False
    try:
        import winreg
    except ImportError:
        return False
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
        try:
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        finally:
            key.Close()
        return int(value) == 0
    except OSError:
        return False


# =============================================================================
# 标题栏主题（Windows 11 视觉规范）
# =============================================================================

_TITLEBAR_LIGHT = dict(
    bar="#F3F3F3",
    title="#1A1A1A",
    title_inactive="#6B6B6B",
    caption="#1A1A1A",
    caption_inactive="#8A8A8A",
    caption_hover="#E9E9E9",
    caption_pressed="#DBDBDB",
    close_hover="#C42B1C",
    close_pressed="#B01F14",
)

_TITLEBAR_DARK = dict(
    bar="#202020",
    title="#FFFFFF",
    title_inactive="#9A9A9A",
    caption="#FFFFFF",
    caption_inactive="#9A9A9A",
    caption_hover="#333333",
    caption_pressed="#454545",
    close_hover="#C42B1C",
    close_pressed="#B01F14",
)


def _titlebar_stylesheet(dark: bool) -> str:
    c = _TITLEBAR_DARK if dark else _TITLEBAR_LIGHT
    return f"""
QWidget#TitleBar {{
    background-color: {c['bar']};
}}
QLabel#TitleBarTitle {{
    color: {c['title']};
    background: transparent;
    font-size: 12px;
    padding-left: 2px;
}}
QLabel#TitleBarTitle[active="false"] {{
    color: {c['title_inactive']};
}}
QLabel#CaptionButton {{
    background: transparent;
    color: {c['caption']};
}}
QLabel#CaptionButton[windowActive="false"] {{
    color: {c['caption_inactive']};
}}
QLabel#CaptionButton[captionState="hover"] {{
    background-color: {c['caption_hover']};
}}
QLabel#CaptionButton[captionState="pressed"] {{
    background-color: {c['caption_pressed']};
}}
/* 关闭按钮：悬停变红、图标变白（Windows 11 行为） */
QLabel#CaptionButton[captionRole="close"] {{
    color: {c['caption']};
}}
QLabel#CaptionButton[captionRole="close"][captionState="hover"] {{
    background-color: {c['close_hover']};
    color: #FFFFFF;
}}
QLabel#CaptionButton[captionRole="close"][captionState="pressed"] {{
    background-color: {c['close_pressed']};
    color: #FFFFFF;
}}
"""


def _repolish(widget):
    """动态属性改变后强制刷新 qss。"""
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    widget.update()


# =============================================================================
# 标题栏控件
# =============================================================================

_CAPTION_GLYPHS = {
    "minimize": "\uE921",
    "maximize": "\uE922",
    "restore": "\uE923",
    "close": "\uE8BB",
}

_CAPTION_ACCESSIBLE_NAMES = {
    "minimize": "最小化",
    "maximize": "最大化",
    "close": "关闭",
}


class CaptionButton(FontIcon):
    """标题栏按钮（最小化 / 最大化 / 关闭）。

    默认（native_caption=True）由 Windows 非客户区命中测试接管：
    鼠标事件不会到达 Qt，按钮只负责画图标和悬停/按下背景。
    若标题栏使用 native_caption=False，则按钮自己处理鼠标事件，
    并发出 clicked 信号。
    """

    hovered = Signal(bool)
    pressed = Signal(bool)
    clicked = Signal()

    def __init__(self, role: str, parent=None):
        super().__init__(_CAPTION_GLYPHS[role], size=10, parent=parent)
        self._role = role
        self._caption_state = "normal"
        self.setObjectName("CaptionButton")
        self.setProperty("captionRole", role)
        self.setProperty("captionState", "normal")
        self.setProperty("windowActive", True)
        self.setAccessibleName(_CAPTION_ACCESSIBLE_NAMES[role])
        self.setFixedSize(46, 32)          # Windows 11 标题栏按钮尺寸
        self.setAlignment(Qt.AlignCenter)
        self.setFocusPolicy(Qt.NoFocus)
        self.setCursor(Qt.ArrowCursor)
        # 原生模式下鼠标事件由 Windows 非客户区命中测试接管；
        # Qt 交互模式下会由 set_qt_interactive(True) 打开。
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)

    # ---------------------------------------------------------------- 状态
    def role(self) -> str:
        return self._role

    def set_qt_interactive(self, enabled: bool):
        """切换成 Qt 交互模式（标题栏 native_caption=False 时使用）。"""
        self.setAttribute(Qt.WA_TransparentForMouseEvents, not enabled)
        if enabled:
            self.setAttribute(Qt.WA_Hover, True)
            self.setMouseTracking(True)

    def set_caption_state(self, state: str):
        state = state if state in ("hover", "pressed") else "normal"
        if state == self._caption_state:
            return
        self._caption_state = state
        self.setProperty("captionState", state)
        _repolish(self)

    def set_window_active(self, active: bool):
        if bool(self.property("windowActive")) == active:
            return
        self.setProperty("windowActive", active)
        _repolish(self)

    def set_glyph(self, glyph: str):
        if self.text() != glyph:
            self.setText(glyph)

    # ---------------------------------------------------- Qt 交互模式（可选）
    def enterEvent(self, event):
        self.hovered.emit(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.hovered.emit(False)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.pressed.emit(True)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            inside = self.rect().contains(event.position().toPoint())
            self.pressed.emit(False)
            if inside:
                self.clicked.emit()
            event.accept()
            return
        super().mouseReleaseEvent(event)


class _TitleLabel(QLabel):
    """会自动省略中间/末尾的标题文本（窗口变窄时显示 …）。"""

    def __init__(self, text: str = "", parent=None):
        super().__init__(parent)
        self._full_text = ""
        self.setObjectName("TitleBarTitle")
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.set_full_text(text)

    def set_full_text(self, text: str):
        self._full_text = text or ""
        self._update_elide()

    def full_text(self) -> str:
        return self._full_text

    def _update_elide(self):
        available = max(0, self.width())
        metrics = self.fontMetrics()
        elided = metrics.elidedText(self._full_text, Qt.ElideRight, available)
        if elided != self.text():
            super().setText(elided)
        self.setToolTip(self._full_text if elided != self._full_text else "")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_elide()

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() in (QEvent.FontChange, QEvent.StyleChange):
            self._update_elide()


class TitleBar(QWidget):
    """Windows 11 风格标题栏：图标 + 标题 + 最小化/最大化/关闭。

    通常不需要手动创建，直接继承 ``TitleBarWindow`` / ``TitleBarMainWindow``
    即可；也可以把它放进 ``TitleBarMainWindow.setMenuWidget()`` 之类的位置。

    参数
    ----
    window:
        所属顶层窗口。Qt 交互模式下按钮要调用窗口的最小化/最大化/关闭。
    title:
        窗口标题，过长会自动省略。
    icon:
        标题左侧的 16x16 图标；传 None 则不显示图标。
    native_caption:
        True（默认）时使用 Windows 原生非客户区命中测试：悬停高亮、
        Windows 11 贴靠布局悬浮面板都由系统提供，点击由组件转换成
        WM_SYSCOMMAND（动画仍是 DWM 原生）。False 时按钮由 Qt 处理，
        没有贴靠布局悬浮面板。
    dark:
        深/浅色主题；None 表示跟随系统。

    自定义控件
    --------
    标题栏里放置的按钮/输入框等控件默认会被当作“拖动区”。
    需要响应鼠标的控件请设置 ``widget.setProperty("titlebarInteractive", True)``，
    命中测试会把该区域交回 Qt。
    """

    HEIGHT = 32

    #: 深/浅色主题变化时发出（跟随系统主题切换时也会发出），
    #: 方便把窗口内容区一起换色。
    themeChanged = Signal(bool)

    def __init__(self, window=None, title: str = "", icon: Optional[QIcon] = None,
                 *, native_caption: bool = True, dark: Optional[bool] = None,
                 parent=None):
        super().__init__(parent)
        self._window = window
        self._native_caption = bool(native_caption)
        self._dark = system_is_dark() if dark is None else bool(dark)
        self._active = True
        self._maximized = False
        self._hover_role = None
        self._pressed_role = None

        self.setObjectName("TitleBar")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setFixedHeight(self.HEIGHT)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFocusPolicy(Qt.NoFocus)

        self._build_layout()
        self.set_icon(icon)
        self.set_title(title)
        self.set_dark(self._dark)
        self.set_active(True)
        self.set_maximized(False)

        if not self._native_caption:
            for button in self._buttons.values():
                button.set_qt_interactive(True)

    # ------------------------------------------------------------------ 构建
    def _build_layout(self):
        self._buttons = {}
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 左侧：图标 + 标题
        left = QWidget(self)
        left.setObjectName("TitleBarLeft")
        left.setAttribute(Qt.WA_StyledBackground, True)
        left_layout = QHBoxLayout(left)
        left_layout.setContentsMargins(12, 0, 0, 0)
        left_layout.setSpacing(12)

        self._icon_label = QLabel(left)
        self._icon_label.setObjectName("TitleBarIcon")
        self._icon_label.setFixedSize(16, 16)
        self._icon_label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self._icon_label.hide()

        self._title_label = _TitleLabel("", left)

        left_layout.addWidget(self._icon_label)
        left_layout.addWidget(self._title_label, 1)
        layout.addWidget(left, 1)

        # 右侧：最小化 / 最大化 / 关闭（从左到右）
        for role in ("minimize", "maximize", "close"):
            button = CaptionButton(role, self)
            self._buttons[role] = button
            button.hovered.connect(
                lambda on, r=role: self._set_hover_role(r if on else None))
            button.pressed.connect(
                lambda on, r=role: self._set_pressed_role(r if on else None))
            button.clicked.connect(lambda r=role: self._on_button_clicked(r))
            layout.addWidget(button)
        self._sync_maximize_glyph()

    # ------------------------------------------------------------------ 属性
    @property
    def buttons(self) -> dict:
        return dict(self._buttons)

    def set_title(self, title: str):
        self._title_label.set_full_text(title or "")

    def title(self) -> str:
        return self._title_label.full_text()

    def set_icon(self, icon: Optional[QIcon]):
        self._icon = icon
        if icon is None or icon.isNull():
            self._icon_label.hide()
            return
        dpr = self.devicePixelRatioF() or 1.0
        try:
            pixmap = icon.pixmap(QSize(16, 16), dpr)
        except TypeError:  # 极老的 Qt
            pixmap = icon.pixmap(QSize(16, 16))
        self._icon_label.setPixmap(pixmap)
        self._icon_label.show()

    def changeEvent(self, event):
        super().changeEvent(event)
        # 窗口拖到不同缩放比例的显示器时，重新取高分图标
        dpr_event = getattr(QEvent, "DevicePixelRatioChange", None)
        if dpr_event is not None and event.type() == dpr_event:
            if self._icon is not None:
                self.set_icon(self._icon)

    def is_dark(self) -> bool:
        return self._dark

    def set_dark(self, dark: bool):
        dark = bool(dark)
        if dark == self._dark and self.styleSheet():
            return
        self._dark = dark
        self.setStyleSheet(_titlebar_stylesheet(dark))
        _repolish(self)
        for button in self._buttons.values():
            _repolish(button)
        self.themeChanged.emit(dark)

    def set_active(self, active: bool):
        active = bool(active)
        if active == self._active:
            return
        self._active = active
        self._title_label.setProperty("active", active and "true" or "false")
        _repolish(self._title_label)
        for button in self._buttons.values():
            button.set_window_active(active)

    def set_maximized(self, maximized: bool):
        maximized = bool(maximized)
        if maximized == self._maximized:
            return
        self._maximized = maximized
        self._sync_maximize_glyph()

    def _sync_maximize_glyph(self):
        button = self._buttons.get("maximize")
        if button is None:
            return
        button.set_glyph(_CAPTION_GLYPHS["restore" if self._maximized else "maximize"])

    # ----------------------------------------------------- 命中测试 / 按钮状态
    def hit_test(self, position: QPointF) -> Optional[str]:
        """返回点击区域类型：close / minimize / maximize / caption / client。

        position 为标题栏本地坐标（逻辑像素）；不在标题栏内返回 None。
        """
        rect = QRectF(self.rect())
        if not rect.contains(position):
            return None

        if self._native_caption:
            role = self._button_at(position)
            if role is not None:
                return role
        else:
            if self._button_at(position) is not None:
                return "client"

        widget = self.childAt(position.toPoint())
        while widget is not None and widget is not self:
            if widget.property("titlebarInteractive"):
                return "client"
            widget = widget.parentWidget()

        # 其余区域：交给系统拖动 / 双击最大化 / 右键系统菜单
        return "caption"

    def _button_at(self, position: QPointF) -> Optional[str]:
        for role, button in self._buttons.items():
            top_left = button.mapTo(self, QPoint(0, 0))
            if QRectF(top_left, button.size()).contains(position):
                return role
        return None

    def set_native_hover(self, hit_code: Optional[int]):
        self._set_hover_role(self._role_from_hit_code(hit_code))

    def set_native_pressed(self, hit_code: Optional[int]):
        role = self._role_from_hit_code(hit_code)
        self._set_pressed_role(role)
        if role is not None:
            self._set_hover_role(role)

    @staticmethod
    def _role_from_hit_code(hit_code: Optional[int]) -> Optional[str]:
        return {HTMINBUTTON: "minimize",
                HTMAXBUTTON: "maximize",
                HTCLOSE: "close"}.get(hit_code)

    def _set_hover_role(self, role: Optional[str]):
        if role == self._hover_role:
            return
        self._hover_role = role
        self._refresh_button_states()

    def _set_pressed_role(self, role: Optional[str]):
        if role == self._pressed_role:
            return
        self._pressed_role = role
        self._refresh_button_states()

    def _refresh_button_states(self):
        for role, button in self._buttons.items():
            if role == self._pressed_role:
                button.set_caption_state("pressed")
            elif role == self._hover_role:
                button.set_caption_state("hover")
            else:
                button.set_caption_state("normal")

    # ------------------------------------------------------------ Qt 交互模式
    def _on_button_clicked(self, role: str):
        window = self._window or self.window()
        if window is None:
            return
        if role == "minimize":
            window.showMinimized()
        elif role == "maximize":
            if window.isMaximized():
                window.showNormal()
            else:
                window.showMaximized()
        elif role == "close":
            window.close()


# =============================================================================
# 原生窗口框架助手
# =============================================================================

class WindowsFrameHelper:
    """把任意 Qt 顶层窗口变成“保留 Windows 原生效果”的自定义标题栏窗口。

    负责：
      * 补回 WS_OVERLAPPEDWINDOW（阴影、动画、贴靠、任务栏都靠它）；
      * WM_NCCALCSIZE 隐藏原生标题栏；
      * WM_NCHITTEST 把标题栏/按钮映射成系统 hit code；
      * WM_NCMOUSEMOVE / WM_NCMOUSELEAVE 维护按钮悬停；
      * WM_NCLBUTTONDOWN / WM_LBUTTONUP 自己处理按钮点击
        （不让 DefWindowProc 进入它的非客户区按钮跟踪：否则它会按标准
         标题栏位置把原生按钮画进客户区，还会取消我们的最小化/最大化）；
      * DWM 圆角与深色模式，并跟随系统主题。
    """

    def __init__(self, window: QWidget, title_bar: TitleBar, *,
                 native_caption: bool = True, dark: Optional[bool] = None,
                 rounded: bool = True, auto_theme: bool = True):
        self.window = window
        self.title_bar = title_bar
        self.native_caption = bool(native_caption)
        self.rounded = bool(rounded)
        self.auto_theme = bool(auto_theme)
        self._dark = system_is_dark() if dark is None else bool(dark)
        self._hwnd = None
        self._last_maximized = None
        self._restyle_pending = False
        self._restyling = False
        # 正在按下的标题栏按钮 hit code（HTMINBUTTON / HTMAXBUTTON / HTCLOSE）
        self._pressed_hit = None

    # ------------------------------------------------------------------ 安装
    def install(self):
        if not _IS_WINDOWS:
            return
        # 先创建原生窗口（此时窗口还不可见），再补回原生边框样式，
        # 避免出现“先弹出无边框窗口再变回带边框”的闪烁。
        hwnd = int(self.window.winId())
        self._hwnd = hwnd
        _inject_native_frame_styles(hwnd)
        _apply_dwm_effects(hwnd, self._dark, self.rounded)
        self.title_bar.set_dark(self._dark)
        self.title_bar.set_active(self.window.isActiveWindow())
        self.title_bar.set_maximized(self.window.isMaximized())
        self._last_maximized = bool(self.window.isMaximized())

    def _ensure_frame_styles(self, hwnd):
        """窗口样式被 Qt 重置（setWindowFlags / 全屏切换）时，安排一次补回。

        Qt 的 setWindowFlags()/showFullScreen() 会把窗口重新变回 WS_POPUP，
        从而丢掉阴影和动画；这里检测到之后用 0 延迟定时器补回，
        避免在 Qt 正在改样式的过程中重入。
        """
        if not _IS_WINDOWS:
            return
        if self._restyle_pending or self._restyling:
            return
        try:
            style = _user32.GetWindowLongPtrW(wt.HWND(hwnd), GWL_STYLE)
        except OSError:
            return
        if (style & WS_OVERLAPPEDWINDOW) == WS_OVERLAPPEDWINDOW and not (style & WS_POPUP):
            return
        self._restyle_pending = True
        QTimer.singleShot(0, self.window, self._restyle)

    def _restyle(self):
        self._restyle_pending = False
        window = self.window
        try:
            if window.isFullScreen():
                # 全屏时保持无边框（Windows 全屏窗口本来就没有阴影）
                return
            hwnd = int(window.winId())
        except (RuntimeError, OSError):
            return
        self._restyling = True
        try:
            self._hwnd = hwnd
            _inject_native_frame_styles(hwnd)
            _apply_dwm_effects(hwnd, self._dark, self.rounded)
        except OSError:
            pass
        finally:
            self._restyling = False

    def set_dark(self, dark: bool):
        self._dark = bool(dark)
        if self._hwnd:
            _apply_dwm_effects(self._hwnd, self._dark, self.rounded)
        self.title_bar.set_dark(self._dark)

    def is_dark(self) -> bool:
        return self._dark

    # -------------------------------------------------------------- 消息处理
    def handle_message(self, event_type, message):
        """由窗口的 nativeEvent() 调用；返回 (handled, result)。"""
        if not _IS_WINDOWS:
            return False, 0
        try:
            event_type = bytes(event_type)
        except TypeError:
            event_type = b""
        if event_type not in (b"windows_generic_MSG", b"windows_dispatcher_MSG"):
            return False, 0

        try:
            msg = wt.MSG.from_address(int(message))
        except (TypeError, ValueError):
            return False, 0

        # 原生窗口创建期间（winId() 尚未返回）不要调用 Qt API，否则会重入
        creating = self._hwnd is None
        if creating and message in (WM_SIZE, WM_NCACTIVATE, WM_NCMOUSEMOVE,
                                    WM_NCLBUTTONDOWN, WM_NCLBUTTONUP,
                                    WM_NCLBUTTONDBLCLK, WM_LBUTTONUP,
                                    WM_CAPTURECHANGED,
                                    WM_MOUSEMOVE, WM_GETMINMAXINFO,
                                    WM_STYLECHANGED):
            return False, 0

        try:
            return self._process(msg)
        except Exception:  # 原生回调里绝不能让异常穿回 C++，否则 Qt 会崩
            traceback.print_exc()
            return False, 0

    def _process(self, msg):
        message = msg.message
        hwnd = msg.hWnd

        # Qt 可能会重置原生样式（setWindowFlags / 全屏切换），发现丢失就补回
        if message in (WM_SIZE, WM_NCHITTEST, WM_NCMOUSEMOVE, WM_NCLBUTTONDOWN,
                       WM_NCLBUTTONUP, WM_STYLECHANGED):
            self._ensure_frame_styles(hwnd)

        if message == WM_STYLECHANGED:
            return False, 0

        if message == WM_NCCALCSIZE:
            if not msg.wParam:
                return False, 0
            # 非客户区算成 0：客户区铺满整个窗口（原生标题栏被“藏”起来）
            if _user32.IsZoomed(hwnd):
                # 最大化时窗口矩形比屏幕大了一圈边框，客户区应正好是工作区
                work_area = _monitor_work_area(hwnd)
                if work_area is not None:
                    params = _NCCALCSIZE_PARAMS.from_address(int(msg.lParam))
                    params.rgrc[0] = work_area
            return True, 0

        if message == WM_NCHITTEST:
            hit = self._on_hit_test(hwnd, msg.lParam)
            if hit is None:
                return False, 0
            return True, int(hit)

        if message == WM_NCMOUSEMOVE:
            self.title_bar.set_native_hover(int(msg.wParam))
            # 让窗口在鼠标离开非客户区时收到 WM_NCMOUSELEAVE
            track = _TRACKMOUSEEVENT(ctypes.sizeof(_TRACKMOUSEEVENT),
                                     TME_LEAVE | TME_NONCLIENT,
                                     hwnd, 0)
            _user32.TrackMouseEvent(ctypes.byref(track))
            return False, 0

        if message == WM_NCMOUSELEAVE:
            if self._pressed_hit is None:
                self.title_bar.set_native_hover(None)
                self.title_bar.set_native_pressed(None)
            return False, 0

        if message == WM_NCLBUTTONDOWN:
            if self._begin_caption_press(hwnd, int(msg.wParam)):
                # 自己处理标题栏按钮：不能再交给 DefWindowProc。
                # 否则 DefWindowProc 会进入它自己的“非客户区按钮跟踪”循环，
                # 按标准标题栏位置把原生按钮画到我们的客户区里（就是那个
                # 按下后出现在按钮旁边的“白底按钮”），而且因为我们的按钮
                # 位置和标准位置不一致，它会在鼠标移动后取消最小化/最大化。
                return True, 0
            self.title_bar.set_native_pressed(int(msg.wParam))
            return False, 0

        if message == WM_NCLBUTTONDBLCLK:
            if self._begin_caption_press(hwnd, int(msg.wParam)):
                return True, 0
            return False, 0

        if message == WM_LBUTTONUP:
            if self._pressed_hit is not None:
                self._finish_caption_press(hwnd)
                return True, 0
            return False, 0

        if message == WM_CAPTURECHANGED:
            if self._pressed_hit is not None:
                self._pressed_hit = None
                self.title_bar.set_native_pressed(None)
                self.title_bar.set_native_hover(None)
            return False, 0

        if message == WM_CANCELMODE:
            if self._pressed_hit is not None:
                self._pressed_hit = None
                try:
                    _user32.ReleaseCapture()
                except OSError:
                    pass
                self.title_bar.set_native_pressed(None)
                self.title_bar.set_native_hover(None)
            return False, 0

        if message == WM_NCLBUTTONUP:
            if self._pressed_hit is not None:
                self._finish_caption_press(hwnd)
                return True, 0
            self.title_bar.set_native_pressed(None)
            self.title_bar.set_native_hover(int(msg.wParam))
            return False, 0

        if message == WM_MOUSEMOVE:
            if self._pressed_hit is not None:
                # 按住按钮拖动时：鼠标在按钮上保持按下态，移出则恢复；
                # 这些消息不再交给 Qt，避免按住标题栏按钮时内容区跟着动。
                hit = self._hit_code_at_cursor(hwnd)
                if hit == self._pressed_hit:
                    self.title_bar.set_native_pressed(self._pressed_hit)
                else:
                    self.title_bar.set_native_pressed(None)
                    if hit in (HTMINBUTTON, HTMAXBUTTON, HTCLOSE):
                        self.title_bar.set_native_hover(hit)
                    else:
                        self.title_bar.set_native_hover(None)
                return True, 0
            # 鼠标进入客户区，标题栏按钮不应继续保持悬停
            self.title_bar.set_native_hover(None)
            return False, 0

        if message == WM_NCACTIVATE:
            self.title_bar.set_active(bool(msg.wParam))
            return False, 0

        if message == WM_SIZE:
            if bool(_user32.IsIconic(hwnd)):
                # 最小化后鼠标状态失效，清掉按钮的悬停/按下残留
                self._pressed_hit = None
                self.title_bar.set_native_pressed(None)
                self.title_bar.set_native_hover(None)
            maximized = bool(_user32.IsZoomed(hwnd))
            if maximized != self._last_maximized:
                self._last_maximized = maximized
                self.title_bar.set_maximized(maximized)
            return False, 0

        if message == WM_GETMINMAXINFO:
            self._apply_min_max_info(hwnd, msg.lParam)
            return False, 0

        if message == WM_SETTINGCHANGE:
            self._on_setting_change(msg.lParam)
            return False, 0

        return False, 0

    # -------------------------------------------------------- 标题栏按钮点击
    def _begin_caption_press(self, hwnd, hit_code):
        """按下标题栏按钮：自己 SetCapture，不让 DefWindowProc 介入。

        这样既能避免 DefWindowProc 按“标准标题栏”位置把原生按钮画进客户区
        （按下时旁边出现的白底按钮），也能避免它用标准位置的命中测试
        取消我们的最小化/最大化。
        """
        if hit_code not in (HTMINBUTTON, HTMAXBUTTON, HTCLOSE):
            return False
        self._pressed_hit = hit_code
        _user32.SetCapture(wt.HWND(hwnd))
        self.title_bar.set_native_pressed(hit_code)
        self.title_bar.set_native_hover(hit_code)
        return True

    def _finish_caption_press(self, hwnd):
        pressed = self._pressed_hit
        self._pressed_hit = None
        try:
            _user32.ReleaseCapture()
        except OSError:
            pass
        self.title_bar.set_native_pressed(None)

        # 松开时鼠标还在按钮上才执行（与系统标题栏行为一致）
        hit = self._hit_code_at_cursor(hwnd)
        if hit in (HTMINBUTTON, HTMAXBUTTON, HTCLOSE):
            self.title_bar.set_native_hover(hit)
        else:
            self.title_bar.set_native_hover(None)
        if pressed is not None and hit == pressed:
            self._perform_caption_action(hwnd, pressed)

    def _hit_code_at_cursor(self, hwnd):
        point = wt.POINT()
        if not _user32.GetCursorPos(ctypes.byref(point)):
            return None
        lparam = ((point.y & 0xFFFF) << 16) | (point.x & 0xFFFF)
        return self._on_hit_test(hwnd, lparam)

    def _perform_caption_action(self, hwnd, hit_code):
        """用系统命令执行按钮动作（动画/状态同步都交给 Windows 自己）。"""
        try:
            style = _user32.GetWindowLongPtrW(wt.HWND(hwnd), GWL_STYLE)
        except OSError:
            return
        if hit_code == HTCLOSE:
            if style & WS_SYSMENU:
                _user32.PostMessageW(wt.HWND(hwnd), WM_CLOSE, 0, 0)
        elif hit_code == HTMINBUTTON:
            if style & WS_MINIMIZEBOX:
                _user32.PostMessageW(wt.HWND(hwnd), WM_SYSCOMMAND, SC_MINIMIZE, 0)
        elif hit_code == HTMAXBUTTON:
            if style & WS_MAXIMIZEBOX:
                command = SC_RESTORE if _user32.IsZoomed(wt.HWND(hwnd)) else SC_MAXIMIZE
                _user32.PostMessageW(wt.HWND(hwnd), WM_SYSCOMMAND, command, 0)

    # ---------------------------------------------------------------- 命中测试
    def _on_hit_test(self, hwnd, lparam):
        if self.title_bar is None:
            return None
        try:
            # 注意：窗口被系统最大化时，Qt 可能会把“无边框 + 铺满屏幕”误判成
            # 全屏（windowState 里同时出现 WindowFullScreen）。用 IsZoomed
            # 区分真正的全屏，否则最大化后标题栏按钮会失去命中测试。
            if not _user32.IsZoomed(hwnd) and self.window.isFullScreen():
                return None
        except (RuntimeError, OSError):
            return None

        hint = self._titlebar_hit_test(hwnd, lparam)
        if hint in ("minimize", "maximize", "close"):
            return {"minimize": HTMINBUTTON,
                    "maximize": HTMAXBUTTON,
                    "close": HTCLOSE}[hint]
        if hint == "client":
            # 交给 Qt 处理（Qt 交互模式的按钮、标题栏里的自定义控件）
            return None

        border = self._resize_border_hit_test(hwnd, lparam)
        if border is not None:
            return border
        if hint == "caption":
            return HTCAPTION
        return None

    def _titlebar_hit_test(self, hwnd, lparam):
        title_bar = self.title_bar
        try:
            if not title_bar.isVisible():
                return None
            point = _screen_point(lparam)
            if not _user32.ScreenToClient(hwnd, ctypes.byref(point)):
                return None
            dpr = self.window.devicePixelRatioF() or 1.0
            local = QPointF(point.x / dpr, point.y / dpr)
            origin = title_bar.mapTo(self.window, QPoint(0, 0))
            rect = QRectF(origin.x(), origin.y(),
                          title_bar.width(), title_bar.height())
            if not rect.contains(local):
                return None
            return title_bar.hit_test(local - QPointF(origin))
        except RuntimeError:
            return None

    def _resize_border_hit_test(self, hwnd, lparam):
        """最大化时没有可拖拽边框；否则按系统边框厚度判断 8 个方向。"""
        try:
            if _user32.IsZoomed(hwnd):
                return None
        except OSError:
            return None
        point = _screen_point(lparam)
        if not _user32.ScreenToClient(hwnd, ctypes.byref(point)):
            return None
        client = wt.RECT()
        if not _user32.GetClientRect(hwnd, ctypes.byref(client)):
            return None
        width, height = client.right - client.left, client.bottom - client.top
        border_x, border_y = _resize_border_size(hwnd)
        x, y = point.x, point.y
        if not (0 <= x < width and 0 <= y < height):
            return None
        left = x < border_x
        right = x >= width - border_x
        top = y < border_y
        bottom = y >= height - border_y
        if top and left:
            return HTTOPLEFT
        if top and right:
            return HTTOPRIGHT
        if bottom and left:
            return HTBOTTOMLEFT
        if bottom and right:
            return HTBOTTOMRIGHT
        if left:
            return HTLEFT
        if right:
            return HTRIGHT
        if top:
            return HTTOP
        if bottom:
            return HTBOTTOM
        return None

    # --------------------------------------------------------------- 其他消息
    def _apply_min_max_info(self, hwnd, lparam):
        """把 QWidget 的 minimumSize / maximumSize 同步给系统的拖拽缩放。"""
        try:
            info = _MINMAXINFO.from_address(int(lparam))
            dpi = 96
            if _HAS_DPI_API:
                dpi = _user32.GetDpiForWindow(hwnd) or 96
            scale = dpi / 96.0
            minimum = self.window.minimumSize()
            maximum = self.window.maximumSize()
            if minimum.width() > 0:
                info.ptMinTrackSize.x = int(round(minimum.width() * scale))
            if minimum.height() > 0:
                info.ptMinTrackSize.y = int(round(minimum.height() * scale))
            if 0 < maximum.width() < QWIDGETSIZE_MAX:
                info.ptMaxTrackSize.x = int(round(maximum.width() * scale))
            if 0 < maximum.height() < QWIDGETSIZE_MAX:
                info.ptMaxTrackSize.y = int(round(maximum.height() * scale))
        except (RuntimeError, OSError):
            pass

    def _on_setting_change(self, lparam):
        if not self.auto_theme or not lparam:
            return
        try:
            text = ctypes.wstring_at(lparam)
        except (ValueError, OSError):
            return
        if text and "ImmersiveColorSet" in text:
            dark = system_is_dark()
            if dark != self._dark:
                self.set_dark(dark)


class _WindowsFrameMixin:
    """为窗口类提供 nativeEvent 转发（子类在 __init__ 里创建 self._frame_helper）。"""

    _frame_helper: Optional[WindowsFrameHelper] = None

    def nativeEvent(self, eventType, message):
        helper = getattr(self, "_frame_helper", None)
        if helper is not None:
            handled, result = helper.handle_message(eventType, message)
            if handled:
                return True, result
        return super().nativeEvent(eventType, message)


class TitleBarWindow(_WindowsFrameMixin, QWidget):
    """自带 Windows 11 风格标题栏的顶层窗口（QWidget 版）。

    内容放进 ``self.body``（它自带一个空的 QVBoxLayout，直接用即可）::

        class MyWindow(TitleBarWindow):
            def __init__(self):
                super().__init__(title="我的应用")
                self.body_layout.addWidget(QTextEdit())

    原生效果：窗口阴影、圆角、最小化/最大化动画、Aero Snap、Win+方向键、
    双击标题栏最大化、右键标题栏系统菜单、Windows 11 贴靠布局悬浮面板。
    """

    def __init__(self, title: str = "", icon: Optional[QIcon] = None,
                 parent=None, *, native_caption: bool = True,
                 dark: Optional[bool] = None, auto_theme: bool = True,
                 rounded: bool = True):
        # 非 Windows 平台没有原生无边框拖动逻辑，保留系统边框以免窗口不可操作
        flags = Qt.Window
        if _IS_WINDOWS:
            flags |= Qt.FramelessWindowHint
        super().__init__(parent, flags)

        self._build_title_bar(title, icon, native_caption, dark)
        self._frame_helper = WindowsFrameHelper(
            self, self._title_bar, native_caption=native_caption,
            dark=dark, rounded=rounded, auto_theme=auto_theme)
        self._frame_helper.install()

    # ------------------------------------------------------------------ 构建
    def _build_title_bar(self, title, icon, native_caption, dark):
        self._title_bar = TitleBar(self, title=title, icon=icon,
                                   native_caption=native_caption, dark=dark)
        self.setWindowTitle(title or "")
        if icon is not None:
            self.setWindowIcon(icon)

        self.body = QWidget(self)
        self.body.setObjectName("TitleBarWindowBody")
        self.body.setAttribute(Qt.WA_StyledBackground, True)
        self.body_layout = QVBoxLayout(self.body)
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(0)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._title_bar)
        layout.addWidget(self.body, 1)
        if not _IS_WINDOWS:
            # 非 Windows 平台保留系统标题栏，隐藏自绘标题栏以免出现两条
            self._title_bar.hide()

    # ------------------------------------------------------------------ 属性
    @property
    def title_bar(self) -> TitleBar:
        return self._title_bar

    def set_title(self, title: str):
        self._title_bar.set_title(title)
        self.setWindowTitle(title)

    def set_title_bar_icon(self, icon: Optional[QIcon]):
        self._title_bar.set_icon(icon)

    def set_dark(self, dark: bool):
        if self._frame_helper is not None:
            self._frame_helper.set_dark(dark)
        else:
            self._title_bar.set_dark(dark)

    def is_dark(self) -> bool:
        return self._title_bar.is_dark()


class TitleBarMainWindow(_WindowsFrameMixin, QMainWindow):
    """自带自定义标题栏的 QMainWindow。

    标题栏固定在窗口最顶端，通过 ``setContentsMargins()`` 为它留出高度，
    所以 ``menuBar()`` / ``statusBar()`` / dock 等 QMainWindow 功能都能照常
    使用（菜单栏会显示在标题栏下方）。
    """

    def __init__(self, title: str = "", icon: Optional[QIcon] = None,
                 parent=None, *, native_caption: bool = True,
                 dark: Optional[bool] = None, auto_theme: bool = True,
                 rounded: bool = True):
        flags = Qt.Window
        if _IS_WINDOWS:
            flags |= Qt.FramelessWindowHint
        super().__init__(parent, flags)

        self._title_bar = TitleBar(self, title=title, icon=icon,
                                   native_caption=native_caption, dark=dark,
                                   parent=self)
        self._title_bar.setGeometry(0, 0, self.width(), TitleBar.HEIGHT)
        self._title_bar.raise_()
        self.setContentsMargins(0, TitleBar.HEIGHT, 0, 0)
        self.setWindowTitle(title or "")
        if icon is not None:
            self.setWindowIcon(icon)
        if not _IS_WINDOWS:
            # 非 Windows 平台保留系统标题栏，隐藏自绘标题栏以免出现两条
            self._title_bar.hide()
            self.setContentsMargins(0, 0, 0, 0)

        self._frame_helper = WindowsFrameHelper(
            self, self._title_bar, native_caption=native_caption,
            dark=dark, rounded=rounded, auto_theme=auto_theme)
        self._frame_helper.install()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        title_bar = getattr(self, "_title_bar", None)
        if title_bar is not None:
            title_bar.setGeometry(0, 0, self.width(), TitleBar.HEIGHT)
            title_bar.raise_()

    @property
    def title_bar(self) -> TitleBar:
        return self._title_bar

    def set_title(self, title: str):
        self._title_bar.set_title(title)
        self.setWindowTitle(title)

    def set_title_bar_icon(self, icon: Optional[QIcon]):
        self._title_bar.set_icon(icon)

    def set_dark(self, dark: bool):
        if self._frame_helper is not None:
            self._frame_helper.set_dark(dark)
        else:
            self._title_bar.set_dark(dark)

    def is_dark(self) -> bool:
        return self._title_bar.is_dark()


# =============================================================================
# 演示程序
# =============================================================================

def _demo_icon() -> QIcon:
    """画一个简单的 16x16 应用图标（蓝色圆角方块 + 白色窗口图案）。"""
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    try:
        painter.setRenderHint(QPainter.Antialiasing, True)
        gradient = QLinearGradient(0, 0, 64, 64)
        gradient.setColorAt(0.0, QColor("#4CC2FF"))
        gradient.setColorAt(1.0, QColor("#0067C0"))
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawRoundedRect(QRectF(2, 2, 60, 60), 14, 14)

        painter.setBrush(QColor(255, 255, 255, 235))
        painter.drawRoundedRect(QRectF(16, 16, 32, 32), 5, 5)
        painter.setBrush(QColor("#0067C0"))
        painter.drawRoundedRect(QRectF(21, 21, 22, 7), 2, 2)
    finally:
        painter.end()
    return QIcon(pixmap)


def _demo_body_stylesheet(dark: bool) -> str:
    if dark:
        bg, fg, muted, panel = "#191919", "#F5F5F5", "#A0A0A0", "#242424"
    else:
        bg, fg, muted, panel = "#FAFAFA", "#1A1A1A", "#5D5D5D", "#FFFFFF"
    return f"""
QWidget#DemoBody {{
    background-color: {bg};
}}
QLabel#DemoHeading {{
    color: {fg};
    font-size: 26px;
    font-family: "Segoe UI Variable Display", "Segoe UI";
}}
QLabel#DemoText {{
    color: {muted};
    font-size: 13px;
    font-family: "Segoe UI Variable Text", "Segoe UI";
}}
QTextEdit#DemoTextEdit {{
    background-color: {panel};
    color: {fg};
    border: 1px solid {"#3A3A3A" if dark else "#E3E3E3"};
    border-radius: 8px;
    padding: 8px;
    font-size: 13px;
    font-family: "Segoe UI Variable Text", "Segoe UI";
}}
QPushButton {{
    background-color: {panel};
    color: {fg};
    border: 1px solid {"#3A3A3A" if dark else "#DADADA"};
    border-radius: 6px;
    padding: 7px 16px;
    font-size: 13px;
    font-family: "Segoe UI Variable Text", "Segoe UI";
}}
QPushButton:hover {{
    background-color: {"#2E2E2E" if dark else "#F0F0F0"};
}}
QPushButton:pressed {{
    background-color: {"#3A3A3A" if dark else "#E2E2E2"};
}}
"""


class DemoWindow(TitleBarWindow):
    def __init__(self):
        super().__init__(title="自定义标题栏 · Windows 11 效果演示", icon=_demo_icon())
        self.setMinimumSize(560, 360)
        self.resize(1000, 660)
        # 标题栏跟随系统深/浅色时，内容区也一起换色
        self.title_bar.themeChanged.connect(self._on_theme_changed)
        self._init_content()
        self._apply_theme(self.is_dark())

    def _init_content(self):
        self.body.setObjectName("DemoBody")
        layout = self.body_layout
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(14)

        heading = QLabel("PySide6 自定义标题栏")
        heading.setObjectName("DemoHeading")
        layout.addWidget(heading)

        description = QLabel(
            "原生窗口效果全部保留：\n"
            "· 窗口阴影 / Windows 11 圆角\n"
            "· 最小化、最大化、还原的 DWM 动画\n"
            "· 拖动标题栏移动窗口，双击最大化/还原\n"
            "· 右键标题栏弹出系统菜单（Alt+Space 同款）\n"
            "· Aero Snap / Win+方向键贴靠\n"
            "· 鼠标悬停最大化按钮出现 Windows 11 贴靠布局")
        description.setObjectName("DemoText")
        description.setWordWrap(True)
        layout.addWidget(description)

        self._text_edit = QTextEdit(self.body)
        self._text_edit.setObjectName("DemoTextEdit")
        self._text_edit.setReadOnly(True)
        self._text_edit.setPlainText(
            "标题栏的按钮走 Windows 原生非客户区命中测试：\n"
            "    WM_NCHITTEST -> HTMINBUTTON / HTMAXBUTTON / HTCLOSE\n"
            "悬停时系统会自动提供 Windows 11 贴靠布局；\n"
            "点击由组件自己 SetCapture + WM_SYSCOMMAND 触发，\n"
            "既保证最小化/最大化可靠，也避免 DefWindowProc 把标准\n"
            "标题栏按钮画进客户区（按下时按钮旁边出现白底按钮）。\n\n"
            "窗口本身保留了 WS_OVERLAPPEDWINDOW 样式，DWM 因此会提供\n"
            "阴影、圆角、最小化/最大化动画、任务栏预览与 Aero Snap。")
        layout.addWidget(self._text_edit, 1)

        buttons = QHBoxLayout()
        buttons.setSpacing(8)
        minimize_btn = QPushButton("最小化")
        minimize_btn.clicked.connect(self.showMinimized)
        maximize_btn = QPushButton("最大化 / 还原")
        maximize_btn.clicked.connect(
            lambda: self.showNormal() if self.isMaximized() else self.showMaximized())
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.close)
        self._theme_btn = QPushButton("切换深/浅色")
        self._theme_btn.clicked.connect(self._toggle_theme)
        for button in (minimize_btn, maximize_btn, close_btn, self._theme_btn):
            buttons.addWidget(button)
        buttons.addStretch(1)
        layout.addLayout(buttons)

        self._status = QLabel("")
        self._status.setObjectName("DemoText")
        layout.addWidget(self._status)
        self._update_status()

    def _apply_theme(self, dark: bool):
        self.body.setStyleSheet(_demo_body_stylesheet(dark))
        self.set_dark(dark)
        if hasattr(self, "_theme_btn"):
            self._theme_btn.setText("切换为浅色" if dark else "切换为深色")

    def _on_theme_changed(self, dark: bool):
        self.body.setStyleSheet(_demo_body_stylesheet(dark))
        if hasattr(self, "_theme_btn"):
            self._theme_btn.setText("切换为浅色" if dark else "切换为深色")

    def _toggle_theme(self):
        self._apply_theme(not self.is_dark())

    def _update_status(self):
        state = "最大化" if self.isMaximized() else "窗口化"
        self._status.setText(f"窗口状态：{state}　（拖动标题栏 / 双击标题栏试试）")

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == QEvent.WindowStateChange and hasattr(self, "_status"):
            self._update_status()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("PySide6 Custom Titlebar")
    window = DemoWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
