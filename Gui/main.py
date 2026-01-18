# 加载框架
from PySide6.QtWidgets import QApplication
import sys
app = QApplication(sys.argv)
from uiStyles.QUI import *

from pathlib import Path # 文件管理库
import pyautogui # 鼠标操作库
import threading # 用于鼠标点击
from time import sleep, time # 延迟
from webbrowser import open as open_url # 关于作者
from version import __version__ # 版本信息
from log import Logger # 日志库
from check_update import check_update # 更新检查
from datetime import datetime # 用于检查缓存的时间和现在相差的时间
import json # 用于读取配置文件
import os # 系统库
import shutil # 用于删除文件夹
from uiStyles import (SelectUI, UnitInputLayout, UCheckBox, styles, maps, StyleReplaceMode, UMessageBox, ULabel) # 软件界面样式
from uiStyles import indexes as style_indexes # 界面组件样式索引
from sharelibs import (run_software, is_process_running) # 共享库
import parse_dev # 解析开发固件配置
import winreg # 注册表库
from pynput import keyboard # 热键功能库
import math # 数学库
import subprocess # 子进程库
import traceback # 异常处理库
import colorsys # 颜色库

# 系统api
import ctypes
from ctypes import wintypes

logger = Logger('主程序日志')
logger.info('日志系统启动')

logger.debug('定义函数')

dev_config = parse_dev.parse()

def get_resource_path(*paths):
    '''
    获取资源文件路径
    '''
    try:
        logger.info(f'获取资源文件路径: {paths}')
        resource = Path('res') # 获取当前目录的资源文件夹路径
        if not resource.exists():
            raise FileNotFoundError(get_lang('13'))
        return str(resource.joinpath(*paths))
    except Exception as e:
        logger.error(f'获取资源文件路径失败: {e}')
        MessageBox.critical(None, get_lang('14'), f'{get_lang('12')}:{e}')
        sys.exit(1)

def get_lang(lang_package_id, lang_id = None, source = None):
    source = langs if source is None else source
    lang_id = select_lang if lang_id is None else lang_id
    for i in source:
        if i['lang_id'] == 0: # 设置默认语言包
            default_lang_text = i['lang_package']
        if i['lang_id'] == lang_id: # 设置目前语言包
            lang_text = i['lang_package']
    try:
        return lang_text.get(lang_package_id, default_lang_text[lang_package_id])
    except KeyError:
        logger.error(f'错误:出现一个不存在的语言包id:{lang_package_id}')
        return 'Language not found'
    except UnboundLocalError:
        lang_text = {}
        return lang_text.get(lang_package_id, default_lang_text[lang_package_id])
    
def get_lang_system_name(lang_id = None):
    # 获取系统语言名称
    lang_id = settings.get('select_lang', 0) if lang_id is None else lang_id
    for i in langs:
        if lang_id == i['lang_id']:
            return i['lang_system_name']
    
def filter_hotkey(text:str):
    return text.split('(')[0]
    
def load_update_cache():
    '''
    加载更新缓存文件
    '''
    logger.info('加载缓存文件')
    if update_cache_path.exists():
        with open(update_cache_path, 'r', encoding='utf-8') as f:
            cache = json.load(f)
        return cache
    else:
        logger.warning('缓存文件不存在，创建默认缓存文件')
        with open(update_cache_path, 'w', encoding='utf-8') as f:
            f.write('{}')
        return {}
   
def save_update_cache(**kwargs):
    '''写入更新缓存文件'''
    logger.info('写入缓存文件')
    
    update_info = kwargs.get('update_info', None)
    update_log = cache_path / 'update_log.md'
    
    if 'update_info' in kwargs:
        del kwargs['update_info']
    
    cache_data = {
        'last_check_time': time(),
        **kwargs
    }
    
    with open(update_cache_path, 'w', encoding='utf-8') as f:
        json.dump(cache_data, f)
        
    with open(update_log, 'w', encoding='utf-8') as f:
        if update_info:
            f.write(update_info)
        else:
            f.write(get_lang('58'))

def should_check_update():
    '''
    检查是否应该检查更新
    '''
    logger.info('检查是否应该检查更新')
    last_check_time = load_update_cache().get('last_check_time')
    if not last_check_time:
        return True
    last_check_time_stamp = datetime.fromtimestamp(last_check_time)
    now = datetime.now()
    if (now - last_check_time_stamp).total_seconds() > 3600 * 24:
        return True
    return False

def load_settings():
    '''
    加载设置
    '''
    logger.info('加载设置')
    try:
        with open(data_path / 'settings.json', 'r', encoding='utf-8') as f:
            settings = json.load(f)
        return settings
    except FileNotFoundError:
        logger.warning('配置文件不存在，创建默认配置文件')
        with open(data_path / 'settings.json', 'w', encoding='utf-8') as f:
            f.write('{}')
        return {}

def save_settings(settings):
    '''
    保存设置
    '''
    logger.info('保存设置')
    with open(data_path / 'settings.json', 'w', encoding='utf-8') as f:
        json.dump(settings, f)
        
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

def get_application_instance():
    '''获取或创建 QApplication 实例'''
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app

def all_in_list(list1, list2):
    if len(list1)!= len(list2):
        return False
    return all(item in list2 for item in list1)

def check_default_delay():
    '''检查默认延迟是否有效'''
    try:
        delay = int(settings.get('click_delay', ''))
        if not delay:
            return True
        if delay < 1:
            raise ValueError
        return True
    except ValueError:
        MessageBox.critical(None, get_lang('14'), get_lang('5b'))
        return False
        
def init_units():
    units = {'ms': 1}
    units['s'] = units['ms'] * 1000
    units['min'] = units['s'] * 60
    units['h'] = units['min'] * 60
    units['d'] = units['h'] * 24

    return units

