
from PySide6.QtWidgets import QApplication, QMessageBox
import os
import sys
import ctypes
import tempfile
import subprocess
import shutil
import winreg
from sharelibs import get_control_lang, is_process_running
from pathlib import Path

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def create_bat_cleaner(script_path):
    bat_content = f'''
    @echo off
    :loop
    del '{script_path}' >nul 2>&1
    if exist '{script_path}' (
        timeout /t 1 /nobreak >nul
        goto loop
    )
    del '%~f0'
    '''
    bat_path = os.path.join(tempfile.gettempdir(), 'cleanup.bat')
    with open(bat_path, 'w') as f:
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
                remove_reg_key(root_key, f'{sub_key}\\{child_subkey}')
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
    script_path = Path.cwd()
    if not script_path:
        QMessageBox.critical(None, get_control_lang('01'), get_control_lang('02'))
    script_dir = os.path.dirname(script_path)

    bat_path = create_bat_cleaner(script_path)
    
    for root, dirs, files in os.walk(script_dir):
        for file in files:
            try:
                os.remove(os.path.join(root, file))
            except:
                pass
        for dir in dirs:
            shutil.rmtree(os.path.join(root, dir), ignore_errors=True)
    
    # 删除快捷方式
    try:
        os.remove(os.path.join(os.path.expanduser('~'), 'Desktop', 'clickmouse.lnk'))
    except:
        pass

    try:
        shutil.rmtree(os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start menu', 'Programs', 'Clickmouse'), ignore_errors=True)
    except:
        pass
    
    subprocess.Popen(['cmd', '/c', bat_path], shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
    
    remove_reg_key(r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\clickmouse')
    
    QMessageBox.information(None, get_control_lang('04'), get_control_lang('05').format(script_dir))
                
if __name__ == '__main__':
    app = QApplication(sys.argv)
    if not(is_process_running('main.exe')):
        QMessageBox.warning(None, get_control_lang('04'), get_control_lang('08'))
    else:
        if is_admin():
            if QMessageBox.question(None, get_control_lang('04'), get_control_lang('06'), QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                main()
        else:
            QMessageBox.critical(None, get_control_lang('01'), get_control_lang('07'))
        sys.exit(app.exec())