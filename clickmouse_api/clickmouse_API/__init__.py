# share.py 存储了一些本软件中，多个模块共用的函数和类。
raise NotImplementedError('未完成！请等待第三方扩展功能上线！')
import json
import os
from packageParser import packages
from pathlib import Path
import subprocess
import warnings
import winreg

setting_path = Path('data', 'settings.json')
setting_path.parent.mkdir(parents=True, exist_ok=True)

in_dev = None
resource = None # 获取当前目录的资源文件夹路径
lang_path = None

def reloadData():
    '''
    重新加载数据
    '''
    global langs

    with open(lang_path, 'r', encoding='utf-8') as f:
        langs = json.load(f)
        
def check_clickmouse_installed():
    software_reg_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\clickMouse'
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, software_reg_key, 0, winreg.KEY_READ):
            return True
    except:
        warnings.warn('ClickMouse未安装，部分功能将不可用，请前往github.com/xystudio889/pyclickmouse/releases 下载安装。', UserWarning)
        return False
        
check_clickmouse_installed()

try:
    pass
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
    try:
        for i in langs:
            if i['lang_id'] == 0: # 设置默认语言包
                lang_text = i['lang_package']
            if i['lang_id'] == lang_id: # 设置目前语言包
                lang_text = i['lang_package']
    except KeyError:
        raise ValueError('非法的语言包，语言包格式请参考文档。')
    try:
        return lang_text[lang_package_id]
    except KeyError:
        return 'Language not found'
    
def get_resource_path(*paths):
    '''
    获取资源文件路径
    '''
    try:
        if not resource.exists():
            raise FileNotFoundError('资源文件出现损坏')
        return str(resource.joinpath(*paths))
    except Exception as e:
        _show_message(f'资源文件损坏: {e}', '错误', wx.OK | wx.ICON_ERROR)
        exit(1)

def init(dev_path=False, lang_path=None, resource_path=None):
    global in_dev, langs, resource

    if lang_path is not None:
        in_dev = os.path.exists(dev_path)
    if resource_path is not None:
        with open(lang_path, 'r', encoding='utf-8') as f:
            langs = json.load(f)
    if resource_path is not None:
        resource = Path(resource_path)
        

def runSoftware(code_path, exe_path = None):
    '''
    运行软件
    '''
    subprocess.Popen(f'python {code_path}' if in_dev else f'start {exe_path}')