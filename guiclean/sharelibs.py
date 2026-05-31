# share.py 存储了一些本软件中，多个模块共用的函数和类。

import json
from pathlib import Path
from PySide6.QtGui import QIcon
from PySide6.QtCore import QThread, Signal
import os
import subprocess
import winreg
import win32com.client
import sys

setting_path = Path('data', 'settings.json')
setting_path.parent.mkdir(parents=True, exist_ok=True)
        
def get_resource_path(*paths):
    '''
    获取资源文件路径
    '''
    try:
        resource = Path('res') # 获取当前目录的资源文件夹路径
        if not resource.exists():
            raise FileNotFoundError('Resource folder missing: res not found')
        return str(resource.joinpath(*paths))
    except Exception:
        sys.exit(1)

try:
    lang_path = Path('res', 'langs')
    with open(lang_path / 'langs.json', 'r', encoding='utf-8') as f:
        langs = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    sys.exit(1)
    
def load_settings():
    '''
    加载设置
    '''
    try:
        with open(setting_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)
        return settings
    except FileNotFoundError:
        with open(setting_path, 'w', encoding='utf-8') as f:
            f.write('{}')
        return {}
    
settings = load_settings()
with open(get_resource_path('defaultsetting.json'), 'r', encoding='utf-8') as f:
    default_settings: dict = json.load(f)

def create_shortcut(path, target, description, work_dir = None, icon_path = None):
    # 创建快捷方式
    try:
        icon_path = target if icon_path is None else icon_path
        work_dir = os.path.dirname(target) if work_dir is None else work_dir
        
        shell = win32com.client.Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.TargetPath = target # 目标程序
        shortcut.WorkingDirectory = work_dir # 工作目录
        shortcut.IconLocation = icon_path # 图标（路径,图标索引）
        shortcut.Description = description # 备注描述
        shortcut.Save()
    except:
        pass

def get_lang(lang_package_id, lang_id = None, source = None):
    source = langs if source is None else source
    lang_id = settings.get('select_lang', system_lang) if lang_id is None else lang_id
    for i in source:
        if i['lang_id'] == 0: # 设置默认语言包
            default_lang_text = i['lang_package']
        if i['lang_id'] == lang_id: # 设置目前语言包
            lang_text = i['lang_package']
    try:
        return lang_text[lang_package_id]
    except KeyError:
        print(f'{lang_package_id} not found')
        return 'Language not found'
    except UnboundLocalError:
        lang_text = {}
        return lang_text.get(lang_package_id, default_lang_text[lang_package_id])
    
def get_system_language():
    '''通过Windows注册表获取系统语言'''
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Control Panel\International')
        lang, _ = winreg.QueryValueEx(key, 'LocaleName')
        return lang
    except Exception:
        return 'en-US'
    
def parse_system_language_to_lang_id():
    '''将系统语言转换为语言ID'''
    system_lang = get_system_language()
    for i in langs:
        if i.get('lang_system_name', 'en-US') == system_lang:
            return i['lang_id']
    return 0

system_lang = parse_system_language_to_lang_id()

in_dev = os.path.exists('dev_list/in_dev') # 是否处于开发模式

def run_software(code_path, exe_path, args=None):
    '''
    运行软件
    '''
    args = [] if args is None else args
    subprocess.Popen(f'python {code_path} {' '.join(args)}' if in_dev else f'{exe_path} {" ".join(args)}')

__version__ = '3.2.3.22'
    
with open(get_resource_path('langs', 'units.json'), 'r', encoding='utf-8') as f:
    unit_lang = json.load(f)
 
__author__ = 'xystudio'

def get_icon(icon_name): 
    icon_folder = 'clickmouse'
    return QIcon(get_resource_path('icons', icon_folder, f'{icon_name}.ico'))

with open('res/langs/default_button_text.json', 'r', encoding='utf-8') as f:
    default_button_text = json.load(f)
    
def init_units():
    '''初始化单位'''
    units = {'ms': 1}
    units['s'] = units['ms'] * 1000
    units['min'] = units['s'] * 60
    units['h'] = units['min'] * 60
    units['d'] = units['h'] * 24

    return units

def init_size_units():
    '''初始化大小单位'''
    units = {'B': 1}
    units['KB'] = units['B'] * 1024
    units['MB'] = units['KB'] * 1024
    
    return units

units = init_units()
size_units = init_size_units()

def get_unit_value(value, unit_list = units, min_unit = 'ms', max_unit = 'd'):
    unit = 1
    unit_text = get_lang(min_unit, source=unit_lang)
    for k, v in unit_list.items():
        if value >= v:
            unit_text = get_lang(k, source=unit_lang)
            unit = v

    if unit_text == get_lang(max_unit, source=unit_lang):
        unit_text = get_lang(max_unit, source=unit_lang)
    return (round(value / unit, 2), unit_text)

def get_unit_text(value, unit_list = units, min_unit = 'ms', max_unit = 'd'):
    '''
    获取单位文本
    '''
    return ''.join(map(lambda x: str(x), get_unit_value(value, unit_list, min_unit, max_unit)))

def get_size_value(value):
    return get_unit_value(value, size_units, 'B', 'MB')

def get_size_text(value):
    return get_unit_text(value, size_units, 'B', 'MB')

class QtThread(QThread):
    '''检查更新工作线程'''
    finished = Signal(object) # 爬取完成信号

    def __init__(self, func, args=(), kwargs={}, parent=None):
        super().__init__(parent)
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        '''线程执行函数'''
        result = self.func(*self.args, **self.kwargs)
        self.finished.emit(result)