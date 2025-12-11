# 加载库
import sys # 系统库
from PySide6.QtWidgets import * # 界面库
from PySide6.QtGui import * # 图标库
from PySide6.QtCore import * # 核心库

app = QApplication(sys.argv) # 创建应用程序实例

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
from uiStyles import SelectUI # 软件界面样式
from uiStyles.WidgetStyles import (styles, maps) # 界面组件样式
from uiStyles.WidgetStyles import indexes as style_indexes # 界面组件样式索引
from sharelibs import (get_style_sheet, replace_style_sheet, is_dark_mode, run_software) # 共享库
import zipfile # 压缩库
import parse_dev # 解析开发固件配置
import winreg # 注册表库
from pynput import keyboard # 热键功能库
from typing import Callable # 类型提示库

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
        QMessageBox.critical(None, f'{get_lang('12')}{e}', get_lang('14'))
        exit(1)
        
def get_style_sheet(style_name: str, mode) -> str:
    '''
    获取样式表
    '''
    if mode is None:
        mode = 'light' if is_dark_mode() else 'dark'
    try:
        logger.info(f'获取样式表: {style_name}')
        with open(get_resource_path('styles', mode, f'{style_name}.qss'), 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        logger.error(f'样式表{style_name}.qss不存在')
        raise FileNotFoundError(f'样式表{style_name}.qss不存在')
    
def replace_style_sheet(style_sheet: str, style_tag: str, old_style: str, new_style: str) -> str:
    '''
    替换样式表
    '''
    old_style_tag = f'{style_tag}: {old_style}'
    new_style_tag = f'{style_tag}: {new_style}'
    return style_sheet.replace(old_style_tag, new_style_tag)

def get_lang(lang_package_id, lang_id = None, source = None):
    source = langs if source is None else source
    lang_id = settings.get('select_lang', 0) if lang_id is None else lang_id
    for i in source:
        if i['lang_id'] == 0: # 设置默认语言包
            default_lang_text = i['lang_package']
        if i['lang_id'] == lang_id: # 设置目前语言包
            lang_text = i['lang_package']
    try:
        return lang_text.get(lang_package_id, default_lang_text[lang_package_id])
    except KeyError:
        logger.error(f'错误：出现一个不存在的语言包id:{lang_package_id}')
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

def replace_extension(filepath):
    '''将文件路径最后一段的.py替换为.exe'''
    base, ext = os.path.splitext(filepath)
    if ext == '.py':
        return base + '.exe'
    return filepath

def restart():
    '''执行应用程序重启'''
    python = sys.executable if os.path.exists(sys.executable) else replace_extension(__file__)
    os.execl(python, python, *sys.argv)
    
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
            f.write('更新内容获取失败')

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
    list_packages = [] # 包名列表
    lang_index = [] # 语言包索引
    package_path = [] # 包路径列表
    package_index = [] # 包索引
    show = []
    
    # # 加载包信息
    # for package in packages:
    #     list_packages.append(package.get('package_name', None))
    #     lang_index.append(package.get('package_name_lang_index', None))
    #     package_path.append(package.get('install_location', None))
    #     package_index.append(package.get('package_id', None))
    #     show.append(package.get('show_in_extension_list', True))
    return (list_packages, lang_index, package_path, package_index, show)

def extract_zip(file_path, extract_path):
    '''
    解压zip文件
    '''
    with zipfile.ZipFile(file_path, 'r') as f:
        f.extractall(extract_path)
        
def check_doc_exists():
    is_installed_docs = True
    is_installed_this_lang_docs = True

    if not(os.path.exists(get_resource_path('docs', 'en.chm'))):
        QMessageBox.warning(None, get_lang('16'), '软件目录下缺少默认文档文件，所以"文档"功能将被禁用\n修复方法：这可能是再编译版本，请找到源程序的docs目录，使用HTML Help Workshop等工具制作chm文档，并将其放入res\\docs目录下后再编译')
        is_installed_docs = False
        is_installed_this_lang_docs = False
    elif not(os.path.exists(get_resource_path('docs', f'{get_lang_system_name()}.chm'))):
        QMessageBox.warning(None, get_lang('16'), f'软件目录下缺少{get_lang_system_name()}语言的文档文件，所以"文档"功能将会显示英文文档\n修复方法：这可能是第三方语言包，需要重新对这个语言包制作html版本文档')
        is_installed_this_lang_docs = False

    return (is_installed_docs, is_installed_this_lang_docs)

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
        if i['is_official']:
            if i.get('lang_system_name', 'en-US') == system_lang:
                return i['lang_id']
    return 0

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
            raise ValueError
        if delay < 1:
            raise ValueError
        return True
    except ValueError:
        QMessageBox.critical(None, get_lang('14'), '请输入有效的正整数默认延迟')
        return False

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
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.paused = False
        self.click_thread = None
        self.right_clicked = False
        self.left_clicked = False
        
    def mouse_left(self, delay):
        logger.info('左键连点')
        self.mouse_click(button='left', input_delay=delay)

    def mouse_right(self, delay):
        # 停止当前运行的点击线程
        logger.info('右键连点')
        self.mouse_click(button='right', input_delay=delay)
        
    def set_default_clicked(self):
        self.left_clicked = False
        self.right_clicked = False
        self.click_changed.emit(self.left_clicked, self.right_clicked)
    
    def mouse_click(self, button: str, input_delay: str):
        '''鼠标连点'''
        logger.info('开始连点')
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
        
        self.click_changed.emit(self.left_clicked, self.right_clicked)

        # 运行状态控制
        self.running = True
        self.paused = False
        
        # 判断参数有效性
        try:
            delay = int(input_delay)
            if delay < 1:
                raise ValueError
        except ValueError:
            if settings.get('click_delay', '') == '':
                QMessageBox.critical(None, get_lang('14'), get_lang('1a'))
                logger.error('用户输入错误：请输入有效的正整数延迟')

                self.set_default_clicked()
                return
            else:
                if input_delay == '':
                    if check_default_delay():
                        delay = int(settings.get('click_delay', ''))
                    else:
                        self.set_default_clicked()
                        return
                elif settings.get('failed_use_default', False):
                    if check_default_delay():
                        delay = int(settings.get('click_delay', ''))
                    else:
                        self.set_default_clicked()
                        return
                else:
                    QMessageBox.critical(None, get_lang('14'), get_lang('1a'))
                    logger.error('用户输入错误：请输入有效的正整数延迟')

                    self.set_default_clicked()
                    return

        # 创建独立线程避免阻塞GUI
        def click_loop():
            self.pause.emit(False)
            while self.running:
                if not self.paused:
                    try:
                        pyautogui.click(button=button)
                        sleep(delay/1000)
                    except Exception as e:
                        QMessageBox.critical(None, get_lang('14'), f'{get_lang('1b')} {str(e)}')
                        logger.critical(f'发生错误:{e}')
    
                        self.set_default_clicked()
                        break
                else:
                    sleep(0.1)  # 暂停时降低CPU占用
        
        # 启动线程
        logger.info(f'启动连点线程')
        self.click_thread = threading.Thread(target=click_loop)
        self.click_thread.daemon = True
        self.click_thread.start()
                    
    def pause_click(self):
        logger.info('连点器暂停或重启')
        self.paused = not self.paused
        self.pause.emit(self.paused)

class ColorGetter(QObject):
    def __init__(self):
        super().__init__()
        
        # 记录当前主题，避免不必要的重绘
        self.style = settings.get('select_style', 0)
        self.current_theme = self.load_theme()

        # 初始化时应用一次主题
        self.apply_global_theme()

        # 使用定时器定期检测主题变化（例如每秒一次）
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_and_apply_theme)
        self.timer.start(1000)
    
    def load_theme(self):
        theme = None
        if self.style == 0:
            theme = QApplication.styleHints().colorScheme()
            if theme == Qt.ColorScheme.Dark:
                theme = 'dark'
            elif theme == Qt.ColorScheme.Light:
                theme = 'light'
        
        for k, v in maps.items():
            if v == settings.get('select_style', 0):
                theme = k
        return theme

    def check_and_apply_theme(self):
        '''检查主题是否变化，变化则重新应用'''
        self.style = settings.get('select_style', 0)
        
        new_theme = self.load_theme()
        if new_theme != self.current_theme:
            self.current_theme = new_theme
            self.apply_global_theme()

    def apply_global_theme(self):
        '''根据当前主题，为整个应用设置全局样式表'''
        global select_styles, default_style, big_title, selected_style, current_theme

        theme = self.current_theme
        app = get_application_instance()

        if theme is None:
            select_styles = styles['light']
            default_style = ''
            big_title = select_styles['big_text']
            selected_style = ''
            current_theme = 'light'
            app.setStyleSheet('')  # 全局应用
        else:
            select_styles = styles[self.current_theme]
            default_style = select_styles['main']
            big_title = select_styles['big_text']
            selected_style = select_styles['selected_button']
            current_theme = self.current_theme
            
            app.setStyleSheet(default_style)  # 全局应用

