"""
ClickMouse库
---
该库提供了鼠标点击操作的函数。

使用方法：
import clickmouse

# 点击鼠标左键
clickmouse.click_mouse(clickmouse.LEFT, 100, 100, 10) # 鼠标左键点击10次，延迟为100毫秒，按下时间为100毫秒
clickmouse.click_mouse(clickmouse.RIGHT, 100, 100, 10) # 鼠标右键点击10次，延迟为100毫秒，按下时间为100毫秒
"""

# 需要的库
import pyautogui
from typing import Literal
from time import sleep
from .version import __version__, __author__ # 导入版本号和作者信息

# 常量
INFINITE = -1
LEFT = pyautogui.LEFT
RIGHT = pyautogui.RIGHT

def click_mouse(button: Literal['left', 'right'], delay: int, time: int=1) -> None:
    '''
    按下鼠标处理函数
    :param button: 鼠标按键，可以是'left'或'right'
    :param delay: 延迟时间，单位为毫秒
    :param press_time: 按键时间，单位为毫秒
    :param time: 按键次数，-1表示无限循环
    '''
    if time == -1:
        # 无限循环
        while True:
            _click(button, delay)
    elif time > 0:
        # 有限循环
        for _ in range(time):
            _click(button, delay)
    else: 
        raise ValueError('time must be greater than or equal to 0') # 时间必须大于或等于0
    
def _click(button: Literal['left', 'right'], delay: int):
    pyautogui.click(button=button)
    sleep(delay/1000)