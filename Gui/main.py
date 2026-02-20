# 加载ui框架
from PySide6.QtWidgets import QApplication
import sys
app = QApplication(sys.argv)
from uiStyles.QUI import *

from datetime import datetime # 检查时间
from uiStyles import (SelectUI, UCheckBox, UMessageBox, MessageButtonTemplate) # 软件界面样式
from pynput import keyboard # 热键功能库
from sharelibs import (get_lang)

# TODO: 添加更新设置，使用hashlib.algorithms_available获取支持的hash算法

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
    
    
def filter_hotkey(text:str):
    return text.split('(')[0]

def load_update_cache():
    '''
    加载更新缓存文件
    '''
    logger.info('加载更新缓存')
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
    last_check_time = update_cache.get('last_check_time')
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
    if len(list1) != len(list2):
        return False
    return all(item in list2 for item in list1)

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

def get_soft_size():
    '''
    获取软件大小
    '''
    size = 0
    for root, dirs, files in os.walk(Path.cwd()): # 遍历文件
        for file in files:
            size += os.path.getsize(os.path.join(root, file))
    return size // 1024 # 单位KB

def on_update_setting_window():
    global setting_window
    if setting_window.isVisible():
        page = setting_window.now_page
        if page is None:
            page = 0
        values = setting_window.values.copy()
        setting_window.close()
        print(values)
        setting_window = SettingWindow(values)
        setting_window.click_setting_changed.connect(lambda: on_input_change(type='main'))
        setting_window.window_restarted.connect(on_update_setting_window)
        setting_window.on_page_button_clicked(page)
        setting_window.show()

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
    
def get_hotkey_listener_instance():
    '''获取全局唯一的 HotkeyListener 实例'''
    if not hasattr(get_hotkey_listener_instance, "instance"):
        global hotkey_thread # 驻留线程，防止自动销毁
        get_hotkey_listener_instance.instance = HotkeyListener()
        logger.info('启动热键监听器')
        # 在后台线程中启动热键监听
        hotkey_thread = QtThread(get_hotkey_listener_instance.instance.start_listening)
        hotkey_thread.start()
    return get_hotkey_listener_instance.instance

def parse_hotkey(hotkey_str: str, default_keys):
    '''解析热键字符串'''
    return settings.get(hotkey_str + '_hotkey', default_keys)

def revert_update():
    '''回滚更新'''
    logger.info('回滚更新')
    try:
        os.rename('updater.old', 'updater')
    except:
        pass
    try:
        os.remove('updater/clickmouse.7z')
    except:
        pass

def on_input_change(*, type:str ):
    '''输入延迟改变'''
    # 判断参数有效性
    if type == 'main':
        global is_inf, is_error, delay_num, time_num
        delay_text = main_window.input_delay
        delay_times = main_window.input_times
        times_combo = main_window.times_combo
        delay_combo = main_window.delay_combo
        total = main_window.total_time_label
        delay_num = settings.get('click_delay', '')
        time_num = settings.get('click_times', '')
        is_error = False
    elif type =='setting':
        delay_text = setting_window.default_delay
        delay_times = setting_window.default_time
        total = setting_window.total_time_label
        times_combo = setting_window.times_combo
        delay_combo = setting_window.delay_combo
        setting_window.click_setting_changed.emit()
    input_delay = delay_text.text().strip()
    input_times = delay_times.text().strip()
    is_inf = False
    delay = 0

    delay_times.setEnabled(not(times_combo.currentIndex() == latest_index or (settings.get('times_unit', 0) == latest_index) and type == 'main'))

    if times_combo.currentIndex() == latest_index or input_times == '0': 
        is_inf = True
    if settings.get('times_unit', 0) == latest_index and type == 'main':
        is_inf = True
        
    def on_delay_error(error_text=get_lang('14')):
        '''输入延迟错误'''
        total.setText(f'{get_lang('2c')}: {error_text}')
        if type == 'main':
            global is_error

            main_window.right_click_button.setEnabled(False)
            main_window.left_click_button.setEnabled(False)
            is_error = True

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
            if type == 'main':
                on_delay_error(get_lang('60'))
            else:
                on_delay_error()
            return False
    
    try:
        delay = math.ceil(float(input_delay))
        if delay < 1:
            raise ValueError
    except ValueError:
        if not settings.get('click_delay', '') == '':
            if input_delay == '':
                if check_default_var('delay'):
                    delay = int(settings.get('click_delay', ''))
                else:
                    return
            elif settings.get('failed_use_default', False):
                if check_default_var('delay'):
                    delay = int(settings.get('click_delay', ''))
                else:
                    return
            else:
                on_delay_error()
                return
    except Exception:
        on_delay_error()
        return

    if not is_inf:
        try:
            times = math.ceil(float(input_times))
            if times < 1:
                raise ValueError
        except ValueError:
            if settings.get('click_times', '') == '' and settings.get('click_delay', '') == '':
                on_delay_error(get_lang('61'))
                return
            else:
                if input_times == '':
                    if check_default_var('times'):
                        times = int(settings.get('click_times', ''))
                    else:
                        return
                elif settings.get('times_failed_use_default', False):
                    if check_default_var('times'):
                        times = int(settings.get('click_times', ''))
                    else:
                        return
                else:
                    on_delay_error()
                    return
        except Exception:
            on_delay_error()
            return

    if type == 'main':
        main_window.right_click_button.setEnabled(True)
        main_window.left_click_button.setEnabled(True)
        is_error = False

    if settings.get('click_delay', '') != '' and input_delay == '':
        match settings.get('delay_unit', 0):
            case 0:
                delay_num = delay
            case 1:
                delay_num = delay * 1000
    else:
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
        if type == 'main':
            if delay_num == 0:
                on_delay_error()
    else:
        if settings.get('click_times', '') != '' and input_times == '':
            match settings.get('times_unit', 0):
                case 0:
                    time_num = times
                case 1:
                    time_num = times * 10000
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

        if (delay_num == 0 and time_num != 0) or (delay_num != 0 and time_num == 0):
            on_delay_error()
            return

        total_run_time = get_unit_value(delay_num * time_num)
        total.setText(f'{get_lang('2c')}: {total_run_time[0]}{total_run_time[1]}')
        
class UMainWindow(QMainWindow):
    '''自定义窗口基类'''
    def __init__(self, parent=None):
        logger.debug('初始化主窗口')

        super().__init__(parent=parent)
        self.setWindowIcon(icon)
        new_color_bar(self)
        
    def showEvent(self, event):
        '''窗口显示事件'''
        new_color_bar(self)
        return super().showEvent(event)
    
class UDialog(QDialog):
    '''自定义对话框基类'''
    def __init__(self, parent=None):
        logger.debug('初始化对话框')

        super().__init__(parent=parent)
        self.setWindowIcon(icon)
        new_color_bar(self)
    
    def showEvent(self, event):
        '''窗口显示事件'''
        new_color_bar(self)
        return super().showEvent(event)

class StartManager(QObject):
    '''开机自启动管理器'''
    updated = Signal(bool)
    def __init__(self):
        super().__init__()
        self.app_name = 'clickmouse.lnk'
        self.status_path = r'Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\StartupFolder'
        self.create_reg()
        self.auto_start = self.is_enabled()

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_value)
        self.timer.start(settings.get('soft_delay', 1))

    def create_reg(self):
        '''检查是否已启用开机自启动'''
        start_path = Path(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup', self.app_name)
        if not(start_path.exists()):
            create_shortcut(str(start_path), str(Path.cwd() / 'main.exe'), 'ClickMouse', work_dir=str(Path.cwd()))
            self.disable()

    def is_enabled(self):
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.status_path, 0, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, self.app_name)

            return value[0] == 2
        except FileNotFoundError:
            return False

    def check_value(self):
        '''检查注册表值是否最新'''
        new_value = self.is_enabled()
        if new_value != self.auto_start:
            self.auto_start = new_value
            self.updated.emit(self.auto_start)

    def enable(self):
        '''启用开机自启动'''
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                            self.status_path, 0, winreg.KEY_WRITE) as key:
            winreg.SetValueEx(key, self.app_name, 0, winreg.REG_BINARY, bytes([0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]))

    def disable(self):
        '''禁用开机自启动''' 
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                            self.status_path, 0, winreg.KEY_WRITE) as key:
            winreg.SetValueEx(key, self.app_name, 0, winreg.REG_BINARY, bytes([0x03, 0x00, 0x00, 0x00]) + get_now_filetime())

