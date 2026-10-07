# 加载ui框架
from PySide6.QtWidgets import QApplication
import sys
from logger import Logger, logging, ExceptionVal
app = QApplication(sys.argv)
logger = Logger('clickmouse.main')

# 加载框架
try:
    from sharelibs import * # 共享库
except:
    logger.exception('clickmouse.main', mode=ExceptionVal.all)
from uiStyles.QUI import *
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEngineScript
from uiStyles import *
from datetime import datetime # 检查时间
from pynput import keyboard # 热键功能库
import pyautogui # 鼠标操作库
from time import sleep, time # 延迟
from check_update import check_update, web_data, download_file # 更新检查
from uiStyles import indexes as style_indexes
from sharelibs import __version__ # 版本号
import winreg # 注册表库
import math # 数学库
import colorsys # 颜色库
import struct # 字节处理库
import pytz # 时区库
from traceback import format_exc # 异常格式化
from itertools import chain # 迭代器库
import platform # 系统信息
from txtinfo import *
import os # 系统库
import shutil # 用于删除文件夹
import json # 用于读取json文件
from pathlib import Path # 路径库

# 系统api
import ctypes
from ctypes import wintypes

# TODO: 添加更多更新设置，使用hashlib.algorithms_available获取支持的hash算法

@logger.auto_logger()
def get_windows_version():
    '''获取winmdows版本'''
    # 检查系统
    if sys.platform != 'win32':
        return
    
    version = platform.win32_ver()[1]
    major_version = int(version.split('.')[0])
    build_number = int(version.split('.')[2]) if len(version.split('.')) > 2 else 0
    if major_version == 10: # win10或win11
        if build_number >= 22000: # win11初始版本为22000
            return 11
        else:
            return 10
    else:
        return major_version

@logger.auto_logger()
def filter_hotkey(text:str):
    return text.split('(')[0]

@logger.auto_logger('clickmouse.update')
def load_update_cache():
    '''
    加载更新缓存文件
    '''
    service = 'clickmouse.update'
    if update_cache_path.exists():
        with open(update_cache_path, 'r', encoding='utf-8') as f:
            cache = json.load(f)
        return cache
    else:
        logger.warning('Update cache file not found, will create a new one.', extra={'service_id': service})
        with open(update_cache_path, 'w', encoding='utf-8') as f:
            f.write('{}')
        return {}

@logger.auto_logger('clickmouse.update')
def save_update_cache(**kwargs):
    '''写入更新缓存文件'''
    cache_data = {
        'last_check_time': time(),
        **kwargs
    }

    with open(update_cache_path, 'w', encoding='utf-8') as f:
        json.dump(cache_data, f)

@logger.auto_logger('clickmouse.update')
def should_check_update():
    '''
    检查是否应该检查更新
    '''
    last_check_time = update_cache.get('last_check_time')
    if not last_check_time:
        return True
    last_check_time_stamp = datetime.fromtimestamp(last_check_time)
    now = datetime.now()
    
    setting_time = setting_value.update_frequency
    time = 9
    
    match setting_time:
        case 0: # 每次打开都启动
            return True
        case 1: # 每天检查一次
            time = 3600 * 24
        case 2: # 每周检查一次
            time = 3600 * 24 * 7
        case 3: # 每月检查一次
            time = 3600 * 24 * 30
    
    if (now - last_check_time_stamp).total_seconds() > time:
        return True
    return False

@logger.auto_logger('clickmouse.setting')
def save_settings():
    '''
    保存设置
    '''
    with open(data_path / 'settings.json', 'w', encoding='utf-8') as f:
        json.dump(settings, f)

@logger.auto_logger('clickmouse.ipk.main')
def get_packages():
    lang_index = [] # 语言包索引
    show = []
    package_id = []

    # 加载包信息
    for package in packages:
        lang_index.append(get_lang(package.get('package_name_index', '-1'), source=package_lang))
        package_id.append(package.get('package_name', None))
        show.append(package.get('show_in_extension_list', True))
    return (lang_index, show, package_id)

@logger.auto_logger()
def get_application_instance():
    '''获取或创建 QApplication 实例'''
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app

@logger.auto_logger('clickmouse.setting.hotkeyManager', level=logging.DEBUG)
def all_in_list(list1, list2):
    if len(list1) != len(list2):
        return False
    return all(item in list2 for item in list1)

@logger.auto_logger('clickmouse.ipk.main')
def import_package(package_id: str):
    for i in packages_info:
        if i['package_name'] == package_id:
            return i
    raise ValueError(f'包名 {package_id} 不存在')

@logger.auto_logger('clickmouse.colorGetter', level=logging.DEBUG)
def get_windows_accent_color():
    '''读取Windows强调色'''
    # 主题色存储在 HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\DWM
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'SOFTWARE\Microsoft\Windows\DWM')

    # 读取 AccentColor 值（DWORD类型）
    accent_color, _ = winreg.QueryValueEx(key, 'AccentColor')
    winreg.CloseKey(key)

    # 转换为RGB格式（注册表中的顺序是ABGR）
    r = accent_color & 0xFF # R通道
    b = (accent_color >> 16) & 0xFF # B通道
    g = (accent_color >> 8) & 0xFF # G通道

    r_str = f'{r:02x}'.zfill(2)
    g_str = f'{g:02x}'.zfill(2)
    b_str = f'{b:02x}'.zfill(2)

    # 通常我们使用RGB格式，忽略Alpha通道
    return f'#{r_str}{g_str}{b_str}'

@logger.auto_logger('clickmouse.colorGetter')
def lighten_color_hex(hex_color, factor):
    '''
    使用HSL色彩空间提亮颜色
    hex_color: 十六进制颜色字符串，如 "#808080"
    factor: 提亮因子 (-1-1之间)，0为不变，1为最亮，-1为最暗
    '''

    if not hex_color.startswith('#') or len(hex_color) != 7:
        raise ValueError('Please enter a valid hex color string, such as #FF0000.')

    if not -1 <= factor <= 1:
        raise ValueError('The lightening factor must be between -1 and 1.')

    # 移除#号并转换为RGB
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0

    # 转换为HSL
    h, l, s = colorsys.rgb_to_hls(r, g, b)

    if factor >= 0:
        # 提亮：向白色(1.0)移动
        l = l + (1.0 - l) * factor
    else:
        # 变暗：向黑色(0.0)移动
        factor_abs = abs(factor)  # 取绝对值
        l = l * (1.0 - factor_abs)

    # 转回RGB
    r, g, b = colorsys.hls_to_rgb(h, l, s)

    # 转换回十六进制
    hex_result = '#{:02x}{:02x}{:02x}'.format(
        int(r * 255), 
        int(g * 255), 
        int(b * 255)
    )

    return hex_result

@logger.auto_logger('clickmouse.setting.startupManager')
def datetime_to_filetime(dt_utc: datetime):
    '''
    将datetime对象转换为FILETIME（64位整数）
    输入必须是UTC时间
    '''
    # FILETIME纪元：1601-01-01 00:00:00 UTC
    filetime_epoch = datetime(1601, 1, 1, tzinfo=pytz.UTC)

    # 计算时间差（微秒精度）
    delta = dt_utc - filetime_epoch

    # 转换为100纳秒间隔数
    # 1秒 = 10,000,000个100纳秒间隔
    filetime_units = delta.total_seconds() * 1e7

    return int(filetime_units)

@logger.auto_logger('clickmouse.setting.startupManager')
def get_now_filetime():
    '''
    获取当前UTC时间对应的FILETIME值
    '''
    # 获取当前UTC时间
    now_utc = datetime.now(pytz.UTC)
    # 转换为FILETIME
    filetime_value = datetime_to_filetime(now_utc)
    # 将整数转换为小端字节序（8字节）
    little_endian = struct.pack('<Q', filetime_value)
    return little_endian

@logger.auto_logger('clickmouse.setting.ui')
def on_update_setting_window():
    global setting_window
    if setting_window.isVisible():
        page = setting_window.now_page
        if page is None:
            page = 0
        values = setting_window.values.copy()
        setting_window.close()
        setting_window = SettingWindow(values)
        setting_window.click_setting_changed.connect(lambda: on_input_change(type=InputChange.main_window))
        setting_window.window_restarted.connect(on_update_setting_window)
        setting_window.on_page_button_clicked(page)
        setting_window.show()

@logger.auto_logger('clickmouse.setting.hotkeyManager', level=logging.DEBUG)
def format_keys(keys_str_list, source=False):
    '''将 pynput 的键字符串转换为用户友好的形式'''
    # 示例：去掉 'Key.' 前缀，并将特殊键首字母大写
    friendly_keys = []
    for k in keys_str_list:
        if k.startswith('Key.'):
            name = k[4:]  # 去掉 'Key.'
            # 处理常见的修饰键名称
            if name.endswith('_l') or name.endswith('_r'):
                name = name[:-2]  # 去掉 _l/_r
            elif name.endswith('_gr'):
                name = name[:-3]  # 去掉 _gr
            elif name == 'cmd': # 系统键
                name = 'Win'
            elif '_' in name:  # 其他修饰键
                name = name.replace('_', '')
            friendly_keys.append(name.capitalize())
        elif k.startswith("'\\x") and k.endswith("'"): # ctrl的热键
            code = int(k[3:-1], 16)
            friendly_keys.append(chr(code + 64)) # \x01 -> A
        elif k.startswith('<') and k.endswith('>'): # ctrl+alt的热键
            code = int(k[1:-1])
            if code > 90:  # 非字母
                if code == 192: # `
                    code = 96 # 实际的 ASCII 码
                elif code == 186: # ;
                    code = 59 # 实际的 ASCII 码
                elif code == 222: # "
                    code = 34 # 实际的 ASCII 码
                elif 96 <= code <= 105: # num区域键
                    code -= 48 # 实际的 ASCII 码位移
                elif 106 <= code <= 111: # 运算符的Num区域键
                    code -= 64 # 实际的 ASCII 码位移
                else:
                    code -= 144  # 去掉 144 偏移
            if code < 0x20: # 不可见字符
                friendly_keys.append(f'<{code}>')
            else:
                friendly_keys.append(chr(code)) # <65> -> A
        elif ((k.startswith("'") and k.endswith("'"))
            or(k.startswith('"') and k.endswith('"'))): # 单个字符
            if k == "'\\\\'": # 反斜杠
                friendly_keys.append('\\')
            else:
                friendly_keys.append(k[1:-1].upper())
        else:
            # 普通字符键直接保留
            friendly_keys.append(k)
    out_list = list(dict.fromkeys(friendly_keys)) # 去重
    if source:
        return out_list
    priority = {'Win': 1, 'Ctrl': 2, 'Alt': 3, 'Shift': 4} # 按优先级排序
    def get_priority(key):
        if key in priority:
            return priority[key]
        elif len(key) == 1:   # 单个字符（字母、数字、符号等）
            return 6
        else:                 # 其他多字符键
            return 5
    return '+'.join(sorted(out_list, key=get_priority)) # 按优先级排序并连接

@logger.auto_logger('clickmouse.setting.hotkeyManager')
def get_hotkey_listener_instance():
    '''获取全局唯一的 HotkeyListener 实例'''
    if not hasattr(get_hotkey_listener_instance, "instance"):
        global hotkey_thread # 驻留线程，防止自动销毁
        get_hotkey_listener_instance.instance = HotkeyListener()
        
        logger.info('Starting hotkey listener.', extra={'service_id': 'clickmouse.setting.hotkeyManager'})
        # 在后台线程中启动热键监听
        hotkey_thread = QtThread(get_hotkey_listener_instance.instance.start_listening)
        hotkey_thread.start()
    return get_hotkey_listener_instance.instance

@logger.auto_logger('clickmouse.update')
def revert_update():
    '''回滚更新'''
    try:os.rename('updater.old', 'updater')
    except:pass

    try:os.remove('updater/clickmouse.7z')
    except:pass

@logger.auto_logger('clickmouse.main.ui', level=logging.DEBUG)
def on_input_change(*, type:str ):
    '''输入延迟改变'''
    # 判断参数有效性
    if type == InputChange.main_window:
        global is_inf, is_error, delay_num, time_num
        delay_text = main_window.input_delay
        delay_times = main_window.input_times
        times_combo = main_window.times_combo
        delay_combo = main_window.delay_combo
        total = main_window.total_time_label
        delay_num = setting_value.click_delay
        time_num = setting_value.click_times
        is_error = False
    elif type == InputChange.setting_window:
        delay_text = setting_window.default_delay
        delay_times = setting_window.default_time
        total = setting_window.total_time_label
        times_combo = setting_window.times_combo
        delay_combo = setting_window.delay_combo
    input_delay = delay_text.text().strip()
    input_times = delay_times.text().strip()
    is_inf = False
    delay = 0

    delay_times.setEnabled(not(times_combo.currentIndex() == latest_index or (setting_value.times_unit == latest_index) and type == InputChange.main_window))

    if times_combo.currentIndex() == latest_index: 
        is_inf = True
    if setting_value.times_unit == latest_index and type == InputChange.main_window:
        is_inf = True

    def on_delay_error(error_text=get_lang('14')):
        '''输入延迟错误'''
        logger.debug(f'Input delay error: {error_text}', extra={'service_id': 'clickmouse.main.ui'})
        total.setText(f'{get_lang('2c')}: {error_text}')
        if type == InputChange.main_window:
            global is_error

            main_window.right_click_button.setEnabled(False)
            main_window.left_click_button.setEnabled(False)
            is_error = True
        elif type == InputChange.setting_window:
            if error_text == get_lang('14'):
                text = get_lang('60')
            else:
                text = error_text
            main_window.total_time_label.setText(f'{get_lang('2c')}: {text}')

    @logger.auto_logger('clickmouse.main.ui', level=logging.DEBUG)  
    def check_default_var(value):
        '''检查默认延迟是否有效'''
        try:
            var = int(settings.get(f'click_{value}', ''))
            if not var:
                return True
            if var < 1:
                raise ValueError
            return True
        except ValueError:
            if type == InputChange.main_window:
                on_delay_error(get_lang('60'))
            else:
                on_delay_error()
            return False
    
    @logger.auto_logger('clickmouse.main.ui', level=logging.DEBUG)  
    def get_num(input_value, value_default, err_use_default, default_var):
        value = None
        try:
            value = math.ceil(float(input_value))
            if value < 1:
                raise ValueError
        except ValueError:
            if value_default:
                if input_delay == '' or err_use_default:
                    if check_default_var(default_var):
                        value = int(value_default)
                    else:
                        return
                else:
                    return
        except Exception:
            return
        return value

    delay = get_num(input_delay, setting_value.click_delay, setting_value.delay_error_use_default, 'delay')

    if not is_inf:
        if not(setting_value.click_times) and not(setting_value.click_delay):
            on_delay_error(get_lang('61'))
            return 1
        times = get_num(input_times, setting_value.click_times, setting_value.times_error_use_default, 'times')
        if times is None:
            on_delay_error()
            return -1
    if delay is None:
        on_delay_error()
        return -1

    if type == InputChange.main_window:
        # 先过滤前面的报错
        main_window.right_click_button.setEnabled(True)
        main_window.left_click_button.setEnabled(True)
        is_error = False
        if bool(delay_text.text()) ^ bool(delay_times.text()): # 状态不同
            if not((setting_value.modify_using_default_input or is_inf) and dev_flags.get('new_settings')):
                on_delay_error()
                return -2
        if ((delay_combo.currentIndex() != setting_value.delay_unit) and not(delay_text.text())):
            if not(setting_value.modify_using_default_combo and dev_flags.get('new_settings')):
                on_delay_error()
                return -2
        if ((times_combo.currentIndex() != setting_value.times_unit or is_inf) and not(delay_text.text())):
            if not(setting_value.modify_using_default_combo and dev_flags.get('new_settings')):
                on_delay_error()
                return -2

    match delay_combo.currentIndex():
        case 0:
            delay_num = delay
        case 1:
            delay_num = delay * 1000
        case 2:
            delay_num = delay * 60 * 1000
        case _:
            delay_num = delay

    if is_inf:
        total.setText(f'{get_lang('2c')}: {get_lang('2b')}')
    else:
        match times_combo.currentIndex():
            case 0:
                time_num = times
            case 1:
                time_num = times * 10000
            case 2:
                time_num = times * 100_0000
            case _:
                time_num = times

        try:
            total_run_time = get_unit_value(delay_num * time_num)
            if type == InputChange.setting_window:
                main_window.delay_combo.setCurrentIndex(delay_combo.currentIndex())
                main_window.times_combo.setCurrentIndex(times_combo.currentIndex())
        except OverflowError:
            on_delay_error(get_lang('67'))
            return -3
        total.setText(f'{get_lang('2c')}: {total_run_time[0]}{total_run_time[1]}')
    if type == InputChange.setting_window:
        on_input_change(type=InputChange.main_window) # 刷新主窗口
    return 0

