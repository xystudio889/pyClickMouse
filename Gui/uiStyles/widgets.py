from uiStyles.QUI import *
import ctypes # 用于获取系统风格
from sharelibs import get_lang, default_button_text, set_style
from typing import Optional, Union
from dataclasses import dataclass
import math
from .levels import level_component
from enum import IntEnum

__all__ = ['UMessageBox', 'VScrollArea', 'HScrollArea', 'UCheckBox', 'UnitInputLayout', 'ULabel', 'MessageButton', 'CustonMessageButton', 'MessageIcon', 'HighLightPanel', 'fonticon', 'icon_img', 'IconImage', 'TextLabel', 'Card', 'ContentCard', 'PressableRow', 'Expander', 'create_expander_row', 'ToggleSwitch', 'DevFlagCard']

# 定义消息框图标对应的声音常量
MB_ICONHAND = 0x00000010      # 错误（手形）
MB_ICONEXCLAMATION = 0x00000030  # 警告
MB_ICONASTERISK = 0x00000040     # 信息

class MessageButton:
    NOBUTTON = 0b0
    YES = 0b1
    NO = 0b10
    OK = 0b100
    CANCEL = 0b1000
    YESNO = YES | NO
    OKCANCEL = OK | CANCEL

    class ReturnValue:
        YES = 1
        NO = 2
        OK = 3
        CANCEL = 4

class MessageIcon:
    INFO = 0b1
    WARNING = 0b10
    CRITICAL = 0b100
    QUESTION = 0b1000

class CustonMessageButton:
    def __init__(self, text, role):
        self.text = text
        self.role = role

class UMessageBox(QDialog):
    def __init__(self, parent: QWidget | None, title: str, text: str, icon: MessageIcon, buttons: MessageButton, defaultButton: MessageButton):
        super().__init__(parent)

        self.setWindowTitle(title)

        self.text = text
        match icon:
            case MessageIcon.INFO:
                self.icon = QStyle.SP_MessageBoxInformation
            case MessageIcon.WARNING:
                self.icon = QStyle.SP_MessageBoxWarning
            case MessageIcon.CRITICAL:
                self.icon = QStyle.SP_MessageBoxCritical
            case MessageIcon.QUESTION:
                self.icon = QStyle.SP_MessageBoxQuestion
            case _:
                raise ValueError('Invalid icon value')

        self.buttons = {}
        self.defaultButton = None

        self.btn_id = 5 # 前四个为默认按钮id，后面为自定义按钮id

        if isinstance(buttons, int):
            if buttons & MessageButton.YES:
                btn = QPushButton(get_lang('01', source=default_button_text))
                msg_id = 1

                self.buttons[msg_id] = btn
                if defaultButton == MessageButton.YES:
                    self.defaultButton = btn
            if buttons & MessageButton.NO:
                btn = QPushButton(get_lang('02', source=default_button_text))
                msg_id = 2
                self.buttons[msg_id] = btn

                if defaultButton == MessageButton.NO:
                    self.defaultButton = btn
            if buttons & MessageButton.OK:
                btn = QPushButton(get_lang('03', source=default_button_text))
                msg_id = 3
                self.buttons[msg_id] = btn

                if defaultButton == MessageButton.OK:
                    self.defaultButton = btn
            if buttons & MessageButton.CANCEL:
                btn = QPushButton(get_lang('04', source=default_button_text))
                msg_id = 4
                self.buttons[msg_id] = btn

                if defaultButton == MessageButton.CANCEL:
                    self.defaultButton = btn
        if isinstance(buttons, CustonMessageButton):
            btn = QPushButton(buttons.text)
            msg_id = self.btn_id
            self.btn_id += 1
            self.buttons[msg_id] = btn

            if defaultButton == btn:
                self.defaultButton = btn
        if isinstance(buttons, list):
            for button in buttons:
                if isinstance(button, CustonMessageButton):
                    btn = QPushButton(button.text, button.role)
                    msg_id = self.btn_id
                    self.buttons[msg_id] = btn
                    if defaultButton == button:
                        self.defaultButton = btn
                else:
                    raise ValueError('buttons must be a list of CustonMessageButton')

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        content_layout = QHBoxLayout()
        icon = QLabel()
        show_icon = icon.style().standardIcon(self.icon)
        icon.setPixmap(show_icon.pixmap(32, 32))

        # 将 label 保存为实例属性，以便后续设置最大宽度
        label = QLabel(self.text)
        label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        label.setWordWrap(True) # 文本换行
        label.setMaximumWidth(500)

        content_layout.addWidget(icon, 0)
        content_layout.addWidget(label, 1)

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        buttons_layout.setContentsMargins(0, 8, 0, 0)
        for k, button in self.buttons.items():
            button.clicked.connect(lambda b, key=k: self.done(key)) # 为按钮添加点击事件
            buttons_layout.addWidget(button)
            if button == self.defaultButton:
                button.setDefault(True)

        layout.addLayout(content_layout)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    def showEvent(self, event):
        match self.icon:
            case QStyle.SP_MessageBoxInformation:
                sound = MB_ICONASTERISK
            case QStyle.SP_MessageBoxWarning:
                sound = MB_ICONEXCLAMATION
            case QStyle.SP_MessageBoxCritical:
                sound = MB_ICONHAND
            case _:
                sound = None

        if sound is not None:
            ctypes.windll.user32.MessageBeep(sound)
        return super().showEvent(event)
    
    @classmethod
    def information(cls, parent: QWidget | None, title: str, text: str, buttons: MessageButton = None, defaultButton: MessageButton = None):
        buttons = MessageButton.OK if buttons is None else buttons
        defaultButton = MessageButton.OK if buttons is None else defaultButton
        return cls(parent, title, text, MessageIcon.INFO, buttons, defaultButton).exec()
    
    @classmethod
    def warning(cls, parent: QWidget | None, title: str, text: str, buttons: MessageButton = None, defaultButton: MessageButton = None):
        buttons = MessageButton.OK if buttons is None else buttons
        defaultButton = MessageButton.OK if buttons is None else defaultButton
        return cls(parent, title, text, MessageIcon.WARNING, buttons, defaultButton).exec()

    @classmethod
    def critical(cls, parent: QWidget | None, title: str, text: str, buttons: MessageButton = None, defaultButton: MessageButton = None):
        buttons = MessageButton.OK if buttons is None else buttons
        defaultButton = MessageButton.OK if buttons is None else defaultButton
        return cls(parent, title, text, MessageIcon.CRITICAL, buttons, defaultButton).exec()

    @classmethod
    def question(cls, parent: QWidget | None, title: str, text: str, buttons: MessageButton = None, defaultButton: MessageButton = None):
        buttons = MessageButton.YESNO if buttons is None else buttons
        defaultButton = MessageButton.YESNO if buttons is None else defaultButton
        return cls(parent, title, text, MessageIcon.QUESTION, buttons, defaultButton).exec()

class VScrollArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 隐藏横向滚动条
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 始终禁用水平滚动条
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)     # 按需显示垂直滚动条

class HScrollArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 隐藏纵向滚动条
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
class UCheckBox(QWidget):
    stateChanged = Signal(Qt.CheckState)
    checkStateChanged = Signal(bool)

    def __init__(self, text='', parent=None):
        super().__init__(parent)
        
        self.checkbox = QCheckBox()
        self.checkbox.stateChanged.connect(lambda: self.stateChanged.emit(self.checkbox.checkState()))
        self.checkbox.checkStateChanged.connect(lambda: self.checkStateChanged.emit(self.checkbox.isChecked()))
        self.label = QLabel(text)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.checkbox)
        layout.addWidget(self.label)
        layout.addStretch()
    
    def setChecked(self, checked):
        return self.checkbox.setChecked(checked)
    
    def setTristate(self, tristate):
        return self.checkbox.setTristate(tristate)
    
    def setCheckState(self, state):
        return self.checkbox.setCheckState(state)

    def isChecked(self):
        return self.checkbox.isChecked()
    
class UnitInputLayout(QLayout):
    '''单位输入行布局：文本与下拉框使用真实尺寸，输入框拉伸填充空白，整行占满可用宽度'''
    def __init__(self, parent=None):
        super().__init__(parent)
        self._item_list = []         # 存储所有子项
        self._row_breaks = []        # 记录每行结束的索引位置（记录上一行最后一个项的索引）
        self._stretch_widgets = []   # 需要在行内拉伸填充剩余空间的控件
        self.setContentsMargins(0, 0, 0, 0)

    def addItem(self, item: QLayoutItem):
        '''添加子项到列表末尾'''
        self._item_list.append(item)

    def addWidget(self, widget: QWidget, stretch: int = 0):
        '''
        添加控件
        
        Args:
            widget: 要添加的控件
            stretch: 大于 0 时该控件会拉伸填充行内的剩余空间
        '''
        super().addWidget(widget)
        if stretch > 0:
            self._stretch_widgets.append(widget)

    def _is_stretch_item(self, item: QLayoutItem) -> bool:
        '''判断子项是否为需要拉伸填充剩余空间的控件'''
        widget = item.widget()
        return widget is not None and any(widget is w for w in self._stretch_widgets)

    def newRow(self):
        '''标记换行位置'''
        if self._item_list:  # 只有在有子项时才记录换行
            # 记录当前最后一个项的索引（从0开始）
            last_index = len(self._item_list) - 1
            # 如果还没有记录换行，或者当前最后一个项不在最近记录的换行中
            if not self._row_breaks or last_index > self._row_breaks[-1]:
                self._row_breaks.append(last_index)

    def count(self):
        '''返回子项数量'''
        return len(self._item_list)

    def itemAt(self, index):
        '''获取指定索引的子项'''
        if 0 <= index < len(self._item_list):
            return self._item_list[index]
        return None

    def takeAt(self, index):
        '''移除并返回指定索引的子项'''
        if 0 <= index < len(self._item_list):
            item = self._item_list.pop(index)

            # 不再追踪被移除子项的拉伸设置
            widget = item.widget()
            if widget is not None:
                self._stretch_widgets = [w for w in self._stretch_widgets if w is not widget]
            
            # 移除后需要更新换行标记
            for i in range(len(self._row_breaks)):
                if self._row_breaks[i] >= index:
                    self._row_breaks[i] -= 1
            
            # 移除已经无效的换行标记（如果换行标记指向的索引已经不存在）
            self._row_breaks = [r for r in self._row_breaks if r < len(self._item_list)]
            
            return item
        return None

    def sizeHint(self):
        '''返回布局的首选大小'''
        if not self._item_list:
            return QSize(0, 0)
        
        # 计算行数和每行的尺寸
        rows = self._get_rows()
        
        # 计算总宽度（取最宽的行）
        max_width = 0
        for row_items in rows:
            row_width = sum(item.sizeHint().width() for item in row_items)
            if row_items:  # 加上行内间距
                row_width += self.spacing() * (len(row_items) - 1)
            max_width = max(max_width, row_width)
        
        # 计算总高度（每行高度之和 + 行间距）
        total_height = 0
        for i, row_items in enumerate(rows):
            if row_items:
                row_height = max(item.sizeHint().height() for item in row_items)
                total_height += row_height
                if i < len(rows) - 1:  # 不是最后一行，添加行间距
                    total_height += self.spacing()
        
        # 加上边距
        margins = self.contentsMargins()
        return QSize(
            max_width + margins.left() + margins.right(),
            total_height + margins.top() + margins.bottom()
        )

    def _get_rows(self):
        '''将子项按行分组'''
        if not self._item_list:
            return []
        
        rows = []
        start_idx = 0
        
        # 根据换行标记分割行
        for break_idx in self._row_breaks:
            if break_idx < len(self._item_list):
                rows.append(self._item_list[start_idx:break_idx + 1])
                start_idx = break_idx + 1
        
        # 添加最后一行（如果有剩余项）
        if start_idx < len(self._item_list):
            rows.append(self._item_list[start_idx:])
        
        # 如果没有任何换行标记，所有项都在一行
        if not self._row_breaks and self._item_list:
            rows.append(self._item_list)
        
        return rows

    def setGeometry(self, rect: QRect):
        '''核心方法，按行排列所有子项：固定尺寸子项保持真实尺寸，可拉伸子项填充剩余空间'''
        super().setGeometry(rect)
        
        if not self._item_list:
            return
        
        # 获取可用区域（排除边距）
        margins = self.contentsMargins()
        available_rect = rect.adjusted(
            margins.left(),
            margins.top(),
            -margins.right(),
            -margins.bottom()
        )
        
        spacing = self.spacing()
        y = available_rect.y()
        
        # 遍历每一行
        for row_items in self._get_rows():
            if not row_items:
                continue
            
            # 计算当前行的最大高度
            row_height = max(item.sizeHint().height() for item in row_items)
            
            stretch_flags = [self._is_stretch_item(item) for item in row_items]
            stretch_count = sum(stretch_flags)
            
            # 固定尺寸子项占用真实尺寸，剩余空间由可拉伸子项均分
            fixed_width = sum(item.sizeHint().width() for item, is_stretch in zip(row_items, stretch_flags) if not is_stretch)
            remaining_width = max(0, available_rect.width() - fixed_width - spacing * (len(row_items) - 1))
            stretch_sizes = []
            if stretch_count:
                base_size, extra = divmod(remaining_width, stretch_count)
                # 多余的像素分给前面的拉伸项，保证整行占满可用宽度
                stretch_sizes = [base_size + 1] * extra + [base_size] * (stretch_count - extra)
            
            row_x = available_rect.x()
            for item, is_stretch in zip(row_items, stretch_flags):
                if is_stretch:
                    item_width = stretch_sizes.pop(0)
                else:
                    item_width = item.sizeHint().width()
                item_height = item.sizeHint().height()
                # 垂直居中
                item_y = y + (row_height - item_height) // 2
                item.setGeometry(QRect(row_x, item_y, item_width, item_height))
                row_x += item_width + spacing
            
            # 换行：更新y坐标，重置x坐标
            y += row_height + spacing

    def addUnitRow(self, text: str, input: QLineEdit, unit: QComboBox):
        '''添加单位选择控件：文本与下拉框使用真实尺寸，输入框拉伸填充空白'''
        self.newRow() # 换行
        self.addWidget(QLabel(text + ': '))
        self.addWidget(input, stretch=1)
        self.addWidget(unit)

