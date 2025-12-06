# 加载库
from pathlib import Path # 文件管理库
import pyautogui # 鼠标操作库
from sys import argv # 获取命令行参数
import threading # 用于鼠标点击
from time import sleep, time # 延迟
from webbrowser import open as open_url # 关于作者
import wx # GUI库
from PySide6.QtWidgets import QApplication # 用于启用使用pyside6的文件缺失错误通知
QApplication()# 启用pyside6 app

from version import __version__, __author__ # 版本信息
from log import Logger # 日志库
from check_update import check_update # 更新检查
from datetime import datetime # 用于检查缓存的时间和现在相差的时间
import json # 用于读取配置文件
import os # 系统库
import shutil # 用于删除文件夹
import sys # 系统库
import uiStyles.old # 软件界面样式
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
        wx.MessageBox(f'{get_lang('12')}{e}', get_lang('14'), wx.OK | wx.ICON_ERROR)
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
    """将文件路径最后一段的.py替换为.exe"""
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
        wx.MessageBox('软件目录下缺少默认文档文件，所以"文档"功能将被禁用\n修复方法：这可能是再编译版本，请找到源程序的docs目录，使用HTML Help Workshop等工具制作chm文档，并将其放入res\\docs目录下后再编译', get_lang('16'), wx.OK | wx.ICON_WARNING)
        is_installed_docs = False
        is_installed_this_lang_docs = False
    elif not(os.path.exists(get_resource_path('docs', f'{get_lang_system_name()}.chm'))):
        wx.MessageBox(f'软件目录下缺少{get_lang_system_name()}语言的文档文件，所以"文档"功能将会显示英文文档\n修复方法：这可能是第三方语言包，需要重新对这个语言包制作html版本文档', get_lang('16'), wx.OK | wx.ICON_WARNING)
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
# 自定义的事件
logger.debug('定义事件')

ID_UPDATE = wx.NewIdRef()
ID_UPDATE_LOG = wx.NewIdRef()
ID_CLEAN_CACHE = wx.NewIdRef()
ID_SETTING = wx.NewIdRef()
ID_DOC = wx.NewIdRef()
ID_MANAGE = wx.NewIdRef()

class SpecialExtensionID:
    '''特殊扩展ID'''
    ID_MANAGE = ID_MANAGE

logger.debug('定义资源')

logger.debug('定义广播完成')
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