@logger.auto_logger('clickmouse.main')
def open_url(url, title: str=None, width:int=None, height:int=None, fixed:bool=False):
    if dev_flags.get('inline_website'):
        webview.show(url, title, width, height, fixed)
    else:
        from webbrowser import open as open_webbrowser
        open_webbrowser(url)

class UMainWindow(QMainWindow):
    '''自定义窗口基类'''
    def __init__(self):   
        logger.info('Initializing window.', extra={'service_id': 'clickmouse.ui'})
        super().__init__()

        self.setWindowIcon(icon)
        self.func = lambda: color_getter.apply_titleBar(self)

        self.addtional_local_value = {'self': self}
        logger.info('Window initialized.', extra={'service_id': 'clickmouse.ui'})
    
    @logger.auto_logger('clickmouse.ui', ['UMainWindow'])
    def showEvent(self, event):
        '''窗口显示事件'''
        color_getter.style_changed.connect(self.func)
        QTimer.singleShot(setting_value.soft_delay, self.func)
        return super().showEvent(event)
    
    @logger.auto_logger('clickmouse.ui', ['UMainWindow'])
    def closeEvent(self, event):
        '''窗口关闭事件'''
        color_getter.style_changed.disconnect(self.func)
        return super().closeEvent(event)

class UDialog(QDialog):
    '''自定义对话框基类'''
    def __init__(self):
        logger.debug('Initializing window.', extra={'service_id': 'clickmouse.ui'})

        super().__init__()
        self.setWindowIcon(icon)
        self.func = lambda: color_getter.apply_titleBar(self)

        self.addtional_local_value = {'self': self}

        logger.debug('Window initialized.', extra={'service_id': 'clickmouse.ui'})  
    
    @logger.auto_logger('clickmouse.ui', ['UDialog'])
    def showEvent(self, event):
        '''窗口显示事件'''
        color_getter.style_changed.connect(self.func)
        QTimer.singleShot(setting_value.soft_delay, self.func)
        return super().showEvent(event)
    
    @logger.auto_logger('clickmouse.ui', ['UDialog'])
    def closeEvent(self, event):
        '''窗口关闭事件'''
        color_getter.style_changed.disconnect(self.func)
        return super().closeEvent(event)
    
class UWebView(UMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint
        ) # 设置窗口属性
        self.web = QWebEngineView()
        self.profile = QWebEngineProfile.defaultProfile()
        self.engine_script = QWebEngineScript()

        self.setCentralWidget(self.web)

    def show(self, url, title: str=None, width:int=None, height:int=None, fixed:bool=False):
        title = title if title is not None else 'UWebView'
        _width = width if width is not None  else 640
        _height = height if height is not None  else 480

        webview.setWindowTitle(title)
        webview.resize(_width, _height)
        if fixed:
            webview.setFixedSize(_width, _height)

        self.update_script(color_getter.is_dark_mode)

        self.web.setUrl(QUrl(url))
        
        return super().show()
    
    def closeEvent(self, event):
        '''窗口关闭事件'''
        self.web.setUrl(QUrl('about:blank')) # 隐藏网页
        return super().closeEvent(event)
    
    @logger.auto_logger('clickmouse.webview', ['UWebView'])
    def update_script(self, is_dark_mode: bool):
        with open(get_resource_path('WebviewTheme.js'), "r", encoding='utf-8') as f:
            self.script = f"var theme = '{'dark' if is_dark_mode else 'light'}';\n" + f.read()

        self.engine_script.setName('dark-mode')
        self.engine_script.setInjectionPoint(QWebEngineScript.DocumentCreation)  # 尽早注入
        self.engine_script.setWorldId(QWebEngineScript.MainWorld)
        self.engine_script.setRunsOnSubFrames(True)
        self.engine_script.setSourceCode(self.script) # 设置代码，配置深色浅色模式
        self.profile.scripts().insert(self.engine_script)
    
class MessageBox(UMessageBox):
    def __init__(self, parent: QWidget | None, title: str, text: str, icon: MessageIcon, buttons: MessageButton, defaultButton: MessageButton):
        super().__init__(parent, title, text, icon, buttons, defaultButton)
        self.func = lambda: color_getter.apply_titleBar(self)

    @logger.auto_logger('clickmouse.ui', ['MessageBox'])
    def showEvent(self, event):
        color_getter.style_changed.connect(self.func)
        evt = super().showEvent(event)
        QTimer.singleShot(setting_value.soft_delay, self.func)
        return evt
    
    @logger.auto_logger('clickmouse.ui', ['MessageBox'])
    def done(self, result):
        '''关闭对话框时执行'''
        color_getter.style_changed.disconnect(self.func)
        return super().done(result)

class StartManager(QObject):
    '''开机自启动管理器'''
    updated = Signal(bool)

    def __init__(self):
        super().__init__()
        logger.info('Starting startup manager.', extra={'service_id': 'clickmouse.setting.startupManager'})
        self.app_name = 'clickmouse.lnk'
        self.status_path = r'Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\StartupFolder'
        self.create_reg()
        self.auto_start = self.is_enabled()

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_value)
        self.timer.start(setting_value.soft_delay)
        logger.info('Startup manager initialized.', extra={'service_id': 'clickmouse.setting.startupManager'})

    @logger.auto_logger('clickmouse.setting.startupManager', ['StartManager'], start_extra_text='Startup folder`s shortcut is not found')
    def create_reg(self):
        '''检查是否已启用开机自启动'''
        start_path = Path(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup', self.app_name)
        if not(start_path.exists()):
            logger.warning('Startup folder`s shortcut is not found,creating shortcut.', extra={'service_id': 'clickmouse.setting.startupManager'})
            create_shortcut(str(start_path), str(Path.cwd() / 'main.exe') + ' --quiet', 'ClickMouse', work_dir=str(Path.cwd()))
            self.disable()
        else:
            logger.info('Startup folder`s shortcut is found.', extra={'service_id': 'clickmouse.setting.startupManager'})  
    
    @logger.auto_logger('clickmouse.setting.startupManager', ['StartManager'], level=logging.DEBUG)
    def is_enabled(self):
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.status_path, 0, winreg.KEY_READ) as key:
                logger.debug('Try to read value from registry..', extra={'service_id': 'clickmouse.setting.startupManager'})
                value, _ = winreg.QueryValueEx(key, self.app_name)

            return value[0] == 2
        except FileNotFoundError:
            logger.warning('Registry path not found.', extra={'service_id': 'clickmouse.setting.startupManager'})
            return False

    @logger.auto_logger('clickmouse.setting.startupManager', ['StartManager'], level=logging.DEBUG)  
    def check_value(self):
        '''检查注册表值是否更新'''
        new_value = self.is_enabled()
        if new_value != self.auto_start:
            self.auto_start = new_value
            self.updated.emit(self.auto_start)
            logger.info('Startup value updated.', extra={'service_id': 'clickmouse.setting.startupManager'})

    @logger.auto_logger('clickmouse.setting.startupManager', ['StartManager'], start_extra_text='Enable startup.')  
    def enable(self):
        '''启用开机自启动'''
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                            self.status_path, 0, winreg.KEY_WRITE) as key:
            winreg.SetValueEx(key, self.app_name, 0, winreg.REG_BINARY, bytes([0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]))

    @logger.auto_logger('clickmouse.setting.startupManager', ['StartManager'], start_extra_text='Disable startup.')  
    def disable(self):
        '''禁用开机自启动''' 
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                            self.status_path, 0, winreg.KEY_WRITE) as key:
            winreg.SetValueEx(key, self.app_name, 0, winreg.REG_BINARY, bytes([0x03, 0x00, 0x00, 0x00]) + get_now_filetime())
        
class UHotkeyLineEdit(QLineEdit):
    '''能够捕获热键组合的输入框，只有获得焦点时才更新'''
    def __init__(self, parent=None):
        super().__init__(parent)
        self._connection = None  # 保存信号连接对象
        self.key_list = []  # 保存按下的热键
        self.setReadOnly(True)
        #self.listener = get_hotkey_listener_instance()
        self.listener = hotkey_listener

    def focusInEvent(self, event):
        '''获得焦点时连接信号'''
        global can_run_hotkey

        can_run_hotkey = False  # 禁止热键运行
        if self._connection is None:
            # 连接信号，使用 Qt.QueuedConnection 确保线程安全（默认 Auto 已经足够）
            self._connection = self.listener.combination_pressed.connect(self.on_combination_pressed ,Qt.QueuedConnection)
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        '''失去焦点时断开连接'''
        global can_run_hotkey

        can_run_hotkey = True  # 允许热键运行
        if self._connection is not None:
            # 断开连接
            self.listener.combination_pressed.disconnect(self.on_combination_pressed)
            self._connection = None
        super().focusOutEvent(event)

    def on_combination_pressed(self, keys_str_list):
        '''处理组合键信号，将列表格式化为字符串并显示'''
        self.key_list = format_keys(keys_str_list)
        self.setText(self.key_list)

class HotkeyListener(QObject):
    '''热键监听器类，用于在后台线程中监听全局热键'''
    combination_pressed = Signal(list)  # 新增信号，用于发送组合键信息

    def __init__(self):
        super().__init__()
        logger.info('Initializing hotkey listener.', extra={'service_id': 'clickmouse.setting.hotkeyManager'})
        self.listener = None
        self.is_listening = False
        self.clicked_keys = set()  # 用于跟踪当前按下的键

    @logger.auto_logger('clickmouse.setting.hotkeyManager', ['HotkeyListener'])
    def start_listening(self):
        '''开始监听热键''' 
        if self.is_listening:
            return

        self.is_listening = True
        # 创建键盘监听器，同时监听按下和释放事件
        self.listener = keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        )
        self.listener.daemon = True  # 设置为守护线程
        self.listener.start()

    @logger.auto_logger('clickmouse.setting.hotkeyManager', ['HotkeyListener'])
    def stop_listening(self):
        '''停止监听热键'''
        if self.listener and self.is_listening:
            self.is_listening = False
            self.listener.stop()

    def on_key_press(self, key):
        '''处理按键按下事件'''
        # 将按下的键添加到集合中
        self.clicked_keys.add(key)

        self.combination()

    def on_key_release(self, key):
        '''处理按键释放事件'''
        # 从集合中移除释放的键
        if key in self.clicked_keys:
            self.clicked_keys.remove(key)

    def combination(self):
        '''发送特定的组合键'''
        self.combination_pressed.emit(list(map(str, self.clicked_keys)))  # 发送组合键信息

class UFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setFrameShape(UFrame.Shape.HLine)
        set_style(self, StyleClass.frame)

class Click(QObject):
    pause = Signal(bool)
    click_changed = Signal(bool, bool)
    stopped = Signal()
    click_conuter = Signal(str, str, str) # 用于修复overflow问题
    started = Signal()

    def __init__(self):
        super().__init__()
        logger.info('Initializing clicker.', extra={'service_id': 'clickmouse.clicker'})
        self.running = False
        self.paused = False
        self.click_thread = None
        self.right_clicked = False
        self.left_clicked = False

    @logger.auto_logger('clickmouse.clicker', ['Click'])
    def mouse_left(self, delay, times):
        if not self.running:
            self.mouse_click(button='left', input_delay=delay, times=times)

    @logger.auto_logger('clickmouse.clicker', ['Click'])
    def mouse_right(self, delay, times):
        # 停止当前运行的点击线程
        if not self.running:
            self.mouse_click(button='right', input_delay=delay, times=times)

    @logger.auto_logger('clickmouse.clicker', ['Click'], start_extra_text='Start clicker.')
    def mouse_click(self, button: str, input_delay, times):
        '''鼠标连点'''
        # 重置状态
        if self.click_thread and self.click_thread.isRunning():
            logger.info('Stop clicker')
            self.running = False
            self.paused = False
            self.pause.emit(False)
            self.click_thread.wait()

        if button == 'left':
            self.left_clicked = True
            self.right_clicked = False
        elif button == 'right':
            self.right_clicked = True
            self.left_clicked = False 

        if is_inf:
            times = float('inf')

        self.click_changed.emit(self.left_clicked, self.right_clicked)

        # 运行状态控制
        self.running = True
        self.paused = False

        # 判断参数有效性
        try:
            logger.debug(f'Clicking {button} with delay {input_delay} and times {times}')
            delay = math.ceil(float(input_delay))
        except Exception:
            trace = format_exc()  # 获取异常堆栈跟踪信息
            MessageBox.critical(None, get_lang('14'), f'{get_lang('1b')}\n{trace}')
            logger.exception('clickmouse.clicker')
            return

        # 创建独立线程避免阻塞GUI
        @logger.auto_logger('clickmouse.clicker', ['Click'])
        def click_loop():
            self.pause.emit(False)
            i = 0
            while self.running:
                if i >= times:
                    self.running = False
                    self.stopped.emit()
                    break
                if not self.paused:
                    try:
                        logger.debug('Clicking.')
                        if times == float('inf'):   
                            self.click_conuter.emit('inf', str(i), str(delay))
                        else:
                            self.click_conuter.emit(str(times), str(i), str(delay))
                        pyautogui.click(button=button)
                        sleep(delay / 1000)
                        i += 1
                    except Exception:
                        trace = format_exc()
                        MessageBox.critical(None, get_lang('14'), f'{get_lang('1b')}\n{trace}')
                        logger.exception('clickmouse.clicker', trace)

                        self.stopped.emit()
                        break
                else:
                    sleep(delay / 1000)  # 暂停
            else:
                self.stopped.emit()

        # 启动线程
        logger.info(f'Starting click thread')
        self.started.emit()
        self.click_thread = QtThread(click_loop)
        self.click_thread.start()

    @logger.auto_logger('clickmouse.clicker', ['Click'])
    def pause_click(self):
        if self.paused:
            logger.info('Clicker resumed')
        else:
            logger.info('Clicker paused')
        self.paused = not self.paused
        self.pause.emit(self.paused)

