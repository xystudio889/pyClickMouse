"""
ClickMouse - pyd库
---
该库提供了鼠标点击操作的函数。

使用方法：
import clickmouse

# 点击鼠标左键
clickmouse.click_mouse(clickmouse.LEFT, 100, 100, 10) # 鼠标左键点击10次，延迟为100毫秒，按下时间为100毫秒
clickmouse.click_mouse(clickmouse.RIGHT, 100, 100, 10) # 鼠标右键点击10次，延迟为100毫秒，按下时间为100毫秒
"""

# 需要的库和功能
from clickmouse import *
from clickmouse import __author__, __version__