data_path = Path('data')
settings = load_settings()

clicker = Click()

current_theme = 'light'
select_styles = styles[current_theme]
default_style = select_styles['main']
big_title = select_styles['big_text']
selected_style = select_styles['selected_button']
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

icon = QIcon(str(get_resource_path('icons', 'clickmouse', 'icon.ico')))

logger.debug('定义语言包')
with open(get_resource_path('langs.json'), 'r', encoding='utf-8') as f:
    langs = json.load(f)
    
need_restart_list = [False, False, False]
logger.debug('定义资源完成')

logger.debug('加载ui')
class SelectLanguage(QMainWindow):
    def __init__(self):
        # 初始化
        logger.info('初始化')
        super().__init__()
        
        self.system_lang = parse_system_language_to_lang_id()

        self.setWindowIcon(icon)
        self.setGeometry(100, 100, 200, 100)
        self.setWindowTitle(get_lang('54', self.system_lang))
        self.setFixedSize(self.width(), self.height()) # 固定窗口大小
        
        self.init_ui()
    
    def init_ui(self):
        settings['select_lang'] = self.system_lang
        save_settings(settings)

        # 创建面板
        logger.debug('创建面板')
        widget = QWidget()
        self.setCentralWidget(widget)
        layout = QVBoxLayout(widget)

        # 面板控件
        logger.debug('创建面板控件')
        text = QLabel(get_lang('54', self.system_lang))
        choices = [i['lang_name'] for i in langs]

        nxt_btn = QPushButton(get_lang('55', self.system_lang))
        
        self.lang_choice = QComboBox()
        self.lang_choice.addItems(choices) # 语言选择下拉框
        
        self.lang_choice.setCurrentIndex(self.system_lang)
        
        self.lang_choice.currentIndexChanged.connect(self.on_choice_change)
        nxt_btn.clicked.connect(self.on_nxt_btn)
        
        # 布局
        logger.debug('布局')
        layout.addWidget(text)
        layout.addWidget(self.lang_choice)
        layout.addWidget(nxt_btn)
        
        self.setLayout(layout)

    def on_choice_change(self, event):
        settings['select_lang'] = self.lang_choice.currentIndex()
        save_settings(settings)
        
    def on_nxt_btn(self, event):
        with open(data_path / 'first_run', 'w'):
            pass
        self.close()

