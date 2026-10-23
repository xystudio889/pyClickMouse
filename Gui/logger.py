import contextvars
import inspect
import os
import re
import tarfile
from datetime import date, datetime
from pathlib import Path
import logging
import functools
import traceback
from PySide6.QtWidgets import QMessageBox
import sys

# 日志文件命名规则: <包名>-<日期>.log，如 com.myapp.main-2024-10-13.log
LOG_FILE_RE = re.compile(r'^(?P<package>.+)-(?P<date>\d{4}-\d{2}-\d{2})\.log$')
# 归档文件命名规则: logs-<日期>.tar.gz，一天一份，包含当天所有包名的日志
ARCHIVE_FILE_TMPL = 'logs-{date}.tar.gz'
# 日志保留天数，超过该天数的日志会被归档
LOG_RETENTION_DAYS = 10

# auto_logger 装饰器执行期间，被装饰函数内部日志使用的 service_id 栈:
# ((logger 名称, 拼接后的 service_id), ...)
# 用栈保存以支持嵌套装饰器，并在函数执行结束后恢复外层设置。
_service_id_scope = contextvars.ContextVar('logger_service_id_scope', default=())


def _format_init_parameters(init_func, instance, args, kwargs):
    '''
    按 __init__ 的参数列表格式化初始化参数，如 "name='alice', count=2"。
    无法解析签名时退化为原始的 args/kwargs 形式。
    '''
    try:
        signature = inspect.signature(init_func)
        bound = signature.bind(instance, *args, **kwargs)
        bound.apply_defaults()
        # 第一个参数是 self，不展示
        arguments = list(bound.arguments.items())[1:]
        return ', '.join(f'{name}={value!r}' for name, value in arguments)
    except (TypeError, ValueError):
        return f'args={args!r} kwargs={kwargs!r}'


def _is_already_auto_logged(func):
    '''判断函数是否已经被 auto_logger / auto_logger_for_class 包装过。'''
    return (
        getattr(func, '__auto_logger__', False)
        or getattr(func, '__auto_logger_for_class__', False)
    )


def _wrap_logged_method(logger, func, display_name, service_id, log_func, strip_first_arg=False):
    '''
    包装类方法：记录调用/返回，并让方法内部通过 logger 输出的日志继承类的 service_id。
    strip_first_arg=True 时在调用日志中隐藏 self/cls 参数。
    '''
    @functools.wraps(func)
    def wrapper(*all_args, **kwargs):
        display_args = all_args[1:] if strip_first_arg else all_args
        log_func(
            f'Calling method: {display_name} args={display_args} kwargs={kwargs}',
            extra={'service_id': service_id},
        )
        token = _service_id_scope.set(
            _service_id_scope.get() + ((logger.logger.name, service_id),)
        )
        try:
            try:
                result = func(*all_args, **kwargs)
            except Exception:
                logger.exception(
                    service_id,
                    f'Method {display_name} raised an unexpected exception',
                    extra={'service_id': service_id},
                )
                raise
        finally:
            _service_id_scope.reset(token)
        log_func(
            f'Method {display_name} returned: {result!r}',
            extra={'service_id': service_id},
        )
        return result

    wrapper.__auto_logger_for_class__ = True
    return wrapper


def parse_log_filename(filename):
    '''
    解析日志文件名，返回 (包名, 文件日期)；不符合命名规则时返回 None
    '''
    matched = LOG_FILE_RE.match(filename)
    if not matched:
        return None
    try:
        file_date = datetime.strptime(matched.group('date'), '%Y-%m-%d').date()
    except ValueError:
        return None
    return matched.group('package'), file_date


def _write_archive(archive_path, log_files):
    '''
    把同一天的日志写入 tar.gz，成功返回 True。
    若归档已存在，则合并其中尚未被重新写入的成员，保证一天只有一份归档。
    '''
    tmp_path = archive_path.with_name(archive_path.name + '.tmp')
    current_names = {log_file.name for log_file in log_files}
    try:
        with tarfile.open(tmp_path, 'w:gz') as tar:
            if archive_path.exists():
                # 先保留历史归档中已有的成员（同名文件以本次磁盘上的日志为准）
                with tarfile.open(archive_path, 'r:gz') as old_tar:
                    for member in old_tar.getmembers():
                        if not member.isfile() or member.name in current_names:
                            continue
                        source = old_tar.extractfile(member)
                        if source is None:
                            continue
                        with source:
                            tar.addfile(member, source)
            for log_file in log_files:
                tar.add(log_file, arcname=log_file.name)
        os.replace(tmp_path, archive_path)
        return True
    except Exception:
        # 归档失败时清理临时文件并保留原日志，避免丢日志
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        return False


