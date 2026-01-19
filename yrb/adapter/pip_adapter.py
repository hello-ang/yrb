"""
pip适配模块
实现yrb pip前缀命令，注入镜像与缓存逻辑
"""
import os
import sys
import re
import shutil
import subprocess
from typing import List
from yrb.core.mirror_pool import get_mirrors
from yrb.core.speed_test import get_best_mirror
from yrb.core.cache_manager import get_cached_package

def _inject_mirror_env():
    """注入最优镜像环境变量"""
    try:
        mirrors = get_mirrors("pip")
        # 启用缓存，默认TTL 1小时
        best = get_best_mirror(mirrors, cache_ttl=3600, tool_name="pip")
        os.environ["PIP_INDEX_URL"] = best["url"]
        if "trusted_host" in best:
            os.environ["PIP_TRUSTED_HOST"] = best["trusted_host"]
    except Exception:
        pass  # 测速失败不阻断，使用默认源

def _parse_package_info(arg: str) -> tuple:
    """解析包名和版本"""
    # 忽略选项参数
    if arg.startswith("-"):
        return "", ""
        
    # 简单解析 pkg==1.0.0 或 pkg>=1.0.0
    match = re.match(r"^([a-zA-Z0-9_\-]+)(?:([<>=!]+)(.*))?$", arg)
    if match:
        return match.group(1), match.group(3) if match.group(3) else ""
    return "", ""

def run_pip(args: List[str]) -> int:
    """
    执行pip命令
    :param args: 命令行参数列表（不含yrb pip前缀）
    :return: 退出码
    """
    # 如果用户已通过参数指定了源，则跳过环境变量注入，尊重用户选择
    user_specified_index = any(arg in args for arg in ["-i", "--index-url", "--extra-index-url"])
    if not user_specified_index:
        _inject_mirror_env()
    
    # 缓存替换逻辑
    new_args = list(args)
    if "install" in args:
        try:
            install_idx = args.index("install")
            # 遍历install之后的所有参数
            for i in range(install_idx + 1, len(args)):
                arg = args[i]
                if arg.startswith("-"):
                    continue
                    
                # 解析包名版本
                pkg_name, version = _parse_package_info(arg)
                if pkg_name and version:
                    # 仅当明确指定版本时尝试查缓存
                    cached_path = get_cached_package(pkg_name, version)
                    if cached_path:
                        new_args[i] = cached_path
        except Exception:
            pass # 解析失败不阻断，使用原参数

    # 调用原生pip (使用 python -m pip 避免警告)
    # 优先使用 PATH 中的 python，以支持虚拟环境；若找不到则回退到 sys.executable
    python_cmd = shutil.which("python") or sys.executable
    cmd = [python_cmd, "-m", "pip"] + new_args
    try:
        return subprocess.run(cmd).returncode
    except Exception as e:
        print(f"Error running pip: {e}")
        return 1