class MainWindow(QMainWindow):
    def __init__(self):
        logger.info('初始化')

        super().__init__()
        self.setWindowTitle('ClickMouse')
        self.setWindowIcon(icon)
        self.setGeometry(100, 100, 400, 275)
        self.setWindowFlags(
            Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint
        ) # 设置窗口属性
        app.styleHints().setColorScheme(Qt.ColorScheme.Unknown)
        
        self.setFixedSize(self.width(), self.height()) # 固定窗口大小

        logger.debug('初始化状态控制变量')
        self.show_update_in_start = False # 是否在启动时显示更新提示
        
        logger.debug('初始化ui')
        self.init_ui()
        
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
        title.setStyleSheet(replace_style_sheet(big_title, 'font-size', '16px', '20px'))
        title.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        
        # 按钮
        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)  # 设置按钮间距

        self.left_click_button = QPushButton(get_lang('0c'))
        self.left_click_button.setFixedSize(100, 60)
        
        self.right_click_button = QPushButton(get_lang('0d'))
        self.right_click_button.setFixedSize(100, 60)
        
        self.pause_button = QPushButton(get_lang('0f'))
        self.pause_button.setFixedSize(100, 40)
        self.pause_button.setEnabled(False)
        
        self.stop_button = QPushButton(get_lang('0e'))
        self.stop_button.setFixedSize(100, 40)
        self.stop_button.setEnabled(False)
        
        logger.debug('初始化布局')
        
        # 输入框
        form_layout = QFormLayout()
        
        self.input_delay = QLineEdit()
        self.input_delay.setFixedWidth(300)
        self.input_delay.setFixedHeight(30)
        
        
        form_layout.addRow(get_lang('11'), self.input_delay)
        
        # 创建布局
        logger.debug('创建按钮布局')
        grid_layout.addWidget(self.left_click_button, 0, 0)
        grid_layout.addWidget(self.right_click_button, 0, 2)
        grid_layout.addWidget(self.pause_button, 1, 1)
        grid_layout.addWidget(self.stop_button, 2, 1)
        
        central_layout.addWidget(title)
        central_layout.addLayout(grid_layout)
        central_layout.addLayout(form_layout)
        self.setLayout(central_layout)
        
        # 按钮信号连接
        logger.debug('信号连接')
        self.left_click_button.clicked.connect(lambda:clicker.mouse_left(self.input_delay.text()))
        self.right_click_button.clicked.connect(lambda:clicker.mouse_right(self.input_delay.text()))
        
        self.pause_button.clicked.connect(clicker.pause_click)
        self.stop_button.clicked.connect(self.on_stop)

        # 创建菜单栏
        logger.debug('创建菜单栏')
        self.create_menu_bar()
        
        logger.info('初始化完成')
    
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
        hotkey_help = help_menu.addAction('热键帮助(&H)')

        # doc = help_menu.addAction('文档(&D)')
        # if not(is_installed_doc):
        #     doc.setEnabled(False)
            
        # 绑定动作
        about_action.triggered.connect(self.show_about)
        update_log.triggered.connect(self.show_update_log)
        clean_cache_action.triggered.connect(self.show_clean_cache)
        update_check.triggered.connect(lambda: self.on_update(True))
        settings_action.triggered.connect(self.show_setting)
        hotkey_help.triggered.connect(self.show_hotkey_help)
        exit_action.triggered.connect(app.quit)
            
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
        hotkey_help_window = HotkeyHelpWindow()
        hotkey_help_window.exec()
    
    def show_setting(self):
        '''显示设置窗口'''
        setting_window = SettingWindow(self)
        setting_window.closed_use_reload.connect(self.show_setting)
        setting_window.show()

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
            result = (update_cache['should_update'], update_cache['latest_version'], update_cache['update_info']) # 使用缓存
        
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
                    QMessageBox.critical(self, get_lang('14'), f'{get_lang('18')}{result[0]}')
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
                QMessageBox.information(self, get_lang('16'), get_lang('19'))
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
        
        # 重置变量
        clicker.running = False
        clicker.left_clicked = False
        clicker.right_clicked = False
        clicker.paused = False
        
        # 重置按钮样式
        self.left_click_button.setStyleSheet(default_style)
        self.right_click_button.setStyleSheet(default_style)
        
        # 重置文本
        self.pause_button.setText(get_lang('0f'))

    def on_click_changed(self, left, right):
        '''click按钮状态改变'''
        if left:
            # 左键点击
            self.left_click_button.setStyleSheet(selected_style)
            self.right_click_button.setStyleSheet(default_style)
        elif right:
            # 右键点击
            self.right_click_button.setStyleSheet(selected_style)
            self.left_click_button.setStyleSheet(default_style)
        else:
            # 未点击
            self.left_click_button.setStyleSheet(default_style)
            self.right_click_button.setStyleSheet(default_style)