class ULabel(QLabel):
    '''自定义 QLabel，在 setText 时发送信号'''
    textChanged = Signal()  # 定义信号，参数是新的文本
    
    def __init__(self, text='', parent=None):
        super().__init__(text, parent)
        
    def setText(self, text: str):
        '''重写 setText 方法'''
        if self.text() != text:  # 只有在文本确实变化时发射信号
            super().setText(text)
            self.textChanged.emit()  # 发射信号

@level_component(contribution=1)
class HighLightPanel(QWidget):
    """背景 #272727，左上角 8px 圆角，内容四周 36px 留白

    配色：底色默认值见 BG，可由 qss 里的 `.HighLightPanel { qproperty-bg_color: ... }` 覆盖
          （临时配色表见 Gui/res/styles/dark.qss）；圆角、留白等形状属性仍由代码控制。
    """

    BG = QColor("#272727")     # 默认底色（qss 未加载时的兜底值）
    RADIUS = 8
    PADDING = 36

    STYLE_CLASS = "HighLightPanel"

    def __init__(self, parent=None):
        super().__init__(parent)
        self._bg_color = QColor(self.BG)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(
            self.PADDING, self.PADDING - 6, self.PADDING, self.PADDING - 3
        )
        self._layout.setSpacing(0)
        set_style(self, self.STYLE_CLASS)

    def setContent(self, widget: QWidget):
        """把业务内容 widget 放进卡片里"""
        self._layout.addWidget(widget)

    # --------------------------- 配色 ---------------------------
    def get_bg_color(self) -> QColor:
        return self._bg_color

    def set_bg_color(self, color):
        color = QColor(color)
        if color != self._bg_color:
            self._bg_color = color
            self.update()

    bg_color = Property(QColor, get_bg_color, set_bg_color)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        r = self.RADIUS
        rect = QRectF(self.rect())

        path = QPainterPath()
        # 只有左上角是圆角，其余三个角是直角
        path.moveTo(rect.left() + r, rect.top())
        path.lineTo(rect.right(), rect.top())
        path.lineTo(rect.right(), rect.bottom())
        path.lineTo(rect.left(), rect.bottom())
        path.lineTo(rect.left(), rect.top() + r)
        path.quadTo(rect.left(), rect.top(), rect.left() + r, rect.top())
        path.closeSubpath()

        painter.fillPath(path, self._bg_color)

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
        icon = FontIcon("\uE799", size=24)                    # 颜色交给 qss 的 .FontIcon
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


def fonticon(icon="", size: int = 20, color: Optional[str] = None) -> FontIcon:
    """新建一个 fonticon 处理后的 QLabel（图标字体 + 居中 + 透明背景）。

    color 为 None（默认）时颜色由 qss 决定；只有确实需要单独配色时才显式传入。

    示例：
        icon = fonticon("\uE799", size=20)                    # 颜色交给 qss
        icon = fonticon("\uE70D", size=12, color="#F7F7F7")   # 单独配色
    """
    return FontIcon(icon, size=size, color=color)


class IconImage(QLabel):
    """内嵌图片图标（QLabel + QPixmap）。

    与 FontIcon（图标字体）不同，它不依赖图标字体，图片直接内嵌在控件里，
    因此完全不受全局 `* { font-size / font-family }` 之类规则影响。

    参数：
        image —— QPixmap / QIcon / 图片文件路径；None 表示暂无图片
        size  —— 目标尺寸：int（正方形）或 QSize；None 表示按原图尺寸

    示例：
        logo = IconImage("logo.png", size=48)                  # 文件路径 + 48×48
        logo = IconImage(QPixmap(48, 48), size=QSize(48, 48))  # QPixmap + 指定尺寸
        logo.set_angle(90)                                     # 原地旋转（可做动画）
    """

    def __init__(self, image=None, size=None, parent=None):
        super().__init__(parent)

        self._source = QPixmap()      # 原图
        self._icon_size = QSize()     # 空 QSize 表示按原图
        self._angle = 0.0

        self.setAlignment(Qt.AlignCenter)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        self.setMinimumWidth(0)

        if size is not None:
            self.set_icon_size(size)
        if image is not None:
            self.set_image(image)

    # --------------------------- 图片 ---------------------------
    def set_image(self, image):
        """设置图片：QPixmap / QIcon / 文件路径。"""
        if isinstance(image, QPixmap):
            pixmap = image
        elif isinstance(image, QIcon):
            size = self._icon_size if not self._icon_size.isEmpty() else QSize(64, 64)
            pixmap = image.pixmap(size)
        elif isinstance(image, str):
            pixmap = QPixmap(image)
        elif image is None:
            pixmap = QPixmap()
        else:
            raise TypeError("image 必须是 QPixmap / QIcon / 文件路径")

        self._source = pixmap
        self._refresh()

    def image(self) -> QPixmap:
        return self._source

    def has_image(self) -> bool:
        return not self._source.isNull()

    def _refresh(self):
        """按目标尺寸等比缩放后显示（保持宽高比）。"""
        if self._source.isNull():
            self.clear()
        else:
            if self._icon_size.isEmpty():
                shown = self._source
            else:
                shown = self._source.scaled(self._icon_size, Qt.KeepAspectRatio,
                                            Qt.SmoothTransformation)
            super().setPixmap(shown)
            self.setFixedSize(shown.size())
        self.updateGeometry()

    # --------------------------- 尺寸 ---------------------------
    def get_icon_size(self) -> QSize:
        return self._icon_size

    def set_icon_size(self, size):
        size = QSize(size, size) if isinstance(size, int) else QSize(size)
        if size != self._icon_size:
            self._icon_size = size
            self._refresh()

    icon_size = Property(QSize, get_icon_size, set_icon_size)

    # --------------------------- 原地旋转（与 FontIcon 一致，可交给动画） ---------------------------
    def get_angle(self) -> float:
        return self._angle

    def set_angle(self, angle: float):
        angle = float(angle)
        if angle != self._angle:
            self._angle = angle
            self.update()

    angle = Property(float, get_angle, set_angle)

    def paintEvent(self, event):
        # 未旋转时走 QLabel 默认绘制
        if self._angle % 360.0 == 0.0 or self.pixmap() is None:
            super().paintEvent(event)
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        rect = QRectF(self.rect())
        painter.translate(rect.center())
        painter.rotate(self._angle)
        painter.translate(-rect.center())
        painter.drawPixmap(rect, self.pixmap(), QRectF(self.pixmap().rect()))


def icon_img(image=None, size=None) -> IconImage:
    """新建一个内嵌图片图标（QLabel + QPixmap，不受全局字体规则影响）。

    示例：
        icon = icon_img("logo.png", size=48)
        icon = icon_img(QPixmap("logo.png"))     # size=None：按原图尺寸
    """
    return IconImage(image, size=size)


def _has_visual_content(label) -> bool:
    """判断图标 / 文字标签是否有内容：有文字或有图片都算。"""
    if label is None:
        return False
    pixmap = label.pixmap() if isinstance(label, QLabel) else None
    if pixmap is not None and not pixmap.isNull():
        return True
    return not _is_empty(label.text())


# ----------------------------- 通用小工具 -----------------------------
def _normalize_text(text) -> str:
    return "" if text is None else str(text)


def _is_empty(text) -> bool:
    """None、空字符串（含仅空白）都算无内容。"""
    return text is None or not str(text).strip()


def _prep_text_label(label: QLabel):
    label.setWordWrap(True)
    label.setMinimumWidth(0)
    label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)


def _hfw_policy(horizontal, vertical) -> QSizePolicy:
    """带 heightForWidth 的尺寸策略。

    自动换行的文字，其高度取决于宽度；只有打开 heightForWidth，
    父布局才能拿到正确高度，否则会按「一行」的最小高度把文字压扁。
    """
    policy = QSizePolicy(horizontal, vertical)
    policy.setHeightForWidth(True)
    return policy


class _HFWContainer(QWidget):
    """把内部布局的 heightForWidth / sizeHint 透传给父布局的容器。

    普通 QWidget 不会把布局的 heightForWidth 暴露出去，父布局于是会
    算出错误高度（要么大得离谱，要么把换行文字压成一行）。
    """

    def heightForWidth(self, width: int) -> int:
        lay = self.layout()
        if lay is not None and lay.hasHeightForWidth():
            return lay.heightForWidth(width)
        return super().heightForWidth(width)

    def sizeHint(self) -> QSize:
        lay = self.layout()
        if lay is not None and lay.hasHeightForWidth() and self.width() > 0:
            return QSize(max(1, lay.sizeHint().width()), max(1, lay.heightForWidth(self.width())))
        return super().sizeHint()


def _as_icon_label(title) -> Optional[QLabel]:
    """把 title 参数（QLabel / QPixmap / QIcon / 图标字符 / None）统一成 QLabel。

    - QLabel：原样使用（例如内嵌图片的 iconImg）
    - QPixmap / QIcon：包成内嵌图片图标 IconImage
    - 其它：按图标字符生成 fonticon
    """
    if title is None or isinstance(title, QLabel):
        return title
    if isinstance(title, (QPixmap, QIcon)):
        return icon_img(title)
    return fonticon(str(title))


class TextLabel(QLabel):
    """带 text_color / text_size 属性的文字标签。

    颜色与字号都写进控件自身样式表，优先级高于全局样式表里的
    `* { color: ...; font-size: ... }`（这类全局规则会覆盖 setFont() 的效果）；
    并可由 qss 里的 `qproperty-text_color` / `qproperty-text_size` 覆盖（见 Gui/res/styles/dark.qss）。

    示例：
        title = TextLabel("副标题", color="#FFFFFF", size=14)
        desc = TextLabel("描述", color="#D1D1D1", size=12)
        desc.set_text_color("#FFB020")     # 也可由 qss 用 qproperty-text_color 覆盖
    """

    def __init__(self, text: str = "", color: str = "#FFFFFF", size: int = 14, parent=None):
        super().__init__(_normalize_text(text), parent)
        self._text_color = QColor(color)
        self._text_size = int(size)
        self._apply_style()

    def _apply_style(self):
        f = self.font()
        f.setPixelSize(self._text_size)
        self.setFont(f)
        # 不在这里写 background：背景交给样式表按层级（level）决定
        self.setStyleSheet(
            f"color: {self._text_color.name()}; "
            f"font-size: {self._text_size}px;"
        )

    def get_text_color(self) -> QColor:
        return self._text_color

    def set_text_color(self, color):
        color = QColor(color)
        if color != self._text_color:
            self._text_color = color
            self._apply_style()

    def get_text_size(self) -> int:
        return self._text_size

    def set_text_size(self, size: int):
        size = int(size)
        if size != self._text_size:
            self._text_size = size
            self._apply_style()

    text_color = Property(QColor, get_text_color, set_text_color)
    text_size = Property(int, get_text_size, set_text_size)


@level_component(contribution=1)
class Card(QWidget):
    """基础卡片：只负责背景、圆角与边框，并挂载一个外部布局。

    组件层级：Card 通过 ``@level_component(contribution=1)`` 为所有子控件
    增加 1 级；Card 自己的层级不包含这个 +1（例如挂在主窗口下时 raw=0）。
    ContentCard / Expander / PressableRow 都继承 Card，因此自动具备同样
    的层级贡献，无需重复声明。

    参数：
        layout —— 要挂载到卡片上的布局（None 则只是一块背景板）。
                  布局的边距 / 间距完全由调用方决定，Card 不做干预。

    配色：底色 / 边框色的默认值见 _BG、_BORDER，可由 qss 里的
          `.Card { qproperty-bg_color: ...; qproperty-border_color: ...; }` 覆盖
          （临时配色表见 Gui/res/styles/dark.qss）；圆角、边框宽度等形状属性仍由代码控制。

    示例：
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.addWidget(TextLabel("卡片内容"))
        card = Card(layout=layout)
    """

    STYLE_CLASS = "Card"

    _BG = "#323232"        # 默认底色（qss 未加载时的兜底值）
    _BORDER = "#232323"    # 默认边框色
    _RADIUS = 4            # 圆角（形状，不由 qss 控制）
    _BORDER_WIDTH = 1      # 边框宽度（形状，不由 qss 控制）

    def __init__(self, layout=None, parent=None):
        super().__init__(parent)

        # ---- 形状参数 ----
        self._radius = self._RADIUS
        self._border_width = self._BORDER_WIDTH

        # ---- 配色（默认值，可被 qss 覆盖）----
        self._bg_color = QColor(self._BG)
        self._border_color = QColor(self._BORDER)

        self.setSizePolicy(_hfw_policy(QSizePolicy.Expanding, QSizePolicy.Preferred))

        if layout is not None:
            self.mount_layout(layout)

        set_style(self, self.STYLE_CLASS)

    # --------------------------- 高度随宽度变化（换行文字） ---------------------------
    def heightForWidth(self, width: int) -> int:
        """返回布局在给定宽度下所需的高度（供父布局使用）。"""
        lay = self.layout()
        if lay is not None and lay.hasHeightForWidth():
            return lay.heightForWidth(width)
        return super().heightForWidth(width)

    def sizeHint(self) -> QSize:
        """宽度已知时按换行后的高度给建议尺寸（否则 Qt 会算出巨大且错误的高度）。"""
        lay = self.layout()
        if lay is not None and lay.hasHeightForWidth():
            width = self.width()
            if width > 0:
                return QSize(max(1, lay.sizeHint().width()), max(1, lay.heightForWidth(width)))
        return super().sizeHint()

    def _sync_content_height(self):
        """把自身最小高度锁到「当前宽度下换行后的自然高度」。

        换行文字的高度取决于宽度，而父布局只会在尺寸变化时重新询问一次，
        因此这里在每次尺寸变化后主动把最小高度对齐，避免被父布局压扁
        （典型场景：Expander 展开时把多行描述压成一行）。
        """
        lay = self.layout()
        if lay is None or not lay.hasHeightForWidth():
            return
        width = self.width()
        if width <= 0:
            return

        lay.invalidate()
        natural = lay.heightForWidth(width)
        if natural > 0 and self.minimumHeight() != natural:
            self.setMinimumHeight(natural)
            self.updateGeometry()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._sync_content_height()

    def showEvent(self, event):
        super().showEvent(event)
        self._sync_content_height()

    # --------------------------- 配色 ---------------------------
    def get_bg_color(self) -> QColor:
        return self._bg_color

    def set_bg_color(self, color):
        color = QColor(color)
        if color != self._bg_color:
            self._bg_color = color
            self.update()

    def get_border_color(self) -> QColor:
        return self._border_color

    def set_border_color(self, color):
        color = QColor(color)
        if color != self._border_color:
            self._border_color = color
            self.update()

    bg_color = Property(QColor, get_bg_color, set_bg_color)
    border_color = Property(QColor, get_border_color, set_border_color)

    # --------------------------- 布局挂载 ---------------------------
    def mount_layout(self, layout):
        """把外部布局挂载为卡片布局（会替换已有布局）。"""
        old = self.layout()
        if old is not None and old is not layout:
            while old.count():
                item = old.takeAt(0)
                w = item.widget()
                if w is not None:
                    w.setParent(None)
            # 交给临时 widget 释放旧布局，否则 setLayout 会拒绝安装新布局
            QWidget().setLayout(old)
        self.setLayout(layout)

    # --------------------------- 自绘 ---------------------------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        rect = QRectF(self.rect())

        path = QPainterPath()
        path.addRoundedRect(rect, self._radius, self._radius)
        painter.fillPath(path, self._bg_color)

        # QPen 宽度为 0 时是 cosmetic pen（仍会画 1px），无边框必须直接跳过描边
        if self._border_width > 0:
            pen = QPen(self._border_color)
            pen.setWidthF(self._border_width)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            inner = rect.adjusted(0.5, 0.5, -0.5, -0.5)
            painter.drawRoundedRect(inner, self._radius, self._radius)


