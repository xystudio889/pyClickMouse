# 加载ui框架
from PySide6.QtWidgets import QApplication
import sys
from logger import Logger
app = QApplication(sys.argv)
logger = Logger('Main')
from uiStyles.QUI import *

# 加载框架
from datetime import datetime # 检查时间
from pynput import keyboard # 热键功能库
import pyautogui # 鼠标操作库
from time import sleep # 延迟
from webbrowser import open as open_url # 关于作者
from uiStyles import (UnitInputLayout, styles, StyleReplaceMode, CustonMessageButton, SelectUI, UCheckBox, UMessageBox, MessageButtonTemplate) # 软件界面样式
from sharelibs import (run_software, langs,  __version__, get_icon, default_button_text, get_unit_value, unit_lang, system_lang, settings, QtThread, 
                       default_settings, get_resource_path, get_lang, create_shortcut) # 共享库
import winreg # 注册表库
import math # 数学库
import colorsys # 颜色库
import struct # 字节处理库
import pytz # 时区库
from traceback import format_exc # 异常格式化
from txtinfo import *
import os # 系统库
import json # 用于读取json文件
from pathlib import Path # 路径库
    
def filter_hotkey(text:str):
    return text.split('(')[0]

def save_settings():
    '''
    保存设置
    '''
    logger.info('Saving settings.')
    with open(data_path / 'settings.json', 'w', encoding='utf-8') as f:
        json.dump(settings, f)

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
        logger.info('Starting hotkey listener.')
        # 在后台线程中启动热键监听
        hotkey_thread = QtThread(get_hotkey_listener_instance.instance.start_listening)
        hotkey_thread.start()
    return get_hotkey_listener_instance.instance

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
    elif type ==InputChange.setting_window:
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

    if times_combo.currentIndex() == latest_index or input_times == '0': 
        is_inf = True
    if setting_value.times_unit == latest_index and type == InputChange.main_window:
        is_inf = True
        
    def on_delay_error(error_text=get_lang('14')):
        '''输入延迟错误'''
        total.setText(f'{get_lang('2c')}: {error_text}')
        if type == InputChange.main_window:
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
            if type == InputChange.main_window:
                on_delay_error(get_lang('60'))
            else:
                on_delay_error()
            return False
    
    try:
        delay = math.ceil(float(input_delay))
        if delay < 1:
            raise ValueError
    except ValueError:
        if not setting_value.click_delay == '':
            if input_delay == '':
                if check_default_var('delay'):
                    delay = int(setting_value.click_delay)
                else:
                    return
            elif setting_value.delay_error_use_default:
                if check_default_var('delay'):
                    delay = int(setting_value.click_delay)
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
            if setting_value.click_times == '' and setting_value.click_delay == '':
                on_delay_error(get_lang('61'))
                return
            else:
                if input_times == '':
                    if check_default_var('times'):
                        times = int(setting_value.click_times)
                    else:
                        return
                elif setting_value.times_error_use_default:
                    if check_default_var('times'):
                        times = int(setting_value.click_times)
                    else:
                        return
                else:
                    on_delay_error()
                    return
        except Exception:
            on_delay_error()
            return

    if type == InputChange.main_window:
        main_window.right_click_button.setEnabled(True)
        main_window.left_click_button.setEnabled(True)
        is_error = False

    if setting_value.click_delay != '' and input_delay == '':
        match setting_value.delay_unit:
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
        if type == InputChange.main_window:
            if delay_num == 0:
                on_delay_error()
    else:
        if setting_value.click_times != '' and input_times == '':
            match setting_value.times_unit:
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
        logger.debug('Initializing window.')

        super().__init__(parent=parent)
        self.setWindowIcon(icon)
    
