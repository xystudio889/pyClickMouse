# from uiStyles.QUI import *
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import ctypes # 用于获取系统风格
from sharelibs import get_lang, default_button_text, set_style
from typing import Optional, Union
import sys

__all__ = ['UMessageBox', 'VScrollArea', 'HScrollArea', 'UCheckBox', 'UnitInputLayout', 'ULabel', 'MessageButton', 'CustonMessageButton', 'MessageIcon', 'HighLightPanel', 'fonticon', 'icon_img', 'IconImage', 'TextLabel', 'Card', 'ContentCard', 'PressableRow', 'Expander', 'create_expander_row']

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


class HighLightPanel(QWidget):
    """背景 #272727，左上角 8px 圆角，内容四周 36px 留白

    配色：底色默认值见 BG，可由 qss 里的 `.HighLightPanel { qproperty-bg_color: ... }` 覆盖
          （临时配色表见 Gui/a.qss）；圆角、留白等形状属性仍由代码控制。
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

    字号通过「控件自身样式表」设置：全局样式表里的 `* { font-size: ... }`
    会覆盖 setFont()，但覆盖不了控件自身样式表，因此图标字号不会被带跑。
    """

    def __init__(self, icon="", size: int = 20, color: str = "#FFFFFF", parent=None):
        super().__init__(icon, parent)

        self._color = QColor(color)
        self._icon_size = int(size)
        self._angle = 0.0

        self.setAlignment(Qt.AlignCenter)
        self.setMinimumWidth(0)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        self._apply_style()

        self._pixmap = None
        self._pixmap_key = None

    def _apply_style(self):
        """把字号 + 颜色写进控件自身样式表（优先级高于全局 `*` 规则）。"""
        f = self.font()
        f.setPixelSize(self._icon_size)
        f.setFamilies(_FONT_FAMILIES)
        self.setFont(f)
        self.setStyleSheet(
            f"color: {self._color.name()}; background: transparent; "
            f"font-size: {self._icon_size}px;"
        )
        self.updateGeometry()

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
        return self._color

    def set_icon_color(self, color):
        color = QColor(color)
        if color != self._color:
            self._color = color
            # 旋转时由 self._color 自绘；未旋转时 QLabel 取自身样式表的颜色
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
        dpr = self.devicePixelRatioF()
        key = (self.size(), self.text(), self.font().key(), self._color.rgba(), dpr)
        if self._pixmap is None or self._pixmap_key != key:
            pm = QPixmap(int(self.width() * dpr), int(self.height() * dpr))
            pm.setDevicePixelRatio(dpr)
            pm.fill(Qt.transparent)

            painter = QPainter(pm)
            painter.setRenderHint(QPainter.Antialiasing, True)
            painter.setRenderHint(QPainter.TextAntialiasing, True)
            painter.setPen(self._color)
            painter.setFont(self.font())
            painter.drawText(QRect(QPoint(0, 0), self.size()), Qt.AlignCenter, self.text())
            painter.end()

            self._pixmap = pm
            self._pixmap_key = key
        return self._pixmap

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


def fonticon(icon="", size: int = 20, color: str = "#FFFFFF") -> FontIcon:
    """新建一个 fonticon 处理后的 QLabel（图标字体 + 居中 + 透明背景）。"""
    return FontIcon(icon, size=size, color=color)