logger.debug('加载ui')
# 主窗口绘制和事件监听
class MainWindow(wx.Frame):
    def __init__(self, parent=None):
        # 初始化
        logger.info('初始化主窗口')
        super().__init__(
            parent, 
            title='ClickMouse', 
            size=(400, 350),
            style = wx.DEFAULT_FRAME_STYLE & ~(wx.MAXIMIZE_BOX | wx.RESIZE_BORDER)# 去掉最大化和可调整的窗口大小
        )

        # 状态控制变量
        logger.debug('初始化状态控制变量')
        self.running = False
        self.paused = False
        self.click_thread = None

        # 窗口初始化
        logger.debug('加载图标和标题')
        self.Icon = wx.Icon(str(get_resource_path('icons', 'clickmouse', 'icon.ico')), wx.BITMAP_TYPE_ICO)
        self.Title = 'ClickMouse'

        # 创建面板
        logger.debug('创建面板')
        panel = wx.Panel(self)

        # 面板控件
        logger.debug('创建控件')
        # 标题大字文本
        logger.debug('创建标题大字')
        wx.StaticText(panel, -1, get_lang('0b'), wx.Point(115, 5), style=wx.ALIGN_CENTER).SetFont(wx.Font(20, wx.DEFAULT, wx.NORMAL, wx.BOLD))

        # 定义按钮
        logger.debug('创建按钮')
        self.button_left = wx.Button(panel, label=get_lang('0c'), pos=wx.Point(5, 60), size=wx.Size(100, 50))
        self.button_right = wx.Button(panel, label=get_lang('0d'), pos=wx.Point(280, 60), size=wx.Size(100, 50))
        self.pause_button = wx.Button(panel, label=get_lang('0f'), pos=wx.Point(137, 60), size=wx.Size(100, 40))
        self.stop_button = wx.Button(panel, label=get_lang('0e'), size=wx.Size(100, 40))

        # 定义输入延迟的输入框
        logger.debug('创建输入框')
        self.text_control_tip = wx.StaticText(panel, -1, get_lang('11'), wx.Point(50, 250), style=wx.ALIGN_CENTER).SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        self.delay_input = wx.TextCtrl(panel, value='', pos=wx.Point(150, 245), size=wx.Size(200, 25))

        # 设置布局
        logger.debug('设置布局')
        main_sizer = wx.BoxSizer(wx.VERTICAL) # 主布局
        main_sizer.AddSpacer(50)

        # 按钮的布局
        logger.debug('创建按钮布局')
        # 第一行的布局
        logger.debug('创建第一行布局')
        sizer_h1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_h1.Add(self.button_left, 1, wx.EXPAND | wx.ALL, 5)
        sizer_h1.AddSpacer(150)
        sizer_h1.Add(self.button_right, 1, wx.EXPAND | wx.ALL, 5)

        # 第二行的布局
        logger.debug('创建第二行布局')
        sizer_h2 = wx.BoxSizer(wx.HORIZONTAL)

        self.create_contol_button(sizer_h2, self.pause_button)

        # 第三行的布局
        logger.debug('创建第三行布局')
        sizer_h3 = wx.BoxSizer(wx.HORIZONTAL)
        self.create_contol_button(sizer_h3, self.stop_button)

        # 添加行布局到主布局
        logger.debug('添加行布局到主布局')
        main_sizer.Add(sizer_h1, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(sizer_h2, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(sizer_h3, 0, wx.EXPAND | wx.ALL, 5)
        
        panel.SetSizer(main_sizer) # 设置主布局

        # 创建菜单栏
        logger.debug('创建菜单栏')
        self.create_menu()
        
        # 绑定事件
        logger.debug('绑定事件')
        self.button_left.Bind(wx.EVT_LEFT_DOWN, self.on_mouse_left)
        self.button_right.Bind(wx.EVT_LEFT_DOWN, self.on_mouse_right)
        # 判断更新结果
        self.Bind(wx.EVT_TIMER, self.on_check_update_result)
        self.check_update_timer = wx.Timer(self)
        self.check_update_timer.Start(100)  # 每100ms检查一次

        logger.info('主窗口初始化完成')
        
    def create_menu(self):
        '''创建菜单栏'''
        menubar = wx.MenuBar()

        # 文件菜单
        file_menu = wx.Menu()
        file_menu.Append(ID_CLEAN_CACHE, get_lang('02'))
        
        # 帮助菜单
        help_menu = wx.Menu()
        help_menu.Append(wx.ID_ABOUT, get_lang('0a'))
        # doc = help_menu.Append(ID_DOC, '文档(&D)')
        # if not(is_installed_doc):
        #     doc.Enable(False)
        
        # 更新菜单
        update_menu = wx.Menu()
        update_menu.Append(ID_UPDATE, get_lang('07'))
        update_menu.Append(ID_UPDATE_LOG, get_lang('08'))

        # 设置菜单
        view_menu = wx.Menu()
        view_menu.Append(ID_SETTING, get_lang('05')) 
        
        # 扩展菜单
        extension_menu = wx.Menu()
        offical_extension_menu = wx.Menu()
        extension_menu.AppendSubMenu(offical_extension_menu, '官方扩展(&O)')
        if not any(show_list):
            # 无官方扩展提示
            offical_extension_menu.Append(wx.ID_ANY, '暂无官方扩展').Enable(False)
        else:
            # 加载官方扩展菜单
            for index, id_data, show in zip(indexes, package_id, show_list):
                if show:
                    offical_extension_menu.Append(id_data, get_lang(index)) # 给菜单项添加ID，方便绑定事件
        offical_extension_menu.Append(ID_MANAGE, '管理扩展(&M)')
        
        # 添加菜单到菜单栏
        logger.debug('添加菜单到菜单栏')
        menubar.Append(file_menu, get_lang('01'))
        menubar.Append(view_menu, get_lang('04'))
        menubar.Append(update_menu, get_lang('06'))
        menubar.Append(help_menu, get_lang('09'))
        menubar.Append(extension_menu, '扩展(&X)')
        
        # 绑定事件
        extension_menu.Bind(wx.EVT_MENU, self.on_parse_offical_extension)
        self.Bind(wx.EVT_MENU, self.on_exit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.on_about, id=wx.ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.on_update, id=ID_UPDATE)
        self.Bind(wx.EVT_MENU, self.on_update_log, id=ID_UPDATE_LOG)
        self.Bind(wx.EVT_MENU, self.on_clean_cache, id=ID_CLEAN_CACHE)
        self.Bind(wx.EVT_MENU, self.on_setting, id=ID_SETTING)
        self.Bind(wx.EVT_MENU, self.on_doc, id=ID_DOC)
        
        # 设置菜单栏
        self.SetMenuBar(menubar)
        
    def on_doc(self, event):
        '''打开文档'''
        logger.info('打开文档')
        if is_installed_lang_doc:
            os.startfile(str(get_resource_path('docs', f'{get_lang_system_name()}.chm')))
        else:
            os.startfile(str(get_resource_path('docs', 'en.chm')))
        
    def on_manage_extension(self, event):
        '''管理扩展'''
        logger.info('打开扩展管理窗口')
        run_software('install_pack.py' ,'inst_pks.exe')
        
    def on_check_update_result(self, event):
        '''检查更新结果'''
        global result
        
        # 判断是否需要检查更新
        if should_check_update_res:
            if check_update_thread.is_alive():
                logger.debug('更新检查仍在进行中，忽略')
                return
        else:
            logger.info('距离上次更新检查不到1天，使用缓存')

        # 判断是否需要缓存
        if should_check_update_res:
            result = check_update_thread.result()
        else:
            result = (update_cache['should_update'], update_cache['latest_version'], update_cache['update_info']) # 使用缓存
        # 停止定时器
        self.check_update_timer.Stop()
        
        # 检查结果处理
        if settings.get('update_notify', 0) in {0}: # 判断是否需要弹出通知
            if result[1] != -1:  # -1表示函数出错
                if should_check_update_res:
                    save_update_cache(should_update=result[0], latest_version=result[1], update_info=result[2]) # 缓存最新版本
                if result[0]:  # 检查到需要更新
                    logger.info('检查到更新')
                    # 弹出更新窗口
                    window = UpdateWindow(self)
                    window.ShowModal()
                    window.Destroy()
            else:
                logger.error(f'检查更新错误: {result[0]}')
                wx.MessageBox(f'{get_lang('18')}{result[0]}', get_lang('14'), wx.ICON_ERROR)
        else:
            if result[1] != -1:
                if should_check_update_res:
                    save_update_cache(should_update=result[0], latest_version=result[1], update_info=result[2])

    def on_exit(self, event):
        '''退出程序'''
        logger.info('退出程序')
        self.Close()

    def on_about(self, event):
        '''显示关于窗口'''
        logger.info('显示关于窗口')
        about_dialog = AboutWindow(self)
        about_dialog.ShowModal()
        about_dialog.Destroy()

    def on_update(self, event):
        '''检查更新'''
        logger.info('检查更新')
        if update_cache.get('should_update'):
            window = UpdateWindow(self)
            window.ShowModal()
            window.Destroy()
        else:
            wx.MessageBox(get_lang('19'), get_lang('16'), wx.ICON_INFORMATION)
    
    def on_update_log(self, event):
        '''显示更新日志'''
        logger.info('显示更新日志')
        update_window = UpdateLogWindow(self)
        update_window.ShowModal()
        update_window.Destroy()
    
    def on_mouse_left(self, event):
        logger.info('左键连点')
        # 停止当前运行的点击线程
        if self.click_thread and self.click_thread.is_alive():
            logger.debug('停止当前运行的点击线程')
            self.running = False
            self.click_thread.join()  # 等待线程结束
        
        # 获取新参数并启动左键点击
        delay = self.delay_input.GetValue()
        self.mouse_click(button='left', input_delay=delay)

    def on_mouse_right(self, event):
        # 停止当前运行的点击线程
        logger.info('右键连点')
        if self.click_thread and self.click_thread.is_alive():
            logger.debug('停止当前运行的点击线程')
            self.running = False
            self.click_thread.join()  # 等待线程结束
        
        # 获取新参数并启动右键点击
        delay = self.delay_input.GetValue()
        self.mouse_click(button='right', input_delay=delay)

    def create_contol_button(self, sizer: wx.BoxSizer, button: wx.Button):
        '''创建控制按钮'''
        sizer.AddStretchSpacer()
        sizer.Add(button, 0, wx.ALL, 3)
        sizer.AddStretchSpacer()
    
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
                wx.MessageBox(get_lang('1a'), get_lang('14'), wx.ICON_ERROR)
                logger.error('用户输入错误：请输入有效的正整数延迟')
                return
            else:
                if input_delay == '':
                    delay = int(settings.get('click_delay', ''))
                elif settings.get('failed_use_default', False):
                    delay = int(settings.get('click_delay', ''))
                else:
                    wx.MessageBox(get_lang('1a'), get_lang('14'), wx.ICON_ERROR)
                    logger.error('用户输入错误：请输入有效的正整数延迟')
                    return

        # 创建独立线程避免阻塞GUI
        def click_loop():
            while self.running:
                if not self.paused:
                    try:
                        pyautogui.click(button=button)
                        wx.CallAfter(self.Update)  # 更新GUI
                        sleep(delay/1000)
                    except Exception as e:
                        wx.MessageBox(f'{get_lang('1b')} {str(e)}',get_lang('14'), wx.ICON_ERROR)
                        logger.critical(f'发生错误:{e}')
                        break
                else:
                    sleep(0.1)  # 暂停时降低CPU占用
        
        def on_pause_click(event):
            logger.info('连点器暂停或重启')
            self.paused = not self.paused
            if self.paused:
                self.pause_button.SetLabel(get_lang('10'))
            else:
                self.pause_button.SetLabel(get_lang('0f'))
            # 强制刷新按钮显示
            self.pause_button.Update()

        self.pause_button.Bind(wx.EVT_BUTTON, on_pause_click)

        # 启动线程
        logger.info(f'启动连点线程')
        self.click_thread = threading.Thread(target=click_loop)
        self.click_thread.daemon = True
        self.click_thread.start()

        # 绑定控制按钮
        self.stop_button.Bind(wx.EVT_BUTTON, lambda e: setattr(self, 'running', False))
        self.stop_button.Bind(wx.EVT_BUTTON, lambda e: (
        setattr(self, 'running', False),
        self.pause_button.SetLabel(get_lang('0f'))
    ))
        
    def on_clean_cache(self, event):
        '''清理日志'''
        window = CleanCacheWindow(self)
        window.ShowModal()
        window.Destroy()

    def on_setting(self, event):
        '''设置'''
        logger.info('打开设置窗口')
        setting_window = SettingWindow(self)
        setting_window.ShowModal()
        setting_window.Destroy()

    def on_parse_offical_extension(self, event: wx.CommandEvent):
        '''解析官方扩展'''
        logger.info('打开官方扩展')
        id_num = event.GetId()
        match id_num:
            case 1: # 测试扩展
                run_software(os.path.join(install_location[1], 'hello.py'), None)
            case SpecialExtensionID.ID_MANAGE: # 管理扩展
                self.on_manage_extension(event)

class SettingWindow(uiStyles.old.SelectUI):
    def __init__(self, parent=MainWindow):
        # 初始化
        logger.info('初始化设置窗口')
        self.cache_setting = settings.copy()
        super().__init__(title=filter_hotkey(get_lang('05')), size=(400, 300))
        self.page_titles = [get_lang('42'), get_lang('43'), get_lang('44')]
        self.create_pages()
        self.switch_page(0)
        
        # 创建保存，应用和取消按钮
        # 创建sizer
        save_panel = wx.Panel(self.main_panel)
        save_button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # 创建三个功能按钮
        self.save_btn = wx.Button(save_panel, label=get_lang('3f'))
        self.apply_btn = wx.Button(save_panel, label=get_lang('40'))
        self.cancel_btn = wx.Button(save_panel, label=get_lang('41'))
        
        self.save_btn.Enable(False)  # 初始状态禁用保存按钮
        self.apply_btn.Enable(False)  # 初始状态禁用应用按钮
        
        # 添加按钮到sizer
        save_button_sizer.AddSpacer(50)
        save_button_sizer.Add(self.save_btn, 0, wx.ALL, 0)
        save_button_sizer.AddSpacer(50)
        save_button_sizer.Add(self.apply_btn, 0, wx.ALL, 0)
        save_button_sizer.AddSpacer(50)
        save_button_sizer.Add(self.cancel_btn, 0, wx.ALL, 0)
        
        save_panel.SetSizer(save_button_sizer)
        self.main_sizer.Add(save_panel, 1, wx.ALL | wx.EXPAND, 0)

        # 绑定事件
        self.save_btn.Bind(wx.EVT_BUTTON, self.on_save)
        self.apply_btn.Bind(wx.EVT_BUTTON, self.on_apply)
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.on_cancel)
        self.Bind(wx.EVT_CLOSE, self.on_cancel)
        logger.info('初始化设置窗口完成')
            
    def draw_page(self, index):
        '''根据索引绘制页面内容'''
        match index:
            case 0:
                main_sizer = wx.BoxSizer(wx.VERTICAL)
                self.pages[index].SetSizer(main_sizer)  # 设置内容面板的布局管理器

                # 更新设置内容
                logger.info('加载更新设置页面')
                # 更新设置ui
                lang_list = [i['lang_name'] for i in langs]
                update_setting_sizer = wx.BoxSizer(wx.HORIZONTAL)
                update_setting_sizer.Add(wx.StaticText(self.pages[index], label=get_lang('45'), pos=(0, 10)).SetFont(self.setting_font), 0, wx.ALL, 5)
                self.lang_choice = wx.Choice(self.pages[index], pos=(55, 5), choices=lang_list)
                update_setting_sizer.AddSpacer(50)
                update_setting_sizer.Add(self.lang_choice, 0, wx.ALL, 5)
                self.lang_choice.SetSelection(self.cache_setting.get('select_lang', 0))
                main_sizer.Add(update_setting_sizer, 0, wx.ALL, 5)
                
                # 绑定事件
                self.lang_choice.Bind(wx.EVT_CHOICE, self.on_lang_select_change)  # 绑定选择改变事件
            case 1:
                main_sizer = wx.BoxSizer(wx.VERTICAL)
                self.pages[index].SetSizer(main_sizer)  # 设置内容面板的布局管理器

                # 连点器设置内容
                logger.info('加载连点器设置页面')
                # 连点器设置ui
                default_setting_sizer = wx.BoxSizer(wx.HORIZONTAL)
                default_setting_sizer.Add(wx.StaticText(self.pages[index], label=get_lang('46'), pos=(0, 10)).SetFont(self.setting_font), 1, wx.ALL, 5)
                self.delay_input = wx.TextCtrl(self.pages[index], value=str(self.cache_setting.get('click_delay', '')), pos=(300, 90))
                
                default_setting_sizer.AddSpacer(150)
                default_setting_sizer.Add(self.delay_input, 0, wx.ALL)
                main_sizer.Add(default_setting_sizer, 0, wx.ALL, 5)
                
                self.failed_use_default_sizer = wx.BoxSizer(wx.HORIZONTAL)
                self.failed_use_default = wx.CheckBox(self.pages[index], label=get_lang('47'), pos=(0, 70))
                self.failed_use_default_sizer.Add(self.failed_use_default, 0, wx.ALL | wx.EXPAND, 5)
                self.failed_use_default.SetValue(self.cache_setting.get('failed_use_default', False))
                main_sizer.Add(self.failed_use_default_sizer, 0, wx.ALL | wx.EXPAND, -5)
                
                if self.cache_setting.get('click_delay', '') == '':
                    self.failed_use_default.Enable(False) # 禁用失败默认值选择框
                else:
                    self.failed_use_default.Enable(True) # 启用失败默认值选择框

                # 绑定事件
                self.delay_input.Bind(wx.EVT_TEXT, self.on_input_change)  # 绑定输入改变事件
                self.failed_use_default.Bind(wx.EVT_CHECKBOX, self.on_failed_use_default_change)  # 绑定选择改变事件
            case 2:
                main_sizer = wx.BoxSizer(wx.VERTICAL)
                self.pages[index].SetSizer(main_sizer)  # 设置内容面板的布局管理器

                # 更新设置内容
                logger.info('加载更新设置页面')
                # 更新设置ui
                update_setting_sizer = wx.BoxSizer(wx.HORIZONTAL)
                update_setting_sizer.Add(wx.StaticText(self.pages[index], label=get_lang('48'), pos=(0, 10)).SetFont(self.setting_font), 0, wx.ALL, 5)
                choice = wx.Choice(self.pages[index], pos=(55, 5), choices=[get_lang('49'), get_lang('4a')])
                update_setting_sizer.AddSpacer(50)
                update_setting_sizer.Add(choice, 0, wx.ALL, 5)
                choice.SetSelection(self.cache_setting.get('update_notify', 0))
                main_sizer.Add(update_setting_sizer, 0, wx.ALL, 5)
                
                # 绑定事件
                choice.Bind(wx.EVT_CHOICE, self.on_choice_change)  # 绑定选择改变事件

    def get_lang_after_setting(self, lang_package_id):
        return get_lang(lang_package_id, self.cache_setting.get('select_lang', 0))

    def on_choice_change(self, event):
        self.on_change(event, 'update_notify', 0, event.GetSelection)
        
    def on_lang_select_change(self, event):
        global settings
        
        self.on_change(event, 'select_lang', 0, event.GetSelection)
        
        if event.GetSelection() == settings.get('select_lang', 0):
            return  # 选择相同的语言，不作处理

        lang_restart = uiStyles.MoreButtonDialog(self, self.get_lang_after_setting('16'), self.get_lang_after_setting('4f'), [self.get_lang_after_setting('1e'), self.get_lang_after_setting('4b')], uiStyles.Style.WARNING, wx.DEFAULT_DIALOG_STYLE & ~(wx.CLOSE_BOX))
        result = lang_restart.ShowModal()
        if result == 1:
            self.on_change(event, 'select_lang', 0, settings.get, ('select_lang', 0)) # 恢复选择框
            self.lang_choice.SetSelection(settings.get('select_lang', 0)) # 恢复选择框
            return  # 取消关闭操作
        
    def on_input_change(self, event):
        new_value = event.GetString # 获取输入值 
        if new_value() == '': # 输入为空
            self.failed_use_default.Enable(False) # 禁用失败默认值选择框
        else:
            self.failed_use_default.Enable(True) # 启用失败默认值选择框
        self.on_change(event, 'click_delay', '', new_value)
            
    def on_failed_use_default_change(self, event):
        self.on_change(event, 'failed_use_default', False, event.IsChecked)
    
    def on_change(self, event, key, default_value, event_handler, args=()):
        new_value = event_handler(*args) # 获取输入值 
        self.cache_setting[key] = new_value # 更新缓存设置
        
        temp_cache_setting = self.cache_setting.copy() # 临时缓存设置
        try:
            temp_cache_setting['click_delay'] = int(temp_cache_setting['click_delay']) # 尝试转换为整数
        except:
            pass

        if temp_cache_setting == settings:
            self.save_btn.Enable(False)
            self.apply_btn.Enable(False)
        else:
            self.save_btn.Enable(True)
            self.apply_btn.Enable(True)
        event.Skip()
        
    def on_save(self, event):
        global settings
        if self.on_apply(event) != -1:
            self.Destroy()
        else:
            return -1

    def on_apply(self, event):
        '''应用按钮事件'''
        global settings
        try:
            if self.cache_setting.get('click_delay', '') != '':
                self.cache_setting['click_delay'] = int(self.cache_setting['click_delay'])
        except ValueError:
            wx.MessageBox(get_lang('51'), get_lang('14'), wx.ICON_ERROR)
            logger.error(f'用户输入错误：请输入有效的正整数延迟')
            return -1
        settings.update(self.cache_setting)
        save_settings(settings)
        self.save_btn.Enable(False)
        self.apply_btn.Enable(False)

    def on_cancel(self, event):
        '''取消按钮事件'''
        global settings
        try:
            if self.cache_setting.get('click_delay', '') != '':
                self.cache_setting['click_delay'] = int(self.cache_setting['click_delay'])
        except ValueError as e:
            wx.MessageBox(get_lang('51'), get_lang('14'), wx.ICON_ERROR)
            logger.error(f'用户输入错误：请输入有效的正整数延迟')
            return # 取消关闭操作

        if self.cache_setting != settings:
            dlg = wx.MessageDialog(self, 
                get_lang('52'),
                get_lang('53'),
                wx.YES_NO | wx.CANCEL | wx.ICON_WARNING)
            result = dlg.ShowModal()
            if result == wx.ID_YES:
                if self.on_save(event) == -1:
                    return  # 保存失败，取消关闭操作
            elif result == wx.ID_CANCEL:
                return  # 取消关闭操作
        self.Destroy()

logger.debug('加载ui完成')
# 显示窗口
def main(app_name=MainWindow):
    frame = app_name()
    frame.Show()
    app.MainLoop()

def command():
    '''
    ClickMouse命令行工具的函数
    '''
    print('ClickMouse命令行工具未实现，敬请期待')

if __name__ == '__main__':
    logger.info('加载完成')
    if argv[1:]:
        # 调用命令行工具
        command()
    else:
        # 调用GUI工具
        if not(data_path / 'first_run').exists():
            run_software('init.py', 'cminit.exe')
        else:
            app = wx.App()
            is_installed_doc, is_installed_lang_doc = (False, False)# check_doc_exists()
            # with open('packages.json', 'r', encoding='utf-8') as f:
            #     packages = json.load(f)

            package_list, indexes, install_location, package_id, show_list = get_packages()

            main(SettingWindow)
            app.MainLoop()
            logger.info('程序退出')