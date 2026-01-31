# share.py 存储了一些本软件中，多个模块共用的函数和类。

import json
from pathlib import Path
from PySide6.QtWidgets import QMessageBox
from PySide6.QtGui import QIcon
import os
import subprocess
import winreg
import sys
import ctypes
import win32com.client

setting_path = Path('data', 'settings.json')
setting_path.parent.mkdir(parents=True, exist_ok=True)

def _show_message(message, title, status):
    if status == 0:
        QMessageBox.information(None, title, message)
    elif status == 1:
        QMessageBox.warning(None, title, message)
    elif status == 2:
        QMessageBox.critical(None, title, message)
        
def get_resource_path(*paths):
    '''
    获取资源文件路径
    '''
    try:
        resource = Path('res') # 获取当前目录的资源文件夹路径
        if not resource.exists():
            raise FileNotFoundError('Resource folder missing: res not found')
        return str(resource.joinpath(*paths))
    except Exception as e:
        _show_message(f'Resource file missing: {e}', 'Error', 2)
        sys.exit(1)

try:
    lang_path = Path('res', 'langs')
    with open(lang_path / 'langs.json', 'r', encoding='utf-8') as f:
        langs = json.load(f)
        
    with open(lang_path / 'control.json', 'r', encoding='utf-8') as f:
        control_langs = json.load(f)
    
    with open(lang_path / 'init.json', 'r', encoding='utf-8') as f:
        init_langs = json.load(f)
except FileNotFoundError:
    _show_message('Resource file missing: langs not found', 'Error', 2)
    sys.exit(1)
except json.JSONDecodeError:
    _show_message('Resource file damaged: langs format error', 'Error', 2)
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
with open(get_resource_path('vars', 'mem_id.json'), 'r') as f:
    mem_id = json.load(f)

def get_lang(lang_package_id, lang_id = None, source = None):
    source = langs if source is None else source
    lang_id = settings.get('select_lang', 0) if lang_id is None else lang_id
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

def get_control_lang(lang_id):
    return get_lang(lang_id, source=control_langs)

def get_init_lang(lang_id, lang_pack_id=system_lang):
    return get_lang(lang_id, lang_pack_id, source=init_langs)

def get_inst_lang(lang_id):
    return get_init_lang(lang_id, settings.get('select_lang', 0))

in_dev = os.path.exists('dev_list/in_dev') # 是否处于开发模式

def run_software(code_path, exe_path):
    '''
    运行软件
    '''
    subprocess.Popen(f'python {code_path}' if in_dev else f'{exe_path}')
    
def is_dark_mode():
    '''是否是深色模式'''
    try:
        # 打开注册表项
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize", 
                            0, winreg.KEY_READ)
        
        # 读取AppsUseLightTheme值（0表示深色模式，1表示浅色模式）
        value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        winreg.CloseKey(key)
        
        return value == 0
    except FileNotFoundError:
        return False  # 注册表项不存在时默认浅色模式

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False
    
def run_as_admin(code, exe):
    subprocess.Popen(f'powershell -Command "Start-Process \'{"python" if in_dev else exe}\' {f'-ArgumentList "{code}"' if in_dev else ''} -Verb RunAs"')
    
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

with open(get_resource_path('versions.json'), 'r') as f:
    __version__ = json.load(f)['clickmouse']
 
__author__ = 'xystudio'
is_pre = ('alpha' in __version__) or ('beta' in __version__) or ('dev' in __version__) or ('rc' in __version__)

def get_icon(icon_name):
    icon_folder = 'clickmouse_pre' if is_pre else 'clickmouse'
    return QIcon(get_resource_path('icons', icon_folder, f'{icon_name}.ico'))

with open('res/langs/default_button_text.json', 'r', encoding='utf-8') as f:
    default_button_text = json.load(f)