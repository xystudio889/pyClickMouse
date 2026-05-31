# share.py 存储了一些本软件中，多个模块共用的函数和类。

import json
from pathlib import Path
import uiml
from uiml import set_style
from PySide6.QtWidgets import QMessageBox
from PySide6.QtGui import QIcon
from PySide6.QtCore import QThread, Signal
import os
import subprocess
import winreg
import sys
import ctypes
import win32com.client
import hashlib
import re
from typing import *

setting_path = Path('data', 'settings.json')
setting_path.parent.mkdir(parents=True, exist_ok=True)

def _show_message(message, title, status):
    if status == 0:
        QMessageBox.information(None, title, message)
    elif status == 1:
        QMessageBox.warning(None, title, message)
    elif status == 2:
        QMessageBox.critical(None, title, message)
        
def multi_replace(text, replace_dict):
    '''一次性替换多个子串'''
    # 将字典键按长度降序排序，避免长词被短词部分覆盖
    sorted_keys = sorted(replace_dict.keys(), key=len, reverse=True)
    # 构建正则模式，注意转义特殊字符
    pattern = '|'.join(re.escape(key) for key in sorted_keys)
    return re.sub(pattern, lambda m: replace_dict[m.group(0)], text)
        
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
with open(get_resource_path('defaultsetting.json'), 'r', encoding='utf-8') as f:
    default_settings: dict = json.load(f)

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
        print(f'Language {lang_package_id} not found')
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

def run_software(code_path, exe_path, args=None):
    '''
    运行软件
    '''
    args = [] if args is None else args
    subprocess.Popen(f'python {code_path} {' '.join(args)}' if in_dev else f'{exe_path} {" ".join(args)}')
    
def is_dark_mode():
    '''是否是深色模式'''
    try:
        # 打开注册表项
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                            r'SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize', 
                            0, winreg.KEY_READ)
        
        # 读取AppsUseLightTheme值（0表示深色模式，1表示浅色模式）
        value, _ = winreg.QueryValueEx(key, 'AppsUseLightTheme')
        winreg.CloseKey(key)
        
        return value == 0
    except FileNotFoundError:
        return False  # 注册表项不存在时默认浅色模式

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False
    
def run_as_admin(code, exe, args=None):
    args_list = []
    if in_dev:
        args_list.append(code)
    if args:
        args_list.extend(args)
    subprocess.Popen(f'powershell -Command "Start-Process \'{"python" if in_dev else exe}\' {f'-ArgumentList "{' '.join(args_list)}"' if args_list else ''} -Verb RunAs"')
    
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
    
with open(get_resource_path('langs', 'units.json'), 'r', encoding='utf-8') as f:
    unit_lang = json.load(f)
 
__author__ = 'xystudio'
is_pre = ('alpha' in __version__) or ('beta' in __version__) or ('dev' in __version__) or ('rc' in __version__)

def get_icon(icon_name): 
    icon_folder = 'clickmouse_pre' if is_pre else 'clickmouse'
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

def get_has_plural():
    return langs[settings.get('select_lang', 0)]['has_plural']

def plural(count, value, plural):
    if has_plural:
        return value if count == 1 else plural
    else:
        return value

has_plural = get_has_plural()

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

def get_file_hash(file_path, algorithm):
    '''
    计算文件的哈希值
    
    参数:
        file_path: 文件路径
        algorithm: 哈希算法，可选值: 'md5', 'sha1', 'sha256', 'sha512'等
    
    返回:
        文件的十六进制哈希字符串
    '''
    hash_func = hashlib.new(algorithm)
    
    try:
        with open(file_path, 'rb') as f:
            # 分块读取大文件，避免内存溢出
            for chunk in iter(lambda: f.read(4096), b''):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except FileNotFoundError:
        return None
    except Exception as e:
        raise Exception(f'计算哈希时出错: {e}')
        return None
    
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
        
def widget_replacer(ui_data: str):
    '''
    替换UI中的widget，使用函数式返回
    '''
    if ui_data.startswith('!lang '):
        return get_lang(ui_data[6:]) # 语言解析
    else:
        uiml.default_replacer(ui_data) # 交由uiml进行替换
        