class MessageBox(UMessageBox):
    @staticmethod
    def new_msg(parent, 
                title: str, 
                text: str, 
                icon: QMessageBox.Icon, 
                buttons: MessageButtonTemplate = MessageButtonTemplate.OK,
                defaultButton: MessageButtonTemplate = MessageButtonTemplate.OK):

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
        
class UHotkeyLineEdit(QLineEdit):
    '''能够捕获热键组合的输入框，只有获得焦点时才更新'''
    def __init__(self, parent=None):
        super().__init__(parent)
        self._connection = None  # 保存信号连接对象
        self.key_list = []  # 保存按下的热键
        self.setReadOnly(True)
        self.listener = get_hotkey_listener_instance()

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
        
class UFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        set_style(self, 'frame')

class HotkeyListener(QObject):
    '''热键监听器类，用于在后台线程中监听全局热键'''
    combination_pressed = Signal(list)  # 新增信号，用于发送组合键信息

    def __init__(self):
        super().__init__()
        self.listener = None
        self.is_listening = False
        self.clicked_keys = set()  # 用于跟踪当前按下的键

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

    def mouse_left(self, delay, times):
        logger.info('左键连点')
        if not self.running:
            self.mouse_click(button='left', input_delay=delay, times=times)

    def mouse_right(self, delay, times):
        # 停止当前运行的点击线程
        logger.info('右键连点')
        if not self.running:
            self.mouse_click(button='right', input_delay=delay, times=times)

    def set_default_clicked(self):
        self.left_clicked = False
        self.right_clicked = False
        self.click_changed.emit(self.left_clicked, self.right_clicked)

    def mouse_click(self, button: str, input_delay, times):
        '''鼠标连点'''
        logger.info('开始连点')
        # 重置状态
        if self.click_thread and self.click_thread.isRunning():
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
            delay = math.ceil(float(input_delay))
        except Exception:
            trace = format_exc()
            MessageBox.critical(None, get_lang('14'), f'{get_lang('1b')}\n{trace}')
            logger.exception('连点服务', trace)
            return

        # 创建独立线程避免阻塞GUI
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
                        pyautogui.click(button=button)
                        sleep(delay / 1000)
                        i += 1     
                        if times == float('inf'):
                            self.click_conuter.emit('inf', str(i), str(delay))
                        else:
                            self.click_conuter.emit(str(times), str(i), str(delay))
                    except Exception:
                        trace = format_exc()
                        MessageBox.critical(None, get_lang('14'), f'{get_lang('1b')}\n{trace}')
                        logger.exception('连点服务', trace)

                        self.stopped.emit()
                        break
                else:
                    sleep(delay / 1000)  # 暂停
            else:
                self.stopped.emit()

        # 启动线程
        logger.info(f'启动连点线程')
        self.started.emit()
        self.click_thread = QtThread(click_loop)
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
        logger.info('运行刷新服务')
        self.do_step(self.steps)

    def do_step(self, codes):
        # 尝试执行代码
        for code in codes:
            logger.debug(f'执行步骤{code.__name__}')
            try:
                code()
                logger.debug(f'步骤{code.__name__}执行成功')
            except NameError as e:
                logger.warning(f'步骤{code.__name__}操作存在未定义:{e}')
            except Exception as e:
                logger.error(f'步骤{code.__name__}执行失败:{e}')

    def refresh_title(self):
        QTimer.singleShot(settings.get('soft_delay', 100), color_getter.style_changed.emit)

    def left_check(self):
        if clicker.left_clicked:
            set_style(main_window.left_click_button, 'selected')
        else:
            logger.debug('左键未连点')
            set_style(main_window.left_click_button, '')

    def right_check(self):
        if clicker.right_clicked:
            set_style(main_window.right_click_button,'selected')
        else:
            logger.debug('右键未连点')
            set_style(main_window.right_click_button, '')

class RunAfter:
    def __init__(self):
        self.program_list = {}

    def add(self, name, python_path, exe_path, run_as_admin=False):
        logger.debug('添加计划')
        self.program_list[name] = (python_path, exe_path, run_as_admin)
        MessageBox.information(main_window, get_lang('59'), get_lang('5a'))

    def remove(self, name):
        logger.debug('移除计划')
        del self.program_list[name]
        MessageBox.information(main_window, get_lang('59'), get_lang('88'))

    def run(self):
        logger.info('运行运行计划')
        for python_path, exe_path, use_admin in self.program_list.values():
            if use_admin:
                run_as_admin(python_path, exe_path)
            else:
                run_software(python_path, exe_path)

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
            QMessageBox.critical(None, get_lang('14'), get_lang('12'))
            logger.critical('设置的样式索引超出范围，已恢复默认样式设置。')
            run_software('main.py', 'main.exe')
            sys.exit(0)

        # 加载刷新服务
        refresh = Refresh()

        # 初始化时应用一次主题
        self.apply_global_theme()

        # 使用定时器定期检测主题变化
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_and_apply_theme)
        self.timer.start(settings.get('soft_delay', 1))

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
        refresh.run()

    def apply_titleBar(self, window: QMainWindow | QDialog):
        '''应用标题栏样式'''
        logger.debug('应用标题栏样式')

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
                select_styles = select_styles.replace(['.selected:pressed', 'color'], StyleReplaceMode.ALL, 'black', output_json=False)
                select_styles = select_styles.replace(['QCheckBox', 'color'], StyleReplaceMode.ALL, 'black', output_json=False)
            else:
                select_styles = select_styles.replace(['.selected', 'background-color'], StyleReplaceMode.ALL, self.windows_color, output_json=False)
                select_styles = select_styles.replace(['.selected:hover', 'background-color'], StyleReplaceMode.ALL, lighten_color_hex(self.windows_color, 0.4), output_json=False)
            select_styles = select_styles.replace(['.selected:pressed', 'background-color'], StyleReplaceMode.ALL, lighten_color_hex(self.windows_color, -0.165), output_json=False)

        app.setStyleSheet(select_styles.css_text)  # 全局应用
        self.refresh()

