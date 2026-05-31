---
title: 配置仓库
description: 介绍如何配置仓库
layout: doc
---
<script setup>
    import warning from '@theme/components/warning.vue'
</script>
# 配置仓库
1. 下载仓库：`git clone https://github.com/xystudiocode/pyclickmouse.git`
2. 对于python版本安装python，推荐使用3.13，和软件开发者的版本一一致，[下载连接](https://www.python.org/downloads/release/python-31312/)
3. 对于头文件和dll版本，可以安装[visual studio](https://visualstudio.microsoft.com/)。
## GUI版本
1. 下载源码
2. 放置一个`7z.exe`和`7z.dll`到`gui`目录
3. 安装chocolately
```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```
4. 安装make工具
```powershell
choco install make
```
5. 配置python包
```powershell
pip install -r requirements.txt
```
6. 编译
```powershell
make clickmouse # 编译clickmouse
make extension # 编译扩展
make clickclean # 如果你要编译精简版，请用这个。
```
7. 运行`dist/clickmouse/main.exe`就可以加载clickmouse了。
## 头文件
仅需修改头文件，就可以被调用
## dll调用
使用visual studio修改`./dll/dll.sln`里的`源文件/dllmain.cpp`
## gui旧版本
<warning title="注意">gui旧版本的再编译不接受pull request</warning>
使用visual studio修改`./ClickMouse-old/ClickMouse.sln`里的`源文件/clickmouse.cpp`
## python库调用
修改`clickmouse/`下的代码，运行`pip install .`安装
## pyd调用
修改`cython/main.py`的代码，然后执行
```python cython/setup.py build_ext --inplace```
编译结束后，该目录下应该会有个以`.pyd`结尾的文件。