class Refresh:
    def __init__(self):
        logger.info('Initializing refresh service', extra={'service_id': 'clickmouse.refresh'})
        self.steps = [
            self.refresh_title,
            self.left_check,
            self.right_check,
        ]

    @logger.auto_logger('clickmouse.refresh', ['Refresh'])
    def run(self):
        self.do_step(self.steps)
    
    @logger.auto_logger('clickmouse.refresh', ['Refresh'])
    def do_step(self, codes):
        # 尝试执行代码
        for code in codes:
            try:
                logger.info(f'Running function: Refresh.{code.__name__}', extra={'service_id': 'clickmouse.refresh'})
                code()
                logger.info(f'Function {code.__name__} running successfull.')
            except NameError as e:
                logger.warning(f'Step {code.__name__} not defined: {e}')
            except Exception as e:
                logger.error(f'Step {code.__name__} Running failed: {e}')

    def refresh_title(self):
        QTimer.singleShot(setting_value.soft_delay, lambda: color_getter.style_changed.emit(bool(color_getter.is_dark_mode)))

    def left_check(self):
        if clicker.left_clicked:
            logger.info('Left click is started.')
            set_style(main_window.left_click_button, StyleClass.selected)
        else:
            logger.info('Left click is not started.')
            set_style(main_window.left_click_button, StyleClass.none)

    def right_check(self):
        if clicker.right_clicked:
            logger.info('Right click is started.')
            set_style(main_window.right_click_button,StyleClass.selected)
        else:
            logger.info('Right click is not started.')
            set_style(main_window.right_click_button, StyleClass.none)

class RunAfter:
    def __init__(self):
        logger.info('Initializing run-after service', extra={'service_id': 'clickmouse.runafter'})
        self.program_list = {}

    @logger.auto_logger('clickmouse.runafter', ['RunAfter'])
    def add(self, name, python_path, exe_path, run_as_admin=False):
        self.program_list[name] = (python_path, exe_path, run_as_admin)
        MessageBox.information(main_window, get_lang('59'), get_lang('5a'))

    @logger.auto_logger('clickmouse.runafter', ['RunAfter'])
    def remove(self, name):
        logger.info('Remove run-after plan')
        del self.program_list[name]
        MessageBox.information(main_window, get_lang('59'), get_lang('88'))

    @logger.auto_logger('clickmouse.runafter', ['RunAfter'])
    def run(self):
        for python_path, exe_path, use_admin in self.program_list.values():
            if use_admin:
                run_as_admin(python_path, exe_path)
            else:
                run_software(python_path, exe_path)

class ColorGetter(QObject):
    style_changed = Signal(bool)

    def __init__(self):
        super().__init__()

        logger.info('Initializing color getter.', extra={'service_id': 'clickmouse.colorgetter'})

        # 记录当前主题
        self.style = setting_value.select_style
        self.is_dark_mode = 0

        self.current_theme, self.windows_theme, self.windows_color, self.use_windows_color = self.load_theme()
        try:
            self.current_theme = self.current_theme.replace('auto-', '')
        except AttributeError:
            settings['select_style'] = 0
            save_settings()
            MessageBox.critical(None, get_lang('14'), get_lang('12'))
            logger.critical('Setting style index is out of range, will reset to default.')
            run_software('main.py', 'main.exe')
            sys.exit(0)

        # 初始化时应用一次主题
        self.apply_global_theme()

        # 使用定时器定期检测主题变化
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_and_apply_theme)
        self.timer.start(setting_value.soft_delay)

        self.need_refresh = False

    @logger.auto_logger('clickmouse.colorgetter', ['ColorGetter'], level=logging.DEBUG)
    def load_theme(self):
        theme = None
        windows_theme = None
        windows_color = None
        use_windows_color = None

        if self.style == 0:
            theme = QApplication.styleHints().colorScheme()
            if theme == Qt.ColorScheme.Dark:
                logger.debug('Dark theme')
                theme = 'auto-dark'
            elif theme == Qt.ColorScheme.Light:
                logger.debug('Light theme')
                theme = 'auto-light'

        windows_theme = QApplication.styleHints().colorScheme()   
        if theme == Qt.ColorScheme.Dark:
            logger.debug('Dark theme')
            windows_theme = 'dark'
        elif theme == Qt.ColorScheme.Light:
            logger.debug('Light theme')
            windows_theme = 'light'

        windows_color = get_windows_accent_color()
        use_windows_color = setting_value.use_windows_color

        for k, v in maps.items():
            if v == setting_value.select_style:
                logger.debug(f'Found theme: {k}')
                theme = k

        return theme, windows_theme, windows_color, use_windows_color

    @logger.auto_logger('clickmouse.colorgetter', ['ColorGetter'], level=logging.DEBUG)
    def check_and_apply_theme(self):
        '''检查主题是否变化，变化则重新应用'''
        logger.debug('Check theme')

        self.style = setting_value.select_style

        new_theme, new_windows_theme, new_windows_color, new_use_windows_color = self.load_theme()

        if new_theme != self.current_theme:
            logger.info('Theme changed')
            self.current_theme = new_theme
            self.apply_global_theme()

        if new_windows_color != self.windows_color:
            logger.info('Windows color changed')
            self.windows_color = new_windows_color
            self.apply_global_theme()

        if new_windows_theme != self.windows_theme:
            logger.info('Windows theme changed')
            self.windows_theme = new_windows_theme
            self.need_refresh = True 

        if new_use_windows_color != self.use_windows_color:
            logger.info('Windows color changed')
            self.use_windows_color = new_use_windows_color
            self.apply_global_theme()

        if self.need_refresh and init_success:
            refresh.run() # 刷新
            self.need_refresh = False
    
    @logger.auto_logger('clickmouse.colorgetter', ['ColorGetter'])
    def apply_titleBar(self, window: QMainWindow | QDialog):
        '''应用标题栏样式'''
        if not init_success: # 等待初始化完成加载
            return -1
        hwnd = window.winId().__int__()

        if select_styles.css_data['.meta']['mode'] == 'dark':
            self.is_dark_mode = 1
        else:
            self.is_dark_mode = 0

        # 设置深色模式
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            wintypes.HWND(hwnd),
            DWMWA_USE_IMMERSIVE,
            ctypes.byref(wintypes.INT(self.is_dark_mode)),
            ctypes.sizeof(wintypes.INT)
        )

        return 0

    @logger.auto_logger('clickmouse.colorgetter', ['ColorGetter'])
    def apply_global_theme(self):
        '''根据当前主题，为整个应用设置全局样式表'''
        global select_styles

        app = get_application_instance()

        current_theme = self.current_theme.replace('auto-', '')

        select_styles = styles[current_theme]
        
        if self.use_windows_color:
            steps = [
                [['.selected:pressed', 'background-color'], lighten_color_hex(self.windows_color, -0.165)]
            ]
            if select_styles.css_data['.meta']['mode'] == 'dark':
                steps.extend([
                    [['.selected', 'background-color'], lighten_color_hex(self.windows_color, 0.4)],
                    [['.selected:hover', 'background-color'], lighten_color_hex(self.windows_color, 0.45)],
                    [['.selected', 'color'], 'black'],
                    [['.selected:hover', 'color'], 'black'],
                    [['.selected:pressed', 'color'], 'black'],
                    [['QCheckBox', 'color'], 'black'],
                ])
            else:
                steps.extend([
                    [['.selected', 'background-color'], self.windows_color],
                    [['.selected:hover', 'background-color'], lighten_color_hex(self.windows_color, 0.4)],
                ])
            for step in steps:
                select_styles = select_styles.replace(step[0], StyleReplaceMode.ALL, step[1], output_json=False)
        
        logger.debug('Apply theme')
        app.setStyleSheet(select_styles.css_text)  # 全局应用
        self.need_refresh = True
        
