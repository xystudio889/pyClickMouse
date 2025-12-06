# share.py 存储了一些本软件中，多个模块共用的函数和类。

import json
from pathlib import Path
from PySide6.QtWidgets import QMessageBox
import os
import subprocess
import winreg

setting_path = Path('data', 'settings.json')
setting_path.parent.mkdir(parents=True, exist_ok=True)

def _show_message(message, title, status):
    if status == 0:
        QMessageBox.information(None, title, message)
    elif status == 1:
        QMessageBox.warning(None, title, message)
    elif status == 2:
        QMessageBox.critical(None, title, message)

try:
    lang_path = Path('res', 'langs.json')
    with open(lang_path, 'r', encoding='utf-8') as f:
        langs = json.load(f)
except FileNotFoundError:
    _show_message('资源损坏: 语言文件丢失', '错误', 2)
    exit(1)
except json.JSONDecodeError:
    _show_message('资源损坏: 语言文件格式错误', '错误', 2)
    exit(1)
    
def get_style_sheet(style_name: str) -> str:
    '''
    获取样式表
    '''
    try:
        with open(get_resource_path('styles', f'{style_name}.qss'), 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f'样式表{style_name}.qss不存在')
    
def replace_style_sheet(style_sheet: str, style_tag: str, old_style: str, new_style: str) -> str:
    '''
    替换样式表
    '''
    old_style_tag = f'{style_tag}: {old_style}'
    new_style_tag = f'{style_tag}: {new_style}'
    return style_sheet.replace(old_style_tag, new_style_tag)
    
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
    
def get_resource_path(*paths):
    '''
    获取资源文件路径
    '''
    try:
        resource = Path('res') # 获取当前目录的资源文件夹路径
        if not resource.exists():
            raise FileNotFoundError('资源文件出现损坏')
        return str(resource.joinpath(*paths))
    except Exception as e:
        _show_message(f'资源文件损坏: {e}', '错误', 2)
        exit(1)

in_dev = os.path.exists('dev_list/in_dev') # 是否处于开发模式

def run_software(code_path, exe_path):
    '''
    运行软件
    '''
    subprocess.Popen(f'python {code_path}' if in_dev else f'start {exe_path}')
    
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