class MainWindow(UMainWindow):
    def __init__(self):
        logger.debug('初始化主窗口')

        super().__init__()
        self.setWindowTitle('ClickMouse')
        self.setGeometry(100, 100, 500, 375)
        self.setWindowFlags(
            Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint
        ) # 设置窗口属性

        self.setFixedSize(self.width(), self.height()) # 固定窗口大小

        logger.debug('初始化状态控制变量')
        self.show_update_in_start = False # 是否在启动时显示更新提示
        self.total_run_time = 0  # 总运行时间
        self.is_ready = True  # 是否状态栏为“就绪”
        self.is_start_from_tray = False # 是否从托盘启动

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
        set_style(title, 'big_text_24')
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
        set_style(self.total_time_label, 'big_text_16')
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

        self.input_delay.textChanged.connect(lambda: on_input_change(type='main'))
        self.input_times.textChanged.connect(lambda: on_input_change(type='main'))
        self.delay_combo.currentIndexChanged.connect(lambda: on_input_change(type='main'))
        self.times_combo.currentIndexChanged.connect(lambda: on_input_change(type='main'))

        self.status_bar.messageChanged.connect(self.reload_status)

        # 创建菜单栏
        logger.debug('创建菜单栏')
        self.create_menu_bar()

        # 刷新按钮状态
        logger.debug('刷新按钮状态')

        logger.debug('初始化完成')

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
        create_issue_action = help_menu.addAction(get_lang('ba'))

        # 文档菜单
        doc = help_menu.addAction(get_lang('5f'))
        doc.triggered.connect(self.open_doc)

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

        # not_official_extension_menu = extension_menu.addMenu(get_lang('93'))

        # cge_menu = not_official_extension_menu.addMenu(get_lang('94'))
        # cge_menu.addAction(get_lang('95')).setDisabled(True)

        # cmm_menu = not_official_extension_menu.addMenu(get_lang('96'))
        # cmm_menu.addAction(get_lang('97')).setDisabled(True)

        # not_official_extension_menu.addSeparator()

        # not_official_extension_menu.addAction(get_lang('98')).triggered.connect(self.show_import_extension_mode) # 管理扩展菜单
        # not_official_extension_menu.addAction(get_lang('92')).triggered.connect(self.show_manage_not_official_extension) # 管理扩展菜单

        # 宏菜单
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
        create_issue_action.triggered.connect(lambda: open_url('https://github.com/xystudiocode/pyClickMouse/issues/new/choose'))
        
    def open_doc(self, *, path: str=''):
        '''打开文档'''
        lang_name = langs[select_lang]['lang_system_name']
        with open(get_resource_path('vars', 'supported_doc_lang.json'), 'r', encoding='utf-8') as f:
            supported_doc_lang = json.load(f)
        if lang_name in supported_doc_lang: # 受支持的语言包
            open_url(f'https://xystudiocode.github.io/clickmouse_docs/{lang_name}/{path}')
        else:
            open_url(f'https://xystudiocode.github.io/clickmouse_docs/en/path')

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
            logger.exception('扩展运行服务', trace)

    def show_manage_extension(self):
        '''管理扩展'''
        logger.info('打开扩展管理窗口')

        run_software('install_pack.py' ,'install_pack.exe', ['--ipk'])

    def show_import_extension_mode(self):
        '''导入扩展模式'''
        logger.info('打开导入扩展窗口')
        set_import_extension_window.exec()

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
            except Exception:
                trace = format_exc()
                MessageBox.critical(self, get_lang('a1'), get_lang('a5').format(trace))
                logger.exception('导入扩展', trace)
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
            except Exception:
                trace = format_exc()
                logger.exception('导入扩展', trace)
                MessageBox.critical(self, get_lang('a1'), get_lang('a5').format(trace))
                return
        else:
            return

    def show_about(self):
        '''显示关于窗口'''
        logger.info('打开关于窗口')
        about_window.exec()

    def show_update_log(self):
        '''显示更新日志'''
        logger.info('打开更新日志窗口')
        self.open_doc(path='updatelog')

    def show_clean_cache(self):
        '''清理缓存'''
        logger.info('打开清理缓存窗口')
        clean_cache_window.exec()

    def show_setting(self):
        '''显示设置窗口'''
        logger.info('打开设置窗口')
        setting_window.show()

    def on_check_update(self):
        # 检查更新
        self.update_checked = True
        if should_check_update_res:
            self.check_update_thread = QtThread(check_update, args=(False,))
            self.check_update_thread.finished.connect(self.on_check_update_result)
            self.check_update_thread.start()
        else:
            logger.info('使用缓存检查更新')
            self.on_check_update_result(update_cache)
            
    def save(self):
        '''保存更新缓存'''
        if should_check_update_res:
            save_update_cache(should_update=result[0], latest_version=result[1], update_info=result[2], hash=result[3], update_version_tag=result[4]) # 缓存最新版本

    def on_check_update_result(self, check_data):
        '''检查更新结果'''
        global result

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
        if settings.get('update_notify', 0) in {0}: # 判断是否需要弹出通知
            if result[1] != -1:  # -1表示函数出错
                self.save()
                if result[0]:  # 检查到需要更新
                    logger.info('检查到更新')
                    # 弹出更新窗口
                    self.show_update_in_start = True
                    if should_check_update_res:
                        # 弹出更新提示
                        self.on_update()
            else:
                if self.check_update_thread.isFinished():
                    logger.error(f'检查更新错误:\n{result[0]}')
                    MessageBox.critical(self, get_lang('14'), f'{get_lang('18')}\n{result[0]}')
        else:
            if result[1] != -1:
                self.save()

    def on_update(self, judge = False):
        '''显示更新提示'''
        if judge:
            if result[0]: # 检查到需要更新
                self.open_update()
            else:
                MessageBox.information(self, get_lang('16'), get_lang('19'))
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
        logger.info('停止连点')

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
            self.right_click_button.setEnabled(False)
            self.left_click_button.setEnabled(True)
        elif right:
            # 右键点击
            set_style(self.right_click_button, 'selected')
            set_style(self.left_click_button, '')
            self.right_click_button.setEnabled(True)
            self.left_click_button.setEnabled(False)
        else:
            # 未点击
            set_style(self.left_click_button, '')
            set_style(self.right_click_button, '')
            self.right_click_button.setEnabled(True)
            self.left_click_button.setEnabled(True)

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

class AboutWindow(UDialog):
    def __init__(self):
        super().__init__()
        logger.debug('初始化关于窗口')
        self.setWindowTitle(filter_hotkey(get_lang('0a')))
        self.setGeometry(100, 100, 375, 175)
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
        self.image_label.setPixmap(icon.pixmap(64, 64))

        # 版本信息
        version_status_text = get_lang('65') if is_pre else ''
        version = QLabel(get_lang('1c').format(__version__, version_status_text))
        about = QLabel(get_lang('1d'))

        # 按钮
        logger.debug('创建按钮')
        ok_button = QPushButton(get_lang('1e'))
        set_style(ok_button, 'selected')

        # 布局
        central_layout.addWidget(self.image_label, 0, 0, 1, 1)
        central_layout.addWidget(version, 0, 1, 1, 2)
        central_layout.addWidget(about, 2, 0, 1, 3)
        central_layout.addWidget(ok_button, 3, 2)

        self.setLayout(central_layout)

        # 绑定事件
        logger.debug('绑定事件')
        ok_button.clicked.connect(self.close)
        logger.debug('初始化关于窗口完成')

