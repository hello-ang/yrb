"""
镜像测速模块
实现HTTP HEAD请求测速与最优镜像筛选
"""
import requests
import time
import json
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from yrb.core.cache_manager import _ensure_cache_dir, CACHE_DIR
from yrb.core.config_manager import get_config_value

# 测速缓存文件
SPEED_CACHE_FILE = CACHE_DIR / "speed_cache.json"

def _load_speed_cache() -> dict:
    """加载测速缓存"""
    try:
        if not SPEED_CACHE_FILE.exists():
            return {}
        with open(SPEED_CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _save_speed_cache(cache: dict):
    """保存测速缓存"""
    try:
        _ensure_cache_dir()
        with open(SPEED_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2)
    except Exception:
        pass

def _get_cache_key(mirrors: list) -> str:
    """根据镜像列表生成唯一的缓存键"""
    # 使用所有镜像URL的排序拼接字符串进行hash
    urls = sorted([m["url"] for m in mirrors])
    content = "|".join(urls)
    return hashlib.md5(content.encode("utf-8")).hexdigest()

def check_mirror_speed(mirror: dict, timeout: int = 3) -> dict:
    """
    对单个镜像进行测速
    :param mirror: 镜像配置字典
    :param timeout: 超时时间（秒）
    :return: 包含延迟和状态的镜像字典
    """
    url = mirror["url"]
    result = mirror.copy()
    
    try:
        start_time = time.time()
        # 使用HEAD请求，禁止重定向，减少流量
        response = requests.head(url, timeout=timeout, allow_redirects=False)
        delay = (time.time() - start_time) * 1000  # 转换为毫秒
        
        if response.status_code < 400:
            result["delay"] = int(delay)
            result["status"] = True
        else:
            result["delay"] = float('inf')
            result["status"] = False
            
    except Exception:
        result["delay"] = float('inf')
        result["status"] = False
        
    return result

from yrb.core.config_manager import get_config_value

def get_ranked_mirrors(mirrors: list, cache_ttl: int = 3600, force: bool = False, tool_name: str = None) -> list:
    """
    并发测速并返回按延迟排序的全部镜像列表
    :param mirrors: 镜像列表
    :param cache_ttl: 缓存有效期（秒），默认1小时
    :param force: 是否强制测速（忽略缓存）
    :param tool_name: 工具名称（如 pip, conda），用于检查锁定配置
    :return: 按延迟排序的镜像列表（包含不可用镜像）
    :raises ConnectionError: 无可用镜像时抛出
    """
    if not mirrors:
        raise ConnectionError("No mirrors provided")

    # 0. 检查用户配置锁定
    if tool_name:
        locked_mirror_name = get_config_value(f"{tool_name}.mirror")
        if locked_mirror_name:
            for m in mirrors:
                if m["name"] == locked_mirror_name:
                    result = m.copy()
                    result["delay"] = 0
                    result["status"] = True
                    result["locked"] = True
                    return [result]

    tested_mirrors = []
    
    # 并发测速，最大线程数5
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_mirror = {
            executor.submit(check_mirror_speed, m): m 
            for m in mirrors
        }
        
        for future in as_completed(future_to_mirror):
            try:
                data = future.result()
                tested_mirrors.append(data)
            except Exception:
                continue

    if not tested_mirrors or not any(m["status"] for m in tested_mirrors):
        raise ConnectionError("No available mirrors found")

    # 按延迟排序：可用镜像在前（按延迟升序），不可用镜像在后
    tested_mirrors.sort(key=lambda x: (not x["status"], x["delay"]))

    # 写入缓存（仍然缓存最优的那个）
    best = tested_mirrors[0]
    if cache_ttl > 0 and not force:
        try:
            cache = _load_speed_cache()
            cache_key = _get_cache_key(mirrors)
            cache[cache_key] = {
                "timestamp": time.time(),
                "best_mirror": best
            }
            _save_speed_cache(cache)
        except Exception:
            pass

    return tested_mirrors

def get_best_mirror(mirrors: list, cache_ttl: int = 3600, force: bool = False, tool_name: str = None) -> dict:
    """
    并发测速并筛选最优镜像（兼容旧接口）
    :param mirrors: 镜像列表
    :param cache_ttl: 缓存有效期（秒），默认1小时
    :param force: 是否强制测速（忽略缓存）
    :param tool_name: 工具名称（如 pip, conda），用于检查锁定配置
    :return: 延迟最低的可用镜像
    :raises ConnectionError: 无可用镜像时抛出
    """
    if not mirrors:
        raise ConnectionError("No mirrors provided")

    # 0. 检查用户配置锁定
    if tool_name:
        locked_mirror_name = get_config_value(f"{tool_name}.mirror")
        if locked_mirror_name:
            for m in mirrors:
                if m["name"] == locked_mirror_name:
                    result = m.copy()
                    result["delay"] = 0
                    result["status"] = True
                    return result

    # 1. 尝试读缓存
    if not force and cache_ttl > 0:
        cache = _load_speed_cache()
        cache_key = _get_cache_key(mirrors)
        if cache_key in cache:
            entry = cache[cache_key]
            if time.time() - entry.get("timestamp", 0) < cache_ttl:
                cached_name = entry.get("best_mirror", {}).get("name")
                for m in mirrors:
                    if m["name"] == cached_name:
                        return entry["best_mirror"]

    # 2. 使用 get_ranked_mirrors 获取排序结果
    ranked = get_ranked_mirrors(mirrors, cache_ttl=cache_ttl, force=force, tool_name=tool_name)
    return ranked[0]

