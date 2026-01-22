import winreg
import json
from sharelibs import get_resource_path, run_as_admin, is_admin

with open(get_resource_path('versions.json'), 'r') as f:
    __version__ = json.load(f)['clickmouse']
    
with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\clickmouse', access=winreg.KEY_READ) as key: # 打开注册表
    version, _ = winreg.QueryValueEx(key, 'DisplayVersion')
    version_diff = version != __version__ # 版本不一致

if is_admin():
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\clickmouse', access=winreg.KEY_WRITE) as key: # 打开注册表
        if version_diff:
            winreg.SetValueEx(key, 'DisplayVersion', 0, winreg.REG_SZ, __version__) # 更新注册表
else:
    if version_diff:
        print('请以管理员身份运行')
        run_as_admin('check_reg_ver.py', 'check_reg_ver.exe')