class IconImage(QLabel):
    """内嵌图片图标（QLabel + QPixmap）。

    与 FontIcon（图标字体）不同，它不依赖图标字体，图片直接内嵌在控件里，
    因此完全不受全局 `* { font-size / font-family }` 之类规则影响。

    参数：
        image —— QPixmap / QIcon / 图片文件路径；None 表示暂无图片
        size  —— 目标尺寸：int（正方形）或 QSize；None 表示按原图尺寸
    """

    def __init__(self, image=None, size=None, parent=None):
        super().__init__(parent)

        self._source = QPixmap()      # 原图
        self._icon_size = QSize()     # 空 QSize 表示按原图
        self._angle = 0.0

        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("background: transparent;")
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
    """新建一个内嵌图片图标（QLabel + QPixmap，不受全局字体规则影响）。"""
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
    并可由 qss 里的 `qproperty-text_color` / `qproperty-text_size` 覆盖（见 Gui/a.qss）。
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
        self.setStyleSheet(
            f"color: {self._text_color.name()}; background: transparent; "
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


class Card(QWidget):
    """基础卡片：只负责背景、圆角与边框，并挂载一个外部布局。

    参数：
        layout —— 要挂载到卡片上的布局（None 则只是一块背景板）。
                  布局的边距 / 间距完全由调用方决定，Card 不做干预。

    配色：底色 / 边框色的默认值见 _BG、_BORDER，可由 qss 里的
          `.Card { qproperty-bg_color: ...; qproperty-border_color: ...; }` 覆盖
          （临时配色表见 Gui/a.qss）；圆角、边框宽度等形状属性仍由代码控制。
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

        pen = QPen(self._border_color)
        pen.setWidthF(self._border_width)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        inner = rect.adjusted(0.5, 0.5, -0.5, -0.5)
        painter.drawRoundedRect(inner, self._radius, self._radius)


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
    """

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
        self._mid_container.setStyleSheet("background: transparent;")
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
        self._right_container.setStyleSheet("background: transparent;")
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

    def _update_layout_mode(self):
        if self._suspend:
            return

        width = self.width()

        self._suspend = True
        try:
            # --- 图标可见性：无 title 时等同于「无图标模式」 ---
            show_icon = self._has_title and width >= self._no_icon_threshold
            if self._title_label is not None and show_icon != self._icon_visible:
                self._title_label.setVisible(show_icon)
                self._icon_visible = show_icon
            # 图标隐藏（或被隐藏的中间列）时不再需要 24px 左缩进
            left = self._ICON_GAP if (show_icon and not self._mid_empty) else 0
            m = self._mid_layout.contentsMargins()
            if m.left() != left:
                self._mid_layout.setContentsMargins(left, m.top(), m.right(), m.bottom())
        finally:
            self._suspend = False

        # --- 压缩模式阈值（固定常数，无抖动） ---
        # 中间列没有文字时无需换行，始终保持宽模式
        if self._mid_empty:
            self._switch_mode(False)
        elif not self._is_narrow:
            if width < self._wrap_threshold:
                self._switch_mode(True)
        elif width >= self._wrap_threshold:
            self._switch_mode(False)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_layout_mode()

    def showEvent(self, event):
        super().showEvent(event)
        self._update_layout_mode()


class PressableRow(Card):
    """可按下的一行（下拉按钮 / 下拉菜单项）：悬浮与按下变色，释放时触发槽函数。

    参数：
        layout   —— 行内布局（挂载到 Card 上，边距由调用方决定）
        on_click —— 释放时调用的槽函数；也可以连接 clicked 信号

    配色：普通 / 悬浮 / 按下三套颜色都在 qss 里（.PressableRow / .PressableRowHover /
          .PressableRowPressed，见 Gui/a.qss），代码只按状态调用 set_style 切换 class。
    """

    clicked = Signal()

    STYLE_CLASS = "PressableRow"
    HOVER_CLASS = "PressableRowHover"
    PRESSED_CLASS = "PressableRowPressed"

    _BG = "#343434"        # 默认配色（qss 未加载时的兜底值）
    _BORDER = "#232323"

    def __init__(self, layout=None, on_click=None, parent=None):
        # 底下的 Card.__init__ 会读取 self._BG / self._BORDER，并按 STYLE_CLASS 上色
        super().__init__(layout=layout, parent=parent)

        self._on_click = on_click
        self._hover = False
        self._pressed = False

        # 背景自绘，置为透明以免被父级样式表覆盖
        self.setStyleSheet("background: transparent;")
        self.setCursor(Qt.PointingHandCursor)

    # --------------------------- 交互 ---------------------------
    def set_on_click(self, on_click):
        self._on_click = on_click

    def _sync_state_class(self):
        """按当前状态切换样式 class（颜色定义在 qss 里）。"""
        if self._pressed:
            set_style(self, self.PRESSED_CLASS)
        elif self._hover:
            set_style(self, self.HOVER_CLASS)
        else:
            set_style(self, self.STYLE_CLASS)

    def enterEvent(self, event):
        self._hover = True
        self._sync_state_class()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hover = False
        self._pressed = False
        self._sync_state_class()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._pressed = True
            self._sync_state_class()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self._pressed:
            self._pressed = False
            self._sync_state_class()
            if self.rect().contains(event.position().toPoint()):
                self.trigger()
        super().mouseReleaseEvent(event)

    def trigger(self):
        """触发一次按下（供代码或测试调用）。"""
        self.clicked.emit()
        if self._on_click is not None:
            self._on_click()


class _Divider(QFrame):
    """下拉内容之间的 1px 分割线。

    颜色默认值见 _COLOR，可由 qss 里的
    `.ExpanderDivider { qproperty-color: ... }` 覆盖（见 Gui/a.qss）。
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

def add_smart(layout, obj):
    if isinstance(obj, QWidget):
        layout.addWidget(obj)
    elif isinstance(obj, QLayout):
        layout.addLayout(obj)
    elif isinstance(obj, QLayoutItem):
        layout.addItem(obj)
    else:
        raise TypeError(f"add_smart not supported type: {type(obj).__name__}")

def create_expander_row(left_widget, right_widget, press_command=None) -> PressableRow | QLayout:
    '''
    创建一个两边布局的项目

    参数：
        left_widget   —— 左侧组件
        right_widget  —— 右侧组件
        press_command —— 按下的操作，为None不注册
    '''
    layout = QHBoxLayout()
    layout.setContentsMargins(60, 20, 45, 20)

    add_smart(layout, left_widget)
    layout.addStretch()
    add_smart(layout, right_widget)

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
                        （例如 PressableRow，按下触发槽函数）；相邻两项间自动插入
                        1px 分割线
        expanded     —— 初始是否展开（默认收起）
        duration     —— 展开 / 收起动画时长（ms），<= 0 表示立即切换
        right_layout —— 自定义右侧布局（可选），放在下拉箭头左侧，间隔 8px；
                        用法与 ContentCard 的 right_layout 一致

    配色：下拉区底色 / 文字 / 箭头 / 分割线的颜色都在 qss 里
          （.Expander、.ExpanderSubtitle、.ExpanderDescription、.ExpanderArrow、
          .ExpanderDivider，见 Gui/a.qss），代码只用 set_style 挂 class，
          具体颜色值不写在代码里（默认值仅作 qss 未加载时的兜底）。

    布局（不随宽度自适应缩放）：
        16px │ 图标(跨两行) 20px 标题 ···· [右侧布局] 8px 箭头(居右) │ 16px
             │                      8px
             │                      描述
        16px
    （图标、文字列、右侧布局、箭头都在竖直方向居中）
    """

    _PAD = 16              # 上下左右内边距
    _GAP = 4               # 基础间距
    _ICON_GAP = 20         # 图标 ↔ 文字列
    _ROW_GAP = 2    # 8px（2 个 Gap），标题 ↔ 描述
    _RIGHT_GAP = 8         # 右侧布局 ↔ 箭头
    _DURATION = 250        # 展开 / 收起动画时长
    _ARROW_ICON = "\uE70D"
    _ARROW_COLOR = "#F7F7F7"     # 默认配色，可由 qss 的 .ExpanderArrow 覆盖
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
        self._arrow = fonticon(self._ARROW_ICON, size=self._ARROW_SIZE, color=self._ARROW_COLOR)
        set_style(self._arrow, self.ARROW_CLASS)

        self._header = PressableRow(layout=self._build_header_layout(subtitle, description),
                                    on_click=self.toggle, parent=self)
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
        self._text_container.setStyleSheet("background: transparent;")
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
        self._right_container.setStyleSheet("background: transparent;")
        self._right_container.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        self._right_container.setMinimumWidth(0)

        # 箭头容器：只在有右侧布局时留出 8px，避免箭头被推离右边缘
        self._arrow_container = QWidget()
        self._arrow_container.setStyleSheet("background: transparent;")
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
        self._body.setStyleSheet("background: transparent;")
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
        return self._body_layout.sizeHint().height()

    def _resize_body(self):
        """收起时高度锁 0，展开时按内容高度。"""
        self._body.setMaximumHeight(self._body_height() if self._expanded else 0)

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