class AboutWindow(QDialog):
    def __init__(self):
        super().__init__()
        logger.info('初始化关于窗口')
        self.setWindowTitle(filter_hotkey(get_lang('0a')))
        self.setGeometry(100, 100, 375, 150)
        self.setWindowIcon(icon)
        self.setFixedSize(self.width(), self.height())
        self.init_ui()

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
        
        version_status_text = '预览版' if ('alpha' in __version__) or ('beta' in __version__) or ('.dev' in __version__) else ''
        version = QLabel(get_lang('1c').format(__version__, version_status_text))
        # version = QLabel(get_lang('1c').format(__version__, version_status_text))
        if not dev_config['verify_clickmouse']:
            not_official_version = QLabel('此clickmouse不是官方版本')
        else:
            not_official_version = QLabel('')
        about = QLabel(get_lang('1d'))
        
        # 按钮
        logger.debug('创建按钮')
        ok_button = QPushButton(get_lang('1e'))
        ok_button.setStyleSheet(selected_style)
        support_author = QPushButton(get_lang('20'))

        # 布局
        central_layout.addWidget(self.image_label, 0, 0, 1, 1)
        central_layout.addWidget(version, 0, 1, 1, 2)
        central_layout.addWidget(not_official_version, 1, 1, 1, 2)
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
            QMessageBox.information(self, get_lang('16'), get_lang('21'))

        with open(get_resource_path('vars', 'update_log.json'), 'r', encoding='utf-8') as f:
            self.update_logs = json.load(f) # 加载更新日志
            
            
        logger.debug('初始化更新日志窗口')
        self.init_ui()

    def init_ui(self):
        # 创建面板
        layout = QVBoxLayout()

        # 通过字典存储的日志信息来绘制日志内容，并动态计算日志的高度，减少代码量且更加方便管理
        for k, v in self.update_logs.items():
            label = QLabel(f'{k}    {v[0]}\n{v[1]}')
            layout.addWidget(label)

        # 调整页面高度，适配现在的更新日志界面大小
        logger.debug('调整页面高度')

        # 面板控件
        license_label = QLabel(get_lang('22'))

        # 按钮
        logger.debug('创建按钮')
        
        bottom_layout = QHBoxLayout() # 底布局
        
        ok_button = QPushButton(get_lang('1e'))
        ok_button.setStyleSheet(selected_style)
        more_update_log = QPushButton(get_lang('23'))
        
        bottom_layout.addWidget(more_update_log)
        bottom_layout.addStretch(1)
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
        self.init_ui()

    def init_ui(self):
        # 加载常量
        logger.debug('加载常量')
        self.locked_checkbox = False # 锁定选择框模式，按下后将不会产生来自非手动操作的更新选择框

        # 创建面板
        layout = QGridLayout()
        
        # 面板控件
        logger.debug('加载ui')
        logger.debug('加载列表标题')
        
        title = QLabel(get_lang('3d'))
        
        title.setStyleSheet(big_title)

        dest = QLabel(get_lang('3e'))
        
        # 布局1
        logger.debug('加载布局-1')
        layout.addWidget(title, 0, 0, 1, 4)
        layout.addWidget(dest, 1, 0, 1, 4)
        
        logger.debug('加载动态数据')

        # 加载ui
        self.point_y = 70 # 初始y坐标
        file = QLabel(get_lang('33'))
        path = QLabel(get_lang('34'))
        dest = QLabel(get_lang('35'))
        size =  QLabel(get_lang('36'))
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
            for value in v:
                if type(value) is str and value.startswith(' '):
                    cache_list[get_lang(k[1:])].append(get_lang(value[1:]))
                else:
                    cache_list[get_lang(k[1:])].append(value)

        self.cache_dir_list = {'logs'} # 缓存文件路径的列表
        self.cache_file_list = {'update.json'} # 缓存文件列表

        self.all_checkbox = QCheckBox('')
        self.all_checkbox.setTristate(True) # 三状态复选框
        self.locked_checkbox = True # 临时切换
        self.all_checkbox.setCheckState(Qt.PartiallyChecked) # 初始状态为部分选中
        self.locked_checkbox = False # 锁定选择框模式
        
        self.all_size_text = QLabel(get_lang('37'))
        # 布局3
        logger.debug('加载布局-3')
        layout.addWidget(self.all_checkbox, 3, 0)
        layout.addWidget(self.all_size_text, 3, 3)

        size_index = 2 # 自定义字符大小的索引
        self.checkbox_list: list[QCheckBox] = [] # 缓存文件选择框的列表
        self.cache_path_list: list[QLabel] = [] # 文件路径字符的列表
        self.cache_size_list: list[QLabel] = [] # 缓存文件大小字符的列表
        logger.debug('加载动态内容')
        for i, d in enumerate(cache_list.items()): # 遍历缓存列表
            k = d[0]
            v = d[1]
            len_v = len(v)
            box = QCheckBox(k)
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
        clean_cache.setStyleSheet(selected_style)
        
        # 布局4
        logger.debug('加载布局-4')        
        bottom_layout = QHBoxLayout()
        bottom_layout.addSpacing(200)
        bottom_layout.addWidget(scan_cache)
        bottom_layout.addStretch(1)
        bottom_layout.addWidget(clean_cache)
        bottom_layout.addStretch(1)
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
                QMessageBox.critical(self, get_lang('14'), get_lang('3a').format(e))
                logger.error(f'无法删除文件或文件夹：{e}')

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
                QMessageBox.critical(self, get_lang('14'), get_lang('3a').format(e))
                logger.error(f'无法删除文件或文件夹：{e}')
        # 弹出提示窗口
        QMessageBox.information(self, get_lang('16'), get_lang('3b').format(self.format_size(select_cache_size)))
    
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
        self.setGeometry(100, 100, 300, 140)
        self.setFixedSize(300, 140)
        self.setWindowIcon(icon)
        
        self.init_ui()

    def init_ui(self):
        # 创建面板
        logger.debug('创建面板')
        layout = QVBoxLayout()
        
        # 面板控件
        logger.debug('创建面板控件')
        title = QLabel(get_lang('24'))
        version = QLabel(get_lang('25').format(__version__, result[1]))
        
        title.setStyleSheet(big_title)

        # 按钮
        update = QPushButton(get_lang('26')) # 更新按钮
        update.setStyleSheet(selected_style)
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

        bottom_layout.addStretch(1)
        bottom_layout.addWidget(update)
        bottom_layout.addWidget(update_log)
        bottom_layout.addWidget(cancel)

        layout.addLayout(bottom_layout)
        
        self.setLayout(layout)

    def on_update(self, event):
        '''更新'''
        open_url('https://github.com/xystudio889/pyClickMouse/releases')

    def on_open_update_log(self, event):
        # 打开更新日志
        logger.debug('打开更新日志')

        update_log = cache_path / 'update_log.md' # 更新日志路径
        
        if not update_log.exists(): # 重建更新日志
            update_info = result[2]
            
            with open(update_log, 'w', encoding='utf-8') as f:
                if update_info:
                    f.write(update_info)
                else:
                    f.write('更新内容获取失败')
        
        os.startfile(update_log) # 打开更新日志
        # 弹出提示窗口
        QMessageBox.information(self, get_lang('16'), get_lang('28'))
        