class ContentCardState(IntEnum):
    """ContentCard 的显示模式。

    Wide / Warp / NoIcon 是卡片实际可能处于的显示模式；Auto 只用于
    setCardMode() 恢复按宽度自适应，不会出现在 cardModeChanged 信号里。
    cardStateChanged 只会广播 Wide / Warp；cardModeChanged 广播 Wide / Warp / NoIcon。

    示例：
        card.setCardMode(ContentCardState.Warp)   # 强制窄模式
        card.setCardMode(ContentCardState.Auto)   # 恢复自动
    """

    Wide = 0
    Warp = 1
    NoIcon = 2
    Auto = 3


class ContentCard(Card):
    """可自定义的内容卡片（宽 / 窄模式自适应），布局由 Card 基类挂载。

    参数：
        title       —— 图标 QLabel（用 fonticon() 生成）；None 表示无图标
        subtitle    —— 子标题文字
        description —— 描述文字

    宽模式：
        [图标] ←20px→ [副标题]                   ←32px→ [右侧 layout]
                      [描述（自动换行）]

    窄模式：
        [图标] ←20px→ [副标题]
                      ↓ 2px
                      [描述]
                      ↓ 8px
                      [右侧 layout（左对齐）]

    阈值参数：
        wrap_threshold     —— 组件宽度 < 该值时切到窄模式（默认 475）
        no_icon_threshold  —— 组件宽度 < 该值时隐藏图标（默认 100）

    空内容处理（None / 空字符串 / 纯空白 都视为「无内容」，对应布局项隐藏）：
        title 为空       —— 按无图标模式处理，中间列不再保留 20px 缩进
        subtitle 为空    —— 隐藏副标题，剩下的描述居中
        description 为空 —— 隐藏描述，剩下的副标题居中
        subtitle 与 description 都为空 —— 两个布局项都隐藏，中间列收敛为 0 宽（不再进入窄模式）

    显示模式（ContentCardState，忽略当前宽度强制切换）：
        Wide   —— 强制宽模式（图标 + 文字并排、右侧 layout 贴右）
        Warp   —— 强制窄模式（右侧 layout 换到描述下方）
        NoIcon —— 强制隐藏图标（宽 / 窄保持当前设置），等同 hideIcon(True)
        Auto   —— 恢复按宽度自适应；只用于 setCardMode，不会出现在 cardModeChanged 里
        Wide / Warp / Auto 只切换宽 / 窄，不改变图标显隐（图标由 hideIcon / NoIcon 单独控制）。

    信号：
        cardModeChanged(旧模式, 新模式) —— 显示模式变化（Wide / Warp / NoIcon），
                                          参数都是 ContentCardState
        cardStateChanged(新模式)        —— 只有宽 / 窄布局变化时发出（只有 Wide / Warp）：
                                          手动切 Wide / Warp 总会广播一次；
                                          Auto 结果与当前状态不同才广播 Wide / Warp
                                          （宽度小到自动隐藏图标时按 Warp 算）；
                                          尺寸变化导致宽 / 窄切换时广播；
                                          NoIcon / ShowIcon 只改图标，不广播。
        IconHided(bool)                 —— 图标显隐变化，bool 为更新后是否隐藏
        hideIcon(bool)：True 强制隐藏，False 恢复自动（Auto 模式下宽度低于
        no_icon_threshold 时仍会隐藏）。
        hideIcon(bool) 单独控制图标：True 强制隐藏；False 恢复自动
        （Auto 模式下宽度低于 no_icon_threshold 时仍会隐藏）。

    示例：
        right = QHBoxLayout()
        right.addWidget(fonticon("\uE76C", size=14))
        card = ContentCard(
            title=fonticon("\uE799", size=20),
            subtitle="Wi-Fi",
            description="已连接：Office-5G",
            right_layout=right,
        )
        card.set_subtitle("蓝牙")            # 文字可随时修改
        card.setCardMode(ContentCardState.Warp)    # 强制窄模式
        card.setCardMode(ContentCardState.Auto)    # 恢复按宽度自适应
        card.hideIcon(True)                        # 单独隐藏图标
        card.hideIcon(False)                       # 恢复显示（不影响宽 / 窄）
        card.cardModeChanged.connect(lambda old, new: print(old, new))
        card.cardStateChanged.connect(lambda state: print(state))
        card.IconHided.connect(lambda hidden: print(hidden))
    """

    cardModeChanged = Signal(ContentCardState, ContentCardState)
    cardStateChanged = Signal(ContentCardState)
    IconHided = Signal(bool)

    _ICON_GAP = 20         # 图标 ↔ 中间列
    _CONTENT_GAP = 32      # 中间列 ↔ 右侧 layout（宽模式）
    _NARROW_TOP_GAP = 8    # 右侧 layout 顶部额外间距（窄模式）
    _ROW_GAP = 2           # 副标题 ↔ 描述

    _SUBTITLE_COLOR = "#FFFFFF"    # 默认配色，可由 qss 的 .CardSubtitle 覆盖
    _DESC_COLOR = "#D1D1D1"        # 默认配色，可由 qss 的 .CardDescription 覆盖
    _SUBTITLE_SIZE = 14            # 字号（写进标签自身样式表，不受全局 `*` 影响）
    _DESC_SIZE = 12

    def __init__(self, title="\uE799", subtitle="副标题文字",
                 description="描述说明文字", right_layout=None,
                 wrap_threshold=475, no_icon_threshold=100, parent=None):
        self._wrap_threshold = wrap_threshold
        self._no_icon_threshold = no_icon_threshold

        # ---- 状态 ----
        self._width_mode = ContentCardState.Auto     # 宽度模式：Auto / Wide / Warp
        self._hide_icon = False                      # hideIcon() 的强制隐藏标记
        self._card_mode = ContentCardState.Wide      # 当前显示模式（供 cardModeChanged）
        self._card_state = ContentCardState.Wide     # 已上报的宽 / 窄布局状态（供 cardStateChanged）
        self._icon_hidden = False                    # 已上报的图标隐藏状态（供 IconHided）
        self._is_narrow = False
        self._icon_visible = True
        self._mid_empty = False
        self._suspend = False
        self._has_title = False
        self._has_subtitle = False
        self._has_description = False

        subtitle = _normalize_text(subtitle)
        description = _normalize_text(description)

        # ================= 根布局（交给 Card 基类挂载） =================
        self._root = QHBoxLayout()
        self._root.setContentsMargins(16, 16, 16, 16)
        # spacing = 0，水平间距全部由 mid_layout 的 left margin
        # 和右侧 layout 的 left margin 精确控制
        self._root.setSpacing(0)

        super().__init__(layout=self._root, parent=parent)

        # 垂直方向按内容高度收敛（仍保留 heightForWidth，换行文字才能算对高度）
        self.setSizePolicy(_hfw_policy(QSizePolicy.Expanding, QSizePolicy.Fixed))

        # ================= 第一列：图标（外部传入的 QLabel，None 则整列省略） =================
        self._title_label = _as_icon_label(title)
        if self._title_label is not None:
            self._root.addWidget(self._title_label, 0, Qt.AlignVCenter)

        # ================= 第二列：副标题 + 描述 =================
        # 中间列放在容器里，副标题与描述都为空时该列收敛为 0 宽（不占位），
        # 但仍保留拉伸因子，保证右侧 layout 依旧贴右。
        self._mid_container = _HFWContainer(self)
        self._mid_container.setSizePolicy(
            _hfw_policy(QSizePolicy.Expanding, QSizePolicy.Preferred))
        self._mid_container.setMinimumWidth(0)

        self._mid_layout = QVBoxLayout(self._mid_container)
        # left = 24 → 图标 ↔ 中间列内容 24px
        self._mid_layout.setContentsMargins(self._ICON_GAP, 0, 0, 0)
        self._mid_layout.setSpacing(self._ROW_GAP)

        self._subtitle_label = TextLabel(subtitle, self._SUBTITLE_COLOR, self._SUBTITLE_SIZE)
        _prep_text_label(self._subtitle_label)
        set_style(self._subtitle_label, "CardSubtitle")

        self._desc_label = TextLabel(description, self._DESC_COLOR, self._DESC_SIZE)
        _prep_text_label(self._desc_label)
        set_style(self._desc_label, "CardDescription")

        self._mid_layout.addWidget(self._subtitle_label, 1, Qt.AlignVCenter)
        self._mid_layout.addWidget(self._desc_label, 1, Qt.AlignVCenter)

        self._root.addWidget(self._mid_container, 1)

        # ================= 第三列：右侧 layout 容器 =================
        self._right_container = QWidget(self)
        self._right_container.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        self._right_container.setMinimumWidth(0)
        self._root.addWidget(self._right_container, 0, Qt.AlignVCenter)

        if right_layout is not None:
            self.set_right_layout(right_layout)

        self._sync_content_state()

    # --------------------------- 帮助函数 ---------------------------
    def _sync_content_state(self):
        """按 title / subtitle / description 是否有内容（文字或图片）同步可见性。"""
        self._has_title = _has_visual_content(self._title_label)
        self._has_subtitle = _has_visual_content(self._subtitle_label)
        self._has_description = _has_visual_content(self._desc_label)

        if self._title_label is not None:
            self._title_label.setVisible(self._has_title)
        self._subtitle_label.setVisible(self._has_subtitle)
        self._desc_label.setVisible(self._has_description)

        # 副标题与描述都没有 → 中间列无内容（宽度收敛为 0，不占位）
        mid_empty = not (self._has_subtitle or self._has_description)
        if mid_empty != self._mid_empty:
            self._mid_empty = mid_empty
            self._apply_right_margins_for_mode()
            self._update_layout_mode()
            self.updateGeometry()
        self._sync_content_height()

    # --------------------------- 文字自定义 ---------------------------
    def set_title(self, title: Optional[Union[QLabel, str]]):
        """设置图标；传入 QLabel（fonticon() 生成）或在位替换旧的图标。"""
        label = _as_icon_label(title)
        old = self._title_label
        if label is not old:
            index = self._root.indexOf(old) if old is not None else 0
            if old is not None:
                self._root.removeWidget(old)
                old.setParent(None)
            self._title_label = label
            if label is not None:
                self._root.insertWidget(index, label, 0, Qt.AlignVCenter)
        self._sync_content_state()
        self._update_layout_mode()

    def title(self) -> Optional[QLabel]:
        return self._title_label

    def set_subtitle(self, text: Optional[str]):
        self._subtitle_label.setText(_normalize_text(text))
        self._sync_content_state()
        self._update_layout_mode()

    def subtitle(self) -> str:
        return self._subtitle_label.text()

    def set_description(self, text: Optional[str]):
        self._desc_label.setText(_normalize_text(text))
        self._sync_content_state()
        self._update_layout_mode()

    def description(self) -> str:
        return self._desc_label.text()

    # --------------------------- 右侧 layout 自定义 ---------------------------
    def set_right_layout(self, layout):
        old = self._right_container.layout()
        if old is not None:
            while old.count():
                item = old.takeAt(0)
                w = item.widget()
                if w is not None:
                    w.setParent(None)
            QWidget().setLayout(old)

        self._right_container.setLayout(layout)
        # Card 内部统一管理间距，不保留用户 layout 的外部边距
        self._apply_right_margins_for_mode()

        if self.isVisible():
            self._update_layout_mode()

    def right_container(self) -> QWidget:
        return self._right_container

    # --------------------------- 间距随模式调整 ---------------------------
    def _apply_right_margins_for_mode(self):
        """Card 内部统一为右侧 layout 设定边距：
        - 宽模式：left = 32  → 与描述保持 32px
        - 窄模式：left = 0、top = 8 → 与描述左对齐，且行间 4 + 8 = 12px
        - 中间列隐藏：left = 0 → 不保留与空中间列的间隔
        """
        lay = self._right_container.layout()
        if lay is None:
            return
        if self._is_narrow:
            lay.setContentsMargins(0, self._NARROW_TOP_GAP, 0, 0)
        elif self._mid_empty:
            lay.setContentsMargins(0, 0, 0, 0)
        else:
            lay.setContentsMargins(self._CONTENT_GAP, 0, 0, 0)

    # --------------------------- 模式切换 ---------------------------
    def _switch_mode(self, narrow: bool):
        if self._suspend or narrow == self._is_narrow:
            return
        self._suspend = True
        try:
            if narrow:
                self._apply_narrow()
            else:
                self._apply_wide()
        finally:
            self._suspend = False

    def _apply_wide(self):
        self._mid_layout.removeWidget(self._right_container)
        self._right_container.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        self._root.addWidget(self._right_container, 0, Qt.AlignVCenter)
        self._is_narrow = False
        self._apply_right_margins_for_mode()
        self._right_container.show()
        self.updateGeometry()

    def _apply_narrow(self):
        self._root.removeWidget(self._right_container)
        self._right_container.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        self._mid_layout.addWidget(self._right_container, 0, Qt.AlignLeft)
        self._is_narrow = True
        self._apply_right_margins_for_mode()
        self._right_container.show()
        self.updateGeometry()

    def _set_card_mode(self, mode: ContentCardState):
        """更新当前显示模式并发出 cardModeChanged（Auto 不会作为状态出现）。"""
        if mode == self._card_mode:
            return
        old = self._card_mode
        self._card_mode = mode
        self.cardModeChanged.emit(old, mode)

    def _set_card_state(self, state: ContentCardState):
        """更新宽 / 窄布局状态并发出 cardStateChanged（只有 Wide / Warp）。"""
        if state == self._card_state:
            return
        self._card_state = state
        self.cardStateChanged.emit(state)

    def _set_icon_hidden(self, hidden: bool):
        """更新图标显隐状态并发出 IconHided（bool 为更新后是否隐藏）。"""
        hidden = bool(hidden)
        if hidden == self._icon_hidden:
            return
        self._icon_hidden = hidden
        self.IconHided.emit(hidden)

    def _update_layout_mode(self):
        """按模式 / 宽度更新图标与宽窄布局，并同步 cardModeChanged。"""
        if self._suspend:
            return

        width = self.width()
        auto = self._width_mode == ContentCardState.Auto

        self._suspend = True
        try:
            # --- 图标可见性 ---
            # 强制模式忽略宽度阈值；Auto 才按 no_icon_threshold 自动隐藏
            if self._hide_icon:
                show_icon = False
            elif auto and width > 0:
                show_icon = self._has_title and width >= self._no_icon_threshold
            else:
                show_icon = self._has_title

            if self._title_label is not None and show_icon != self._icon_visible:
                self._title_label.setVisible(show_icon)
                self._icon_visible = show_icon
            # 图标隐藏（或被隐藏的中间列）时不再需要 24px 左缩进
            left = self._ICON_GAP if (show_icon and not self._mid_empty) else 0
            m = self._mid_layout.contentsMargins()
            if m.left() != left:
                self._mid_layout.setContentsMargins(left, m.top(), m.right(), m.bottom())

            # --- 宽 / 窄 ---
            if auto:
                if width <= 0:
                    narrow = self._is_narrow          # 尺寸未知时保持现状
                elif self._mid_empty:
                    narrow = False                    # 中间列没有文字时无需换行
                else:
                    narrow = width < self._wrap_threshold
            else:
                narrow = self._width_mode == ContentCardState.Warp
        finally:
            self._suspend = False

        self._switch_mode(narrow)

        # --- 当前布局状态 / 图标状态 / 组合显示模式 ---
        state = ContentCardState.Warp if self._is_narrow else ContentCardState.Wide
        icon_hidden = bool(self._has_title and not show_icon)
        # 图标隐藏时 cardModeChanged 上报 NoIcon；Auto 永远不会作为状态出现
        mode = ContentCardState.NoIcon if icon_hidden else state

        self._set_icon_hidden(icon_hidden)
        self._set_card_state(state)
        self._set_card_mode(mode)

    # --------------------------- 显示模式 ---------------------------
    def setCardMode(self, mode: ContentCardState):
        """强制切换显示模式（不论当前宽度）。

        mode 取 ContentCardState：
            Wide   —— 强制宽模式，并广播 cardStateChanged(Wide)
            Warp   —— 强制窄模式，并广播 cardStateChanged(Warp)
            NoIcon —— 强制隐藏图标，宽 / 窄保持当前设置（等同 hideIcon(True)）；
                      只改图标，不广播 cardStateChanged
            Auto   —— 恢复按宽度自动切换；解析结果与当前状态不同才广播
                      Wide / Warp（不会广播 Auto）
        Wide / Warp / Auto 只切换宽 / 窄，不改变图标显隐；要重新显示图标请调 hideIcon(False)。
        手动切 Wide / Warp 时总会广播一次 cardStateChanged（即使状态没变）。
        """
        mode = ContentCardState(mode)
        if mode == ContentCardState.NoIcon:
            self.hideIcon(True)
            return
        previous_state = self._card_state
        self._width_mode = mode
        self._update_layout_mode()
        if mode in (ContentCardState.Wide, ContentCardState.Warp) and previous_state == mode:
            # 状态真正变化时 _update_layout_mode 已经发过；这里补发“手动切到相同状态”
            self.cardStateChanged.emit(mode)

    def hideIcon(self, hidden: bool = True):
        """单独控制图标显隐（与宽 / 窄模式无关）。

        hidden=True 时无论宽度都隐藏图标（优先于 Wide / Warp 模式）；
        hidden=False 恢复自动：强制模式（Wide / Warp）下直接显示，
        Auto 模式下仍受 no_icon_threshold 限制。
        图标显隐实际发生变化时发出 IconHided(bool)。
        setCardMode(Wide / Warp / Auto) 不会改变这里的强制隐藏；要显示图标请调 hideIcon(False)。
        """
        hidden = bool(hidden)
        if hidden == self._hide_icon:
            return
        self._hide_icon = hidden
        self._update_layout_mode()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_layout_mode()

    def showEvent(self, event):
        super().showEvent(event)
        self._update_layout_mode()