def layout_parser(ui_data: Dict[str, Any]):
    if ui_data.get('direction').lower() == 'u':
        input_compiled_list = []
        # 索引0 -- 字
        # 索引1 -- 输入框
        # 索引2 -- 选择框
        inputs = ui_data['content'][1]
        for input in inputs['content']:
            input_compiled_list.append(uiml.compile_ui(input)) # 递归解析
        combos = ui_data['content'][2] # 组合框
        combos_compiled_list = []
        for combo in combos['content']:
            combos_compiled_list.append(uiml.compile_ui(combo)) # 递归解析
        return {'name': ui_data.get('name'), 'direction': ui_data.get('direction'), "texts": ui_data['content'][0]['values'], 'inputs': input_compiled_list, 'combos': combos_compiled_list}
    return uiml.default_layout_parser(ui_data) # 交由uiml进行替换

uiml.set_namespace(value_replace_func=widget_replacer, layout_parser_func=layout_parser) # 设置uiml的控制函数

class UIWindow(uiml.UIMLLayout):
    def __init__(self, list=None):
        super().__init__(list)
        
    def find_widget(self, path: str, data=None):
        '''
        在嵌套字典结构中按点分隔路径查找元素。

        规则：
        - 路径中的每一段对应字典中的 'name' 字段。
        - 若当前节点是布局（含有 'direction' 键），且不是最后一段，则自动进入其子元素继续查找。
        - 普通布局（direction 非 'u'）的子元素在 'content' 列表中。
        - 特殊布局（direction == 'u'）的子元素在 'inputs' 和 'combos' 列表中（'texts' 不参与导航）。
        - 最后一段如果是普通布局，返回其 'content' 列表；如果是 'u' 布局，返回 {'texts':..., 'inputs':..., 'combos':...}；如果是控件，返回其 'content'。
        - 路径必须完整且精确，找不到时抛出 KeyError。

        参数:
            path: 点分隔的路径字符串，如 "layout.vlayout.checkbox2"
            data: 根字典（例如 {'name': 'layout', 'direction': 'h', 'content': [...]}）

        返回:
            根据路径找到的控件对象、布局的 content 列表，或 'u' 布局的 texts/inputs/combos 字典。
        '''
        data = self.list if data is None else data
        parts = path.split('.')
        if not parts:
            raise ValueError("Empty path")

        # 根节点名称必须匹配第一段
        if data.get('name') != parts[0]:
            raise KeyError(f"Root name mismatch: expected '{parts[0]}', got '{data.get('name')}'")

        current = data

        for i, part in enumerate(parts):
            # 检查当前节点名称是否匹配
            if current.get('name') != part:
                raise KeyError(f"Name mismatch: expected '{part}', got '{current.get('name')}'")

            # 最后一段
            if i == len(parts) - 1:
                if 'direction' in current:
                    direction = current.get('direction', '').lower()
                    if direction == 'u':
                        # 特殊布局：返回 texts、inputs、combos 组成的字典
                        return {
                            'texts': current.get('texts', []),
                            'inputs': current.get('inputs', []),
                            'combos': current.get('combos', [])
                        }
                    else:
                        # 普通布局：返回 content 列表
                        content = current.get('content')
                        if content is None:
                            raise ValueError(f"Layout '{part}' has no content")
                        if not isinstance(content, list):
                            raise TypeError(f"Layout '{part}' content is not a list")
                        return content
                else:
                    # 控件：返回 content 属性
                    content = current.get('content')
                    if content is None:
                        raise ValueError(f"Widget '{part}' has no content")
                    return content

            # 不是最后一段，当前节点必须是布局
            if 'direction' not in current:
                raise KeyError(f"'{part}' is not a layout, cannot traverse further")

            direction = current.get('direction', '').lower()
            next_name = parts[i + 1]
            found = None

            if direction == 'u':
                # 从 inputs 和 combos 中查找子元素
                for child in current.get('inputs', []) + current.get('combos', []):
                    if child.get('name') == next_name:
                        found = child
                        break
            else:
                # 普通布局从 content 中查找
                for child in current.get('content', []):
                    if child.get('name') == next_name:
                        found = child
                        break

            if found is None:
                raise KeyError(f"Child '{next_name}' not found in layout '{part}'")
            current = found

        # 正常流程不会执行到这里
        return None

    def extend_layout(self, list_info):
        if list_info['direction'].lower() == 'u':
            from uiStyles.widgets import UnitInputLayout
            layout = UnitInputLayout()
            for text, input, combo in zip(list_info['texts'], list_info['inputs'], list_info['combos']):
                if text.startswith('!lang '): # 语言解析
                    text = get_lang(text[6:])
                layout.addUnitRow(text, input['content'], combo['content'])
            return layout, 'layout'
        else:
            uiml.WidgetError.direction_error() # 交由 uiml 进行处理