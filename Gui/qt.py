# 加载库
import sys # 系统库
from PySide6.QtWidgets import * # 界面库
from PySide6.QtGui import (QPixmap, QIcon, QFont) # 图标库
from PySide6.QtCore import (Qt, QThread, Signal) # 核心库
app = QApplication(sys.argv)

from pathlib import Path # 文件管理库
import pyautogui # 鼠标操作库
import threading # 用于鼠标点击
from time import sleep, time # 延迟
from webbrowser import open as open_url # 关于作者
from version import __version__, __author__ # 版本信息
from log import Logger # 日志库
from check_update import check_update # 更新检查
from datetime import datetime # 用于检查缓存的时间和现在相差的时间
import json # 用于读取配置文件
import os # 系统库
import shutil # 用于删除文件夹
# import uiStyles # 软件界面样式
from sharelibs import (run_software, in_dev)
import zipfile # 压缩库
import parse_dev # 解析开发固件配置

logger = Logger('主程序日志', level=0)
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

def get_lang(lang_package_id, lang_id = None):
    lang_id = settings.get('select_lang', 0) if lang_id is None else lang_id
    for i in langs:
        if i['lang_id'] == 0: # 设置默认语言包
            default_lang_text = i['lang_package']
        if i['lang_id'] == lang_id: # 设置目前语言包
            lang_text = i['lang_package']
    try:
        return lang_text.get(lang_package_id, default_lang_text[lang_package_id])
    except KeyError:
        logger.critical(f'错误：出现一个不存在的语言包id:{lang_package_id}')
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
    cache_data = {
        'last_check_time': time(),
        **kwargs
    }
    with open(update_cache_path, 'w', encoding='utf-8') as f:
        json.dump(cache_data, f)
        
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
    
    # 加载包信息
    for package in packages:
        list_packages.append(package.get('package_name', None))
        lang_index.append(package.get('package_name_lang_index', None))
        package_path.append(package.get('install_location', None))
        package_index.append(package.get('package_id', None))
        show.append(package.get('show_in_extension_list', True))
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

class QtThread(QThread):
    """检查更新工作线程"""
    finished = Signal(object) # 爬取完成信号

    def __init__(self, func, args=(), kwargs={}, parent=None):
        super().__init__(parent)
        self.func = func
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        """线程执行函数"""
        result = self.func(*self.args, **self.kwargs)
        self.finished.emit(result)

# 变量
logger.debug('定义资源')

logger.debug('定义数据路径和创建文件夹')

# 定义数据路径
data_path = Path('data')
cache_path = Path('cache')
update_cache_path = cache_path / 'update.json'

# 创建文件夹（如果不存在）
data_path.mkdir(parents=True, exist_ok=True)
cache_path.mkdir(parents=True, exist_ok=True)

# 创建资源
should_check_update_res = should_check_update()
update_cache = load_update_cache()
settings = load_settings()
icon = QIcon(str(get_resource_path('icons', 'clickmouse', 'icon.ico')))

logger.debug('定义语言包')
with open(get_resource_path('langs.json'), 'r', encoding='utf-8') as f:
    langs = json.load(f)
logger.debug('定义资源完成')

with open(get_resource_path('versions.json'), 'r') as f:
    __version__ = json.load(f)['clickmouse_in_qt']

