# 加载库
import sys # 系统库
from PySide6.QtWidgets import * # 界面库
from PySide6.QtGui import (QPixmap, QIcon, QFont) # 图标库
from PySide6.QtCore import (Qt) # 核心库
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
import uiStyles # 软件界面样式
from sharelibs import (run_software, in_dev)
import zipfile # 压缩库
import parse_dev # 解析开发固件配置

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
        # 创建文件
        logger.warning('更新缓存文件不存在，创建默认缓存文件')
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
        QMessageBox.warning('软件目录下缺少默认文档文件，所以"文档"功能将被禁用\n修复方法：这可能是再编译版本，请找到源程序的docs目录，使用HTML Help Workshop等工具制作chm文档，并将其放入res\\docs目录下后再编译', '提示')
        is_installed_docs = False
        is_installed_this_lang_docs = False
    elif not(os.path.exists(get_resource_path('docs', f'{get_lang_system_name()}.chm'))):
        QMessageBox.warning(f'软件目录下缺少{get_lang_system_name()}语言的文档文件，所以"文档"功能将会显示英文文档\n修复方法：这可能是第三方语言包，需要重新对这个语言包制作html版本文档', '提示')
        is_installed_this_lang_docs = False

    return (is_installed_docs, is_installed_this_lang_docs)

class ResultThread(threading.Thread):
    '''带有返回值的线程'''
    def __init__(self, target, args=(), daemon=False):
        super().__init__()
        self.target = target
        self.args = args
        self.daemon = daemon
        self._result = None
    
    def run(self):
        self._result = self.target(*self.args)
        
    def result(self):
        return self._result

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

logger.debug('检查更新')
# 检查更新
if should_check_update_res:
    shutil.rmtree(str(cache_path), ignore_errors=True) # 删除旧缓存
    check_update_thread = ResultThread(target=check_update, args=('gitee', False), daemon=True)
    check_update_thread.start()    
logger.debug('检查更新完成')

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
        
        self.init_ui()
    
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

        doc = help_menu.addAction('文档(&D)')
        if not(is_installed_doc):
            doc.setEnabled(False)
            
        # 绑定动作
        about_action.triggered.connect(self.show_about)
            
    def show_about(self):
        '''显示关于窗口'''
        about_window = AboutWindow()
        about_window.exec()
        
    def on_mouse_left(self, event):
        logger.info('左键连点')
        # 停止当前运行的点击线程
        if self.click_thread and self.click_thread.is_alive():
            logger.debug('停止当前运行的点击线程')
            self.running = False
            self.click_thread.join()  # 等待线程结束
        
        # 获取新参数并启动左键点击
        delay = self.input_delay.text()
        self.mouse_click(button='left', input_delay=delay)

    def on_mouse_right(self, event):
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
        # if dev_config['verify_clickmouse']:
        #     not_official_version = QLabel('此clickmouse不是官方版本')
        about = QLabel(get_lang('1d'))
        
        # 按钮
        logger.debug('创建按钮')
        ok_button = QPushButton(get_lang('1e'))
        support_author = QPushButton(get_lang('20'))

        # 布局
        central_layout.addWidget(self.image_label, 0, 0, 1, 1)
        central_layout.addWidget(version, 0, 1, 1, 2)
        # central_layout.addWidget(not_official_version, 1, 1, 1, 2)
        central_layout.addWidget(about, 1, 0, 1, 3)
        central_layout.addWidget(support_author, 2, 0)
        central_layout.addWidget(ok_button, 2, 2)

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

    def on_support_author(self, event):
        '''支持作者'''
        open_url('https://github.com/xystudio889/pyClickMouse')
        
if __name__ == '__main__':
    if not(data_path / 'first_run').exists():
        run_software('init.py', 'cminit.exe')
    else:
        is_installed_doc, is_installed_lang_doc = (False, False)# check_doc_exists()
        with open('packages.json', 'r', encoding='utf-8') as f:
            packages = json.load(f)

        package_list, indexes, install_location, package_id, show_list = get_packages()

        window = MainWindow()
        window.show()
        sys.exit(app.exec())

