import wx
from pathlib import Path
import winreg
import os
import sys
import ctypes
import json
import py7zr
from datetime import datetime
import pyperclip
import win32com.client

def create_shortcut(path, target, description, work_dir = None, icon_path = None):
    # 创建快捷方式
    icon_path = target if icon_path is None else icon_path
    work_dir = os.path.dirname(target) if work_dir is None else work_dir
    
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(path)
    shortcut.TargetPath = target # 目标程序
    shortcut.WorkingDirectory = work_dir # 工作目录
    shortcut.IconLocation = icon_path # 图标（路径,图标索引）
    shortcut.Description = description # 备注描述
    shortcut.Save()

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    ctypes.windll.shell32.ShellExecuteW(
        None, 'runas', sys.executable, ' '.join(sys.argv), None, 1
    )
    with open('run_as_admin.json', 'w') as f:
        json.dump({'is_not_admin': 0}, f)
    sys.exit(0)
    
def get_install_size():
    return os.path.getsize(get_inst_resouce_path('packages', 'clickmouse.7z'))
        
def get_inst_resouce_path(*paths):
    '''
    获取安装资源文件路径
    '''
    try:
        resource = Path(__file__).parent.resolve() / Path('inst_res') # 获取当前目录的资源文件夹路径
        if not resource.exists():
            return ""
        return str(resource.joinpath(*paths))
    except Exception as e:
        wx.MessageBox(f'资源损坏: {e}', '错误', wx.OK | wx.ICON_ERROR)
        
def extract_7z(file_path, extract_path):
    '''
    解压7z文件
    '''
    with py7zr.SevenZipFile(file_path, mode='r') as z:
        z.extractall(path=extract_path)
    
def check_reg_key(subkey):
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, subkey, 0, winreg.KEY_READ):
            return True
    except:
        return False

def read_reg_key(key, value):
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key, 0, winreg.KEY_READ) as k:
            return winreg.QueryValueEx(k, value)[0]
    except:
        return None

class InstallFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title='clickMouse 安装向导', size=(400, 300))
        # 初始化
        self.pages = []
        self.current_page = 0
        self.total_pages = 9
        self.status = ''
        self.error = ''
        self.not_create_in_start_menu = False
        self.create_desktop_shortcut = False
        self.run_clickmouse = False
        self.software_reg_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\clickMouse'
        
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
        self.btn_prev = wx.Button(btn_panel, label='上一步', pos = (0,5))
        self.btn_next = wx.Button(btn_panel, label='下一步', pos = (100, 5))
        self.btn_cancel = wx.Button(btn_panel, label='取消', pos = (200, 5))
        self.btn_exit = wx.Button(btn_panel, label='退出', pos = (200, 5))
        self.btn_copy_err = wx.Button(btn_panel, label='复制错误信息', pos = (100, 5))
        self.btn_show_sol = wx.Button(btn_panel, label='显示解决方案', pos = (0, 5))
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
        title = wx.StaticText(title_panel, label='clickMouse 安装向导', pos=(0, 0)).SetFont(wx.Font(20, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        icon = wx.Icon(get_inst_resouce_path('icons', 'icon.ico'), wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)
        # 绘制icon在标题栏
        title_bitmap = wx.StaticBitmap(title_panel, -1, wx.Bitmap(get_inst_resouce_path('icons', 'icon.png')), pos=(300, 0))
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
        self.btn_cancel.Bind(wx.EVT_BUTTON, self.on_cancel)
        self.btn_exit.Bind(wx.EVT_BUTTON, lambda e: self.Close())
        self.btn_copy_err.Bind(wx.EVT_BUTTON, self.on_copy_err)
        self.btn_show_sol.Bind(wx.EVT_BUTTON, lambda e: os.startfile(get_inst_resouce_path('errnote.txt')))
        
        self.update_buttons()
        if check_reg_key(self.software_reg_key):
            self.update_page(8)
    
    def create_pages(self):    
        for i in range(self.total_pages):
            panel = wx.Panel(self.content_panel)
            match i:
                case 0:
                    wx.StaticText(panel, label='欢迎使用 clickMouse 安装向导!\n\n这个程序将简单的使用几分钟时间，帮助你完成安装。\n点击下一步开启安装助手。', pos=(5, 0))
                case 1:
                    wx.StaticText(panel, label='请先阅读下方的说明，确认无误后，点击下一步。', pos=(5, 0))
                    # 滚动的文本框
                    with open(get_inst_resouce_path('license.txt'), 'r', encoding='utf-8') as f:
                        wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2, size = (350, 125), pos=(5, 30)).SetValue(f.read()) # 显示协议内容
                    
                    self.allow_checkbox = wx.CheckBox(panel, label='我已阅读并同意上述说明', pos=(5, 160))
                    # 绑定事件
                    self.allow_checkbox.Bind(wx.EVT_CHECKBOX, self.on_checkbox_toggle) 
                case 2:
                    wx.StaticText(panel, label='请选择你要安装的路径，然后点击下一步。', pos=(5, 0))
                    # 选择路径
                    self.path_picker = wx.DirPickerCtrl(panel, message='请选择安装路径', pos=(5, 30), size=(350, -1))
                    self.path_picker.SetPath(os.environ['PROGRAMFILES'] + r'\clickMouse')
                    
                    # 绑定事件
                    self.path_picker.Bind(wx.EVT_DIRPICKER_CHANGED, self.on_update_button) # 路径选择器改变
                case 3:
                    wx.StaticText(panel, label='请选择你的文件快捷方式设置，然后点击下一步：', pos=(5, 0))
                    wx.StaticText(panel, label='开始菜单的快捷方式名称：', pos=(5, 30))
                    self.set_start_menu_textctrl = wx.TextCtrl(panel, pos=(5, 50), size=(350, -1))
                    self.set_start_menu_checkbox = wx.CheckBox(panel, label='不要在开始菜单中显示', pos=(5, 80))
                    self.desktop_shortcut = wx.CheckBox(panel, label='创建桌面快捷方式', pos=(5, 110))
                    
                    # 绑定事件
                    self.set_start_menu_checkbox.Bind(wx.EVT_CHECKBOX, self.on_update_button) # 选择不在开始菜单中显示
                    self.set_start_menu_textctrl.Bind(wx.EVT_TEXT, self.on_update_button) # 快捷方式名称改变
                    self.desktop_shortcut.Bind(wx.EVT_CHECKBOX, self.on_desktop_toggle) # 创建桌面快捷方式
                case 4:
                    wx.StaticText(panel, label='正在安装clickmouse, 请稍候...', pos=(5, 0))
                    self.status_text = wx.StaticText(panel, label='安装进度', pos=(5, 30))
                case 5:
                    wx.StaticText(panel, label='安装完成！点击确定退出安装向导。', pos=(5, 0))
                case 6:
                    wx.StaticText(panel, label='安装已取消！点击确定退出安装向导。', pos=(5, 0))
                case 7:
                    wx.StaticText(panel, label='安装失败！点击确定退出安装向导。', pos=(5, 0))
                    self.error_text = wx.StaticText(panel, label=f'错误信息：\n在{self.status}时候错误\n错误信息：{self.error}', pos=(5, 30))
                case 8:
                    location = read_reg_key(self.software_reg_key, 'InstallLocation')
                    wx.StaticText(panel, label=f'clickMouse 已经安装，位于{location if location else "未知路径"}', pos=(5, 0))
            panel.Hide()
            self.content_sizer.Add(panel, 1, wx.EXPAND)  # 将页面加入Sizer
            self.pages.append(panel)
    
        self.pages[0].Show()
        
    def setStatus(self, text):
        self.status = text
        self.status_text.SetLabel(text)
    
    def on_copy_err(self, event):
        """ 复制错误信息"""
        pyperclip.copy(f'在{self.status}出现错误，错误信息：\n{self.error}')
        wx.MessageBox('错误信息已复制到剪贴板', '提示', wx.OK | wx.ICON_INFORMATION)
        
    def on_update_button(self, event):
        """更新按钮状态"""
        self.update_buttons()
        
    def on_checkbox_toggle(self, event):
        """同意协议"""
        self.not_create_in_start_menu = self.set_start_menu_checkbox.GetValue()
        self.update_buttons()
        
    def on_run_toggle(self, event):
        """运行clickmouse选择框更新"""
        self.run_clickmouse = self.run_checkbox.GetValue()

    def on_desktop_toggle(self, event):
        """创建桌面快捷方式"""
        self.create_desktop_shortcut = self.desktop_shortcut.GetValue()

    def update_buttons(self):
        '''更新按钮状态'''
        self.btn_prev.Show(self.current_page > 0)
        
        if self.current_page >= 5:
            self.btn_next.Hide()
            self.btn_cancel.Hide()
            self.btn_prev.Hide()
            self.btn_exit.Show()
        else:
            self.btn_next.Show()
            self.btn_cancel.Show()
            self.btn_exit.Hide()
        
        # 按钮启用状态处理
        if self.current_page == -1:  # 退出页面
            self.btn_next.Hide()
            self.btn_cancel.Hide()
            self.btn_prev.Hide()
            self.btn_exit.Show()
        elif self.current_page == 1:  # 说明页面
            self.btn_next.Enable(self.allow_checkbox.GetValue())
        elif self.current_page == 2:  # 路径页面
            if os.path.exists('\\'.join(self.path_picker.GetPath().split('\\')[:-1])):
                self.btn_next.Enable(True)
            else:
                self.btn_next.Enable(False)
        elif self.current_page == 3:  # 快捷方式页面
            self.btn_next.Enable(False)
            if self.set_start_menu_checkbox.GetValue():
                self.btn_next.Enable(True)
            else:
                self.btn_next.Enable(bool(self.set_start_menu_textctrl.GetValue()))
    
            self.set_start_menu_textctrl.Enable(not self.set_start_menu_checkbox.GetValue())
        elif self.current_page == 4:  # 进度页面
            self.btn_next.Hide()
            self.btn_prev.Hide()
            self.btn_cancel.Hide()
            
            self.install()
        elif self.current_page == 7: # 错误页面
            self.error_text.SetLabel(f'错误信息：\n在{self.status}\n错误：{self.error}')
            self.btn_copy_err.Show()
            self.btn_show_sol.Show()
        else:
            self.btn_next.Enable(True)  # 其他页面保持可用
            self.btn_copy_err.Hide()
            self.btn_show_sol.Hide()
        
        self.content_panel.Layout()
        self.Layout()
        
    def install(self):
        '''安装程序'''
        # 创建文件夹
        try:
            self.setStatus('正在创建文件夹...')
            install_path = self.path_picker.GetPath()
            os.makedirs(install_path, exist_ok=True)
            self.setStatus('解压安装包...')
            extract_7z(get_inst_resouce_path('packages', 'clickmouse.7z'), install_path)
            self.setStatus('正在创建包管理器文件...')
            with open(fr'{install_path}\packages.json', 'w', encoding='utf-8') as f:
                package = [
                    {
                        "package_name" : "clickmouse",
                        "install_location" : f"{install_path}",
                        "create_in_start_menu" : not self.not_create_in_start_menu,
                        "create_desktop_shortcut" : self.create_desktop_shortcut,
                        "start_menu_name" : self.set_start_menu_textctrl.GetValue() if not self.set_start_menu_checkbox.GetValue() else None,
                    }
                ]
                json.dump(package, f)
            self.setStatus('正在创建安装信息...')
            key = winreg.CreateKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\clickmouse"
            )
            winreg.SetValue(key, '', winreg.REG_SZ, fr'{install_path}\clickmouse.exe')
            winreg.SetValueEx(key, 'Path', 0, winreg.REG_SZ, f'{install_path}')
            winreg.CloseKey(key)

            self.setStatus('正在创建卸载信息...')
            uninstall_key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\clickmouse")
            winreg.SetValueEx(uninstall_key, 'DisplayName', 0, winreg.REG_SZ, 'clickmouse')
            winreg.SetValueEx(uninstall_key, 'Publisher', 0, winreg.REG_SZ, f'xystudio')
            winreg.SetValueEx(uninstall_key, 'InstallLocation', 0, winreg.REG_SZ, f'{install_path}')
            winreg.SetValueEx(uninstall_key, 'UninstallString', 0, winreg.REG_SZ, fr'{install_path}\uninstall.exe')
            winreg.SetValueEx(uninstall_key, 'InstallDate', 0, winreg.REG_SZ, str(datetime.now()))
            with open(get_inst_resouce_path('version'), 'r', encoding='utf-8') as f:
                version = f.read()
            winreg.SetValueEx(uninstall_key, 'DisplayVersion', 0, winreg.REG_SZ, version)
            winreg.SetValueEx(uninstall_key, 'EstimatedSize', 0, winreg.REG_DWORD, int(str(f"{os.path.getsize(fr'{install_path}\clickmouse.exe') // 1024 :.0f}")))
            winreg.SetValueEx(uninstall_key, 'NoModify', 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(uninstall_key, 'NoRepair', 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(uninstall_key, 'URLInfoAbout', 0, winreg.REG_SZ, 'https://www.github.com/xystudio/pyclickmouse')
            winreg.SetValueEx(uninstall_key, 'DisplayIcon', 0, winreg.REG_SZ, fr'{install_path}\res\icons\clickmouse\icon.ico')

            winreg.CloseKey(uninstall_key)

            self.setStatus('正在创建快捷方式...')
            if package[0]["create_in_start_menu"]:
                create_shortcut(fr"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\{package[0]["start_menu_name"]}.lnk", fr"{install_path}\clickmouse.exe", "鼠标连点器")
            if package[0]['create_desktop_shortcut']:
                create_shortcut(fr"{os.path.expanduser('~')}\Desktop\clickmouse.lnk", fr"{install_path}\clickmouse.exe", "鼠标连点器")
            self.on_next(None)
        except Exception as e:
            self.error = e
            wx.MessageBox(f'安装失败: {e}', '错误', wx.OK | wx.ICON_ERROR)
            self.update_page(7)

    def on_prev(self, event):
        """上一步按钮"""
        if self.current_page > 0:
            self.update_page(self.current_page - 1)

    def on_next(self, event):
        """下一步按钮"""
        if self.current_page < self.total_pages - 1:
            self.update_page(self.current_page + 1)
    
    def on_cancel(self, event):
        """取消按钮"""
        self.update_page(6)
    
    def update_page(self, page_index):
        """更新页面"""
        self.pages[self.current_page].Hide()
        self.current_page = page_index
        self.pages[self.current_page].Show()
        self.update_buttons()

if __name__ == '__main__':
    app = wx.App()
    frame = InstallFrame()
    if not get_inst_resouce_path('packages'):
        wx.MessageBox('由于每个版本都会更新安装包，未防止git文件夹过大，安装包不会添加，请自行打包（格式必须为7z）并放入inst_res/packages文件夹下。', '错误', wx.OK | wx.ICON_ERROR)
    if is_admin():  # 管理员权限
        if os.path.exists('run_as_admin.json'):
            os.remove('run_as_admin.json')
        frame.Show()
        app.MainLoop()
    else:
        try:
            with open('run_as_admin.json', 'r') as f:
                data = json.load(f).get('is_not_admin', 0)
        except:
            data = 0
        if data == 0:
            run_as_admin() # 请求管理员权限
        elif data == 1:
            wx.MessageBox("错误", "程序已请求提升权限，但是仍然以非管理员权限运行，请联系系统管理员", wx.OK | wx.ICON_ERROR)
            os.remove('run_as_admin.json')