def get_unit_value(value):
    unit = 1
    unit_text = get_lang('ms', source=unit_lang)
    for k, v in units.items():
        if value >= v:
            unit_text = get_lang(k, source=unit_lang)
            unit = v
    
    if unit_text == get_lang('d', source=unit_lang):
        unit_text = plural(value // unit, unit_text[:-1], unit_text)
    return (value / unit, unit_text)

def get_has_plural():
    return langs[settings.get('select_lang', 0)]['has_plural']

def plural(count, value, plural):
    if has_plural:
        return value if count == 1 else plural
    else:
        return value
    
def import_package(package_id: str):
    for i in packages_info:
        if i['package_name'] == package_id:
            return i
    raise ValueError(f'包名 {package_id} 不存在')

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

def new_color_bar(obj):
    '''
    给创建添加样式标题栏
    '''
    color_getter.style_changed.connect(lambda: color_getter.apply_titleBar(obj))
    color_getter.style_changed.emit()
    
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

class MessageBox(UMessageBox):
    @staticmethod
    def new_msg(parent, 
                title: str, 
                text: str, 
                icon: QMessageBox.Icon, 
                buttons: QMessageBox.StandardButton = QMessageBox.StandardButton.Ok,
                defaultButton: QMessageBox.StandardButton = QMessageBox.StandardButton.NoButton):
        
        msg_box = UMessageBox.new_msg(parent, title, text, icon, buttons, defaultButton)
        
        new_color_bar(msg_box)
        
        return msg_box

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
        
class HotkeyListener(QObject):
    '''热键监听器类，用于在后台线程中监听全局热键'''
    pressed_key = Signal(keyboard.Key)
    combination_pressed = Signal(list)  # 新增信号，用于发送组合键信息
    
    def __init__(self):
        super().__init__()
        self.listener = None
        self.is_listening = False
        self.pressed_keys = set()  # 用于跟踪当前按下的键
    
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
    
    def stop_listening(self):
        '''停止监听热键'''
        if self.listener and self.is_listening:
            self.is_listening = False
            self.listener.stop()
    
    def on_key_press(self, key):
        '''处理按键按下事件'''
        # 将按下的键添加到集合中
        self.pressed_keys.add(key)
        self.pressed_key.emit(key)
        
        # 检查是否为Ctrl+Alt+A组合键
        self.check_combination()
    
    def on_key_release(self, key):
        '''处理按键释放事件'''
        # 从集合中移除释放的键
        if key in self.pressed_keys:
            self.pressed_keys.remove(key)
    
    def check_combination(self):
        '''检查特定的组合键'''
        # 检查是否同时按下了Ctrl、Alt和A
        self.combination_pressed.emit(list(map(str, self.pressed_keys)))  # 发送组合键信息
                
class Click(QObject):
    pause = Signal(bool)
    click_changed = Signal(bool, bool)
    stopped = Signal()
    click_conuter = Signal(str, str, str) # 用于修复overflow问题
    started = Signal()
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.paused = False
        self.click_thread = None
        self.right_clicked = False
        self.left_clicked = False
        self.stop_count = 0  # 连点停止计数器，连续两次停止则恢复默认状态
        self.default_stop_1 = False  # 以1作为停止计数器的默认值
        
    def mouse_left(self, delay, times):
        logger.info('左键连点')
        self.mouse_click(button='left', input_delay=delay, times=times, default_stop_1=self.default_stop_1)
        self.default_stop_1 = False

    def mouse_right(self, delay, times):
        # 停止当前运行的点击线程
        logger.info('右键连点')
        self.mouse_click(button='right', input_delay=delay, times=times, default_stop_1=self.default_stop_1)
        self.default_stop_1 = False
        
    def set_default_clicked(self):
        self.left_clicked = False
        self.right_clicked = False
        self.click_changed.emit(self.left_clicked, self.right_clicked)
    
    def mouse_click(self, button: str, input_delay, times, default_stop_1=False):
        '''鼠标连点'''
        logger.info('开始连点')
        self.stop_count = 0
        if button == 'right':
            default_stop_1 = True
        
        if default_stop_1:
            self.stop_count = 1 # 右键停止计数器重置
        # 重置状态
        if self.click_thread and self.click_thread.is_alive():
            self.running = False
            self.paused = False
            self.pause.emit(False)
            self.click_thread.join()
        
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
            delay = math.ceil(float(input_delay))
        except Exception as e:
            MessageBox.critical(None, get_lang('14'), f'{get_lang('1b')} {str(e)}')
            logger.critical(f'发生错误:{e}')
            return

        # 创建独立线程避免阻塞GUI
        def click_loop():
            self.pause.emit(False)
            i = 0
            while i <= times and self.running:
                if not self.paused:
                    try:
                        pyautogui.click(button=button)
                        sleep(delay / 1000)
                        i += 1
                        if times == float('inf'):
                            self.click_conuter.emit('inf', str(i), str(delay))
                        else:
                            self.click_conuter.emit(str(times), str(i), str(delay))
                    except Exception as e:
                        MessageBox.critical(None, get_lang('14'), f'{get_lang('1b')}\n{traceback.format_exc()}')
                        logger.critical(f'发生错误:{e}')

                        self.stopped.emit()
                        break
                else:
                    sleep(delay / 1000)  # 暂停
            else:
                self.stop_count += 1
                if self.stop_count >= 2:
                    self.stopped.emit()
    
        # 启动线程
        logger.info(f'启动连点线程')
        self.started.emit()
        self.click_thread = threading.Thread(target=click_loop)
        self.click_thread.daemon = True
        self.click_thread.start()
                    
    def pause_click(self):
        logger.info('连点器暂停或重启')
        self.paused = not self.paused
        self.pause.emit(self.paused)
        
class Refresh:
    def __init__(self):
        self.steps = [
            self.refresh_title,
            self.left_check,
            self.right_check,
        ]
    
    def run(self):
        self.do_step(self.steps)
                
    def do_step(self, codes):
        # 尝试执行代码
        for code in codes:
            logger.info(f'执行步骤{code.__name__}')
            try:
                code()
                logger.info(f'步骤{code.__name__}执行成功')
            except NameError as e:
                logger.warning(f'步骤{code.__name__}操作存在未定义:{e}')
            except Exception as e:
                logger.error(f'步骤{code.__name__}执行失败:{e}')
        
    def refresh_title(self):
        QTimer.singleShot(1, color_getter.style_changed.emit)
    
    def left_check(self):
        if clicker.left_clicked:
            set_style(main_window.left_click_button, 'selected')
        else:
            logger.info('左键未连点')
            set_style(main_window.left_click_button, '')
    
    def right_check(self):
        if clicker.right_clicked:
            set_style(main_window.right_click_button,'selected')
        else:
            logger.info('右键未连点')
            set_style(main_window.right_click_button, '')

class ColorGetter(QObject):
    style_changed = Signal()
    
    def __init__(self):
        global refresh

        super().__init__()
        
        # 记录当前主题
        self.style = settings.get('select_style', 0)

        self.current_theme, self.windows_theme, self.windows_color, self.use_windows_color = self.load_theme()
        try:
            self.current_theme = self.current_theme.replace('auto-', '')
        except AttributeError:
            settings['select_style'] = 0
            save_settings(settings)
            MessageBox.critical(None, 'Error', 'Find the index of the style settings is out of range, the default style setting has been restored, please restart ClickMouse.')
            sys.exit(0)
        
        # 加载刷新服务
        refresh = Refresh()
    
        # 初始化时应用一次主题
        self.apply_global_theme()

        # 使用定时器定期检测主题变化
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_and_apply_theme)
        self.timer.start(1)
    
    def load_theme(self):
        logger.debug('获取最新的主题')
        
        theme = None
        windows_theme = None
        windows_color = None
        use_windows_color = None
        
        if self.style == 0:
            theme = QApplication.styleHints().colorScheme()
            if theme == Qt.ColorScheme.Dark:
                theme = 'auto-dark'
            elif theme == Qt.ColorScheme.Light:
                theme = 'auto-light'
        
        windows_theme = QApplication.styleHints().colorScheme()   
        if theme == Qt.ColorScheme.Dark:
            windows_theme = 'dark'
        elif theme == Qt.ColorScheme.Light:
            windows_theme = 'light'
            
        windows_color = get_windows_accent_color()
        use_windows_color = settings.get('use_windows_color', True)
        
        for k, v in maps.items():
            if v == settings.get('select_style', 0):
                theme = k
    
        return theme, windows_theme, windows_color, use_windows_color

    def check_and_apply_theme(self):
        '''检查主题是否变化，变化则重新应用'''
        logger.debug('检查主题是否变化')
        
        self.style = settings.get('select_style', 0)
        
        new_theme, new_windows_theme, new_windows_color, new_use_windows_color = self.load_theme()
        
        if new_theme != self.current_theme:
            self.current_theme = new_theme
            self.apply_global_theme()

        if new_windows_color != self.windows_color:
            self.windows_color = new_windows_color
            self.apply_global_theme()
            
        if new_windows_theme != self.windows_theme:
            self.windows_theme = new_windows_theme
            self.refresh()
            
        if new_use_windows_color != self.use_windows_color:
            self.use_windows_color = new_use_windows_color
            self.apply_global_theme()
            
    def refresh(self):
        logger.info('刷新软件')

        refresh.run()
            
    def apply_titleBar(self, window: QMainWindow | QDialog):
        '''应用标题栏样式'''
        logger.info('应用标题栏样式')
        
        hwnd = window.winId().__int__()
        
        if select_styles.css_data['.meta']['mode'] == 'dark':
            is_dark_mode = 1
        else:
            is_dark_mode = 0

        # 设置深色模式
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            wintypes.HWND(hwnd),
            DWMWA_USE_IMMERSIVE,
            ctypes.byref(wintypes.INT(is_dark_mode)),
            ctypes.sizeof(wintypes.INT)
        )

    def apply_global_theme(self):
        '''根据当前主题，为整个应用设置全局样式表'''
        global select_styles

        logger.info('应用全局样式表')

        app = get_application_instance()
        self.style_changed.emit()

        current_theme = self.current_theme.replace('auto-', '')
        
        select_styles = styles[current_theme]

        if self.use_windows_color:
            if select_styles.css_data['.meta']['mode'] == 'dark':
                select_styles = select_styles.replace(['.selected', 'background-color'], StyleReplaceMode.ALL, lighten_color_hex(self.windows_color, 0.4), output_json=False)
                select_styles = select_styles.replace(['.selected:hover', 'background-color'], StyleReplaceMode.ALL, lighten_color_hex(self.windows_color, 0.45), output_json=False)
                select_styles = select_styles.replace(['.selected', 'color'], StyleReplaceMode.ALL, 'black', output_json=False)
                select_styles = select_styles.replace(['.selected:hover', 'color'], StyleReplaceMode.ALL, 'black', output_json=False)
                select_styles = select_styles.replace(['QCheckBox', 'color'], StyleReplaceMode.ALL, 'black', output_json=False)
            else:
                select_styles = select_styles.replace(['.selected', 'background-color'], StyleReplaceMode.ALL, self.windows_color, output_json=False)
                select_styles = select_styles.replace(['.selected:hover', 'background-color'], StyleReplaceMode.ALL, lighten_color_hex(self.windows_color, 0.4), output_json=False)
            select_styles = select_styles.replace(['.selected:pressed', 'background-color'], StyleReplaceMode.ALL, lighten_color_hex(self.windows_color, -0.165), output_json=False)
            
        app.setStyleSheet(select_styles.css_text)  # 全局应用
        self.refresh()
    
def set_style(widget: QWidget, class_name: str):
    '''
    设置按钮的class属性并刷新样式
    '''
    # 1. 设置class属性
    widget.setProperty('class', class_name)
    
    # 2. 强制样式刷新
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    
    # 3. 触发重绘
    widget.update()
    
# Windows API常量
DWMWA_USE_IMMERSIVE = 20
DWMWA_USE_IMMERSIVE_DARK_MODE = 20
DWM_WINDOW_CORNER_PREFERENCE = 33
DWMWCP_ROUND = 2
DWMNCRP_ENABLED = 1

data_path = Path('data')
settings = load_settings()

clicker = Click()

color_getter = ColorGetter()

# 变量
logger.debug('定义资源')

logger.debug('定义数据路径和创建文件夹')

# 定义数据路径
cache_path = Path('cache')
update_cache_path = cache_path / 'update.json'

# 创建文件夹（如果不存在）
data_path.mkdir(parents=True, exist_ok=True)
cache_path.mkdir(parents=True, exist_ok=True)

# 创建资源
should_check_update_res = should_check_update()
update_cache = load_update_cache()
icon = QIcon(str(get_resource_path('icons', 'clickmouse', 'icon.ico')))

logger.debug('定义语言包')
with open(get_resource_path('langs', 'langs.json'), 'r', encoding='utf-8') as f:
    langs = json.load(f)
    
with open(get_resource_path('langs', 'packages.json'), 'r', encoding='utf-8') as f:
    package_lang = json.load(f)
    
with open(get_resource_path('langs', 'units.json'), 'r', encoding='utf-8') as f:
    unit_lang = json.load(f)

with open(get_resource_path('package_info.json')) as f:
    packages_info = json.load(f)
    
settings_need_restart = False

# 单位控制
units = init_units()
latest_index = 2
select_lang = settings.get('select_lang', 0)

logger.debug('定义资源完成')

logger.debug('加载ui')

