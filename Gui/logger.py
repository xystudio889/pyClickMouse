import os
import re
from datetime import datetime
from pathlib import Path
import logging
import functools
import traceback
from PySide6.QtWidgets import QMessageBox
import sys

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

class ExceptionVal:
    raise_trace = 0b1
    output_msg = 0b10
    exit = 0b100
    all = raise_trace | output_msg | exit
            
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
    
class LogFilter(logging.Filter):
    def __init__(self, default_service_id):
        super().__init__()
        self.default_service_id = default_service_id

    def filter(self, record):
        if not hasattr(record, 'service_id'):
            record.service_id = self.default_service_id
        return True

class Logger:
    def __init__(self, default_service_id):
        self.default_service_id = default_service_id
        # 创建self.logger对象
        self.logger = logging.getLogger(default_service_id)
        self.logger.setLevel(logging.DEBUG)  # 设置最低日志级别

        # 控制台处理器 - 仅WARNING及以上级别
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)  # 设置控制台日志级别
        format = {
            'default_format': '%(asctime)s - %(service_id)s - %(levelname)s - %(message)s', 
            'simple_format': '%(message)s' # 仅输出消息
        }
        console_fmt = ConditionalFormatter(
            **format
        )
        console_handler.setFormatter(console_fmt)

        # 文件处理器 - 仅INFO及以上级别
        file_handler = logging.FileHandler(folder_path / f'{log_id}.log', mode='a',encoding='utf-8')
        file_handler.setLevel(logging.INFO)  # 设置文件日志级别
        file_fmt = ConditionalFormatter(
            **format
        )
        file_handler.setFormatter(file_fmt)

        # 添加处理器
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        self.logger.addFilter(LogFilter(default_service_id=default_service_id))
        
        self.info(f'{"-" * 50}', extra={'simple_format': True})
        self.info(f'logger Started')
        remove_old_log(folder_path)

    def auto_logger(self, service_id: str | None=None, parent:list | None=None , start_extra_text: str='', end_extra_text:str='', start_extra:str | None=None, end_extra: str | None=None, level=logging.INFO):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                match level:
                    case logging.DEBUG:
                        log_func = self.debug
                    case logging.INFO:
                        log_func = self.info
                    case logging.WARNING:
                        log_func = self.warning
                    case logging.ERROR:
                        log_func = self.error
                    case logging.CRITICAL:
                        log_func = self.critical
                    case _:
                        log_func = self.info
                out_service_id = self.default_service_id if service_id is None else service_id
                start_extra_out = {} if start_extra is None else start_extra
                end_extra_out = {} if end_extra is None else end_extra
                parent_out = [] if parent is None else parent

                function_name = '.'.join(parent_out) + ('.' if parent else '') + func.__name__

                log_func(f'Running function: {function_name} args={args} kwargs={kwargs}', extra={'service_id': out_service_id, **start_extra_out})
                if start_extra_text:
                    log_func(start_extra_text, extra={'service_id': out_service_id, **start_extra_out})
                try:
                    result = func(*args, **kwargs)
                except Exception as e:
                    trace = traceback.format_exc()
                    self.exception(out_service_id, f'Function {function_name} raised an unexpected exception', extra={'service_id': out_service_id, **end_extra_out}, mode=ExceptionVal.raise_trace | ExceptionVal.output_msg | ExceptionVal.exit)
                    QMessageBox.critical(None, 'An unexpected error occurred', f'An unexpected error occurred in {function_name}: \n{trace}\nPlease look the log path: {(folder_path / f"{log_id}.log").resolve()} and send me the log file on issue: https://github.com/xystudiocode/pyClickMouse/issues/new/choose')
                    sys.exit(1)  # 退出程序
                log_func(f'Function {function_name} running successfull, returned: {result}', extra={'service_id': out_service_id, **end_extra_out})
                if end_extra_text:
                    log_func(end_extra_text, extra={'service_id': out_service_id, **end_extra_out})
                return result
            return wrapper
        return decorator

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
        
    def exception(self, service, msg='', extra=None, mode: ExceptionVal = ExceptionVal.raise_trace):
        if mode & ExceptionVal.raise_trace: # 获取堆栈
            trace = '\n' + traceback.format_exc()
        else:
            trace = ''
        self.critical(f'{msg}: An error occurred in {service}:{trace}', extra=extra)
        if mode & ExceptionVal.output_msg: # 输出消息
            QMessageBox.critical(None, 'An unexpected error occurred', f'An unexpected error occurred: {trace}\nPlease look the log path: {(folder_path / f"{log_id}.log").resolve()} and send me the log file on issue: https://github.com/xystudiocode/pyClickMouse/issues/new/choose')
        if mode & ExceptionVal.exit: # 退出程序
            sys.exit(1)  # 退出程序
