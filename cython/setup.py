"""这个是使用setuptools打包的脚本，用于安装使用pyd调用的clickmouse工具
这个库仅供开发人员使用，普通人请前往github releases(https://github.com/xystudio/pyClickMouse/releases)下载安装包
"""
# 导入模块
from setuptools import setup
from Cython.Build import cythonize

# 定义setup函数
setup(
    ext_modules=cythonize(["main.py"]), # 编译main.py为.pyd文件
    install_requires=["clickmouse"],  # 依赖模块
)