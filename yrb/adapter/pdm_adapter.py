"""
PDM适配模块
实现yrb pdm前缀命令，注入镜像逻辑
"""
import os
import subprocess
from typing import List
from yrb.core.mirror_pool import get_mirrors
from yrb.core.speed_test import get_best_mirror

def _inject_pdm_env():
    """注入最优镜像环境变量"""
    try:
        mirrors = get_mirrors("pip")
        best = get_best_mirror(mirrors, cache_ttl=3600, tool_name="pip")
        
        # PDM 尊重 PIP_INDEX_URL
        os.environ["PIP_INDEX_URL"] = best["url"]
        # PDM 也支持 PDM_PYPI_URL
        os.environ["PDM_PYPI_URL"] = best["url"]
        
        if "trusted_host" in best:
            os.environ["PIP_TRUSTED_HOST"] = best["trusted_host"]
    except Exception:
        pass

def run_pdm(args: List[str]) -> int:
    """
    执行pdm命令
    :param args: 命令行参数列表
    :return: 退出码
    """
    _inject_pdm_env()
    cmd = ["pdm"] + args
    try:
        is_windows = os.name == 'nt'
        return subprocess.run(cmd, shell=is_windows).returncode
    except Exception as e:
        print(f"Error running pdm: {e}")
        return 1
