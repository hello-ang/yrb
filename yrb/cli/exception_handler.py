"""
异常处理模块
自定义异常类与全局异常捕获
"""
import sys
import click

class YrbError(Exception):
    """yrb工具通用基类异常"""
    pass

class MirrorUnavailableError(YrbError):
    """镜像不可用异常"""
    def __init__(self, message="所有镜像均无法连接"):
        self.message = message
        super().__init__(self.message)

class ConfigError(YrbError):
    """配置错误异常"""
    def __init__(self, message="配置文件损坏或格式错误"):
        self.message = message
        super().__init__(self.message)

def handle_exception(func):
    """
    CLI异常处理装饰器
    捕获已知异常并输出友好提示，屏蔽堆栈
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except YrbError as e:
            click.echo(f"Error: {e.message}", err=True)
            sys.exit(1)
        except Exception as e:
            # 对于未知异常，保留堆栈以便调试（或者也可以选择屏蔽）
            # 生产环境通常建议:
            # click.echo(f"Unexpected Error: {e}", err=True)
            # sys.exit(1)
            raise e
    return wrapper
