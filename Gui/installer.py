import wx
from pathlib import Path
import logging
import winreg
import os
import sys
import ctypes
import json

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(sys.argv), None, 1
    )
    with open("run_as_admin.json", "w") as f:
        json.dump({"is_not_admin": True}, f)
    sys.exit(0)

def get_resource_path(*paths):
    '''
    获取软件资源文件路径
    '''
    try:
        resource = Path(__file__).parent.resolve() / Path('res') # 获取当前目录的资源文件夹路径
        if not resource.exists():
            raise FileNotFoundError('资源文件出现损坏')
        return str(resource.joinpath(*paths))
    except Exception as e:
        wx.MessageBox(f'资源损坏: {e}', '错误', wx.OK | wx.ICON_ERROR)
        
def get_inst_resouce_path(*paths):
    '''
    获取安装资源文件路径
    '''
    try:
        resource = Path(__file__).parent.resolve() / Path('inst_res') # 获取当前目录的资源文件夹路径
        if not resource.exists():
            raise FileNotFoundError('资源文件出现损坏')
        return str(resource.joinpath(*paths))
    except Exception as e:
        wx.MessageBox(f'资源损坏: {e}', '错误', wx.OK | wx.ICON_ERROR)

class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="clickMouse 安装向导", size=(400, 300))
        self.pages = []
        self.current_page = 0
        self.total_pages = 5
        
        # 主面板
        main_panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # 创建内容面板容器
        self.content_panel = wx.Panel(main_panel)
        self.content_sizer = wx.BoxSizer(wx.VERTICAL)
        self.content_panel.SetSizer(self.content_sizer)
        
        # 创建按钮面板
        btn_panel = wx.Panel(main_panel)
        
        # 创建按钮
        self.btn_prev = wx.Button(btn_panel, label="上一步", pos = (0,5))
        self.btn_next = wx.Button(btn_panel, label="下一步", pos = (100, 5))
        self.btn_cancel = wx.Button(btn_panel, label="取消", pos = (200, 5))
        self.btn_exit = wx.Button(btn_panel, label="退出", pos = (200, 5))
        self.btn_exit.Hide()
        
        # 创建页面内容
        self.create_pages()
        
        # 创建标题面板
        title_panel = wx.Panel(main_panel)
        title_panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        title_panel.SetWindowStyle(wx.BORDER_SIMPLE)
        title_sizer = wx.BoxSizer(wx.HORIZONTAL)
        title_panel.SetSizer(title_sizer)
        
        # 创建标题
        title = wx.StaticText(title_panel, label="clickMouse 安装向导", pos=(0, 0)).SetFont(wx.Font(20, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        icon = wx.Icon(get_resource_path("icons", 'icon.ico'), wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)
        # 绘制icon在标题栏
        title_bitmap = wx.StaticBitmap(title_panel, -1, wx.Bitmap(get_inst_resouce_path('icon.png')), pos=(300, 0))
        title_sizer.Add(title, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 10)
        title_sizer.Add(title_bitmap, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        
        # 主布局调整
        main_sizer.Add(title_panel, 1, wx.EXPAND | wx.TOP | wx.Center, 5)
        main_sizer.Add(self.content_panel, 5, wx.EXPAND)
        main_sizer.Add(btn_panel, 1, wx.ALIGN_RIGHT | wx.BOTTOM, 10)
        main_panel.SetSizer(main_sizer)
        
        # 绑定事件
        self.btn_prev.Bind(wx.EVT_BUTTON, self.on_prev)
        self.btn_next.Bind(wx.EVT_BUTTON, self.on_next)
        self.btn_cancel.Bind(wx.EVT_BUTTON, lambda e: self.Close())
        self.btn_exit.Bind(wx.EVT_BUTTON, lambda e: self.Close())
        
        self.update_buttons()
    
    def create_pages(self):    
        for i in range(self.total_pages):
            panel = wx.Panel(self.content_panel)
            match i:
                case 0:
                    wx.StaticText(panel, label="欢迎使用 clickMouse 安装向导!\n\n这个程序将简单的使用几分钟时间，帮助你完成安装。\n点击下一步开启安装助手。", pos=(5, 0))
                case 1:
                    wx.StaticText(panel, label="请先阅读下方的说明，确认无误后，点击下一步。", pos=(5, 0))
                    # 滚动的文本框
                    with open(get_inst_resouce_path("license.txt"), 'r', encoding='utf-8') as f:
                        wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2, size = (350, 125), pos=(5, 30)).SetValue(f.read())
                    
                    self.allow_checkbox = wx.CheckBox(panel, label="我已阅读并同意上述说明", pos=(5, 160))
                    # 绑定事件
                    self.allow_checkbox.Bind(wx.EVT_CHECKBOX, self.on_checkbox_toggle)
                case 2:
                    wx.StaticText(panel, label="请选择你要安装的路径，然后点击下一步。", pos=(5, 0))
                    # 选择路径
                    self.path_picker = wx.DirPickerCtrl(panel, message="请选择安装路径", pos=(5, 30), size=(350, -1))
                    self.path_picker.SetPath(os.environ['PROGRAMFILES'] + "\\clickMouse")
                    
                    # 绑定事件
                    self.path_picker.Bind(wx.EVT_DIRPICKER_CHANGED, self.on_path_changed)
                case 3:
                    wx.StaticText(panel, label="请选择你的文件快捷方式设置，然后点击下一步：", pos=(5, 0))
                    wx.StaticText(panel, label="开始菜单的快捷方式名称：", pos=(5, 30))
                    self.set_start_menu_textctrl = wx.TextCtrl(panel, pos=(5, 50), size=(350, -1))
                    self.set_start_menu_checkbox = wx.CheckBox(panel, label="不要在开始菜单中显示", pos=(5, 80))
                    self.desktop_shortcut = wx.CheckBox(panel, label="创建桌面快捷方式", pos=(5, 110))
                    
                    # 绑定事件
                    self.set_start_menu_checkbox.Bind(wx.EVT_CHECKBOX, self.on_menu_toggle)
                    self.desktop_shortcut.Bind(wx.EVT_CHECKBOX, self.on_desktop_toggle)
            panel.Hide()
            self.content_sizer.Add(panel, 1, wx.EXPAND)  # 将页面加入Sizer
            self.pages.append(panel)
        
        self.pages[0].Show()
        
    def on_path_changed(self, event):
        self.update_buttons()
        
    def on_menu_toggle(self, event):
        if self.set_start_menu_checkbox.GetValue():
            self.set_start_menu_textctrl.Enable(False)
        else:
            self.set_start_menu_textctrl.Enable(True)
        
    def on_checkbox_toggle(self, event):
        self.not_create_in_start_menu = not self.allow_checkbox.GetValue()
        self.update_buttons()
        
    def on_desktop_toggle(self, event):
        self.create_desktop_shortcut = self.desktop_shortcut.GetValue()

    def update_buttons(self):
        """更新按钮状态"""
        self.btn_prev.Show(self.current_page > 0)
        
        if self.current_page == self.total_pages - 1:
            self.btn_next.Hide()
            self.btn_cancel.Hide()
            self.btn_prev.Hide()
            self.btn_exit.Show()
        else:
            self.btn_next.Show()
            self.btn_cancel.Show()
            self.btn_exit.Hide()
        
        # 按钮启用状态处理
        if self.current_page == 1:  # 说明页面
            self.btn_next.Enable(self.allow_checkbox.GetValue())
        elif self.current_page == 2:  # 路径页面
            if os.path.exists("\\".join(self.path_picker.GetPath().split("\\")[:-1])):
                self.btn_next.Enable(True)
            else:
                self.btn_next.Enable(False)
        else:
            self.btn_next.Enable(True)  # 其他页面保持可用
        
        self.content_panel.Layout()
        self.Layout()

    def on_prev(self, event):
        if self.current_page > 0:
            self.pages[self.current_page].Hide()
            self.current_page -= 1
            self.pages[self.current_page].Show()
            self.update_buttons()

    def on_next(self, event):
        if self.current_page < self.total_pages - 1:
            self.pages[self.current_page].Hide()
            self.current_page += 1
            self.pages[self.current_page].Show()
            self.update_buttons()

if __name__ == "__main__":
    app = wx.App()
    frame = MainFrame()
    if not is_admin():
        if os.path.exists("run_as_admin.json"):
            try:
                with open("run_as_admin.json", "r") as f:
                    data = json.load(f)
                    try:
                        not_admin = data.get("is_not_admin", True)
                    except:
                        not_admin = True
                if not_admin:
                    wx.MessageBox("程序已请求提升权限，但是仍然以非管理员权限运行，请联系系统管理员", "错误", wx.OK | wx.ICON_ERROR)
                    os.remove("run_as_admin.json")
                    sys.exit(1)
            except:
                sys.exit(1)
        run_as_admin()
    frame.Show()
    app.MainLoop()