class CleanCacheWindow(UDialog):
    def __init__(self):
        logger.debug('初始化清理缓存窗口')
        super().__init__()
        self.setWindowTitle(filter_hotkey(get_lang('02')))

        # 加载常量
        logger.debug('加载常量')
        self.locked_checkbox = False # 锁定选择框模式，按下后将不会产生来自非手动操作的更新选择框
        # 清理缓存
        logger.debug('加载清理项')
        with open(get_resource_path('vars', 'caches.json'), 'r', encoding='utf-8') as f:
            self.cache_config = json.load(f)
        self.path_list = [i['path'] for i in self.cache_config if i['path']]
        self.cache_config[-1]['exclude'] = self.merge_lists_dicts(*self.path_list)

        self.init_ui()

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
            checkbox.checkStateChanged.connect(self.update_all_check_status)

        # 设置布局
        logger.debug('设置布局')

        self.setLayout(layout)

        logger.debug('清理缓存窗口初始化完成')

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
        cache_size = self.calc_cache_size()
        total_size = 0
        for text, cache in zip(self.cache_size_list, cache_size):
            if cache is not None:
                text.setText(get_size_text(cache))
                total_size += cache

        self.all_size_text.setText(get_size_text(total_size))

    def try_to_remove_file(self, file_path: str):
        '''尝试删除文件'''
        try:
            size = self.get_dir_or_file_size(file_path)
            os.remove(file_path)
            return size
        except:
            return 0

    def delete_empty_folders(self, root_path):
        '''
        删除所有空文件夹（包括嵌套的空文件夹）
        '''
        if not os.path.exists(root_path) or not os.path.isdir(root_path):
            return

        # 标记是否删除了任何文件夹
        deleted_any = False

        # 递归处理子文件夹
        for item in os.listdir(root_path):
            item_path = os.path.join(root_path, item)
            if os.path.isdir(item_path):
                if self.delete_empty_folders(item_path):
                    deleted_any = True

        # 检查当前文件夹是否为空
        try:
            items = os.listdir(root_path)
        except PermissionError:
            return deleted_any

        # 如果为空则删除
        if len(items) == 0:
            try:
                os.rmdir(root_path)
                return True
            except OSError:
                pass

        return deleted_any

    def on_clean_cache(self):
        '''清理缓存'''
        logger.info('清理缓存')

        cache_clicked = list(map(lambda x: x.isChecked(), self.checkbox_list))
        cache_size = 0

        for i in self.cache_config:
            if cache_clicked[i['check_index']]: # 选择了该项
                if i['path'] is not None: # 是否全选
                    for items in chain(i['path']['dirs'], i['path']['files']):
                        cache_size += self.try_to_remove_file(cache_path / items)  
                else:
                    for root, dirs, files in os.walk(cache_path):
                        for file in files:
                            if file in i['exclude']['files'] or self.contains_substring(i['exclude']['dirs'], root):
                                continue
                            cache_size += self.try_to_remove_file(os.path.join(root, file))
        # 清理空文件夹
        for root, dirs, files in os.walk(cache_path):
            for dir in dirs:
                self.delete_empty_folders(os.path.join(root, dir))

        # 弹出提示窗口
        MessageBox.information(self, get_lang('16'), get_lang('3b').format(get_size_text(cache_size)))

    def get_dir_or_file_size(self, dir_or_file_path: str) -> int:
        '''获取目录或文件大小'''
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

    def calc_cache_size(self) -> list:
        '''扫描缓存'''
        logger.info('计算缓存大小')

        cache_clicked = list(map(lambda x: x.isChecked(), self.checkbox_list))
        every_cache_size = [None for _ in cache_clicked]

        for i in self.cache_config:
            if cache_clicked[i['check_index']]: # 选择了该项
                if i['path'] is not None: # 是否全选
                    for items in chain(i['path']['dirs'], i['path']['files']):
                        every_cache_size[i['check_index']] = self.get_dir_or_file_size(cache_path / items)
                else:
                    size = 0
                    for root, dirs, files in os.walk(cache_path):
                        for file in files:
                            if file in i['exclude']['files'] or self.contains_substring(i['exclude']['dirs'], root):
                                continue
                            size += self.get_dir_or_file_size(os.path.join(root, file))
                    every_cache_size[i['check_index']] = size

        return every_cache_size

    def on_check(self, state):
        '''全选按钮点击事件'''
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
        logger.debug('初始化更新窗口')
        super().__init__()
        self.setWindowTitle(get_lang('29'))
        self.setGeometry(100, 100, 300, 110)
        self.setFixedSize(self.width(), self.height())
        self.setWindowIcon(icon)

        self.init_ui()
        self.down_thread = None # 下载线程

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

        logger.debug('初始化更新窗口完成')

    def on_update(self):
        '''更新'''
        try:
            self.close()
            os.rename('updater', 'updater.old')
            self.down_thread = QtThread(download_file, args=(web_data['down_web'].format(latest_version=result[4]), 'updater.old/clickmouse.7z'))
            self.down_thread.finished.connect(self.on_update_finished)
            self.down_thread.start()
        except:
            trace = format_exc()
            logger.exception('更新安装', trace)
            revert_update()
            MessageBox.critical(self, get_lang('14'), f'更新安装失败：\n{trace}')
            
    def on_update_finished(self, state):
        '''更新完成'''
        global can_update
        if state[0]:
            hash_info = result[3]
            if get_file_hash('updater.old/clickmouse.7z', hash_info[1]) == hash_info[0]:
                can_update = True
                update_ok = UpdateOKWindow()
                update_ok.show()
            else:
                logger.exception('更新安装', '文件校验失败')
                QMessageBox.critical(self, get_lang('14'), '更新包校验失败')
        else:
            logger.exception('更新安装', state[1])
            QMessageBox.critical(self, get_lang('14'), f'更新失败:\n{state[1]}')

    def on_open_update_log(self):
        # 打开更新日志
        logger.debug('打开更新日志')

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
        logger.debug('创建面板')
        layout = QVBoxLayout()

        # 面板控件
        logger.debug('创建面板控件')
        title = QLabel(get_lang('b3'))
        tip = QLabel(get_lang('b8'))

        set_style(title, 'big_text_16')

        # 按钮
        update = QPushButton(get_lang('7e')) # 更新按钮
        set_style(update, 'selected')
        update_log = QPushButton(get_lang('27')) # 查看更新日志按钮
        revert = QPushButton(get_lang('6a')) # 回滚更新按钮
        cancel = QPushButton(get_lang('1f')) # 取消按钮

        bottom_layout = QHBoxLayout()
        # 绑定事件
        logger.debug('绑定事件')
        update.clicked.connect(self.on_update)
        revert.clicked.connect(self.on_revert)
        update_log.clicked.connect(self.on_open_update_log)
        cancel.clicked.connect(self.close)

        # 布局
        logger.debug('布局')
        layout.addWidget(title)
        layout.addWidget(tip)

        bottom_layout.addStretch()
        bottom_layout.addWidget(update)
        bottom_layout.addWidget(update_log)
        bottom_layout.addWidget(revert)
        bottom_layout.addWidget(cancel)

        layout.addLayout(bottom_layout)

        self.setLayout(layout)

        logger.debug('初始化更新窗口完成')

    def on_update(self):
        '''更新'''
        run_software('updater.old/updater.py', 'updater.old/updater.exe')
        sys.exit(0)
        
    def on_revert(self):
        '''回滚'''
        global can_update
        logger.info('回滚更新')
        revert_update()
        self.close()
        can_update = False
        MessageBox.information(self, get_lang('16'), get_lang('b9'))

    def on_open_update_log(self):
        # 打开更新日志
        update_window.on_open_update_log()

class FastSetClickWindow(UDialog):
    def __init__(self):
        logger.debug('初始化快速连点窗口')

        super().__init__()
        self.setWindowTitle(get_lang('75'))
        self.setGeometry(100, 100, 475, 125)
        self.setWindowFlags(
            Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint
        ) # 设置窗口属性

        self.setFixedSize(self.width(), self.height()) # 固定窗口大小

        logger.debug('初始化状态控制变量')
        self.total_run_time = 0  # 总运行时间

        logger.debug('初始化ui')
        self.init_ui()

    def init_ui(self):
        # 创建主控件和布局
        central_layout = QVBoxLayout()

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
        self.total_time_label = QLabel(main_window.total_time_label.text())
        self.total_time_label.setAlignment(Qt.AlignHCenter)
        set_style(self.total_time_label, 'big_text_16')

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

        logger.debug('初始化快速连点窗口完成')

    def sync_input(self, get_handle, set_handle, source, dest):
        '''同步输入框'''
        set_handle(dest, get_handle(source))