class MainWindow(QMainWindow):
    def __init__(self):
        logger.info('初始化')

        super().__init__()
        self.setWindowTitle('ClickMouse')
        self.setWindowIcon(icon)
        self.setGeometry(100, 100, 500, 375)
        self.setWindowFlags(
            Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint
        ) # 设置窗口属性
        
        self.setFixedSize(self.width(), self.height()) # 固定窗口大小

        logger.debug('初始化状态控制变量')
        self.show_update_in_start = False # 是否在启动时显示更新提示
        self.total_run_time = 0  # 总运行时间
        self.is_ready = True  # 是否状态栏为“就绪”
        
        logger.debug('初始化ui')
        self.init_ui()
        
        new_color_bar(self)
        
        logger.debug('检查更新')
        self.on_check_update()
    
    def init_ui(self):
        # 创建主控件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_layout = QVBoxLayout(central_widget)
        
        # 创建标题大字
        title = QLabel(get_lang('0b'))
        
        # 创建标题风格
        set_style(title, 'big_text_20')
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
        
        logger.debug('初始化布局')
        
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
        set_style(self.total_time_label, 'big_text_14')
        self.total_time_label.textChanged.emit()
        
        # 创建状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # 设置默认状态
        self.status_bar.showMessage(get_lang('5d'))
        
        # 创建布局
        logger.debug('创建按钮布局')
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
        logger.debug('信号连接')
        self.left_click_button.clicked.connect(lambda:clicker.mouse_left(delay_num, time_num))
        self.right_click_button.clicked.connect(lambda:clicker.mouse_right(delay_num, time_num))
        
        self.pause_button.clicked.connect(clicker.pause_click)
        self.stop_button.clicked.connect(self.on_stop)
        
        self.input_delay.textChanged.connect(self.on_input_change)
        self.input_times.textChanged.connect(self.on_input_change)
        self.delay_combo.currentIndexChanged.connect(self.on_input_change)
        self.times_combo.currentIndexChanged.connect(self.on_input_change)
        
        self.status_bar.messageChanged.connect(self.reload_status)

        # 创建菜单栏
        logger.debug('创建菜单栏')
        self.create_menu_bar()
        
        # 刷新按钮状态
        logger.debug('刷新按钮状态')
        self.on_input_change()
        
        logger.info('初始化完成')
        
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
        file_menu = menu_bar.addMenu(get_lang('01'))
        
        # 清理缓存动作
        clean_cache_action = file_menu.addAction(get_lang('02'))
        
        # 退出动作
        exit_action = file_menu.addAction(get_lang('03'))
        
        # 设置菜单
        settings_menu = menu_bar.addMenu(get_lang('04'))
        settings_action = settings_menu.addAction(get_lang('05'))
        
        # 更新菜单
        update_menu = menu_bar.addMenu(get_lang('06'))
        
        # 更新菜单动作
        update_check = update_menu.addAction(get_lang('07'))
        update_log = update_menu.addAction(get_lang('08'))
        
        # 帮助菜单
        help_menu = menu_bar.addMenu(get_lang('09'))
        about_action = help_menu.addAction(get_lang('0a'))
        
        # 热键帮助
        hotkey_help = help_menu.addAction(get_lang('5e'))
        
        # 文档菜单
        doc = help_menu.addAction(get_lang('5f'))

        # 扩展菜单
        extension_menu = menu_bar.addMenu(get_lang('8e'))
        official_extension_menu = extension_menu.addMenu(get_lang('90'))
        if not any(show_list):
            # 无官方扩展提示
            official_extension_menu.addAction(get_lang('91')).setDisabled(True)
        else:
            # 加载官方扩展菜单
            for name, show, package_id in zip(package_names, show_list, package_ids):
                if show:
                    official_extension_menu.addAction(name).triggered.connect(lambda chk, idx=package_id: self.do_extension(idx)) # 给菜单项添加ID，方便绑定事件
        manage_extension_menu = official_extension_menu.addAction(get_lang('92'))
        manage_extension_menu.triggered.connect(self.show_manage_extension) # 管理扩展菜单
        manage_extension_menu.setEnabled(has_packages)
        
        not_official_extension_menu = extension_menu.addMenu(get_lang('93'))
        
        cge_menu = not_official_extension_menu.addMenu(get_lang('94'))
        cge_menu.addAction(get_lang('95')).setDisabled(True)
        
        cmm_menu = not_official_extension_menu.addMenu(get_lang('96'))
        cmm_menu.addAction(get_lang('97')).setDisabled(True)

        not_official_extension_menu.addSeparator()

        not_official_extension_menu.addAction(get_lang('98')).triggered.connect(self.show_import_extension_mode) # 管理扩展菜单
        not_official_extension_menu.addAction(get_lang('92')).triggered.connect(self.show_manage_not_official_extension) # 管理扩展菜单
        
        # 宏菜单
        macro_menu = menu_bar.addMenu(get_lang('99'))
        
        run_marco_menu = macro_menu.addMenu(get_lang('9d'))
        for action in cmm_menu.actions():
            run_marco_menu.addAction(action)
            
        macro_menu.addAction(get_lang('9a')).triggered.connect(self.show_import_macro) # 导入宏
        macro_menu.addAction(get_lang('9b')).triggered.connect(self.show_manage_not_official_extension) # 管理宏
            
        # 绑定动作
        about_action.triggered.connect(self.show_about)
        update_log.triggered.connect(self.show_update_log)
        clean_cache_action.triggered.connect(self.show_clean_cache)
        update_check.triggered.connect(lambda: self.on_update(True))
        settings_action.triggered.connect(self.show_setting)
        hotkey_help.triggered.connect(self.show_hotkey_help)
        exit_action.triggered.connect(app.quit)
        
    def do_extension(self, index):
        '''执行扩展'''
        try:
            match index:
                case 'xystudio.clickmouse.repair':
                    QMessageBox.information(self, get_lang('16'), get_lang('b3').format(Path.cwd() / 'repair.exe'))
                    return
                case _:
                    subprocess.Popen(f'extensions/{index}/main.exe')
        except Exception as e:
            MessageBox.critical(self, get_lang('14'), get_lang('9c').format(e))
            logger.error(f'执行扩展失败: {e}')
            
    def show_manage_extension(self):
        '''管理扩展'''
        logger.info('打开扩展管理窗口')
        
        run_software('install_pack.py' ,'install_pack.exe')
        
    def show_import_extension_mode(self):
        '''导入扩展模式'''
        logger.info('打开导入扩展窗口')

        import_extension_window = SetImportExtensionModeWindow()
        import_extension_window.exec()
        
    def show_import_extension(self, mode):
        '''导入扩展'''
        logger.info('导入扩展')
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
            except Exception as e:
                logger.error(f'导入扩展失败: {e}')
                MessageBox.critical(self, get_lang('a1'), get_lang('a5').format(e))
                return
        else:
            return
        
    def show_manage_not_official_extension(self):
        '''管理第三方扩展'''
        logger.info('打开第三方扩展管理窗口')
        
        MessageBox.information(self, get_lang('a1'), get_lang('a4'))
        
    def show_import_macro(self):
        '''导入宏'''
        logger.info('导入宏')

        file_name, _ = QFileDialog.getOpenFileName(self, get_lang('9e'), '', get_lang('9f').split(';;')[2])

        if file_name:
            try:
                # 导入扩展
                MessageBox.information(self, get_lang('a1'), get_lang('a4'))
            except Exception as e:
                logger.error(f'导入宏失败: {e}')
                MessageBox.critical(self, get_lang('a1'), get_lang('a5').format(e))
                return
        else:
            return
            
    def show_about(self):
        '''显示关于窗口'''
        about_window = AboutWindow()
        about_window.exec()
        
    def show_update_log(self):
        '''显示更新日志'''
        update_log_window = UpdateLogWindow()
        update_log_window.exec()
    
    def show_clean_cache(self):
        '''清理缓存'''
        clean_cache_window = CleanCacheWindow()
        clean_cache_window.exec()

    def show_hotkey_help(self):
        '''显示热键帮助'''
        hotkey_help_window.show()
    
    def show_setting(self):
        '''显示设置窗口'''
        global setting_window
        
        try:
            idx = setting_window.stacked_widget.currentIndex()
        except NameError:
            idx = 0

        setting_window = SettingWindow(self)
        
        setting_window.click_setting_changed.connect(self.on_input_change)
        setting_window.window_restarted.connect(self.show_setting)

        setting_window.show()
        setting_window.on_page_button_clicked(idx)

    def on_check_update(self):
        # 检查更新
        if should_check_update_res:
            shutil.rmtree(str(cache_path / 'logs'), ignore_errors=True) # 删除旧缓存
            self.check_update_thread = QtThread(check_update, args=('gitee', False))
            self.check_update_thread.finished.connect(self.on_check_update_result)
            self.check_update_thread.start()
        else:
            logger.info('距离上次更新检查不到1天，使用缓存')
            self.on_check_update_result(update_cache)
            
    def on_check_update_result(self, check_data):
        '''检查更新结果'''
        global result

        # 判断是否需要缓存
        if should_check_update_res:
            result = check_data
        else:
            result = (update_cache['should_update'], update_cache['latest_version']) # 使用缓存
        
        # 检查结果处理
        if settings.get('update_notify', 0) in {0}: # 判断是否需要弹出通知
            if result[1] != -1:  # -1表示函数出错
                if should_check_update_res:
                    save_update_cache(should_update=result[0], latest_version=result[1], update_info=result[2]) # 缓存最新版本
                    pass
                if result[0]:  # 检查到需要更新
                    logger.info('检查到更新')
                    # 弹出更新窗口
                    self.show_update_in_start = True
                    if should_check_update_res:
                        # 弹出更新提示
                        self.on_update()
            else:
                if self.check_update_thread.isFinished():
                    logger.error(f'检查更新错误: {result[0]}')
                    MessageBox.critical(self, get_lang('14'), f'{get_lang('18')}{result[0]}')
        else:
            if result[1] != -1:
                if should_check_update_res:
                    save_update_cache(should_update=result[0], latest_version=result[1], update_info=result[2])
    
    def on_update(self, judge = False):
        '''显示更新提示'''
        if judge:
            if result[0]: # 检查到需要更新
                update_window = UpdateWindow()
                update_window.exec()
            else:
                MessageBox.information(self, get_lang('16'), get_lang('19'))
        else:
            update_window = UpdateWindow()
            update_window.exec()

    def show(self):
        super().show()
        if self.show_update_in_start:
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
        logger.info('停止连点')

        # 禁用按钮
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        
        # 启用按钮
        self.input_times.setEnabled(not is_inf)
        self.input_delay.setEnabled(True)
        self.delay_combo.setEnabled(True)
        self.times_combo.setEnabled(True)
        
        # 重置变量
        clicker.running = False
        clicker.left_clicked = False
        clicker.right_clicked = False
        clicker.paused = False
        self.is_ready = True
        
        # 重置按钮样式
        set_style(self.left_click_button, '')
        set_style(self.right_click_button, '')
        
        # 重置文本
        self.pause_button.setText(get_lang('0f'))
        self.status_bar.showMessage(get_lang('5d'))
    
    def on_start(self):
        '''开始连点'''
        logger.info('开始连点')
        
        # 禁用按钮
        self.input_times.setEnabled(False)
        self.input_delay.setEnabled(False)
        self.delay_combo.setEnabled(False)
        self.times_combo.setEnabled(False)

    def on_click_changed(self, left, right):
        '''click按钮状态改变'''
        if left:
            # 左键点击
            set_style(self.left_click_button, 'selected')
            set_style(self.right_click_button, '')
        elif right:
            # 右键点击
            set_style(self.right_click_button, 'selected')
            set_style(self.left_click_button, '')
        else:
            # 未点击
            set_style(self.left_click_button, '')
            set_style(self.right_click_button, '')

    def check_default_var(self, value):
        '''检查默认延迟是否有效'''
        try:
            var = int(settings.get(f'click_{value}', ''))
            if not var:
                return True
            if var < 1:
                raise ValueError
            return True
        except ValueError:
            self.on_delay_error(get_lang('60'))
            return False
        
    def on_delay_error(self, error_text=get_lang('14')):
        '''输入延迟错误'''
        global is_error
        
        is_error = True
        self.total_time_label.setText(f'{get_lang('2c')}: {error_text}')
        self.right_click_button.setEnabled(False)
        self.left_click_button.setEnabled(False)
    
    def on_input_change(self, var=None):
        '''输入延迟改变'''
        global is_inf, is_error, delay_num, time_num

        # 判断参数有效性
        input_delay = self.input_delay.text().strip()
        input_times = self.input_times.text().strip()
        is_inf = False
        is_error = False
        delay_num = settings.get('click_delay', '')
        time_num = settings.get('click_times', '')
        delay = 0

        self.input_times.setEnabled(not(self.times_combo.currentIndex() == latest_index or settings.get('times_unit', 0) == latest_index))

        if self.times_combo.currentIndex() == latest_index or input_times == '0' or settings.get('times_unit', 0) == latest_index:
            is_inf = True
        
        try:
            delay = math.ceil(float(input_delay))
            if delay < 1:
                raise ValueError
        except ValueError:
            if not settings.get('click_delay', '') == '':
                if input_delay == '':
                    if self.check_default_var('delay'):
                        delay = int(settings.get('click_delay', ''))
                    else:
                        return
                elif settings.get('failed_use_default', False):
                    if self.check_default_var('delay'):
                        delay = int(settings.get('click_delay', ''))
                    else:
                        return
                else:
                    self.on_delay_error()
                    return
        except Exception:
            self.on_delay_error()
            return

        if not is_inf:
            try:
                times = math.ceil(float(input_times))
                if times < 1:
                    raise ValueError
            except ValueError:
                if settings.get('click_times', '') == '' and settings.get('click_delay', '') == '':
                    self.on_delay_error(get_lang('61'))
                    return
                else:
                    if input_times == '':
                        if self.check_default_var('times'):
                            times = int(settings.get('click_times', ''))
                        else:
                            return
                    elif settings.get('times_failed_use_default', False):
                        if self.check_default_var('times'):
                            times = int(settings.get('click_times', ''))
                        else:
                            return
                    else:
                        self.on_delay_error()
                        return
            except Exception:
                self.on_delay_error()
                return
        
        self.right_click_button.setEnabled(True)
        self.left_click_button.setEnabled(True)
        is_error = False
        
        if settings.get('click_delay', '') != '' and input_delay == '':
            match settings.get('delay_unit', 0):
                case 0:
                    delay_num = delay
                case 1:
                    delay_num = delay * 1000
        else:
            match self.delay_combo.currentIndex():
                case 0:
                    delay_num = delay
                case 1:
                    delay_num = delay * 1000
                case 2:
                    delay_num = delay * 60 * 1000
                case _:
                    delay_num = delay

        if is_inf:
            self.total_time_label.setText(f'{get_lang('2c')}: {get_lang('2b')}')
            if delay_num == 0:
                self.on_delay_error()
        else:
            if settings.get('click_times', '') != '' and input_times == '':
                match settings.get('times_unit', 0):
                    case 0:
                        time_num = times
                    case 1:
                        time_num = times * 10000
            else:
                match self.times_combo.currentIndex():
                    case 0:
                        time_num = times
                    case 1:
                        time_num = times * 10000
                    case 2:
                        time_num = times * 100_0000
                    case _:
                        time_num = times
            
            if (delay_num == 0 and time_num != 0) or (delay_num != 0 and time_num == 0):
                self.on_delay_error()
                return
                                        
            self.total_run_time = delay_num * time_num
            self.total_time_label.setText(f'{get_lang('2c')}: {self.total_run_time}{get_lang('ms', source=unit_lang)}')
            self.total_run_time = get_unit_value(self.total_run_time)
            self.total_time_label.setText(f'{get_lang('2c')}: {self.get_full_unit(self.total_run_time)}')
    
    def on_click_counter(self, totel, now, delay):
        '''连点计数器'''
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

