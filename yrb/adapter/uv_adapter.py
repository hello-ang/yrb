"""
uv适配模块
实现yrb uv前缀命令，注入镜像逻辑
"""
import os
import shutil
import subprocess
from typing import List
from yrb.core.mirror_pool import get_mirrors
from yrb.core.speed_test import get_best_mirror

def _inject_uv_env():
    """注入最优镜像环境变量"""
    try:
        mirrors = get_mirrors("pip")
        # uv 使用 pip 的镜像源，且速度极快，我们沿用 pip 的配置
        # 如果用户配置了 pip.mirror，这里也会生效
        best = get_best_mirror(mirrors, cache_ttl=3600, tool_name="pip")
        
        # uv 优先读取 UV_INDEX_URL，同时也兼容 PIP_INDEX_URL
        # 为了确保生效，我们同时设置
        os.environ["UV_INDEX_URL"] = best["url"]
        os.environ["PIP_INDEX_URL"] = best["url"]
        
        if "trusted_host" in best:
            os.environ["PIP_TRUSTED_HOST"] = best["trusted_host"]
            # uv 可能不需要 trusted_host，它默认支持 https，但也无害
    except Exception:
        pass

def run_uv(args: List[str]) -> int:
    """
    执行uv命令
    :param args: 命令行参数列表
    :return: 退出码
    """
    _inject_uv_env()
    
    # 查找 uv 可执行文件
    uv_cmd = shutil.which("uv")
    if not uv_cmd:
        print("Error: 'uv' command not found. Please install it first (e.g., pip install uv).")
        return 127

    cmd = [uv_cmd] + args
    try:
        return subprocess.run(cmd).returncode
    except Exception as e:
        print(f"Error running uv: {e}")
        return 1
