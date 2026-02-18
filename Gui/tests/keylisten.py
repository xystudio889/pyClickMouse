from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QObject, Signal
from pynput import keyboard

# 假设你已经有了 HotkeyListener 类
# 这里为完整起见，简要复述你的类（仅作参考）
class HotkeyListener(QObject):
    '''热键监听器类，用于在后台线程中监听全局热键'''
    pressed_key = Signal(keyboard.Key)
    combination_pressed = Signal(list)  # 用于发送组合键信息

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

        self.combination()

    def on_key_release(self, key):
        '''处理按键释放事件'''
        # 从集合中移除释放的键
        if key in self.pressed_keys:
            self.pressed_keys.remove(key)

    def combination(self):
        '''发送特定的组合键'''
        self.combination_pressed.emit(list(map(str, self.pressed_keys)))  # 发送组合键
        
def format_keys(keys_str_list):
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
        priority = {'Win': 1, 'Ctrl': 2, 'Alt': 3, 'Shift': 4} # 按优先级排序
        def get_priority(key):
            if key in priority:
                return priority[key]
            elif len(key) == 1:   # 单个字符（字母、数字、符号等）
                return 6
            else:                 # 其他多字符键
                return 5
        return '+'.join(sorted(out_list, key=get_priority)) # 按优先级排序并连接

class HotkeyLineEdit(QLineEdit):
    '''能够捕获热键组合的输入框，只有获得焦点时才更新'''
    def __init__(self, parent=None):
        super().__init__(parent)
        self._connection = None  # 保存信号连接对象
        self.key_list = []  # 保存按下的热键
        self.setReadOnly(True)
        self.listener =  HotkeyListener()
        self.listener.start_listening()

    def focusInEvent(self, event):
        '''获得焦点时连接信号'''
        if self._connection is None:
            # 连接信号，使用 Qt.QueuedConnection 确保线程安全（默认 Auto 已经足够）
            self._connection = self.listener.combination_pressed.connect(
                self.on_combination_pressed,
                Qt.QueuedConnection
            )
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        '''失去焦点时断开连接'''
        if self._connection is not None:
            # 断开连接
            self.listener.combination_pressed.disconnect(self.on_combination_pressed)
            self._connection = None
        super().focusOutEvent(event)

    def on_combination_pressed(self, keys_str_list):
        '''处理组合键信号，将列表格式化为字符串并显示'''
        self.key_list = format_keys(keys_str_list)
        self.setText(self.key_list)

class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Hotkey Example')
        self.setFixedSize(300, 100)
        
        widget = QWidget(self)
        layout = QVBoxLayout(widget)
        self.line_edit = HotkeyLineEdit(widget)
        
        self.line_edit2 = HotkeyLineEdit(widget)
        layout.addWidget(self.line_edit2)
        layout.addWidget(self.line_edit)
        self.setCentralWidget(widget)

if __name__ == '__main__':
    app = QApplication([])
    main = Main()
    main.show()
    app.exec()