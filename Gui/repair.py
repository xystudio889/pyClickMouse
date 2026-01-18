from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
import psutil
from shutil import rmtree
import os
import winreg
from sharelibs import get_control_lang, get_resource_path, is_admin
import json
import sys

def is_process_running(process_name):
   for proc in psutil.process_iter(['name']):
       if proc.info['name'] == process_name:
           return True
   return False

def remove_file(file_path):
    try:
        os.remove(file_path)
    except:
        pass

def remove_folder(folder_path):
    try:
        rmtree(folder_path)
    except Exception as e:
        pass
    
def remove_reg_key(sub_key):
    root_key = winreg.HKEY_LOCAL_MACHINE
    try:
        # 以写入权限打开父键
        parent_key = winreg.OpenKey(root_key, sub_key, 0, winreg.KEY_ALL_ACCESS)
        
        # 先删除所有子项（递归处理）
        while True:
            try:
                child_subkey = winreg.EnumKey(parent_key, 0)  # 获取第一个子项
                remove_reg_key(root_key, f"{sub_key}\\{child_subkey}")
            except OSError:  # 没有更多子项时抛出OSError
                break
        
        # 删除所有键值
        while True:
            try:
                value_name = winreg.EnumValue(parent_key, 0)[0]  # 获取第一个键值名
                winreg.DeleteValue(parent_key, value_name)
            except OSError:  # 没有更多键值时抛出OSError
                break
        
        # 关闭父键后删除空项
        winreg.CloseKey(parent_key)
        winreg.DeleteKey(root_key, sub_key)
    except:
        pass

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(get_control_lang('0b'))
        self.setGeometry(0, 0, 880, 250)
        self.setWindowIcon(QIcon(get_resource_path('icons', 'clickmouse', 'icon.ico')))
        self.setFixedSize(self.width(), self.height())
        self.init_ui()

    def init_ui(self):
        # 创建面板
        widget = QWidget()
        self.setCentralWidget(widget)
        layout = QGridLayout(widget)
        # 从json读取缓存列表
        cache_list = {}
        
        with open(get_resource_path('vars', 'repair.json'), 'r', encoding='utf-8') as f:
            load_cache = json.load(f)
            
        file = QLabel(get_control_lang('0c'))
        path = QLabel(get_control_lang('0d'))
        dest = QLabel(get_control_lang('0e'))
        # 布局2
        layout.addWidget(file, 0, 0)
        layout.addWidget(path, 0, 1)
        layout.addWidget(dest, 0, 2)
        
        # 解析缓存源文件
        for k, v in load_cache.items():
            if k.startswith(' '):
                cache_list[get_control_lang(k[1:])] = [] # 初始化空项
                k_is_lang = True
            else:
                cache_list[k] = []
                k_is_lang = False
            for value in v:
                if type(value) is str and value.startswith(' '):
                    if k_is_lang:
                        cache_list[get_control_lang(k[1:])].append(get_control_lang(value[1:]))
                    else:
                        cache_list[k].append(get_control_lang(value[1:]))
                else:
                    if k_is_lang:
                        cache_list[get_control_lang(k[1:])].append(value)
                    else:
                        cache_list[k].append(value)

        self.cache_dir_list = {'logs'} # 缓存文件路径的列表
        self.cache_file_list = {'update.json'} # 缓存文件列表

        self.checkbox_list: list[QCheckBox] = [] # 缓存文件选择框的列表
        self.cache_path_list: list[QLabel] = [] # 文件路径字符的列表

        for i, d in enumerate(cache_list.items()): # 遍历缓存列表
            k = d[0]
            v = d[1]
            box = QCheckBox(k)
            self.checkbox_list.append(box)
            path = QLabel(v[0])
            self.cache_path_list.append(path)
            dest = QLabel(v[1]) # 加载文件描述
            
            line = i + 4
            layout.addWidget(box, line, 0)
            layout.addWidget(path, line, 1)
            layout.addWidget(dest, line, 2)
        
        # 按钮
        ok = QPushButton(get_control_lang('0f'))
        clean_cache = QPushButton(get_control_lang('10'))
        
        # 布局4
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch(1)
        bottom_layout.addWidget(clean_cache)
        bottom_layout.addWidget(ok)
        
        layout.addLayout(bottom_layout, line + 1, 2)

        # 绑定事件
        clean_cache.clicked.connect(self.on_repair)
        ok.clicked.connect(self.close)

        print(self.width(), self.height())


    def on_repair(self):
        '''修复'''
        message = QMessageBox.information(None, get_control_lang('04'), get_control_lang('09'), QMessageBox.Yes | QMessageBox.No)
        if message == QMessageBox.Yes:
            check_list = list(map(lambda x: x.isChecked(), self.checkbox_list))
            if check_list[0]:
                for root, dirs, files in os.walk('cache'):
                    for dir in dirs:
                        remove_folder(os.path.join(root, dir))
                    for file in files:
                        if file not in {'update.json', 'update_log.md'}:
                            remove_file(os.path.join(root, file))
            if check_list[1]:
                remove_file('cache/update.json')
                remove_file('cache/update_log.md')
            if check_list[2]:
                with open('packages.json', 'w', encoding='utf-8') as f:
                    json.dump(['xystudio.clickmouse'], f)
                remove_folder('extensions')
            if check_list[3]:
                remove_reg_key('SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\clickmouse')
                remove_reg_key('SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\clickmouse')
            if check_list[4]:
                for root, dirs, files in os.walk('data'):
                    for dir in dirs:
                        remove_folder(os.path.join(root, dir))
                    for file in files:
                        if file not in {'first_run'}:
                            remove_file(os.path.join(root, file))
            if check_list[5]:
                remove_file('data/first_run')
            
        QMessageBox.information(None, get_control_lang('04'), get_control_lang('0a'))
        self.close()

if __name__ == '__main__':
    app = QApplication()
    with open('packages.json', 'r', encoding='utf-8') as f:
        packages = json.load(f)
    if 'xystudio.clickmouse.repair' in packages:
        if is_process_running('main.exe'):
            QMessageBox.warning(None, get_control_lang('04'), get_control_lang('08'))
        else:
            if is_admin():
                window = MainWindow()
                window.show()
            else:
                QMessageBox.critical(None, get_control_lang('04'), get_control_lang('07'))
                sys.exit(1)
    else:
        QMessageBox.critical(None, get_control_lang('04'), get_control_lang('11'))
    sys.exit(app.exec())