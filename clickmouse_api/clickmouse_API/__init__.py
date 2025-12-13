# clickmouse_API开发工具 存储了一些本软件中，常用的的函数和类。

import winreg

init_datas = {}
        
def check_clickmouse_installed():
    software_reg_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\clickMouse'
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, software_reg_key, 0, winreg.KEY_READ):
            pass
    except:
        raise UserWarning('ClickMouse未安装！请前往https://www.github.com/xystudio889/pyclickmouse/releases下载安装.')
        
check_clickmouse_installed()

from clickmouse_API import GUI
from clickmouse_API.packageParser import packages
import os

__version__ = '1.0.1'
__author__ = 'xystudio'

def reloadData():
    '''
    重新加载数据
    '''
    pass

def init(dev_path=None, **kwargs):
    global init_datas

    if dev_path is not None:
        init_datas['in_dev'] = os.path.exists(dev_path)
    
    for k, v in kwargs.items():
        if v is not None:
            init_datas[k] = v

    reloadData()