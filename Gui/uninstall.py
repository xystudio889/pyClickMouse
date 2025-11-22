from tkinter import messagebox
import os
import sys
import ctypes
import tempfile
import subprocess
import json
import shutil
import winreg

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False
    
def run_as_admin():
    ctypes.windll.shell32.ShellExecuteW(
        None, 'runas', sys.executable, ' '.join(sys.argv), None, 1
    )
    with open('run_as_admin.json', 'w') as f:
        json.dump({'is_not_admin': 1}, f)
    sys.exit(0)

def create_bat_cleaner(script_path):
    bat_content = f"""
    @echo off
    :loop
    del "{script_path}" >nul 2>&1
    if exist "{script_path}" (
        timeout /t 1 /nobreak >nul
        goto loop
    )
    del "%~f0"
    """
    bat_path = os.path.join(tempfile.gettempdir(), "cleanup.bat")
    with open(bat_path, "w") as f:
        f.write(bat_content)
    return bat_path

def remove_reg_key(sub_key):
    root_key = winreg.HKEY_LOCAL_MACHINE
    try:
        # 以写入权限打开父键
        parent_key = winreg.OpenKey(root_key, sub_key, 0, winreg.KEY_ALL_ACCESS)
        
        # 先删除所有子项（递归处理）
        while True:
            try:
                child_subkey = winreg.EnumKey(parent_key, 0)  # 获取第一个子项
                remove_reg_key(root_key, f"{sub_key}\\{child_subkey}")
            except OSError:  # 没有更多子项时抛出OSError
                break
        
        # 删除所有键值
        while True:
            try:
                value_name = winreg.EnumValue(parent_key, 0)[0]  # 获取第一个键值名
                winreg.DeleteValue(parent_key, value_name)
            except OSError:  # 没有更多键值时抛出OSError
                break
        
        # 关闭父键后删除空项
        winreg.CloseKey(parent_key)
        winreg.DeleteKey(root_key, sub_key)
    except:
        pass

def read_reg_key(key, value):
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key, 0, winreg.KEY_READ) as k:
            return winreg.QueryValueEx(k, value)[0]
    except:
        return None

def main():
    script_path = read_reg_key(r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\clickmouse", "UninstallString")
    if not script_path:
        messagebox.showerror("错误", "无法定位clickmouse的卸载脚本，有可能是注册表损坏或权限问题")
    script_dir = os.path.dirname(script_path)
    
    if not os.path.exists(script_path):
        messagebox.showerror("错误", f"无法找到clickmouse的卸载脚本：{script_path}")
        sys.exit(1)

    bat_path = create_bat_cleaner(script_path)
    subprocess.Popen(['cmd', '/c', bat_path], shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
    
    with open(os.path.join(script_dir, "package.json"), "r") as f:
        data = json.load(f)
        created_desktop_shortcut = data["create_desktop_shortcut"]
        created_startmenu_shortcut = data["create_in_start_menu"]
        startmenu_shortcut_name = data["start_menu_name"]
    
    for root, dirs, files in os.walk(script_dir):
        for file in files:
            try:
                os.remove(os.path.join(root, file))
            except:
                pass
        for dir in dirs:
            shutil.rmtree(os.path.join(root, dir), ignore_errors=True)
    
    # 删除快捷方式
    if created_desktop_shortcut:
        try:
            os.remove(os.path.join(os.path.expanduser("~"), "Desktop", "clickmouse.lnk"))
        except:
            pass
    if created_startmenu_shortcut:
        try:
            os.remove(os.path.join(fr"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\{startmenu_shortcut_name}"))
        except:
            pass
    
    remove_reg_key(r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\clickmouse")
    
    messagebox.showinfo("提示", f"程序已成功卸载，但是部分内容可能有残留，请尽快重启并删除这个文件夹：{script_dir}")
                
if __name__ == "__main__":
    if is_admin():
        if os.path.exists('run_as_admin.json'):
            os.remove('run_as_admin.json')
        if messagebox.askyesno("提示", "是否卸载clickmouse和其相关组件？"):
            main()
    else:
        try:
            with open('run_as_admin.json', 'r') as f:
                data = json.load(f).get('is_not_admin', 0)
        except:
            data = 0
        if data == 0:
            run_as_admin()
        elif data == 1:
            messagebox.showerror("错误", "请以管理员身份运行！")
            os.remove('run_as_admin.json')
