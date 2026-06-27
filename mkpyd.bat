@echo off
setlocal enabledelayedexpansion

set versions=3.8 3.9 3.10 3.11 3.12 3.13 3.14 3.15 3.13t 3.14t 3.15t
set setupPath=setup.py
set pydPath="src\clickmouse\"

for %%i in (%versions%) do (
    py -V:%%i %setupPath% build_ext --inplace || echo "Python %%i is not installed."
)

del build\ clickmouse.egg-info %pydPath%\*.c /s /q /f

set "merged="

:: 处理第一个列表
for %%a in (%versions%) do (
    set "item=%%a"
    set "item=!item:.=!"
    set "merged=!merged! !item!"
)

echo Merged items: !merged!

for %%i in (%merged%) do (
    ren %pydPath%__init__.cp%%i-win_amd64.pyd clickmouse.cp%%i-win_amd64.pyd || echo Renaming failed for __init__.cp%%i-win_amd64.pyd.
)