class AboutWindow(QDialog):
    def __init__(self):
        super().__init__()
        logger.info('初始化关于窗口')
        self.setWindowTitle(filter_hotkey(get_lang('0a')))
        self.setGeometry(100, 100, 375, 175)
        self.setWindowIcon(icon)
        self.setFixedSize(self.width(), self.height())
        self.init_ui()
        
        new_color_bar(self)

    def init_ui(self):
        # 创建面板
        logger.debug('创建面板')
        central_layout = QGridLayout()

        # 面板控件
        logger.debug('创建组件')

        # 绘制内容
        logger.debug('绘制内容')

        self.image_label = QLabel()
        # 加载图片
        self.loadImage(get_resource_path('icons', 'clickmouse', 'icon.png'))
        
        # 版本信息
        version_status_text = get_lang('65') if ('alpha' in __version__) or ('beta' in __version__) or ('dev' in __version__) else ''
        version = QLabel(get_lang('1c').format(__version__, version_status_text))
        if not dev_config['verify_clickmouse']:
            not_official_version = QLabel(get_lang('67'))
            central_layout.addWidget(not_official_version, 1, 1, 1, 2)
        about = QLabel(get_lang('1d'))
        
        # 按钮
        logger.debug('创建按钮')
        ok_button = QPushButton(get_lang('1e'))
        set_style(ok_button, 'selected')
        support_author = QPushButton(get_lang('20'))

        # 布局
        central_layout.addWidget(self.image_label, 0, 0, 1, 1)
        central_layout.addWidget(version, 0, 1, 1, 2)
        central_layout.addWidget(about, 2, 0, 1, 3)
        central_layout.addWidget(support_author, 3, 0)
        central_layout.addWidget(ok_button, 3, 2)

        self.setLayout(central_layout)
        
        # 绑定事件
        logger.debug('绑定事件')
        support_author.clicked.connect(self.on_support_author)
        ok_button.clicked.connect(self.close)
        logger.info('初始化关于窗口完成')
        
    def loadImage(self, image_path):
        '''加载并显示图片'''
        # 创建QPixmap对象
        pixmap = QPixmap(image_path)
        
        # 按比例缩放图片以适应标签大小
        scaled_pixmap = pixmap.scaled(
            50, 
            50,
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)

    def on_support_author(self):
        '''支持作者'''
        open_url('https://github.com/xystudio889/pyClickMouse')

class UpdateLogWindow(QDialog):
    def __init__(self):
        logger.info('初始化更新日志窗口')
        super().__init__()
        self.setWindowTitle(filter_hotkey(get_lang('08')))
        self.setWindowIcon(icon)

        logger.debug('加载更新日志')
        
        if settings.get('select_lang', 0) != 1:
            MessageBox.information(self, get_lang('16'), get_lang('21'))

        with open(get_resource_path('vars', 'update_log.json'), 'r', encoding='utf-8') as f:
            self.update_logs = json.load(f) # 加载更新日志
            
        logger.debug('初始化更新日志窗口')
        self.init_ui()
        
        new_color_bar(self)

    def init_ui(self):
        # 创建面板
        layout = QVBoxLayout()

        # 通过字典存储的日志信息来绘制日志内容，并动态计算日志的高度，减少代码量且更加方便管理
        for k, v in self.update_logs.items():
            title_label = QLabel(f'{k}    {v[0]}')
            set_style(title_label, 'big_text_14')
            log_label = QLabel(f'{v[1]}')
            layout.addWidget(title_label)
            layout.addWidget(log_label)

        # 调整页面高度，适配现在的更新日志界面大小
        logger.debug('调整页面高度')

        # 面板控件
        license_label = QLabel(get_lang('22'))

        # 按钮
        logger.debug('创建按钮')
        
        bottom_layout = QHBoxLayout() # 底布局
        
        ok_button = QPushButton(get_lang('1e'))
        set_style(ok_button, 'selected')
        more_update_log = QPushButton(get_lang('23'))
        
        bottom_layout.addStretch(1)
        bottom_layout.addWidget(more_update_log)
        bottom_layout.addWidget(ok_button)
        
        # 绑定事件
        logger.debug('绑定事件')
        ok_button.clicked.connect(self.close)
        more_update_log.clicked.connect(self.on_more_update_log)
        
        # 设置布局
        logger.debug('设置布局')
        layout.addWidget(license_label)
        layout.addLayout(bottom_layout)
        
        logger.info('初始化更新日志窗口完成')
        
        self.setLayout(layout)

    def on_more_update_log(self):
        '''显示更多更新日志'''
        logger.info('显示更多更新日志')
        open_url('https://github.com/xystudio889/pyClickMouse/releases')

