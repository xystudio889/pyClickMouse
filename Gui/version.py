"""读取版本号信息"""
import sharelibs

with open(sharelibs.get_resource_path('version'), 'r') as f:
    version = f.read()

__version__ = version    
__author__ = "xystudio"