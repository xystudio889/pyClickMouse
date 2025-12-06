'''
组件样式
'''
from sharelibs import get_style_sheet, replace_style_sheet, is_dark_mode
from time import sleep
from threading import Thread

big_title = get_style_sheet('big_text')
selected_style = get_style_sheet('selected_button')
light_mode = get_style_sheet('light')
dark_mode = get_style_sheet('dark')
if is_dark_mode():
    default_style = dark_mode
else:
    default_style = light_mode
