---
title: Configuring Repository
description: Introduction to how to configure repository
layout: doc
---
<script setup>
    import warning from '@theme/components/warning.vue'
</script>
# Configuring Repository
1. Download repository: `git clone https://github.com/xystudiocode/pyclickmouse.git`
2. For python version install python, recommend using 3.13, consistent with software developer's version, [download link](https://www.python.org/downloads/release/python-31312/)
3. For header files and dll version, can install [visual studio](https://visualstudio.microsoft.com/).
## GUI Version
1. Download source code
2. Place a `7z.exe` and `7z.dll` in `gui` directory
3. Install chocolately
```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```
4. Install make tool
```powershell
choco install make
```
5. Configure python packages
```powershell
pip install -r requirements.txt
```
6. Compile
```powershell
make clickmouse # compile clickmouse
make extension # compile extension
make clickclean # if you want to make clean version, please run this command
```
7. Run `dist/clickmouse/main.exe` to load clickmouse.
## Header Files
Only need to modify header files, can be called
## dll Calling
Use visual studio modify `./dll/dll.sln` inside `source files/dllmain.cpp`
## GUI Old Version
<warning title="Note">GUI old version recompilation does not accept pull request</warning>
Use visual studio modify `./ClickMouse-old/ClickMouse.sln` inside `source files/clickmouse.cpp`
## python Library Calling
Modify code under `clickmouse/`, run `pip install .` to install
## pyd Calling
Modify code of `cython/main.py`, then execute
```python cython/setup.py build_ext --inplace```
After compilation ends, there should be a file ending with `.pyd` in this directory.