def archive_old_logs(directory_path, retention_days=LOG_RETENTION_DAYS):
    '''
    归档过期日志（替代原来的直接删除逻辑）:
    - 只处理命名为 <包名>-<日期>.log 的日志文件
    - 超过 retention_days 天的日志按天打包为 logs-<日期>.tar.gz，
      同一天所有包名的日志打进同一个归档文件
    - 打包成功后才删除原日志文件；归档失败则保留原日志
    - 未到期的日志以及不符合命名规则的其他文件保持不动
    '''
    # 获取所有文件
    try:
        filenames = os.listdir(directory_path)
    except OSError:
        return

    today = date.today()
    logs_by_date = {}
    for filename in filenames:
        parsed = parse_log_filename(filename)
        if parsed is None:
            continue
        _, file_date = parsed
        # 未超过保留天数的日志不动
        if (today - file_date).days <= retention_days:
            continue
        logs_by_date.setdefault(file_date, []).append(Path(directory_path) / filename)

    for file_date in sorted(logs_by_date):
        log_files = logs_by_date[file_date]
        archive_path = Path(directory_path) / ARCHIVE_FILE_TMPL.format(date=file_date.isoformat())
        if not _write_archive(archive_path, log_files):
            continue
        # 归档成功后再删除原日志
        for log_file in log_files:
            try:
                os.remove(log_file)
            except OSError:
                pass


# 兼容旧调用方使用的函数名（旧逻辑是直接删除过期日志）
remove_old_log = archive_old_logs

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
        if not getattr(record, 'service_id', None):
            record.service_id = self.default_service_id
            # 在 auto_logger 装饰的函数内部，日志自动使用装饰器设置的 service_id
            for logger_name, scoped_service_id in reversed(_service_id_scope.get()):
                if logger_name == record.name:
                    record.service_id = scoped_service_id
                    break
        return True

