"""
conda适配模块
实现yrb conda前缀命令，注入镜像逻辑
"""
import os
import subprocess
from typing import List
from yrb.core.mirror_pool import get_mirrors
from yrb.core.speed_test import get_best_mirror

def _inject_conda_env():
    """注入最优镜像环境变量"""
    try:
        mirrors = get_mirrors("conda")
        # 启用缓存，默认TTL 1小时
        best = get_best_mirror(mirrors, cache_ttl=3600, tool_name="conda")
        if "channels" in best:
            # conda 识别 CONDA_CHANNELS 环境变量 (逗号分隔)
            os.environ["CONDA_CHANNELS"] = ",".join(best["channels"])
    except Exception:
        pass  # 失败则使用默认配置

def run_conda(args: List[str]) -> int:
    """
    执行conda命令
    :param args: 命令行参数列表（不含yrb conda前缀）
    :return: 退出码
    """
    _inject_conda_env()
    
    # 构造命令
    cmd = ["conda"] + args
    
    try:
        # 使用shell=True在Windows下可能更好，但跨平台建议False并确保conda在PATH中
        # Windows下conda通常是bat脚本，需要shell=True或者找到绝对路径
        # 为了兼容性，先尝试直接调用
        is_windows = os.name == 'nt'
        result = subprocess.run(cmd, shell=is_windows)
        return result.returncode
    except FileNotFoundError:
        print("Error: 'conda' command not found. Please ensure Conda is installed and in PATH.")
        return 127
    except Exception as e:
        print(f"Error running conda: {e}")
        return 1