class TrayApp:
    def __init__(self):
        self.app = get_application_instance()

        show_tray_icon = settings.get('show_tray_icon', True)
        if show_tray_icon:
            self.app.setQuitOnLastWindowClosed(False)  # 关闭窗口时不退出应用
        
        # 激活主窗口
        main_window.show()
        
        # 创建设置延迟窗口
        self.set_dalay_window = FastSetClickWindow()
        
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
        show_action = QAction('打开应用', self.app)
        show_action.triggered.connect(self.show_main_window)
        tray_menu.addAction(show_action)
        
        # 添加分隔线
        tray_menu.addSeparator()
        
        # 控制类按钮
        left_click_action = QAction('左键连点', self.app)
        right_click_action = QAction('右键连点', self.app)
        pause_action = QAction('暂停/重启连点', self.app)
        stop_action = QAction('停止连点', self.app)
        set_delay_action = QAction('设置延迟', self.app)
        
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
        quit_action = QAction('退出', self.app)
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(quit_action)
        
        # 设置托盘图标的菜单
        self.tray_icon.setContextMenu(tray_menu)
    
    def start_hotkey_listener(self):
        '''启动热键监听器（在单独的线程中）''' 
        # 在后台线程中启动热键监听
        hotkey_thread = threading.Thread(target=self.hotkey_listener.start_listening)
        hotkey_thread.daemon = True  # 设置为守护线程，主程序退出时自动结束
        hotkey_thread.start()
    
    def on_tray_icon_activated(self, reason):
        '''处理托盘图标激活事件'''
        if reason == QSystemTrayIcon.ActivationReason.Trigger:  # 左键点击
            self.show_main_window()
            
    def check_delay(self, input_delay):
        try:
            delay = int(input_delay)
            if delay < 1:
                raise ValueError
        except ValueError:
            if settings.get('click_delay', '') == '':
                self.tray_icon.showMessage(get_lang('14'), get_lang('1a'), QSystemTrayIcon.MessageIcon.Critical, 1000)
                logger.error('用户输入错误：请输入有效的正整数延迟')
                return
            else:
                if input_delay == '':
                    if check_default_delay():
                        delay = int(settings.get('click_delay', ''))
                    else:
                        return
                elif settings.get('failed_use_default', False):
                    if check_default_delay():
                        delay = int(settings.get('click_delay', ''))
                    else:
                        return
                else:
                    self.tray_icon.showMessage(get_lang('14'), get_lang('1a'), QSystemTrayIcon.MessageIcon.Critical, 1000)
                    logger.error('用户输入错误：请输入有效的正整数延迟')
                    return
        return True
    
    def on_key_pressed(self, key):
        '''处理按键事件'''
        if key == keyboard.Key.f1:
            self.set_dalay_window.exec()
        elif key == keyboard.Key.f2:
            # 判断参数有效性
            input_delay = main_window.input_delay.text()
            
            if not self.check_delay(input_delay):
                return

            self.tray_icon.showMessage('热键提示', '已启动左键连点', QSystemTrayIcon.MessageIcon.Information, 1000)
            clicker.mouse_left(input_delay)
        elif key == keyboard.Key.f3:
            # 判断参数有效性
            input_delay = main_window.input_delay.text()
            
            if not self.check_delay(input_delay):
                return

            self.tray_icon.showMessage('热键提示', '已启动右键连点', QSystemTrayIcon.MessageIcon.Information, 1000)
            clicker.mouse_right(input_delay)
        elif key == keyboard.Key.f4:
            clicker.pause_click()
            if clicker.running:
                if clicker.paused:
                    self.tray_icon.showMessage('热键提示', '已暂停连点', QSystemTrayIcon.MessageIcon.Information, 1000)
                else:
                    self.tray_icon.showMessage('热键提示', '已重启连点', QSystemTrayIcon.MessageIcon.Information, 1000)
            else:
                self.tray_icon.showMessage('热键提示', '连点未启动', QSystemTrayIcon.MessageIcon.Warning, 1000)
        elif key == keyboard.Key.f6:
            if clicker.running:
                main_window.on_stop()
                self.tray_icon.showMessage('热键提示', '已停止连点', QSystemTrayIcon.MessageIcon.Information, 1000)
            else:
                self.tray_icon.showMessage('热键提示', '连点未启动', QSystemTrayIcon.MessageIcon.Warning, 1000)
    
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
        
    def on_combination_pressed(self, combination):
        '''处理组合键事件'''
        temp_combination = combination.copy()
        
        for index, i in enumerate(temp_combination):
            temp_combination[index] = i.replace('Key.', '').replace('_l', '').replace('_r', '').replace('_gr', '')
        combination = temp_combination.copy()

        if all_in_list(combination, ['<68>', 'ctrl', 'alt']):
            # 处理Ctrl+Alt+D组合键
            if main_window.isVisible():
                main_window.hide()
            else:
                main_window.show()

