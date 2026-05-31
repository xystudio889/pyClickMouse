import os 
import json

# 判断扩展包生命文件合法
if not(os.path.exists('packages.json')):
    raise ImportError('clickmouse扩展包声明文件packages.json未设置')

try:
    with open('packages.json', 'r', encoding='utf-8') as f:
        packages = json.load(f)
except json.JSONDecodeError:
    raise ImportError('clickmouse扩展包声明文件packages.json格式错误')