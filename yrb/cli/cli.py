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

# Rich 控制台实例（全局共享）
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich import box
    console = Console()
    _rich_available = True
except ImportError:
    console = None
    _rich_available = False

def _echo(message, style=None, **kwargs):
    """统一输出函数：优先使用 rich，降级到 click.echo"""
    if _rich_available and console:
        console.print(message, style=style, **kwargs)
    else:
        # 去除 rich markup
        click.echo(message)

# ── 镜像名称映射（英文 -> 中文）──
MIRROR_NAME_MAP = {
    "aliyun": "阿里云",
    "tsinghua": "清华大学",
    "tencent": "腾讯云",
    "huawei": "华为云",
    "ustc": "中科大",
    "douban": "豆瓣",
}

def _display_name(name: str) -> str:
    """获取镜像的显示名称"""
    cn = MIRROR_NAME_MAP.get(name, "")
    return f"{cn} ({name})" if cn else name

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """Python国内下载加速工具"""
    if ctx.invoked_subcommand is None:
        if _rich_available:
            from yrb import __version__
            console.print(Panel(
                f"[bold cyan]yrb[/bold cyan] [dim]v{__version__}[/dim] — Python 国内下载加速工具\n\n"
                f"[dim]使用[/dim] [bold]yrb --help[/bold] [dim]查看全部命令[/dim]",
                border_style="cyan",
                padding=(1, 2),
            ))
        else:
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
            _echo(f"Error running python: {e}", style="bold red")
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
        if _rich_available:
            if config:
                table = Table(title="📋 用户配置", box=box.ROUNDED, border_style="cyan")
                table.add_column("配置项", style="bold white")
                table.add_column("值", style="green")
                for section, values in config.items():
                    if isinstance(values, dict):
                        for k, v in values.items():
                            table.add_row(f"{section}.{k}", str(v))
                    else:
                        table.add_row(section, str(values))
                console.print(table)
            else:
                _echo("  [dim](暂无用户配置)[/dim]")
        else:
            click.echo(json.dumps(config, indent=2, ensure_ascii=False))
        return

    if not key:
        _echo("Error: Missing argument 'KEY'.", style="bold red")
        return

    if action == "get":
        val = get_config_value(key)
        if val is None:
            _echo(f"[dim]{key} 未设置[/dim]")
        else:
            _echo(f"[bold]{key}[/bold] = [green]{val}[/green]")
            
    elif action == "set":
        if not value:
            _echo("Error: Missing argument 'VALUE'.", style="bold red")
            return
        set_config_value(key, value)
        _echo(f"[green]✓[/green] 已设置 [bold]{key}[/bold] = [cyan]{value}[/cyan]")
        
    elif action == "unset":
        unset_config_value(key)
        _echo(f"[green]✓[/green] 已删除 [bold]{key}[/bold]")

@cli.command(name="clean")
@handle_exception
def clean_cmd():
    """清理缓存"""
    if clean_cache():
        _echo("[green]✓[/green] 缓存已清理完毕")
    else:
        _echo("[red]✗[/red] 缓存清理失败", style="bold red")

@cli.command(name="info")
@handle_exception
def info_cmd():
    """显示配置信息"""
    from yrb import __version__
    
    if _rich_available:
        # ── 标题面板 ──
        console.print(Panel(
            f"[bold cyan]yrb[/bold cyan] [dim]v{__version__}[/dim] — Python 国内下载加速工具",
            border_style="cyan",
            padding=(0, 2),
        ))
        console.print()
        
        # ── 镜像表格 ──
        for tool in ["pip", "conda"]:
            mirrors = get_mirrors(tool)
            table = Table(
                title=f"🪞 {tool.upper()} 镜像源",
                box=box.ROUNDED,
                border_style="blue",
                show_lines=False,
            )
            table.add_column("#", style="dim", width=3, justify="right")
            table.add_column("名称", style="bold white", min_width=16)
            table.add_column("URL", style="cyan", no_wrap=True)
            table.add_column("优先级", justify="center", width=6)
            
            for i, m in enumerate(mirrors, 1):
                priority = m.get("priority", "-")
                priority_style = "green" if (isinstance(priority, int) and priority >= 90) else "yellow"
                table.add_row(
                    str(i),
                    _display_name(m["name"]),
                    m["url"],
                    f"[{priority_style}]{priority}[/{priority_style}]",
                )
            console.print(table)
            console.print()

        # ── 配置信息 ──
        config = load_config()
        if config:
            config_table = Table(title="📋 用户配置", box=box.ROUNDED, border_style="cyan")
            config_table.add_column("配置项", style="bold white")
            config_table.add_column("值", style="green")
            for section, values in config.items():
                if isinstance(values, dict):
                    for k, v in values.items():
                        config_table.add_row(f"{section}.{k}", str(v))
                else:
                    config_table.add_row(section, str(values))
            console.print(config_table)
        else:
            _echo("  [dim](暂无用户配置)[/dim]")
        console.print()

        # ── 支持的工具 ──
        tools_text = Text()
        tools_text.append("🛠️  支持的工具: ", style="bold")
        tool_names = ["pip", "conda", "pdm", "uv", "poetry*"]
        for i, t in enumerate(tool_names):
            style = "dim italic" if t.endswith("*") else "cyan bold"
            tools_text.append(t, style=style)
            if i < len(tool_names) - 1:
                tools_text.append("  ·  ", style="dim")
        console.print(tools_text)
        console.print("    [dim italic]* 实验性支持[/dim italic]")
    else:
        # 降级到纯文本
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
        click.echo("\nSupported Tools: pip, conda, poetry*, pdm, uv")