class UDialog(QDialog):
    '''自定义对话框基类'''
    def __init__(self, parent=None):
        logger.debug('Initializing window.')

        super().__init__(parent=parent)
        self.setWindowIcon(icon)

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
        self.timer.start(100)

    def create_reg(self):
        '''检查是否已启用开机自启动'''
        start_path = Path(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup', self.app_name)
        if not(start_path.exists()):
            create_shortcut(str(start_path), str(Path.cwd() / 'main.exe') + ' --quiet', 'ClickMouse', work_dir=str(Path.cwd()))
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
        set_style(self, StyleClass.frame)

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
        logger.info('Left click')
        if not self.running:
            self.mouse_click(button='left', input_delay=delay, times=times)

    def mouse_right(self, delay, times):
        # 停止当前运行的点击线程
        logger.info('Right click')
        if not self.running:
            self.mouse_click(button='right', input_delay=delay, times=times)

    def set_default_clicked(self):
        self.left_clicked = False
        self.right_clicked = False
        self.click_changed.emit(self.left_clicked, self.right_clicked)

    def mouse_click(self, button: str, input_delay, times):
        '''鼠标连点'''
        logger.info('Start click')
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
            UMessageBox.critical(None, get_lang('14'), f'{get_lang('1b')}\n{trace}')
            logger.exception('Clicker', trace)
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
                        UMessageBox.critical(None, get_lang('14'), f'{get_lang('1b')}\n{trace}')
                        logger.exception('Clicker', trace)

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

    def pause_click(self):
        if self.paused:
            logger.info('Clicker resumed')
        else:
            logger.info('Clicker paused')
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
        logger.info('Running refresh service')
        self.do_step(self.steps)

    def do_step(self, codes):
        # 尝试执行代码
        for code in codes:
            logger.debug(f'Running step {code.__name__}')
            try:
                code()
                logger.debug(f'Step {code.__name__} running successfully.')
            except NameError as e:
                logger.warning(f'Step {code.__name__} not defined: {e}')
            except Exception as e:
                logger.error(f'Step {code.__name__} Running failed: {e}')

    def refresh_title(self):
        QTimer.singleShot(100, color_getter.style_changed.emit)

    def left_check(self):
        if clicker.left_clicked:
            set_style(main_window.left_click_button, StyleClass.selected)
        else:
            logger.warning('Left click is not enabled.')
            set_style(main_window.left_click_button, StyleClass.none)

    def right_check(self):
        if clicker.right_clicked:
            set_style(main_window.right_click_button,StyleClass.selected)
        else:
            logger.warning('Right click is not enabled.')
            set_style(main_window.right_click_button, StyleClass.none)

class ColorGetter(QObject):
    style_changed = Signal()

    def __init__(self):
        global refresh
        super().__init__()
        
        self.current_theme, self.windows_color = self.load_theme()
        self.check_and_apply_theme()

        # 加载刷新服务
        refresh = Refresh()

        # 初始化时应用一次主题
        self.apply_global_theme()

        # 使用定时器定期检测主题变化
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_and_apply_theme)
        self.timer.start(100)

    def load_theme(self):
        logger.debug('Get latest theme')

        theme = None
        windows_color = None

        theme = QApplication.styleHints().colorScheme()
        if theme == Qt.ColorScheme.Dark:
            theme = 'dark'
        elif theme == Qt.ColorScheme.Light:
            theme = 'light'

        windows_color = get_windows_accent_color()

        return theme, windows_color

    def check_and_apply_theme(self):
        '''检查主题是否变化，变化则重新应用'''
        logger.debug('Check theme')

        new_theme, new_windows_color = self.load_theme()

        if new_theme != self.current_theme:
            self.current_theme = new_theme
            self.apply_global_theme()

        if new_windows_color != self.windows_color:
            self.windows_color = new_windows_color
            self.apply_global_theme()

    def refresh(self):
        refresh.run()

    def apply_global_theme(self):
        '''根据当前主题，为整个应用设置全局样式表'''
        global select_styles

        logger.info('Use style')

        app = get_application_instance()
        self.style_changed.emit()

        select_styles = styles[self.current_theme]
        
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
        
        app.setStyleSheet(select_styles.css_text)  # 全局应用
        self.refresh()
        
