# from uiStyles.QUI import *
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import ctypes # 用于获取系统风格
from sharelibs import get_lang, default_button_text

__all__ = ['UMessageBox', 'VScrollArea', 'HScrollArea', 'UCheckBox', 'UnitInputLayout', 'ULabel', 'MessageButton', 'CustonMessageButton', 'MessageIcon']

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
    def infomation(cls, parent: QWidget | None, title: str, text: str, buttons: MessageButton = None, defaultButton: MessageButton = None):
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
    def __init__(self, parent=None):
        super().__init__(parent)
        self._item_list = []      # 存储所有子项
        self._row_breaks = []     # 记录每行结束的索引位置（记录上一行最后一个项的索引）
        self.setContentsMargins(0, 0, 0, 0)

    def addItem(self, item: QLayoutItem):
        '''添加子项到列表末尾'''
        self._item_list.append(item)

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
        '''核心方法，按行排列所有子项'''
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
        
        x = available_rect.x()
        y = available_rect.y()
        spacing = self.spacing()
        
        # 获取按行分组的子项
        rows = self._get_rows()
        
        # 遍历每一行
        for row_items in rows:
            if not row_items:
                continue
                
            # 计算当前行所有子项的总宽度（包括间距）
            total_items_width = sum(item.sizeHint().width() for item in row_items)
            total_spacing = spacing * (len(row_items) - 1)
            available_width = available_rect.width()
            
            # 计算当前行的最大高度
            row_height = max(item.sizeHint().height() for item in row_items)
            
            # 如果行内总宽度超过可用宽度，按比例压缩
            if total_items_width + total_spacing > available_width:
                scale_factor = available_width / (total_items_width + total_spacing)
                row_x = x
                for item in row_items:
                    hint = item.sizeHint()
                    item_width = int(hint.width() * scale_factor)
                    item_height = int(hint.height() * scale_factor)
                    # 垂直居中
                    item_y = y + (row_height - item_height) // 2
                    item.setGeometry(QRect(row_x, item_y, item_width, item_height))
                    row_x += item_width + spacing
            else:
                # 正常排列，保持原大小
                row_x = x
                for item in row_items:
                    hint = item.sizeHint()
                    # 垂直居中
                    item_y = y + (row_height - hint.height()) // 2
                    item.setGeometry(QRect(row_x, item_y, hint.width(), hint.height()))
                    row_x += hint.width() + spacing
            
            # 换行：更新y坐标，重置x坐标
            y += row_height + spacing

    def addUnitRow(self, text: str, input: QLineEdit, unit: QComboBox):
        '''添加单位选择控件'''
        self.newRow() # 换行
        self.addWidget(QLabel(text + ': '))
        self.addWidget(input)
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