class MainWindow(UMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('ClickMouse')
        self.setGeometry(100, 100, 500, 375)
        self.setWindowFlags(
            Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint
        ) # 设置窗口属性

        self.setFixedSize(self.width(), self.height()) # 固定窗口大小

        logger.debug('Initializing value')
        self.show_update_in_start = False # 是否在启动时显示更新提示
        self.total_run_time = 0  # 总运行时间
        self.is_ready = True  # 是否状态栏为“就绪”
        self.is_start_from_tray = False # 是否从托盘启动

        logger.debug('Initializing clicker')
        self.init_ui()

        logger.debug('Check updates')
        self.on_check_update()

    def init_ui(self):
        # 创建主控件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_layout = QVBoxLayout(central_widget)

        # 创建标题大字
        title = QLabel(get_lang('0b'))

        # 创建标题风格
        set_style(title, StyleClass.big_24)
        title.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        # 按钮
        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)  # 设置按钮间距

        self.left_click_button = QPushButton(get_lang('0c'))
        self.left_click_button.setFixedSize(100, 60)
        self.left_click_button.setEnabled(False)

        self.right_click_button = QPushButton(get_lang('0d'))
        self.right_click_button.setFixedSize(100, 60)
        self.right_click_button.setEnabled(False)

        self.pause_button = QPushButton(get_lang('0f'))
        self.pause_button.setFixedSize(100, 40)
        self.pause_button.setEnabled(False)

        self.stop_button = QPushButton(get_lang('0e'))
        self.stop_button.setFixedSize(100, 40)
        self.stop_button.setEnabled(False)

        logger.debug('Initializing layout')

        # 单位输入框
        unit_layout = UnitInputLayout()

        self.input_delay = QLineEdit()
        self.input_delay.setFixedWidth(300)
        self.input_delay.setFixedHeight(30)

        self.delay_combo = QComboBox()
        self.delay_combo.addItems([get_lang('ms', source=unit_lang), get_lang('s', source=unit_lang)])
        self.delay_combo.setFixedWidth(60)
        self.delay_combo.setFixedHeight(30)

        unit_layout.addUnitRow(get_lang('11'), self.input_delay, self.delay_combo)

        self.input_times = QLineEdit()
        self.input_times.setFixedWidth(300)
        self.input_times.setFixedHeight(30)

        self.times_combo = QComboBox()
        self.times_combo.addItems([get_lang('66'), get_lang('2a'), get_lang('2b')])

        unit_layout.addUnitRow(get_lang('5c'), self.input_times, self.times_combo)

        # 总连点时长提示
        self.total_time_label = ULabel(get_lang('2c'))
        self.total_time_label.setAlignment(Qt.AlignHCenter)
        set_style(self.total_time_label, StyleClass.big_16)
        self.total_time_label.textChanged.emit()

        # 创建状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # 设置默认状态
        self.status_bar.showMessage(get_lang('5d'))

        # 创建布局
        logger.debug('Setting layout')
        grid_layout.addWidget(self.left_click_button, 0, 0)
        grid_layout.addWidget(self.right_click_button, 0, 2)
        grid_layout.addWidget(self.pause_button, 1, 1)
        grid_layout.addWidget(self.stop_button, 2, 1)

        central_layout.addWidget(title)
        central_layout.addLayout(grid_layout)
        central_layout.addLayout(unit_layout)
        central_layout.addWidget(self.total_time_label)
        self.setLayout(central_layout)

        # 按钮信号连接
        logger.debug('Singnal connection')
        self.left_click_button.clicked.connect(lambda:clicker.mouse_left(delay_num, time_num))
        self.right_click_button.clicked.connect(lambda:clicker.mouse_right(delay_num, time_num))

        self.pause_button.clicked.connect(clicker.pause_click)
        self.stop_button.clicked.connect(self.on_stop)

        self.input_delay.textChanged.connect(lambda: on_input_change(type=InputChange.main_window))
        self.input_times.textChanged.connect(lambda: on_input_change(type=InputChange.main_window))
        self.delay_combo.currentIndexChanged.connect(lambda: on_input_change(type=InputChange.main_window))
        self.times_combo.currentIndexChanged.connect(lambda: on_input_change(type=InputChange.main_window))

        self.status_bar.messageChanged.connect(self.reload_status)

        # 创建菜单栏
        logger.debug('Creating menu bar')
        self.create_menu_bar()

        # 刷新按钮状态

        logger.debug('Initializing color successd.')

    def reload_status(self):
        '''刷新状态栏'''
        if self.status_bar.currentMessage() == '':
            if self.is_ready:
                self.status_bar.showMessage(get_lang('5d'))
            else:
                self.status_bar.showMessage(get_lang('8d'))

    def create_menu_bar(self):
        menu_bar = self.menuBar()

        # 文件菜单
        file_menu: QMenu = menu_bar.addMenu(get_lang('01'))

        # 清理缓存动作
        clean_cache_action: QAction = file_menu.addAction(get_lang('02'))

        # 退出动作
        exit_action: QAction = file_menu.addAction(get_lang('03'))

        # 设置菜单
        settings_menu: QMenu = menu_bar.addMenu(get_lang('04'))
        settings_action: QAction = settings_menu.addAction(get_lang('05'))
        attr_action: QAction = settings_menu.addAction(get_lang('8c'))

        # 更新菜单
        update_menu: QMenu = menu_bar.addMenu(get_lang('06'))

        # 更新菜单动作
        update_check: QAction = update_menu.addAction(get_lang('07'))
        update_log: QAction = update_menu.addAction(get_lang('08'))

        # 帮助菜单
        help_menu: QMenu = menu_bar.addMenu(get_lang('09'))
        about_action: QAction = help_menu.addAction(get_lang('0a'))

        # 发送反馈
        create_issue_action: QAction = help_menu.addAction(get_lang('ba'))

        # 文档菜单
        doc: QAction = help_menu.addAction(get_lang('5f'))
        doc.triggered.connect(self.open_doc)

        # 扩展菜单
        extension_menu: QMenu = menu_bar.addMenu(get_lang('8e'))
        official_extension_menu: QMenu = extension_menu.addMenu(get_lang('90'))
        if not any(show_list):
            # 无官方扩展提示
            official_extension_menu.addAction(get_lang('91')).setDisabled(True)
        else:
            # 加载官方扩展菜单
            for name, show, package_id in zip(package_names, show_list, package_ids):
                if show:
                    official_extension_menu.addAction(name).triggered.connect(lambda chk, idx=package_id: self.do_extension(idx)) # 给菜单项添加ID，方便绑定事件
        manage_extension_menu: QAction = official_extension_menu.addAction(get_lang('92'))
        manage_extension_menu.triggered.connect(self.show_manage_extension) # 管理扩展菜单
        manage_extension_menu.setEnabled(has_packages)

        # not_official_extension_menu = extension_menu.addMenu(get_lang('93'))

        # cge_menu = not_official_extension_menu.addMenu(get_lang('94'))
        # cge_menu.addAction(get_lang('95')).setDisabled(True)

        # cmm_menu = not_official_extension_menu.addMenu(get_lang('96'))
        # cmm_menu.addAction(get_lang('97')).setDisabled(True)

        # not_official_extension_menu.addSeparator()

        # not_official_extension_menu.addAction(get_lang('98')).triggered.connect(self.show_import_extension_mode) # 管理扩展菜单
        # not_official_extension_menu.addAction(get_lang('92')).triggered.connect(self.show_manage_not_official_extension) # 管理扩展菜单

        # # 宏菜单
        # macro_menu = menu_bar.addMenu(get_lang('99'))

        # run_marco_menu = macro_menu.addMenu(get_lang('9d'))
        # for action in cmm_menu.actions():
        #     run_marco_menu.addAction(action)

        # macro_menu.addAction(get_lang('9a')).triggered.connect(self.show_import_macro) # 导入宏
        # macro_menu.addAction(get_lang('9b')).triggered.connect(self.show_manage_not_official_extension) # 管理宏

        # 绑定动作
        about_action.triggered.connect(self.show_about)
        update_log.triggered.connect(self.show_update_log)
        clean_cache_action.triggered.connect(self.show_clean_cache)
        update_check.triggered.connect(lambda: self.on_update(True))
        settings_action.triggered.connect(self.show_setting)
        exit_action.triggered.connect(app.quit)
        create_issue_action.triggered.connect(lambda: open_url(setting_value.feedback, filter_hotkey(get_lang('ba')), 1000, 600, True))
        attr_action.triggered.connect(self.show_attr)
        
    def open_doc(self, *, path: str=''):
        '''打开文档'''
        lang_name = langs[select_lang]['lang_system_name']
        supported_doc_lang = [i['lang_system_name'] for i in langs if i['supported']]
            
        doc_choice = setting_value.lang_doc
        if doc_choice == 0: # 软件语言
            doc_choice_lang = lang_name
        elif doc_choice == 1: # 系统语言
            doc_choice_lang = langs[system_lang]['lang_system_name']
        else: # 大于等于2的数字，表示语言包
            doc_choice_lang = supported_doc_lang[doc_choice-2]
            
        if doc_choice_lang not in supported_doc_lang: # 不受支持的语言包
            doc_choice_lang = 'en' # 默认英文

        open_url(f'{setting_value.default_doc_link}/{path}'.format(lang=doc_choice_lang), filter_hotkey(get_lang('5f')), 1000, 600, True)
        
        logger.info(f'{setting_value.default_doc_link}/{path}'.format(lang=doc_choice_lang))

    def do_extension(self, index):
        '''执行扩展'''
        try:
            match index:
                case 'xystudio.clickmouse.repair':
                    if 'repair' in run_after.program_list:
                        run_after.remove('repair')
                    else:
                        run_after.add('repair', 'repair.py', 'repair.exe', True)
                    return
                case _:
                    run_software('NoneFile', f'extensions/{index}/main.exe')
        except Exception:
            trace = format_exc()
            MessageBox.critical(self, get_lang('14'), get_lang('9c').format(trace))
            logger.exception('Extension runner', trace)

    def show_manage_extension(self):
        '''管理扩展'''
        logger.info('Open extension management window')

        run_software('install_pack.py' ,'install_pack.exe', ['--ipk'])

    def show_import_extension_mode(self):
        '''导入扩展模式'''
        logger.info('Open extension import window')
        set_import_extension_window.exec()

    def show_import_extension(self, mode):
        '''导入扩展'''
        logger.info('Import extension')
        if mode == 1:
            file_name, _ = QFileDialog.getOpenFileName(self, get_lang('9e'), '', get_lang('9f'))
        else :
            file_name = QFileDialog.getExistingDirectory(self, get_lang('a0'), '')

        if file_name:
            ans = MessageBox.warning(self, get_lang('a1'), get_lang('a2'), MessageBox.Yes | MessageBox.No)
            try:
                if ans == MessageBox.No:
                    raise Exception(get_lang('a3'))
                # 导入扩展
                MessageBox.information(self, get_lang('a1'), get_lang('a4'))
            except Exception:
                trace = format_exc()
                MessageBox.critical(self, get_lang('a1'), get_lang('a5').format(trace))
                logger.exception('Import extension', trace)
                return
        else:
            return

    def show_manage_not_official_extension(self):
        '''管理第三方扩展'''
        logger.info('Opening threerd-party extension management window')

        MessageBox.information(self, get_lang('a1'), get_lang('a4'))

    def show_import_macro(self):
        '''导入宏'''
        logger.info('Import macro')

        file_name, _ = QFileDialog.getOpenFileName(self, get_lang('9e'), '', get_lang('9f').split(';;')[2])

        if file_name:
            try:
                # 导入扩展
                MessageBox.information(self, get_lang('a1'), get_lang('a4'))
            except Exception:
                trace = format_exc()
                logger.exception('Import macro', trace)
                MessageBox.critical(self, get_lang('a1'), get_lang('a5').format(trace))
                return
        else:
            return

    def show_about(self):
        '''显示关于窗口'''
        logger.info('Opening about window')
        about_window.exec()

    def show_attr(self):
        '''显示属性窗口'''
        logger.info('Opening attribute window')
        click_attr_window.show()

    def show_update_log(self):
        '''显示更新日志'''
        logger.info('Opening update log')
        self.open_doc(path=setting_value.update_log_path)

    def show_clean_cache(self):
        logger.info('Opening clean cache window')
        clean_cache_window.exec()

    def show_setting(self):
        '''显示设置窗口'''
        logger.info('Opening setting window')
        setting_window.show()

    def on_check_update(self):
        # 检查更新
        if setting_value.update_enabled:
            self.update_checked = True
            if should_check_update_res:
                self.check_update_thread = QtThread(check_update, args=(False,))
                self.check_update_thread.finished.connect(self.on_check_update_result)
                self.check_update_thread.start()
            else:
                logger.info('Checking update by cache')
                self.on_check_update_result(update_cache)
            
    def save(self):
        '''保存更新缓存'''
        if should_check_update_res:
            save_update_cache(should_update=result[0], latest_version=result[1], hash=result[3], update_version_tag=result[4]) # 缓存最新版本

    def on_check_update_result(self, check_data):
        '''检查更新结果'''
        global result
        
        logger.info('Checking update result')

        # 判断是否需要缓存
        if should_check_update_res:
            result = check_data
        else:
            result = [update_cache['should_update'], update_cache['latest_version'], None, update_cache['hash'], update_cache['update_version_tag']] # 使用缓存
        
        if result[3] is None and web_data['has_hash']: # 哈希为空，但是有哈希属性，说明这个版本没有发布的编译压缩包
            self.save()
            result[0] = False # 因为没有最新版本，没有编译后版本，所以认为不需要更新
            return

        # 检查结果处理
        if setting_value.update_notify:
            if result[1] != -1:  # -1表示函数出错
                self.save()
                if result[0]:  # 检查到需要更新
                    logger.info('Check update result: need update')
                    # 弹出更新窗口
                    self.show_update_in_start = True
                    if should_check_update_res:
                        # 弹出更新提示
                        self.on_update()
            else:
                if self.check_update_thread.isFinished():
                    logger.critical(f'Check update failed:\n{result[0]}')
                    MessageBox.critical(self, get_lang('14'), f'{get_lang('18')}\n{result[0]}')

    def on_update(self, judge=False):
        '''显示更新提示'''
        logger.info('Showing update window')
        if judge:
            if setting_value.update_enabled:
                if result[0]: # 检查到需要更新
                    self.open_update()
                else:
                    MessageBox.information(self, get_lang('16'), get_lang('19'))
            else:
                MessageBox.critical(self, get_lang('14'), get_lang('4e'))
        else:
            self.open_update()
            
    def open_update(self):
        if can_update:
            update_ok_window.exec()
        else:
            update_window.exec()

    def show(self):
        super().show()
        if self.show_update_in_start and not self.is_start_from_tray:
            self.is_start_from_tray = False
            self.on_update()

    def on_pause(self, paused):
        if clicker.running:
            self.pause_button.setEnabled(True)
            self.stop_button.setEnabled(True)
            if paused:
                self.pause_button.setText(get_lang('10'))
            else:
                self.pause_button.setText(get_lang('0f'))
        else:
            self.pause_button.setEnabled(False)
            self.stop_button.setEnabled(False)

    def on_stop(self):
        '''停止连点'''
        logger.info('Stopping clicker')

        # 禁用按钮
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)

        # 启用按钮
        self.input_times.setEnabled(not is_inf)
        self.input_delay.setEnabled(True)
        self.delay_combo.setEnabled(True)
        self.times_combo.setEnabled(True)
        self.right_click_button.setEnabled(True)
        self.left_click_button.setEnabled(True)

        # 重置变量
        clicker.running = False
        clicker.left_clicked = False
        clicker.right_clicked = False
        clicker.paused = False
        self.is_ready = True

        # 重置按钮样式
        set_style(self.left_click_button, StyleClass.none)
        set_style(self.right_click_button, StyleClass.none)

        # 重置文本
        self.pause_button.setText(get_lang('0f'))
        self.status_bar.showMessage(get_lang('5d'))

    def on_start(self):
        '''开始连点'''
        logger.info('Starting clicker')

        # 禁用按钮
        self.input_times.setEnabled(False)
        self.input_delay.setEnabled(False)
        self.delay_combo.setEnabled(False)
        self.times_combo.setEnabled(False)

    def on_click_changed(self, left, right):
        '''click按钮状态改变'''
        if left:
            # 左键点击
            set_style(self.left_click_button, StyleClass.selected)
            set_style(self.right_click_button, StyleClass.none)
            self.right_click_button.setEnabled(False)
            self.left_click_button.setEnabled(True)
        elif right:
            # 右键点击
            set_style(self.right_click_button, StyleClass.selected)
            set_style(self.left_click_button, StyleClass.none)
            self.right_click_button.setEnabled(True)
            self.left_click_button.setEnabled(False)
        else:
            # 未点击
            set_style(self.left_click_button, StyleClass.none)
            set_style(self.right_click_button, StyleClass.none)
            self.right_click_button.setEnabled(True)
            self.left_click_button.setEnabled(True)

    def on_click_counter(self, totel, now, delay):
        '''连点计数器'''
        logger.debug('Update click counter')
        self.is_ready = False
        now = int(now)
        delay = int(delay)
        if totel == 'inf':
            now_total_delay = get_unit_value(delay * now)
            delay = get_unit_value(delay)
            self.status_bar.showMessage(f'{get_lang('62') if clicker.paused else ''}{get_lang('63').format(now, self.get_full_unit(now_total_delay), self.get_full_unit(delay))}')
        else:
            totel = int(totel)

            left = totel - now
            totel_delay = get_unit_value(delay * totel)
            now_total_delay = get_unit_value(delay * now)
            left_delay = get_unit_value(delay * left)
            delay = get_unit_value(delay)
            self.status_bar.showMessage(f'{get_lang('62') if clicker.paused else ''}{get_lang('64').format(totel, now, left, self.get_full_unit(totel_delay), self.get_full_unit(now_total_delay), self.get_full_unit(left_delay), self.get_full_unit(delay))}')

    def get_full_unit(self, unit_text: tuple) -> str:
        '''获取完整单位'''
        return f'{unit_text[0]:.2f}{unit_text[1]}'

    def sync_input(self, get_handle, set_handle, source, dest):
        '''同步输入框'''
        set_handle(dest, get_handle(source))

class AboutWindow(UDialog):
    def __init__(self):
        super().__init__()
        logger.debug('Initizing about window')
        self.setWindowTitle(filter_hotkey(get_lang('0a')))
        self.setGeometry(100, 100, 375, 175)
        self.setFixedSize(self.width(), self.height())
        self.init_ui()

    def init_ui(self):
        # 创建面板
        logger.debug('Create panel')
        central_layout = QGridLayout()

        # 绘制内容
        logger.debug('Draw content')

        self.image_label = QLabel()
        # 加载图片
        self.image_label.setPixmap(icon.pixmap(64, 64))

        # 版本信息
        version_status_text = get_lang('65') if is_pre else ''

        version = QLabel(get_lang('1c').format(__version__, version_status_text, build_number))
        about = QLabel(get_lang('1d'))

        # 按钮
        logger.debug('Create Button')
        ok_button = QPushButton(get_lang('1e'))
        set_style(ok_button, StyleClass.selected)

        # 布局
        central_layout.addWidget(self.image_label, 0, 0, 1, 1)
        central_layout.addWidget(version, 0, 1, 1, 4)
        central_layout.addWidget(about, 2, 0, 1, 5)
        central_layout.addWidget(ok_button, 3, 4)

        self.setLayout(central_layout)

        # 绑定事件
        logger.debug('Singal connection')
        ok_button.clicked.connect(self.close)
        logger.debug('Initializing about window')

