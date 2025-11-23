import logging
import uuid # 生成唯一日志ID
from pathlib import Path # 路径处理

# 定义日志路径
folder_path = Path("cache/logs")
id = uuid.uuid4()

# 创建文件夹（如果不存在）
folder_path.mkdir(parents=True, exist_ok=True)

class Logger:
    def __init__(self, name, level=logging.DEBUG):
        # 创建self.logger对象
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)  # 设置最低日志级别

        # 控制台处理器 - 仅WARNING及以上级别
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)  # 设置控制台日志级别
        console_fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_fmt)

        # 文件处理器 - 仅INFO及以上级别
        file_handler = logging.FileHandler(folder_path / f'{id}.log', mode='a',encoding='utf-8')
        file_handler.setLevel(logging.INFO)  # 设置文件日志级别
        file_fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_fmt)

        # 添加处理器
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def critical(self, msg):
        self.logger.critical(msg)