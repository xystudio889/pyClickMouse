def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False
    
def run_as_admin(code, exe, args=None):
    args_list = []
    if in_dev:
        args_list.append(code)
    if args:
        args_list.extend(args)
    subprocess.Popen(f'powershell -Command "Start-Process \'{"python" if in_dev else exe}\' {f'-ArgumentList "{' '.join(args_list)}"' if args_list else ''} -Verb RunAs"')

if __name__ == '__main__':
    import winreg
    import json
    import ctypes
    import subprocess
    import os
    import sys

    with open('res/versions.json', 'r') as f:
        __version__ = json.load(f)['clickmouse']
    in_dev = os.path.exists('dev_list/in_dev') # 是否处于开发模式

    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\clickmouse', access=winreg.KEY_READ) as key: # 打开注册表
            version, _ = winreg.QueryValueEx(key, 'DisplayVersion')
            version_diff = version != __version__ # 版本不一致
    except FileNotFoundError:
        os.remove('data/first_run')
        run_as_admin('main.py', 'main.exe')
        sys.exit(1)

    if is_admin():
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\clickmouse', access=winreg.KEY_WRITE) as key: # 打开注册表
            if version_diff:
                winreg.SetValueEx(key, 'DisplayVersion', 0, winreg.REG_SZ, __version__) # 更新注册表
    else:
        if version_diff:
            run_as_admin('check_reg_ver.py', 'check_reg_ver.exe')