class CleanCacheWindow(QDialog):
    def __init__(self):
        logger.info('初始化清理缓存窗口')
        super().__init__()
        self.setWindowTitle(filter_hotkey(get_lang('02')))
        self.setWindowIcon(icon)

        # 加载常量
        logger.debug('加载常量')
        self.locked_checkbox = False # 锁定选择框模式，按下后将不会产生来自非手动操作的更新选择框
        
        self.init_ui()
        
        new_color_bar(self)

    def init_ui(self):
        logger.debug('加载ui')
        # 创建面板
        layout = QGridLayout()
        
        # 面板控件
        logger.debug('加载ui')
        logger.debug('加载列表标题')
        
        title = QLabel(get_lang('3d'))
        set_style(title, 'big_text_20')

        dest = QLabel(get_lang('3e'))
        set_style(dest, 'dest')
        
        # 布局1
        logger.debug('加载布局-1')
        layout.addWidget(title, 0, 0, 1, 4)
        layout.addWidget(dest, 1, 0, 1, 4)
        
        logger.debug('加载动态数据')

        # 加载ui
        file = QLabel(get_lang('33'))
        path = QLabel(get_lang('34'))
        dest = QLabel(get_lang('35'))
        size =  QLabel(get_lang('36'))
        
        set_style(file, 'bold')
        set_style(path, 'bold')
        set_style(dest, 'bold')
        set_style(size, 'bold')
        # 布局2
        logger.debug('加载布局-2')
        layout.addWidget(file, 2, 0)
        layout.addWidget(path, 2, 1)
        layout.addWidget(dest, 2, 2)
        layout.addWidget(size, 2, 3)
        
        # 从json读取缓存列表
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

        self.cache_dir_list = {'logs'} # 缓存文件路径的列表
        self.cache_file_list = {'update.json'} # 缓存文件列表

        self.all_checkbox = UCheckBox('')
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
        logger.debug('加载动态内容')
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
        logger.debug('创建按钮')
        scan_cache = QPushButton(get_lang('38'))
        ok = QPushButton(get_lang('1f'))
        clean_cache = QPushButton(get_lang('39'))
        set_style(clean_cache, 'selected')
        
        # 布局4
        logger.debug('加载布局-4')        
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch(1)
        bottom_layout.addWidget(scan_cache)
        bottom_layout.addWidget(clean_cache)
        bottom_layout.addWidget(ok)
        
        layout.addLayout(bottom_layout, line + 1, 2)

        # 绑定事件
        self.all_checkbox.stateChanged.connect(self.on_check)
        scan_cache.clicked.connect(self.on_scan_cache)
        clean_cache.clicked.connect(self.on_clean_cache)
        ok.clicked.connect(self.close)
        
        for checkbox in self.checkbox_list:
            checkbox.stateChanged.connect(self.update_all_check_status)
            
        # 设置布局
        logger.debug('设置布局')
            
        self.setLayout(layout)
        
        logger.info('清理缓存窗口初始化完成')
        
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
        logger.info('扫描缓存')
        cache_size = [0 if i is None else i for i in self.calc_cache_size(True)]
        for text, cache, checkbox in zip(self.cache_size_list, cache_size, self.checkbox_list):
            if cache != 0:
                text.setText(self.format_size(cache))
            elif checkbox.isChecked():
                    text.setText(self.format_size(0))
        self.all_size_text.setText(self.format_size(sum(cache_size)))
    
    def on_clean_cache(self):
        '''清理缓存'''
        logger.info('清理缓存')
        cache = []
        select_cache_size = self.calc_cache_size()
        # 获取选择的缓存文件
        for checkbox, text in zip(self.checkbox_list, self.cache_path_list):
            if checkbox.isChecked() and text.text():
                cache.append(text.text())
        # 清理缓存文件
        for i in cache:
            try:
                if os.path.isfile('cache/' + i):
                    os.remove('cache/' + i)
                elif os.path.isdir('cache/' + i):
                    shutil.rmtree('cache/' + i, ignore_errors=True)
            except Exception as e:
                MessageBox.critical(self, get_lang('14'), get_lang('3a').format(e))
                logger.error(f'无法删除文件或文件夹:{e}')

        dir_list = []
        # 添加文件夹开始的字符
        for i in self.cache_dir_list:
            dir_list.append('cache\\' + i)
        # 扫描其他文件
        additional_cache_list = []
        for root, dirs, files in os.walk(cache_path):
            for file in files:
                if root in dir_list:
                    continue
                if file in self.cache_file_list:
                    continue
                additional_cache_list.append(file)
            for dir in dirs:
                if dir in self.cache_dir_list:
                    continue
                additional_cache_list.append(dir)

        # 删除其他文件
        for i in additional_cache_list:
            try:
                if os.path.isfile('cache/' + i):
                    os.remove('cache/' + i)
                elif os.path.isdir('cache/' + i):
                    shutil.rmtree('cache/' + i, ignore_errors=True)
            except Exception as e:
                MessageBox.critical(self, get_lang('14'), get_lang('3a').format(e))
                logger.error(f'无法删除文件或文件夹:{e}')
        # 弹出提示窗口
        MessageBox.information(self, get_lang('16'), get_lang('3b').format(self.format_size(select_cache_size)))
    
    def calc_cache_size(self, output_every_file:bool=False) -> int:
        '''扫描缓存'''
        logger.info('计算缓存大小')
        cache = []
        every_cache_size = []
        cache_size = 0
        # 获取选择的缓存文件
        for checkbox, text in zip(self.checkbox_list, self.cache_path_list):
            if checkbox.isChecked() and text.text():
                cache.append(text.text())
            else:
                cache.append(None)
        
        # 扫描缓存文件大小
        for i in cache:
            if i is not None:
                one_cache_size = self.scan_file_size('cache/' + i, False)
                cache_size += one_cache_size
                every_cache_size.append(one_cache_size)
            else:
                every_cache_size.append(None)
        
        extra_cache_size = 0
        if self.checkbox_list[-1].isChecked():
            dir_list = []
            # 添加文件夹开始的字符
            for i in self.cache_dir_list:
                dir_list.append('cache\\' + i)

            # 扫描其他文件大小
            additional_cache_list = []
            for root, dirs, files in os.walk(cache_path):
                for file in files:
                    if root in dir_list:
                        continue
                    if file in self.cache_file_list:
                        continue
                    additional_cache_list.append(file)
                for dir in dirs:
                    if dir in self.cache_dir_list:
                        continue
                    additional_cache_list.append(dir)
            # 计算其他文件大小
            for i in additional_cache_list:
                one_cache_size = self.scan_file_size('cache/' + i, False)
                extra_cache_size += one_cache_size
            every_cache_size[-1] = extra_cache_size
        
        return every_cache_size if output_every_file else cache_size + extra_cache_size

    def scan_file_size(self, file_or_dir_path: str, format_size: bool = True) -> str | int:
        '''扫描文件大小'''
        if os.path.isfile(file_or_dir_path):
            # 是文件的情况
            size = os.path.getsize(file_or_dir_path)
            return self.format_size(size) if format_size else size
        elif os.path.isdir(file_or_dir_path):
            # 是目录的情况
            size = 0
            for root, dirs, files in os.walk(file_or_dir_path):
                for file in files:
                    size += os.path.getsize(os.path.join(root, file))
            return self.format_size(size) if format_size else size
        else:
            # 其他情况返回值
            return '0.00B' if format_size else 0
            
    def format_size(self, size: int) -> str:
        '''格式化文件大小'''
        size_list = ['B', 'KB', 'MB']
        for i in size_list:
            if size < 1024:
                return f'{size:.2f} {i}'
            size /= 1024
        return get_lang('3c')

    def on_check(self, state):
        '''全选按钮点击事件'''
        if state == 0: # 未选中
            if not self.locked_checkbox: # 非手动操作
                for checkbox in self.checkbox_list:
                    checkbox.setChecked(False)
        elif state == 1: # 部分选中
            if not self.locked_checkbox: # 非手动操作
                self.all_checkbox.setCheckState(Qt.Checked)
        elif state == 2: # 全选
            if not self.locked_checkbox: # 非手动操作
                for checkbox in self.checkbox_list:
                    checkbox.setChecked(True)

class UpdateWindow(QDialog):
    def __init__(self):
        # 初始化
        logger.info('初始化更新窗口')
        super().__init__()
        self.setWindowTitle(get_lang('29'))
        self.setGeometry(100, 100, 300, 110)
        self.setFixedSize(self.width(), self.height())
        self.setWindowIcon(icon)
        
        self.init_ui()
        
        new_color_bar(self)

    def init_ui(self):
        # 创建面板
        logger.debug('创建面板')
        layout = QVBoxLayout()
        
        # 面板控件
        logger.debug('创建面板控件')
        title = QLabel(get_lang('24'))
        version = QLabel(get_lang('25').format(__version__, result[1]))

        set_style(title, 'big_text_16')

        # 按钮
        update = QPushButton(get_lang('26')) # 更新按钮
        set_style(update, 'selected')
        update_log = QPushButton(get_lang('27')) # 查看更新日志按钮
        cancel = QPushButton(get_lang('1f')) # 取消按钮
        
        bottom_layout = QHBoxLayout()
        # 绑定事件
        logger.debug('绑定事件')
        update.clicked.connect(self.on_update)
        update_log.clicked.connect(self.on_open_update_log)
        cancel.clicked.connect(self.close)
        
        # 布局
        logger.debug('布局')
        layout.addWidget(title)
        layout.addWidget(version)

        bottom_layout.addStretch()
        bottom_layout.addWidget(update)
        bottom_layout.addWidget(update_log)
        bottom_layout.addWidget(cancel)

        layout.addLayout(bottom_layout)
        
        self.setLayout(layout)

    def on_update(self):
        '''更新'''
        open_url('https://github.com/xystudio889/pyClickMouse/releases')

    def on_open_update_log(self):
        # 打开更新日志
        logger.debug('打开更新日志')

        update_log = cache_path / 'update_log.md' # 更新日志路径

        try:
            os.startfile(update_log) # 打开更新日志
            MessageBox.information(self, get_lang('16'), get_lang('28')) 
        except:
            MessageBox.critical(self, get_lang('14'), get_lang('58'))

class HotkeyHelpWindow(QDialog):
    def __init__(self):
        logger.info('初始化热键帮助窗口')
        super().__init__()
        self.setWindowTitle(filter_hotkey(get_lang('5e')))
        self.setWindowIcon(icon)
        
        self.init_ui()
        
        new_color_bar(self)
    
    def init_ui(self):
        # 创建面板
        logger.debug('创建面板')
        layout = QVBoxLayout()
        
        # 面板控件
        logger.debug('创建面板控件')
        title = QLabel(filter_hotkey(get_lang('5e')))
        set_style(title, 'big_text_16')

        layout.addWidget(title)
        
        # 热键说明
        with open(get_resource_path('vars', 'hotkey.json'), 'r', encoding='utf-8') as f:
            hotkeys = json.load(f)
        
        # 显示热键说明
        for k, v in hotkeys.items():
            if v.startswith(' '):
                v = get_lang(v[1:])
            hotkey_label = QLabel(f'{k}:{v}')
            layout.addWidget(hotkey_label)
            
        bottom_layout = QHBoxLayout()
        ok_button = QPushButton(get_lang('1e'))
        set_style(ok_button, 'selected')
        ok_button.clicked.connect(self.close)
        
        # 布局
        logger.debug('布局')
        bottom_layout.addStretch(1)
        bottom_layout.addWidget(ok_button)
        
        layout.addLayout(bottom_layout)
        
        self.setLayout(layout)

