import logging
import uuid # 生成唯一日志ID
from pathlib import Path # 路径处理

# 定义日志路径
folder_path = Path("logs")

# 创建文件夹（如果不存在）
folder_path.mkdir(parents=True, exist_ok=True)

# 创建logger对象
logger = logging.getLogger('multi_handler_logger')
logger.setLevel(logging.DEBUG)  # 设置最低日志级别

# 控制台处理器 - 仅WARNING及以上级别
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)  # 设置控制台日志级别
console_fmt = logging.Formatter('%(levelname)-8s - %(message)s')
console_handler.setFormatter(console_fmt)

# 文件处理器 - 仅INFO及以上级别
file_handler = logging.FileHandler(f'logs/{uuid.uuid4()}.log', mode='a',encoding='utf-8')
file_handler.setLevel(logging.INFO)  # 设置文件日志级别
file_fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_fmt)

# 添加处理器
logger.addHandler(console_handler)
logger.addHandler(file_handler)

def debug(msg):
    logger.debug(msg)

def info(msg):
    logger.info(msg)

def warning(msg):
    logger.warning(msg)

def error(msg):
    logger.error(msg)

def critical(msg):
    logger.critical(msg)