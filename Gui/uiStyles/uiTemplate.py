from uiStyles.QUI import *
from uiStyles.widgets import VScrollArea

__all__ = ['SelectUI', 'PagesUI']

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
        self.left_scroll = QScrollArea()
        main_layout.addWidget(self.left_scroll, 1)  # 拉伸系数为1
        
        # 创建右侧滚动区域
        self.right_scroll = VScrollArea()
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
   
class PagesUI(QMainWindow):
    '''分页窗口类'''
    def __init__(self, pages: list[str]):
        super().__init__()
        
        # 页面索引
        self.total_pages = 0
        self.current_page = 0
        
        self.set_pages(pages)
        self.init_ui()
        self.update_buttons()
        self.init_pages()
        
    def set_pages(self, pages: list[str]):
        '''设置页面'''
        for index, page in enumerate(pages):
            self.__setattr__(f'PAGE_{page}', index)
            self.total_pages += 1
        
    def init_ui(self):
        '''初始化UI'''
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)  # 移除边距
        main_layout.setSpacing(0)  # 移除间距
        
        # 页面堆叠控件
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        # 按钮布局
        self.button_layout = QHBoxLayout()
        self.button_layout.addStretch(0)
        
        # 上一步按钮
        self.prev_btn = QPushButton('上一步')
        self.prev_btn.clicked.connect(self.on_prev)
        self.button_layout.addWidget(self.prev_btn)
        
        # 下一步按钮
        self.next_btn = QPushButton('下一步')
        self.next_btn.clicked.connect(self.on_next)
        self.button_layout.addWidget(self.next_btn)
        
        # 取消/完成按钮容器（重叠放置）
        self.action_button_container = QWidget()
        self.action_button_layout = QHBoxLayout(self.action_button_container)
        
        # 取消按钮
        self.cancel_btn = QPushButton('取消')
        self.cancel_btn.clicked.connect(self.close)
        self.action_button_layout.addWidget(self.cancel_btn)
        
        # 完成按钮
        self.finish_btn = QPushButton('完成')
        self.finish_btn.clicked.connect(self.close)
        self.action_button_layout.addWidget(self.finish_btn)
        
        self.button_layout.addWidget(self.action_button_container)
        
        main_layout.addLayout(self.button_layout)
        
    def update_buttons(self):
        '''更新按钮的显示/隐藏状态'''
        if (self.current_page == self.total_pages - 1):
            # 最后一页正常页面：只显示完成按钮
            self.prev_btn.setVisible(False)
            self.next_btn.setVisible(False)
            self.cancel_btn.setVisible(False)
            self.finish_btn.setVisible(True)
        else:
            # 正常页面：显示上一步、下一步、取消
            self.prev_btn.setVisible(self.current_page != 0)
            self.next_btn.setVisible(True)
            self.cancel_btn.setVisible(True)
            self.finish_btn.setVisible(False)
            
    def draw_page(self):
        '''绘制页面内容'''
        self.stacked_widget.setCurrentIndex(self.current_page)
        
    def init_pages(self):
        '''初始化页面'''
        for i in range(self.total_pages):
            self.stacked_widget.addWidget(self.show_page(i))
            
    def show_page(self, page_index: int):
        '''显示指定页面'''
        page_widget = QWidget()
        page_layout = QVBoxLayout(page_widget)
        
        page_layout.addStretch(1)
        return page_widget
        
    def on_prev(self):
        '''切换到上一页'''
        self.set_page(self.current_page - 1)
    
    def on_next(self):
        '''切换到下一页'''
        self.set_page(self.current_page + 1)
    
    def set_page(self, index):
        '''切换到取消页面'''
        self.current_page = index
        self.draw_page()
        self.update_buttons()
