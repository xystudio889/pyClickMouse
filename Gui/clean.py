import shutil

try:
    shutil.rmtree("..\\update")
except PermissionError:
    pass