class HotkeyHelpWindow(QDialog):
    def __init__(self):
        logger.info('初始化热键帮助窗口')
        super().__init__()
        self.setWindowTitle('热键帮助')
        self.setWindowIcon(icon)
        
        self.init_ui()
    
    def init_ui(self):
        # 创建面板
        logger.debug('创建面板')
        layout = QVBoxLayout()
        
        # 面板控件
        logger.debug('创建面板控件')
        title = QLabel('热键帮助')
        title.setStyleSheet(big_title)

        layout.addWidget(title)
        
        # 热键说明
        with open(get_resource_path('vars', 'hotkey.json'), 'r', encoding='utf-8') as f:
            hotkeys = json.load(f)
        
        # 显示热键说明
        for k, v in hotkeys.items():
            hotkey_label = QLabel(f'{k}：{v}')
            layout.addWidget(hotkey_label)
            
        bottom_layout = QHBoxLayout()
        ok_button = QPushButton(get_lang('1e'))
        ok_button.setStyleSheet(selected_style)
        ok_button.clicked.connect(self.close)
        
        # 布局
        logger.debug('布局')
        bottom_layout.addStretch(1)
        bottom_layout.addWidget(ok_button)
        
        layout.addLayout(bottom_layout)
        
        self.setLayout(layout)