@level_component(contribution=0)
class PressableRow(Card):
    """可按下的一行（下拉按钮 / 下拉菜单项）：悬浮与按下变色，释放时触发槽函数。

    参数：
        layout   —— 行内布局（挂载到 Card 上，边距由调用方决定）
        on_click —— 释放时调用的槽函数；也可以连接 clicked 信号
        variant  —— 样式变体：
                    "default" 独立使用：无边框、透明背景、上下左右 8px 内边距、4px 圆角，
                              悬浮 / 按下只改背景色
                    "menu"    挂载在 Expander 下时使用：卡片底色 + 边框配色

    挂载时切换样式（与 layout 挂载同理）：Expander.add_layout 会把 PressableRow
    切到 "menu" 变体；也可直接调用 set_variant()。

    配色：普通 / 悬浮 / 按下三套 class 都在 qss 里
          （.PressableRow / .PressableRowHover / .PressableRowPressed 与
          .ExpanderRow / .ExpanderRowHover / .ExpanderRowPressed，见 Gui/res/styles/dark.qss），
          代码只按状态与变体调用 set_style 切换 class。

    信号：
        clicked  —— 在行内释放时触发（按下后拖出再拖回、仍在行内释放也算）
        pressed  —— 按下时触发（按住拖出后拖回会再次触发，与 QPushButton 一致）
        released —— 松开或按住拖出时触发（与 QPushButton 一致）

    示例：
        row_layout = QHBoxLayout()
        row_layout.addWidget(fonticon("\uE713", size=16))
        row_layout.addWidget(TextLabel("菜单项"), 1)
        row = PressableRow(layout=row_layout, on_click=lambda: print("clicked"))
        row.clicked.connect(lambda: print("clicked signal"))
        row.pressed.connect(lambda: print("pressed"))
        row.released.connect(lambda: print("released"))
    """

    clicked = Signal()
    pressed = Signal()
    released = Signal()

    VARIANT_DEFAULT = "default"
    VARIANT_MENU = "menu"

    STYLE_CLASS = "PressableRow"
    HOVER_CLASS = "PressableRowHover"
    PRESSED_CLASS = "PressableRowPressed"

    MENU_STYLE_CLASS = "ExpanderRow"
    MENU_HOVER_CLASS = "ExpanderRowHover"
    MENU_PRESSED_CLASS = "ExpanderRowPressed"

    _CLASSES = {
        VARIANT_DEFAULT: (STYLE_CLASS, HOVER_CLASS, PRESSED_CLASS),
        VARIANT_MENU: (MENU_STYLE_CLASS, MENU_HOVER_CLASS, MENU_PRESSED_CLASS),
    }

    _BG = "#343434"        # menu 变体默认配色（qss 未加载时的兜底值）
    _BORDER = "#232323"
    _RADIUS = 4            # 圆角（形状，不由 qss 控制）
    _BORDER_WIDTH = 1      # menu 变体边框宽度（default 变体无边框）
    _PADDING = 8           # default 变体上下左右内边距

    def __init__(self, layout=None, on_click=None, parent=None,
                 variant=VARIANT_DEFAULT):
        # Card.__init__ 会读取 _source_margins / variant 相关状态
        self._variant = self._normalize_variant(variant)
        self._source_margins = None

        super().__init__(layout=layout, parent=parent)

        self._on_click = on_click
        self._hover = False
        self._pressed = False
        self._down = False

        # 背景自绘（paintEvent），不需要 QSS 背景
        self.setCursor(Qt.PointingHandCursor)
        self._apply_variant()

    # --------------------------- 变体 ---------------------------
    @classmethod
    def _normalize_variant(cls, variant) -> str:
        if variant not in cls._CLASSES:
            raise ValueError(f"未知的 PressableRow 变体：{variant!r}")
        return variant

    def variant(self) -> str:
        return self._variant

    def set_variant(self, variant):
        """切换样式变体（挂载到 Expander 时由 Expander 调用）。"""
        variant = self._normalize_variant(variant)
        if variant == self._variant:
            return
        self._variant = variant
        self._apply_variant()

    def _apply_variant(self):
        """按变体设置形状、内边距与配色 class。"""
        if self._variant == self.VARIANT_MENU:
            self._border_width = self._BORDER_WIDTH
        else:
            self._border_width = 0
        self._radius = self._RADIUS

        self._apply_padding()
        self._sync_state_class()
        self._sync_content_height()
        self.updateGeometry()
        self.update()

    # --------------------------- 内边距 ---------------------------
    def mount_layout(self, layout):
        """挂载布局时记录调用方边距，便于切回 menu 变体时恢复。"""
        super().mount_layout(layout)
        self._source_margins = layout.contentsMargins()
        self._apply_padding()

    def _apply_padding(self):
        """default 变体：上下左右 8px；menu 变体：恢复调用方设置的边距。"""
        lay = self.layout()
        if lay is None:
            return
        if self._variant == self.VARIANT_MENU:
            if self._source_margins is None:
                return
            target = self._source_margins
        else:
            target = QMargins(self._PADDING, self._PADDING,
                              self._PADDING, self._PADDING)
        if lay.contentsMargins() != target:
            lay.setContentsMargins(target)
            self.updateGeometry()

    # --------------------------- 交互 ---------------------------
    def set_on_click(self, on_click):
        self._on_click = on_click

    def _base_bg_color(self) -> QColor:
        return QColor(self._BG) if self._variant == self.VARIANT_MENU else QColor(0, 0, 0, 0)

    def _base_border_color(self) -> QColor:
        return QColor(self._BORDER) if self._variant == self.VARIANT_MENU else QColor(0, 0, 0, 0)

    def _sync_state_class(self):
        """按当前状态切换样式 class（颜色定义在 qss 里）。"""
        normal, hover, pressed = self._CLASSES[self._variant]
        if self._pressed:
            set_style(self, pressed)
        elif self._hover:
            set_style(self, hover)
        else:
            # qss 未提供对应 class 时也要干净地回到常态配色
            self._bg_color = self._base_bg_color()
            self._border_color = self._base_border_color()
            set_style(self, normal)

    def _set_down(self, down: bool):
        """更新按下状态并发出 pressed / released（与 QPushButton 一致）。"""
        down = bool(down)
        if down == self._down:
            return
        self._down = down
        self._pressed = down
        self._sync_state_class()
        if down:
            self.pressed.emit()
        else:
            self.released.emit()

    def enterEvent(self, event):
        self._hover = True
        self._sync_state_class()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hover = False
        if not self._down:
            self._pressed = False
        self._sync_state_class()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._hover = True
            if not self._down and self.rect().contains(event.position().toPoint()):
                self._set_down(True)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        # 与 QPushButton 一致：按住拖出时 released、拖回时再次 pressed
        if event.buttons() & Qt.LeftButton:
            inside = self.rect().contains(event.position().toPoint())
            if inside != self._down:
                self._set_down(inside)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self._down:
            inside = self.rect().contains(event.position().toPoint())
            self._set_down(False)
            if inside:
                self._emit_click()
        super().mouseReleaseEvent(event)

    def _emit_click(self):
        self.clicked.emit()
        if self._on_click is not None:
            self._on_click()

    def trigger(self):
        """程序化触发一次点击（等价 QPushButton.click()：pressed → released → clicked）。"""
        self._set_down(True)
        self._set_down(False)
        self._emit_click()


class _Divider(QFrame):
    """下拉内容之间的 1px 分割线。

    颜色默认值见 _COLOR，可由 qss 里的
    `.ExpanderDivider { qproperty-color: ... }` 覆盖（见 Gui/res/styles/dark.qss）。

    示例：
        line = _Divider()
        line.setFixedHeight(1)
        line.set_color("#3A3A3A")     # 或交给 qss 的 .ExpanderDivider
    """

    STYLE_CLASS = "ExpanderDivider"

    _COLOR = "#232323"

    def __init__(self, parent=None):
        super().__init__(parent)
        self._color = QColor(self._COLOR)
        self._apply_color()
        set_style(self, self.STYLE_CLASS)

    def _apply_color(self):
        self.setStyleSheet(f"background-color: {self._color.name()}; border: none;")

    def get_color(self) -> QColor:
        return self._color

    def set_color(self, color):
        color = QColor(color)
        if color != self._color:
            self._color = color
            self._apply_color()

    color = Property(QColor, get_color, set_color)