class FastSetClickWindow(QMainWindow):
    def __init__(self):
        logger.info('初始化')

        super().__init__()
        self.setWindowTitle(get_lang('75'))
        self.setWindowIcon(icon)
        self.setGeometry(100, 100, 475, 125)
        self.setWindowFlags(
            Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint
        ) # 设置窗口属性
        
        self.setFixedSize(self.width(), self.height()) # 固定窗口大小

        logger.debug('初始化状态控制变量')
        self.total_run_time = 0  # 总运行时间
        
        logger.debug('初始化ui')
        self.init_ui()
        
        new_color_bar(self)
    
    def init_ui(self):
        # 创建主控件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_layout = QVBoxLayout(central_widget)
        
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
        self.total_time_label = QLabel(f'{get_lang('2c')}: ')
        self.total_time_label.setAlignment(Qt.AlignHCenter)
        set_style(self.total_time_label, 'big_text_14')
        
        # 创建布局
        logger.debug('创建按钮布局')
    
        central_layout.addLayout(unit_layout)
        central_layout.addWidget(self.total_time_label)
        self.setLayout(central_layout)
        
        # 按钮信号连接
        logger.debug('信号连接')

        # 双向同步
        # 主窗口同步
        main_window.input_delay.textChanged.connect(lambda: self.sync_input(QLineEdit.text, QLineEdit.setText, main_window.input_delay, self.input_delay))
        main_window.input_times.textChanged.connect(lambda: self.sync_input(QLineEdit.text, QLineEdit.setText, main_window.input_times, self.input_times))
        main_window.delay_combo.currentIndexChanged.connect(lambda: self.sync_input(QComboBox.currentIndex, QComboBox.setCurrentIndex, main_window.delay_combo, self.delay_combo))
        main_window.times_combo.currentIndexChanged.connect(lambda: self.sync_input(QComboBox.currentIndex, QComboBox.setCurrentIndex, main_window.times_combo, self.times_combo))
        main_window.total_time_label.textChanged.connect(lambda: self.sync_input(QLabel.text, QLabel.setText, main_window.total_time_label, self.total_time_label))
        
        # 本窗口同步
        self.input_delay.textChanged.connect(lambda: self.sync_input(QLineEdit.text, QLineEdit.setText, self.input_delay, main_window.input_delay))
        self.input_times.textChanged.connect(lambda: self.sync_input(QLineEdit.text, QLineEdit.setText, self.input_times, main_window.input_times))
        self.delay_combo.currentIndexChanged.connect(lambda: self.sync_input(QComboBox.currentIndex, QComboBox.setCurrentIndex, self.delay_combo, main_window.delay_combo))
        self.times_combo.currentIndexChanged.connect(lambda: self.sync_input(QComboBox.currentIndex, QComboBox.setCurrentIndex, self.times_combo, main_window.times_combo))
        
        logger.info('初始化完成')
        
    def sync_input(self, get_handle, set_handle, source, dest):
        '''同步输入框'''
        set_handle(dest, get_handle(source))

class ClickAttrWindow(QDialog):
    def __init__(self):
        logger.info('初始化连点器属性窗口')
        super().__init__()
        self.setWindowTitle(get_lang('8c'))
        self.setWindowIcon(icon)

        # 定义变量
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_attr)
        self.timer.start(1000)
        
        self.init_ui()
        
        new_color_bar(self)

    def init_ui(self):
        # 创建主布局
        central_layout = QVBoxLayout()
        
        # 内容
        self.left_clicked = QLabel(f'{get_lang('69')}:')
        self.right_clicked = QLabel(f'{get_lang('6a')}:')
        self.click_delay = QLabel(f'{get_lang('78')}:')
        self.click_times = QLabel(f'{get_lang('5c')}:')
        self.paused = QLabel(f'{get_lang('0f')}:')
        self.stopped = QLabel(f'{get_lang('0e')}:')
        self.total_run_time = QLabel(f'{get_lang('2c')}:')
        
        # 底边栏
        bottom_layout = QHBoxLayout()
        ok_button = QPushButton(get_lang('1e'))
        set_style(ok_button, 'selected')
        ok_button.clicked.connect(self.close)
        
        # 布局
        bottom_layout.addStretch(1)
        bottom_layout.addWidget(ok_button)

        central_layout.addWidget(self.left_clicked)
        central_layout.addWidget(self.right_clicked)
        central_layout.addWidget(self.click_delay)
        central_layout.addWidget(self.click_times)
        central_layout.addWidget(self.paused)
        central_layout.addWidget(self.stopped)
        central_layout.addWidget(self.total_run_time)
        central_layout.addLayout(bottom_layout)
        
        self.setLayout(central_layout)
        
    def update_attr(self):
        '''更新属性'''
        self.left_clicked.setText(f'{get_lang('69')}: {get_lang('7b') if clicker.left_clicked else get_lang('7c')}')
        self.right_clicked.setText(f'{get_lang('6a')}: {get_lang('7b') if clicker.right_clicked else get_lang('7c')}')
        self.click_delay.setText(f'{get_lang('78')}: {delay_num}{get_lang('ms', source=unit_lang)}')
        self.click_times.setText(f'{get_lang('5c')}: {get_lang('2b') if is_inf else time_num}')
        self.paused.setText(f'{get_lang('0f')}: {get_lang('79') if clicker.paused else get_lang('7a')}')
        self.stopped.setText(f'{get_lang('0e')}: {get_lang('79') if not clicker.running else get_lang('7a')}')
        try:
            if is_inf:
                self.total_run_time.setText(f'{get_lang('2c')}: {get_lang('2b')}')
            else:
                self.total_run_time.setText(f'{get_lang('2c')}: {main_window.total_run_time[0]:.2f}{main_window.total_run_time[1]}')
        except TypeError:
            value = get_unit_value(main_window.total_run_time)
            self.total_run_time.setText(f'{get_lang('2c')}: {value[0]:.2f}{value[1]}')

