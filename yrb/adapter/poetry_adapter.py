"""
Poetry适配模块
实现yrb poetry前缀命令，注入镜像逻辑
"""
import os
import subprocess
from typing import List
from yrb.core.mirror_pool import get_mirrors
from yrb.core.speed_test import get_best_mirror

def _inject_poetry_env():
    """注入最优镜像环境变量"""
    # 注意：Poetry 对环境变量的支持比较复杂，通常需要配置 config
    # 但为了零侵入，我们尝试设置 POETRY_REPOSITORIES_PYPI_URL (仅对自定义仓库有效)
    # 或者对于默认 PyPI，Poetry 很难通过简单环境变量覆盖。
    # 
    # 策略：
    # Poetry 1.2+ 并不直接支持 PIP_INDEX_URL。
    # 
    # 临时方案：
    # 如果是 install/add/update 命令，我们可能无法简单通过 env var 改变默认源，
    # 除非用户已经配置了 source。
    #
    # 另一种思路：
    # 很多用户使用 Poetry 时，底层还是依赖 pip 或者是独立的安装逻辑。
    # 
    # 经过调研，Poetry 确实比较难通过 Env Var 临时改变 PyPI 源。
    # 但我们可以尝试设置 PIP_INDEX_URL，因为 Poetry 在某些操作（如 run pip）可能会用到，
    # 或者在安装构建依赖时。
    #
    # 更好的方案可能是：
    # 提示用户 Poetry 最好在 pyproject.toml 中配置 source。
    # 
    # 但为了 "加速"，我们可以尝试设置:
    # POETRY_HTTP_BASIC_PYPI_USERNAME
    # POETRY_HTTP_BASIC_PYPI_PASSWORD
    # POETRY_REPOSITORIES_PYPI_URL -> 这通常是错的，因为 PyPI 是默认的。
    #
    # 让我们先尝试通用的 PIP 环境变量，看看是否对 poetry 有效 (有时 poetry 会读取 pip 配置)
    # 实际上 Poetry 不读取 PIP_INDEX_URL。
    #
    # 妥协方案：
    # 对于 Poetry，我们可能需要暂时不做“强”加速，或者提示用户。
    # 或者，我们只加速 `poetry run pip ...` 这种情况。
    #
    # 还有一种方法：使用 `poetry source add --priority=default` 但这修改了文件。
    #
    # 让我们再仔细想想 PDM。PDM 支持 PIP_INDEX_URL 吗？
    # PDM 尊重 pip 的配置。
    
    try:
        mirrors = get_mirrors("pip")
        best = get_best_mirror(mirrors, cache_ttl=3600, tool_name="pip")
        
        # 尝试注入 pip 变量，对 PDM 有效，对 Poetry 可能无效但无害
        os.environ["PIP_INDEX_URL"] = best["url"]
        if "trusted_host" in best:
            os.environ["PIP_TRUSTED_HOST"] = best["trusted_host"]
            
        # PDM 特有
        os.environ["PDM_PYPI_URL"] = best["url"]
        
    except Exception:
        pass

def run_poetry(args: List[str]) -> int:
    """
    执行poetry命令
    :param args: 命令行参数列表
    :return: 退出码
    """
    # 尝试注入兼容性变量
    _inject_poetry_env()
    
    # 检查是否为安装类命令
    if any(cmd in args for cmd in ["add", "install", "update"]):
        # 提示用户 Poetry 可能不会完全生效
        print("Note: Poetry acceleration via env vars is experimental and may not work for all commands.")
        print("Tip: For permanent acceleration, run: poetry source add --priority=default mirrors <mirror_url>")
        
    cmd = ["poetry"] + args
    try:
        # Windows下poetry通常是bat/exe
        is_windows = os.name == 'nt'
        return subprocess.run(cmd, shell=is_windows).returncode
    except Exception as e:
        print(f"Error running poetry: {e}")
        return 1
