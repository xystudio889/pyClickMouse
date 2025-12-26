import re

def replace_background_color(css_text):
    # 使用正则表达式匹配 background-color 属性及其值
    pattern = r'background-color\s*:\s*[^;]+;?'
    # 替换为 white
    replacement = 'background-color: white;'
    
    # 进行替换，并确保后面有分号
    result = re.sub(pattern, replacement, css_text, flags=re.IGNORECASE)
    return result

# 示例使用
css_code = """
a {
    background-color: #fb900;
    color: white;
}
"""

new_css = replace_background_color(css_code)
print(new_css)