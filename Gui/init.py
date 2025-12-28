from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *
import sys
app = QApplication(sys.argv)

import os
from pathlib import Path
import winreg # 注册表编辑
import ctypes # 管理员运行
import pyperclip # 复制错误信息
import win32com.client # 创建快捷方式
import zipfile # 解压文件
import json # 读写json文件
from sharelibs import (get_resource_path, settings, run_software) # 共享库
from uiStyles import PagesUI

with open(get_resource_path('langs', 'init.json'), 'r', encoding='utf-8') as f:
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

icon = QIcon(str(get_resource_path('icons', 'clickmouse', 'icon.ico')))

class InstallWindow(PagesUI):
    def __init__(self):
        super().__init__(['hello'])
        
        self.setWindowTitle('ClickMouse')
        self.setWindowIcon(icon)
        self.setGeometry(100, 100, 500, 375)
        self.setWindowFlags(
            Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint
        ) # 设置窗口属性
        
        self.setFixedSize(self.width(), self.height()) # 固定窗口大小
        
    def init_ui(self):
        """初始化UI"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)  # 移除边距
        main_layout.setSpacing(0)  # 移除间距
        
        # 创建顶部白色区域
        top_widget = QWidget()
        top_widget.setFixedHeight(75)  # 设置顶部高度
        
        # 设置顶部背景色为白色
        top_widget.setAutoFillBackground(True)
        palette = top_widget.palette()
        palette.setColor(QPalette.Window, QColor(255, 255, 255))
        top_widget.setPalette(palette)
        
        # 创建顶部区域的内容布局
        self.top_layout = QHBoxLayout(top_widget)
        
        # 将顶部和内容区域添加到主布局
        main_layout.addWidget(top_widget)
        
        # 页面堆叠控件
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        # 按钮布局
        self.button_layout = QHBoxLayout()
        self.button_layout.addStretch(0)
        
        # 上一步按钮
        self.prev_btn = QPushButton("上一步")
        self.prev_btn.clicked.connect(self.on_prev)
        self.button_layout.addWidget(self.prev_btn)
        
        # 下一步按钮
        self.next_btn = QPushButton("下一步")
        self.next_btn.clicked.connect(self.on_next)
        self.button_layout.addWidget(self.next_btn)
        
        # 取消/完成按钮容器（重叠放置）
        self.action_button_container = QWidget()
        self.action_button_layout = QHBoxLayout(self.action_button_container)
        
        # 取消按钮
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.close)
        self.action_button_layout.addWidget(self.cancel_btn)
        
        # 完成按钮
        self.finish_btn = QPushButton("完成")
        self.finish_btn.clicked.connect(self.close)
        self.action_button_layout.addWidget(self.finish_btn)
        
        self.button_layout.addWidget(self.action_button_container)
        
        main_layout.addLayout(self.button_layout)
        
    def show_page(self, page_index):
        """显示指定页面"""
        page_widget = QWidget()
        page_layout = QVBoxLayout(page_widget)
        
        match page_index:
            case 0:
                # 第一页：欢迎
                page_layout.addWidget(QLabel("欢迎使用ClickMouse安装向导!"))
        
        page_layout.addStretch(1) # 居上显示
        return page_widget

if __name__ == '__main__':
    has_package = True
    if not get_resource_path('packages'):
        QMessageBox.warning(None, '错误', '再编译版安装包不会添加，请自行打包（格式必须为zip）并放入res/packages文件夹下。')
        has_package = False

    if is_admin():  # 管理员权限
        if os.path.exists('run_as_admin.json'):
            os.remove('run_as_admin.json')
        window = InstallWindow()
        window.show()
        sys.exit(app.exec())
    else:
        try:
            with open('run_as_admin.json', 'r') as f:
                data = json.load(f).get('is_not_admin', 0)
        except:
            data = 0
        if data == 0:
            run_as_admin() # 请求管理员权限
        elif data == 1:
            QMessageBox.critical(None, '错误', '程序已请求提升权限，但是仍然以非管理员权限运行，请联系系统管理员')
            os.remove('run_as_admin.json')
            sys.exit(1)