def add_smart(layout, obj, stretch: int = 0):
    """把一个控件 / 布局 / 布局项添加到布局里（按类型自动选择 addWidget / addLayout / addItem）。

    示例：
        row = QHBoxLayout()
        add_smart(row, fonticon("\uE799"))          # QWidget → addWidget
        add_smart(row, QVBoxLayout(), stretch=1)    # QLayout  → addLayout
    """
    if isinstance(obj, QWidget):
        layout.addWidget(obj, stretch)
    elif isinstance(obj, QLayout):
        layout.addLayout(obj, stretch)
    elif isinstance(obj, QLayoutItem):
        layout.addItem(obj)
    else:
        raise TypeError(f"add_smart not supported type: {type(obj).__name__}")


def _iter_labels(widget: QWidget):
    """遍历控件自身（若是文字标签）及其内部的文字标签。"""
    if isinstance(widget, QLabel):
        yield widget
    yield from widget.findChildren(QLabel)


def _one_char_width(label: QLabel) -> int:
    """一个字符的最小宽度（一行至少能放一个字符）。"""
    fm = label.fontMetrics()
    return max(1, fm.horizontalAdvance("M"), fm.horizontalAdvance("字"))


def _as_side_widget(obj, hfw: bool = False):
    """把一侧内容统一成可设置尺寸策略的控件；spacer 等无法包装的对象原样返回。

    传入 QLayout 时会包进容器：外层行已提供内边距，内部布局的默认 9px 边距
    （Qt 默认值）必须清零，否则那一侧会比纯控件高 18px，内容还会内缩。
    hfw=True 用支持 heightForWidth 的容器（供左侧换行压缩使用）。
    """
    if isinstance(obj, QWidget):
        return obj
    if isinstance(obj, QLayout):
        container = _HFWContainer() if hfw else QWidget()
        obj.setContentsMargins(0, 0, 0, 0)
        container.setLayout(obj)
        return container
    if isinstance(obj, QLayoutItem):
        widget = obj.widget()
        if widget is not None:
            return widget
        layout = obj.layout()
        if layout is not None:
            return _as_side_widget(layout, hfw)
    return obj


def _prepare_expander_side(obj, compressible: bool):
    """按左右两侧的不同需求设置尺寸策略。

    左侧（compressible=True）：文字自动换行，可一路压缩到一行一个字符；
    右侧（compressible=False）：保持原有尺寸，不随可用宽度收缩。
    """
    widget = _as_side_widget(obj, hfw=compressible)
    if not isinstance(widget, QWidget):
        return obj

    if compressible:
        for label in _iter_labels(widget):
            label.setWordWrap(True)
            label.setMinimumWidth(_one_char_width(label))
            label.setSizePolicy(_hfw_policy(QSizePolicy.Preferred, QSizePolicy.Preferred))
        if isinstance(widget, QLabel):
            widget.setSizePolicy(_hfw_policy(QSizePolicy.Preferred, QSizePolicy.Preferred))
        else:
            policy = widget.sizePolicy()
            policy.setHorizontalPolicy(QSizePolicy.Preferred)
            lay = widget.layout()
            # 只有真正支持 heightForWidth 的内容才开启，否则布局会算出错误高度
            policy.setHeightForWidth(bool(lay is not None and lay.hasHeightForWidth()))
            widget.setSizePolicy(policy)
            # 容器最小宽度 = 内部内容的最小宽度（文字已按一个字符为下限）
            widget.setMinimumWidth(widget.minimumSizeHint().width())
    else:
        # 不换行 + Fixed：sizeHint 即上限，右侧不会被压缩
        for label in _iter_labels(widget):
            label.setWordWrap(False)
            label_policy = label.sizePolicy()
            label_policy.setHeightForWidth(False)
            label.setSizePolicy(label_policy)
        policy = widget.sizePolicy()
        policy.setHorizontalPolicy(QSizePolicy.Fixed)
        policy.setHeightForWidth(False)
        widget.setSizePolicy(policy)
    return widget


def create_expander_row(left_widget, right_widget, press_command=None) -> PressableRow | QLayout:
    '''
    创建一个两边布局的项目

    左侧按可用宽度自动换行压缩（最小压缩到一行一个字符），右侧保持原尺寸不被压缩。

    参数：
        left_widget   —— 左侧组件
        right_widget  —— 右侧组件
        press_command —— 按下的操作，为None不注册

    示例：
        row = create_expander_row(
            TextLabel("Wi-Fi"),                        # 左侧：可压缩、自动换行
            fonticon("\uE72E", size=14),               # 右侧：保持原尺寸
            press_command=lambda: print("clicked"),    # 传入则返回 PressableRow
        )
        expander = Expander(layouts=[row])
    '''
    layout = QHBoxLayout()
    layout.setContentsMargins(60, 20, 16, 20)

    add_smart(layout, _prepare_expander_side(left_widget, compressible=True), stretch=1)
    add_smart(layout, _prepare_expander_side(right_widget, compressible=False), stretch=0)

    if press_command:
        return PressableRow(layout=layout, on_click=press_command)
    else:
        return layout

