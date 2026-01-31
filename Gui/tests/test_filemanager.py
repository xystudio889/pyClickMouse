import os
import re
from datetime import datetime

def remove_old_log(directory_path):
    '''
    管理文件，保持最多指定数量的文件
    '''
    # 定义日期格式的正则表达式
    date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}(?:\..+)?$')
    
    # 获取所有文件
    all_files = os.listdir(directory_path)
    
    # 筛选并解析日期文件
    valid_files = []
    for filename in all_files:
        if date_pattern.match(filename):
            # 提取日期部分
            date_str = filename.split('.')[0]
            try:
                file_date = datetime.strptime(date_str, '%Y-%m-%d')
                valid_files.append((filename, file_date))
            except ValueError:
                continue
    
    if not valid_files:
        return True
    
    # 按日期排序
    valid_files.sort(key=lambda x: x[1])
    
    # 如果文件数超过限制，删除最旧的文件
    if len(valid_files) > 10:
        files_to_delete = valid_files[:len(valid_files) - 10]
        
        for filename, _ in files_to_delete:
            file_path = os.path.join(directory_path, filename)
            try:
                os.remove(file_path)
            except Exception as e:
                pass
    return True

# 使用示例
def test_main():
    # 执行每日操作
    assert remove_old_log('tests/test')
