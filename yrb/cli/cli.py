import click
import sys
import subprocess
import json
from yrb.adapter.pip_adapter import run_pip
from yrb.adapter.conda_adapter import run_conda
from yrb.adapter.poetry_adapter import run_poetry
from yrb.adapter.pdm_adapter import run_pdm
from yrb.adapter.uv_adapter import run_uv
from yrb.core.cache_manager import clean_cache
from yrb.core.mirror_pool import add_custom_mirror, get_mirrors
from yrb.core.config_manager import set_config_value, get_config_value, unset_config_value, load_config
from yrb.cli.exception_handler import handle_exception

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """Python国内下载加速工具"""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())

@cli.command(
    name="pip",
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True
    )
)
@click.pass_context
@handle_exception
def pip_cmd(ctx):
    """
    执行pip命令（自动加速）
    示例：yrb pip install numpy
    """
    sys.exit(run_pip(ctx.args))

@cli.command(
    name="conda",
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True
    )
)
@click.pass_context
@handle_exception
def conda_cmd(ctx):
    """
    执行conda命令（自动加速）
    示例：yrb conda install numpy
    """
    sys.exit(run_conda(ctx.args))

@cli.command(
    name="poetry",
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True
    )
)
@click.pass_context
@handle_exception
def poetry_cmd(ctx):
    """
    执行poetry命令（尝试加速）
    示例：yrb poetry add numpy
    """
    sys.exit(run_poetry(ctx.args))

@cli.command(
    name="pdm",
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True
    )
)
@click.pass_context
@handle_exception
def pdm_cmd(ctx):
    """
    执行pdm命令（自动加速）
    示例：yrb pdm add numpy
    """
    sys.exit(run_pdm(ctx.args))

@cli.command(
    name="uv",
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True
    )
)
@click.pass_context
@handle_exception
def uv_cmd(ctx):
    """
    执行uv命令（自动加速）
    示例：yrb uv pip install numpy
    """
    sys.exit(run_uv(ctx.args))

@cli.command(
    name="python",
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True
    )
)
@click.pass_context
@handle_exception
def python_cmd(ctx):
    """
    执行python命令（自动识别 -m pip 并加速）
    示例：yrb python -m pip install numpy
    """
    args = ctx.args
    # 检查是否为 python -m pip 调用
    if len(args) >= 2 and args[0] == "-m" and args[1] == "pip":
        # 复用 run_pip 逻辑，传入 pip 之后的参数
        sys.exit(run_pip(args[2:]))
    else:
        # 其他 python 命令直接透传
        try:
            cmd = [sys.executable] + args
            sys.exit(subprocess.run(cmd).returncode)
        except Exception as e:
            click.echo(f"Error running python: {e}", err=True)
            sys.exit(1)

@cli.command(name="config")
@click.argument("action", type=click.Choice(["set", "get", "unset", "list"]))
@click.argument("key", required=False)
@click.argument("value", required=False)
@handle_exception
def config_cmd(action, key, value):
    """
    管理用户配置
    
    \b
    用法:
      yrb config list               # 列出所有配置
      yrb config get <key>          # 获取配置项
      yrb config set <key> <value>  # 设置配置项
      yrb config unset <key>        # 删除配置项
      
    \b
    示例:
      yrb config set pip.mirror aliyun  # 锁定 pip 使用阿里云镜像
      yrb config unset pip.mirror       # 取消锁定，恢复自动测速
    """
    if action == "list":
        config = load_config()
        click.echo(json.dumps(config, indent=2, ensure_ascii=False))
        return

    if not key:
        click.echo("Error: Missing argument 'KEY'.")
        return

    if action == "get":
        val = get_config_value(key)
        if val is None:
            click.echo(f"{key} is not set.")
        else:
            click.echo(f"{key} = {val}")
            
    elif action == "set":
        if not value:
            click.echo("Error: Missing argument 'VALUE'.")
            return
        set_config_value(key, value)
        click.echo(f"Set {key} = {value}")
        
    elif action == "unset":
        unset_config_value(key)
        click.echo(f"Unset {key}")

@cli.command(name="clean")
@handle_exception
def clean_cmd():
    """清理缓存"""
    if clean_cache():
        click.echo("Cache cleaned successfully.")
    else:
        click.echo("Failed to clean cache.")

@cli.command(name="info")
@handle_exception
def info_cmd():
    """显示配置信息"""
    from yrb import __version__
    click.echo(f"YRB Tool - Python国内下载加速工具 v{__version__}")
    click.echo("\nSupported Mirrors:")
    for tool in ["pip", "conda"]:
        click.echo(f"\n[{tool}]")
        for m in get_mirrors(tool):
            click.echo(f"  - {m['name']}: {m['url']}")
            
    click.echo("\nConfiguration:")
    config = load_config()
    if config:
        click.echo(json.dumps(config, indent=2, ensure_ascii=False))
    else:
        click.echo("  (No user configuration)")

    click.echo("\nSupported Tools:")
    click.echo("  - pip")
    click.echo("  - conda")
    click.echo("  - poetry (partial support)")
    click.echo("  - pdm")
    click.echo("  - uv")

@cli.command(name="test")
@handle_exception
def test_cmd():
    """
    运行自检测试
    强制重新测速并显示结果
    """
    # 简单调用测速逻辑验证连通性
    from yrb.core.speed_test import get_best_mirror
    click.echo("Testing connectivity (forcing refresh)...")
    try:
        # 强制测速，忽略缓存
        best_pip = get_best_mirror(get_mirrors("pip"), force=True, tool_name="pip")
        click.echo(f"Pip Best Mirror: {best_pip['name']} ({best_pip.get('delay', 'N/A')}ms)")
        
        best_conda = get_best_mirror(get_mirrors("conda"), force=True, tool_name="conda")
        click.echo(f"Conda Best Mirror: {best_conda['name']} ({best_conda.get('delay', 'N/A')}ms)")
        
        click.echo("\nAll checks passed.")
    except Exception as e:
        click.echo(f"Self-test failed: {e}")
        sys.exit(1)
