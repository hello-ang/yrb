"""
镜像池模块
管理国内主流 pip/conda 镜像源配置
"""

# 预定义国内镜像列表（URL/同步状态/信任主机）
MIRRORS = {
    "pip": [
        {
            "name": "aliyun",
            "url": "https://mirrors.aliyun.com/pypi/simple/",
            "trusted_host": "mirrors.aliyun.com",
            "priority": 100
        },
        {
            "name": "tsinghua",
            "url": "https://pypi.tuna.tsinghua.edu.cn/simple",
            "trusted_host": "pypi.tuna.tsinghua.edu.cn",
            "priority": 95
        },
        {
            "name": "tencent",
            "url": "https://mirrors.cloud.tencent.com/pypi/simple",
            "trusted_host": "mirrors.cloud.tencent.com",
            "priority": 90
        },
        {
            "name": "huawei",
            "url": "https://repo.huaweicloud.com/repository/pypi/simple/",
            "trusted_host": "repo.huaweicloud.com",
            "priority": 85
        },
        {
            "name": "ustc",
            "url": "https://pypi.mirrors.ustc.edu.cn/simple/",
            "trusted_host": "pypi.mirrors.ustc.edu.cn",
            "priority": 80
        },
        {
            "name": "douban",
            "url": "https://pypi.doubanio.com/simple/",
            "trusted_host": "pypi.doubanio.com",
            "tool": "pip",
            "desc": "豆瓣 (pip)"
        }
    ],
    "conda": [
        {
            "name": "tsinghua",
            "url": "https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/",
            "channels": [
                "https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/",
                "https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/",
                "https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/"
            ],
            "priority": 100
        },
        {
            "name": "aliyun",
            "url": "https://mirrors.aliyun.com/anaconda/pkgs/main/",
            "channels": [
                "https://mirrors.aliyun.com/anaconda/pkgs/main/",
                "https://mirrors.aliyun.com/anaconda/pkgs/free/",
                "https://mirrors.aliyun.com/anaconda/cloud/conda-forge/"
            ],
            "priority": 95
        },
        {
            "name": "ustc",
            "url": "https://mirrors.ustc.edu.cn/anaconda/pkgs/main/",
            "channels": [
                "https://mirrors.ustc.edu.cn/anaconda/pkgs/main/",
                "https://mirrors.ustc.edu.cn/anaconda/pkgs/free/",
                "https://mirrors.ustc.edu.cn/anaconda/cloud/conda-forge/"
            ],
            "priority": 90
        }
    ]
}

def get_mirrors(tool: str = "pip") -> list:
    """
    获取指定工具的镜像列表
    :param tool: 工具名称 (pip/conda)
    :return: 镜像配置字典列表
    """
    return MIRRORS.get(tool, [])

def add_custom_mirror(tool: str, mirror_config: dict) -> bool:
    """
    添加自定义镜像（临时内存添加，不持久化到文件）
    :param tool: 工具名称
    :param mirror_config: 镜像配置字典
    :return: 是否添加成功
    """
    if tool not in MIRRORS:
        return False
        
    # 简单校验必要字段
    required_keys = ["name", "url"]
    if not all(k in mirror_config for k in required_keys):
        return False
        
    # 查重（按name或url）
    current_list = MIRRORS[tool]
    for m in current_list:
        if m["name"] == mirror_config["name"] or m["url"] == mirror_config["url"]:
            return False
            
    current_list.append(mirror_config)
    return True