class Logger:
    def __init__(self, default_service_id):
        self.default_service_id = default_service_id
        # 日志文件: <包名>-<日期>.log，如 com.myapp.main-2024-10-13.log
        self.log_file = folder_path / f'{default_service_id}-{log_id}.log'
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
        file_handler = logging.FileHandler(self.log_file, mode='a', encoding='utf-8')
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
        archive_old_logs(folder_path)

    def _compose_service_id(self, service_id):
        '''把装饰器的 service_id 拼接到 logger 全局包名之后。'''
        if not service_id:
            return self.default_service_id
        return f'{self.default_service_id}.{service_id}'

    def _log_func_for_level(self, level):
        '''按日志级别返回对应的 Logger 方法。'''
        match level:
            case logging.DEBUG:
                return self.debug
            case logging.INFO:
                return self.info
            case logging.WARNING:
                return self.warning
            case logging.ERROR:
                return self.error
            case logging.CRITICAL:
                return self.critical
            case _:
                return self.info

    def auto_logger(self, service_id: str | None=None, parent:list | None=None , start_extra_text: str='', end_extra_text:str='', start_extra:str | None=None, end_extra: str | None=None, level=logging.INFO):
        log_func = self._log_func_for_level(level)
        # service_id 拼接到 logger 的全局包名之后，
        # 如 logger 为 com.myapp.main、装饰器为 my_func，则输出 com.myapp.main.my_func
        out_service_id = self._compose_service_id(service_id)

        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_extra_out = {} if start_extra is None else start_extra
                end_extra_out = {} if end_extra is None else end_extra
                parent_out = [] if parent is None else parent

                function_name = '.'.join(parent_out) + ('.' if parent else '') + func.__name__

                log_func(f'Running function: {function_name} args={args} kwargs={kwargs}', extra={'service_id': out_service_id, **start_extra_out})
                if start_extra_text:
                    log_func(start_extra_text, extra={'service_id': out_service_id, **start_extra_out})
                # 进入被装饰函数前记录 service_id 作用域，函数内部 self.info/warning 等
                # 日志会自动使用 out_service_id；退出函数（含异常）后恢复外层设置
                scope_token = _service_id_scope.set(
                    _service_id_scope.get() + ((self.logger.name, out_service_id),)
                )
                try:
                    result = func(*args, **kwargs)
                except Exception as e:
                    trace = traceback.format_exc()
                    self.exception(out_service_id, f'Function {function_name} raised an unexpected exception', extra={'service_id': out_service_id, **end_extra_out}, mode=ExceptionVal.raise_trace | ExceptionVal.output_msg | ExceptionVal.exit)
                    QMessageBox.critical(None, 'An unexpected error occurred', f'An unexpected error occurred in {function_name}: \n{trace}\nPlease look the log path: {self.log_file.resolve()} and send me the log file on issue: https://github.com/xystudiocode/pyClickMouse/issues/new/choose')
                    sys.exit(1)  # 退出程序
                finally:
                    _service_id_scope.reset(scope_token)
                log_func(f'Function {function_name} running successfull, returned: {result}', extra={'service_id': out_service_id, **end_extra_out})
                if end_extra_text:
                    log_func(end_extra_text, extra={'service_id': out_service_id, **end_extra_out})
                return result
            # 标记该函数已由 auto_logger 处理，auto_logger_for_class 会优先保留其配置
            wrapper.__auto_logger__ = True
            return wrapper
        return decorator

    def auto_logger_for_class(self, service_id: str | None=None, level=logging.INFO):
        '''
        auto_logger 的类装饰器版本:
        - 记录类的初始化操作，参数列表按 __init__ 的签名显示（name=value 形式）；
        - 记录类方法的调用与返回；
        - 类方法内部的 logger.info / warning 等日志自动继承本装饰器设置的 service_id；
        - 类方法自身已用 auto_logger 装饰时保留 auto_logger 的选项（不重复包装，其 service_id 优先）；
        - 方法异常会记录日志后继续抛出，不会像 auto_logger 那样弹窗退出。
        '''
        log_func = self._log_func_for_level(level)

        def decorator(cls):
            class_name = cls.__name__
            class_service_id = self._compose_service_id(service_id)

            # ---- 包装 __init__: 记录类的初始化操作 ----
            init_func = getattr(cls, '__init__')
            if not _is_already_auto_logged(init_func):

                @functools.wraps(init_func)
                def wrapped_init(instance, *args, **kwargs):
                    log_func(
                        f'Initializing class {class_name} with parameters: '
                        f'{_format_init_parameters(init_func, instance, args, kwargs)}',
                        extra={'service_id': class_service_id},
                    )
                    token = _service_id_scope.set(
                        _service_id_scope.get() + ((self.logger.name, class_service_id),)
                    )
                    try:
                        try:
                            result = init_func(instance, *args, **kwargs)
                        except Exception:
                            self.exception(
                                class_service_id,
                                f'Class {class_name} initialization raised an unexpected exception',
                                extra={'service_id': class_service_id},
                            )
                            raise
                    finally:
                        _service_id_scope.reset(token)
                    log_func(f'Class {class_name} initialized', extra={'service_id': class_service_id})
                    return result

                wrapped_init.__auto_logger_for_class__ = True
                cls.__init__ = wrapped_init

            # ---- 包装类方法: 记录调用/返回，并让内部日志继承类 service_id ----
            for method_name, member in list(vars(cls).items()):
                if method_name == '__init__':
                    continue
                # 不包装其他魔术方法，避免影响 __repr__/__eq__/__call__ 等
                if method_name.startswith('__') and method_name.endswith('__'):
                    continue

                if isinstance(member, staticmethod):
                    func, wrapper_factory = member.__func__, staticmethod
                elif isinstance(member, classmethod):
                    func, wrapper_factory = member.__func__, classmethod
                elif inspect.isfunction(member):
                    func, wrapper_factory = member, None
                else:
                    # 属性、描述符、类属性等不处理
                    continue

                # 已应用 auto_logger 的方法以 auto_logger 的选项为准
                if _is_already_auto_logged(func):
                    continue

                wrapped = _wrap_logged_method(
                    self,
                    func,
                    f'{class_name}.{method_name}',
                    class_service_id,
                    log_func,
                    strip_first_arg=not isinstance(member, staticmethod),
                )
                setattr(cls, method_name, wrapper_factory(wrapped) if wrapper_factory else wrapped)

            return cls

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
            QMessageBox.critical(None, 'An unexpected error occurred', f'An unexpected error occurred: {trace}\nPlease look the log path: {self.log_file.resolve()} and send me the log file on issue: https://github.com/xystudiocode/pyClickMouse/issues/new/choose')
        if mode & ExceptionVal.exit: # 退出程序
            sys.exit(1)  # 退出程序
