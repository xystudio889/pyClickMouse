# share.py 存储了一些本软件中，多个模块共用的函数和类。

import json
from pathlib import Path
import wx
import os
import subprocess

setting_path = Path('data', 'settings.json')
setting_path.parent.mkdir(parents=True, exist_ok=True)

def _show_message(message, title, style):
    temp_app = wx.App()
    wx.MessageBox(message, title, style)
    temp_app.Destroy()

try:
    lang_path = Path('res', 'langs.json')
    with open(lang_path, 'r', encoding='utf-8') as f:
        langs = json.load(f)
except FileNotFoundError:
    _show_message('资源损坏: 语言文件丢失', '错误', wx.OK | wx.ICON_ERROR)
    exit(1)
except json.JSONDecodeError:
    _show_message('资源损坏: 语言文件格式错误', '错误', wx.OK | wx.ICON_ERROR)
    exit(1)
    
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
        _show_message(f'资源文件损坏: {e}', '错误', wx.OK | wx.ICON_ERROR)
        exit(1)

in_dev = os.path.exists('dev_list/in_dev') # 是否处于开发模式

def run_software(code_path, exe_path):
    '''
    运行软件
    '''
    subprocess.Popen(f'python {code_path}' if in_dev else f'start {exe_path}')