"""这个是使用setuptools打包的脚本，用于安装使用python调用的clickmouse工具
这个库仅供开发人员使用，普通人请前往github releases(https://github.com/xystudio/pyClickMouse/releases)
推荐通过'pip install clickmouse'安装，若网络较差，可以使用清华镜像源'pip install clickmouse -i https://pypi.tuna.tsinghua.edu.cn/simple'
若要下载本地安装包，建议下载whl格式的安装包，下载地址：https://github.com/xystudio/pyClickMouse/releases，下载结束后在下载位置打开命令行，运行'python setup.py install'"""

# 以下为setup.py文件内容
# 导入setuptools模块
import setuptools
import sys

args = sys.argv[1:] + ['']

if "build_ext" in args:
    from Cython.Build import cythonize

    ext_modules = cythonize(["src/clickmouse/__init__.py"]) # 编译main.py为.pyd文件
else:
    ext_modules = None # 不需要编译main.py为.pyd文件

with open("README.md", "r", encoding="utf-8") as f:
    markdown = f.read()

with open("README-zh_CN.md", "r", encoding="utf-8") as f:
    markdown += '\n\n' + f.read()

# 定义setup函数
setuptools.setup(
    name="ClickMouse", # 包名
    version="3.3.0alpha6", # 版本号
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    author="xystudio", # 作者
    author_email="173288240@qq.com", # 作者邮箱 
    description="基于Python的鼠标连点工具", # 包描述
    url="https://github.com/xystudiocode/pyClickMouse", # 包的github地址
    long_description=markdown, # 包的readme文件
    long_description_content_type="text/markdown", # 指定readme文件格式为markdown
    classifiers=[ # 包的分类列表
        "Programming Language :: Python :: 3", # python版本
        "License :: OSI Approved :: MIT License", # 许可证
        "Operating System :: OS Independent",# 系统
    ],
    keywords=["mouse", "click", "automation", "clickmouse"], # 包的关键字列表
    python_requires='>=3.10', # python版本要求
    install_requires=['pyautogui', 'PySide6>=6.10.0', 'nuitka>=4'], # 依赖的包列表
    entry_points={ # 脚本入口
        "console_scripts": [
            "clickmouse = clickmouse.__main__:main",
            "clickmouse-apiCli = clickmouse_api.__main__:main"
        ]
    }, 
    ext_modules=ext_modules, # 编译main.py为.pyd文件
)
