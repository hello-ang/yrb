# yrb - Python国内下载加速工具

[![PyPI version](https://badge.fury.io/py/yrb.svg)](https://badge.fury.io/py/yrb)
[![Downloads](https://pepy.tech/badge/yrb)](https://pepy.tech/project/yrb)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)

`yrb` 是一个极简的 Python 国内下载加速工具，专为解决 pip/conda 下载慢、连接超时等问题设计。它通过“前缀式命令”自动注入最优国内镜像，**不修改系统配置，不残留环境变量**。

## ✨ 核心特性

- **极速体验**：自动测速并选择最快的国内镜像（阿里云、清华、腾讯、华为、中科大、豆瓣等）。
- **零侵入**：仅在当前命令生效，不修改 `pip.conf` 或 `.condarc`。
- **全兼容**：完美支持 `yrb pip ...` 和 `yrb conda ...`，兼容所有原生参数。
- **智能缓存**：内置本地缓存机制，重复下载秒级完成。
- **断点续传**：支持大文件断点续传，网络波动也不怕。
- **轻量级**：安装包体积 <500KB，无冗余依赖。

## 🚀 快速开始

### 安装

```bash
pip install yrb
```

### 使用方法

**1. 加速 pip**

只需在 `pip` 命令前加上 `yrb`：

```bash
# 安装包（自动加速）
yrb pip install numpy pandas

# 或者使用 python -m pip（推荐）
yrb python -m pip install numpy

# 安装 requirements.txt
yrb pip install -r requirements.txt

# 升级包
yrb pip install --upgrade requests
```

**2. 加速 conda**

同样在 `conda` 命令前加上 `yrb`：

```bash
# 安装包
yrb conda install pytorch

# 创建环境
yrb conda create -n myenv python=3.9
```

**3. 辅助命令**

```bash
# 查看支持的镜像与当前配置
yrb info

# 清理本地缓存
yrb clean

# 网络连通性自检
yrb test
```

**4. 加速现代包管理器**

```bash
# 加速 pdm
yrb pdm add requests

# 加速 uv
yrb uv pip install requests

# 加速 poetry (实验性)
yrb poetry add requests
```

**5. 持久化配置**

如果您希望锁定使用特定的镜像源，或者需要管理其他偏好设置，可以使用 `config` 命令：

```bash
# 查看所有配置
yrb config list

# 锁定 pip 使用阿里云镜像（不再自动测速）
yrb config set pip.mirror aliyun

# 查看当前锁定的 pip 镜像
yrb config get pip.mirror

# 取消锁定（恢复自动测速）
yrb config unset pip.mirror
```

## 🛠️ 常见问题

**Q: `yrb` 会修改我的 pip/conda 配置文件吗？**
A: **不会**。`yrb` 通过临时环境变量注入配置，命令执行结束后立即失效，不会对您的系统环境产生任何持久化影响。

**Q: 支持哪些操作系统？**
A: 完美支持 Windows, macOS, Linux。

**Q: 遇到 "MirrorUnavailableError" 或包版本找不到怎么办？**
A: 这可能是因为国内镜像同步有延迟。您可以：
1. 等待一段时间再试。
2. **手动指定官方源**（`yrb` 会自动检测并停止注入镜像）：
   ```bash
   yrb pip install package_name -i https://pypi.org/simple
   ```

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源。

Copyright (c) 2026 杨如斌 (Rubin Yang) - 兰州文理学院

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！详情请查看 [贡献指南](CONTRIBUTING.md)。

