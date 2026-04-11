from uiStyles.QUI import *
from uiStyles.widgets import VScrollArea

__all__ = ['SelectUI']

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
