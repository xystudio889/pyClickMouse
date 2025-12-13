"""读取版本号信息"""
import json
from sharelibs import get_resource_path

with open(get_resource_path('versions.json'), 'r') as f:
    __version__ = json.load(f)['clickmouse']
 
__author__ = "xystudio"