class ClickAttrWindow(UDialog):
    def __init__(self):
        logger.debug('初始化连点器属性窗口')
        super().__init__()
        self.setWindowTitle(get_lang('8c'))

        # 定义变量
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_attr)
        self.timer.start(settings.get('soft_delay', 1))

        self.init_ui()

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

        logger.debug('初始化连点器属性窗口完成')

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

    def __init__(self, values:dict | None = None):
        super().__init__()

        logger.debug('初始化设置窗口')
        self.setGeometry(300, 300, 625, 400)
        self.setFixedSize(self.width(), self.height())
        self.setWindowTitle(filter_hotkey(get_lang('04')))
        self.setParent(main_window)
        self.setWindowIcon(icon)
        self.setWindowFlags(
            Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint
        ) # 设置窗口属性

        # 变量
        self.page_choice_buttons = [get_lang('42'), get_lang('a6'), get_lang('43'), get_lang('44'), get_lang('69')]
        self.last_page = None
        self.now_page = 0
        self.values = {} if values is None else values

        self.init_ui()
        self.check_values() # 检查设置值

        # 连接信号
        clicker.started.connect(self.on_clicker_started)

        logger.debug('初始化设置窗口完成')
        
    def check_values(self):
        '''检查设置值'''
        # 热键设置
        if self.values.get('need_restart', False):
            self.on_need_restart_setting_changed(lambda: system_lang, 'select_lang')
        self.values.clear()

    def create_setting_page(self, title):
        logger.debug(f'创建设置页面: {title}')
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
            logger.debug(f'设置内容标签')
            content_label.setText(text)

        def create_horizontal_line():
            logger.debug(f'创建水平线')
            line = UFrame()
            line.setFrameShape(UFrame.Shape.HLine)  # 水平线
            return line
        
        def parse_hotkey(input: UHotkeyLineEdit):
            return input.text().split('+')

        self.page_general = self.page_choice_buttons[0] # 默认设置
        self.page_style = self.page_choice_buttons[1] # 样式设置
        self.page_click = self.page_choice_buttons[2] # 连点器设置
        self.page_update = self.page_choice_buttons[3] # 更新设置
        self.page_hotkey = self.page_choice_buttons[4] # 热键设置

        # 主程序
        self.app = get_application_instance()

        # 添加一些示例设置控件
        match title:
            case self.page_general:
                set_content_label(get_lang('7f'))
                # 选择语言 
                lang_choice_layout = QHBoxLayout() # 语言选择布局
                self.lang_choice = QComboBox()
                self.lang_choice.addItems([i['lang_name'] for i in langs])
                self.lang_choice.setCurrentIndex(settings.get('select_lang', 0))

                # 布局
                lang_choice_layout.addWidget(QLabel(f'{get_lang('45')}{get_lang('b5')}:')) # 选择语言提示
                lang_choice_layout.addWidget(self.lang_choice)
                lang_choice_layout.addStretch(1)   

                # 显示托盘图标
                tray_layout = QHBoxLayout() # 窗口风格布局
                tray = UCheckBox(get_lang('80'))
                tray.setChecked(settings.get('show_tray_icon', True))

                tray_layout.addWidget(tray)
                tray_layout.addStretch(1)

                # 开机自启动
                start_layout = QHBoxLayout() # 开机自启动布局
                self.start_checkbox = UCheckBox(get_lang('b6'))
                self.start_checkbox.setChecked(auto_start_manager.auto_start)

                start_layout.addWidget(self.start_checkbox)
                start_layout.addStretch(1)

                auto_start_manager.updated.connect(lambda enb: self.start_checkbox.setChecked(enb))
                self.start_checkbox.checkStateChanged.connect(self.on_auto_start_changed)

                # 延迟
                soft_delay_layout = QHBoxLayout() # 颜色延迟布局
                soft_delay_setting = settings.get('soft_delay', 100)

                soft_delay = QSlider(Qt.Horizontal)
                soft_delay.setMinimum(0)
                soft_delay.setMaximum(100)
                soft_delay.setValue(soft_delay_setting // 10)
                soft_delay.setTickPosition(QSlider.TicksBelow)
                soft_delay.setTickInterval(10)
                soft_delay.setFixedWidth(200)

                delay_tip_label = QLabel(get_lang("8a"))
                set_style(delay_tip_label, 'dest_small')

                # 布局
                soft_delay_layout.addWidget(QLabel(f'{get_lang('b0')}\n{get_lang('b5')}:'))
                soft_delay_layout.addWidget(soft_delay)
                soft_delay_layout.addStretch(1)

                delay_layout_text = QLabel(f'{get_lang('b0')}:{soft_delay_setting}{get_lang("ms", source=unit_lang)}')
                set_style(delay_layout_text, 'big_text_16')
                
                # 重置所有设置
                repair_layout = QHBoxLayout() # 重置布局
                self.repair_button = QPushButton(get_lang('5e'))

                repair_layout.addWidget(self.repair_button)
                repair_layout.addStretch(1)

                # 布局
                layout.addLayout(lang_choice_layout)
                layout.addLayout(tray_layout)
                layout.addLayout(start_layout)
                layout.addWidget(create_horizontal_line())
                layout.addLayout(soft_delay_layout)
                layout.addWidget(delay_layout_text)
                layout.addWidget(delay_tip_label)
                layout.addWidget(create_horizontal_line())
                layout.addLayout(repair_layout)

                # 绑定事件
                self.lang_choice.currentIndexChanged.connect(lambda: self.on_need_restart_setting_changed(self.lang_choice.currentIndex, 'select_lang'))
                tray.checkStateChanged.connect(lambda: self.on_setting_changed(tray.isChecked,'show_tray_icon'))
                tray.checkStateChanged.connect(lambda: self.app.setQuitOnLastWindowClosed(not tray.isChecked()))  # 关闭窗口时不退出应用
                soft_delay.valueChanged.connect(lambda: self.on_setting_changed(lambda: soft_delay.value() * 10 if soft_delay.value() > 0 else 1, 'soft_delay'))
                soft_delay.valueChanged.connect(lambda: delay_layout_text.setText(f'{get_lang('b0')}: {soft_delay.value() * 10 if soft_delay.value() > 0 else 1}{get_lang("ms", source=unit_lang)}'))
                self.repair_button.clicked.connect(self.repair_all_settings)
            case self.page_click:
                set_content_label(get_lang('84'))
                # 选择默认连点器延迟
                layout_delay = QVBoxLayout() # 延迟布局
                unit_delay_layout = QHBoxLayout() # 窗口风格布局
                self.default_delay = QLineEdit()
                self.default_delay.setText(str(settings.get('click_delay', '')))
                self.delay_combo = QComboBox()
                self.delay_combo.addItems([get_lang('ms', source=unit_lang), get_lang('s', source=unit_lang)])
                self.delay_combo.setCurrentIndex(settings.get('delay_unit', 0))

                unit_delay_layout.addWidget(QLabel(get_lang('46') + ': '))
                unit_delay_layout.addWidget(self.default_delay)
                unit_delay_layout.addWidget(self.delay_combo)
                unit_delay_layout.addStretch(1)

                # 连点出错时使用默认值
                use_default_delay = UCheckBox(get_lang('47'))
                use_default_delay.setChecked(settings.get('failed_use_default', False))
                if not self.default_delay.text():
                    use_default_delay.setEnabled(False)

                # 布局
                layout_delay.addLayout(unit_delay_layout)
                layout_delay.addWidget(use_default_delay)
                layout_delay.addWidget(create_horizontal_line())
                layout_delay.addStretch(1)

                # 连点器默认点击次数
                layout_time = QVBoxLayout() # 次数布局
                unit_time_layout = QHBoxLayout() # 窗口风格布局
                self.default_time = QLineEdit()
                self.default_time.setText(str(settings.get('click_times', '')))
                self.times_combo = QComboBox()
                self.times_combo.addItems([get_lang('66'), get_lang('2a'), get_lang('2b')])
                self.times_combo.setCurrentIndex(settings.get('times_unit', 0))

                unit_time_layout.addWidget(QLabel(get_lang('85') + ': '))
                unit_time_layout.addWidget(self.default_time)
                unit_time_layout.addWidget(self.times_combo)
                unit_time_layout.addStretch(1)

                # 连点出错时使用默认值
                use_default_time = UCheckBox(get_lang('86'))
                use_default_time.setChecked(settings.get('times_failed_use_default', False))
                if not self.default_time.text():
                    use_default_time.setEnabled(False)

                self.total_time_label = QLabel(f'{get_lang('2c')}: {get_lang('61')}')
                self.total_time_label.setAlignment(Qt.AlignHCenter)
                set_style(self.total_time_label, 'big_text_16')

                # 布局
                layout_time.addLayout(unit_time_layout)
                layout_time.addWidget(use_default_time)
                layout_time.addWidget(create_horizontal_line())
                layout_time.addStretch(1)

                # 布局
                layout.addLayout(layout_delay)
                layout.addLayout(layout_time)
                layout.addWidget(self.total_time_label)
                layout.addStretch(1)

                # 连接信号
                self.default_delay.textChanged.connect(lambda: self.on_default_input_changed(self.default_delay, 'click_delay', use_default_delay))
                self.default_delay.textChanged.connect(lambda: on_input_change(type='setting'))
                use_default_delay.checkStateChanged.connect(lambda: self.on_setting_changed(use_default_delay.isChecked, 'failed_use_default'))
                self.default_time.textChanged.connect(lambda: self.on_default_input_changed(self.default_time, 'click_times', use_default_time))
                self.default_time.textChanged.connect(lambda: on_input_change(type='setting'))
                use_default_time.checkStateChanged.connect(lambda: self.on_setting_changed(use_default_time.isChecked, 'times_failed_use_default'))
                self.delay_combo.currentIndexChanged.connect(lambda: self.on_setting_changed(self.delay_combo.currentIndex, 'delay_unit'))
                self.delay_combo.currentIndexChanged.connect(lambda: on_input_change(type='setting'))
                self.times_combo.currentIndexChanged.connect(lambda: self.on_setting_changed(self.times_combo.currentIndex, 'times_unit'))
                self.times_combo.currentIndexChanged.connect(lambda: on_input_change(type='setting'))
            case self.page_update:
                set_content_label(get_lang('87'))
                # 选择更新检查提示
                check_update_layout = QHBoxLayout() # 窗口风格布局

                check_update_notify_text = QLabel(get_lang('48')) # 选择更新检查提示
                check_update_notify = QComboBox()
                check_update_notify.addItems([get_lang('49'), get_lang('4a')])
                check_update_notify.setCurrentIndex(settings.get('update_notify', 0))

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
                style_layout = QHBoxLayout() # 窗口风格布局
                self.style_choice = QComboBox()

                items = list(style_indexes[select_lang]['lang_package'].values())

                self.style_choice.addItems([get_lang('82')] + items)
                self.style_choice.setCurrentIndex(settings.get('select_style', 0))

                # 布局
                style_layout.addWidget(QLabel(get_lang('81'))) # 选择窗口风格提示
                style_layout.addWidget(self.style_choice)
                style_layout.addStretch(1)

                style_use_windows_layout = QHBoxLayout() # 颜色使用windows按钮布局
                style_choice_use_windows = UCheckBox(get_lang('a8'))
                tip_label = QLabel(get_lang('b4'))
                set_style(tip_label, 'dest_small')
                style_choice_use_windows.setChecked(settings.get('use_windows_color', True))

                # 布局
                style_use_windows_layout.addWidget(style_choice_use_windows)
                style_use_windows_layout.addStretch(1)
                
                theme_layout = QHBoxLayout() # 主题布局
                theme_tip_window = QLabel(get_lang('4b'))
                set_style(theme_tip_window, 'dest_small')
                theme_combo = QComboBox()
                theme_combo.addItems(QStyleFactory.keys())
                theme_combo.setCurrentText(settings.get('theme', theme))
                
                # 布局
                theme_layout.addWidget(QLabel(get_lang('23')))
                theme_layout.addWidget(theme_combo)
                theme_layout.addStretch(1)

                # 布局
                layout.addLayout(style_layout)
                layout.addWidget(create_horizontal_line())
                layout.addLayout(style_use_windows_layout)
                layout.addWidget(tip_label)
                layout.addWidget(create_horizontal_line())
                layout.addLayout(theme_layout)
                layout.addWidget(theme_tip_window)
                layout.addWidget(create_horizontal_line())

                # 连接信号
                self.style_choice.currentIndexChanged.connect(lambda: self.on_setting_changed(self.style_choice.currentIndex, 'select_style'))
                style_choice_use_windows.checkStateChanged.connect(lambda: self.on_setting_changed(style_choice_use_windows.isChecked, 'use_windows_color'))
                theme_combo.currentIndexChanged.connect(lambda: self.on_setting_changed(theme_combo.currentText, 'theme'))
                theme_combo.currentIndexChanged.connect(lambda: self.app.setStyle(theme_combo.currentText()))
            case self.page_hotkey:
                set_content_label(get_lang('21'))
                
                # 左键连点
                left_click_layout = QHBoxLayout() # 左键连点布局
                left_click_input = UHotkeyLineEdit() # 左键连点输入框
                left_click_input.setText(format_keys(settings.get('left_click_hotkey', ['F2'])))
                left_repair_button = QPushButton(get_lang('20')) # 还原默认设置按钮
                
                # 布局 
                left_click_layout.addWidget(QLabel(f'{get_lang('0c')}: '), 1) # 左键连点提示
                left_click_layout.addWidget(left_click_input, 6)
                left_click_layout.addWidget(left_repair_button, 2)
                left_click_layout.addStretch()
                
                # 右键连点
                right_click_layout = QHBoxLayout() # 右键连点布局
                right_click_input = UHotkeyLineEdit() # 右键连点输入框
                right_repair_button = QPushButton(get_lang('20')) # 还原默认设置按钮
                
                right_click_input.setText(format_keys(settings.get('right_click_hotkey', ['F3'])))
                
                # 布局
                right_click_layout.addWidget(QLabel(f'{get_lang('0d')}: '), 1) # 右键连点提示
                right_click_layout.addWidget(right_click_input, 6)
                right_click_layout.addWidget(right_repair_button, 2)
                right_click_layout.addStretch()
                
                # 暂停/重启连点
                pause_click_layout = QHBoxLayout() # 暂停/重启连点布局
                pause_click_input = UHotkeyLineEdit() # 暂停/重启连点输入框
                pause_click_input.setText(format_keys(settings.get('pause_click_hotkey', ['F4'])))
                pause_repair_button = QPushButton(get_lang('20')) # 还原默认设置按钮
                
                # 布局
                pause_click_layout.addWidget(QLabel(f'{get_lang('6b')}: '), 1) # 暂停/重启连点提示
                pause_click_layout.addWidget(pause_click_input, 6)
                pause_click_layout.addWidget(pause_repair_button, 2)
                pause_click_layout.addStretch()
                
                # 停止连点
                stop_click_layout = QHBoxLayout() # 停止连点布局
                stop_click_input = UHotkeyLineEdit() # 停止连点输入框
                stop_click_input.setText(format_keys(settings.get('stop_click_hotkey', ['F6'])))
                stop_repair_button = QPushButton(get_lang('20')) # 还原默认设置按钮
                
                # 布局
                stop_click_layout.addWidget(QLabel(f'{get_lang('6c')}: '), 1) # 停止连点提示
                stop_click_layout.addWidget(stop_click_input, 6)
                stop_click_layout.addWidget(stop_repair_button, 2)
                stop_click_layout.addStretch()
                
                # 连点属性
                click_attr_layout = QHBoxLayout() # 连点属性布局
                click_attr_input = UHotkeyLineEdit() # 连点属性输入框
                click_attr_input.setText(format_keys(settings.get('click_attr_hotkey', ['Ctrl', 'Alt', 'A'])))
                click_attr_button = QPushButton(get_lang('20')) # 还原默认设置按钮
                
                # 布局
                click_attr_layout.addWidget(QLabel(f'{get_lang('8c')}: '), 1) # 连点属性提示
                click_attr_layout.addWidget(click_attr_input, 6)
                click_attr_layout.addWidget(click_attr_button, 2)
                click_attr_layout.addStretch()
                
                # 快速连点
                fast_click_layout = QHBoxLayout() # 快速连点布局
                fast_click_input = UHotkeyLineEdit() # 快速连点输入框
                fast_click_input.setText(format_keys(settings.get('fast_click_hotkey', ['Ctrl', 'Alt', 'F'])))
                fast_click_button = QPushButton(get_lang('20')) # 还原默认设置按钮
                
                # 布局
                fast_click_layout.addWidget(QLabel(f'{get_lang('75')}: '), 1) # 快速连点提示
                fast_click_layout.addWidget(fast_click_input, 6)
                fast_click_layout.addWidget(fast_click_button, 2)
                fast_click_layout.addStretch()
                
                # 主窗口
                main_window_layout = QHBoxLayout() # 主窗口布局
                main_window_input = UHotkeyLineEdit() # 主窗口输入框
                main_window_input.setText(format_keys(settings.get('main_window_hotkey', ['Ctrl', 'Alt', 'M'])))
                main_window_button = QPushButton(get_lang('20')) # 还原默认设置按钮

                # 布局
                main_window_layout.addWidget(QLabel(f'{get_lang('76')}: '), 1) # 主窗口提示
                main_window_layout.addWidget(main_window_input, 6)
                main_window_layout.addWidget(main_window_button, 2)
                main_window_layout.addStretch()

                # 布局
                layout.addLayout(left_click_layout)
                layout.addLayout(right_click_layout)
                layout.addLayout(pause_click_layout)
                layout.addLayout(stop_click_layout)
                layout.addLayout(click_attr_layout)
                layout.addLayout(fast_click_layout)
                layout.addLayout(main_window_layout)
                
                # 连接信号
                left_click_input.textChanged.connect(lambda: self.on_setting_changed(lambda: parse_hotkey(left_click_input), 'left_click_hotkey'))
                right_click_input.textChanged.connect(lambda: self.on_setting_changed(lambda: parse_hotkey(right_click_input), 'right_click_hotkey'))
                pause_click_input.textChanged.connect(lambda: self.on_setting_changed(lambda: parse_hotkey(pause_click_input), 'pause_click_hotkey'))
                stop_click_input.textChanged.connect(lambda: self.on_setting_changed(lambda: parse_hotkey(stop_click_input),'stop_click_hotkey'))
                click_attr_input.textChanged.connect(lambda: self.on_setting_changed(lambda: parse_hotkey(click_attr_input), 'click_attr_hotkey'))
                fast_click_input.textChanged.connect(lambda: self.on_setting_changed(lambda: parse_hotkey(fast_click_input), 'fast_click_hotkey'))
                
                left_repair_button.clicked.connect(lambda: self.repair_settings('left_click_hotkey'))
                right_repair_button.clicked.connect(lambda: self.repair_settings('right_click_hotkey'))
                pause_repair_button.clicked.connect(lambda: self.repair_settings('pause_click_hotkey'))
                stop_repair_button.clicked.connect(lambda: self.repair_settings('stop_click_hotkey'))
                click_attr_button.clicked.connect(lambda: self.repair_settings('click_attr_hotkey'))
                fast_click_button.clicked.connect(lambda: self.repair_settings('fast_click_hotkey'))
                main_window_button.clicked.connect(lambda: self.repair_settings('main_window_hotkey'))
                
        restart_layout = QHBoxLayout() # 重启提示布局
        self.restart_button = QPushButton(get_lang('7e'))

        set_style(self.restart_button, 'selected')
        self.restart_button.clicked.connect(self.restart)
        
        restart_layout.addStretch()
        restart_layout.addWidget(self.restart_button)
        
        if not settings_need_restart:
            self.restart_button.hide()
        
        layout.addLayout(restart_layout)

        # 添加弹簧，让内容靠上显示
        layout.addStretch()

        return page

    def showEvent(self, event):
        '''窗口显示事件'''
        new_color_bar(self)
        return super().showEvent(event)
    
    def repair_settings(self, key: str):
        '''还原默认设置'''
        global settings
        if MessageBox.warning(self, get_lang('15'), get_lang('22'), MessageButtonTemplate.YESNO) != 2: # 不确认重置
            return
        settings[key] = default_setting[key]
        save_settings(settings)
        self.window_restarted.emit()
            
    def repair_all_settings(self):
        global settings
        if MessageBox.warning(self, get_lang('15'), get_lang('22'), MessageButtonTemplate.YESNO) != 2: # 不确认重置
            return
        settings = default_setting.copy()
        settings['theme'] = default_theme
        settings['select_lang'] = system_lang
        save_settings(settings)
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

        lang = self.lang_choice.currentIndex()

        restart_place = list(map(lambda x: get_lang(x, lang_id=lang), restart_place))

        selected_lang_yes = CustonMessageButton(get_lang('01', source=default_button_text, lang_id=lang), QMessageBox.YesRole)
        selected_lang_no = CustonMessageButton(get_lang('02', source=default_button_text, lang_id=lang), QMessageBox.AcceptRole)
        need_restart = MessageBox.warning(self, get_lang('15', lang_id=lang), f'{get_lang("89", lang_id=lang)}: {", ".join(restart_place)}', [selected_lang_yes, selected_lang_no], selected_lang_yes)
        if need_restart == 2:
            self.restart()
        else:
            self.restart_window()

    def restart_window(self):
        self.window_restarted.emit()

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
                set_style(button, 'selected')
            else:
                set_style(button, '')

    def restart(self):
        app.quit(lambda: run_software('main.py', 'main.exe'))

    def init_right_pages(self):
        super().init_right_pages()
        set_style(self.buttons[0], 'selected')

    def on_clicker_started(self):
        '''连点器启动事件'''
        if self.now_page == self.page_choice_buttons.index(get_lang('43')):
            self.on_page_button_clicked(self.last_page)
            MessageBox.critical(self, get_lang('14'), get_lang('aa'))
            return

class SetImportExtensionModeWindow(UDialog):
    def __init__(self):
        super().__init__()
        logger.debug('初始化管理扩展提示窗口')
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

        logger.debug('管理扩展提示窗口初始化完成')

    def on_mode_button_clicked(self):
        self.close()
        main_window.show_import_extension(self.mode_combo.currentIndex())

class TrayApp:
    def __init__(self):
        logger.info('加载托盘程序')
        self.app = get_application_instance()

        show_tray_icon = settings.get('show_tray_icon', True)
        if show_tray_icon:
            self.app.setQuitOnLastWindowClosed(False)  # 关闭窗口时不退出应用

        # 激活主窗口
        main_window.show()

        # 加载警告
        if not has_packages:
            MessageBox.warning(None, get_lang('15'), get_lang('ae'))

        # 创建热键监听器
        self.hotkey_listener = get_hotkey_listener_instance()
        self.hotkey_listener.combination_pressed.connect(self.run_combination)

        # 创建系统托盘图标
        self.setup_tray_icon()

        clicker.pause.connect(main_window.on_pause)
        clicker.click_changed.connect(main_window.on_click_changed)
        clicker.stopped.connect(main_window.on_stop)
        clicker.click_conuter.connect(main_window.on_click_counter)
        clicker.started.connect(self.on_start)
        clicker.started.connect(main_window.on_start)

        logger.info('托盘程序框架加载完成')

    def setup_tray_icon(self):
        '''设置系统托盘图标'''
        logger.info('设置系统托盘图标')
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
        logger.info('创建右键菜单')
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
        logger.info('启动热键监听器')
        # 在后台线程中启动热键监听
        self.hotkey_thread = QtThread(self.hotkey_listener.start_listening)
        self.hotkey_thread.start()

    def on_tray_icon_activated(self, reason):
        '''处理托盘图标激活事件'''
        if reason == QSystemTrayIcon.ActivationReason.Trigger:  # 左键点击
            self.show_main_window()
            self.refresh()

    def check_delay(self, input_delay):
        try:
            math.ceil(float(input_delay))
        except Exception:
            trace = format_exc()
            MessageBox.critical(main_window, get_lang('13'), f'{get_lang('ae')}\n{trace}')
            logger.exception('延迟处理', trace)
            return False
        return True

    def show_main_window(self):
        '''显示主窗口'''
        main_window.is_start_from_tray = True
        main_window.show()

    def quit_application(self):
        '''退出应用程序'''
        # 停止热键监听
        self.hotkey_listener.stop_listening()
        self.app.quit()

    def run(self):
        '''运行应用程序'''
        logger.info('运行托盘程序')
        code = self.app.exec()
        if can_update:
            run_software('updater.old/updater.py', 'updater.old/updater.exe')
        else:
            # 进行清理
            run_after.run()
            self.quit()
        logger.info('主程序退出')
        sys.exit(code)

    def refresh(self):
        refresh.run()
        
    def quit(self, code=lambda: None):
        if update_window.down_thread is not None:
            if update_window.down_thread.isRunning():
                update_window.down_thread.quit()
                update_window.down_thread.wait(1000)  # 等待一段时间
                if update_window.down_thread.isRunning(): # 仍然运行，强制退出
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
        if can_run_hotkey:
            self.on_combination_pressed(combination)
            
    def on_start_clicker_tray(self, direction):
        '''启动托盘连点'''
        if direction == 'left': # 左键
            warn_text = '左'
            button = main_window.left_click_button
            start_lang_id = '6f'
            func = clicker.mouse_left
        elif direction == 'right': # 右键
            warn_text = '右'
            button = main_window.right_click_button
            start_lang_id = '70'
            func = clicker.mouse_right
        else:
            logger.critical('未知的方向，代码退出')
            return

        # 判断参数有效性
        if not button.isEnabled():
            logger.warning(f'{warn_text}键未启用')
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
            self.refresh()
    
    def on_combination_pressed(self, combination):
        '''处理组合键事件'''
        combination = format_keys(combination, source=True)

        if all_in_list(combination, parse_hotkey('fast_click', ['F', 'Ctrl', 'Alt'])):
            # 处理Ctrl+Alt+F组合键
            if clicker.running:
                self.tray_icon.showMessage(get_lang('14'), get_lang('af'), QSystemTrayIcon.MessageIcon.Critical, 1000)
            else:
                self.show_window(fast_click_window)
        elif all_in_list(combination, parse_hotkey('main_window', ['Ctrl', 'Alt', 'M'])):
            # 处理Ctrl+Alt+M组合键
            self.show_window(main_window)
            if not main_window.isVisible():
                main_window.is_start_from_tray = True
        elif all_in_list(combination, parse_hotkey('click_attr', ['Ctrl', 'Alt', 'A'])):
            # 处理Ctrl+Alt+A组合键
            self.show_window(click_attr_window)
        elif all_in_list(combination, parse_hotkey('left_click', ['F2'])):
            self.on_start_clicker_tray('left') # 左键
        elif all_in_list(combination, parse_hotkey('right_click', ['F3'])):
            self.on_start_clicker_tray('right') # 右键
        elif all_in_list(combination, parse_hotkey('pause_click', ['F4'])):
            if clicker.running:
                clicker.pause_click()
                if clicker.paused:
                    self.tray_icon.showMessage(get_lang('6e'), get_lang('71'), QSystemTrayIcon.MessageIcon.Information, 1000)
                else:
                    self.tray_icon.showMessage(get_lang('6e'), get_lang('72'), QSystemTrayIcon.MessageIcon.Information, 1000)
            else:
                self.tray_icon.showMessage(get_lang('6e'), get_lang('74'), QSystemTrayIcon.MessageIcon.Warning, 1000)
        elif all_in_list(combination, parse_hotkey('stop_click', ['F6'])):
            if clicker.running:
                main_window.on_stop()
                self.tray_icon.showMessage(get_lang('6e'), get_lang('73'), QSystemTrayIcon.MessageIcon.Information, 1000)
            else:
                self.tray_icon.showMessage(get_lang('6e'), get_lang('74'), QSystemTrayIcon.MessageIcon.Warning, 1000)

    def on_start(self):
        '''连点器启动事件'''
        if fast_click_window.isVisible():
            fast_click_window.hide()
            self.tray_icon.showMessage(get_lang('14'), get_lang('af'), QSystemTrayIcon.MessageIcon.Critical, 1000)

if __name__ == '__main__':
    from sharelibs import (mem_id, get_resource_path, run_as_admin) # 共享库
    import json # 用于读取json文件
    from pathlib import Path # 路径库

    shared_memory = QSharedMemory(mem_id[0])
    if shared_memory.attach():
        # 已经有一个实例在运行
        sys.exit(2)
    shared_memory.create(1)

    is_running = any(list(map(lambda x: QSharedMemory(x).attach(), mem_id[3:4])))
    if is_running:
        # 已经有一个实例在运行
        sys.exit(2)

    with open(get_resource_path('langs', 'packages.json'), 'r', encoding='utf-8') as f:
        package_lang = json.load(f)

    data_path = Path('data')
    if not((data_path / 'first_run').exists()):
        run_as_admin('install_pack.py', 'install_pack.exe')
        sys.exit(0)
    else:
        import os # 系统库
        import shutil # 用于删除文件夹
        from logger import Logger

        logger = Logger('主程序日志')

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
                    logger.warning(f'扩展{i}已过期，自动清除')
                    shutil.rmtree(f'extensions/{i}', ignore_errors=True)
                    del packages_name[packages_name.index(i)]
            for file in os.listdir('extensions'):
                full_path = os.path.join('extensions', file)
                # 检查是否是文件
                if os.path.isfile(full_path):
                    if file != 'packages.json':
                        os.remove(full_path)
                        logger.warning(f'错误文件{file}自动清除')
                elif os.path.isdir(full_path):
                    if file not in packages_name:
                        logger.warning(f'扩展{file}已过期，自动清除')
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

        # 加载框架
        import pyautogui # 鼠标操作库
        from time import sleep, time # 延迟
        from webbrowser import open as open_url # 关于作者
        from check_update import check_update, web_data, download_file # 更新检查
        from uiStyles import (UnitInputLayout, styles, maps, StyleReplaceMode, ULabel, CustonMessageButton) # 软件界面样式
        from uiStyles import indexes as style_indexes # 界面组件样式索引
        from sharelibs import (run_software, langs, create_shortcut, __version__, is_pre, get_icon, default_button_text, 
                               get_unit_value, unit_lang, get_size_text, get_file_hash, system_lang) # 共享库
        import parse_dev # 解析开发固件配置
        import winreg # 注册表库
        import math # 数学库
        import colorsys # 颜色库
        import struct # 字节处理库
        import pytz # 时区库
        from traceback import format_exc # 异常格式化
        from itertools import chain # 迭代器库
        import platform # 系统信息

        # 系统api
        import ctypes
        from ctypes import wintypes

        logger.info('加载变量')
        logger.debug('定义常量')
        has_packages = os.path.exists(get_resource_path('packages'))
        package_names, show_list, package_ids = get_packages()

        # Windows API常量
        logger.debug('定义Windows API常量')
        DWMWA_USE_IMMERSIVE = 20
        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        DWM_WINDOW_CORNER_PREFERENCE = 33
        DWMWCP_ROUND = 2
        DWMNCRP_ENABLED = 1

        logger.info('加载设置')
        settings = load_settings()

        logger.info('加载服务程序')
        clicker = Click()
        auto_start_manager = StartManager()
        color_getter = ColorGetter()
        run_after = RunAfter()

        # 变量
        logger.info('定义数据路径')

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
        should_check_update_res = should_check_update()
        icon = get_icon('icon')

        settings_need_restart = False
        can_update = False

        # 单位控制
        latest_index = 2
        select_lang = settings.get('select_lang', 0)

        # 其他
        dev_config = parse_dev.parse() # 开发者模式配置
        can_run_hotkey = True # 热键是否可用
        result = (None, None, None, None) # 更新检查结果

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
            
        with open(get_resource_path('default_setting.json')) as f:
            default_setting = json.load(f)

        theme = settings.get('theme', default_theme)

        logger.info('定义资源完成')

        logger.info('检查更新注册表')

        # 检查版本号与注册表是否一致,不一样就修改注册表
        run_software('check_reg_ver.py', 'check_reg_ver.exe')

        # 移除过期组件
        shutil.rmtree('updater.old', ignore_errors=True)
        
        # 加载窗口
        logger.info('加载ui')
        main_window = MainWindow()
        on_input_change(type='main') # 更新时间估计状态

        about_window = AboutWindow()
        clean_cache_window = CleanCacheWindow()
        update_window = UpdateWindow()
        update_ok_window = UpdateOKWindow()
        click_attr_window = ClickAttrWindow()
        fast_click_window = FastSetClickWindow()

        setting_window = SettingWindow()
        on_input_change(type='setting') # 更新时间估计状态
        setting_window.click_setting_changed.connect(lambda: on_input_change(type='setting'))
        setting_window.window_restarted.connect(on_update_setting_window)
        
        set_import_extension_window = SetImportExtensionModeWindow()

        app = TrayApp()
        app.app.setStyle(theme)
        app.run()