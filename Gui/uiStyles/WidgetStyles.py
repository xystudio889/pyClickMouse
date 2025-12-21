'''
组件样式
'''
from sharelibs import get_resource_path
import os
import json

styles = {}
style_path = 'styles/'

for root, dirs, files in os.walk(get_resource_path(style_path)):
    for dir in dirs:
        styles[dir] = {}
    
    for file in files:
        if file.endswith('.qss'):
            with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                styles[os.path.basename(root)][os.path.splitext(file)[0]] = f.read()

with open(get_resource_path(style_path, 'indexes.json'), 'r', encoding='utf-8') as f:
    indexes = json.load(f)
    
with open(get_resource_path(style_path, 'maps.json'), 'r', encoding='utf-8') as f:
    maps = json.load(f)

with open(get_resource_path(style_path, 'style_attrs.json'), 'r', encoding='utf-8') as f:
    style_attrs = json.load(f)