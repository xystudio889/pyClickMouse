import json
import os
from pathlib import Path
import pyperclip
from sharelibs import (get_resource_path, get_lang)
import win32com.client
import winreg
import wx
import zipfile
from uiStyles import PagesUI

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

with open('packages.json', 'r', encoding='utf-8') as f:
    packages_source = json.load(f)
    
with open(get_resource_path('package_info.json'), 'r', encoding='utf-8') as f:
    packages_info = json.load(f)

def get_packages():
    package_index = [] # 包索引
    package_path = [] # 包路径
    package_map = {} # 包映射
    
    # 加载包信息
    for package in packages_source:
        package_path.append(package.get('install_location', None))
        package_index.append(get_lang(package.get('package_name_in_select_index', None)))
        package_map[package['package_id']] = packages_source.index(package)
    return (package_path, package_index, package_map)

def get_list_diff(list1: list, list2: list) -> list:
    '''
    获取两个列表的差集

    :param list1: 列表1
    :param list2: 列表2
    :return: 他们的差集，如果是list2中增加了元素，则返回'+多的元素'，如果在list2中删除了元素，则返回'-少的元素'
    '''
    set1 = set(list1)
    set2 = set(list2)
   
    diff_list = []

    for i in set1 - set2:# 被删除元素集合
        diff_list.append(f"-{i}")

    for i in set2 - set1:# 被添加元素集合
        diff_list.append(f"+{i}")
    
    return diff_list

def import_package(package_id, **config):
    global package_map, packages_source
    
    packages_source.append(packages_info[package_id])
    packages_source[-1].update(config)
    package_map = update_map()
    
def remove_package(package_id: int):
    '''移除包信息'''
    global package_map

    for k, v in package_map.items():
        if k == package_id:
            del packages_source[v]
    temp_package_map = update_map()
    package_map = temp_package_map.copy()
    
def update_map():
    '''更新包映射'''
    package_map = {}
    for package in packages_source:
        package_map[package['package_id']] = packages_source.index(package)
    return package_map

install_path, packages, package_map = get_packages()

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
        self.init_pages(['PAGE_START', 'PAGE_SET_COMPONENT', 'PAGE_CHECK_COMPONENT', 'PAGE_INSTALL', 'PAGE_FINISH', 'PAGE_CANCEL', 'PAGE_ERROR'])
        
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

        
    def init_show(self):
        self.main_sizer.Add(self.title_panel, 1, wx.EXPAND | wx.TOP | wx.Center, 5)
        self.content = self.main_sizer.Add(self.content_panel, 5, wx.EXPAND)
        self.btn = self.main_sizer.Add(self.btn_panel, 1, wx.ALIGN_RIGHT | wx.BOTTOM, 10)
    
    def draw_page(self, index):
        match index:
            case self.PAGE_START:
                wx.StaticText(self.panel, label='欢迎使用 clickMouse 更改扩展向导!\n\n这个程序将简单的使用几分钟时间，帮助你完成更改扩展。\n点击下一步开启安装助手。', pos=(5, 0))
            case self.PAGE_SET_COMPONENT:
                self.selected_components = ['clickmouse 主程序']
                self.protected_item = None
                self.current_mode = '当前'
                
                sizer = wx.BoxSizer(wx.VERTICAL)
                select_sizer = wx.BoxSizer(wx.HORIZONTAL)
                
                # 左侧未选择树形控件
                self.unselected_tree = self.create_tree(self.panel, '未安装组件')
                select_sizer.Add(self.unselected_tree, 3, wx.EXPAND | wx.ALL, 5)
                
                # 中间按钮区域
                btn_panel = wx.Panel(self.panel)
                btn_sizer = wx.BoxSizer(wx.VERTICAL)
                
                # 添加模板选择器
                choises = ['完整', '默认', '精简', '当前', '自定义']
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
                self.apply_template('当前')
            case self.PAGE_CHECK_COMPONENT:
                sizer = wx.BoxSizer(wx.VERTICAL)
                
                title = wx.StaticText(self.panel, label='您已更改的组件：')
                sizer.Add(title, 1, wx.ALL | wx.EXPAND, 10)
                
                self.text = wx.StaticText(self.panel, label='正在加载组件列表...', pos=(5, 30))
                sizer.Add(self.text, 15, wx.EXPAND | wx.LEFT | wx.RIGHT, 20)
                
                self.panel.SetSizer(sizer)
            case self.PAGE_INSTALL:
                wx.StaticText(self.panel, label='正在安装clickmouse, 请稍候...', pos=(5, 0))
                self.status_text = wx.StaticText(self.panel, label='安装进度', pos=(5, 30))
            case self.PAGE_FINISH:
                wx.StaticText(self.panel, label='安装完成！点击确定退出安装向导。', pos=(5, 0))
            case self.PAGE_CANCEL:
                wx.StaticText(self.panel, label='安装已取消！点击确定退出安装向导。', pos=(5, 0))
            case self.PAGE_ERROR:
                wx.StaticText(self.panel, label='安装失败！点击确定退出安装向导。', pos=(5, 0))
                self.error_text = wx.StaticText(self.panel, label=f'错误信息：\n在{self.status}时候错误\n错误信息：{self.error}', pos=(5, 30))
        
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
        self.components = ['clickmouse 扩展测试', 'b']
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
        elif template_name == '当前':
            for comp in packages[1:]:
                self.add_component(comp)
            self.set_component(packages[1:])
    
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
            self.template_choice.SetSelection(4)  # 切换到自定义模式
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
            self.template_choice.SetSelection(4)  # 切换到自定义模式
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
        elif self.current_page == self.PAGE_CHECK_COMPONENT:  # 组件页面
            self.text.SetLabel('\n'.join(self.selected_change) if self.selected_change else '没有更改的组件')
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
        
    def on_close(self, event):
        if self.current_page == self.PAGE_INSTALL:
            wx.MessageBox('正在安装，请等待完成后再退出', '提示', wx.OK | wx.ICON_INFORMATION)
            return
        if self.current_page >= self.PAGE_CANCEL:
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
            if not self.selected_change:
                self.update_page(self.PAGE_FINISH)
                return
            wx.MessageBox('提示：此版本不会进行任何的包更改，将在后续测试版支持。')
            remove = []
            add = []
            self.setStatus('检查需要更新的文件...')
            for comp in self.selected_change:
                if comp.startswith('-'):
                    remove.append(comp[1:])
                elif comp.startswith('+'):
                    add.append(comp[1:])
                    
            print(remove, add)

            # self.update_page(self.PAGE_FINISH)
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
            
        self.selected_change = get_list_diff(packages, self.selected_components)

    def on_next(self, event):
        '''下一步按钮'''
        if self.current_page == self.PAGE_SET_COMPONENT:
            self.on_confirm(None)
        if self.current_page < self.total_pages - 1:
            self.update_page(self.current_page + 1)
    
    def on_cancel(self, event):
        '''取消按钮'''
        self.update_page(self.PAGE_CANCEL)
        
if __name__ == '__main__':
    app = wx.App()
    frame = InstallFrame()
    frame.Show()
    app.MainLoop()