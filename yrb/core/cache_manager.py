"""
缓存管理模块
管理包文件的缓存查询、写入与清理
"""
import os
import json
import shutil
import hashlib
from pathlib import Path
from platformdirs import user_cache_dir

CACHE_DIR = Path(user_cache_dir("yrb", "yrb_team"))
CACHE_INDEX_FILE = CACHE_DIR / "index.json"

def _ensure_cache_dir():
    """确保缓存目录存在"""
    if not CACHE_DIR.exists():
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
    if not CACHE_INDEX_FILE.exists():
        try:
            with open(CACHE_INDEX_FILE, "w", encoding="utf-8") as f:
                json.dump({}, f)
        except OSError:
            pass # 无法写入索引则忽略，视为无缓存

def _load_index() -> dict:
    """加载缓存索引"""
    try:
        _ensure_cache_dir()
        if not CACHE_INDEX_FILE.exists():
             return {}
        with open(CACHE_INDEX_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}

def _save_index(index: dict):
    """保存缓存索引"""
    try:
        _ensure_cache_dir()
        with open(CACHE_INDEX_FILE, "w", encoding="utf-8") as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
    except OSError:
        pass # 无法保存索引则忽略

def get_cached_package(pkg_name: str, version: str) -> str:
    """
    查询缓存中的包路径
    :param pkg_name: 包名
    :param version: 版本号
    :return: 缓存文件绝对路径，若无缓存返回空字符串
    """
    index = _load_index()
    key = f"{pkg_name}@{version}"
    record = index.get(key)
    
    if record and os.path.exists(record["path"]):
        return record["path"]
    
    # 缓存记录存在但文件缺失，清理无效记录
    if record:
        del index[key]
        _save_index(index)
        
    return ""

def cache_package(pkg_name: str, version: str, file_path: str, file_hash: str = "") -> bool:
    """
    将文件写入缓存
    :param pkg_name: 包名
    :param version: 版本号
    :param file_path: 源文件路径
    :param file_hash: 文件哈希（可选）
    :return: 是否缓存成功
    """
    if not os.path.exists(file_path):
        return False
        
    _ensure_cache_dir()
    
    # 计算目标路径
    filename = os.path.basename(file_path)
    target_path = CACHE_DIR / filename
    
    try:
        # 如果是不同文件才复制
        if str(target_path) != str(file_path):
            shutil.copy2(file_path, target_path)
            
        # 更新索引
        index = _load_index()
        key = f"{pkg_name}@{version}"
        index[key] = {
            "pkg_name": pkg_name,
            "version": version,
            "path": str(target_path),
            "hash": file_hash
        }
        _save_index(index)
        return True
    except OSError:
        return False

def clean_cache() -> bool:
    """
    清理所有缓存
    :return: 是否清理成功
    """
    try:
        if CACHE_DIR.exists():
            shutil.rmtree(CACHE_DIR)
        return True
    except OSError:
        return False