@cli.command(name="test")
@handle_exception
def test_cmd():
    """
    运行自检测试
    强制重新测速并显示结果
    """
    from yrb.core.speed_test import get_ranked_mirrors
    
    if _rich_available:
        from rich.spinner import Spinner
        from rich.live import Live
        
        console.print()
        console.print("[bold]🔍 正在测速中...[/bold]", style="cyan")
        console.print()
        
        for tool in ["pip", "conda"]:
            mirrors = get_mirrors(tool)
            try:
                ranked = get_ranked_mirrors(mirrors, force=True, tool_name=tool)
                
                # ── 测速结果排行榜 ──
                table = Table(
                    title=f"⚡ {tool.upper()} 镜像测速排行",
                    box=box.HEAVY_HEAD,
                    border_style="green",
                    show_lines=False,
                )
                table.add_column("排名", style="bold", width=4, justify="center")
                table.add_column("镜像", style="bold white", min_width=16)
                table.add_column("延迟 (ms)", justify="right", width=12)
                table.add_column("状态", justify="center", width=8)
                
                for i, m in enumerate(ranked, 1):
                    name = _display_name(m["name"])
                    status_ok = m.get("status", False)
                    delay = m.get("delay", float("inf"))
                    
                    # 排名标记
                    if i == 1 and status_ok:
                        rank = "🥇"
                    elif i == 2 and status_ok:
                        rank = "🥈"
                    elif i == 3 and status_ok:
                        rank = "🥉"
                    else:
                        rank = str(i)
                    
                    # 延迟颜色
                    if not status_ok:
                        delay_str = "[dim]超时[/dim]"
                        status_str = "[red]✗[/red]"
                        name = f"[dim]{name}[/dim]"
                    elif delay < 200:
                        delay_str = f"[bold green]{delay}[/bold green]"
                        status_str = "[green]✓[/green]"
                    elif delay < 500:
                        delay_str = f"[yellow]{delay}[/yellow]"
                        status_str = "[green]✓[/green]"
                    else:
                        delay_str = f"[red]{delay}[/red]"
                        status_str = "[yellow]⚠[/yellow]"
                    
                    table.add_row(rank, name, delay_str, status_str)
                
                console.print(table)
                console.print()
                
            except ConnectionError as e:
                console.print(f"  [red]✗[/red] {tool}: {e}")
        
        console.print("[bold green]✓ 自检完成[/bold green]")
    else:
        # 降级到纯文本
        from yrb.core.speed_test import get_best_mirror
        click.echo("Testing connectivity (forcing refresh)...")
        try:
            best_pip = get_best_mirror(get_mirrors("pip"), force=True, tool_name="pip")
            click.echo(f"Pip Best Mirror: {best_pip['name']} ({best_pip.get('delay', 'N/A')}ms)")
            
            best_conda = get_best_mirror(get_mirrors("conda"), force=True, tool_name="conda")
            click.echo(f"Conda Best Mirror: {best_conda['name']} ({best_conda.get('delay', 'N/A')}ms)")
            
            click.echo("\nAll checks passed.")
        except Exception as e:
            click.echo(f"Self-test failed: {e}")
            sys.exit(1)
