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
    
def remove_reg_value(key, value):
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key, 0, winreg.KEY_ALL_ACCESS) as k:
            winreg.DeleteValue(k, value)
    except:
        pass

def main():
    soft_path = Path.cwd()
    shutil.rmtree(soft_path, ignore_errors=True)
    
    # 删除快捷方式
    try:
        os.remove(os.path.join(os.path.expanduser('~'), 'Desktop', 'clickmouse.lnk'))
    except:
        pass
    shutil.rmtree(os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start menu', 'Programs', 'Clickmouse'), ignore_errors=True)
    
    remove_reg_key(r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\clickmouse')
    remove_reg_key(r'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\clickmouse')
    try:
        os.remove(os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup', 'clickmouse.lnk'))
    except:
        pass
    remove_reg_value(r'Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run', 'Clickmouse')
    
    QMessageBox.information(None, get_control_lang('04'), get_control_lang('05').format(soft_path))
    sys.exit(0)
                
if __name__ == '__main__':
    from PySide6.QtCore import QSharedMemory
    import sys
    from sharelibs import mem_id

    shared_memory = QSharedMemory(mem_id[4])
    if shared_memory.attach():
        # 已经有一个实例在运行
        sys.exit(2)
    shared_memory.create(1)
    
    from PySide6.QtWidgets import QApplication, QMessageBox
    from sharelibs import get_control_lang

    app = QApplication(sys.argv)
    is_running = any(list(map(lambda x: QSharedMemory(x).attach(), [i for i in mem_id if i != mem_id[4]])))
    if is_running:
        # 已经有一个实例在运行
        QMessageBox.critical(None, get_control_lang('04'), get_control_lang('08'))
        sys.exit(2)
        
    from sharelibs import is_admin

    if is_admin():
        if QMessageBox.question(None, get_control_lang('04'), get_control_lang('06'), QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            import os
            import shutil
            import winreg
            from pathlib import Path
            main()
        else:
            sys.exit(3)
    else:
        QMessageBox.critical(None, get_control_lang('01'), get_control_lang('07'))
        sys.exit(1)
    sys.exit(app.exec())