import os
import re
from datetime import datetime
from pathlib import Path
import logging

def remove_old_log(directory_path):
    '''
    管理文件，保持最多指定数量的文件
    '''
    # 定义日期格式的正则表达式
    date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}(?:\..+)?$')
    
    # 获取所有文件
    try:
        all_files = os.listdir(directory_path)
    except:
        pass
    
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
        return
    
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
            
# 定义日志路径
folder_path = Path("cache/logs")
log_id = datetime.now().strftime('%Y-%m-%d')

# 创建文件夹
folder_path.mkdir(parents=True, exist_ok=True)

class ConditionalFormatter(logging.Formatter):
    def __init__(self, default_format, simple_format=None):
        super().__init__()
        self.default_formatter = logging.Formatter(default_format)
        self.simple_formatter = logging.Formatter(simple_format) if simple_format else None
    
    def format(self, record):
        # 检查是否有特殊属性标记
        if hasattr(record, 'simple_format') and record.simple_format:
            if self.simple_formatter:
                return self.simple_formatter.format(record)
            else:
                # 如果没有simple_formatter，直接返回消息
                return record.getMessage()
        else:
            return self.default_formatter.format(record)

class Logger:
    def __init__(self, name):
        # 创建self.logger对象
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)  # 设置最低日志级别

        # 控制台处理器 - 仅WARNING及以上级别
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)  # 设置控制台日志级别
        console_fmt = ConditionalFormatter(
            '%(asctime)s-%(levelname)s-%(message)s',
            simple_format='%(message)s'  # 直接输出消息
        )
        console_handler.setFormatter(console_fmt)

        # 文件处理器 - 仅INFO及以上级别
        file_handler = logging.FileHandler(folder_path / f'{log_id}.log', mode='a',encoding='utf-8')
        file_handler.setLevel(logging.INFO)  # 设置文件日志级别
        file_fmt = ConditionalFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            simple_format='%(message)s'  # 仅输出消息
        )
        file_handler.setFormatter(file_fmt)

        # 添加处理器
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        
        self.info(f'{"-" * 50}', extra={'simple_format': True})
        self.info(f'logger启动，位于{log_id}.log,程序名{name}')
        remove_old_log(folder_path)

    def debug(self, msg, extra=None):
        self.logger.debug(msg, extra=extra)

    def info(self, msg, extra=None):
        self.logger.info(msg, extra=extra)

    def warning(self, msg, extra=None):
        self.logger.warning(msg, extra=extra)

    def error(self, msg, extra=None):
        self.logger.warning(msg, extra=extra)

    def critical(self, msg, extra=None):
        self.logger.critical(msg, extra=extra)