logger.debug('加载ui')

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
        
        self.setFixedSize(self.width(), self.height()) # 固定窗口大小

        logger.debug('初始化状态控制变量')
        self.running = False
        self.paused = False
        self.click_thread = None
        
        logger.debug('初始化ui')
        
        self.on_check_update()
        self.init_ui()
        
    def on_check_update(self):
        logger.debug('检查更新')
        # 检查更新
        if should_check_update_res:
            shutil.rmtree(str(cache_path / 'logs'), ignore_errors=True) # 删除旧缓存
            self.check_update_thread = QtThread(check_update, args=('gitee', False))
            self.check_update_thread.finished.connect(self.on_check_update_result)
            self.check_update_thread.start()
        else:
            logger.info('距离上次更新检查不到1天，使用缓存')
            self.on_check_update_result(update_cache) # 使用缓存
            
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
                if result[0]:  # 检查到需要更新
                    logger.info('检查到更新')
                    # 弹出更新窗口
                    # window = UpdateWindow(self)
                    # window.ShowModal()
                    # window.Destroy()
            else:
                if self.check_update_thread.isFinished():
                    logger.error(f'检查更新错误: {result[0]}')
                    QMessageBox.critical(self, get_lang('14'), f'{get_lang('18')}{result[0]}')
        else:
            if result[1] != -1:
                if should_check_update_res:
                    save_update_cache(should_update=result[0], latest_version=result[1], update_info=result[2])
    
    def init_ui(self):
        # 创建主控件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_layout = QVBoxLayout(central_widget)
        
        # 创建标题大字
        title_label = QLabel(get_lang('0b'))
        
        title_font = QFont()
        title_font.setFamily('宋体')
        title_font.setPointSize(20)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        title_label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        
        # 按钮
        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)  # 设置按钮间距

        self.left_click_button = QPushButton(get_lang('0c'))
        self.left_click_button.setFixedSize(100, 60)
        
        self.right_click_button = QPushButton(get_lang('0d'))
        self.right_click_button.setFixedSize(100, 60)
        
        self.pause_button = QPushButton(get_lang('0f'))
        self.pause_button.setFixedSize(100, 40)
        
        self.stop_button = QPushButton(get_lang('0e'))
        self.stop_button.setFixedSize(100, 40)
        
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
        
        central_layout.addWidget(title_label)
        central_layout.addLayout(grid_layout)
        central_layout.addLayout(form_layout)
        self.setLayout(central_layout)
        
        # 按钮信号连接
        logger.debug('信号连接')
        self.left_click_button.clicked.connect(self.on_mouse_left)
        self.right_click_button.clicked.connect(self.on_mouse_right)

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

        # doc = help_menu.addAction('文档(&D)')
        # if not(is_installed_doc):
        #     doc.setEnabled(False)
            
        # 绑定动作
        about_action.triggered.connect(self.show_about)
        update_log.triggered.connect(self.show_update_log)
        clean_cache_action.triggered.connect(self.clean_cache)
            
    def show_about(self):
        '''显示关于窗口'''
        about_window = AboutWindow()
        about_window.exec()
        
    def show_update_log(self):
        '''显示更新日志'''
        update_log_window = UpdateLogWindow()
        update_log_window.exec()
    
    def clean_cache(self):
        '''清理缓存'''
        clean_cache_window = CleanCacheWindow()
        clean_cache_window.exec()
        
    def on_mouse_left(self):
        logger.info('左键连点')
        # 停止当前运行的点击线程
        if self.click_thread and self.click_thread.is_alive():
            logger.debug('停止当前运行的点击线程')
            self.running = False
            self.click_thread.join()  # 等待线程结束
        
        # 获取新参数并启动左键点击
        delay = self.input_delay.text()
        self.mouse_click(button='left', input_delay=delay)

    def on_mouse_right(self):
        # 停止当前运行的点击线程
        logger.info('右键连点')
        if self.click_thread and self.click_thread.is_alive():
            logger.debug('停止当前运行的点击线程')
            self.running = False
            self.click_thread.join()  # 等待线程结束
        
        # 获取新参数并启动右键点击
        delay = self.input_delay.text()
        self.mouse_click(button='right', input_delay=delay)
        
    def mouse_click(self, button: str, input_delay: str):
        '''鼠标连点'''
        logger.info('开始连点')
        # 重置状态
        if self.click_thread and self.click_thread.is_alive():
            self.running = False
            self.click_thread.join()

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
                QMessageBox.critical(self, get_lang('14'), get_lang('1a'))
                logger.error('用户输入错误：请输入有效的正整数延迟')
                return
            else:
                if input_delay == '':
                    delay = int(settings.get('click_delay', ''))
                elif settings.get('failed_use_default', False):
                    delay = int(settings.get('click_delay', ''))
                else:
                    QMessageBox.critical(self, get_lang('14'), get_lang('1a'))
                    logger.error('用户输入错误：请输入有效的正整数延迟')
                    return

        # 创建独立线程避免阻塞GUI
        def click_loop():
            while self.running:
                if not self.paused:
                    try:
                        pyautogui.click(button=button)
                        sleep(delay/1000)
                    except Exception as e:
                        QMessageBox.critical(None, get_lang('14'), f'{get_lang('1b')} {str(e)}')
                        logger.critical(f'发生错误:{e}')
                        break
                else:
                    sleep(0.1)  # 暂停时降低CPU占用
                    
        def on_pause_click(event):
            logger.info('连点器暂停或重启')
            self.paused = not self.paused
            if self.paused:
                self.pause_button.setText(get_lang('10'))
            else:
                self.pause_button.setText(get_lang('0f'))

        self.pause_button.clicked.connect(on_pause_click)

        # 启动线程
        logger.info(f'启动连点线程')
        self.click_thread = threading.Thread(target=click_loop)
        self.click_thread.daemon = True
        self.click_thread.start()

        # 绑定控制按钮
        self.stop_button.clicked.connect(lambda e: setattr(self, 'running', False))
        self.stop_button.clicked.connect(lambda e: (
        setattr(self, 'running', False),
        self.pause_button.setText(get_lang('0f'))
    ))
        
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

        version = QLabel(f'clickmouse in Qt,版本号{__version__}\n\n一款快捷，使用python制作的鼠标连点器')
        # version = QLabel(get_lang('1c').format(__version__, version_status_text))
        if not dev_config['verify_clickmouse']:
            not_official_version = QLabel('此clickmouse不是官方版本')
        else:
            not_official_version = QLabel('')
        about = QLabel(get_lang('1d'))
        
        # 按钮
        logger.debug('创建按钮')
        ok_button = QPushButton(get_lang('1e'))
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
        """加载并显示图片"""
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
    def __init__(self, parent=MainWindow):
        logger.info('初始化清理缓存窗口')
        super().__init__()
        self.setWindowTitle(filter_hotkey(get_lang('02')))
        self.setWindowIcon(icon)
        self.init_ui()

    def init_ui(self):
        # 创建面板
        layout = QGridLayout()
        
        # 面板控件
        self.select_mode_text = {'all':get_lang('2a'),'none':get_lang('2b'),'part':get_lang('2c')}
        logger.debug('加载ui')
        logger.debug('加载列表标题')
        
        title = QLabel(get_lang('3d'))
        
        font = QFont()
        font.setFamily('宋体')
        font.setPointSize(16)
        font.setBold(True)
        
        title.setFont(font)

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

        self.btn_all = QPushButton(self.select_mode_text['part'])
        self.all_size_text = QLabel(get_lang('37'))
        # 布局3
        logger.debug('加载布局-3')
        layout.addWidget(self.btn_all, 3, 0)
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
        self.btn_all.clicked.connect(self.on_all_check)
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
        checked_count = sum(cb.isChecked() for cb in self.checkbox_list)
        total = len(self.checkbox_list)
        
        if checked_count == 0:
            self.btn_all.setText(self.select_mode_text['none'])
        elif checked_count == total:
            self.btn_all.setText(self.select_mode_text['all'])
        else:
            self.btn_all.setText(self.select_mode_text['part'])
            
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

    def on_all_check(self):
        '''全选按钮点击事件'''
        current_label = self.btn_all.text()
        target_state = not (current_label == self.select_mode_text['all'])  # 根据当前状态取反
        
        for cb in self.checkbox_list:
            cb.setChecked(target_state)
        
        # 自动更新缓存按钮状态
        self.update_all_check_status()

if __name__ == '__main__':
    # if not(data_path / 'first_run').exists():
    #     run_software('init.py', 'cminit.exe')
    # else:
    is_installed_doc, is_installed_lang_doc = (False, False)# check_doc_exists()
    # with open('packages.json', 'r', encoding='utf-8') as f:
    #     packages = json.load(f)

    # package_list, indexes, install_location, package_id, show_list = get_packages()

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

