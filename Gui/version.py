"""读取版本号信息"""

with open("res/version", "r") as f:
    __version__ = f.read()
__author__ = "xystudio"