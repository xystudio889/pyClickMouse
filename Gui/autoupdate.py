import os
import shutil
from tkinter import messagebox
import log

try:
    pass
except Exception as e:
    messagebox.showerror("错误", f"无法完成更新，正在回退版本...\n{e}")