class SettingWindow(SelectUI):
    click_setting_changed = Signal()
    window_restarted = Signal()

    def __init__(self, parent=None):
        super().__init__()

        self.setGeometry(300, 300, 600, 400)  # 增加窗口大小以容纳更多内容
        self.setWindowTitle(filter_hotkey(get_lang('04')))
        self.setParent(parent)
        self.setWindowIcon(icon)
        self.setWindowFlags(
            Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint
        ) # 设置窗口属性
        
        # 变量
        self.page_choice_buttons = [get_lang('42'), get_lang('a6'), get_lang('43'), get_lang('44')]
        self.last_page = None
        self.now_page = None
        
        self.init_ui()
        
        new_color_bar(self)
        
        # 连接信号
        clicker.started.connect(self.on_clicker_started)

    def create_setting_page(self, title):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # 标题标签
        title_label = QLabel(title)
        set_style(title_label, 'big_text_24')
        layout.addWidget(title_label)
        
        # 内容标签
        content_label = QLabel(get_lang('7d'))
        set_style(content_label, 'dest')
        layout.addWidget(content_label)
        
        def set_content_label(text):
            content_label.setText(text)
            
        def create_horizontal_line():
            line = QFrame()
            line.setFrameShape(QFrame.Shape.HLine)  # 水平线
            line.setFrameShadow(QFrame.Shadow.Sunken)  # 凹陷效果
            return line
        
        restart_layout = QHBoxLayout()
        self.restart_button = QPushButton(get_lang('7e'))

        set_style(self.restart_button, 'selected')
        self.restart_button.clicked.connect(self.restart)

        if settings_need_restart:
            self.restart_button.show()
        else:
            self.restart_button.hide()
        
        self.page_general = self.page_choice_buttons[0] # 默认设置
        self.page_style = self.page_choice_buttons[1] # 样式设置
        self.page_click = self.page_choice_buttons[2] # 连点器设置
        self.page_update = self.page_choice_buttons[3] # 更新设置
        
        # 主程序
        self.app = get_application_instance()
        
        # 添加一些示例设置控件
        match title:
            case self.page_general:
                set_content_label(get_lang('7f'))
                # 选择语言
                choice_text = QLabel(get_lang('45')) # 选择语言提示
                
                lang_choice_layout = QHBoxLayout() # 语言选择布局
                self.lang_choice = QComboBox()
                self.lang_choice.addItems([i['lang_name'] for i in langs])
                self.lang_choice.setCurrentIndex(settings.get('select_lang', 0))
                
                # 布局
                lang_choice_layout.addWidget(choice_text)
                lang_choice_layout.addWidget(self.lang_choice)
                lang_choice_layout.addStretch(1)   
                
                # 显示托盘图标
                tray_layout = QHBoxLayout() # 窗口风格布局
                tray = UCheckBox(get_lang('80'))
                tray.setChecked(settings.get('show_tray_icon', True))
    
                tray_layout.addWidget(tray)
                tray_layout.addStretch(1)

                # 布局
                layout.addLayout(lang_choice_layout)
                layout.addLayout(tray_layout)
                
                # 绑定事件
                self.lang_choice.currentIndexChanged.connect(lambda: self.on_need_restart_setting_changed(self.lang_choice.currentIndex, 'select_lang'))
                tray.stateChanged.connect(lambda: self.on_setting_changed(tray.isChecked,'show_tray_icon'))
                tray.stateChanged.connect(lambda: self.app.setQuitOnLastWindowClosed(not tray.isChecked()))  # 关闭窗口时不退出应用
            case self.page_click:
                set_content_label(get_lang('84'))
                # 选择默认连点器延迟
                unit_layout = UnitInputLayout() # 窗口风格布局
                self.default_delay = QLineEdit()
                self.default_delay.setText(str(settings.get('click_delay', '')))
                self.delay_combo = QComboBox()
                self.delay_combo.addItems([get_lang('ms', source=unit_lang), get_lang('s', source=unit_lang)])
                self.delay_combo.setCurrentIndex(settings.get('delay_unit', 0))
                unit_layout.addUnitRow(get_lang('46'), self.default_delay, self.delay_combo)
                
                # 连点出错时使用默认值
                use_default_delay = UCheckBox(get_lang('47'))
                use_default_delay.setChecked(settings.get('failed_use_default', False))
                if not self.default_delay.text():
                    use_default_delay.setEnabled(False)
                    
                line1 = create_horizontal_line()

                # 布局
                unit_layout.newRow()
                unit_layout.addWidget(use_default_delay)
                unit_layout.newRow()
                unit_layout.addWidget(line1)
                
                self.default_time = QLineEdit()
                self.default_time.setText(str(settings.get('click_times', '')))
                self.times_combo = QComboBox()
                self.times_combo.addItems([get_lang('66'), get_lang('2a'), get_lang('2b')])
                self.times_combo.setCurrentIndex(settings.get('times_unit', 0))
                unit_layout.addUnitRow(get_lang('85'), self.default_time, self.times_combo)
                
                # 连点出错时使用默认值
                use_default_time = UCheckBox(get_lang('86'))
                use_default_time.setChecked(settings.get('times_failed_use_default', False))
                if not self.default_time.text():
                    use_default_time.setEnabled(False)
                unit_layout.newRow()
                unit_layout.addWidget(use_default_time)
                
                line2 = create_horizontal_line()
                
                self.total_time_label = QLabel(f'{get_lang('2c')}: {get_lang('61')}')
                set_style(self.total_time_label, 'big_text_14')
                self.on_input_change()
                
                # 布局
                layout.addLayout(unit_layout)
                layout.addWidget(line2)
                layout.addWidget(self.total_time_label)
                
                # 连接信号
                self.default_delay.textChanged.connect(lambda: self.on_default_input_changed(self.default_delay, 'click_delay', use_default_delay))
                self.default_delay.textChanged.connect(self.on_input_change)
                use_default_delay.stateChanged.connect(lambda: self.on_setting_changed(use_default_delay.isChecked, 'failed_use_default'))
                self.default_time.textChanged.connect(lambda: self.on_default_input_changed(self.default_time, 'click_times', use_default_time))
                self.default_time.textChanged.connect(self.on_input_change)
                use_default_time.stateChanged.connect(lambda: self.on_setting_changed(use_default_time.isChecked, 'times_failed_use_default'))
                self.delay_combo.currentIndexChanged.connect(lambda: self.on_setting_changed(self.delay_combo.currentIndex, 'delay_unit'))
                self.delay_combo.currentIndexChanged.connect(self.on_input_change)
                self.times_combo.currentIndexChanged.connect(lambda: self.on_setting_changed(self.times_combo.currentIndex, 'times_unit'))
                self.times_combo.currentIndexChanged.connect(self.on_input_change)
            case self.page_update:
                set_content_label(get_lang('87'))
                # 选择更新检查提示
                check_update_layout = QHBoxLayout() # 窗口风格布局
                
                check_update_notify_text = QLabel(get_lang('48')) # 选择更新检查提示
                check_update_notify = QComboBox()
                check_update_notify.addItems([get_lang('49'), get_lang('4a')])
                check_update_notify.setCurrentIndex(settings.get('check_update_notify', 0))
                
                # 布局
                check_update_layout.addWidget(check_update_notify_text)
                check_update_layout.addWidget(check_update_notify)
                check_update_layout.addStretch(1)
                
                # 布局
                layout.addLayout(check_update_layout)
                
                # 连接信号
                check_update_notify.currentIndexChanged.connect(lambda: self.on_setting_changed(check_update_notify.currentIndex, 'update_notify'))
            case self.page_style:
                set_content_label(get_lang('a7'))
                # 选择窗口风格
                style_text = QLabel(get_lang('81')) # 选择窗口风格提示
                
                style_layout = QHBoxLayout() # 窗口风格布局
                style_choice = QComboBox()
                
                items = list(style_indexes[settings.get('select_lang', 0)]['lang_package'].values())
    
                style_choice.addItems([get_lang('82')] + items)
                style_choice.setCurrentIndex(settings.get('select_style', 0))
                
                # 布局
                style_layout.addWidget(style_text)
                style_layout.addWidget(style_choice)
                style_layout.addStretch(1)
                
                style_use_windows_layout = QHBoxLayout() # 颜色使用windows按钮布局
                style_choice_use_windows = UCheckBox(get_lang('a8'))
                tip_label = QLabel(get_lang('b4'))
                set_style(tip_label, 'dest_small')
                
                style_choice_use_windows.setChecked(settings.get('use_windows_color', True))
                
                # 布局
                style_use_windows_layout.addWidget(style_choice_use_windows)
                style_use_windows_layout.addWidget(tip_label)
                style_use_windows_layout.addStretch(1)
                
                # 布局
                layout.addLayout(style_layout)
                layout.addLayout(style_use_windows_layout)
                
                # 连接信号
                style_choice.currentIndexChanged.connect(lambda: self.on_setting_changed(style_choice.currentIndex, 'select_style'))
                style_choice_use_windows.stateChanged.connect(lambda: self.on_setting_changed(style_choice_use_windows.isChecked, 'use_windows_color'))
        
        restart_layout.addStretch()
        restart_layout.addWidget(self.restart_button)
        layout.addLayout(restart_layout)

        # 添加弹簧，让内容靠上显示
        layout.addStretch()
        
        return page
        
    def on_need_restart_setting_changed(self, handle , key: str, restart_place: list[str] = ['a9'], *args):
        '''托盘图标选择事件'''
        global settings_need_restart
        
        self.on_setting_changed(handle, key, *args)
        settings_need_restart = True
        
        lang = self.lang_choice.currentIndex()
        
        restart_place = list(map(lambda x: get_lang(x, lang_id=lang), restart_place))
        
        need_restart = MessageBox.warning(self, get_lang('15', lang_id=lang), f'{get_lang("89", lang_id=lang)}: {", ".join(restart_place)}', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if need_restart == QMessageBox.Yes:
            self.restart()
        else:
            self.restart_window()
            
    def restart_window(self):
        self.window_restarted.emit()
        self.close()
        
    def on_setting_changed(self, handle, key, *args):
        '''更新检查提示选择事件'''
        settings[key] = handle(*args)
        save_settings(settings)
        
    def on_default_input_changed(self, default: QLineEdit, key: str, use_default: UCheckBox):
        '''默认延迟输入框内容变化事件'''
        if not default.text():
            use_default.setEnabled(False)
        else:
            use_default.setEnabled(True)
        self.on_setting_changed(default.text, key)
        
    def check_default_var(self, value):
        '''检查默认延迟是否有效'''
        try:
            var = int(settings.get(f'click_{value}', ''))
            if not var:
                return True
            if var < 1:
                raise ValueError
            return True
        except ValueError:
            return False
        
    def on_delay_error(self, error_text=get_lang('14')):
        '''输入延迟错误'''
        self.total_time_label.setText(f'{get_lang('2c')}: {error_text}')
    
    def on_input_change(self, var=None):
        '''输入延迟改变'''
        # 判断参数有效性
        input_delay = self.default_delay.text().strip()
        input_times = self.default_time.text().strip()
        is_inf = False
        delay = 0
        self.click_setting_changed.emit()
        
        self.default_time.setEnabled(not self.times_combo.currentIndex() == latest_index)

        if self.times_combo.currentIndex() == latest_index or input_times == '0':
            is_inf = True
        
        try:
            delay = math.ceil(float(input_delay))
            if delay < 1:
                raise ValueError
        except ValueError:
            if not settings.get('click_delay', '') == '':
                if input_delay == '':
                    if self.check_default_var('delay'):
                        delay = int(settings.get('click_delay', ''))
                    else:
                        self.on_delay_error()
                        return
                elif settings.get('failed_use_default', False):
                    if self.check_default_var('delay'):
                        delay = int(settings.get('click_delay', ''))
                    else:
                        self.on_delay_error()
                        return
                else:
                    self.on_delay_error()
                    return
        except Exception:
            self.on_delay_error()
            return

        if not is_inf:
            try:
                times = math.ceil(float(input_times))
                if times < 1:
                    raise ValueError
            except ValueError:
                if settings.get('click_times', '') == '' and settings.get('click_delay', '') == '':
                    self.on_delay_error(get_lang('61'))
                    return
                else:
                    if input_times == '':
                        if self.check_default_var('times'):
                            times = int(settings.get('click_times', ''))
                        else:
                            self.on_delay_error()
                            return
                    elif settings.get('times_failed_use_default', False):
                        if self.check_default_var('times'):
                            times = int(settings.get('click_times', ''))
                        else:
                            self.on_delay_error()
                            return
                    else:
                        self.on_delay_error()
                        return
            except Exception:
                self.on_delay_error()
                return
        
        if settings.get('click_delay', '') != '' and input_delay == '':
            match settings.get('delay_unit', 0):
                case 0:
                    delay_num = delay
                case 1:
                    delay_num = delay * 1000
        else:
            match self.delay_combo.currentIndex():
                case 0:
                    delay_num = delay
                case 1:
                    delay_num = delay * 1000
                case 2:
                    delay_num = delay * 60 * 1000
                case _:
                    delay_num = delay

        if is_inf:
            self.total_time_label.setText(f'{get_lang('2c')}: {get_lang('2b')}')
        else:
            if settings.get('click_times', '') != '' and input_times == '':
                match settings.get('times_unit', 0):
                    case 0:
                        time_num = times
                    case 1:
                        time_num = times * 10000
            else:
                match self.times_combo.currentIndex():
                    case 0:
                        time_num = times
                    case 1:
                        time_num = times * 10000
                    case 2:
                        time_num = times * 100_0000
                    case _:
                        time_num = times
                        
            if (delay_num == 0 and time_num != 0) or (delay_num != 0 and time_num == 0):
                self.on_delay_error()
                return
                                        
            self.total_run_time = delay_num * time_num
            self.total_time_label.setText(f'{get_lang('2c')}: {self.total_run_time}{get_lang('ms', source=unit_lang)}')
            self.total_run_time = get_unit_value(self.total_run_time)
            self.total_time_label.setText(f'{get_lang('2c')}: {self.total_run_time[0]:.2f}{self.total_run_time[1]}')
    
    def on_page_button_clicked(self, index):
        '''处理页面按钮点击事件'''
        # 切换到对应的页面
        if index == self.page_choice_buttons.index(get_lang('43')) and clicker.running:
            MessageBox.critical(self, get_lang('14'), get_lang('aa'))
            return
        self.stacked_widget.setCurrentIndex(index)
        self.last_page = self.now_page
        self.now_page = self.stacked_widget.currentIndex()

        # 更新按钮样式
        for i, button in enumerate(self.buttons):
            if i == index:
                set_style(button, 'selected')
            else:
                set_style(button, '')
    
    def restart(self):
        run_software('main.py', 'main.exe')
        sys.exit(0)
    
    def init_right_pages(self):
        super().init_right_pages()
        set_style(self.buttons[0], 'selected')
        
    def on_clicker_started(self):
        '''连点器启动事件'''
        if self.now_page == self.page_choice_buttons.index(get_lang('43')):
            self.on_page_button_clicked(self.last_page)
            MessageBox.critical(self, get_lang('14'), get_lang('aa'))
            return
        
class SetImportExtensionModeWindow(QDialog):
    def __init__(self):
        super().__init__()
        logger.info('初始化管理扩展窗口')
        self.setWindowTitle(filter_hotkey(get_lang('92')))
        self.setGeometry(100, 100, 200, 125)
        self.setWindowIcon(icon)
        self.setFixedSize(self.width(), self.height())
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 选择扩展模式
        # 提示
        mode_label = QLabel(get_lang('ab'))
        mode_label.setAlignment(Qt.AlignCenter)
        set_style(mode_label, 'big_text_16')

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
        mode_button.clicked.connect(self.on_mode_button_clicked)
        
    def on_mode_button_clicked(self):
        self.close()
        main_window.show_import_extension(self.mode_combo.currentIndex())

class TrayApp:
    def __init__(self):
        self.app = get_application_instance()

        show_tray_icon = settings.get('show_tray_icon', True)
        if show_tray_icon:
            self.app.setQuitOnLastWindowClosed(False)  # 关闭窗口时不退出应用
        
        # 激活主窗口
        main_window.show()
        
        # 加载警告
        if not has_packages:
            MessageBox.warning(None, get_lang('15'), get_lang('ae'))
        
        # 创建设置延迟窗口
        self.set_dalay_window = FastSetClickWindow()
        self.click_attr_window = ClickAttrWindow()
        
        # 创建热键监听器
        self.hotkey_listener = HotkeyListener()
        self.hotkey_listener.pressed_key.connect(self.on_key_pressed)
        self.hotkey_listener.combination_pressed.connect(self.on_combination_pressed)
        
        # 创建系统托盘图标
        self.setup_tray_icon()
        
        # 启动热键监听
        self.start_hotkey_listener()
        
        clicker.pause.connect(main_window.on_pause)
        clicker.click_changed.connect(main_window.on_click_changed)
        clicker.stopped.connect(main_window.on_stop)
        clicker.click_conuter.connect(main_window.on_click_counter)
        clicker.started.connect(self.on_start)
        clicker.started.connect(main_window.on_start)

    def setup_tray_icon(self):
        '''设置系统托盘图标'''
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
        tray_menu = QMenu()
        
        # 添加'打开应用'菜单项
        show_action = QAction(get_lang('68'), self.app)
        show_action.triggered.connect(self.show_main_window)
        tray_menu.addAction(show_action)
        
        # 添加分隔线
        tray_menu.addSeparator()
        
        # 控制类按钮
        left_click_action = QAction(get_lang('69'), self.app)
        right_click_action = QAction(get_lang('6a'), self.app)
        pause_action = QAction(get_lang('6b'), self.app)
        stop_action = QAction(get_lang('6c'), self.app)
        set_delay_action = QAction(get_lang('6d'), self.app)
        
        set_delay_action.triggered.connect(lambda: pyautogui.press('f1'))
        left_click_action.triggered.connect(lambda: pyautogui.press('f2'))
        right_click_action.triggered.connect(lambda: pyautogui.press('f3'))
        pause_action.triggered.connect(lambda: pyautogui.press('f4'))
        stop_action.triggered.connect(lambda: pyautogui.press('f6'))
        
        tray_menu.addAction(left_click_action)
        tray_menu.addAction(right_click_action)
        tray_menu.addAction(pause_action)
        tray_menu.addAction(stop_action)
        tray_menu.addAction(set_delay_action)
        
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
        # 在后台线程中启动热键监听
        hotkey_thread = threading.Thread(target=self.hotkey_listener.start_listening)
        hotkey_thread.daemon = True  # 设置为守护线程，主程序退出时自动结束
        hotkey_thread.start()
    
    def on_tray_icon_activated(self, reason):
        '''处理托盘图标激活事件'''
        if reason == QSystemTrayIcon.ActivationReason.Trigger:  # 左键点击
            self.show_main_window()
            self.refresh()
            
    def check_delay(self, input_delay):
        try:
            math.ceil(float(input_delay))
        except Exception as e:
            MessageBox.critical(main_window, get_lang('13'), f'{get_lang('ae')} {str(e)}')
            logger.critical(f'发生错误:{e}')
            return False
        return True
    
    def on_key_pressed(self, key):
        '''处理按键事件'''
        if key == keyboard.Key.f2:
            clicker.default_stop_1 = True
            # 判断参数有效性
            if not main_window.left_click_button.isEnabled():
                MessageBox.critical(None, get_lang('14'), get_lang('1a'))
                return

            if not (self.check_delay(delay_num) or self.check_delay(time_num)):
                return

            self.tray_icon.showMessage(get_lang('6e'), get_lang('6f'), QSystemTrayIcon.MessageIcon.Information, 1000)
            clicker.mouse_left(delay_num, time_num)
        elif key == keyboard.Key.f3:
            clicker.default_stop_1 = True
            # 判断参数有效性
            if not main_window.right_click_button.isEnabled():
                MessageBox.critical(None, get_lang('14'), get_lang('1a'))
                return
            
            if not (self.check_delay(delay_num) or self.check_delay(time_num)):
                return

            self.tray_icon.showMessage(get_lang('6e'), get_lang('70'), QSystemTrayIcon.MessageIcon.Information, 1000)
            clicker.mouse_right(delay_num, time_num)
        elif key == keyboard.Key.f4:
            clicker.pause_click()
            if clicker.running:
                if clicker.paused:
                    self.tray_icon.showMessage(get_lang('6e'), get_lang('71'), QSystemTrayIcon.MessageIcon.Information, 1000)
                else:
                    self.tray_icon.showMessage(get_lang('6e'), get_lang('72'), QSystemTrayIcon.MessageIcon.Information, 1000)
            else:
                self.tray_icon.showMessage(get_lang('6e'), get_lang('74'), QSystemTrayIcon.MessageIcon.Warning, 1000)
        elif key == keyboard.Key.f6:
            if clicker.running:
                main_window.on_stop()
                self.tray_icon.showMessage(get_lang('6e'), get_lang('73'), QSystemTrayIcon.MessageIcon.Information, 1000)
            else:
                self.tray_icon.showMessage(get_lang('6e'), get_lang('74'), QSystemTrayIcon.MessageIcon.Warning, 1000)
    
    def show_main_window(self):
        '''显示主窗口'''
        main_window.show()
    
    def quit_application(self):
        '''退出应用程序'''
        # 停止热键监听
        self.hotkey_listener.stop_listening()
        self.app.quit()
    
    def run(self):
        '''运行应用程序'''
        sys.exit(self.app.exec())
        
    def refresh(self):
        refresh.run()
        
    def on_combination_pressed(self, combination):
        '''处理组合键事件'''
        temp_combination = combination.copy()
        
        for index, i in enumerate(temp_combination):
            temp_combination[index] = i.replace('Key.', '').replace('_l', '').replace('_r', '').replace('_gr', '')
        combination = temp_combination.copy()

        # print(combination)
        if all_in_list(combination, ['<70>', 'ctrl', 'alt']):
            # 处理Ctrl+Alt+F组合键
            if clicker.running:
                self.tray_icon.showMessage(get_lang('14'), get_lang('af'), QSystemTrayIcon.MessageIcon.Critical, 1000)
            else:
                if self.set_dalay_window.isVisible():
                    self.set_dalay_window.hide()
                else:
                    self.set_dalay_window.show()
                    self.refresh()
        elif all_in_list(combination, ['<77>', 'ctrl', 'alt']):
            # 处理Ctrl+Alt+M组合键
            if main_window.isVisible():
                main_window.hide()
            else:
                main_window.show()
                self.refresh()
        elif all_in_list(combination, ['<65>', 'ctrl', 'alt']):
            # 处理Ctrl+Alt+A组合键
            if self.click_attr_window.isVisible():
                self.click_attr_window.hide()
            else:
                self.click_attr_window.show()
                self.refresh()
        elif all_in_list(combination, ['<72>', 'ctrl', 'alt']):
            # 处理Ctrl+Alt+H组合键
            if hotkey_help_window.isVisible():
                hotkey_help_window.hide()
            else:
                hotkey_help_window.show()
                self.refresh()
    
    def on_start(self):
        '''连点器启动事件'''
        if self.set_dalay_window.isVisible():
            self.set_dalay_window.hide()
            self.tray_icon.showMessage(get_lang('14'), get_lang('af'), QSystemTrayIcon.MessageIcon.Critical, 1000)

if __name__ == '__main__':
    if not(is_process_running('init.exe')):
        if not((data_path / 'first_run').exists()):
            QMessageBox.information(None, get_lang('14'), '前往当前目录的init.exe文件运行初始化程序')
        else:
            try:
                packages = []
                with open('packages.json', 'r', encoding='utf-8') as f:
                    packages_name = json.load(f)
                for i in packages_name:
                    packages.append(import_package(i))
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
            
            has_packages = os.path.exists(get_resource_path('packages'))
            package_names, show_list, package_ids = get_packages()
            has_plural = get_has_plural()

            main_window = MainWindow()
            hotkey_help_window = HotkeyHelpWindow()
            
            app = TrayApp()
            app.run()
            
            logger.info('主程序退出')
    else:
        QMessageBox.critical(None, get_lang('14'), '请关闭初始化程序运行')
