from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *
import sys

class SelectUI(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()

        self.page_choice_buttons = [] # 用于存储页面选择按钮文字
        self.buttons = []  # 用于存储所有按钮对象
        self.stacked_widget = None  # 右侧堆叠窗口部件
        self.pages = []  # 用于存储所有页面

        self.init_base_ui()
    
    def init_base_ui(self):
        '''创建基础UI'''
        # 创建中心部件和主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # 设置两个滚动区域之间的间距为15像素
        main_layout.setSpacing(15)
        
        # 创建左侧滚动区域
        self.left_scroll = self.create_scroll_area()
        main_layout.addWidget(self.left_scroll, 1)  # 拉伸系数为1
        
        # 创建右侧滚动区域
        self.right_scroll = self.create_scroll_area()
        main_layout.addWidget(self.right_scroll, 5)  # 拉伸系数为5
        
    def init_ui(self):
        '''创建设置界面'''
        self.draw_page_choice()
        self.init_right_pages()
        
    def draw_page_choice(self):
        '''绘制左侧页面选择'''
        content = QWidget()
        content_layout = QVBoxLayout(content)
        
        # 为每个页面创建按钮
        for i, page_title in enumerate(self.page_choice_buttons):
            button = QPushButton(page_title)
            # 连接按钮点击信号到槽函数
            button.clicked.connect(lambda checked, idx=i: self.on_page_button_clicked(idx))
            content_layout.addWidget(button)
            self.buttons.append(button)
        
        # 添加一个弹簧，让按钮靠上显示
        content_layout.addStretch()
        
        self.left_scroll.setWidget(content)
    
    def init_right_pages(self):
        '''初始化右侧设置页面'''
        # 创建堆叠窗口部件
        self.stacked_widget = QStackedWidget()
        
        # 为每个左侧选项创建一个对应的右侧页面
        for i, page_title in enumerate(self.page_choice_buttons):
            page = self.create_setting_page(page_title)
            self.stacked_widget.addWidget(page)
            self.pages.append(page)
        
        # 将堆叠窗口部件设置为右侧滚动区域的内容
        self.right_scroll.setWidget(self.stacked_widget)
    
    def create_setting_page(self, title):
        '''创建设置页面'''
        # 添加：
        # page = QWidget()
        # layout = QVBoxLayout(page)
        
        # # 标题标签
        # title_label = QLabel(title)
        # title_label.setStyleSheet(replace_style_sheet(big_title, 'font-size', '16px', '24px'))
        # layout.addWidget(title_label)
        
        # # 内容标签
        # content_label = QLabel('该设置暂无描述')
        # content_label.setStyleSheet('color: gray;font-size: 16px;')
        # layout.addWidget(content_label)

        # def set_content_label(text):
        #     content_label.setText(text)
        # 请在下方添加窗口显示
        # 例如：
        # match title:
        #     case '页面1':
        #         set_content_label('页面1的内容')
        #     case '页面2':
        #         set_content_label('页面2的内容')
        #...
        # 然后输入：
        # layout.addStretch()
        # return page
        pass
    
    def create_scroll_area(self):
        '''创建滚动区域'''
        # 创建滚动区域
        scroll_area = QScrollArea()
        
        # 限制滚动方向（只能上下滚动）
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 始终禁用水平滚动条
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)     # 按需显示垂直滚动条
        
        return scroll_area

class VScrollArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 隐藏横向滚动条
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

class HScrollArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 隐藏纵向滚动条
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

class UnitInputLayout(QLayout):
    def __init__(self, parent=None, spacing=10):
        super().__init__(parent)
        self._item_list = []      # 存储所有子项
        self._row_breaks = []     # 记录每行结束的索引位置（记录上一行最后一个项的索引）
        self.setSpacing(spacing)  # 设置间距

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
                # 正常排列，保持原大小，可以水平居中
                row_x = x + (available_width - (total_items_width + total_spacing)) // 2
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
