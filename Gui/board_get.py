from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication
import sys
from pynput import keyboard
import threading
from pynput.keyboard import Key, KeyCode

def get_application_instance():
    '''获取或创建 QApplication 实例'''
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app

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

class MyApp:
    def __init__(self):
        self.app = get_application_instance()
        self.app.setQuitOnLastWindowClosed(False)  # 关闭窗口时不退出应用
        
        # 创建热键监听器
        self.hotkey_listener = HotkeyListener()
        self.hotkey_listener.pressed_key.connect(self.on_key_pressed)
        self.hotkey_listener.combination_pressed.connect(self.on_combination_pressed)  # 连接组合键信号
        self.start_hotkey_listener()
        
    def start_hotkey_listener(self):
        '''启动热键监听器（在单独的线程中）''' 
        # 在后台线程中启动热键监听
        hotkey_thread = threading.Thread(target=self.hotkey_listener.start_listening)
        hotkey_thread.daemon = True  # 设置为守护线程，主程序退出时自动结束
        hotkey_thread.start()
    
    def on_key_pressed(self, key):
        '''处理单个按键事件'''
        # 这里可以保留原来的按键打印，或注释掉以减少输出
        pass
    
    def on_combination_pressed(self, combination):
        '''处理组合键事件'''
        print(combination)

    def quit_application(self):
        '''退出应用程序'''
        # 停止热键监听
        self.hotkey_listener.stop_listening()
        self.app.quit()
    
    def run(self):
        '''运行应用程序'''
        sys.exit(self.app.exec())

if __name__ == '__main__':
    app = MyApp()
    app.run()