class CleanCacheWindow(UDialog):
    def __init__(self):
        logger.debug('Initizing clean cache window')
        super().__init__()
        self.setWindowTitle(filter_hotkey(get_lang('02')))

        # 加载常量
        logger.debug('Loading values')
        self.locked_checkbox = False # 锁定选择框模式，按下后将不会产生来自非手动操作的更新选择框
        # 清理缓存
        logger.debug('Loading cache config')
        with open(get_resource_path('vars', 'caches.json'), 'r', encoding='utf-8') as f:
            self.cache_config = json.load(f)
        self.path_list = [i['path'] for i in self.cache_config if i['path']]
        self.cache_config[-1]['exclude'] = self.merge_lists_dicts(*self.path_list)

        self.init_ui()

    def init_ui(self):
        logger.debug('Loading ui')
        # 创建面板
        layout = QGridLayout()

        logger.debug('Loading title')

        title = QLabel(get_lang('3d'))
        set_style(title, StyleClass.big_20)

        dest = QLabel(get_lang('3e'))
        set_style(dest, StyleClass.dest)

        # 布局1
        layout.addWidget(title, 0, 0, 1, 4)
        layout.addWidget(dest, 1, 0, 1, 4)

        # 加载ui
        file = QLabel(get_lang('33'))
        path = QLabel(get_lang('34'))
        dest = QLabel(get_lang('35'))
        size =  QLabel(get_lang('36'))

        set_style(file, StyleClass.b)
        set_style(path, StyleClass.b)
        set_style(dest, StyleClass.b)
        set_style(size, StyleClass.b)

        # 布局2
        layout.addWidget(file, 2, 0)
        layout.addWidget(path, 2, 1)
        layout.addWidget(dest, 2, 2)
        layout.addWidget(size, 2, 3)

        # 从json读取缓存列表
        logger.info('Loading cache list.')
        cache_list = {}

        with open(get_resource_path('vars', 'cleancache.json'), 'r', encoding='utf-8') as f:
            load_cache = json.load(f)

        # 解析缓存源文件
        for k, v in load_cache.items():
            if k.startswith(' '):
                cache_list[get_lang(k[1:])] = [] # 初始化空项
                k_is_lang = True
            else:
                cache_list[k] = []
                k_is_lang = False
            for value in v:
                if type(value) is str and value.startswith(' '):
                    if k_is_lang:
                        cache_list[get_lang(k[1:])].append(get_lang(value[1:]))
                    else:
                        cache_list[k].append(get_lang(value[1:]))
                else:
                    if k_is_lang:
                        cache_list[get_lang(k[1:])].append(value)
                    else:
                        cache_list[k].append(value)
                        
        logger.info('Load cache list successful.')

        self.cache_dir_list = {'logs'} # 缓存文件路径的列表
        self.cache_file_list = {'update.json'} # 缓存文件列表

        self.all_checkbox = UCheckBox(get_lang('db'))
        self.all_checkbox.setTristate(True)
        self.locked_checkbox = True # 临时切换
        self.all_checkbox.setCheckState(Qt.PartiallyChecked) # 初始状态为部分选中
        self.locked_checkbox = False # 锁定选择框模式

        self.all_size_text = QLabel(get_lang('37'))
        # 布局3
        logger.debug('加载布局-3')
        layout.addWidget(self.all_checkbox, 3, 0)
        layout.addWidget(self.all_size_text, 3, 3)

        size_index = 2 # 自定义字符大小的索引
        self.checkbox_list: list[UCheckBox] = [] # 缓存文件选择框的列表
        self.cache_path_list: list[QLabel] = [] # 文件路径字符的列表
        self.cache_size_list: list[QLabel] = [] # 缓存文件大小字符的列表
        logger.debug('Loading cache list')
        for i, d in enumerate(cache_list.items()): # 遍历缓存列表
            k = d[0]
            v = d[1]
            len_v = len(v)
            box = UCheckBox(k)
            box.setChecked(v[size_index + 1] if len_v > size_index + 1 else True)
            self.checkbox_list.append(box)
            path = QLabel(v[0])
            self.cache_path_list.append(path)
            dest = QLabel(v[1]) # 加载文件描述
            size = QLabel(get_lang('37'))
            self.cache_size_list.append(size) # 加载文件大小

            line = i + 4
            layout.addWidget(box, line, 0)
            layout.addWidget(path, line, 1)
            layout.addWidget(dest, line, 2)
            layout.addWidget(size, line, 3)

        # 按钮
        scan_cache = QPushButton(get_lang('38'))
        ok = QPushButton(get_lang('1f'))
        clean_cache = QPushButton(get_lang('39'))
        set_style(clean_cache, StyleClass.selected)

        # 布局4      
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch(1)
        bottom_layout.addWidget(scan_cache)
        bottom_layout.addWidget(clean_cache)
        bottom_layout.addWidget(ok)

        layout.addLayout(bottom_layout, line + 1, 2)

        # 绑定事件
        logger.debug('Singal connection')
        self.all_checkbox.stateChanged.connect(self.on_check)
        scan_cache.clicked.connect(self.on_scan_cache)
        clean_cache.clicked.connect(lambda: self.on_control_cache(clean=True))
        ok.clicked.connect(self.close)

        for checkbox in self.checkbox_list:
            checkbox.checkStateChanged.connect(self.update_all_check_status)

        # 设置布局
        logger.debug('Set layout')
        self.setLayout(layout)

        logger.debug('Initializing clean cache window successful.')

    def update_all_check_status(self):
        '''当任何复选框状态变化时自动更新全选按钮状态'''
        checked_count = list(map(lambda x: x.isChecked(), self.checkbox_list))
        self.locked_checkbox = True # 切换锁定模式

        if not any(checked_count):
            self.all_checkbox.setCheckState(Qt.Unchecked)
        elif all(checked_count):
            self.all_checkbox.setCheckState(Qt.Checked)
        else:
            self.all_checkbox.setCheckState(Qt.PartiallyChecked)

        self.locked_checkbox = False # 退出锁定模式

    def on_scan_cache(self):
        '''扫描缓存'''
        logger.info('Scaning cache')
        cache_size = self.on_control_cache(clean=False)
        total_size = 0
        for text, cache in zip(self.cache_size_list, cache_size):
            if cache is not None:
                text.setText(get_size_text(cache))
                total_size += cache

        self.all_size_text.setText(get_size_text(total_size))

    def try_to_remove_file(self, file_path: str):
        '''尝试删除文件'''
        try:
            size = 0
            if os.path.isfile(file_path):
                size = self.get_dir_or_file_size(file_path)
                os.remove(file_path)
            elif os.path.isdir(file_path):
                for root, dirs, files in os.walk(file_path):
                    for file in files:
                        size += self.try_to_remove_file(os.path.join(root, file))
            else:
                raise OSError('Not a file or directory')
            logger.info(f'Remove {file_path} successful.')
            return size
        except OSError as e:
            logger.warning(f'Remove {file_path} failed: {e}.')
            return 0

    def delete_empty_folders(self, root_path):
        '''删除所有空文件夹（包括嵌套的空文件夹）'''
        if not os.path.exists(root_path) or not os.path.isdir(root_path):
            return

        # 标记是否删除了任何文件夹
        deleted_any = False

        # 递归处理子文件夹
        for item in os.listdir(root_path):
            item_path = os.path.join(root_path, item)
            if os.path.isdir(item_path):
                if self.delete_empty_folders(item_path):
                    logger.debug(f'Add remove empty folder list: {item_path}')
                    deleted_any = True

        # 检查当前文件夹是否为空
        try:
            logger.debug(f'Checking {root_path}')
            items = os.listdir(root_path)
        except PermissionError:
            logger.warning(f'Permission denied when listing {root_path}')
            return deleted_any

        # 如果为空则删除
        if len(items) == 0:
            try:
                logger.info(f'Remove empty folder {root_path}')
                os.rmdir(root_path)
                return True
            except OSError:
                logger.warning(f'Remove empty folder {root_path} failed')
                pass

        return deleted_any

    def on_control_cache(self, clean: bool):
        '''清理或计算缓存'''
        logger.info('Calcuate cache cache')

        cache_clicked = list(map(lambda x: x.isChecked(), self.checkbox_list))
        if clean:
            cache_size = 0
        else:
            cache_size = [None for _ in cache_clicked]

        for i in self.cache_config:
            if cache_clicked[i['check_index']]: # 选择了该项
                if i['path'] is not None: # 是否全选
                    for items in chain(i['path']['dirs'], i['path']['files']):
                        if clean:
                            logger.info(f'Remove: {cache_path / items}')
                            cache_size += self.try_to_remove_file(cache_path / items)  
                        else:
                            logger.info(f'Calculate size: {cache_path / items}')
                            cache_size[i['check_index']] = self.get_dir_or_file_size(cache_path / items)
                else:
                    size = 0
                    for root, dirs, files in os.walk(cache_path):
                        for file in files:
                            if file in i['exclude']['files'] or self.contains_substring(i['exclude']['dirs'], root):
                                logger.info(f'Exclude: {os.path.join(root, file)}')
                                continue
                            if clean:
                                cache_size += self.try_to_remove_file(os.path.join(root, file))
                            else:
                                size += self.get_dir_or_file_size(os.path.join(root, file))
                    if not clean:
                        cache_size[i['check_index']] = size
                        
        if clean:
            # 清理空文件夹
            for root, dirs, files in os.walk(cache_path):
                for dir in dirs:
                    logger.info(f'Try toemove empty folder: {os.path.join(root, dir)}')
                    self.delete_empty_folders(os.path.join(root, dir))

            # 弹出提示窗口
            MessageBox.information(self, get_lang('16'), get_lang('3b').format(get_size_text(cache_size)))
        else:
            return cache_size

    def get_dir_or_file_size(self, dir_or_file_path: str) -> int:
        '''获取目录或文件大小'''
        logger.info('Calculate size of directory or file')
        if os.path.isfile(dir_or_file_path):
            # 是文件的情况
            size = os.path.getsize(dir_or_file_path)
            return size
        elif os.path.isdir(dir_or_file_path):
            # 是目录的情况
            size = 0
            for root, dirs, files in os.walk(dir_or_file_path):
                for file in files:
                    size += os.path.getsize(os.path.join(root, file))
            return size
        else:
            # 其他情况返回值
            return 0

    def merge_lists_dicts(self, *dicts):
        '''
        合并多个字典，每个字典的值都是列表

        Params:
        *dicts: 任意数量的字典，每个字典的值都是列表

        Returns:
        合并后的字典，每个键对应的值是列表，列表中元素不重复

        Raises:
        ValueError: 输入的字典中有重复元素
        TypeError: 输入的字典不是字典
        '''
        if len(dicts) < 2:
            raise ValueError('At least two dictionaries are required')

        for d in dicts:
            if not isinstance(d, dict):
                raise TypeError(f'Value {d} is not a dictionary')

        # 1. 收集所有键
        all_keys = set()
        for d in dicts:
            all_keys.update(d.keys())

        # 2. 合并每个键对应的列表
        merged_result = {}
        for key in all_keys:
            merged_list = []
            for d in dicts:
                if key in d:
                    merged_list.extend(d[key])

            # 对合并后的列表去重（保留1个）
            deduplicated = []
            seen = set()
            for item in merged_list:
                if item not in seen:
                    seen.add(item)
                    deduplicated.append(item)

            merged_result[key] = deduplicated

        # 3. 检查不同键之间是否有重复元素
        # 构建元素到键的映射
        element_to_keys = {}
        for key, values in merged_result.items():
            for value in values:
                if value in element_to_keys:
                    # 如果元素已经出现过，检查是否是同一个键
                    if key not in element_to_keys[value]:
                        # 同一个元素出现在不同键中，报错
                        raise ValueError(
                            f'The merged result contains duplicate items: the element {value} appears in keys {element_to_keys[value]} and {key}'
                        )
                else:
                    element_to_keys[value] = {key}

        return merged_result
    
    def contains_substring(self, str_list, target_str):
        '''
        检查目标字符串是否包含列表中的任意一个子串
        
        Params:
        str_list: 字符串列表，包含要查找的子串
        target_str: 目标字符串
        
        Returns:
        bool: 如果目标字符串包含列表中的任意一个子串则返回True，否则返回False
        '''
        return any(substring in target_str for substring in str_list)

    def on_check(self, state):
        '''全选按钮点击事件'''
        logger.info('All check box updated.')
        if state == Qt.CheckState.Unchecked: # 未选中
            if not self.locked_checkbox: # 非手动操作
                for checkbox in self.checkbox_list:
                    checkbox.setChecked(False)
        elif state == Qt.CheckState.PartiallyChecked: # 部分选中
            if not self.locked_checkbox: # 非手动操作
                self.all_checkbox.setCheckState(Qt.Checked)
        elif state == Qt.CheckState.Checked: # 全选
            if not self.locked_checkbox: # 非手动操作
                for checkbox in self.checkbox_list:
                    checkbox.setChecked(True)

class UpdateWindow(UDialog):
    def __init__(self):
        # 初始化
        logger.debug('Initizalizing update window')
        super().__init__()
        self.setWindowTitle(get_lang('29'))
        self.setGeometry(100, 100, 300, 110)
        self.setFixedSize(self.width(), self.height())
        self.setWindowIcon(icon)

        self.init_ui()
        self.down_thread = None # 下载线程

    def init_ui(self):
        # 创建面板
        logger.debug('Create layout')
        layout = QVBoxLayout()

        # 面板控件
        logger.debug('Create widget')
        title = QLabel(get_lang('24'))
        version = QLabel(get_lang('25').format(__version__, result[1]))

        set_style(title, StyleClass.big_16)

        # 按钮
        update = QPushButton(get_lang('26')) # 更新按钮
        set_style(update, StyleClass.selected)
        update_log = QPushButton(get_lang('27')) # 查看更新日志按钮
        cancel = QPushButton(get_lang('1f')) # 取消按钮

        bottom_layout = QHBoxLayout()
        # 绑定事件
        logger.debug('Signal connection')
        update.clicked.connect(self.on_update)
        update_log.clicked.connect(self.on_open_update_log)
        cancel.clicked.connect(self.close)

        # 布局
        logger.debug('Layout')
        layout.addWidget(title)
        layout.addWidget(version)

        bottom_layout.addStretch()
        bottom_layout.addWidget(update)
        bottom_layout.addWidget(update_log)
        bottom_layout.addWidget(cancel)

        layout.addLayout(bottom_layout)

        self.setLayout(layout)

        logger.debug('Initizalizing update window successful.')

    def exec(self):
        if setting_value.quiet_update:
            self.close()
            self.on_update()
        else:
            return super().exec()

    def on_update(self):
        '''更新'''
        if self.down_thread is None:
            try:
                self.close()
                os.rename('updater', 'updater.old')
                self.down_thread = QtThread(download_file, args=(web_data['down_web'].format(latest_version=result[4]), 'updater.old/clickmouse.7z'))
                self.down_thread.finished.connect(self.on_update_finished)
                self.down_thread.start()
            except:
                trace = format_exc()
                logger.exception('update failed', trace)
                revert_update()
                MessageBox.critical(self, get_lang('14'), f'{get_lang('bb')}：\n{trace}')
        else:
            MessageBox.critical(self, get_lang('14'), get_lang('4d'))
            
    def on_update_finished(self, state):
        '''更新完成'''
        global can_update
        if state[0]:
            hash_info = result[3]
            if get_file_hash('updater.old/clickmouse.7z', hash_info[1]) == hash_info[0]:
                can_update = True
                if setting_value.update_ok_notify:
                    update_ok_window.show()
            else:
                logger.exception('Update install', 'Update file hash check failed')
                MessageBox.critical(self, get_lang('14'), get_lang('bc'))
        else:
            logger.exception('Update install', state[1])
            MessageBox.critical(self, get_lang('14'), f'{get_lang('bb')}:\n{state[1]}')

    def on_open_update_log(self):
        # 打开更新日志
        logger.debug('Open update log')

        version = result[1]
        version = version.replace('.', '').replace('beta', 'b').replace('alpha', 'a')
        version_start = result[1].split('.')[0]
        is_pre = False
        if 'b' in version or 'a' in version or 'rc' in version or 'dev' in version:
            is_pre = True
        main_window.open_doc(path=f'updatelog/{'beta' if is_pre else 'final'}/{version_start}/{version}')

