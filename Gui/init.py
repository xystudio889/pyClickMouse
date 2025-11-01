import wx
import os
from pathlib import Path
import winreg # 注册表编辑
import ctypes # 管理员运行
import pyperclip # 复制错误信息
import win32com.client # 创建快捷方式
import zipfile # 解压文件
import json # 读写json文件
import sys # 运行权限
from sharelibs import (get_resource_path, settings, run_software) # 共享库
from uiStyles import PagesUI # 界面样式
from datetime import datetime # 时间

with open('res/init_langs.json', 'r', encoding='utf-8') as f:
    langs = json.load(f)
    
with open(get_resource_path('package_info.json'), 'r', encoding='utf-8') as f:
    packages_info = json.load(f)
    
software_reg_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\clickMouse'

def get_lang(lang_package_id, lang_id = None):
    lang_id = settings.get('select_lang', 0) if lang_id is None else lang_id
    for i in langs:
        if i['lang_id'] == 0: # 设置默认语言包
            lang_text = i['lang_package']
        if i['lang_id'] == lang_id: # 设置目前语言包
            lang_text = i['lang_package']
    try:
        return lang_text[lang_package_id]
    except KeyError:
        return 'Language not found'

def save_settings(settings):
    '''
    保存设置
    '''
    with open(data_path / 'settings.json', 'w', encoding='utf-8') as f:
        json.dump(settings, f)

data_path = Path('data')

def create_shortcut(path, target, description, work_dir = None, icon_path = None):
    # 创建快捷方式
    icon_path = target if icon_path is None else icon_path
    work_dir = os.path.dirname(target) if work_dir is None else work_dir
    
    shell = win32com.client.Dispatch('WScript.Shell')
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
    pass
        
def extract_zip(file_path, extract_path):
    '''
    解压zip文件
    '''
    with zipfile.ZipFile(file_path, 'r') as f:
        f.extractall(extract_path)
    
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

def get_system_language():
    '''通过Windows注册表获取系统语言'''
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\International")
        lang, _ = winreg.QueryValueEx(key, "LocaleName")
        return lang
    except Exception:
        return 'en-US'
    
def parse_system_language_to_lang_id():
    '''将系统语言转换为语言ID'''
    system_lang = get_system_language()
    for i in langs:
        if i['is_official']:
            if i['lang_info'].get('lang_system_name', 'en-US') == system_lang:
                return i['lang_id']
    return 0
    
def get_dir_size_for_reg(dir):
    size = 0
    
    for root, dirs, files in os.walk(dir):
        for file in files:
            size += os.path.getsize(file)
    return size // 1024

def import_package(package_id, **config):
    package = packages_info[package_id]
    package.update(config)
    return package
    
