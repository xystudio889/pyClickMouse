import wx

class Style:
    DEFAULT = 0b1
    OK = 0b10
    CANCEL = 0b100
    YES = 0b1000
    NO = 0b10000
    YESNO = YES | NO
    OKCANCEL = OK | CANCEL
    YESNOCANCEL = YES | NO | CANCEL
    INFO = 0b100000
    QUESTION = 0b1000000
    WARNING = 0b10000000
    ERROR = 0b100000000
    

class MoreButtonDialog(wx.Dialog):
    def __init__(self, parent, title:str, message:str, buttons:list, msgbox_style=Style.DEFAULT, window_style=wx.DEFAULT_DIALOG_STYLE):
        super().__init__(parent, title=title, style=window_style, size=(300, 300))
        
        self.msgbox_style = msgbox_style
        sizer = wx.BoxSizer(wx.VERTICAL)
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        title_sizer = wx.BoxSizer(wx.HORIZONTAL)
        icon = self.parse_box_icon()
        if icon is not None:
            title_sizer.Add(wx.StaticBitmap(self, bitmap=wx.ArtProvider.GetBitmap(icon, wx.ART_MESSAGE_BOX, (32, 32))), 0, wx.ALL, 15)
        else:
            title_sizer.AddSpacer(15)
        title_sizer.Add(wx.StaticText(self, label=message), 0, wx.ALL, 15)
        
        self.button_text_list = buttons.copy()
        self.buttons_text_list = self.parse_button_style()
        self.buttons = []
        for i, btn_text in enumerate(self.buttons_text_list):
            btn = wx.Button(self, wx.ID_ANY, btn_text)
            btn.Bind(wx.EVT_BUTTON, lambda evt, idx=i: self.EndModal(idx))
            btn_sizer.Add(btn)
            self.buttons.append(btn)

        sizer.Add(title_sizer, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(sizer)
        self.Fit()
    
    def parse_box_icon(self):
        if self.msgbox_style & Style.INFO:
            return wx.ART_INFORMATION
        elif self.msgbox_style & Style.QUESTION:
            return wx.ART_QUESTION
        elif self.msgbox_style & Style.WARNING:
            return wx.ART_WARNING
        elif self.msgbox_style & Style.ERROR:
            return wx.ART_ERROR
        else:
            return None
    
    def parse_button_style(self):
        buttons = self.button_text_list.copy()
        if self.msgbox_style & Style.YES:
            buttons.append("是")
        if self.msgbox_style & Style.NO:
            buttons.append("否")   
        if self.msgbox_style & Style.CANCEL:
            buttons.append("取消")
        if self.msgbox_style & Style.OK:
            buttons.append("确定")
        return buttons

class SelectUI(wx.Dialog):
    def __init__(self, title, size, parent=None, **kwargs):
        super().__init__(parent, title=title, size=size, **kwargs)
        self.setting_font = wx.Font(wx.FontInfo().FaceName('Microsoft YaHei UI').Bold(False))
        
        # 初始化主界面
        self.main_panel = wx.Panel(self)
        
        # 使用布局管理器
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        setting_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # 创建左侧按钮面板（立即初始化sizer）
        self.button_panel = wx.Panel(self.main_panel)
        button_sizer = wx.BoxSizer(wx.VERTICAL)  # 先创建sizer
        self.button_panel.SetSizer(button_sizer)  # 立即设置到面板
        # 设置按钮样式
        self.button_panel.SetWindowStyle(wx.BORDER_SIMPLE)
        self.button_panel.SetBackgroundColour(wx.WHITE)
        
        # 创建右侧内容面板（立即初始化sizer）
        self.content_panel = wx.Panel(self.main_panel)
        self.content_sizer = wx.BoxSizer(wx.VERTICAL)
        self.content_panel.SetSizer(self.content_sizer)

        # 初始化页面和按钮
        self.pages = []
        self.buttons = []
        self.page_titles = []
        
        # 设置布局比例（左侧1:右侧5）
        setting_sizer.Add(self.button_panel, 1, wx.EXPAND | wx.ALL, 5)
        setting_sizer.Add(self.content_panel, 5, wx.EXPAND | wx.ALL, 5)
        
        self.main_sizer.Add(setting_sizer, 7, wx.EXPAND | wx.ALL, 0)
        
        # 应用布局
        self.main_panel.SetSizer(self.main_sizer)

    def create_pages(self):
        '''创建页面内容和对应按钮'''
        for index, title in enumerate(self.page_titles):
            # 创建内容页面
            page = wx.Panel(self.content_panel)
            self.pages.append(page)
            self.content_panel.GetSizer().Add(page, 1, wx.EXPAND)
            page.Hide()
            
            # 创建对应按钮
            btn = wx.Button(self.button_panel, label=title, size=wx.Size(70, 30)) 
            btn.Bind(wx.EVT_BUTTON, lambda evt, idx=index: self.switch_page(idx))
            self.buttons.append(btn)
            self.button_panel.GetSizer().Add(btn, 0, wx.EXPAND | wx.ALL, 0)

    def draw_page(self, index):
        '''根据索引绘制页面内容'''
        pass

    def switch_page(self, index):
        '''切换页面并更新按钮状态'''
        # 隐藏所有页面
        for page in self.pages:
            page.Hide()
            
        # 显示选中页面
        self.pages[index].Show()
        self.draw_page(index)
        
        # 更新按钮样式
        for i, btn in enumerate(self.buttons):
            color = wx.SystemSettings.GetColour(wx.SYS_COLOUR_ACTIVECAPTION) if i == index else None
            btn.SetBackgroundColour(color)
        # 调整布局
        self.content_sizer.Layout()
        
class PagesUI(wx.Frame):
    '''页面UI样式'''
    def __init__(self, title, size, parent=None, **kwargs):
        super().__init__(parent, title=title, size=size, **kwargs)
        # 初始化
        self.pages = []
        self.current_page = 0
        self.next_page = 0
        self.total_pages = 0
        
        # 主面板
        self.main_panel = wx.Panel(self)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 创建内容面板容器
        self.content_panel = wx.Panel(self.main_panel)
        self.content_sizer = wx.BoxSizer(wx.VERTICAL)
        self.content_panel.SetSizer(self.content_sizer)
        
        # 创建按钮面板
        self.btn_panel = wx.Panel(self.main_panel)
        
        # 创建按钮
        self.btn_prev = wx.Button(self.btn_panel, label='上一步', pos = (0,5))
        self.btn_next = wx.Button(self.btn_panel, label='下一步', pos = (100, 5))
        self.btn_cancel = wx.Button(self.btn_panel, label='取消', pos = (200, 5))
        self.btn_exit = wx.Button(self.btn_panel, label='退出', pos = (200, 5))
        self.btn_exit.Hide()
        
        # 主布局调整
        self.main_panel.SetSizer(self.main_sizer)
        
        # 绑定事件
        self.btn_prev.Bind(wx.EVT_BUTTON, self.on_prev)
        self.btn_next.Bind(wx.EVT_BUTTON, self.on_next)
        self.btn_cancel.Bind(wx.EVT_BUTTON, self.on_close)
        self.btn_exit.Bind(wx.EVT_BUTTON, self.on_close)
            
        self.Bind(wx.EVT_CLOSE, self.on_close)
        
    def init_show(self):
        """初始化显示框架结构"""
        self.content = self.main_sizer.Add(self.content_panel, 5, wx.EXPAND)
        self.btn = self.main_sizer.Add(self.btn_panel, 1, wx.ALIGN_RIGHT | wx.BOTTOM, 10)
        
    def init_pages(self, varible_name: list):
        '''初始化页面值'''
        for i in varible_name:
            self.__dict__[i] = self.new_page()
            
    def draw_page(self, index):
        '''根据索引绘制页面内容'''
        pass
    
    def create_pages(self):
        """创建显示器页面"""    
        for i in range(self.total_pages):
            self.panel = wx.Panel(self.content_panel)
            self.draw_page(i)
            self.panel.Hide()
            self.content_sizer.Add(self.panel, 1, wx.EXPAND)  # 将页面加入Sizer
            self.pages.append(self.panel)
    
    def new_page(self):
        '''创建新页面'''
        self.total_pages += 1
        self.next_page += 1
        return self.total_pages - 1

    def update_buttons(self):
        '''更新按钮状态，如果有按钮显示操作则重载此函数'''
        if self.current_page >= self.total_pages - 1:
            self.btn_prev.Hide()
            self.btn_next.Hide()
            self.btn_cancel.Hide()
            self.btn_exit.Show()
        else:
            self.btn_next.Show()
            self.btn_cancel.Show()
            self.btn_exit.Hide()
            if self.current_page > 0:
                self.btn_prev.Show()
            else:
                self.btn_prev.Hide()

    def on_prev(self, event):
        '''上一步按钮'''
        if self.current_page > 0:
            self.update_page(self.current_page - 1)

    def on_next(self, event):
        '''下一步按钮'''
        if self.current_page < self.total_pages - 1:
            self.update_page(self.current_page + 1)
    
    def update_page(self, page_index):
        '''更新页面'''
        self.pages[self.current_page].Hide()
        self.current_page = page_index
        self.pages[self.current_page].Show()
        self.update_buttons()
        
    def on_close(self, event):
        '''关闭窗口'''
        self.Destroy()

if __name__ == '__main__':
    app = wx.App()
    frame = PagesUI('test', (300, 200))
    
    frame.Show()
    app.MainLoop()