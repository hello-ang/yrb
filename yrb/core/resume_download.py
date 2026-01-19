"""
断点续传模块
实现基于HTTP Range的大文件断点续传与Hash校验
"""
import os
import hashlib
import requests
from typing import Tuple, Optional

def calculate_file_hash(file_path: str, chunk_size: int = 8192) -> str:
    """计算文件SHA256哈希"""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def resume_download(url: str, save_path: str, expected_hash: Optional[str] = None) -> Tuple[bool, str]:
    """
    断点续传下载文件
    :param url: 文件URL
    :param save_path: 保存路径
    :param expected_hash: 期望的文件哈希（SHA256），用于校验
    :return: (是否成功, 最终文件路径或错误信息)
    """
    temp_path = save_path + ".tmp"
    headers = {}
    mode = "wb"
    
    # 检查临时文件是否存在以决定是否续传
    if os.path.exists(temp_path):
        existing_size = os.path.getsize(temp_path)
        headers["Range"] = f"bytes={existing_size}-"
        mode = "ab"
    
    try:
        response = requests.get(url, headers=headers, stream=True, timeout=10)
        response.raise_for_status()
        
        # 写入文件
        with open(temp_path, mode) as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    
        # 校验哈希
        if expected_hash:
            actual_hash = calculate_file_hash(temp_path)
            if actual_hash != expected_hash:
                os.remove(temp_path)
                return False, "Hash mismatch"
                
        # 重命名为正式文件
        if os.path.exists(save_path):
            os.remove(save_path)
        os.rename(temp_path, save_path)
        
        return True, save_path
        
    except (requests.RequestException, OSError, Exception) as e:
        return False, str(e)