class SettingValue(SettingValue):
    def get(self, value):
        default_value = default_settings.get(value, None)
        if isinstance(default_value, str):
            if default_value.startswith('!var '): # 需要加载变量
                var_name = default_value[5:]
                default_value = eval(var_name)
        return settings.get(value, default_value)
        
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
        self.total_run_time = 0  # 总运行时间
        self.is_ready = True  # 是否状态栏为“就绪”
        self.is_start_from_tray = False # 是否从托盘启动

        logger.debug('Initializing clicker')
        self.init_ui()

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
        self.total_time_label = QLabel(get_lang('2c'))
        self.total_time_label.setAlignment(Qt.AlignHCenter)
        set_style(self.total_time_label, StyleClass.big_16)

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

        # 功能菜单
        function_menu = menu_bar.addMenu(get_lang('d6'))

        # 设置菜单
        settings_action = function_menu.addAction(get_lang('05'))

        # 帮助菜单
        help_menu = function_menu.addMenu(get_lang('09'))
        about_action = help_menu.addAction(get_lang('0a'))

        # 热键帮助
        create_issue_action = help_menu.addAction(get_lang('ba'))
        
        # 退出动作
        exit_action = function_menu.addAction(get_lang('03'))

        # 绑定动作
        about_action.triggered.connect(self.show_about)
        settings_action.triggered.connect(self.show_setting)
        exit_action.triggered.connect(app.quit)
        create_issue_action.triggered.connect(lambda: open_url(setting_value.feedback))

    def show_about(self):
        '''显示关于窗口'''
        logger.info('Opening about window')
        about_window.exec()

    def show_setting(self):
        '''显示设置窗口'''
        logger.info('Opening setting window')
        setting_window.show()

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
        version = QLabel(get_lang('1c').format(__version__))
        about = QLabel(get_lang('1d'))

        # 按钮
        logger.debug('Create Button')
        ok_button = QPushButton(get_lang('1e'))
        set_style(ok_button, StyleClass.selected)

        # 布局
        central_layout.addWidget(self.image_label, 0, 0, 1, 1)
        central_layout.addWidget(version, 0, 1, 1, 2)
        central_layout.addWidget(about, 2, 0, 1, 3)
        central_layout.addWidget(ok_button, 3, 2)

        self.setLayout(central_layout)

        # 绑定事件
        logger.debug('Singal connection')
        ok_button.clicked.connect(self.close)
        logger.debug('Initializing about window')

