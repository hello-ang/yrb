"""
配置管理模块
管理用户持久化配置
"""
import json
import os
from pathlib import Path
from platformdirs import user_config_dir

CONFIG_DIR = Path(user_config_dir("yrb", "yrb_team"))
CONFIG_FILE = CONFIG_DIR / "config.json"

def _ensure_config_dir():
    """确保配置目录存在"""
    if not CONFIG_DIR.exists():
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def load_config() -> dict:
    """加载配置"""
    try:
        if not CONFIG_FILE.exists():
            return {}
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_config(config: dict):
    """保存配置"""
    _ensure_config_dir()
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
    except Exception:
        pass

def set_config_value(key: str, value: str):
    """设置配置项"""
    config = load_config()
    # 支持 pip.mirror 这种嵌套键
    if "." in key:
        section, subkey = key.split(".", 1)
        if section not in config:
            config[section] = {}
        config[section][subkey] = value
    else:
        config[key] = value
    save_config(config)

def get_config_value(key: str):
    """获取配置项"""
    config = load_config()
    if "." in key:
        section, subkey = key.split(".", 1)
        return config.get(section, {}).get(subkey)
    return config.get(key)

def unset_config_value(key: str):
    """删除配置项"""
    config = load_config()
    if "." in key:
        section, subkey = key.split(".", 1)
        if section in config and subkey in config[section]:
            del config[section][subkey]
            # 如果 section 空了，也可以清理
            if not config[section]:
                del config[section]
    else:
        if key in config:
            del config[key]
    save_config(config)
