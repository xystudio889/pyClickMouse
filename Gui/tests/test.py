import psutil
import time

def wait_for_process_exit(process_name):
    '''
    等待指定进程退出
    
    Args:
        process_name: 进程名（如：notepad.exe, chrome.exe）
        check_interval: 检查间隔（秒）
    '''
    while True:
        # 查找所有匹配的进程
        running = False
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] and process_name.lower() in proc.info['name'].lower():
                    running = True
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        if not running:
            break

        time.sleep(0.0001)

# 使用示例
wait_for_process_exit('notepad.exe')