import os
from pathlib import Path
import subprocess
import shutil

def delete_folder(folder_path, exclude_dirs):
    '''
    递归删除文件夹，保留指定目录列表中的内容
    支持嵌套的目录结构
    '''
    if not os.path.exists(folder_path):
        return
    
    # 确保 exclude_dirs 是列表
    if not isinstance(exclude_dirs, list):
        exclude_dirs = [exclude_dirs]
    
    def should_preserve(path):
        '''检查路径是否应该保留'''
        rel_path = os.path.relpath(path, folder_path) if path != folder_path else ''
        # 检查路径的任何部分是否在排除列表中
        for part in rel_path.split(os.sep):
            if part in exclude_dirs:
                return True
        return False
    
    def _delete_recursive(current_path):
        # 如果当前目录本身应该保留，则跳过
        if should_preserve(current_path) and current_path != folder_path:
            return
        
        if os.path.isdir(current_path):
            # 遍历目录内容
            items = list(os.listdir(current_path))
            for item in items:
                item_path = os.path.join(current_path, item)
                
                # 如果子项应该保留，则跳过
                if should_preserve(item_path):
                    continue
                
                _delete_recursive(item_path)
            
            # 尝试删除空目录（如果不是要保留的目录）
            if not should_preserve(current_path) and current_path != folder_path:
                shutil.rmtree(current_path, ignore_errors=True)
        elif os.path.isfile(current_path):
            # 删除文件
            try:
                os.remove(current_path)
            except:
                pass
    
    # 执行删除
    _delete_recursive(folder_path)
        
def extract_7z(file_path):
    subprocess.run(['7z', 'x', file_path])
    
def move_contents_to_parent(folder_path):
    """
    将指定文件夹内的所有内容移动到其父目录
    """
    # 转换为Path对象
    folder = Path(folder_path)
    
    # 检查文件夹是否存在
    if not folder.exists() or not folder.is_dir():
        return
    
    # 获取父目录
    parent_dir = folder.parent
    
    # 遍历文件夹内的所有内容
    for item in folder.iterdir():
        try:
            # 构建目标路径
            target_path = parent_dir / item.name
            
            # 如果目标已存在，添加后缀避免覆盖
            counter = 1
            original_name = item.name
            while target_path.exists():
                name_parts = original_name.rsplit('.', 1)
                if len(name_parts) > 1:
                    new_name = f"{name_parts[0]}_{counter}.{name_parts[1]}"
                else:
                    new_name = f"{original_name}_{counter}"
                target_path = parent_dir / new_name
                counter += 1

            # 移动文件或文件夹
            shutil.move(str(item), str(target_path))
        except Exception:
            return
    
    # 检查文件夹是否为空
    try:
        folder.rmdir()
    except Exception:
        return

if __name__ == '__main__':
    clickmouse_path = Path.cwd()
    shutil.move(clickmouse_path / 'packages.json', clickmouse_path / 'extensions')
    extract_7z('updater.old/clickmouse.7z')
    delete_folder(clickmouse_path, ['data', 'updater.old', 'extensions', 'clickmouse'])
    move_contents_to_parent(clickmouse_path / 'clickmouse')
    shutil.move(clickmouse_path / 'extensions' / 'packages.json', clickmouse_path)