"""Windows 11 风格自定义标题栏（保留 Windows 原生视觉效果）。

特点
----
* 窗口阴影、Windows 11 圆角、最小化/最大化/还原的 DWM 动画全部保留；
* 拖动标题栏移动窗口、双击最大化/还原；
* 自带 **Qt 自绘系统菜单**：左键按下应用图标、右键按下标题栏
  （按钮区域除外）或 Alt+Space 弹出；菜单项为
  还原/移动/大小/最小化/最大化/关闭，支持“移动”“大小”提示模式；
* **双击应用图标直接关闭窗口**（不经过菜单里的“关闭”）；
* Aero Snap、Win + 方向键贴靠、任务栏预览照常工作；
* 最大化按钮悬停时出现 Windows 11 的“贴靠布局”悬浮面板
  （按钮走原生 HTMINBUTTON / HTMAXBUTTON / HTCLOSE 命中测试）；
* 按钮点击由组件自己 SetCapture + WM_SYSCOMMAND 完成：最小化/最大化可靠，
  也不会出现 DefWindowProc 画出来的“白底原生按钮”残影；
* 标题、图标、深/浅色主题可换，窗口变窄时标题自动省略；
* 标题栏高度可在构造时用 ``height=...`` 指定，按钮尺寸、命中测试区域
  与 QMainWindow 的预留边距都会同步（见 ``set_title_bar_height()``）；
* 窗口无边框，但 Qt 的 resize()/move() 仍然按客户区精确生效。

用法
----
继承 ``TitleBarWindow``（QVBoxLayout + 内容区）::

    class MyWindow(TitleBarWindow):
        def __init__(self):
            super().__init__(title="我的应用", icon=QIcon("app.ico"), height=40)
            self.body_layout.addWidget(QTextEdit())

或者继承 ``TitleBarMainWindow``（QMainWindow，标题栏固定在顶部，
菜单栏会显示在标题栏下方）::

    class MyWindow(TitleBarMainWindow):
        def __init__(self):
            super().__init__(title="我的应用")
            self.setCentralWidget(QTextEdit())

注意
----
* 标题栏高度在构造时用 ``height=...`` 指定（逻辑像素，默认取
  ``TitleBar.HEIGHT``），运行时用 ``set_title_bar_height()`` 修改；按钮尺寸、非客户区命中测试
  区域、``TitleBarMainWindow`` 为标题栏预留的边距都由同一个高度推导。
  直接改 ``TitleBar.HEIGHT`` 只对之后新建的实例生效。
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
WM_NCRBUTTONDOWN = 0x00A4
WM_NCRBUTTONUP = 0x00A5
WM_NCMOUSELEAVE = 0x02A2
WM_CONTEXTMENU = 0x007B
WM_MOUSEMOVE = 0x0200
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202
WM_RBUTTONDOWN = 0x0204
WM_KEYDOWN = 0x0100
WM_SYSKEYDOWN = 0x0104
WM_SETCURSOR = 0x0020
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
SC_KEYMENU = 0xF100
WM_CLOSE = 0x0010

VK_SPACE = 0x20
VK_ESCAPE = 0x1B

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
SM_CXCURSOR = 13
SM_CYCURSOR = 14

# 系统光标资源（MAKEINTRESOURCE 编号）
IDC_ARROW = 32512
IDC_SIZEWE = 32644
IDC_SIZENS = 32645
IDC_SIZEALL = 32646

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
    _user32.GetWindowRect.restype = wt.BOOL
    _user32.GetWindowRect.argtypes = [wt.HWND, ctypes.POINTER(wt.RECT)]
    _user32.SetCursorPos.restype = wt.BOOL
    _user32.SetCursorPos.argtypes = [ctypes.c_int, ctypes.c_int]
    _user32.SetCursor.restype = wt.HANDLE
    _user32.SetCursor.argtypes = [wt.HANDLE]
    _user32.LoadCursorW.restype = wt.HANDLE
    _user32.LoadCursorW.argtypes = [wt.HINSTANCE, ctypes.c_void_p]
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


def _window_rect(hwnd):
    """窗口物理矩形（屏幕坐标）；失败返回 None。"""
    if not _IS_WINDOWS:
        return None
    rect = wt.RECT()
    try:
        if not _user32.GetWindowRect(wt.HWND(hwnd), ctypes.byref(rect)):
            return None
    except OSError:
        return None
    return rect


_CURSOR_CACHE = {}


def _system_cursor(cursor_id):
    """加载（并缓存）系统光标句柄；失败返回 None。"""
    if not _IS_WINDOWS:
        return None
    if cursor_id in _CURSOR_CACHE:
        return _CURSOR_CACHE[cursor_id]
    handle = None
    try:
        # MAKEINTRESOURCE：整数资源编号按 LPWSTR 指针传入
        handle = _user32.LoadCursorW(None, ctypes.c_void_p(cursor_id))
    except OSError:
        handle = None
    _CURSOR_CACHE[cursor_id] = handle
    return handle


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

#: 标题栏默认高度（逻辑像素）。``TitleBar.HEIGHT`` 保留这个值，
#: 子类/老代码仍可覆盖类属性；实例高度请用构造参数 ``height=``。
_DEFAULT_TITLEBAR_HEIGHT = 48

#: 标题栏按钮宽度（逻辑像素）；按钮高度始终等于标题栏高度。
_CAPTION_BUTTON_WIDTH = 48


class CaptionButton(FontIcon):
    """标题栏按钮（最小化 / 最大化 / 关闭）。

    默认（native_caption=True）由 Windows 非客户区命中测试接管：
    鼠标事件不会到达 Qt，按钮只负责画图标和悬停/按下背景。
    若标题栏使用 native_caption=False，则按钮自己处理鼠标事件，
    并发出 clicked 信号。

    按钮高度由标题栏高度决定（见 ``height`` 参数），保证点击/悬停区域
    与视觉上的按钮完全一致。
    """

    hovered = Signal(bool)
    pressed = Signal(bool)
    clicked = Signal()

    def __init__(self, role: str, parent=None, *,
                 height: int = _DEFAULT_TITLEBAR_HEIGHT):
        super().__init__(_CAPTION_GLYPHS[role], size=10, parent=parent)
        self._role = role
        self._height = max(1, int(height))
        self._caption_state = "normal"
        self.setObjectName("CaptionButton")
        self.setProperty("captionRole", role)
        self.setProperty("captionState", "normal")
        self.setProperty("windowActive", True)
        self.setAccessibleName(_CAPTION_ACCESSIBLE_NAMES[role])
        # Windows 11 标题栏按钮：宽度固定（_CAPTION_BUTTON_WIDTH），高度铺满标题栏
        self.setFixedSize(_CAPTION_BUTTON_WIDTH, self._height)
        self.setAlignment(Qt.AlignCenter)
        self.setFocusPolicy(Qt.NoFocus)
        self.setCursor(Qt.ArrowCursor)
        # 原生模式下鼠标事件由 Windows 非客户区命中测试接管；
        # Qt 交互模式下会由 set_qt_interactive(True) 打开。
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)

    # ---------------------------------------------------------------- 状态
    def role(self) -> str:
        return self._role

    def caption_height(self) -> int:
        """按钮当前高度（逻辑像素），始终等于标题栏高度。"""
        return self._height

    def set_caption_height(self, height: int):
        """跟随标题栏高度变化（按钮即命中区域，二者必须同步）。"""
        height = max(1, int(height))
        if height == self._height:
            return
        self._height = height
        self.setFixedSize(_CAPTION_BUTTON_WIDTH, height)

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


# =============================================================================
# Qt 自绘系统菜单（Windows 11 风格）
# =============================================================================

#: 菜单主题（无深色适配）
_MENU_BG = "#F9F9F9"
_MENU_BORDER = "#E8E8E8"
_MENU_SEPARATOR = "#E2E2E2"
_MENU_TEXT = "#000000"
_MENU_HOVER_BG = "#F0F0F0"
_MENU_DISABLED_TEXT = "#ABABAB"
_MENU_FONT_PX = 12
_MENU_ICON_PX = 8
#: 固定菜单宽度（逻辑像素，按 96 DPI 设计）；可见面板宽度
_MENU_PANEL_WIDTH = 200
_MENU_RADIUS = 4
_MENU_OUTER_MARGIN = 8
#: 行内容/悬停高亮/分割线相对面板左右边缘的留白
_MENU_CONTENT_INSET = 8
#: fonticon 左边缘距面板左侧；描述文字左边缘距面板左侧
_MENU_ICON_LEFT = 16
_MENU_ICON_SLOT = 16
_MENU_TEXT_LEFT = 32
#: 右侧 Alt+F4 距面板右边缘
_MENU_SHORTCUT_RIGHT = 16
_MENU_ITEM_V_MARGIN = 4
_MENU_SEPARATOR_H = 1
_MENU_SHORTCUT_GAP = 16
_MENU_FADE_MS = 250
_MENU_SPACE_GAP = 16
#: 双击图标“第二次按下”的位置容差（逻辑像素）
_ICON_DOUBLE_CLICK_SLOP = 8

_MENU_SEPARATOR_KEY = "separator"


def _system_menu_position(anchor: QPoint, panel_size: QSize,
                          available: QRect, full: QRect, *,
                          margin: int = _MENU_OUTER_MARGIN,
                          gap: int = _MENU_SPACE_GAP) -> QPoint:
    """计算系统菜单弹窗左上角（Qt 逻辑坐标）。

    * 默认：可见面板左上角对准 ``anchor``；
    * 下方空间不足（离任务栏/显示器下边界 < ``gap``）：可见面板左下角对准
      ``anchor``（菜单向上展开）；
    * 水平超出工作区 / 翻转后超出屏幕顶部时贴边。
    """
    popup_w = panel_size.width() + 2 * margin
    popup_h = panel_size.height() + 2 * margin

    x = anchor.x() - margin
    y = anchor.y() - margin

    # 任务栏可见时用工作区下边界；自动隐藏/无任务栏时用显示器下边界
    boundary = (available.bottom() if available.bottom() < full.bottom()
                else full.bottom())
    if boundary - (anchor.y() + panel_size.height()) < gap:
        y = anchor.y() - panel_size.height() - margin

    # 水平贴边
    if x + popup_w > available.right() + 1:
        x = available.right() + 1 - popup_w
    if x < available.left():
        x = available.left()

    # 垂直贴边（翻转后可能超出屏幕顶部）
    if y < available.top():
        y = available.top()
    if y + popup_h > full.bottom() + 1:
        y = full.bottom() + 1 - popup_h
    return QPoint(x, y)


class _SystemMenuItem:
    """菜单项数据（纯数据 + 弹窗本地矩形）。"""

    __slots__ = ("key", "text", "glyph", "shortcut", "enabled",
                 "separator", "rect")

    def __init__(self, key, text, glyph="", shortcut="", *,
                 enabled=True, separator=False):
        self.key = key
        self.text = text
        self.glyph = glyph
        self.shortcut = shortcut
        self.enabled = bool(enabled)
        self.separator = bool(separator)
        self.rect = QRect()

    @classmethod
    def make_separator(cls):
        return cls(_MENU_SEPARATOR_KEY, "", separator=True)


class SystemMenu(QWidget):
    """Qt 自绘系统菜单（还原/移动/大小/最小化/最大化/关闭）。

    由 ``TitleBar.show_system_menu()`` 创建和弹出；也可单独实例化用于测试。
    可见面板固定 200px 宽（96 DPI 逻辑像素）、4px 圆角；行高随字体自适应。
    弹窗自身负责：定位、渐显（125ms，无渐隐）、悬停/按下、圆角阴影绘制、
    点击任意位置关闭（Qt::Popup 的全局鼠标抓取 + WA_NoMouseReplay）。
    """

    actionTriggered = Signal(str)
    iconDoubleClicked = Signal()

    def __init__(self, window=None, parent=None):
        super().__init__(parent)
        self._window = window
        self._items = []
        self._panel_size = QSize(_MENU_PANEL_WIDTH, 1)
        self._text_x = _MENU_OUTER_MARGIN + _MENU_TEXT_LEFT
        self._icon_x = _MENU_OUTER_MARGIN + _MENU_ICON_LEFT
        self._shortcut_right = (_MENU_OUTER_MARGIN + _MENU_PANEL_WIDTH
                                - _MENU_SHORTCUT_RIGHT)
        self._hover_index = -1
        self._pressed_index = -1
        self._has_press = False

        # 双击图标关闭：只对“左键图标打开”的菜单生效
        self._allow_icon_double_click = False
        self._icon_anchor = QPoint()
        self._opened_timer = QElapsedTimer()

        self._fade_anim = None

        self._label_font = QFont(self.font())
        self._label_font.setPixelSize(_MENU_FONT_PX)
        self._label_font.setWeight(QFont.Normal)
        self._bold_font = QFont(self._label_font)
        self._bold_font.setWeight(QFont.Bold)
        self._icon_font = QFont()
        self._icon_font.setFamilies(_FONT_FAMILIES)
        self._icon_font.setPixelSize(_MENU_ICON_PX)
        self._icon_font.setWeight(QFont.Normal)

        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint
                            | Qt.NoDropShadowWindowHint
                            | Qt.WindowDoesNotAcceptFocus)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self.setAttribute(Qt.WA_NoMouseReplay, True)
        self.setFocusPolicy(Qt.NoFocus)
        self.setMouseTracking(True)

    # ------------------------------------------------------------------ 构建
    def _rebuild(self, maximized: bool, supports_hints: bool):
        glyphs = _CAPTION_GLYPHS
        self._items = [
            _SystemMenuItem("restore", "还原(R)", glyphs["restore"],
                            enabled=maximized),
            _SystemMenuItem("move", "移动(M)",
                            enabled=(not maximized and supports_hints)),
            _SystemMenuItem("size", "大小(S)",
                            enabled=(not maximized and supports_hints)),
            _SystemMenuItem("minimize", "最小化(N)", glyphs["minimize"]),
            _SystemMenuItem("maximize", "最大化(X)", glyphs["maximize"],
                            enabled=not maximized),
            _SystemMenuItem.make_separator(),
            _SystemMenuItem("close", "关闭(C)", glyphs["close"], "Alt+F4"),
        ]
        self._layout_items()
        self._hover_index = -1
        self._pressed_index = -1
        self._has_press = False

    def _layout_items(self):
        label_fm = QFontMetrics(self._label_font)
        icon_fm = QFontMetrics(self._icon_font)
        row_h = max(label_fm.height(), icon_fm.height()) + 2 * _MENU_ITEM_V_MARGIN

        # 宽度固定（按 96 DPI 设计），高度按行数自适应
        panel_w = _MENU_PANEL_WIDTH
        panel_h = 0
        for item in self._items:
            panel_h += (_MENU_SEPARATOR_H if item.separator else row_h)

        # 放置每行（弹窗本地坐标，含 8px 阴影外边距）
        y = _MENU_OUTER_MARGIN
        for item in self._items:
            if item.separator:
                item.rect = QRect(_MENU_OUTER_MARGIN, y, panel_w,
                                  _MENU_SEPARATOR_H)
                y += _MENU_SEPARATOR_H
            else:
                item.rect = QRect(_MENU_OUTER_MARGIN, y, panel_w, row_h)
                y += row_h

        self._panel_size = QSize(panel_w, panel_h)
        self._text_x = _MENU_OUTER_MARGIN + _MENU_TEXT_LEFT
        self._icon_x = _MENU_OUTER_MARGIN + _MENU_ICON_LEFT
        self._shortcut_right = (_MENU_OUTER_MARGIN + panel_w
                                - _MENU_SHORTCUT_RIGHT)
        self.resize(panel_w + 2 * _MENU_OUTER_MARGIN,
                    panel_h + 2 * _MENU_OUTER_MARGIN)

    # ------------------------------------------------------------------ 弹出
    def panel_size(self) -> QSize:
        """可见面板尺寸（不含 8px 阴影外边距）。"""
        return QSize(self._panel_size)

    def popup_at(self, anchor: QPoint, *, icon_press: bool = False):
        window = self._window
        if window is None:
            return
        try:
            maximized = bool(window.isMaximized())
        except RuntimeError:
            return
        helper = getattr(window, "_frame_helper", None)
        self._rebuild(maximized, _IS_WINDOWS and helper is not None)

        anchor = QPoint(anchor)
        self._allow_icon_double_click = bool(icon_press)
        self._icon_anchor = QPoint(anchor)
        self._opened_timer.start()

        try:
            screen = QGuiApplication.screenAt(anchor) or self._window.screen()
        except RuntimeError:
            screen = QGuiApplication.primaryScreen()
        if screen is None:
            screen = QGuiApplication.primaryScreen()
        if screen is None:
            return
        pos = _system_menu_position(anchor, self._panel_size,
                                    screen.availableGeometry(),
                                    screen.geometry())
        self.setGeometry(QRect(pos, self.size()))
        self.setWindowOpacity(0.0)
        self.show()
        self.raise_()
        self._start_fade()
        self.update()

    def _start_fade(self):
        self._fade_anim = QPropertyAnimation(self, b"windowOpacity", self)
        self._fade_anim.setDuration(_MENU_FADE_MS)
        self._fade_anim.setStartValue(0.0)
        self._fade_anim.setEndValue(1.0)
        self._fade_anim.setEasingCurve(QEasingCurve.OutCubic)
        self._fade_anim.start()

    def hideEvent(self, event):
        if self._fade_anim is not None:
            self._fade_anim.stop()
            self._fade_anim = None
        self.setWindowOpacity(1.0)
        self._hover_index = -1
        self._pressed_index = -1
        self._has_press = False
        self._allow_icon_double_click = False
        super().hideEvent(event)

    # ------------------------------------------------------------------ 交互
    def _item_at(self, point: QPoint) -> int:
        for index, item in enumerate(self._items):
            if item.separator:
                continue
            if item.rect.contains(point):
                return index
        return -1

    def mouseMoveEvent(self, event):
        index = self._item_at(event.position().toPoint())
        if index != self._hover_index:
            self._hover_index = index
            self.update()
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        # 双击图标关闭：第二次按下落在菜单窗口上（位置/时间都匹配）时关窗
        if (event.button() == Qt.LeftButton
                and self._allow_icon_double_click
                and self._opened_timer.isValid()
                and self._opened_timer.elapsed() <= QApplication.doubleClickInterval()
                and (event.globalPosition().toPoint() - self._icon_anchor)
                .manhattanLength() <= _ICON_DOUBLE_CLICK_SLOP):
            self._allow_icon_double_click = False
            self.hide()
            self.iconDoubleClicked.emit()
            event.accept()
            return

        if event.button() == Qt.RightButton:
            # 菜单里右键也视为“点击任一地方消除”
            self.hide()
            event.accept()
            return

        if event.button() == Qt.LeftButton:
            self._pressed_index = self._item_at(event.position().toPoint())
            self._has_press = True
            self.update()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self._has_press:
            self._has_press = False
            index = self._item_at(event.position().toPoint())
            if index == self._pressed_index and index >= 0:
                item = self._items[index]
                if item.enabled:
                    self.hide()
                    self.actionTriggered.emit(item.key)
                    event.accept()
                    return
            self.hide()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def leaveEvent(self, event):
        if self._hover_index != -1:
            self._hover_index = -1
            self.update()
        super().leaveEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.hide()
            event.accept()
            return
        super().keyPressEvent(event)

    # ------------------------------------------------------------------ 绘制
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)

        margin = _MENU_OUTER_MARGIN
        panel = QRectF(self.rect()).adjusted(margin, margin, -margin, -margin)
        path = QPainterPath()
        path.addRoundedRect(panel, _MENU_RADIUS, _MENU_RADIUS)

        self._paint_shadow(painter, panel)
        painter.fillPath(path, QColor(_MENU_BG))

        painter.save()
        painter.setClipPath(path)

        for index, item in enumerate(self._items):
            if item.separator:
                y = item.rect.top() + 0.5
                painter.setPen(QPen(QColor(_MENU_SEPARATOR), 1))
                painter.drawLine(
                    QPointF(panel.left() + _MENU_CONTENT_INSET, y),
                    QPointF(panel.right() - _MENU_CONTENT_INSET, y))
                continue

            if index in (self._hover_index, self._pressed_index):
                hover_rect = QRectF(item.rect).adjusted(
                    _MENU_CONTENT_INSET, 0, -_MENU_CONTENT_INSET, 0)
                painter.fillRect(hover_rect, QColor(_MENU_HOVER_BG))

            color = QColor(_MENU_TEXT if item.enabled else _MENU_DISABLED_TEXT)
            content_h = item.rect.height() - 2 * _MENU_ITEM_V_MARGIN
            is_close = item.key == "close"

            if item.glyph:
                painter.setFont(self._icon_font)
                painter.setPen(color)
                painter.drawText(
                    QRectF(self._icon_x, item.rect.top() + _MENU_ITEM_V_MARGIN,
                           _MENU_ICON_SLOT, content_h),
                    Qt.AlignLeft | Qt.AlignVCenter, item.glyph)

            text_font = self._bold_font if is_close else self._label_font
            painter.setFont(text_font)
            painter.setPen(color)
            text_rect = QRectF(self._text_x, item.rect.top(),
                               max(0.0, self._shortcut_right - self._text_x),
                               item.rect.height())
            if item.shortcut:
                shortcut_w = QFontMetrics(self._bold_font).horizontalAdvance(
                    item.shortcut)
                text_rect.setWidth(max(0.0, text_rect.width()
                                       - shortcut_w - _MENU_SHORTCUT_GAP))
                shortcut_rect = QRectF(self._shortcut_right - shortcut_w,
                                       item.rect.top(), shortcut_w,
                                       item.rect.height())
                painter.setFont(self._bold_font)
                painter.drawText(shortcut_rect,
                                 Qt.AlignRight | Qt.AlignVCenter, item.shortcut)
                painter.setFont(text_font)
            painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter,
                             item.text)

        painter.restore()

        # 边框画在 panel 内侧半像素处，保证 1px 在 100% 缩放下不糊
        painter.setPen(QPen(QColor(_MENU_BORDER), 1))
        painter.setBrush(Qt.NoBrush)
        border_rect = panel.adjusted(0.5, 0.5, -0.5, -0.5)
        border_path = QPainterPath()
        border_path.addRoundedRect(border_rect, _MENU_RADIUS - 0.5,
                                   _MENU_RADIUS - 0.5)
        painter.drawPath(border_path)

    @staticmethod
    def _paint_shadow(painter: QPainter, panel: QRectF):
        """在 8px 透明外边距内画柔和阴影（不依赖 QGraphicsEffect）。"""
        for step in range(5, 0, -1):
            alpha = 6 + (5 - step) * 4
            rect = panel.adjusted(-step, -step + 2, step, step + 2)
            shadow_path = QPainterPath()
            shadow_path.addRoundedRect(rect, _MENU_RADIUS + step,
                                       _MENU_RADIUS + step)
            painter.fillPath(shadow_path, QColor(0, 0, 0, alpha))


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
    height:
        标题栏高度（逻辑像素），None（默认）表示使用类属性 ``HEIGHT``。
        三个标题栏按钮的高度、非客户区命中测试区域都会跟着变，
        不会出现“栏变高了、按钮碰撞箱还是旧值”的问题。
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

    系统菜单
    --------
    左键按下应用图标、右键按下标题栏（CaptionButton 区域除外）或按
    ``Alt+Space`` 会弹出 Qt 自绘的系统菜单（``SystemMenu``）：
    还原/移动/大小/最小化/最大化/关闭。``移动``/``大小`` 由
    ``WindowsFrameHelper.begin_system_menu_hint()`` 实现；关闭窗口用
    ``window.close()``。也可以手动调用 ``show_system_menu()``。
    """

    HEIGHT = _DEFAULT_TITLEBAR_HEIGHT

    #: 深/浅色主题变化时发出（跟随系统主题切换时也会发出），
    #: 方便把窗口内容区一起换色。
    themeChanged = Signal(bool)

    #: 标题栏高度变化时发出（参数为新高度，逻辑像素）。
    heightChanged = Signal(int)

    def __init__(self, window=None, title: str = "", icon: Optional[QIcon] = None,
                 *, height: Optional[int] = None, native_caption: bool = True,
                 dark: Optional[bool] = None, parent=None):
        super().__init__(parent)
        self._window = window
        # 实例高度：显式 height 参数优先，否则取类属性 HEIGHT（子类可覆盖）。
        # 必须在 _build_layout() 之前确定，按钮会按它定尺寸。
        self._height = self._resolve_height(height)
        self._native_caption = bool(native_caption)
        self._dark = system_is_dark() if dark is None else bool(dark)
        self._active = True
        self._maximized = False
        self._hover_role = None
        self._pressed_role = None
        #: 惰性创建的自绘系统菜单
        self._system_menu = None
        self._icon_close_in_progress = False

        self.setObjectName("TitleBar")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setFixedHeight(self._height)
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

    @classmethod
    def _resolve_height(cls, height: Optional[int]) -> int:
        value = cls.HEIGHT if height is None else int(height)
        if value <= 0:
            raise ValueError("标题栏高度必须为正整数")
        return value

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
            button = CaptionButton(role, self, height=self._height)
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

    def title_bar_height(self) -> int:
        """标题栏高度（逻辑像素）。"""
        return self._height

    def set_title_bar_height(self, height: int):
        """运行时修改标题栏高度（按钮与命中测试区域同步更新）。

        注意：``TitleBarMainWindow`` 会通过 ``heightChanged`` 信号自动
        调整标题栏几何和内容区边距；``TitleBarWindow`` 由布局自动处理。
        """
        height = int(height)
        if height <= 0:
            raise ValueError("标题栏高度必须为正整数")
        if height == self._height:
            return
        self._height = height
        self.setFixedHeight(height)
        for button in self._buttons.values():
            button.set_caption_height(height)
        layout = self.layout()
        if layout is not None:
            layout.activate()
        self.updateGeometry()
        self.heightChanged.emit(height)

    def set_title(self, title: str):
        self._title_label.set_full_text(title or "")

    def title(self) -> str:
        return self._title_label.full_text()

    # ---------------------------------------------------------------- 系统菜单
    def icon_rect(self) -> QRectF:
        """应用图标在标题栏本地坐标中的矩形；没有图标时返回空矩形。"""
        label = getattr(self, "_icon_label", None)
        if label is None or label.isHidden():
            return QRectF()
        top_left = label.mapTo(self, QPoint(0, 0))
        return QRectF(top_left, label.size())

    def show_system_menu(self, global_pos: Optional[QPoint] = None, *,
                         icon_press: bool = False):
        """在 ``global_pos``（屏幕逻辑坐标）弹出系统菜单。

        ``icon_press=True`` 表示由“左键按下图标”触发，此时菜单会额外识别
        “双击图标”的第二按并发出 ``iconDoubleClicked``（见 ``_on_icon_double_clicked``）。
        """
        window = self._window or self.window()
        if window is None:
            return
        if self._system_menu is not None and self._system_menu.isVisible():
            return
        if global_pos is None:
            global_pos = QCursor.pos()
        if self._system_menu is None:
            self._system_menu = SystemMenu(window, parent=window)
            self._system_menu.actionTriggered.connect(self._on_system_menu_action)
            self._system_menu.iconDoubleClicked.connect(self._on_icon_double_clicked)
        self._icon_close_in_progress = False
        self._set_hover_role(None)
        self._set_pressed_role(None)
        self._system_menu.popup_at(QPoint(global_pos), icon_press=icon_press)

    def hide_system_menu(self):
        if self._system_menu is not None:
            self._system_menu.hide()

    def system_menu_visible(self) -> bool:
        return self._system_menu is not None and self._system_menu.isVisible()

    def _on_icon_double_clicked(self):
        """菜单收到“双击图标”的第二次按下：直接关闭窗口。"""
        if self._icon_close_in_progress:
            return
        self._icon_close_in_progress = True
        window = self._window or self.window()
        if window is not None:
            QTimer.singleShot(0, window, window.close)

    def _on_system_menu_action(self, key: str):
        window = self._window or self.window()
        if window is None:
            return
        handler = getattr(window, "handle_system_menu_action", None)
        if callable(handler):
            try:
                if handler(key):
                    return
            except Exception:
                traceback.print_exc()
        # 独立使用 TitleBar（窗口没有原生 helper）时的兜底
        if key == "restore":
            window.showNormal()
        elif key == "minimize":
            window.showMinimized()
        elif key == "maximize":
            window.showMaximized()
        elif key == "close":
            window.close()
        elif key == "move":
            handle = window.windowHandle()
            if handle is not None:
                handle.startSystemMove()

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

    # ------------------------------------------- Qt 交互模式的系统菜单触发
    def mousePressEvent(self, event):
        # 原生模式下这些区域走非客户区命中测试，不会到达这里；
        # 这里保证 TitleBar 单独使用（无 helper）时菜单仍然可用。
        pos = event.position()
        if event.button() == Qt.LeftButton and self.icon_rect().contains(pos):
            self.show_system_menu(event.globalPosition().toPoint(),
                                  icon_press=True)
            event.accept()
            return
        if event.button() == Qt.RightButton and self._button_at(pos) is None:
            self.show_system_menu(event.globalPosition().toPoint())
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        if (event.button() == Qt.LeftButton
                and self.icon_rect().contains(event.position())):
            window = self._window or self.window()
            if window is not None:
                window.close()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def contextMenuEvent(self, event):
        if self._button_at(QPointF(event.pos())) is None:
            self.show_system_menu(event.globalPos())
            event.accept()
            return
        super().contextMenuEvent(event)


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
        # 原生回调里不能直接创建 Qt 弹窗：延迟 0ms 弹出系统菜单
        self._menu_open_timer = QTimer(window)
        self._menu_open_timer.setSingleShot(True)
        self._menu_open_timer.timeout.connect(self._show_pending_system_menu)
        self._pending_menu_pos = None
        self._pending_icon_press = False
        # “移动/大小”提示模式（系统菜单里选择后进入）
        self._hint_mode = None
        self._hint_edge = None
        self._hint_dragging = False
        self._hint_capture = False
        self._hint_releasing = False
        self._hint_timer = QTimer(window)
        self._hint_timer.setInterval(15)
        self._hint_timer.timeout.connect(self._tick_hint)

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

        # 移动/大小提示模式期间优先接管鼠标/光标消息
        if self._hint_mode is not None:
            handled = self._process_hint_message(msg)
            if handled is not None:
                return handled

        # Alt+Space：用自制菜单替换原生系统菜单
        if message == WM_SYSKEYDOWN and int(msg.wParam) == VK_SPACE:
            if int(msg.lParam) & (1 << 29):  # context 位：Alt 组合键
                if not int(msg.lParam) & (1 << 30):  # 忽略按住产生的重复
                    self._handle_alt_space()
                return True, 0
        if (message == WM_SYSCOMMAND
                and (int(msg.wParam) & 0xFFF0) == SC_KEYMENU
                and int(msg.lParam) == VK_SPACE):
            self._handle_alt_space()
            return True, 0

        # 右键标题栏（按钮区域除外）→ 自制菜单；同时吞掉原生菜单
        if message == WM_NCRBUTTONDOWN:
            if self._begin_caption_context_menu(hwnd, msg):
                return True, 0
            return False, 0

        if message == WM_NCRBUTTONUP:
            if self._consume_title_bar_context(hwnd, msg.lParam):
                return True, 0
            return False, 0

        if message == WM_CONTEXTMENU:
            if self._consume_title_bar_context(hwnd, msg.lParam):
                return True, 0
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
            if self._begin_caption_menu(hwnd, msg):
                return True, 0
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
            if self._begin_caption_double_click(hwnd, msg):
                return True, 0
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

    # ------------------------------------------------------------ 系统菜单触发
    def _title_bar_local(self, hwnd, lparam):
        """屏幕坐标 lParam -> 标题栏本地坐标；不在标题栏内返回 None。"""
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
            return local - QPointF(origin)
        except RuntimeError:
            return None

    def _title_bar_local_at_cursor(self):
        if self._hwnd is None:
            return None
        point = wt.POINT()
        if not _user32.GetCursorPos(ctypes.byref(point)):
            return None
        lparam = ((point.y & 0xFFFF) << 16) | (point.x & 0xFFFF)
        return self._title_bar_local(self._hwnd, lparam)

    def _open_system_menu(self, *, icon_press: bool = False, anchor=None):
        """记录锚点并用 0ms 定时器弹出菜单（避免在原生回调里造 Qt 窗口）。"""
        if not _IS_WINDOWS or self._hwnd is None:
            return
        self.cancel_system_menu_hint()
        self._pressed_hit = None
        try:
            self.title_bar.set_native_pressed(None)
            self.title_bar.set_native_hover(None)
        except RuntimeError:
            pass
        try:
            if not self.window.isActiveWindow():
                self.window.activateWindow()
        except RuntimeError:
            pass
        if anchor is None:
            anchor = QCursor.pos()
        self._pending_menu_pos = QPoint(anchor)
        self._pending_icon_press = bool(icon_press)
        self._menu_open_timer.start(0)

    def _show_pending_system_menu(self):
        pos = self._pending_menu_pos
        if pos is None:
            return
        icon_press = self._pending_icon_press
        self._pending_menu_pos = None
        self._pending_icon_press = False
        try:
            if self.title_bar.system_menu_visible():
                return
            self.title_bar.show_system_menu(pos, icon_press=icon_press)
        except RuntimeError:
            pass

    def _cancel_pending_system_menu(self):
        self._menu_open_timer.stop()
        self._pending_menu_pos = None
        self._pending_icon_press = False

    def _begin_caption_menu(self, hwnd, msg):
        """左键按下应用图标：弹出系统菜单（并阻止拖动）。"""
        if self._hint_mode is not None:
            # 移动/大小模式里自己 Post 的 WM_NCLBUTTONDOWN，不能再当菜单触发
            return False
        if int(msg.wParam) != HTCAPTION:
            return False
        local = self._title_bar_local(hwnd, msg.lParam)
        if local is None:
            return False
        icon_rect = self.title_bar.icon_rect()
        if icon_rect.isEmpty() or not icon_rect.contains(local):
            return False
        self._open_system_menu(icon_press=True)
        return True

    def _begin_caption_context_menu(self, hwnd, msg):
        """右键按下标题栏（CaptionButton 区域除外）：弹出系统菜单。"""
        if self._hint_mode is not None:
            return True  # 模式进行中：吞掉右键（等同取消前的保护）
        local = self._title_bar_local(hwnd, msg.lParam)
        if local is None:
            return False
        if self.title_bar._button_at(local) is not None:
            return True  # 按钮区域：吞掉，不弹原生菜单
        self._open_system_menu()
        return True

    def _consume_title_bar_context(self, hwnd, lparam):
        """吞掉标题栏上的 WM_NCRBUTTONUP / WM_CONTEXTMENU，防止原生菜单。"""
        if int(lparam) == -1:  # 键盘触发
            return False
        return self._title_bar_local(hwnd, lparam) is not None

    def _begin_caption_double_click(self, hwnd, msg):
        """双击应用图标：取消待弹菜单并关闭窗口。"""
        if self._hint_mode is not None:
            return False
        if int(msg.wParam) != HTCAPTION:
            return False
        local = self._title_bar_local(hwnd, msg.lParam)
        if local is None:
            return False
        icon_rect = self.title_bar.icon_rect()
        if icon_rect.isEmpty() or not icon_rect.contains(local):
            return False
        self._cancel_pending_system_menu()
        try:
            self.title_bar.hide_system_menu()
        except RuntimeError:
            pass
        _user32.PostMessageW(wt.HWND(hwnd), WM_CLOSE, 0, 0)
        return True

    def _handle_alt_space(self):
        """Alt+Space：弹出自制系统菜单，锚点 = 窗口左上角。"""
        try:
            if self.title_bar.system_menu_visible():
                self.title_bar.hide_system_menu()
                self._cancel_pending_system_menu()
                return
        except RuntimeError:
            pass
        try:
            anchor = self.window.mapToGlobal(QPoint(0, 0))
        except RuntimeError:
            anchor = QCursor.pos()
        self._open_system_menu(anchor=anchor)

    # -------------------------------------------------------- 移动/大小模式
    def begin_system_menu_hint(self, kind: str) -> bool:
        """进入“移动”或“大小”提示模式（系统菜单里选择后调用）。"""
        if not _IS_WINDOWS or self._hwnd is None:
            return False
        if kind not in ("move", "size"):
            return False
        try:
            hwnd = int(self.window.winId())
        except (RuntimeError, OSError):
            return False
        try:
            if _user32.IsZoomed(wt.HWND(hwnd)):
                return False
        except OSError:
            return False
        self.cancel_system_menu_hint()
        self._cancel_pending_system_menu()
        rect = _window_rect(hwnd)
        if rect is None:
            return False

        self._hint_mode = kind
        self._hint_edge = None
        self._hint_dragging = False
        self._hint_releasing = False

        if kind == "move":
            # 十字箭头热点在中心：让上箭头尖端正好落在窗口上边界
            cursor_h = _system_metrics_for_dpi(hwnd, SM_CYCURSOR) or 32
            target = QPoint((rect.left + rect.right) // 2,
                            rect.top + max(1, cursor_h // 2))
        else:
            target = QPoint((rect.left + rect.right) // 2,
                            (rect.top + rect.bottom) // 2)

        try:
            _user32.SetCapture(wt.HWND(hwnd))
            # SetCapture 可能因为窗口不在前台而失败，用 GetCapture 确认
            self._hint_capture = (_user32.GetCapture() or 0) == hwnd
        except OSError:
            self._hint_capture = False
        try:
            _user32.SetCursorPos(target.x(), target.y())
        except OSError:
            # 锁屏等情况下可能移动失败；模式本身仍可继续（光标提示照常）
            pass
        self._apply_hint_cursor()
        self._hint_timer.start()
        return True

    def cancel_system_menu_hint(self):
        """退出移动/大小模式并恢复光标（幂等）。"""
        self._hint_timer.stop()
        self._hint_mode = None
        self._hint_edge = None
        self._hint_dragging = False
        had_capture = self._hint_capture
        self._hint_capture = False
        if had_capture and _IS_WINDOWS:
            try:
                _user32.ReleaseCapture()
            except OSError:
                pass
        try:
            self.title_bar.unsetCursor()
            self.window.unsetCursor()
        except RuntimeError:
            pass
        handle = _system_cursor(IDC_ARROW)
        if handle:
            try:
                _user32.SetCursor(handle)
            except OSError:
                pass

    def _tick_hint(self):
        if self._hint_mode is not None:
            self._apply_hint_cursor()

    def _hint_cursor_id(self):
        if self._hint_mode == "size" and self._hint_edge:
            if self._hint_edge in ("left", "right"):
                return IDC_SIZEWE, Qt.SizeHorCursor
            return IDC_SIZENS, Qt.SizeVerCursor
        return IDC_SIZEALL, Qt.SizeAllCursor

    def _apply_hint_cursor(self):
        if self._hint_mode is None:
            return
        cursor_id, qt_cursor = self._hint_cursor_id()
        handle = _system_cursor(cursor_id)
        if handle:
            try:
                _user32.SetCursor(handle)
            except OSError:
                pass
        try:
            self.title_bar.setCursor(qt_cursor)
        except RuntimeError:
            pass

    def _edge_at_cursor(self):
        """大小模式：返回距离最近的那条边（严格单边，角落也不对角）。"""
        if self._hwnd is None:
            return None
        point = wt.POINT()
        if not _user32.GetCursorPos(ctypes.byref(point)):
            return None
        rect = _window_rect(self._hwnd)
        if rect is None:
            return None
        try:
            border_x, border_y = _resize_border_size(self._hwnd)
        except OSError:
            border_x = border_y = 8

        candidates = []
        left = abs(point.x - rect.left)
        right = abs(rect.right - point.x)
        top = abs(point.y - rect.top)
        bottom = abs(rect.bottom - point.y)
        if left <= border_x:
            candidates.append((left, 0, "left"))
        if right <= border_x:
            candidates.append((right, 0, "right"))
        if top <= border_y:
            candidates.append((top, 1, "top"))
        if bottom <= border_y:
            candidates.append((bottom, 1, "bottom"))
        if not candidates:
            return None
        candidates.sort(key=lambda candidate: (candidate[0], candidate[1]))
        return candidates[0][2]

    def _start_native_drag(self, hit_code):
        """交给 DefWindowProc 的原生拖动/缩放循环（保留 Snap/动画）。"""
        hwnd = self._hwnd
        if hwnd is None:
            return
        self._hint_dragging = True
        self._hint_releasing = True
        try:
            if self._hint_capture:
                self._hint_capture = False
                _user32.ReleaseCapture()
        except OSError:
            pass
        finally:
            self._hint_releasing = False
        point = wt.POINT()
        if not _user32.GetCursorPos(ctypes.byref(point)):
            self.cancel_system_menu_hint()
            return
        lparam = ((point.y & 0xFFFF) << 16) | (point.x & 0xFFFF)
        _user32.PostMessageW(wt.HWND(hwnd), WM_NCLBUTTONDOWN, hit_code, lparam)

    def _process_hint_message(self, msg):
        """移动/大小模式期间优先处理消息；返回 None 表示继续走原逻辑。"""
        if self._hint_mode is None:
            return None
        message = msg.message
        if message == WM_SETCURSOR:
            self._apply_hint_cursor()
            return True, 1
        if message == WM_MOUSEMOVE:
            if self._hint_mode == "size":
                self._hint_edge = self._edge_at_cursor()
            self._apply_hint_cursor()
            return False, 0
        if message == WM_LBUTTONDOWN:
            if self._hint_mode == "move":
                if self._title_bar_local_at_cursor() is not None:
                    self._start_native_drag(HTCAPTION)
                else:
                    self.cancel_system_menu_hint()
                return True, 0
            edge = self._edge_at_cursor()
            self._hint_edge = edge
            hit_code = {"left": HTLEFT, "right": HTRIGHT,
                        "top": HTTOP, "bottom": HTBOTTOM}.get(edge)
            if hit_code is None:
                self.cancel_system_menu_hint()
            else:
                self._start_native_drag(hit_code)
            return True, 0
        if message == WM_RBUTTONDOWN:
            self.cancel_system_menu_hint()
            return True, 0
        if message in (WM_LBUTTONUP, WM_NCLBUTTONUP):
            QTimer.singleShot(0, self.window, self.cancel_system_menu_hint)
            return False, 0
        if message == WM_CAPTURECHANGED:
            if self._hint_releasing or self._hint_dragging:
                return False, 0
            self.cancel_system_menu_hint()
            return False, 0
        if message == WM_CANCELMODE:
            self.cancel_system_menu_hint()
            return False, 0
        if message == WM_KEYDOWN and int(msg.wParam) == VK_ESCAPE:
            self.cancel_system_menu_hint()
            return True, 0
        return None

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
        local = self._title_bar_local(hwnd, lparam)
        if local is None:
            return None
        return self.title_bar.hit_test(local)

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

    def handle_system_menu_action(self, key: str) -> bool:
        """系统菜单动作路由：move/size 交给原生 helper，其余走 Qt 窗口方法。"""
        if key in ("move", "size"):
            helper = getattr(self, "_frame_helper", None)
            if helper is not None:
                return helper.begin_system_menu_hint(key)
            return False
        if key == "restore":
            self.showNormal()
        elif key == "minimize":
            self.showMinimized()
        elif key == "maximize":
            self.showMaximized()
        elif key == "close":
            self.close()
        else:
            return False
        return True

    def hideEvent(self, event):
        # 窗口隐藏/最小化/关闭时清理移动/大小模式（避免光标卡在十字箭头）
        helper = getattr(self, "_frame_helper", None)
        if helper is not None:
            try:
                helper.cancel_system_menu_hint()
                helper._cancel_pending_system_menu()
            except Exception:
                traceback.print_exc()
        title_bar = getattr(self, "_title_bar", None)
        if title_bar is not None:
            try:
                title_bar.hide_system_menu()
            except RuntimeError:
                pass
        super().hideEvent(event)


class TitleBarWindow(_WindowsFrameMixin, QWidget):
    """自带 Windows 11 风格标题栏的顶层窗口（QWidget 版）。

    内容放进 ``self.body``（它自带一个空的 QVBoxLayout，直接用即可）::

        class MyWindow(TitleBarWindow):
            def __init__(self):
                super().__init__(title="我的应用", height=40)
                self.body_layout.addWidget(QTextEdit())

    标题栏高度用 ``height=`` 指定（逻辑像素，默认取 ``HEIGHT``），运行时想改就调用
    ``set_title_bar_height()``；布局会自动重排，不需要手动设置固定尺寸。

    原生效果：窗口阴影、圆角、最小化/最大化动画、Aero Snap、Win+方向键、
    双击标题栏最大化、Qt 自绘系统菜单（左键图标 / 右键标题栏 / Alt+Space）、
    Windows 11 贴靠布局悬浮面板。双击应用图标可直接关闭窗口。
    """

    def __init__(self, title: str = "", icon: Optional[QIcon] = None,
                 parent=None, *, height: Optional[int] = None,
                 native_caption: bool = True,
                 dark: Optional[bool] = None, auto_theme: bool = True,
                 rounded: bool = True):
        # 非 Windows 平台没有原生无边框拖动逻辑，保留系统边框以免窗口不可操作
        flags = Qt.Window
        if _IS_WINDOWS:
            flags |= Qt.FramelessWindowHint
        super().__init__(parent, flags)

        self._build_title_bar(title, icon, native_caption, dark, height)
        self._frame_helper = WindowsFrameHelper(
            self, self._title_bar, native_caption=native_caption,
            dark=dark, rounded=rounded, auto_theme=auto_theme)
        self._frame_helper.install()

    # ------------------------------------------------------------------ 构建
    def _build_title_bar(self, title, icon, native_caption, dark, height=None):
        self._title_bar = TitleBar(self, title=title, icon=icon, height=height,
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

    def set_title_bar_height(self, height: int):
        """修改标题栏高度；布局会自动重排并同步按钮命中区域。"""
        self._title_bar.set_title_bar_height(height)

    def title_bar_height(self) -> int:
        return self._title_bar.title_bar_height()

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
    使用（菜单栏会显示在标题栏下方）。标题栏高度用 ``height=`` 指定
    （逻辑像素，默认取 ``HEIGHT``），之后也可以通过 ``set_title_bar_height()`` 修改，
    标题栏几何与内容区边距会一起同步。
    """

    def __init__(self, title: str = "", icon: Optional[QIcon] = None,
                 parent=None, *, height: Optional[int] = None,
                 native_caption: bool = True,
                 dark: Optional[bool] = None, auto_theme: bool = True,
                 rounded: bool = True):
        flags = Qt.Window
        if _IS_WINDOWS:
            flags |= Qt.FramelessWindowHint
        super().__init__(parent, flags)

        self._title_bar = TitleBar(self, title=title, icon=icon, height=height,
                                   native_caption=native_caption, dark=dark,
                                   parent=self)
        bar_height = self._title_bar.title_bar_height()
        self._title_bar.setGeometry(0, 0, self.width(), bar_height)
        self._title_bar.raise_()
        self.setContentsMargins(0, bar_height, 0, 0)
        self._title_bar.heightChanged.connect(self._on_title_bar_height_changed)
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

    def _on_title_bar_height_changed(self, height: int):
        """标题栏高度变化：重新确定标题栏几何，并为内容区留出同样高度。"""
        title_bar = getattr(self, "_title_bar", None)
        if title_bar is None or title_bar.isHidden():
            return
        title_bar.setGeometry(0, 0, self.width(), height)
        title_bar.raise_()
        self.setContentsMargins(0, height, 0, 0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        title_bar = getattr(self, "_title_bar", None)
        if title_bar is not None:
            title_bar.setGeometry(0, 0, self.width(),
                                  title_bar.title_bar_height())
            title_bar.raise_()

    @property
    def title_bar(self) -> TitleBar:
        return self._title_bar

    def set_title_bar_height(self, height: int):
        """修改标题栏高度；标题栏几何与内容区边距会一起同步。"""
        self._title_bar.set_title_bar_height(height)

    def title_bar_height(self) -> int:
        return self._title_bar.title_bar_height()

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
            "· 左键图标 / 右键标题栏 / Alt+Space 弹出系统菜单\n"
            "· 双击应用图标可直接关闭窗口\n"
            "· Aero Snap / Win+方向键贴靠\n"
            "· 鼠标悬停最大化按钮出现 Windows 11 贴靠布局\n"
            "· 标题栏高度可配置（height=…，按钮命中区域同步）")
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
            "阴影、圆角、最小化/最大化动画、任务栏预览与 Aero Snap。\n\n"
            "标题栏高度在构造时用 height=40 指定；运行时调用\n"
            "set_title_bar_height() 也会同步按钮尺寸与命中测试区域。\n\n"
            "系统菜单由 Qt 自绘（圆角/阴影/渐显），支持还原、移动、大小、\n"
            "最小化、最大化、关闭；移动/大小会进入对应的光标提示模式。")
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
        self._height_btn = QPushButton(f"标题栏高度：{self.title_bar_height()}")
        self._height_btn.clicked.connect(self._cycle_title_bar_height)
        for button in (minimize_btn, maximize_btn, close_btn, self._theme_btn,
                       self._height_btn):
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

    #: 演示里循环切换的标题栏高度（逻辑像素）
    _DEMO_HEIGHTS = (32, 40, 48, 56)

    def _cycle_title_bar_height(self):
        """演示运行时改高度：按钮/命中区域会一起变。"""
        heights = self._DEMO_HEIGHTS
        try:
            index = heights.index(self.title_bar_height())
        except ValueError:
            index = 0
        height = heights[(index + 1) % len(heights)]
        self.set_title_bar_height(height)
        if hasattr(self, "_height_btn"):
            self._height_btn.setText(f"标题栏高度：{height}")

    def _update_status(self):
        state = "最大化" if self.isMaximized() else "窗口化"
        self._status.setText(
            f"窗口状态：{state}　标题栏高度：{self.title_bar_height()}　"
            "（拖动标题栏 / 双击标题栏试试）")

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
