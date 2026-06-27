from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication
from pynput import keyboard
import re

count = 0

def multi_replace(text, replace_dict):
    '''一次性替换多个子串'''
    # 将字典键按长度降序排序，避免长词被短词部分覆盖
    sorted_keys = sorted(replace_dict.keys(), key=len, reverse=True)
    # 构建正则模式，注意转义特殊字符
    pattern = '|'.join(re.escape(key) for key in sorted_keys)
    return re.sub(pattern, lambda m: replace_dict[m.group(0)], text)

class HotkeyListener(QObject):
    '''热键监听器类，用于在后台线程中监听全局热键'''
    combination_pressed = Signal(list)  # 新增信号，用于发送组合键信息
    
    def __init__(self):
        super().__init__()
        self.listener = None
        self.is_listening = False
        self.pressed_keys = set()  # 用于跟踪当前按下的键
    
    def start_listening(self):
        '''开始监听热键''' 
        try:
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
        except Exception as e:
            print(e)
    
    def stop_listening(self):
        '''停止监听热键'''
        if self.listener and self.is_listening:
            self.is_listening = False
            self.listener.stop()
    
    def on_key_press(self, key):
        '''处理按键按下事件'''
        # 将按下的键添加到集合中
        self.pressed_keys.add(key)
        
        # 检查是否为Ctrl+Alt+A组合键
        self.check_combination()
    
    def on_key_release(self, key):
        '''处理按键释放事件'''
        # 从集合中移除释放的键
        if key in self.pressed_keys:
            self.pressed_keys.remove(key)
    
    def check_combination(self):
        '''检查特定的组合键'''
        self.combination_pressed.emit(list(map(str, self.pressed_keys)))  # 发送组合键信息

class KeyListen(QObject):
    def __init__(self):
        super().__init__()
        self.hotkey_listener = HotkeyListener()
        self.hotkey_listener.combination_pressed.connect(self.combination_pressed)

    def combination_pressed(self, combination):
        '''处理组合键事件'''
        global count
        temp_combination = combination.copy()
        
        for index, i in enumerate(temp_combination):
            replacements = {
                'Key.': '',
                '_l': '',
                '_r': '',
                '_gr': ''
            }
            temp_combination[index] = multi_replace(i, replacements)
        combination = temp_combination.copy()

        print(combination)
        count += 1
        if count >= 20:
            print('测试结束')
            app = QApplication.instance()
            app.quit()
        
if __name__ == '__main__':
    app = QApplication([])
    key_listen = KeyListen()
    key_listen.hotkey_listener.start_listening()
    app.exec()