class Expander(Card):
    """下拉框（Expander）：标题行常显，下拉区可挂载多个布局，1px 分割线分隔。

    参数：
        title        —— 图标 QLabel（用 fonticon() 生成）；None 表示无图标
        subtitle     —— 标题文字
        description  —— 描述文字
        layouts      —— 下拉内容列表，元素可以是 QLayout，也可以是 QWidget
                        （例如 PressableRow，按下触发槽函数；挂载时会自动切到
                        「菜单」样式变体）；相邻两项间自动插入 1px 分割线
        expanded     —— 初始是否展开（默认收起）
        duration     —— 展开 / 收起动画时长（ms），<= 0 表示立即切换
        right_layout —— 自定义右侧布局（可选），放在下拉箭头左侧，间隔 8px；
                        用法与 ContentCard 的 right_layout 一致

    信号：
        toggled(bool)            —— 展开状态变化后发出（旧信号，保留兼容）
        expandStateChanged(bool) —— 展开状态变化后发出，bool 为变化后的展开状态

    配色：下拉区底色 / 文字 / 箭头 / 分割线的颜色都在 qss 里
          （.Expander、.ExpanderSubtitle、.ExpanderDescription、.ExpanderArrow、
          .ExpanderDivider，见 Gui/res/styles/dark.qss），代码只用 set_style 挂 class，
          具体颜色值不写在代码里。

    布局（不随宽度自适应缩放）：
        16px │ 图标(跨两行) 20px 标题 ···· [右侧布局] 8px 箭头(居右) │ 16px
             │                      8px
             │                      描述
        16px
    （图标、文字列、右侧布局、箭头都在竖直方向居中）

    组件层级：Expander 继承 Card（贡献 +1），所以标题栏（PressableRow）和
    下拉区的每个布局 / 控件都处于 1 级；Expander 自身是否加层由它所在
    的父组件决定（挂在页面根上时 raw=0）。

    示例：
        expander = Expander(
            title=fonticon("\uE713", size=20),
            subtitle="设置",
            description="网络 / 蓝牙 / 飞行模式",
            layouts=[
                create_expander_row(TextLabel("Wi-Fi"), fonticon("\uE72E", size=14)),
                create_expander_row(TextLabel("蓝牙"), TextLabel("关", "#9A9A9A", 12)),
            ],
            expanded=False,
        )
        expander.expandStateChanged.connect(
            lambda expanded: print("展开状态:", expanded))
    """

    _PAD = 16              # 上下左右内边距
    _GAP = 4               # 基础间距
    _ICON_GAP = 20         # 图标 ↔ 文字列
    _ROW_GAP = 2    # 8px（2 个 Gap），标题 ↔ 描述
    _RIGHT_GAP = 8         # 右侧布局 ↔ 箭头
    _DURATION = 250        # 展开 / 收起动画时长
    _ARROW_ICON = "\uE70D"
    _ARROW_SIZE = 12

    _SUBTITLE_COLOR = "#FFFFFF"  # 默认配色，可由 qss 的 .ExpanderSubtitle 覆盖
    _DESC_COLOR = "#D1D1D1"      # 默认配色，可由 qss 的 .ExpanderDescription 覆盖
    _SUBTITLE_SIZE = 14          # 字号（写进标签自身样式表，不受全局 `*` 影响）
    _DESC_SIZE = 12

    STYLE_CLASS = "Expander"
    ARROW_CLASS = "ExpanderArrow"

    _BG = "#323232"        # 下拉菜单底色默认值（可由 qss 的 .Expander 覆盖）
    _BORDER = "#232323"

    toggled = Signal(bool)
    expandStateChanged = Signal(bool)

    def __init__(self, title=None, subtitle="", description="", layouts=None,
                 expanded=False, duration=None, right_layout=None, parent=None):
        self._expanded = bool(expanded)
        self._duration = self._DURATION if duration is None else int(duration)

        # ================= 根布局（交给 Card 基类挂载） =================
        self._root = QVBoxLayout()
        self._root.setContentsMargins(0, 0, 0, 0)
        self._root.setSpacing(0)

        super().__init__(layout=self._root, parent=parent)

        # Card 底色即下拉菜单背景（#323232 / #232323）；
        # 标题行（PressableRow）自带下拉按钮配色

        # ================= 标题行 =================
        self._title_label = _as_icon_label(title)
        self._arrow = fonticon(self._ARROW_ICON, size=self._ARROW_SIZE)
        set_style(self._arrow, self.ARROW_CLASS)

        self._header = PressableRow(layout=self._build_header_layout(subtitle, description),
                                    on_click=self.toggle, parent=self,
                                    variant=PressableRow.VARIANT_MENU)
        self._root.addWidget(self._header)
        if right_layout is not None:
            self.set_right_layout(right_layout)
        self._apply_right_margins()

        # ================= 下拉区（透明，露出 Card 的菜单底色） =================
        self._items = []
        self._create_body()
        for obj in layouts or []:
            self.add_layout(obj)

        # ================= 动画 =================
        self._arrow_anim = QPropertyAnimation(self._arrow, b"angle", self)
        self._arrow_anim.setDuration(self._duration)
        self._arrow_anim.setStartValue(0.0)
        self._arrow_anim.setEndValue(180.0)

        self._body_anim = QPropertyAnimation(self._body, b"maximumHeight", self)
        self._body_anim.setDuration(self._duration)
        self._body_anim.finished.connect(self._on_body_anim_finished)

        self._sync_content_state()
        self._apply_expanded_state()

    # --------------------------- 标题行布局 ---------------------------
    def _build_header_layout(self, subtitle, description) -> QHBoxLayout:
        # 标题行：只有标题（箭头放到整行右侧，见下方 box）
        title_row = QHBoxLayout()
        title_row.setContentsMargins(0, 0, 0, 0)
        title_row.setSpacing(0)

        self._subtitle_label = TextLabel(_normalize_text(subtitle), self._SUBTITLE_COLOR,
                                         self._SUBTITLE_SIZE)
        _prep_text_label(self._subtitle_label)
        set_style(self._subtitle_label, "ExpanderSubtitle")

        self._desc_label = TextLabel(_normalize_text(description), self._DESC_COLOR,
                                     self._DESC_SIZE)
        _prep_text_label(self._desc_label)
        set_style(self._desc_label, "ExpanderDescription")

        title_row.addWidget(self._subtitle_label, 1, Qt.AlignVCenter)

        # 文字列容器：全空时宽度收敛为 0，但仍吸收拉伸，
        # 保证右侧布局与箭头始终贴右（与 ContentCard 的中间列同思路）
        self._text_container = _HFWContainer()
        self._text_container.setSizePolicy(
            _hfw_policy(QSizePolicy.Expanding, QSizePolicy.Preferred))
        self._text_container.setMinimumWidth(0)

        # 文字列：图标右侧 20px，标题 ↔ 描述 8px
        self._text_layout = QVBoxLayout(self._text_container)
        self._text_layout.setContentsMargins(self._ICON_GAP, 0, 0, 0)
        self._text_layout.setSpacing(self._ROW_GAP)
        self._text_layout.addLayout(title_row)
        self._text_layout.addWidget(self._desc_label, 0, Qt.AlignVCenter)

        # 右侧自定义布局容器（可选）
        self._right_container = QWidget()
        self._right_container.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        self._right_container.setMinimumWidth(0)

        # 箭头容器：只在有右侧布局时留出 8px，避免箭头被推离右边缘
        self._arrow_container = QWidget()
        self._arrow_container.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        self._arrow_layout = QHBoxLayout(self._arrow_container)
        self._arrow_layout.setContentsMargins(0, 0, 0, 0)
        self._arrow_layout.setSpacing(0)
        self._arrow_layout.addWidget(self._arrow, 0, Qt.AlignVCenter)

        # 标题行：图标 / 文字列 / 右侧布局 / 箭头（居右），都在竖直方向居中
        box = QHBoxLayout()
        box.setContentsMargins(self._PAD, self._PAD, self._PAD, self._PAD)
        box.setSpacing(0)
        if self._title_label is not None:
            box.addWidget(self._title_label, 0, Qt.AlignVCenter)
        box.addWidget(self._text_container, 1)
        box.addWidget(self._right_container, 0, Qt.AlignVCenter)
        box.addWidget(self._arrow_container, 0, Qt.AlignVCenter)
        return box

    def _sync_content_height(self):
        """Expander 自身高度由展开 / 收起动画控制，不能锁自己的最小高度。

        否则展开时会把最小高度锁成「标题行 + 下拉内容」，收起后父布局再也压不下去，
        腾出来的空间会被标题行吸收 —— 看起来就是「按钮变高到下拉框的高度」
        而不是下拉菜单向上收回。
        这里只需要保证标题行（内部是 Card）不被压扁即可。
        """
        header = getattr(self, "_header", None)   # __init__ 早于标题行创建
        if header is not None:
            header._sync_content_height()

    # --------------------------- 右侧自定义布局 ---------------------------
    def set_right_layout(self, layout):
        """设置右侧布局（箭头左侧，间隔 8px）；会替换已有布局。"""
        old = self._right_container.layout()
        if old is not None and old is not layout:
            while old.count():
                item = old.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)
            QWidget().setLayout(old)

        self._right_container.setLayout(layout)
        self._apply_right_margins()
        self._sync_content_height()

    def right_layout(self):
        return self._right_container.layout()

    def right_container(self) -> QWidget:
        return self._right_container

    def _apply_right_margins(self):
        """Expander 统一管理右侧间距（与 ContentCard 一致，不留用户 layout 的外部边距）：
        - 右侧布局：边距归零
        - 箭头：与右侧布局之间 8px；没有右侧布局时不留空隙
        """
        lay = self._right_container.layout()
        if lay is not None:
            lay.setContentsMargins(0, 0, 0, 0)

        m = self._arrow_layout.contentsMargins()
        left = self._RIGHT_GAP if lay is not None else 0
        if m.left() != left:
            self._arrow_layout.setContentsMargins(left, m.top(), m.right(), m.bottom())

    # --------------------------- 内容可见性 ---------------------------
    def _sync_content_state(self):
        """空的 title / subtitle / description 对应布局项隐藏（有图片也算有内容）。"""
        self._has_title = _has_visual_content(self._title_label)
        self._has_subtitle = _has_visual_content(self._subtitle_label)
        self._has_description = _has_visual_content(self._desc_label)

        if self._title_label is not None:
            self._title_label.setVisible(self._has_title)
        self._subtitle_label.setVisible(self._has_subtitle)
        self._desc_label.setVisible(self._has_description)

        # 图标不可见、或没有任何文字时，文字列不再保留 20px 缩进
        has_text = self._has_subtitle or self._has_description
        left = self._ICON_GAP if (self._has_title and has_text) else 0
        m = self._text_layout.contentsMargins()
        if m.left() != left:
            self._text_layout.setContentsMargins(left, m.top(), m.right(), m.bottom())
        self._text_container.updateGeometry()
        self.updateGeometry()
        self._sync_content_height()

    # --------------------------- 下拉内容 ---------------------------
    def _create_body(self):
        """新建下拉区容器（旧容器连同其中的布局 / 控件一并销毁）。"""
        old = getattr(self, "_body", None)
        self._body = QWidget(self)
        self._body_layout = QVBoxLayout(self._body)
        self._body_layout.setContentsMargins(0, 0, 0, 0)
        self._body_layout.setSpacing(0)
        self._root.addWidget(self._body)

        if old is not None:
            self._root.removeWidget(old)
            old.setParent(None)
            old.deleteLater()
            anim = getattr(self, "_body_anim", None)
            if anim is not None:
                anim.setTargetObject(self._body)

    def set_layouts(self, layouts):
        """重建下拉内容：元素为 QLayout 或 QWidget，中间自动插入 1px 分割线。"""
        self._items = []
        self._create_body()
        for obj in layouts or []:
            self.add_layout(obj)

    def add_layout(self, obj):
        """追加一个下拉项（自动补 1px 分割线）。"""
        # 挂载时切换样式：Expander 内的 PressableRow 使用菜单配色
        if isinstance(obj, PressableRow):
            obj.set_variant(PressableRow.VARIANT_MENU)
        if self._items:
            self._body_layout.addWidget(self._make_divider())
        if isinstance(obj, QLayout):
            self._body_layout.addLayout(obj)
        elif isinstance(obj, QWidget):
            self._body_layout.addWidget(obj)
        else:
            raise TypeError("layouts 的元素必须是 QLayout 或 QWidget")
        self._items.append(obj)
        self._resize_body()

    def layouts(self):
        """当前下拉项列表。"""
        return list(self._items)

    @staticmethod
    def _make_divider() -> "_Divider":
        line = _Divider()
        line.setFixedHeight(1)
        line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        return line

    def _body_height(self) -> int:
        """展开后的内容高度。

        文字换行时内容高度随宽度变化，因此优先用布局的 heightForWidth；
        没有 heightForWidth 的内容退回 sizeHint。
        """
        lay = self._body_layout
        hint = lay.sizeHint().height()
        if lay.hasHeightForWidth():
            # 下拉区与 Expander 同宽（根布局无边距），resizeEvent 里 body 的宽度还是旧值，
            # 因此优先用自身的宽度计算
            width = self.width() if self.width() > 0 else self._body.width()
            if width > 0:
                return max(hint, lay.heightForWidth(width))
        return hint

    def _resize_body(self):
        """收起时高度锁 0，展开时按内容高度。"""
        self._body.setMaximumHeight(self._body_height() if self._expanded else 0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # 宽度变化会改变换行内容的高度，展开状态下需要同步下拉区高度
        anim = getattr(self, "_body_anim", None)
        if (self._expanded and anim is not None
                and anim.state() != QAbstractAnimation.Running):
            self._resize_body()

    # --------------------------- 展开 / 收起 ---------------------------
    def is_expanded(self) -> bool:
        return self._expanded

    def toggle(self):
        self.set_expanded(not self._expanded)

    def set_expanded(self, expanded: bool, animate: bool = True):
        expanded = bool(expanded)
        if expanded == self._expanded:
            return
        self._expanded = expanded

        if animate and self._duration > 0:
            self._animate_to(expanded)
        else:
            self._apply_expanded_state()
        self.toggled.emit(expanded)
        self.expandStateChanged.emit(expanded)

    def _apply_expanded_state(self):
        """不做动画，直接切到当前展开状态。"""
        self._body_anim.stop()
        self._arrow_anim.stop()
        self._body.setVisible(self._expanded)
        self._resize_body()
        self._arrow.set_angle(180.0 if self._expanded else 0.0)

    def _animate_to(self, expanded: bool):
        self._body_anim.stop()
        if expanded:
            self._body.setVisible(True)
            self._body.setMaximumHeight(0)
            self._body_anim.setStartValue(0)
            self._body_anim.setEndValue(self._body_height())
            self._arrow_anim.setDirection(QAbstractAnimation.Forward)
        else:
            self._body_anim.setStartValue(self._body.height())
            self._body_anim.setEndValue(0)
            self._arrow_anim.setDirection(QAbstractAnimation.Backward)
        self._body_anim.start()
        self._arrow_anim.start()

    def _on_body_anim_finished(self):
        if self._expanded:
            self._body.setMaximumHeight(16777215)   # QWIDGETSIZE_MAX
        else:
            self._body.setVisible(False)

    # --------------------------- 文字自定义 ---------------------------
    def set_title(self, title: Optional[Union[QLabel, str]]):
        label = _as_icon_label(title)
        old = self._title_label
        if label is not old:
            header = self._header.layout()
            index = header.indexOf(old) if old is not None else 0
            if old is not None:
                header.removeWidget(old)
                old.setParent(None)
            self._title_label = label
            if label is not None:
                header.insertWidget(index, label, 0, Qt.AlignVCenter)
        self._sync_content_state()

    def title(self) -> Optional[QLabel]:
        return self._title_label

    def set_subtitle(self, text: Optional[str]):
        self._subtitle_label.setText(_normalize_text(text))
        self._sync_content_state()

    def subtitle(self) -> str:
        return self._subtitle_label.text()

    def set_description(self, text: Optional[str]):
        self._desc_label.setText(_normalize_text(text))
        self._sync_content_state()

    def description(self) -> str:
        return self._desc_label.text()

    def header(self) -> PressableRow:
        return self._header

    def body(self) -> QWidget:
        return self._body

    def arrow(self) -> FontIcon:
        return self._arrow


# ============================================================================
#  组件示例（可直接运行：python test.py）
#  ---------------------------------------------------------------------------
#  每个组件一条示例；同样的用法也写在各组件 docstring 的「示例」里。
#  ContentCard 可用下方按钮切换 Wide / Warp / NoIcon / Auto，ShowIcon 恢复图标，并观察三个信号。
# ============================================================================

_DEMO_QSS = """
/* 演示专用：set_style 示例用到的自定义 class（不影响库本身） */
.DemoAccent {
    qproperty-bg_color: #2F5D8C;
    qproperty-border_color: #4C8BF5;
}

/* 层级（level）演示：1 级的内容控件（FontIcon / QLabel 家族）红底，
   便于看到组件把子控件推到了 1 级；Card / Expander 等容器本身不染色，
   这样 Expander 不会整块变红，红色只落在其内部的图标、文字上。
   level 动态属性由 levels.LevelManager 计算。 */
QLabel[level="1"] {
    background-color: #C62828;
}

/* 演示窗口的深色滚动条 */
QScrollBar:vertical {
    background: #1E1E1E;
    width: 12px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #4A4A4A;
    border-radius: 6px;
    min-height: 24px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
"""


def _demo_pixmap(size: int = 56, color: str = "#4C8BF5", text: str = "") -> QPixmap:
    """画一张示例图片，避免演示依赖外部图片文件。"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing, True)
    path = QPainterPath()
    path.addRoundedRect(QRectF(0, 0, size, size), size * 0.24, size * 0.24)
    painter.fillPath(path, QColor(color))

    if text:
        font = painter.font()
        font.setPixelSize(int(size * 0.42))
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor("#FFFFFF"))
        painter.drawText(QRect(0, 0, size, size), Qt.AlignCenter, text)
    painter.end()
    return pixmap


def _demo_section(title: str, description: str = "") -> QWidget:
    """示例区标题。"""
    box = QWidget()
    layout = QVBoxLayout(box)
    layout.setContentsMargins(0, 20, 0, 4)
    layout.setSpacing(2)
    layout.addWidget(TextLabel(title, "#FFFFFF", 16))
    if description:
        layout.addWidget(TextLabel(description, "#9A9A9A", 12))
    return box


def _demo_right_layout(icon: str = "\uE76C") -> QHBoxLayout:
    """ContentCard / Expander 通用的右侧布局示例。"""
    layout = QHBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(fonticon(icon, size=14))
    return layout


def _demo_mode_buttons(card) -> QHBoxLayout:
    """生成切换 ContentCard 显示模式 / 图标显隐的 PressableRow 按钮。"""
    row = QHBoxLayout()
    row.setSpacing(8)

    def add_button(label, on_click):
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(12, 6, 12, 6)
        button_layout.addWidget(TextLabel(label, "#FFFFFF", 13))
        row.addWidget(PressableRow(
            layout=button_layout,
            variant=PressableRow.VARIANT_MENU,
            on_click=on_click))

    for label, mode in (
        ("Wide", ContentCardState.Wide),
        ("Warp", ContentCardState.Warp),
        ("NoIcon", ContentCardState.NoIcon),
        ("Auto", ContentCardState.Auto),
    ):
        add_button(label, lambda m=mode: card.setCardMode(m))
    # 图标显隐独立于宽 / 窄：NoIcon 之后可以用 ShowIcon 重新显示
    add_button("ShowIcon", lambda: card.hideIcon(False))
    row.addStretch(1)
    return row

@dataclass
class _Colors:
    track: QColor
    border: QColor
    thumb: QColor
    label: QColor

    def copy(self) -> "_Colors":
        return _Colors(
            QColor(self.track), QColor(self.border),
            QColor(self.thumb), QColor(self.label)
        )

def _mix_color(a: QColor, b: QColor, t: float) -> QColor:
    """在 sRGB 空间混合两个颜色（包含 alpha）。"""
    t = max(0.0, min(1.0, float(t)))
    return QColor.fromRgbF(
        a.redF() + (b.redF() - a.redF()) * t,
        a.greenF() + (b.greenF() - a.greenF()) * t,
        a.blueF() + (b.blueF() - a.blueF()) * t,
        a.alphaF() + (b.alphaF() - a.alphaF()) * t,
    )

class ToggleSwitch(QAbstractButton):
    """胶囊形开关，支持悬浮和拖动指示器。"""

    stateChanged = Signal(bool)

    # -- 几何尺寸 -----------------------------------------------------------
    _DEFAULT_GAP = 4.0          # 默认态：填充区边缘到指示器边缘
    _DEFAULT_RADIUS_EXTRA = 1.0 # 默认圆形额外增加的半径
    _HOVER_GAP = 2.0            # 悬浮态：填充区边缘到指示器边缘
    _PRESS_STRETCH = 4.0        # 按下时向中间额外拉伸的宽度
    _STRETCH_DURATION = 125     # 按下 / 松开拉伸动画时长（毫秒）
    _HITBOX_PADDING_Y = 8.0     # 碰撞箱上下额外扩展
    _LABEL_GAP = 12.0           # 文字与开关框的间距
    _BORDER_WIDTH = 1.0

    # 兜底颜色：样式表生效前使用，也用于没有加载任何样式表的场景。
    _OFF_TRACK = QColor("#272727")
    _OFF_BORDER = QColor("#9b9da6")
    _OFF_THUMB = QColor("#cecece")
    _OFF_LABEL = QColor("#ffffff")

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        state_text: tuple[str, str] = (get_lang('off'), get_lang('on')),
        checked: bool = False,
        track_width: int = 40,
        track_height: int = 20,
        animation_duration: int = 250,
        easing_curve: QEasingCurve | int = QEasingCurve.OutCubic,
    ) -> None:
        super().__init__(parent)

        if not isinstance(state_text, (tuple, list)) or len(state_text) != 2:
            raise ValueError("state_text 必须是 (关文本, 开文本) 二元组")
        self._off_text, self._on_text = (str(state_text[0]), str(state_text[1]))

        self.setCheckable(True)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setAttribute(Qt.WA_Hover, True)

        # ``track_width`` / ``track_height`` 表示胶囊填充区域尺寸。
        # 1px 边框绘制在填充区外侧，因此默认 track_height=20 时
        # 可见外框高度为 20 + 2px。
        self._track_width = max(32, int(track_width))
        self._track_height = max(12, int(track_height))
        self._border_width = float(self._BORDER_WIDTH)
        self._outer_height = self._track_height + 2.0 * self._border_width
        self._animation_duration = max(0, int(animation_duration))
        self._easing = QEasingCurve(easing_curve)
        self._label_gap = self._LABEL_GAP

        # 计算指示器尺寸
        self._thumb_normal = max(
            1.0,
            self._track_height
            - 2.0 * self._DEFAULT_GAP
            + 2.0 * self._DEFAULT_RADIUS_EXTRA,
        )
        self._thumb_hover = max(1.0, self._track_height - 2.0 * self._HOVER_GAP)
        self._thumb_pressed_w = self._thumb_hover + self._PRESS_STRETCH
        if self._track_width <= self._thumb_pressed_w:
            self._track_width = int(math.ceil(self._thumb_pressed_w)) + 20

        # 字体确定后再测量布局几何
        self._label_width = 0.0
        self._outer_left = 0.0
        self._body_left = 0.0
        self._left_center = 0.0
        self._right_center = 0.0
        self._center = 0.0
        self._geometry_ready = False

        # 交互状态
        self._hovered = False
        self._mouse_down = False
        self._press_mouse_x = 0.0
        self._press_center = 0.0
        self._press_direction = 1.0   # +1：关态向右拉伸；-1：开态向左拉伸
        self._stretch_direction = 1.0
        self._stretch = 0.0
        self._keyboard_focus = False

        # QSS 目标颜色和实际绘制颜色（颜色过渡时使用）
        self._target_colors = _Colors(
            self._OFF_TRACK, self._OFF_BORDER, self._OFF_THUMB, self._OFF_LABEL
        )
        self._display_colors = self._target_colors.copy()
        self._suppress_color_sync = False
        self._repolishing = False

        # 动画对象
        self._slide_anim: QVariantAnimation | None = None
        self._stretch_anim: QVariantAnimation | None = None
        self._color_anim: QVariantAnimation | None = None
        self._color_from = self._display_colors.copy()
        self._color_to = self._display_colors.copy()

        font = QFont(self.font())
        font.setWeight(QFont.Medium)
        self.setFont(font)

        self._set_visual_state("off")
        self.setAccessibleName("开关")

        self._refresh_size()
        self._sync_display_colours()

        # 基类信号还可用于键盘和程序化触发
        self.pressed.connect(self._update_visual_state)
        self.released.connect(self._update_visual_state)
        self.toggled.connect(self._on_toggled)

        if checked:
            self.setChecked(True)

    # ------------------------------------------------------------------ API
    def set_animation_duration(self, milliseconds: int) -> None:
        """设置状态切换动画时长（毫秒，默认 250）。"""
        self._animation_duration = max(0, int(milliseconds))

    def animation_duration(self) -> int:
        return self._animation_duration

    def set_easing_curve(self, curve: QEasingCurve | int) -> None:
        """设置状态切换使用的缓动曲线。"""
        self._easing = QEasingCurve(curve)

    def easing_curve(self) -> QEasingCurve:
        return QEasingCurve(self._easing)

    def set_state_text(self, state_text: tuple[str, str]) -> None:
        """按 ``(关文本, 开文本)`` 设置状态文字。"""
        if not isinstance(state_text, (tuple, list)) or len(state_text) != 2:
            raise ValueError("state_text 必须是 (关文本, 开文本) 二元组")
        self._off_text, self._on_text = (str(state_text[0]), str(state_text[1]))
        self._refresh_size()
        self.update()

    def state_text(self) -> tuple[str, str]:
        return self._off_text, self._on_text

    def sizeHint(self) -> QSize:
        metrics = QFontMetricsF(self.font())
        label_w = math.ceil(max(
            metrics.horizontalAdvance(self._off_text),
            metrics.horizontalAdvance(self._on_text),
        ))
        outer_w = self._track_width + 2.0 * self._border_width
        width = label_w + self._label_gap + outer_w
        height = max(self._outer_height, metrics.height()) + 2 * self._HITBOX_PADDING_Y
        height = int(round(height))
        # 保证轨道上下留白为整数距离。
        if (height - int(round(self._outer_height))) % 2:
            height += 1
        return QSize(int(math.ceil(width)), height)

    def minimumSizeHint(self) -> QSize:
        return self.sizeHint()

    # -- QSS 颜色属性 -------------------------------------------------------
    def _set_target_colour(self, field: str, value) -> None:
        c = QColor(value)
        if c == getattr(self._target_colors, field):
            return
        setattr(self._target_colors, field, c)
        self._on_target_colour_changed()

    def _get_track_color(self) -> QColor:
        return QColor(self._target_colors.track)

    def _set_track_color(self, value) -> None:
        self._set_target_colour("track", value)

    def _get_border_color(self) -> QColor:
        return QColor(self._target_colors.border)

    def _set_border_color(self, value) -> None:
        self._set_target_colour("border", value)

    def _get_thumb_color(self) -> QColor:
        return QColor(self._target_colors.thumb)

    def _set_thumb_color(self, value) -> None:
        self._set_target_colour("thumb", value)

    def _get_label_color(self) -> QColor:
        return QColor(self._target_colors.label)

    def _set_label_color(self, value) -> None:
        self._set_target_colour("label", value)

    # 这些属性由 STYLE_SHEET 中的 qproperty-trackColor 等声明提供。
    trackColor = Property(QColor, _get_track_color, _set_track_color)
    borderColor = Property(QColor, _get_border_color, _set_border_color)
    thumbColor = Property(QColor, _get_thumb_color, _set_thumb_color)
    labelColor = Property(QColor, _get_label_color, _set_label_color)

    # ------------------------------------------------------------------ Qt
    def changeEvent(self, event: QEvent) -> None:
        super().changeEvent(event)
        if event.type() in (QEvent.FontChange, QEvent.StyleChange):
            self._refresh_size()
            if event.type() == QEvent.StyleChange:
                self._sync_display_colours()
            self.update()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._apply_visual_state(force=True)
        self._refresh_size()
        self._sync_display_colours()

    def enterEvent(self, event) -> None:
        super().enterEvent(event)
        if not self._hovered:
            self._hovered = True
            if not self._mouse_down:
                self._stop_color_animation(snap=True)
            self._update_visual_state()
            self.update()

    def focusInEvent(self, event) -> None:
        super().focusInEvent(event)
        self._keyboard_focus = event.reason() in (
            Qt.TabFocusReason,
            Qt.BacktabFocusReason,
            Qt.ShortcutFocusReason,
        )
        self.update()

    def focusOutEvent(self, event) -> None:
        super().focusOutEvent(event)
        self._keyboard_focus = False
        self.update()

    def leaveEvent(self, event) -> None:
        super().leaveEvent(event)
        if self._hovered:
            self._hovered = False
            if not self._mouse_down:
                self._stop_color_animation(snap=True)
            self._update_visual_state()
            self.update()

    def mousePressEvent(self, event) -> None:
        if event.button() != Qt.LeftButton or not self.isEnabled():
            event.ignore()
            return
        if not self.rect().contains(event.position().toPoint()):
            event.ignore()
            return

        # 新的交互会终止正在运行的过渡动画。
        self._stop_slide_animation()
        self._stop_color_animation(snap=True)

        self.setFocus(Qt.MouseFocusReason)
        self._mouse_down = True
        self._press_mouse_x = event.position().x()
        self._press_direction = 1.0 if not self.isChecked() else -1.0
        self._stretch_direction = self._press_direction
        self._press_center = self._center
        self._animate_stretch(1.0)
        self.setDown(True)
        self._update_visual_state()
        self.update()
        event.accept()
        self.pressed.emit()

    def mouseMoveEvent(self, event) -> None:
        if not self._mouse_down:
            event.ignore()
            return
        dx = event.position().x() - self._press_mouse_x
        self._center = self._clamp_base_center(self._press_center + dx)
        self.update()
        event.accept()

    def mouseReleaseEvent(self, event) -> None:
        if event.button() != Qt.LeftButton or not self._mouse_down:
            event.ignore()
            return

        # 拉伸在 125 毫秒内收回，状态切换的滑动和颜色过渡则按各自时长运行。
        self._mouse_down = False
        self._animate_stretch(0.0)
        self.setDown(False)
        self.nextCheckState()
        self._update_visual_state()
        self.update()
        self.released.emit()
        self.clicked.emit()
        event.accept()

    def keyPressEvent(self, event) -> None:
        # 空格 / 回车的键盘行为交给 QAbstractButton 处理。
        if event.key() in (Qt.Key_Space, Qt.Key_Return, Qt.Key_Enter):
            if not event.isAutoRepeat():
                self.update()
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event) -> None:
        super().keyReleaseEvent(event)
        self.update()

    def hitButton(self, pos) -> bool:
        # 整个控件矩形（含左侧文字和上下各 8px 留白）都是碰撞箱。
        point = pos.toPoint() if hasattr(pos, "toPoint") else pos
        return self.rect().contains(point)

    # ------------------------------------------------------------- 几何计算
    def _refresh_size(self) -> None:
        metrics = QFontMetricsF(self.font())
        label_w = math.ceil(max(
            metrics.horizontalAdvance(self._off_text),
            metrics.horizontalAdvance(self._on_text),
        ))
        outer_w = self._track_width + 2.0 * self._border_width
        width = label_w + self._label_gap + outer_w
        height = max(self._outer_height, metrics.height()) + 2 * self._HITBOX_PADDING_Y
        height = int(round(height))
        if (height - int(round(self._outer_height))) % 2:
            height += 1
        hint = QSize(int(math.ceil(width)), height)

        old_size = self.size()
        old_body_left = self._body_left
        if self.size() != hint:
            self.setFixedSize(hint)

        self._label_width = label_w
        self._outer_left = label_w + self._label_gap
        self._body_left = self._outer_left + self._border_width
        self._left_center = self._body_left + self._track_height / 2.0
        self._right_center = (
            self._body_left + self._track_width - self._track_height / 2.0
        )
        self._center += self._body_left - old_body_left

        geometry_changed = (
            old_size != hint or abs(self._body_left - old_body_left) > 0.001
        )
        if not self._geometry_ready:
            self._center = self._right_center if self.isChecked() else self._left_center
            self._geometry_ready = True
        elif (
            geometry_changed
            and self._slide_anim is None
            and self._stretch_anim is None
            and not self._mouse_down
            and self._stretch <= 0.001
        ):
            self._center = self._right_center if self.isChecked() else self._left_center

    def _outer_rect(self) -> QRectF:
        y = (self.height() - self._outer_height) / 2.0
        return QRectF(
            self._outer_left,
            y,
            self._track_width + 2.0 * self._border_width,
            self._outer_height,
        )

    def _body_rect(self) -> QRectF:
        return self._outer_rect().adjusted(
            self._border_width,
            self._border_width,
            -self._border_width,
            -self._border_width,
        )

    def _thumb_metrics(self) -> tuple[float, float, float]:
        """返回当前拉伸量对应的（宽、高、X 偏移）。"""
        stretched = self._hovered or self._mouse_down
        rest = self._thumb_hover if stretched else self._thumb_normal
        s = max(0.0, min(1.0, self._stretch))
        width = rest + (self._thumb_pressed_w - rest) * s
        height = rest + (self._thumb_hover - rest) * s
        offset = (
            self._stretch_direction
            * (self._thumb_pressed_w - self._thumb_hover)
            / 2.0
            * s
        )
        return width, height, offset

    def _thumb_rect(self) -> QRectF:
        track = self._body_rect()
        width, height, offset = self._thumb_metrics()
        center = self._center + offset
        low = track.left() + width / 2.0
        high = track.right() - width / 2.0
        if high < low:
            high = low
        center = max(low, min(high, center))
        return QRectF(
            center - width / 2.0,
            track.center().y() - height / 2.0,
            width,
            height,
        )

    def _clamp_base_center(self, center: float) -> float:
        track = self._body_rect()
        width, _height, offset = self._thumb_metrics()
        low = track.left() + width / 2.0 - offset
        high = track.right() - width / 2.0 - offset
        if high < low:
            high = low
        return max(low, min(high, float(center)))

    def _target_center(self, checked: bool) -> float:
        return self._right_center if checked else self._left_center

    # -------------------------------------------------------------- 颜色状态
    def _set_visual_state(self, state: str) -> None:
        if self.property("visualState") != state:
            self.setProperty("visualState", state)
            self._repolish()

    def _apply_visual_state(self, force: bool = False) -> None:
        if self._mouse_down:
            state = "on-pressed" if self.isChecked() else "off-pressed"
        elif self._hovered:
            state = "on-hover" if self.isChecked() else "off-hover"
        else:
            state = "on" if self.isChecked() else "off"
        if force and self.property("visualState") == state:
            self._repolish()
        else:
            self._set_visual_state(state)

    def _update_visual_state(self) -> None:
        self._apply_visual_state()
        self.update()

    def _repolish(self) -> None:
        if self._repolishing:
            return
        self._repolishing = True
        try:
            self.style().unpolish(self)
            self.style().polish(self)
        finally:
            self._repolishing = False

    def _on_target_colour_changed(self) -> None:
        # 由样式表 qproperty-* setter 在重新 polish 时调用。
        if self._suppress_color_sync:
            return
        if (
            self._color_anim is not None
            and self._color_anim.state() == QVariantAnimation.Running
        ):
            # 运行期间的外部配色变化不应让动画继续追逐旧目标色。
            self._color_to = self._target_colors.copy()
            return
        self._display_colors = self._target_colors.copy()
        self.update()

    def _sync_display_colours(self) -> None:
        if self._suppress_color_sync:
            return
        if self._color_anim is None:
            self._display_colors = self._target_colors.copy()
            self.update()

    # ------------------------------------------------------------ 滑动动画
    def _on_toggled(self, checked: bool) -> None:
        self._refresh_size()
        target_center = self._target_center(checked)

        # 先通知外部状态已经变化，再启动滑动 / 颜色动画，这样在槽函数里
        # 读到的 isChecked() 一定是新状态。
        self.stateChanged.emit(bool(checked))

        # 隐藏状态下直接切换，避免第一次显示时动画已经播放了一部分。
        if not self.isVisible():
            self._stop_slide_animation()
            self._stop_stretch_animation()
            self._stop_color_animation(snap=False)
            self._stretch = 0.0
            self._suppress_color_sync = True
            try:
                self._apply_visual_state(force=True)
                self._center = target_center
                self._display_colors = self._target_colors.copy()
            finally:
                self._suppress_color_sync = False
            self.update()
            return

        start_colors = self._display_colors.copy()
        start_center = self._center

        # 在切换新状态时暂时冻结颜色同步，以便捕获新的目标配色，
        # 然后再向目标颜色插值。
        self._suppress_color_sync = True
        try:
            self._stop_slide_animation()
            self._stop_color_animation(snap=False)
            self._apply_visual_state(force=True)
            target_colors = self._target_colors.copy()
        finally:
            self._suppress_color_sync = False

        if self._animation_duration == 0:
            self._center = target_center
            self._display_colors = target_colors
            self.update()
            return

        if abs(target_center - start_center) > 0.01:
            anim = QVariantAnimation(self)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.setDuration(self._animation_duration)
            anim.setEasingCurve(self._easing)
            anim.valueChanged.connect(
                lambda value: self._on_slide_tick(value, start_center, target_center)
            )
            anim.finished.connect(
                lambda: self._on_slide_finished(target_center)
            )
            self._slide_anim = anim
            anim.start()
        else:
            self._center = target_center
            self.update()

        self._start_color_animation(start_colors, target_colors)

    def _on_slide_tick(self, value, start_center: float, target_center: float) -> None:
        center = start_center + (target_center - start_center) * float(value)
        # OutBack 等缓动曲线可能过冲，这里仍把指示器限制在胶囊内。
        self._center = self._clamp_base_center(center)
        self.update()

    def _on_slide_finished(self, target_center: float) -> None:
        self._center = target_center
        self._slide_anim = None
        self.update()

    def _stop_slide_animation(self) -> None:
        if self._slide_anim is not None:
            anim = self._slide_anim
            self._slide_anim = None
            anim.stop()
            anim.deleteLater()

    # -- 按下 / 松开拉伸 ---------------------------------------------------
    def _animate_stretch(self, target: float) -> None:
        target = max(0.0, min(1.0, float(target)))
        self._stop_stretch_animation()
        start = self._stretch
        if abs(target - start) <= 0.001:
            self._stretch = target
            self.update()
            return

        duration = self._STRETCH_DURATION
        if duration <= 0:
            self._stretch = target
            self.update()
            return

        anim = QVariantAnimation(self)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setDuration(duration)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.valueChanged.connect(
            lambda value: self._on_stretch_tick(value, start, target)
        )
        anim.finished.connect(lambda: self._on_stretch_finished(target))
        self._stretch_anim = anim
        anim.start()

    def _on_stretch_tick(self, value, start: float, target: float) -> None:
        self._stretch = start + (target - start) * float(value)
        self.update()

    def _on_stretch_finished(self, target: float) -> None:
        self._stretch = target
        self._stretch_anim = None
        self.update()

    def _stop_stretch_animation(self) -> None:
        if self._stretch_anim is not None:
            anim = self._stretch_anim
            self._stretch_anim = None
            anim.stop()
            anim.deleteLater()

    def _start_color_animation(self, start: _Colors, target: _Colors) -> None:
        self._stop_color_animation(snap=False)
        self._color_from = start.copy()
        self._color_to = target.copy()
        if self._animation_duration == 0:
            self._display_colors = target.copy()
            self.update()
            return

        anim = QVariantAnimation(self)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setDuration(self._animation_duration)
        anim.setEasingCurve(self._easing)
        anim.valueChanged.connect(self._on_color_tick)
        anim.finished.connect(self._on_color_finished)
        self._color_anim = anim
        anim.start()

    def _on_color_tick(self, value) -> None:
        t = float(value)
        self._display_colors = _Colors(
            _mix_color(self._color_from.track, self._color_to.track, t),
            _mix_color(self._color_from.border, self._color_to.border, t),
            _mix_color(self._color_from.thumb, self._color_to.thumb, t),
            _mix_color(self._color_from.label, self._color_to.label, t),
        )
        self.update()

    def _on_color_finished(self) -> None:
        self._display_colors = self._color_to.copy()
        self._color_anim = None
        self.update()

    def _stop_color_animation(self, snap: bool) -> None:
        if self._color_anim is not None:
            anim = self._color_anim
            self._color_anim = None
            anim.stop()
            anim.deleteLater()
        if snap:
            self._sync_display_colours()

    # --------------------------------------------------------------- 绘制
    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)

        outer = self._outer_rect()
        body = self._body_rect()
        border = self._display_colors.border

        # 1px 边框位于 20px 填充区域外侧。
        if border.alpha() > 0:
            outer_path = QPainterPath()
            outer_path.addRoundedRect(
                outer, outer.height() / 2.0, outer.height() / 2.0
            )
            painter.fillPath(outer_path, border)

        body_path = QPainterPath()
        body_path.addRoundedRect(body, body.height() / 2.0, body.height() / 2.0)
        painter.fillPath(body_path, self._display_colors.track)

        # 圆形指示器。
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._display_colors.thumb)
        painter.drawEllipse(self._thumb_rect())

        # 左侧文字。
        painter.setFont(self.font())
        painter.setPen(self._display_colors.label)
        label_rect = QRectF(
            0.0,
            0.0,
            max(0.0, self._label_width),
            float(self.height()),
        )
        text = self._on_text if self.isChecked() else self._off_text
        painter.drawText(
            label_rect,
            Qt.AlignLeft | Qt.AlignVCenter,
            text,
        )

        if self.hasFocus() and self._keyboard_focus:
            focus_color = QColor(self._display_colors.label)
            focus_color.setAlpha(150)
            focus_pen = QPen(focus_color)
            focus_pen.setWidthF(1.0)
            painter.setPen(focus_pen)
            painter.setBrush(Qt.NoBrush)
            focus_path = QPainterPath()
            fr = body.adjusted(1.5, 1.5, -1.5, -1.5)
            focus_path.addRoundedRect(fr, fr.height() / 2.0, fr.height() / 2.0)
            painter.drawPath(focus_path)

class DevFlagCard(ContentCard):
    """开发标志选择卡片：ContentCard + 中间「代码行」+ 右侧固定 ToggleSwitch。

    与 ContentCard 的区别：
        - 在副标题和描述之间插入一行等宽字体代码：
              副标题 ──2px── 代码行 ──4px── 描述
        - 窄模式（Warp）下是四行：副标题 / 代码行 / 描述 / 右侧 ToggleSwitch；
        - 右侧不可自定义，固定挂载一个 ToggleSwitch（开发标志开关）。

    代码行字体："Consolas", "Courier New", Courier, monospace；
    代码行颜色由 qss 的 .DevFlagCode（qproperty-text_color）决定。

    参数：
        title / subtitle / description —— 同 ContentCard
        code      —— 代码行文字（空字符串时该行连同上下间距一起隐藏）
        checked   —— ToggleSwitch 初始状态
        state_text—— ToggleSwitch 的 (关文本, 开文本)
        wrap_threshold / no_icon_threshold —— 同 ContentCard

    信号：
        flagChanged(bool) —— 右侧 ToggleSwitch 状态变化

    示例：
        card = DevFlagCard(
            title=fonticon("\\uE713", size=20),
            subtitle="Enable experimental renderer",
            code='feature_flags["experimental_renderer"] = True',
            description="开发标志：实验性渲染路径",
        )
        card.flagChanged.connect(lambda checked: print("dev flag:", checked))
    """

    flagChanged = Signal(bool)

    _CODE_COLOR = "#C1C1C1"
    _REQIRE_COLOR = "#fce100"
    _CODE_SIZE = 12
    _CODE_FAMILIES = ["Consolas", "Courier New", "Courier", "monospace"]
    _GAP_SUBTITLE_CODE = 2     # 副标题 ↔ 代码行
    _GAP_CODE_DESC = 4         # 代码行 ↔ 描述

    def __init__(self, title="\uE799", subtitle="副标题文字", code="",
                 description="描述说明文字", items=None, needs_restart=False, checked=False,
                 state_text: tuple[str, str] = (get_lang('off'), get_lang('on')),
                 wrap_threshold=475,
                 no_icon_threshold=100, parent=None):
        super().__init__(
            title=title,
            subtitle=subtitle,
            description=description,
            right_layout=None,
            wrap_threshold=wrap_threshold,
            no_icon_threshold=no_icon_threshold,
            parent=parent,
        )

        self.items = [] if items is None else items # 项目列表

        # ================= 代码行：副标题 -2px- 代码 -4px- 描述 =================
        self._code_label = TextLabel(code, self._CODE_COLOR, self._CODE_SIZE)
        _prep_text_label(self._code_label)
        code_font = self._code_label.font()
        code_font.setFamilies(self._CODE_FAMILIES)
        self._code_label.setFont(code_font)

        self._reqires_label = TextLabel('', self._REQIRE_COLOR, self._CODE_SIZE)
        _prep_text_label(self._reqires_label)

        self._restart_label = TextLabel('This flag need to restart the application.', self._REQIRE_COLOR, self._CODE_SIZE)
        _prep_text_label(self._restart_label)

        set_style(self._code_label, "DevFlagCode")
        set_style(self._reqires_label, "DevFlagRequire")
        set_style(self._restart_label, "DevFlagRequire")

        self._reqires_label.setVisible(bool(self.items))
        self._restart_label.setVisible(needs_restart)

        self._reqires_label.setText(f'Requires: {",".join(self.items)}')

        # ContentCard 的中间列默认 spacing=2，这里改为显式的 2px / 4px 间隔
        self._mid_layout.setSpacing(0)
        self._mid_layout.removeWidget(self._subtitle_label)
        self._mid_layout.removeWidget(self._desc_label)
        self._gap_subtitle_code = QSpacerItem(
            0, self._GAP_SUBTITLE_CODE, QSizePolicy.Minimum, QSizePolicy.Fixed)
        self._gap_code_desc = QSpacerItem(
            0, self._GAP_CODE_DESC, QSizePolicy.Minimum, QSizePolicy.Fixed)
        self._gap_desc_reqires = QSpacerItem(
            0, self._GAP_CODE_DESC, QSizePolicy.Minimum, QSizePolicy.Fixed)
        self._gap_requires_restart = QSpacerItem(
            0, self._GAP_CODE_DESC, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self._mid_layout.addWidget(self._subtitle_label, 1, Qt.AlignVCenter)
        self._mid_layout.addItem(self._gap_subtitle_code)
        self._mid_layout.addWidget(self._code_label, 0, Qt.AlignVCenter)
        self._mid_layout.addItem(self._gap_code_desc)
        self._mid_layout.addWidget(self._desc_label, 1, Qt.AlignVCenter)
        self._mid_layout.addItem(self._gap_desc_reqires)
        self._mid_layout.addWidget(self._reqires_label, 1, Qt.AlignVCenter)
        self._mid_layout.addItem(self._gap_requires_restart)
        self._mid_layout.addWidget(self._restart_label, 1, Qt.AlignVCenter)

        # ================= 右侧固定 ToggleSwitch（不可自定义） =================
        self._toggle_switch = ToggleSwitch(
            self._right_container, checked=checked, state_text=state_text)
        toggle_layout = QHBoxLayout(self._right_container)
        toggle_layout.setContentsMargins(0, 0, 0, 0)
        toggle_layout.setSpacing(0)
        toggle_layout.addWidget(self._toggle_switch, 0, Qt.AlignVCenter)
        self._toggle_switch.stateChanged.connect(self._on_toggle_changed)
        self._apply_right_margins_for_mode()

        self._has_code = True
        self._sync_content_state()

    # --------------------------- 状态同步 ---------------------------
    def _on_toggle_changed(self, checked: bool) -> None:
        self.flagChanged.emit(bool(checked))

    def _sync_content_state(self):
        super()._sync_content_state()
        if not hasattr(self, "_code_label"):
            return   # ContentCard.__init__ 阶段代码行还没创建

        self._has_code = _has_visual_content(self._code_label)
        self._code_label.setVisible(self._has_code)
        gap1 = self._GAP_SUBTITLE_CODE if self._has_code else 0
        gap2 = self._GAP_CODE_DESC if self._has_code else 0
        self._gap_subtitle_code.changeSize(
            0, gap1, QSizePolicy.Minimum, QSizePolicy.Fixed)
        self._gap_code_desc.changeSize(
            0, gap2, QSizePolicy.Minimum, QSizePolicy.Fixed)

        # 代码行是唯一内容时，中间列不能按空内容塌缩
        if self._has_code and self._mid_empty:
            self._mid_empty = False
            self._apply_right_margins_for_mode()
            self._update_layout_mode()
            self.updateGeometry()

    # --------------------------- 右侧固定 ---------------------------
    def set_right_layout(self, layout):
        """DevFlagCard 右侧固定为 ToggleSwitch，禁止自定义。"""
        raise AttributeError("DevFlagCard 的右侧固定为 ToggleSwitch，不能自定义 right_layout")

    def toggle_switch(self) -> ToggleSwitch:
        return self._toggle_switch

    def is_checked(self) -> bool:
        return self._toggle_switch.isChecked()

    def set_checked(self, checked: bool) -> None:
        self._toggle_switch.setChecked(bool(checked))

    # --------------------------- 代码行 ---------------------------
    def code(self) -> str:
        return self._code_label.text()

    def set_code(self, text: str) -> None:
        self._code_label.setText(_normalize_text(text))
        self._sync_content_state()