class UpdateOKWindow(UDialog):
    def __init__(self):
        # 初始化
        logger.debug(get_lang('b3'))
        super().__init__()
        self.setWindowTitle(get_lang('6e'))
        self.setGeometry(100, 100, 400, 100)
        self.setFixedSize(self.width(), self.height())

        self.init_ui()

    def init_ui(self):
        # 创建面板
        logger.debug('Create layout')
        layout = QVBoxLayout()

        # 面板控件
        logger.debug('Create widget')
        title = QLabel(get_lang('b3'))
        tip = QLabel(get_lang('b8'))

        set_style(title, StyleClass.big_16)

        # 按钮
        update = QPushButton(get_lang('7e')) # 更新按钮
        set_style(update, StyleClass.selected)
        update_log = QPushButton(get_lang('27')) # 查看更新日志按钮
        revert = QPushButton(get_lang('6a')) # 回滚更新按钮
        cancel = QPushButton(get_lang('1f')) # 取消按钮

        bottom_layout = QHBoxLayout()
        # 绑定事件
        logger.debug('Signal connection')
        update.clicked.connect(self.on_update)
        revert.clicked.connect(self.on_revert)
        update_log.clicked.connect(self.on_open_update_log)
        cancel.clicked.connect(self.close)

        # 布局
        logger.debug('Layout')
        layout.addWidget(title)
        layout.addWidget(tip)

        bottom_layout.addStretch()
        bottom_layout.addWidget(update)
        bottom_layout.addWidget(update_log)
        bottom_layout.addWidget(revert)
        bottom_layout.addWidget(cancel)

        layout.addLayout(bottom_layout)

        self.setLayout(layout)

        logger.debug('Initizalizing update window successful.')

    def on_update(self):
        '''更新'''
        run_software('updater.old/updater.py', 'updater.old/updater.exe')
        sys.exit(0)
        
    def on_revert(self):
        '''回滚'''
        global can_update
        logger.info('Revert update')
        revert_update()
        self.close()
        can_update = False
        MessageBox.information(self, get_lang('16'), get_lang('b9'))

    def on_open_update_log(self):
        # 打开更新日志
        update_window.on_open_update_log()

class ClickAttrWindow(UDialog):
    def __init__(self):
        logger.debug('Initizalizing click attribute window')
        super().__init__()
        self.setWindowTitle(filter_hotkey(get_lang('8c')))

        # 定义变量
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_attr)
        self.timer.start(setting_value.soft_delay)

        self.init_ui()

    def init_ui(self):
        self.layout_list = UIWindow(uiml.compile_ui_file(get_resource_path('ui', 'clickattr.gui'), additional=self.addtional_local_value))
        self.setLayout(self.layout_list.show())

        logger.debug('Initizalizing click attribute window successful.')

    def update_attr(self):
        '''更新属性'''
        logger.debug('update attribute')
        if is_error:
            _delay_num = get_lang('14')
            _time_num = get_lang('14')
        else:
            _delay_num = get_unit_text(delay_num)
            _time_num = get_lang('2b') if is_inf else str(time_num) + get_lang('66')

        left_clicked = self.layout_list.find_widget('central_layout.left_clicked')
        right_clicked = self.layout_list.find_widget('central_layout.right_clicked')
        click_delay = self.layout_list.find_widget('central_layout.click_delay')
        click_times = self.layout_list.find_widget('central_layout.click_times')
        paused = self.layout_list.find_widget('central_layout.paused')
        stopped = self.layout_list.find_widget('central_layout.stopped')
        total_run_time = self.layout_list.find_widget('central_layout.total_run_time')

        left_clicked.setText(f'{get_lang('0c')}: {get_lang('7b') if clicker.left_clicked else get_lang('7c')}')
        right_clicked.setText(f'{get_lang('0d')}: {get_lang('7b') if clicker.right_clicked else get_lang('7c')}')
        click_delay.setText(f'{get_lang('78')}: {_delay_num}')
        click_times.setText(f'{get_lang('5c')}: {_time_num}')
        paused.setText(f'{get_lang('0f')}: {get_lang('79') if clicker.paused else get_lang('7a')}')
        stopped.setText(f'{get_lang('0e')}: {get_lang('79') if not clicker.running else get_lang('7a')}')
        total_run_time.setText(main_window.total_time_label.text())