class InstallFrame(PagesUI):
    def __init__(self):
        super().__init__(parent=None, title='clickMouse 安装向导', size=(400, 300), style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        # 初始化
        self.pages = []
        self.current_page = 0
        self.total_pages = 11
        self.status = ''
        self.error = ''
        self.not_create_in_start_menu = False
        self.create_desktop_shortcut = False

        # 创建按钮
        self.btn_copy_err = wx.Button(self.btn_panel, label='复制错误信息', pos = (100, 5))
        self.btn_show_sol = wx.Button(self.btn_panel, label='显示解决方案', pos = (0, 5))
        
        # 定义页面id
        self.init_pages(['PAGE_START', 'PAGE_READ_LICENSE', 'PAGE_SET_INSTALL_PATH', 'PAGE_SELECT_LINK', 'PAGE_SET_COMPONENT', 'PAGE_CHECK_COMPONENT', 'PAGE_INSTALL', 'PAGE_FINISH', 'PAGE_CANCEL', 'PAGE_ERROR', 'PAGE_IS_INSTALLED'])
        
        # 创建页面内容
        self.create_pages()
        
        # 创建标题面板
        self.title_panel = wx.Panel(self.main_panel)
        self.title_panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.title_panel.SetWindowStyle(wx.BORDER_SIMPLE)
        title_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.title_panel.SetSizer(title_sizer)
        
        # 创建标题
        wx.StaticText(self.title_panel, label='clickMouse 安装向导', pos=(0, 0)).SetFont(wx.Font(20, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        self.SetIcon(wx.Icon(get_resource_path('icons', 'clickmouse', 'init.ico')))
        # 绘制icon在标题栏
        title_icon = wx.Bitmap(get_resource_path('icons', 'clickmouse', 'icon.png'), wx.BITMAP_TYPE_PNG).ConvertToImage().Scale(32, 32, wx.IMAGE_QUALITY_HIGH)
        wx.StaticBitmap(self.title_panel, -1, wx.Bitmap(title_icon), pos=(340, 0))
        
        self.init_show()

        self.btn_cancel.Bind(wx.EVT_BUTTON, self.on_cancel)
        self.btn_copy_err.Bind(wx.EVT_BUTTON, self.on_copy_err)
        self.btn_show_sol.Bind(wx.EVT_BUTTON, lambda e: os.startfile(get_resource_path('errnote.txt')))
        
        self.update_buttons()
        self.update_page(self.PAGE_START)
        
        if check_reg_key(software_reg_key):
            self.update_page(self.PAGE_IS_INSTALLED)

        
    def init_show(self):
        self.main_sizer.Add(self.title_panel, 1, wx.EXPAND | wx.TOP | wx.Center, 5)
        self.content = self.main_sizer.Add(self.content_panel, 5, wx.EXPAND)
        self.btn = self.main_sizer.Add(self.btn_panel, 1, wx.ALIGN_RIGHT | wx.BOTTOM, 10)
    
    def draw_page(self, index):
        match index:
            case self.PAGE_START:
                wx.StaticText(self.panel, label='欢迎使用 clickMouse 安装向导!\n\n这个程序将简单的使用几分钟时间，帮助你完成安装。\n点击下一步开启安装助手。', pos=(5, 0))
            case self.PAGE_READ_LICENSE:
                wx.StaticText(self.panel, label='请先阅读下方的说明，确认无误后，点击下一步。', pos=(5, 0))
                # 滚动的文本框
                with open(get_resource_path('license.txt'), 'r', encoding='utf-8') as f:
                    wx.TextCtrl(self.panel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2, size = (350, 125), pos=(5, 30)).SetValue(f.read()) # 显示协议内容
                
                self.allow_checkbox = wx.CheckBox(self.panel, label='我已阅读并同意上述说明', pos=(5, 160))
                # 绑定事件
                self.allow_checkbox.Bind(wx.EVT_CHECKBOX, self.on_checkbox_toggle) 
            case self.PAGE_SET_INSTALL_PATH:
                wx.StaticText(self.panel, label='这是本软件的安装路径', pos=(5, 0))
                wx.StaticText(self.panel, label='当前无法选择路径，若要移动安装位置，请将clickmouse文件夹移动\n到新的位置', pos=(5, 60))
                # 选择路径
                self.path_picker = wx.DirPickerCtrl(self.panel, message='请选择安装路径', pos=(5, 30), size=(350, -1))
                self.path_picker.SetPath(str(Path.cwd()))
                self.path_picker.Enable(False)
                
                # 绑定事件
                self.path_picker.Bind(wx.EVT_DIRPICKER_CHANGED, self.on_update_button) # 路径选择器改变
            case self.PAGE_SELECT_LINK:
                wx.StaticText(self.panel, label='请选择你的文件快捷方式设置，然后点击下一步：', pos=(5, 0))
                wx.StaticText(self.panel, label='开始菜单的快捷方式名称：', pos=(5, 30))
                self.set_start_menu_textctrl = wx.TextCtrl(self.panel, pos=(5, 50), size=(350, -1))
                self.set_start_menu_checkbox = wx.CheckBox(self.panel, label='不要在开始菜单中显示', pos=(5, 80))
                self.desktop_shortcut = wx.CheckBox(self.panel, label='创建桌面快捷方式', pos=(5, 110))
                
                # 绑定事件
                self.set_start_menu_checkbox.Bind(wx.EVT_CHECKBOX, self.on_update_button) # 选择不在开始菜单中显示
                self.set_start_menu_textctrl.Bind(wx.EVT_TEXT, self.on_update_button) # 快捷方式名称改变
            case self.PAGE_SET_COMPONENT:
                self.selected_components = ['clickmouse 主程序']
                self.protected_item = None
                self.current_mode = '完整'
                
                sizer = wx.BoxSizer(wx.VERTICAL)
                select_sizer = wx.BoxSizer(wx.HORIZONTAL)
                
                # 左侧未选择树形控件
                self.unselected_tree = self.create_tree(self.panel, '未安装组件')
                select_sizer.Add(self.unselected_tree, 3, wx.EXPAND | wx.ALL, 5)
                
                # 中间按钮区域
                btn_panel = wx.Panel(self.panel)
                btn_sizer = wx.BoxSizer(wx.VERTICAL)
                
                # 添加模板选择器
                choises = ['完整', '默认', '精简', '自定义']
                self.template_choice = wx.Choice(btn_panel, choices=choises)
                self.template_choice.SetSelection(choises.index(self.current_mode))  # 默认选中'默认'模板
                self.template_choice.Bind(wx.EVT_CHOICE, self.on_template_change)
                btn_sizer.Add(self.template_choice, 0, wx.ALL | wx.EXPAND, 5)
                
                btn_sizer.AddStretchSpacer()
                self.add_btn = wx.Button(btn_panel, label='添加 >>', size=(120, -1))
                self.remove_btn = wx.Button(btn_panel, label='<< 移除', size=(120, -1))
                btn_sizer.Add(self.add_btn, 0, wx.ALL | wx.ALIGN_CENTER, 5)
                btn_sizer.Add(self.remove_btn, 0, wx.ALL | wx.ALIGN_CENTER, 5)
                btn_sizer.AddStretchSpacer()
                btn_panel.SetSizer(btn_sizer)
                select_sizer.Add(btn_panel, 1, wx.EXPAND)
                
                # 右侧已选择树形控件
                self.selected_tree = self.create_tree(self.panel, '已安装组件')
                select_sizer.Add(self.selected_tree, 3, wx.EXPAND | wx.ALL, 5)
                
                sizer.Add(wx.StaticText(self.panel, label='请选择你要安装的组件，然后点击确认选择。', pos=(5, 0)), 1, wx.EXPAND | wx.ALL, 1)
                sizer.Add(select_sizer, 15, wx.EXPAND | wx.ALL, 1)
                self.panel.SetSizer(sizer)
                
                # 绑定事件
                self.add_btn.Bind(wx.EVT_BUTTON, self.on_add)
                self.remove_btn.Bind(wx.EVT_BUTTON, self.on_remove)
                
                # 初始化树数据
                self.init_tree_data()
                self.apply_template('完整')
            case self.PAGE_CHECK_COMPONENT:
                sizer = wx.BoxSizer(wx.VERTICAL)
                
                title = wx.StaticText(self.panel, label='您已选择的组件：')
                sizer.Add(title, 1, wx.ALL | wx.EXPAND, 10)
                
                self.text = wx.StaticText(self.panel, label='正在加载组件列表...', pos=(5, 30))
                sizer.Add(self.text, 15, wx.EXPAND | wx.LEFT | wx.RIGHT, 20)
                
                self.panel.SetSizer(sizer)
            case self.PAGE_INSTALL:
                wx.StaticText(self.panel, label='正在安装clickmouse, 请稍候...', pos=(5, 0))
                self.status_text = wx.StaticText(self.panel, label='安装进度', pos=(5, 30))
            case self.PAGE_FINISH:
                wx.StaticText(self.panel, label='安装完成！点击确定退出安装向导。', pos=(5, 0))
                self.launch_checkbox = wx.CheckBox(self.panel, label='启动clickmouse', pos=(5, 30))
                self.launch_checkbox.SetValue(True)
            case self.PAGE_CANCEL:
                wx.StaticText(self.panel, label='安装已取消！点击确定退出安装向导。', pos=(5, 0))
            case self.PAGE_ERROR:
                wx.StaticText(self.panel, label='安装失败！点击确定退出安装向导。', pos=(5, 0))
                self.error_text = wx.StaticText(self.panel, label=f'错误信息：\n在{self.status}时候错误\n错误信息：{self.error}', pos=(5, 30))
            case self.PAGE_IS_INSTALLED:
                location = read_reg_key(software_reg_key, 'InstallLocation')
                wx.StaticText(self.panel, label=f'clickMouse 已经安装，位于{location if location else '未知路径'}', pos=(5, 0))
                self.launch_installed_checkbox = wx.CheckBox(self.panel, label='启动clickmouse', pos=(5, 30))
                self.launch_installed_checkbox.SetValue(True)
                cannot_select_note = wx.StaticText(self.panel, label='无法确认clickmouse的位置，请手动启动。', pos=(120, 30))
                cannot_select_note.Hide()
                if not location:
                    cannot_select_note.Show()
                    self.launch_installed_checkbox.Enable(False) # 未知路径无法选择
                    self.launch_installed_checkbox.SetValue(False) # 未知路径无法启动
        
    def create_tree(self, parent, root_label):
        '''创建树形控件'''
        tree = wx.TreeCtrl(parent, style=wx.TR_DEFAULT_STYLE)
        img_list = wx.ImageList(16, 16)
        img_list.Add(wx.ArtProvider.GetBitmap(wx.ART_FOLDER, size=(16,16)))
        img_list.Add(wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, size=(16,16)))
        tree.AssignImageList(img_list)
        tree.AddRoot(root_label, image=0)
        return tree
    
    def init_tree_data(self):
        '''初始化树形控件数据'''
        self.components = ['clickmouse 扩展测试']
        root = self.unselected_tree.GetRootItem()
        for comp in self.components:
            self.unselected_tree.AppendItem(root, comp, 1)
        self.unselected_tree.Expand(root)
        
        installed_root = self.selected_tree.GetRootItem()
        self.protected_item = self.selected_tree.AppendItem(installed_root, 'clickmouse 主程序', 1)
        # self.cmd_tool_item = self.selected_tree.AppendItem(installed_root, 'clickmouse命令行', 1) # 暂时禁用
        self.selected_tree.Expand(installed_root)
    
    def apply_template(self, template_name):
        '''使用内置的模板'''
        self.current_mode = template_name
        root = self.selected_tree.GetRootItem()
        
        # 清除所有非保护项
        item, cookie = self.selected_tree.GetFirstChild(root)
        while item.IsOk():
            if item not in {self.protected_item}:
                next_item, cookie = self.selected_tree.GetNextChild(root, cookie)
                comp_name = self.selected_tree.GetItemText(item)
                self.unselected_tree.AppendItem(self.unselected_tree.GetRootItem(), comp_name, 1)
                self.selected_tree.Delete(item)
                item = next_item
            else:
                item, cookie = self.selected_tree.GetNextChild(root, cookie)
        
        # 根据模板添加组件
        if template_name == '完整':
            for comp in self.components:
                self.add_component(comp)
            self.set_component(self.components)
        elif template_name == '默认':
            self.set_component([])
        elif template_name == '精简':
            self.set_component([])
    
    def get_component_list(self, index):
        return self.selected_components[index]
    
    def add_component(self, comp_name):
        '''
        配置模板选项
        '''
        root = self.unselected_tree.GetRootItem()
        item, cookie = self.unselected_tree.GetFirstChild(root)
        while item.IsOk():
            if self.unselected_tree.GetItemText(item) == comp_name:
                self.unselected_tree.Delete(item)
                self.selected_tree.AppendItem(self.selected_tree.GetRootItem(), comp_name, 1)
                break
            item, cookie = self.unselected_tree.GetNextChild(root, cookie)

    def set_component(self, components: list):
        '''设置加载组件'''
        self.selected_components = ['clickmouse 主程序'] + components
        
    def on_template_change(self, event):
        selected = self.template_choice.GetStringSelection()
        if selected != '自定义':
            self.apply_template(selected)
    
    def on_add(self, event):
        if self.current_mode != '自定义':
            self.template_choice.SetSelection(3)  # 切换到自定义模式
            self.current_mode = '自定义'
        
        item = self.unselected_tree.GetSelection()
        if not item or item == self.unselected_tree.GetRootItem():
            wx.MessageBox('请先选择要添加的未安装组件', '提示', wx.OK|wx.ICON_INFORMATION)
            return
        
        comp_name = self.unselected_tree.GetItemText(item)
        root = self.selected_tree.GetRootItem()
        self.selected_tree.AppendItem(root, comp_name, 1)
        self.unselected_tree.Delete(item)
    
    def on_remove(self, event):
        if self.current_mode != '自定义':
            self.template_choice.SetSelection(3)  # 切换到自定义模式
            self.current_mode = '自定义'
        
        item = self.selected_tree.GetSelection()
        if not item or item == self.selected_tree.GetRootItem():
            wx.MessageBox('请先选择要移除的已安装组件', '提示', wx.OK|wx.ICON_INFORMATION)
            return
        
        if item == self.protected_item:
            wx.MessageBox('基础模块是系统默认组件，不可移除！', '警告', wx.OK|wx.ICON_WARNING)
            return
        
        comp_name = self.selected_tree.GetItemText(item)
        root = self.unselected_tree.GetRootItem()
        self.unselected_tree.AppendItem(root, comp_name, 1)
        self.selected_tree.Delete(item)
        
    def setStatus(self, text):
        self.status = text
        self.status_text.SetLabel(text)
    
    def on_copy_err(self, event):
        ''' 复制错误信息'''
        pyperclip.copy(f'在{self.status}出现错误，错误信息：\n{self.error}')
        wx.MessageBox('错误信息已复制到剪贴板', '提示', wx.OK | wx.ICON_INFORMATION)
        
    def on_update_button(self, event):
        '''更新按钮状态'''
        self.update_buttons()
        
    def on_checkbox_toggle(self, event):
        '''同意协议'''
        self.not_create_in_start_menu = self.set_start_menu_checkbox.GetValue()
        self.update_buttons()

    def update_buttons(self):
        '''更新按钮状态'''
        self.btn_prev.Show(self.current_page > 0)
        
        if self.current_page >= self.PAGE_FINISH:
            self.btn_next.Hide()
            self.btn_prev.Hide()
            self.btn_cancel.Hide()
            self.btn_exit.Show()
        else:
            self.btn_next.Show()
            self.btn_prev.Show()
            self.btn_cancel.Show()
            self.btn_exit.Hide()
        
        if self.current_page == self.PAGE_START:  # 开始页面
            self.btn_prev.Hide()
        if self.current_page == self.PAGE_READ_LICENSE:  # 说明页面
            self.btn_next.Enable(self.allow_checkbox.GetValue())
        elif self.current_page == self.PAGE_SET_INSTALL_PATH:  # 路径页面
            if os.path.exists('\\'.join(self.path_picker.GetPath().split('\\')[:-1])):
                self.btn_next.Enable(True)
            else:
                self.btn_next.Enable(False)
        elif self.current_page == self.PAGE_SELECT_LINK:  # 快捷方式页面
            self.btn_next.Enable(False)
            if self.set_start_menu_checkbox.GetValue():
                self.btn_next.Enable(True)
            else:
                self.btn_next.Enable(bool(self.set_start_menu_textctrl.GetValue()))
    
            self.set_start_menu_textctrl.Enable(not self.set_start_menu_checkbox.GetValue())
        elif self.current_page == self.PAGE_CHECK_COMPONENT:  # 组件页面
            self.text.SetLabel('\n'.join(self.selected_components))
        elif self.current_page == self.PAGE_INSTALL:  # 进度页面
            self.btn_next.Hide()
            self.btn_prev.Hide()
            self.btn_cancel.Hide()

            self.install()
        elif self.current_page == self.PAGE_ERROR: # 错误页面
            self.error_text.SetLabel(f'错误信息：\n在{self.status}\n错误：{self.error}')
            self.btn_copy_err.Show()
            self.btn_show_sol.Show()
        else:
            self.btn_next.Enable(True)  # 其他页面保持可用
            self.btn_copy_err.Hide()
            self.btn_show_sol.Hide()
        
        self.content_panel.Layout()
        self.Layout()
    
    def run_clickmouse(self, checkbox: wx.CheckBox):
        if checkbox.GetValue():
            try:
                run_software(fr'{self.path_picker.GetPath()}\main.py', fr'{self.path_picker.GetPath()}\main.exe')
                with open(data_path / 'first_run', 'w', encoding='utf-8'):pass
                self.Destroy()
            except Exception as e:
                wx.MessageBox(f'启动失败：{e}，将会关闭此窗口', '提示', wx.OK | wx.ICON_ERROR)
        else:
            exit(0)
        
    def on_close(self, event):
        if self.current_page == self.PAGE_INSTALL:
            wx.MessageBox('正在安装，请等待完成后再退出', '提示', wx.OK | wx.ICON_INFORMATION)
            return
        if self.current_page == self.PAGE_FINISH:
            self.run_clickmouse(self.launch_checkbox)
        if self.current_page == self.PAGE_IS_INSTALLED:
            self.run_clickmouse(self.launch_installed_checkbox)
        if self.current_page >= self.PAGE_CANCEL and self.current_page < self.PAGE_IS_INSTALLED:
            self.Destroy()
            exit(0)
        if self.current_page >= self.PAGE_FINISH:
            self.Destroy()
        else:
            self.update_page(self.PAGE_CANCEL)

    def install(self):
        '''安装程序'''
        # 创建文件夹
        try:
            self.setStatus('初始化...')
            install_path = self.path_picker.GetPath()
            self.setStatus('正在创建包管理器文件...')
            package = []
            package.append(import_package(0, install_location=install_path, create_in_start_menu=not self.set_start_menu_checkbox.GetValue(), create_desktop_shortcut=self.desktop_shortcut.GetValue(), start_menu_name=self.set_start_menu_textctrl.GetValue() if not self.set_start_menu_checkbox.GetValue() else None))
            print(package)
            
            self.setStatus('解压安装包...')
            if 'clickmouse 扩展测试' in self.selected_components:
                package.append(import_package(1, install_location=f'{install_path}/extensions/offical/clickmouse_cli'))
                extract_zip(get_resource_path('packages', 'clickmouse_cli.zip'), f'{install_path}/extensions/offical/clickmouse_cli')

            self.setStatus('正在写入包管理器文件...')
            with open(fr'{install_path}\packages.json', 'w', encoding='utf-8') as f:
                json.dump(package, f)
                
            # 卸载功能敬请期待

            # self.setStatus('正在创建安装信息...')
            # key = winreg.CreateKey(
            #     winreg.HKEY_LOCAL_MACHINE,
            #     r'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\clickmouse'
            # )
            # winreg.SetValue(key, '', winreg.REG_SZ, fr'{install_path}\clickmouse.exe')
            # winreg.SetValueEx(key, 'Path', 0, winreg.REG_SZ, f'{install_path}')
            # winreg.CloseKey(key)

            # self.setStatus('正在创建卸载信息...')
            # uninstall_key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\clickmouse')
            # winreg.SetValueEx(uninstall_key, 'DisplayName', 0, winreg.REG_SZ, 'clickmouse')
            # winreg.SetValueEx(uninstall_key, 'Publisher', 0, winreg.REG_SZ, f'xystudio')
            # winreg.SetValueEx(uninstall_key, 'InstallLocation', 0, winreg.REG_SZ, f'{install_path}')
            # winreg.SetValueEx(uninstall_key, 'UninstallString', 0, winreg.REG_SZ, f'cmd /k echo 卸载功能敬请期待，请前往删除clickmouse安装路径：{install_path}。')
            # winreg.SetValueEx(uninstall_key, 'ModifyString', 0, winreg.REG_SZ, f'cmd /k echo 修改功能敬请期待，请启动clickmouse，找到扩展--官方扩展--修改(未完成)中修改。')
            # winreg.SetValueEx(uninstall_key, 'InstallDate', 0, winreg.REG_SZ, str(datetime.now()))
            # with open(get_resource_path('versions.json'), 'r', encoding='utf-8') as f:
            #     version = json.load(f)['clickmouse']
            # winreg.SetValueEx(uninstall_key, 'DisplayVersion', 0, winreg.REG_SZ, version)
            # try:
            #     winreg.SetValueEx(uninstall_key, 'EstimatedSize', 0, winreg.REG_DWORD, int(get_dir_size_for_reg(install_path)))
            # except:
            #     winreg.SetValueEx(uninstall_key, 'EstimatedSize', 0, winreg.REG_DWORD, int(0))
            # winreg.SetValueEx(uninstall_key, 'NoRepair', 0, winreg.REG_DWORD, 1)
            # winreg.SetValueEx(uninstall_key, 'URLInfoAbout', 0, winreg.REG_SZ, 'https://www.github.com/xystudio/pyclickmouse')
            # winreg.SetValueEx(uninstall_key, 'DisplayIcon', 0, winreg.REG_SZ, fr'{install_path}\res\icons\clickmouse\icon.ico')

            # winreg.CloseKey(uninstall_key)

            self.setStatus('正在创建快捷方式...')
            if package[0]['create_in_start_menu']:
                create_shortcut(fr'C:\ProgramData\Microsoft\Windows\Start Menu\Programs\{package[0]['start_menu_name']}.lnk', fr'{install_path}\clickmouse.exe', '鼠标连点器')
            if package[0]['create_desktop_shortcut']:
                create_shortcut(fr'{os.path.expanduser('~')}\Desktop\clickmouse.lnk', fr'{install_path}\clickmouse.exe', '鼠标连点器')
            self.update_page(self.PAGE_FINISH)
        except Exception as e:
            self.error = e
            wx.MessageBox(f'安装失败: {e}', '错误', wx.OK | wx.ICON_ERROR)
            self.update_page(self.PAGE_ERROR)
    
    def on_confirm(self, event):
        '''确认按钮'''
        self.selected_components = [] # 清空已选组件
        root = self.selected_tree.GetRootItem() # 遍历已选组件
        item, cookie = self.selected_tree.GetFirstChild(root) # 遍历已选组件
        while item.IsOk():
            self.selected_components.append(self.selected_tree.GetItemText(item)) # 添加组件名称到列表
            item, cookie = self.selected_tree.GetNextChild(root, cookie) # 遍历已选组件

    def on_next(self, event):
        '''下一步按钮'''
        if self.current_page == self.PAGE_SET_COMPONENT:
            self.on_confirm(None)
        if self.current_page < self.total_pages - 1:
            self.update_page(self.current_page + 1)
    
    def on_cancel(self, event):
        '''取消按钮'''
        self.update_page(self.PAGE_CANCEL)
    
class SelectLanguage(wx.Frame):
    def __init__(self, parent=None):
        # 初始化
        super().__init__(parent, title='Please select language.', size=(300, 150),style=wx.DEFAULT_FRAME_STYLE & ~(wx.MAXIMIZE_BOX | wx.RESIZE_BORDER | wx.CLOSE_BOX))
        system_lang = parse_system_language_to_lang_id()
        settings['select_lang'] = system_lang
        save_settings(settings)
        self.SetTitle(get_lang('01', system_lang))

        # 窗口初始化
        self.Icon = wx.Icon(str(get_resource_path('icons', 'clickmouse', 'icon.ico')), wx.BITMAP_TYPE_ICO)

        # 创建面板
        panel = wx.Panel(self)

        # 面板控件
        wx.StaticText(panel, -1, get_lang('01', system_lang), pos=(60, 0))
        choices = [i['lang_name'] for i in langs]

        nxt_btn = wx.Button(panel, -1, get_lang('02', system_lang), (200, 80))
        
        self.lang_choice = wx.Choice(panel, -1, (75, 30), choices=choices)
        self.lang_choice.SetSelection(system_lang)
        
        self.lang_choice.Bind(wx.EVT_CHOICE, self.on_choice_change)
        nxt_btn.Bind(wx.EVT_BUTTON, self.on_nxt_btn)
        
    def on_choice_change(self, event):
        settings['select_lang'] = self.lang_choice.GetSelection()
        save_settings(settings)
        
    def on_nxt_btn(self, event):
        self.Close()
        
# 显示窗口
def main(app_name):
    frame = app_name()
    frame.Show()
    app.MainLoop()        

if __name__ == '__main__':
    app = wx.App()
    # 调用GUI工具
    if not get_resource_path('packages'):
        wx.MessageBox('由于每个版本都会更新安装包，未防止git文件夹过大，安装包不会添加，请自行打包（格式必须为zip）并放入res/packages文件夹下。', '错误', wx.OK | wx.ICON_ERROR)
    if is_admin():  # 管理员权限
        if os.path.exists('run_as_admin.json'):
            os.remove('run_as_admin.json')
        if not(check_reg_key(software_reg_key)):
            main(SelectLanguage)
        main(InstallFrame)
    else:
        try:
            with open('run_as_admin.json', 'r') as f:
                data = json.load(f).get('is_not_admin', 0)
        except:
            data = 0
        if data == 0:
            run_as_admin() # 请求管理员权限
        elif data == 1:
            wx.MessageBox('错误', '程序已请求提升权限，但是仍然以非管理员权限运行，请联系系统管理员', wx.OK | wx.ICON_ERROR)
            os.remove('run_as_admin.json')
    app.MainLoop()