class SettingWindow(SelectUI):
    click_setting_changed = Signal()
    window_restarted = Signal()

    def __init__(self, values:dict | None = None):
        super().__init__()

        logger.debug('Initizalizing setting window')
        self.setGeometry(300, 300, 625, 400)
        self.setFixedSize(self.width(), self.height())
        self.setWindowTitle(filter_hotkey(get_lang('04')))
        self.setParent(main_window)
        self.setWindowIcon(QIcon(get_resource_path('icons', 'clickmouse', f'cms.ico')))
        self.setWindowFlags(
            Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint
        ) # 设置窗口属性

        # 变量
        self.page_choice_buttons = [get_lang('42'), get_lang('43'), get_lang('69')]

        self.create_setting_page_value()

        self.last_page = None
        self.now_page = 0
        self.values = {} if values is None else values

        self.init_ui()
        self.check_values() # 检查设置值

        # 连接信号
        clicker.started.connect(self.on_clicker_started)

        logger.debug('Initizalizing setting window successful.')
        
    def create_setting_page_value(self):
        self.page_general = self.page_choice_buttons[0] # 默认设置
        self.page_click = self.page_choice_buttons[1] # 连点器设置
        self.page_hotkey = self.page_choice_buttons[2] # 热键设置
        
    def check_values(self):
        '''检查设置值'''
        # 热键设置
        if self.values.get('need_restart', False):
            self.on_need_restart_setting_changed(lambda: system_lang, 'select_lang')
        self.values.clear()

    def create_setting_page(self, title):
        logger.info(f'Loading setting page: {title}')
        page = QWidget()
        layout = QVBoxLayout(page)

        def set_content_label(text):
            logger.debug(f'Set content label: {text}')
            content_label.setText(text)

        def create_horizontal_line():
            logger.debug('Create horizontal line')
            line = UFrame()
            line.setFrameShape(UFrame.Shape.HLine)  # 水平线
            return line
        
        def parse_hotkey(input: UHotkeyLineEdit):
            return input.text().split('+')

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
                self.lang_choice.setCurrentIndex(setting_value.select_lang)

                # 布局
                lang_choice_layout.addWidget(QLabel(f'{get_lang('45')}{get_lang('b5')}:')) # 选择语言提示
                lang_choice_layout.addWidget(self.lang_choice)
                lang_choice_layout.addStretch(1)   

                # 显示托盘图标
                tray_layout = QHBoxLayout() # 窗口风格布局
                tray = UCheckBox(get_lang('80'))
                tray.setChecked(setting_value.show_tray_icon)

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
                
                # 重置开机自启动
                repair_start_layout = QHBoxLayout() # 重置开机自启动布局
                repair_start_button = QPushButton(get_lang('20'))
                
                repair_tip = QLabel(get_lang('d1'))
                set_style(repair_tip, StyleClass.d_11)
                
                repair_start_layout.addWidget(repair_start_button)
                repair_start_layout.addWidget(repair_tip)
                repair_start_layout.addStretch(1)
                
                # 重置所有设置
                repair_layout = QHBoxLayout() # 重置布局
                self.repair_button = QPushButton(get_lang('5e'))

                repair_layout.addWidget(self.repair_button)
                repair_layout.addStretch(1)

                # 布局
                layout.addLayout(lang_choice_layout)
                layout.addLayout(tray_layout)
                layout.addWidget(create_horizontal_line())
                layout.addLayout(start_layout)
                
                layout.addLayout(repair_start_layout)
                layout.addWidget(create_horizontal_line())
                layout.addLayout(repair_layout)

                # 绑定事件
                self.lang_choice.currentIndexChanged.connect(lambda: self.on_need_restart_setting_changed(self.lang_choice.currentIndex, SettingText.select_lang))
                tray.checkStateChanged.connect(lambda: self.on_setting_changed(tray.isChecked, SettingText.show_tray_icon))
                tray.checkStateChanged.connect(lambda: self.app.setQuitOnLastWindowClosed(not tray.isChecked()))  # 关闭窗口时不退出应用
                self.repair_button.clicked.connect(self.repair_all_settings)
                repair_start_button.clicked.connect(self.repair_auto_start)
            case self.page_click:
                set_content_label(get_lang('84'))
                # 选择默认连点器延迟
                layout_delay = QVBoxLayout() # 延迟布局
                unit_delay_layout = QHBoxLayout() # 窗口风格布局
                self.default_delay = QLineEdit()
                self.default_delay.setText(setting_value.click_delay)
                self.delay_combo = QComboBox()
                self.delay_combo.addItems([get_lang('ms', source=unit_lang), get_lang('s', source=unit_lang)])
                self.delay_combo.setCurrentIndex(setting_value.delay_unit)

                unit_delay_layout.addWidget(QLabel(get_lang('46') + ': '))
                unit_delay_layout.addWidget(self.default_delay)
                unit_delay_layout.addWidget(self.delay_combo)
                unit_delay_layout.addStretch(1)

                # 连点出错时使用默认值
                use_default_delay = UCheckBox(get_lang('47'))
                use_default_delay.setChecked(setting_value.delay_error_use_default)
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
                self.default_time.setText(str(setting_value.click_times))
                self.times_combo = QComboBox()
                self.times_combo.addItems([get_lang('66'), get_lang('2a'), get_lang('2b')])
                self.times_combo.setCurrentIndex(setting_value.times_unit)

                unit_time_layout.addWidget(QLabel(get_lang('85') + ': '))
                unit_time_layout.addWidget(self.default_time)
                unit_time_layout.addWidget(self.times_combo)
                unit_time_layout.addStretch(1)

                # 连点出错时使用默认值
                use_default_time = UCheckBox(get_lang('86'))
                use_default_time.setChecked(setting_value.times_error_use_default)
                if not self.default_time.text():
                    use_default_time.setEnabled(False)
                self.total_time_label = QLabel(f'{get_lang('2c')}: {get_lang('61')}')
                self.total_time_label.setAlignment(Qt.AlignHCenter)
                set_style(self.total_time_label, StyleClass.big_16)

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
                self.default_delay.textChanged.connect(lambda: self.on_default_input_changed(self.default_delay, SettingText.click_delay, use_default_delay))
                self.default_delay.textChanged.connect(lambda: on_input_change(type=InputChange.setting_window))
                use_default_delay.checkStateChanged.connect(lambda: self.on_setting_changed(use_default_delay.isChecked, SettingText.delay_error_use_default))
                self.default_time.textChanged.connect(lambda: self.on_default_input_changed(self.default_time, SettingText.click_times, use_default_time))
                self.default_time.textChanged.connect(lambda: on_input_change(type=InputChange.setting_window))
                use_default_time.checkStateChanged.connect(lambda: self.on_setting_changed(use_default_time.isChecked, SettingText.times_error_use_default))
                self.delay_combo.currentIndexChanged.connect(lambda: self.on_setting_changed(self.delay_combo.currentIndex, SettingText.delay_unit))
                self.delay_combo.currentIndexChanged.connect(lambda: on_input_change(type=InputChange.setting_window))
                self.times_combo.currentIndexChanged.connect(lambda: self.on_setting_changed(self.times_combo.currentIndex, SettingText.times_unit))
                self.times_combo.currentIndexChanged.connect(lambda: on_input_change(type=InputChange.setting_window))
            case self.page_hotkey:
                set_content_label(get_lang('21'))
                
                self.hotkey_enabled = UCheckBox(get_lang('c9')) # 热键启用
                self.hotkey_enabled.setChecked(setting_value.hotkey_enabled)
                
                # 左键连点
                self.left_click_layout = QHBoxLayout()
                self.left_click_input = UHotkeyLineEdit() # 左键连点输入框
                self.left_click_input.setText(format_keys(setting_value.left_click_hotkey))
                self.left_repair_button = QPushButton(get_lang('20')) # 还原默认设置按钮
                
                # 布局 
                self.left_click_layout.addWidget(QLabel(f'{get_lang('0c')}: '), 1) # 左键连点提示
                self.left_click_layout.addWidget(self.left_click_input, 6)
                self.left_click_layout.addWidget(self.left_repair_button, 1)
                self.left_click_layout.addStretch()
                
                # 右键连点
                self.right_click_layout = QHBoxLayout() # 右键连点布局
                self.right_click_input = UHotkeyLineEdit() # 右键连点输入框
                self.right_repair_button = QPushButton(get_lang('20')) # 还原默认设置按钮
                
                self.right_click_input.setText(format_keys(setting_value.right_click_hotkey))
                
                # 布局
                self.right_click_layout.addWidget(QLabel(f'{get_lang('0d')}: '), 1) # 右键连点提示
                self.right_click_layout.addWidget(self.right_click_input, 6)
                self.right_click_layout.addWidget(self.right_repair_button, 1)
                self.right_click_layout.addStretch()
                
                # 暂停/重启连点
                self.pause_click_layout = QHBoxLayout() # 暂停/重启连点布局
                self.pause_click_input = UHotkeyLineEdit() # 暂停/重启连点输入框
                self.pause_click_input.setText(format_keys(setting_value.pause_click_hotkey))
                self.pause_repair_button = QPushButton(get_lang('20')) # 还原默认设置按钮
                
                # 布局
                self.pause_click_layout.addWidget(QLabel(f'{get_lang('6b')}: '), 1) # 暂停/重启连点提示
                self.pause_click_layout.addWidget(self.pause_click_input, 6)
                self.pause_click_layout.addWidget(self.pause_repair_button, 1)
                self.pause_click_layout.addStretch()
                
                # 停止连点
                self.stop_click_layout = QHBoxLayout() # 停止连点布局
                self.stop_click_input = UHotkeyLineEdit() # 停止连点输入框
                self.stop_click_input.setText(format_keys(setting_value.stop_click_hotkey))
                self.stop_repair_button = QPushButton(get_lang('20')) # 还原默认设置按钮
                
                # 布局
                self.stop_click_layout.addWidget(QLabel(f'{get_lang('6c')}: '), 1) # 停止连点提示
                self.stop_click_layout.addWidget(self.stop_click_input, 6)
                self.stop_click_layout.addWidget(self.stop_repair_button, 1)
                self.stop_click_layout.addStretch()
                
                # 主窗口
                self.main_window_layout = QHBoxLayout() # 主窗口布局
                self.main_window_input = UHotkeyLineEdit() # 主窗口输入框
                self.main_window_input.setText(format_keys(setting_value.main_window_hotkey))
                self.main_window_button = QPushButton(get_lang('20')) # 还原默认设置按钮

                # 布局
                self.main_window_layout.addWidget(QLabel(f'{get_lang('76')}: '), 1) # 主窗口提示
                self.main_window_layout.addWidget(self.main_window_input, 6)
                self.main_window_layout.addWidget(self.main_window_button, 1)
                self.main_window_layout.addStretch()

                # 布局
                layout.addWidget(self.hotkey_enabled)
                layout.addLayout(self.left_click_layout)
                layout.addLayout(self.right_click_layout)
                layout.addLayout(self.pause_click_layout)
                layout.addLayout(self.stop_click_layout)
                layout.addLayout(self.main_window_layout)
                
                # 连接信号
                self.left_click_input.textChanged.connect(lambda: self.on_setting_changed(lambda: parse_hotkey(self.left_click_input), SettingText.left_click_hotkey))
                self.right_click_input.textChanged.connect(lambda: self.on_setting_changed(lambda: parse_hotkey(self.right_click_input), SettingText.right_click_hotkey))
                self.pause_click_input.textChanged.connect(lambda: self.on_setting_changed(lambda: parse_hotkey(self.pause_click_input), SettingText.pause_click_hotkey))
                self.stop_click_input.textChanged.connect(lambda: self.on_setting_changed(lambda: parse_hotkey(self.stop_click_input), SettingText.stop_click_hotkey))
                self.main_window_input.textChanged.connect(lambda: self.on_setting_changed(lambda: parse_hotkey(self.main_window_input), SettingText.main_window_hotkey))

                self.left_repair_button.clicked.connect(lambda: self.repair_settings(SettingText.left_click_hotkey))
                self.right_repair_button.clicked.connect(lambda: self.repair_settings(SettingText.right_click_hotkey))
                self.pause_repair_button.clicked.connect(lambda: self.repair_settings(SettingText.pause_click_hotkey))
                self.stop_repair_button.clicked.connect(lambda: self.repair_settings(SettingText.stop_click_hotkey))
                self.main_window_button.clicked.connect(lambda: self.repair_settings(SettingText.main_window_hotkey))
                
                self.hotkey_enabled.checkStateChanged.connect(self.on_enable_hotkey_changed)
                self.on_enable_hotkey_changed(self.hotkey_enabled.isChecked())

        restart_layout = QHBoxLayout() # 重启提示布局
        self.restart_button = QPushButton(get_lang('7e'))

        set_style(self.restart_button, StyleClass.selected)
        self.restart_button.clicked.connect(self.restart)
        
        restart_layout.addStretch()
        restart_layout.addWidget(self.restart_button)
        
        if not settings_need_restart:
            self.restart_button.hide()
        
        layout.addLayout(restart_layout)

        # 添加弹簧，让内容靠上显示
        layout.addStretch()

        return page
    
    def on_enable_hotkey(self, state):
        '''启用热键'''
        # 输入框
        self.left_click_input.setEnabled(state)
        self.right_click_input.setEnabled(state)
        self.pause_click_input.setEnabled(state)
        self.stop_click_input.setEnabled(state)
        self.main_window_input.setEnabled(state)
        
        # 按钮
        self.left_repair_button.setEnabled(state)
        self.right_repair_button.setEnabled(state)
        self.pause_repair_button.setEnabled(state)
        self.stop_repair_button.setEnabled(state)
        self.main_window_button.setEnabled(state)
        
    def on_enable_hotkey_changed(self, state):
        '''热键复选框状态改变'''
        self.on_enable_hotkey(state)
        self.on_setting_changed(self.hotkey_enabled.isChecked, SettingText.hotkey_enabled)
        
    def repair_auto_start(self):
        logger.info('Repair auto start')
        os.remove(Path(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup', 'Clickmouse.lnk'))
        auto_start_manager.create_reg()
        UMessageBox.information(self, get_lang('16'), get_lang('d2'))

    def showEvent(self, event):
        '''窗口显示事件'''
        return super().showEvent(event)
    
    def repair_settings(self, key: str):
        '''还原默认设置'''
        global settings
        if UMessageBox.warning(self, get_lang('15'), get_lang('22'), MessageButtonTemplate.YESNO) != 2: # 不确认重置
            return
        try:
            del settings[key]
        except KeyError:
            pass
        save_settings()
        self.window_restarted.emit()
            
    def repair_all_settings(self):
        logger.info('Reset all settings')
        global settings
        if UMessageBox.warning(self, get_lang('15'), get_lang('22'), MessageButtonTemplate.YESNO) != 2: # 不确认重置
            return
        settings = {}
        save_settings()
        self.values.update({'need_restart': True}) # values 用于存储需要重启后还原的内容
        self.window_restarted.emit()

    def on_auto_start_changed(self, state):
        '''自启动复选框状态改变'''
        if state:
            auto_start_manager.enable()
        else:
            auto_start_manager.disable()
            
    def on_setting_changed(self, handle, key, *args):
        '''更新检查提示选择事件'''
        logger.info(f'Setting changed: {key}')
        settings[key] = handle(*args)
        save_settings()

    def on_need_restart_setting_changed(self, handle, key: str, restart_place: list[str] = ['a9'], *args):
        '''托盘图标选择事件'''
        global settings_need_restart

        self.on_setting_changed(handle, key, *args)
        settings_need_restart = True

        lang = self.lang_choice.currentIndex()

        restart_place = list(map(lambda x: get_lang(x, lang_id=lang), restart_place))

        selected_lang_yes = CustonMessageButton(get_lang('01', source=default_button_text, lang_id=lang), UMessageBox.YesRole)
        selected_lang_no = CustonMessageButton(get_lang('02', source=default_button_text, lang_id=lang), UMessageBox.AcceptRole)
        need_restart = UMessageBox.warning(self, get_lang('15', lang_id=lang), f'{get_lang("89", lang_id=lang)}: {", ".join(restart_place)}', [selected_lang_yes, selected_lang_no], selected_lang_yes)
        if need_restart == 2:
            self.restart()
        else:
            self.restart_window()

    def restart_window(self):
        self.window_restarted.emit()

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
            UMessageBox.critical(self, get_lang('14'), get_lang('aa'))
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
        app.quit(lambda: run_software('clickclean.py', 'clickclean.exe'))

    def init_right_pages(self):
        super().init_right_pages()
        set_style(self.buttons[0], StyleClass.selected)

    def on_clicker_started(self):
        '''连点器启动事件'''
        if self.now_page == self.page_choice_buttons.index(get_lang('43')):
            self.on_page_button_clicked(self.last_page)
            UMessageBox.critical(self, get_lang('14'), get_lang('aa'))
            return

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

        # 创建热键监听器
        self.hotkey_listener = get_hotkey_listener_instance()
        self.hotkey_listener.combination_pressed.connect(self.run_combination)

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

        left_click_action.triggered.connect(lambda: self.on_combination_pressed(setting_value.left_click_hotkey))
        right_click_action.triggered.connect(lambda: self.on_combination_pressed(setting_value.right_click_hotkey))
        pause_action.triggered.connect(lambda: self.on_combination_pressed(setting_value.pause_click_hotkey))
        stop_action.triggered.connect(lambda: self.on_combination_pressed(setting_value.stop_click_hotkey))
        
        tray_menu.addAction(left_click_action)
        tray_menu.addAction(right_click_action)
        tray_menu.addAction(pause_action)
        tray_menu.addAction(stop_action)

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
            self.refresh()

    def check_delay(self, input_delay):
        try:
            math.ceil(float(input_delay))
        except Exception:
            trace = format_exc()
            UMessageBox.critical(main_window, get_lang('13'), f'{get_lang('ae')}\n{trace}')
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
        if can_update:
            run_software('updater.old/updater.py', 'updater.old/updater.exe')
        else:
            self.quit()
        logger.info(f'Main program exited with {code}')
        sys.exit(code)

    def refresh(self):
        refresh.run()
        
    def quit(self, code=lambda: None):
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
            self.refresh()
    
    def on_combination_pressed(self, combination):
        '''处理组合键事件'''
        combination = format_keys(combination, source=True)

        if all_in_list(combination, setting_value.main_window_hotkey):
            # 处理主窗口组合键
            self.show_window(main_window)
            if not main_window.isVisible():
                main_window.is_start_from_tray = True
        elif all_in_list(combination, setting_value.left_click_hotkey):
            self.on_start_clicker_tray('left') # 左键
        elif all_in_list(combination, setting_value.right_click_hotkey):
            self.on_start_clicker_tray('right') # 右键
        elif all_in_list(combination, setting_value.pause_click_hotkey):
            if clicker.running:
                clicker.pause_click()
                if clicker.paused:
                    self.tray_icon.showMessage(get_lang('6e'), get_lang('71'), QSystemTrayIcon.MessageIcon.Information, 1000)
                else:
                    self.tray_icon.showMessage(get_lang('6e'), get_lang('72'), QSystemTrayIcon.MessageIcon.Information, 1000)
            else:
                self.tray_icon.showMessage(get_lang('6e'), get_lang('74'), QSystemTrayIcon.MessageIcon.Warning, 1000)
        elif all_in_list(combination, setting_value.stop_click_hotkey):
            if clicker.running:
                main_window.on_stop()
                self.tray_icon.showMessage(get_lang('6e'), get_lang('73'), QSystemTrayIcon.MessageIcon.Information, 1000)
            else:
                self.tray_icon.showMessage(get_lang('6e'), get_lang('74'), QSystemTrayIcon.MessageIcon.Warning, 1000)

if __name__ == '__main__':
    shared_memory = QSharedMemory('clickmouse_running')
    if shared_memory.attach():
        # 已经有一个实例在运行
        sys.exit(2)
    shared_memory.create(1)

    data_path = Path('data')

    logger.info('Loading services')
    setting_value = SettingValue()
    clicker = Click()
    auto_start_manager = StartManager()
    color_getter = ColorGetter()

    # 变量
    logger.info('Define pathes')

    # 定义数据路径
    cache_path = Path('cache')
    update_cache_path = cache_path / 'update.json'

    # 创建文件夹（如果不存在）
    data_path.mkdir(parents=True, exist_ok=True)
    cache_path.mkdir(parents=True, exist_ok=True)

    # 创建资源
    icon = get_icon('icon')
    
    settings_need_restart = False
    can_update = False

    # 单位控制
    latest_index = 2
    select_lang = setting_value.select_lang

    # 其他
    can_run_hotkey = True # 热键是否可用
    
    # 加载窗口
    logger.info('Loading ui')
    main_window = MainWindow()
    on_input_change(type=InputChange.main_window) # 更新时间估计状态

    about_window = AboutWindow()
    setting_window = SettingWindow()
    on_input_change(type=InputChange.setting_window) # 更新时间估计状态
    setting_window.click_setting_changed.connect(lambda: on_input_change(type=InputChange.setting_window))
    setting_window.window_restarted.connect(on_update_setting_window)

    app = TrayApp()
    app.run()