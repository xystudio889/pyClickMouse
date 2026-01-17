from PySide6.QtWidgets import QMessageBox, QApplication
import psutil
from shutil import rmtree
import os
import winreg
from sharelibs import get_control_lang

def is_process_running(process_name):
   for proc in psutil.process_iter(['name']):
       if proc.info['name'] == process_name:
           return True
   return False

def remove_file(file_path):
    try:
        os.remove(file_path)
    except:
        pass

def remove_folder(folder_path):
    try:
        rmtree(folder_path)
    except Exception as e:
        pass
    
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

if __name__ == '__main__':
    app = QApplication()
    # if is_process_running('main.exe'):
    #     QMessageBox.warning(None, get_control_lang('04'), get_control_lang('08'))
    # else:
    #     message = QMessageBox.information(None, get_control_lang('04'), get_control_lang('09'), QMessageBox.Yes | QMessageBox.No)
    #     if message == QMessageBox.Yes:
    #         remove_folder('data')
    #         remove_folder('cache')
    #         remove_folder('extensions')
    #         remove_file('packages.json')
    #         QMessageBox.information(None, get_control_lang('04'), get_control_lang('0a'))
    #     pass