class FastSetClickWindow(QDialog):
    def __init__(self):
        logger.info('初始化快速设置延迟窗口')
        super().__init__()
        self.setWindowTitle('设置延迟')
        self.setWindowIcon(icon)
        self.setGeometry(100, 100, 400, 50)
        self.setFixedSize(self.width(), self.height())        
        self.init_ui()
    
    def init_ui(self):
        # 创建面板
        logger.debug('创建面板')
        layout = QFormLayout()
        
        # 面板控件
        logger.debug('创建面板控件')
  
        self.input_delay = QLineEdit()
        self.input_delay.setFixedWidth(300)
        self.input_delay.setFixedHeight(30)
        
        layout.addRow(get_lang('11'), self.input_delay)
        
        # 添加信号
        self.input_delay.textChanged.connect(self.on_input_delay_changed)
        
        # 布局
        self.setLayout(layout)
        
    def exec(self):
        '''显示窗口'''
        super().exec()
        self.input_delay.setText(main_window.input_delay.text())
    
    def on_input_delay_changed(self, text):
        '''输入框内容变化事件'''
        main_window.input_delay.setText(text)
        
class SettingWindow(SelectUI):
    closed_use_reload = Signal()

    def __init__(self, parent=None):
        super().__init__()

        self.setGeometry(300, 300, 600, 400)  # 增加窗口大小以容纳更多内容
        self.setWindowTitle('设置')
        self.setParent(parent)
        self.setWindowIcon(icon)
        self.setWindowFlags(
            Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint
        ) # 设置窗口属性
        # self.setFixedSize(self.width(), self.height()) # 固定窗口大小
        
        self.page_choice_buttons = [get_lang('42'), get_lang('43'), get_lang('44')]
        self.init_ui()

    def create_setting_page(self, title):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # 标题标签
        title_label = QLabel(title)
        title_label.setStyleSheet(replace_style_sheet(big_title, 'font-size', '16px', '24px'))
        layout.addWidget(title_label)
        
        # 内容标签
        dest = get_style_sheet('dest', current_theme)
        content_label = QLabel('该设置暂无描述')
        content_label.setStyleSheet(dest)
        layout.addWidget(content_label)
        
        def set_content_label(text):
            content_label.setText(text)
        
        restart_layout = QHBoxLayout()
        self.restart_button = QPushButton('立即重启')
        
        self.restart_button.setStyleSheet(selected_style)
        self.restart_button.clicked.connect(self.restart)

        if any(need_restart_list):
            self.restart_button.show()
        else:
            self.restart_button.hide()
            
        need_restart_style = replace_style_sheet(dest, 'font-size', '16px', '12px')
        
        self.page_general = self.page_choice_buttons[0] # 默认设置
        self.page_click = self.page_choice_buttons[1] # 连点器设置
        self.page_update = self.page_choice_buttons[2] # 更新设置
        
        # 添加一些示例设置控件
        match title:
            case self.page_general:
                set_content_label('用于应用一些常规功能，可能需要重启软件。')
                # 选择语言
                choice_text = QLabel(get_lang('45')) # 选择语言提示
                
                lang_choice_layout = QHBoxLayout() # 语言选择布局
                self.lang_choice = QComboBox()
                self.lang_choice.addItems([i['lang_name'] for i in langs])
                self.lang_choice.setCurrentIndex(settings.get('select_lang', 0))
                lang_choice_need_restart = QLabel(get_lang('56'))
                lang_choice_need_restart.setStyleSheet(need_restart_style)
                if need_restart_list[0]:
                    lang_choice_need_restart.show()
                else:
                    lang_choice_need_restart.hide()
                
                # 布局
                lang_choice_layout.addWidget(choice_text)
                lang_choice_layout.addWidget(self.lang_choice)
                lang_choice_layout.addWidget(lang_choice_need_restart)
                lang_choice_layout.addStretch(1)
                
                # 选择窗口风格
                style_text = QLabel('窗口主题:') # 选择窗口风格提示
                
                style_layout = QHBoxLayout() # 窗口风格布局
                style_choice = QComboBox()
                
                items = list(style_indexes[settings['select_lang']]['lang_package'].values())
    
                style_choice.addItems(['跟随Windows系统'] + items + ['禁用'])
                style_choice.setCurrentIndex(settings.get('select_style', 0))
                
                style_layout.addWidget(style_text)
                style_layout.addWidget(style_choice)
                style_layout.addStretch(1)
                
                # 显示托盘图标
                # 选择窗口风格  
                tray_layout = QHBoxLayout() # 窗口风格布局
                tray = QCheckBox('保留托盘图标')
                tray.setChecked(settings.get('show_tray_icon', True))
                tray_need_restart = QLabel('需要重启软件才能生效。')
                tray_need_restart.setStyleSheet(need_restart_style)
                if need_restart_list[1]:
                    tray_need_restart.show()
                else:
                    tray_need_restart.hide()
    
                tray_layout.addWidget(tray)
                tray_layout.addWidget(tray_need_restart)
                tray_layout.addStretch(1)

                # 布局
                layout.addLayout(lang_choice_layout)
                layout.addLayout(style_layout)
                layout.addLayout(tray_layout)
                
                # 绑定事件
                self.lang_choice.currentIndexChanged.connect(lambda: self.on_need_restart_setting_changed(self.lang_choice.currentIndex, 'select_lang', lang_choice_need_restart, 0))
                style_choice.currentIndexChanged.connect(lambda: self.on_setting_changed(style_choice.currentIndex, 'select_style'))
                tray.stateChanged.connect(lambda: self.on_need_restart_setting_changed(tray.isChecked,'show_tray_icon', tray_need_restart, 1))
            case self.page_click:
                set_content_label('用于设置连点器的一些参数。')
                # 选择默认连点器延迟
                default_delay_layout = QFormLayout() # 窗口风格布局
                self.default_delay = QLineEdit()
                self.default_delay.setText(str(settings.get('click_delay', '')))
                default_delay_layout.addRow(get_lang('46'), self.default_delay)
                
                # 连点出错时使用默认值
                use_default_delay = QCheckBox(get_lang('47'))
                use_default_delay.setChecked(settings.get('failed_use_default', False))
                if not self.default_delay.text():
                    use_default_delay.setEnabled(False)
                    
                # 布局
                layout.addLayout(default_delay_layout)
                layout.addWidget(use_default_delay)
                
                # 连接信号
                self.default_delay.textChanged.connect(lambda: self.on_default_delay_changed(use_default_delay))
                use_default_delay.stateChanged.connect(lambda: self.on_setting_changed(use_default_delay.isChecked, 'failed_use_default'))
            case self.page_update:
                set_content_label('用于设置软件更新相关设置。')
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
        
        restart_layout.addStretch()
        restart_layout.addWidget(self.restart_button)
        layout.addLayout(restart_layout)

        # 添加弹簧，让内容靠上显示
        layout.addStretch()
        
        return page
        
    def on_need_restart_setting_changed(self, handle: Callable, setting_key: str, need_restart_label: QLabel, index: int, *args):
        '''托盘图标选择事件'''
        need_restart_label.show()
        self.restart_button.show()
        need_restart_list[index] = True
        settings[setting_key] = handle(*args)
        save_settings(settings)
        self.closed_use_reload.emit()
        self.close()
        
    def on_default_delay_changed(self, use_default_delay):
        '''默认延迟输入框内容变化事件'''
        if not self.default_delay.text():
            use_default_delay.setEnabled(False)
        else:
            use_default_delay.setEnabled(True)
        settings['click_delay'] = self.default_delay.text()
        save_settings(settings)

    def on_setting_changed(self, handle, key):
        '''更新检查提示选择事件'''
        settings[key] = handle()
        save_settings(settings)
    
    def on_page_button_clicked(self, index):
        '''处理页面按钮点击事件'''
        # 切换到对应的页面
        self.stacked_widget.setCurrentIndex(index)
        
        # 更新按钮样式
        for i, button in enumerate(self.buttons):
            if i == index:
                button.setStyleSheet(selected_style)
            else:
                button.setStyleSheet(default_style)  # 恢复默认样式
    
    def restart(self):
        run_software('main.py', 'main.exe')
        exit(0)
    
    def init_right_pages(self):
        super().init_right_pages()
        self.buttons[0].setStyleSheet(selected_style)
def main():
    app = TrayApp()
    app.run()

if __name__ == '__main__':
    # if not(data_path / 'first_run').exists():
    #     run_software('init.py', 'cminit.exe')
    # else:

    is_installed_doc, is_installed_lang_doc = (False, False)# check_doc_exists()
    # with open('packages.json', 'r', encoding='utf-8') as f:
    #     packages = json.load(f)
    packages = None

    # package_list, indexes, install_location, package_id, show_list = get_packages()

    if not (data_path / 'first_run').exists():
        SelectLanguage_window = SelectLanguage()
        SelectLanguage_window.show()
        app.exec()
    main_window = MainWindow()
    main()
    logger.info('主程序退出')
