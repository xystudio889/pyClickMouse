'''
组件样式
'''
from sharelibs import get_style_sheet, replace_style_sheet, is_dark_mode

big_title = get_style_sheet('big_text')
selected_style = get_style_sheet('selected_button')
light_mode = get_style_sheet('styles/light')
dark_mode = get_style_sheet('styles/dark')
if is_dark_mode():
    default_style = dark_mode
else:
    default_style = light_mode