class SettingWindow(SelectUI, UMainWindow):
    click_setting_changed = Signal()
    window_restarted = Signal()

    def __init__(self, values:dict | None = None):
        super().__init__()

        logger.debug('Initizalizing setting window')
        self.setGeometry(300, 300, 625, 400)
        self.setFixedSize(self.width(), self.height())
        self.setWindowTitle(filter_hotkey(get_lang('04')))
        self.setParent(main_window)
        self.setWindowFlags(
            Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint
        ) # 设置窗口属性

        # 变量
        if dev_flags.get('new_settings', False):
            self.page_choice_buttons = [get_lang('42'), get_lang('a6'), get_lang('43'), get_lang('44'), get_lang('69'), filter_hotkey(get_lang('5f')), get_lang('cb'), get_lang('d3')]
            self.ui_file_name = ['general.gui', 'style.gui', 'clicker.gui', 'updater.gui', 'hotkey.gui', 'document.gui', 'notify.gui', 'flags.gui']
        else:
            self.page_choice_buttons = [get_lang('42'), get_lang('a6'), get_lang('43'), get_lang('44'), get_lang('69'), filter_hotkey(get_lang('5f')), get_lang('d3')]
            self.ui_file_name = ['general.gui', 'style.gui', 'clicker.gui', 'updater.gui', 'hotkey.gui', 'document.gui', 'notify.gui', 'flags.gui']

        # 主程序
        self.app = get_application_instance()

        self.create_setting_page_value()

        self.last_page = None
        self.now_page = 0
        self.values = {} if values is None else values
        self.code_list = {}

        self.init_ui()
        self.check_values() # 检查设置值

        # 连接信号
        clicker.started.connect(self.on_clicker_started)

        logger.debug('Initizalizing setting window successful.')
        # 将堆叠窗口部件设置为右侧滚动区域的内容
        self.right_scroll.setWidget(self.stacked_widget)
        
    def create_setting_page_value(self):
        self.page_general = self.page_choice_buttons[0] # 默认设置
        self.page_style = self.page_choice_buttons[1] # 样式设置
        self.page_click = self.page_choice_buttons[2] # 连点器设置
        self.page_update = self.page_choice_buttons[3] # 更新设置
        self.page_hotkey = self.page_choice_buttons[4] # 热键设置
        self.page_doc = self.page_choice_buttons[5] # 文档设置
        if dev_flags.get('new_settings', False):
            self.page_notify = self.page_choice_buttons[6] # 通知设置
            self.page_flags = self.page_choice_buttons[7] # 标志设置
        else:
            self.page_flags = self.page_choice_buttons[6] # 标志设置
            self.page_notify = ''
        
    def check_values(self):
        '''检查设置值'''
        # 热键设置
        if self.values.get('need_restart', False):
            self.on_need_restart_setting_changed(lambda: system_lang, 'select_lang')
        self.values.clear()
        
    def get_code(self, id) -> UIWindow:
        return self.code_list[id+'.gui']

    def create_setting_page(self, title):
        logger.info(f'Loading setting page: {title}')
        page = QWidget()

        def set_content_label(text):
            logger.debug(f'Set content label: {text}')
            content_label.setText(text)

        def create_horizontal_line():
            logger.debug('Create horizontal line')
            line = UFrame()
            return line
        
        def parse_hotkey(input: UHotkeyLineEdit):
            return input.text().split('+')
        
        self.addtional_local_value.update({'title': title})
        if title in [self.page_general, self.page_style, self.page_click]:
            layout_code = UIWindow(uiml.compile_ui_file(get_resource_path('ui', 'settings', self.ui_file_name[self.page_choice_buttons.index(title)]), additional=self.addtional_local_value))
            self.code_list[self.ui_file_name[self.page_choice_buttons.index(title)]] = layout_code
            
            layout = layout_code.show()
            page.setLayout(layout)
        else:
            layout = QVBoxLayout(page)
            # 标题标签
            title_label = QLabel(title)
            set_style(title_label, StyleClass.big_24)

            # 内容标签
            content_label = QLabel(get_lang('7d'))
            set_style(content_label, StyleClass.dest)
            
            # 布局
            layout.addWidget(title_label)
            layout.addWidget(content_label)
            layout.addWidget(create_horizontal_line())

        # 添加一些示例设置控件
        match title:
            case self.page_general:
                auto_start_manager.updated.connect(lambda enb: self.get_code('general').find_widget('general.start_layout.start_checkbox').setChecked(enb))
                self.get_code('general').find_widget('general.delay_layout.delay_label').setText(f'{get_lang('b0')}:{setting_value.soft_delay}{get_lang("ms", source=unit_lang)}')
            case self.page_click:
                self.default_delay: QLineEdit = self.get_code('clicker').find_widget('clicker.delay_layout.delay_input_layout.delay_input')
                self.delay_combo: QComboBox = self.get_code('clicker').find_widget('clicker.delay_layout.delay_input_layout.delay_combo')
                self.use_default_delay: QCheckBox = self.get_code('clicker').find_widget('clicker.delay_layout.error_use_default_delay')
                if not self.default_delay.text():
                    self.use_default_delay.setEnabled(False)
                self.default_time: QLineEdit = self.get_code('clicker').find_widget('clicker.times_layout.times_input_layout.times_input')
                self.times_combo: QComboBox = self.get_code('clicker').find_widget('clicker.times_layout.times_input_layout.times_combo')
                self.use_default_times: QCheckBox = self.get_code('clicker').find_widget('clicker.times_layout.error_use_default_times')
                if not self.default_time.text():
                    self.use_default_times.setEnabled(False)
                self.total_time_label: QLabel = self.get_code('clicker').find_widget('clicker.total_time_label')
                if dev_flags.get('new_settings', False):
                    self.modify_using_default_input = self.get_code('clicker').find_widget('clicker.attributes_layout.modify_using_default_input')
                    self.modify_using_default_combo = self.get_code('clicker').find_widget('clicker.attributes_layout.modify_using_default_combo')
            case self.page_update:
                set_content_label(get_lang('87'))
                # 选择更新检查提示
                self.enable_update = UCheckBox(get_lang('48')) # 开启更新
                self.enable_update.setChecked(setting_value.update_enabled)
                
                update_disable_text = QLabel(get_lang('d0')) # 更新禁止提示
                set_style(update_disable_text, StyleClass.d_11)
                
                self.update_notify = UCheckBox(get_lang('4a')) # 更新提示
                self.update_notify.setChecked(setting_value.update_notify)
                
                self.quiet_install = UCheckBox(get_lang('49')) # 静默安装
                self.quiet_install.setChecked(setting_value.quiet_update)
                
                self.update_ok = UCheckBox(get_lang('4c')) # 更新完成弹出提示
                self.update_ok.setChecked(setting_value.update_ok_notify)
                
                update_frequency_layout = QHBoxLayout() # 更新频率布局
                self.update_frequency = QComboBox() # 更新频率
                self.update_frequency.addItems([get_lang('bd'), get_lang('be'), get_lang('bf'), get_lang('c0')])
                self.update_frequency.setCurrentIndex(setting_value.update_frequency)
                update_frequency_layout.addWidget(QLabel(get_lang('c1')))
                update_frequency_layout.addWidget(self.update_frequency)
                update_frequency_layout.addStretch(1)

                # 布局
                layout.addWidget(self.enable_update)
                layout.addWidget(update_disable_text)
                layout.addWidget(self.update_notify)
                layout.addWidget(self.quiet_install)
                layout.addWidget(self.update_ok)
                layout.addLayout(update_frequency_layout)

                # 连接信号
                self.enable_update.checkStateChanged.connect(self.on_enable_update_changed)
                self.update_notify.checkStateChanged.connect(lambda: self.on_setting_changed(self.update_notify.isChecked, SettingText.update_notify))
                self.quiet_install.checkStateChanged.connect(lambda: self.on_setting_changed(self.quiet_install.isChecked, SettingText.quiet_update))
                self.update_ok.checkStateChanged.connect(lambda: self.on_setting_changed(self.update_ok.isChecked, SettingText.update_ok_notify))
                self.update_frequency.currentIndexChanged.connect(lambda: self.on_setting_changed(self.update_frequency.currentIndex, SettingText.update_frequency))
                if dev_flags.get('new_settings', False):
                    self.update_notify.checkStateChanged.connect(self.on_sync_notice)
                    self.update_ok.checkStateChanged.connect(self.on_sync_ok_notice)
                else:
                    self.on_enable_update(self.enable_update.isChecked())
            case self.page_hotkey:
                set_content_label(get_lang('21'))
                
                self.hotkey_enabled = UCheckBox(get_lang('c9')) # 热键启用
                self.hotkey_enabled.setChecked(setting_value.hotkey_enabled)

                self.hotkeys_widget_list = []

                self.hotkey_enabled.checkStateChanged.connect(self.on_enable_hotkey_changed)
                self.on_enable_hotkey_changed(self.hotkey_enabled.isChecked() if dev_flags.get('new_settings', False) else True)

                # 布局
                if dev_flags.get('new_settings', False):
                    layout.addWidget(self.hotkey_enabled)

                lang_id = {
                    "left_click": ["0c", False],
                    "right_click": ["0d", False],
                    "pause_click": ["6b", False],
                    "stop_click": ["6c", False],
                    "click_attr": ["8c", True],
                    "main_window": ["76", False]
                }

                for hotkey, enabled, lang, k in zip(
                    setting_value.hotkey_list.values(), 
                    setting_value.hotkey_enabled_list.values(),
                    lang_id.values(),
                    setting_keys,
                ):
                    # 设置元件
                    input = UHotkeyLineEdit()
                    input.setText(format_keys(hotkey))
                    repair_button = QPushButton(get_lang('20')) # 还原默认设置按钮

                    if not enabled:
                        repair_button.setEnabled(False)
                        input.setEnabled(False)

                    # 添加布局
                    hotkey_layout = QHBoxLayout()
                    hotkey_layout.addWidget(QLabel(f'{filter_hotkey(get_lang(lang[0])) if lang[1] else get_lang(lang[0])}: '), 1)
                    hotkey_layout.addWidget(input, 6)
                    hotkey_layout.addWidget(repair_button, 1)
                    hotkey_layout.addStretch()

                    layout.addLayout(hotkey_layout)

                    # 添加列表
                    self.hotkeys_widget_list.append([input, repair_button])

                    # 连接信号
                    input.textChanged.connect(lambda val, inp=input, key=k: self.on_setting_changed(lambda: parse_hotkey(inp), f'hotkey,hotkeys,{key}'))
                    repair_button.clicked.connect(lambda b, key=k: self.repair_settings([f'hotkey,hotkeys,{key}', f'hotkey,enabled,{key}']))
            case self.page_doc:
                set_content_label(get_lang('ca'))
                
                default_doc_layout = QHBoxLayout() # 默认打开文档布局
                
                default_doc_link = QLineEdit() # 默认打开文档链接
                default_doc_link.setText(setting_value.default_doc_link)
                repair_default_doc_link_button = QPushButton(get_lang('20')) # 还原默认设置按钮
                
                # 布局
                default_doc_layout.addWidget(QLabel(get_lang('c2')), 1) # 默认打开文档提示
                default_doc_layout.addWidget(default_doc_link, 6)
                default_doc_layout.addStretch()
                
                default_lang_layout = QHBoxLayout() # 默认文档语言布局
                lang_choice = QComboBox() # 语言选择框
                lang_choice.addItems([get_lang('45'), get_lang('c4')] + [i['lang_name'] for i in langs if i['supported']])
                lang_choice.setCurrentIndex(setting_value.lang_doc)
                
                # 布局
                default_lang_layout.addWidget(QLabel(get_lang('c5'))) # 默认文档语言提示
                default_lang_layout.addWidget(lang_choice)
                default_lang_layout.addStretch()
                
                update_log_path_layout = QHBoxLayout() # 更新日志路径布局
                update_log_path_input = QLineEdit() # 更新日志路径输入框
                update_log_path_input.setText(setting_value.update_log_path)
                
                repair_update_log_path_button = QPushButton(get_lang('20')) # 还原默认路径按钮
                
                # 布局
                update_log_path_layout.addWidget(QLabel(get_lang('c6')), 1) # 更新日志路径提示
                update_log_path_layout.addWidget(update_log_path_input, 6)
                update_log_path_layout.addStretch()
                
                label = QLabel(get_lang('c7'))
                # 布局
                set_style(label, StyleClass.d_11)
                
                layout.addLayout(default_doc_layout)
                layout.addLayout(default_lang_layout)
                layout.addWidget(create_horizontal_line())
                layout.addLayout(update_log_path_layout)
                layout.addWidget(create_horizontal_line())
                layout.addWidget(label)
                
                # 链接信号
                default_doc_link.textChanged.connect(lambda: self.on_setting_changed(default_doc_link.text, SettingText.default_doc_link))
                lang_choice.currentIndexChanged.connect(lambda: self.on_setting_changed(self.lang_choice.currentIndex, SettingText.lang_doc))
                update_log_path_input.textChanged.connect(lambda: self.on_setting_changed(update_log_path_input.text, SettingText.update_log_path))
                repair_default_doc_link_button.clicked.connect(lambda: self.repair_settings(SettingText.default_doc_link))
                repair_update_log_path_button.clicked.connect(lambda: self.repair_settings(SettingText.update_log_path))
            case self.page_notify:
                set_content_label(get_lang('cc'))

                # 更新提示
                self.notice_update_notify = UCheckBox(get_lang('4a'))
                self.notice_update_notify.setChecked(setting_value.update_notify)
                
                # 更新完成提示
                self.notice_update_ok_notify = UCheckBox(get_lang('4c'))
                self.notice_update_ok_notify.setChecked(setting_value.update_ok_notify)
                
                # 启用软件启动警告
                self.start_warning = UCheckBox(get_lang('cd'))
                tip_label = QLabel(get_lang('ce'))
                set_style(tip_label, StyleClass.d_11)
                self.start_warning.setChecked(setting_value.show_warning)
                
                self.package_warning = UCheckBox(get_lang('cf'))
                self.package_warning.setChecked(setting_value.show_package_warning)
                
                # 布局
                layout.addWidget(self.notice_update_notify)
                layout.addWidget(self.notice_update_ok_notify)
                layout.addWidget(create_horizontal_line())
                layout.addWidget(self.start_warning)
                layout.addWidget(tip_label)
                layout.addWidget(self.package_warning)
                
                # 连接信号
                self.notice_update_notify.checkStateChanged.connect(lambda: self.on_setting_changed(self.notice_update_notify.isChecked, SettingText.update_notify))
                self.notice_update_notify.checkStateChanged.connect(self.on_sync_notice)
                self.notice_update_ok_notify.checkStateChanged.connect(lambda: self.on_setting_changed(self.notice_update_ok_notify.isChecked, SettingText.update_ok_notify))
                self.notice_update_ok_notify.checkStateChanged.connect(self.on_sync_ok_notice)
                self.start_warning.checkStateChanged.connect(self.on_enable_warn)
                self.package_warning.checkStateChanged.connect(lambda: self.on_setting_changed(self.package_warning.isChecked, SettingText.show_package_warning))
               
                self.on_enable_update(self.enable_update.isChecked())
                self.on_warning_update(self.start_warning.isChecked())
            case self.page_flags:
                set_content_label(get_lang('d4'))
                
                if not dev_settings:
                    layout.addWidget(QLabel('No dev settings found.'))
                else:
                    for i in dev_settings:
                        checkbox = UCheckBox(i['name'])
                        if i['key'] == 'new_settings':
                            checkbox.checkStateChanged.connect(lambda chk,idx=i['key']:(self.save_dev_config(chk, idx),self.window_restarted.emit(),))
                        else:
                            checkbox.checkStateChanged.connect(lambda chk,idx=i['key']:(self.save_dev_config(chk, idx)))   
                        checkbox.setChecked(dev_flags.get(i['key'], False))
                        desc = QLabel(i['desc'])
                        set_style(desc, StyleClass.d_11)                        

                        layout.addWidget(checkbox)
                        layout.addWidget(desc)
                        layout.addWidget(create_horizontal_line())
            
        restart = uiml.compile_ui_file(get_resource_path('ui', 'settings', 'bottom.gui'), additional=self.addtional_local_value)
        
        layout.addLayout(UIWindow(restart).show())
        layout.addStretch(1)

        return page
    
    def on_clicker_changed(self, func, value, checkbox: UCheckBox=None):
        '''clicker更新状态改变事件'''
        if checkbox is not None:
            if not func():
                checkbox.setEnabled(False)
            else:
                checkbox.setEnabled(True)
        self.on_setting_changed(func, value)
        on_input_change(type=InputChange.setting_window)
    
    def on_theme_updated(self, theme: str):
        style_list = QStyleFactory.keys()
        
        self.on_setting_changed(lambda: style_list[theme], SettingText.theme)
        refresh.run()
        self.app.setStyle(style_list[theme])
    
    def on_hide_flag_changed(self, state):
        self.on_setting_changed(self.get_code('general').find_widget('general.hide_flag').isChecked, SettingText.hide_flags)
        self.restart_window()
    
    def on_soft_delay_changed(self, value):
        soft_delay: QSlider = self.get_code('general').find_widget('general.delay_layout.software_delay_layout.software_delay')
        delay_layout_text: QLabel = self.get_code('general').find_widget('general.delay_layout.delay_label')
        
        self.on_setting_changed(lambda: soft_delay.value() * 10 if soft_delay.value() > 0 else 1, SettingText.soft_delay)
        delay_layout_text.setText(f'{get_lang('b0')}: {soft_delay.value() * 10 if soft_delay.value() > 0 else 1}{get_lang("ms", source=unit_lang)}')
    
    def on_tray_checked(self, state):
        '''托盘图标选择事件'''
        tray = self.get_code('general').find_widget('general.tray_layout.tray')
        self.on_setting_changed(tray.isChecked, SettingText.show_tray_icon)
        self.app.setQuitOnLastWindowClosed(not tray.isChecked())
    
    def save_dev_config(self, checked: bool, flag_name: str):
        dev_flags[flag_name] = checked
        with open('data/dev_flags.json', 'w', encoding='utf-8') as f:
            json.dump(dev_flags, f)
    
    def on_warning_update(self, state):
        '''启用软件启动警告'''
        self.package_warning.setEnabled(state)
        
    def on_enable_warn(self, state):
        '''启用软件启动警告'''
        self.on_warning_update(state)
        self.on_setting_changed(self.start_warning.isChecked, SettingText.show_warning)
    
    def on_sync_notice(self, state):
        '''提示同步'''
        self.update_notify.setChecked(state)
        self.update_notify.setEnabled(setting_value.update_enabled)
    
    def on_sync_ok_notice(self, state):
        '''提示同步'''
        self.update_ok.setChecked(state)
        self.update_ok.setEnabled(setting_value.update_enabled)
    
    def on_enable_hotkey(self, state):
        '''启用热键'''
        for input, btn in self.hotkeys_widget_list:
            input.setEnabled(state)
            btn.setEnabled(state)
    
    def on_enable_update_changed(self, state):
        '''更新提示复选框状态改变'''
        global should_check_update_res

        self.on_enable_update(state)
        if not state:
            if MessageBox.warning(self, get_lang('15'), get_lang('c8'), MessageButton.YESNO) == MessageButton.ReturnValue.NO:
                self.enable_update.setCheckState(Qt.Checked)
                return
        else:
            should_check_update_res = should_check_update()
            main_window.on_check_update()
        self.on_setting_changed(self.enable_update.isChecked, SettingText.update_enabled)
        
    def on_enable_hotkey_changed(self, state):
        '''热键复选框状态改变'''
        self.on_enable_hotkey(state)
        self.on_setting_changed(self.hotkey_enabled.isChecked, SettingText.hotkey_enabled)
        
    def on_enable_update(self, state):
        '''更新提示复选框状态改变'''
        self.update_notify.setEnabled(state)
        self.quiet_install.setEnabled(state)
        self.update_ok.setEnabled(state)
        self.update_frequency.setEnabled(state)
        
    def repair_auto_start(self):
        logger.info('Repair auto start')
        os.remove(Path(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup', 'Clickmouse.lnk'))
        auto_start_manager.create_reg()
        MessageBox.information(self, get_lang('16'), get_lang('d2'))
    
    def repair_settings(self, key: str | list):
        '''
        还原默认设置

        :param key: 控制要恢复的设置项，可以是单个键，也可以是多个键组成的列表。
        '''
        global settings
        if MessageBox.warning(self, get_lang('15'), get_lang('22'), MessageButton.YESNO) != MessageButton.ReturnValue.NO: # 不确认重置
            return
        try:
            if isinstance(key, str):
                self.set_nested_value(settings, key, 'del', ) # 删除键：一个
            elif isinstance(key, list):
                for k in key:
                    self.set_nested_value(settings, k, 'del', ) # 删除键：多个
            else:
                raise ValueError(f'Invalid key type: {type(key)}')
        except KeyError:
            pass
        save_settings()
        self.window_restarted.emit()
            
    def repair_all_settings(self):
        logger.info('Reset all settings')
        global settings
        if MessageBox.warning(self, get_lang('15'), get_lang('22'), MessageButton.YESNO) != MessageButton.ReturnValue.NO: # 不确认重置
            return
        settings = {}
        save_settings()
        self.app.setStyle(default_theme)
        self.values.update({'need_restart': True}) # values 用于存储需要重启后还原的内容
        self.window_restarted.emit()

    def on_auto_start_changed(self, state):
        '''自启动复选框状态改变'''
        if state:
            auto_start_manager.enable()
        else:
            auto_start_manager.disable()

    def on_need_restart_setting_changed(self, handle, key: str, restart_place: list[str] = ['a9'], *args):
        '''托盘图标选择事件'''
        global settings_need_restart

        self.on_setting_changed(handle, key, *args)
        settings_need_restart = True

        lang = self.code_list['general.gui'].find_widget('general.lang_choice_layout.lang_choice').currentIndex()
        if lang >= 1:
            lang -= 1
        elif lang == 0:
            lang = system_lang

        restart_place = list(map(lambda x: get_lang(x, lang_id=lang), restart_place))

        need_restart = MessageBox.warning(self, get_lang('15', lang_id=lang), f'{get_lang("89", lang_id=lang)}: {", ".join(restart_place)}', MessageButton.YESNO, MessageButton.YES)
        if need_restart == MessageButton.ReturnValue.YES:
            self.restart()
        else:
            self.restart_window()

    def restart_window(self):
        self.window_restarted.emit()

    def on_setting_changed(self, handle, key, *args):
        '''更新检查提示选择事件'''
        logger.info(f'Setting changed: {key}')
        self.set_nested_value(settings, key, 'set', handle(*args))
        save_settings()

    def set_nested_value(self, dic: dict, path: str, mode:str, value=None) -> None:
        '''
        在字典中按路径设置值。
        - 如果路径不含逗号，则直接设置 dic[path] = value。
        - 如果路径含逗号，则按逗号分割为多级键，逐层递进，在最后一级键处设置值。
        若中间键不存在，则自动创建新字典；若中间键存在但不是字典，则覆盖为字典（原值丢失）。
        '''
        def check_dic(dic, path, val):
            if mode == 'set':
                dic[path] = val
            elif mode == 'del':
                del dic[path]
            else:
                raise ValueError('Invalid mode: ' + mode)

        if ',' not in path:
            check_dic(dic, path, value)
            return

        keys = [k.strip() for k in path.split(',')]  # 去除可能的空格
        current = dic
        # 逐层深入到倒数第二个键
        for key in keys[:-1]:
            if key not in current:
                check_dic(current, key, {})
            elif not isinstance(current[key], dict):
                raise ValueError('Invalid path: ' + path)  # 路径中存在无效的键
            current = current[key]
        # 在最后一级键处赋值
        check_dic(current, keys[-1], value)

    def on_page_button_clicked(self, index):
        '''处理页面按钮点击事件'''
        # 切换到对应的页面
        if index == self.page_choice_buttons.index(get_lang('43')) and clicker.running:
            MessageBox.critical(self, get_lang('14'), get_lang('aa'))
            return
        self.last_page = self.now_page
        self.stacked_widget.setCurrentIndex(index)
        self.now_page = self.stacked_widget.currentIndex()

        # 更新按钮样式
        for i, button in enumerate(self.buttons):
            if i == index:
                set_style(button, StyleClass.selected)
            else:
                set_style(button, StyleClass.none)

    def restart(self):
        app.quit(lambda: run_software('main.py', 'main.exe'))

    def init_right_pages(self):
        super().init_right_pages()
        set_style(self.buttons[0], StyleClass.selected)

    def on_clicker_started(self):
        '''连点器启动事件'''
        if self.now_page == self.page_choice_buttons.index(get_lang('43')):
            self.on_page_button_clicked(self.last_page)
            MessageBox.critical(self, get_lang('14'), get_lang('aa'))
            return

class SetImportExtensionModeWindow(UDialog):
    def __init__(self):
        super().__init__()
        logger.debug('Initializing import extension mode window')
        self.setWindowTitle(filter_hotkey(get_lang('92')))
        self.setGeometry(100, 100, 200, 125)
        self.setWindowIcon(icon)
        self.setFixedSize(self.width(), self.height())
        
        if dev_flags.get('decoupling', False):
            self.init_ui()
        else:
            self.init_ui_old()
            
    def init_ui(self):
        self.main_layout = UIWindow(uiml.compile_ui_file(get_resource_path('ui', 'importExtension.gui'), additional=self.addtional_local_value))
        self.setLayout(self.main_layout.show())

        logger.debug('Init import extension mode window finished')

    def init_ui_old(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # 选择扩展模式
        # 提示
        mode_label = QLabel(get_lang('ab'))
        mode_label.setAlignment(Qt.AlignCenter)
        set_style(mode_label, StyleClass.big_16)

        # 选择框
        self.mode_combo = QComboBox()
        self.mode_combo.addItems([get_lang('ac'), get_lang('ad')])
        self.mode_combo.setCurrentIndex(1)

        # 按钮
        mode_button = QPushButton(get_lang('1e'))

        # 布局
        layout.addWidget(mode_label)
        layout.addWidget(self.mode_combo)
        layout.addWidget(mode_button)

        # 连接信号
        mode_button.clicked.connect(self.on_mode_button_clicked_old)

        logger.debug('Init import extension mode window finished')

    def on_mode_button_clicked_old(self):
        self.close()
        main_window.show_import_extension(self.mode_combo.currentIndex())
        
    def on_mode_button_clicked(self):
        self.close()
        mode_combo = self.main_layout.find_widget('main_layout.mode_combo')
        # main_window.show_import_extension(mode_combo.currentIndex())

class TrayApp:
    def __init__(self):
        logger.info('Loading tray app framework')
        self.app = get_application_instance()

        show_tray_icon = setting_value.show_tray_icon
        if show_tray_icon:
            self.app.setQuitOnLastWindowClosed(False)  # 关闭窗口时不退出应用

        # 激活主窗口
        if '--quiet' not in sys.argv:
            main_window.show()

        # 加载警告
        if setting_value.show_warning:
            if (not has_packages) and setting_value.show_package_warning:
                MessageBox.warning(None, get_lang('15'), get_lang('ae'))

        # 创建热键监听器
        self.hotkey_listener = get_hotkey_listener_instance()
        hotkey_listener.combination_pressed.connect(self.run_combination)

        # 创建系统托盘图标
        self.setup_tray_icon()

        clicker.pause.connect(main_window.on_pause)
        clicker.click_changed.connect(main_window.on_click_changed)
        clicker.stopped.connect(main_window.on_stop)
        clicker.click_conuter.connect(main_window.on_click_counter)
        clicker.started.connect(main_window.on_start)

        logger.info('Initializing tray app finished')
        logger.info('Start finished.')

    def setup_tray_icon(self):
        '''设置系统托盘图标'''
        logger.info('Setting up tray icon')
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setIcon(icon)

        # 创建右键菜单
        self.create_menu()

        # 连接左键点击事件（显示主窗口）
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

        # 设置托盘提示
        self.tray_icon.setToolTip('clickMouse')

        # 显示托盘图标
        self.tray_icon.show()

    def create_menu(self):
        logger.info('Creatting tray icon menu')
        tray_menu = QMenu()

        # 添加'打开应用'菜单项
        show_action = QAction(get_lang('68'), self.app)
        show_action.triggered.connect(lambda: self.show_window(main_window))
        tray_menu.addAction(show_action)

        # 添加分隔线
        tray_menu.addSeparator()

        # 控制类按钮
        left_click_action = QAction(get_lang('0c'), self.app)
        right_click_action = QAction(get_lang('0d'), self.app)
        pause_action = QAction(get_lang('6b'), self.app)
        stop_action = QAction(get_lang('6c'), self.app)
        set_delay_action = QAction(get_lang('75'), self.app)
        click_attr_action = QAction(filter_hotkey(get_lang('8c')), self.app)

        left_click_action.triggered.connect(lambda: self.run_command(0))
        right_click_action.triggered.connect(lambda: self.run_command(1))
        pause_action.triggered.connect(lambda: self.run_command(2))
        stop_action.triggered.connect(lambda: self.run_command(3))
        click_attr_action.triggered.connect(lambda: self.show_window(click_attr_window))

        tray_menu.addAction(left_click_action)
        tray_menu.addAction(right_click_action)
        tray_menu.addAction(pause_action)
        tray_menu.addAction(stop_action)
        tray_menu.addAction(set_delay_action)
        tray_menu.addAction(click_attr_action)

        # 添加分割线
        tray_menu.addSeparator()

        # 添加'退出'菜单项
        quit_action = QAction(filter_hotkey(get_lang('03')), self.app)
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(quit_action)

        # 设置托盘图标的菜单
        self.tray_icon.setContextMenu(tray_menu)

    def start_hotkey_listener(self):
        '''启动热键监听器''' 
        logger.info('Starting hotkey listener')
        # 在后台线程中启动热键监听
        self.hotkey_thread = QtThread(self.hotkey_listener.start_listening)
        self.hotkey_thread.start()

    def on_tray_icon_activated(self, reason):
        '''处理托盘图标激活事件'''
        if reason == QSystemTrayIcon.ActivationReason.Trigger:  # 左键点击
            self.show_window(main_window)

    def check_delay(self, input_delay):
        try:
            math.ceil(float(input_delay))
        except Exception:
            trace = format_exc()
            MessageBox.critical(main_window, get_lang('13'), f'{get_lang('ae')}\n{trace}')
            logger.exception('Delay control', trace)
            return False
        return True

    def quit_application(self):
        '''退出应用程序'''
        # 停止热键监听
        self.hotkey_listener.stop_listening()
        self.app.quit()

    def run(self):
        '''运行应用程序'''
        logger.info('Running tray app')
        code = self.app.exec()
        logger.info(f'Main program exited with {code}')
        if can_update:
            run_software('updater.old/updater.py', 'updater.old/updater.exe')
        else:
            # 进行清理
            run_after.run()
            self.quit()
        sys.exit(code)
        
    def quit(self, code=lambda: None):
        if update_window.down_thread is not None:
            logger.info('Waiting for update thread to exit')
            if update_window.down_thread.isRunning():
                update_window.down_thread.quit()
                update_window.down_thread.wait(1000)  # 等待一段时间
                if update_window.down_thread.isRunning(): # 仍然运行，强制退出
                    logger.warning('Update thread is still running, force quit')
                    update_window.down_thread.terminate()  # 作为最后手段
                    update_window.down_thread.wait()
                revert_update()
        else:
            revert_update()
        self.quit_application()
        code()
        sys.exit(0)
        
    def run_combination(self, combination):
        '''运行组合键'''
        if can_run_hotkey and setting_value.hotkey_enabled:
            self.on_combination_pressed(combination)
            
    def on_start_clicker_tray(self, direction):
        '''启动托盘连点'''
        if direction == 'left': # 左键
            warn_text = 'left'
            button = main_window.left_click_button
            start_lang_id = '6f'
            func = clicker.mouse_left
        elif direction == 'right': # 右键
            warn_text = 'right'
            button = main_window.right_click_button
            start_lang_id = '70'
            func = clicker.mouse_right
        else:
            logger.critical('Invalid direction')
            return

        # 判断参数有效性
        if not button.isEnabled():
            logger.warning(f'{warn_text} click is not enabled.')
            self.tray_icon.showMessage(get_lang('14'), get_lang('1a'), QSystemTrayIcon.MessageIcon.Critical, 1000)
            return

        if not (self.check_delay(delay_num) or self.check_delay(time_num)):
            return

        if not clicker.running: # 判断是否正在运行
            self.tray_icon.showMessage(get_lang('6e'), get_lang(start_lang_id), QSystemTrayIcon.MessageIcon.Information, 1000)
            func(delay_num, time_num)
        else:
            self.tray_icon.showMessage(get_lang('6e'), get_lang('b7'), QSystemTrayIcon.MessageIcon.Warning, 1000)
    
    def show_window(self, window: QMainWindow | QDialog):
        '''显示窗口'''
        if window.isVisible():
            window.hide()
        else:
            window.show()
            refresh.run()
    
    def on_combination_pressed(self, combination):
        '''处理组合键事件'''
        combination = format_keys(combination, source=True)

        for index, i in enumerate(setting_keys):
            if all_in_list(combination, setting_value.hotkey_list[i]):
                self.run_command(index)
                break

    def run_command(self, command):
        '''运行命令'''
        match command:
            case 0:
                self.on_start_clicker_tray('left') # 左键
            case 1:
                self.on_start_clicker_tray('right') # 右键
            case 2:
                if clicker.running:
                    clicker.pause_click()
                    if clicker.paused:
                        self.tray_icon.showMessage(get_lang('6e'), get_lang('71'), QSystemTrayIcon.MessageIcon.Information, 1000)
                    else:
                        self.tray_icon.showMessage(get_lang('6e'), get_lang('72'), QSystemTrayIcon.MessageIcon.Information, 1000)
                else:
                    self.tray_icon.showMessage(get_lang('6e'), get_lang('74'), QSystemTrayIcon.MessageIcon.Warning, 1000)
            case 3:
                if clicker.running:
                    main_window.on_stop()
                    self.tray_icon.showMessage(get_lang('6e'), get_lang('73'), QSystemTrayIcon.MessageIcon.Information, 1000)
                else:
                    self.tray_icon.showMessage(get_lang('6e'), get_lang('74'), QSystemTrayIcon.MessageIcon.Warning, 1000)
            case 4:
                self.show_window(click_attr_window)
            case 5:
                self.show_window(main_window)
                if not main_window.isVisible():
                    main_window.is_start_from_tray = True
            case _:
                raise ValueError(f'Invalid command: {command}')
if __name__ == '__main__':
    init_success = False

    shared_memory = QSharedMemory(mem_id[0])
    if shared_memory.attach():
        # 已经有一个实例在运行
        QMessageBox.critical(None, get_lang('14'), get_lang('d6'))
        sys.exit(2)
    shared_memory.create(1)

    is_running = any(list(map(lambda x: QSharedMemory(x).attach(), mem_id[3:4])))
    if is_running:
        # 已经有一个实例在运行
        QMessageBox.critical(None, get_lang('14'), get_lang('d6'))
        sys.exit(2)

    with open(get_resource_path('langs', 'packages.json'), 'r', encoding='utf-8') as f:
        package_lang = json.load(f)

    data_path = Path('data')
    if not((data_path / 'first_run').exists()):
        run_as_admin('install_pack.py', 'install_pack.exe')
        sys.exit(0)
    else:
        with open(get_resource_path('package_info.json')) as f:
            packages_info = json.load(f)
        try:
            # 加载并移除弃用扩展
            packages = []
            with open('packages.json', 'r', encoding='utf-8') as f:
                packages_name: list = json.load(f)
            for i in packages_name.copy():
                try:
                    packages.append(import_package(i))
                except ValueError as e:
                    logger.warning(f'Extension {i} is deprecated. Auto delete.')
                    shutil.rmtree(f'extensions/{i}', ignore_errors=True)
                    del packages_name[packages_name.index(i)]
            for file in os.listdir('extensions'):
                full_path = os.path.join('extensions', file)
                # 检查是否是文件
                if os.path.isfile(full_path):
                    if file != 'packages.json':
                        os.remove(full_path)
                        logger.warning(f'Invalid extension {file} found. Auto delete.')
                elif os.path.isdir(full_path):
                    if file not in packages_name:
                        logger.warning(f'Extension {file} is deprecated. Auto delete.')
                        shutil.rmtree(full_path, ignore_errors=True)
            if (os.path.exists('packages.json')) and (os.path.exists('extensions/packages.json')):
                os.remove('extensions/packages.json')
            with open('packages.json', 'w', encoding='utf-8') as f:
                json.dump(packages_name, f)
        except FileNotFoundError:
            os.remove(data_path / 'first_run')
            with open(data_path / 'first_run', 'w'):pass
            if not(os.path.exists('packages.json')):
                package = ['xystudio.clickmouse']
                with open(fr'{Path.cwd()}\packages.json', 'w', encoding='utf-8') as f:
                    json.dump(package, f)
            if os.path.exists('extensions') and os.path.isdir('extensions'):
                shutil.rmtree('extensions')
            pass
        
        # Windows API常量
        logger.debug('Setting WinAPI const value')
        DWMWA_USE_IMMERSIVE = 20
        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        DWM_WINDOW_CORNER_PREFERENCE = 33
        DWMWCP_ROUND = 2
        DWMNCRP_ENABLED = 1

        logger.info('Loading services')
        icon = get_icon('icon')

        refresh = Refresh()
        setting_value = SettingValue()
        clicker = Click()
        auto_start_manager = StartManager()
        color_getter = ColorGetter()
        run_after = RunAfter()
        webview = UWebView()
        hotkey_listener = get_hotkey_listener_instance()

        logger.info('Loading value')
        logger.debug('Loading const value')
        has_packages = os.path.exists(get_resource_path('packages'))
        package_names, show_list, package_ids = get_packages()

        # 变量
        logger.info('Define pathes')

        # 定义数据路径
        cache_path = Path('cache')
        update_cache_path = cache_path / 'update.json'
        extension_path = Path('extensions')

        # 创建文件夹（如果不存在）
        data_path.mkdir(parents=True, exist_ok=True)
        cache_path.mkdir(parents=True, exist_ok=True)
        extension_path.mkdir(parents=True, exist_ok=True)

        # 创建资源
        update_cache = load_update_cache()
        should_check_update_res = should_check_update() if setting_value.update_enabled else False
        
        settings_need_restart = False
        can_update = False
        
        try:
            with open(data_path / 'dev_flags.json', 'r', encoding='utf-8') as f:
                dev_flags = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            dev_flags = {}
            
        try:
            with open(get_resource_path('dev_settings.json'), 'r', encoding='utf-8') as f:
                dev_settings = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            dev_settings = {}
        
        dev_back = dev_flags.copy()
        for k in dev_flags.keys():
            if k not in [i['key'] for i in dev_settings]:
                del dev_back[k]
                logger.warning(f'Beta feature ID:{k} is deprecated. Auto delete.')
        dev_flags = dev_back.copy()
        with open(data_path / 'dev_flags.json', 'w', encoding='utf-8') as f:
            json.dump(dev_flags, f)

        # 单位控制
        latest_index = 2

        # 热键管理相关
        is_error = True
        delay_num = 0
        time_num = 0

        # 其他
        can_run_hotkey = True # 热键是否可用
        result = (None, None, None, None) # 更新检查结果
        setting_keys = list(setting_value.hotkey_list.keys()) # 热键列表

        if in_dev:
            logger.info('In development mode')
            uiml.set_namespace(is_debug=True)

        # 系统版本
        windows_version = get_windows_version()
        if windows_version is None: # 非windows
            default_theme = 'Fusion'
        elif windows_version < 10: # 低于win10
            default_theme = 'Windows'
        elif windows_version == 10: # win10
            default_theme = 'Windows10'
        elif windows_version == 11: # win11
            default_theme = 'Windows11'
        else: # 未知
            default_theme = 'Fusion'

        logger.info('Loading data successed')

        logger.info('Check and update registry version.')

        # 检查版本号与注册表是否一致,不一样就修改注册表
        run_software('check_reg_ver.py', 'check_reg_ver.exe')

        # 移除过期组件
        shutil.rmtree('updater.old', ignore_errors=True)
        
        # 加载窗口
        logger.info('Loading ui')
        
        main_window = MainWindow()

        about_window = AboutWindow()
        clean_cache_window = CleanCacheWindow()
        update_ok_window = UpdateOKWindow()
        update_window = UpdateWindow()
        click_attr_window = ClickAttrWindow()
        setting_window = SettingWindow()
        set_import_extension_window = SetImportExtensionModeWindow()
        on_input_change(type=InputChange.setting_window) # 更新时间估计状态
        setting_window.click_setting_changed.connect(lambda: on_input_change(type=InputChange.setting_window))
        setting_window.window_restarted.connect(on_update_setting_window)

        app = TrayApp()
        app.app.setStyle(setting_value.theme)
        init_success = True
        app.run()