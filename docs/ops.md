# yrb 部署运维手册

## 1. 环境准备

开发与构建 `yrb` 需要以下环境：

- Python 3.8+
- 依赖管理工具：建议使用 `venv`。
- 构建工具：`build`
- 发布工具：`twine`

```bash
# 安装构建依赖
pip install build twine
```

## 2. 本地开发与调试

### 2.1 安装为可编辑模式

在项目根目录下执行：

```bash
pip install -e .
```

安装后，修改代码会立即生效，无需重新安装。

### 2.2 运行测试

可以使用 `test` 命令进行自检：

```bash
yrb test
```

## 3. 构建流程

在发布新版本前，需要构建源码包 (sdist) 和轮子包 (wheel)。

1. **清理旧构建**（可选但推荐）：
   删除 `dist/` 目录下的旧文件。

2. **执行构建**：
   ```bash
   python -m build
   ```

3. **检查产物**：
   构建完成后，检查 `dist/` 目录下是否生成了 `.tar.gz` 和 `.whl` 文件。

4. **验证包元数据**：
   使用 `twine` 检查包描述是否符合 PyPI 规范：
   ```bash
   python -m twine check dist/*
   ```

## 4. 发布流程

### 4.1 更新版本号

发布前务必更新版本号，涉及文件：
- `pyproject.toml`: `version = "x.y.z"`
- `yrb/__init__.py`: `__version__ = "x.y.z"`

### 4.2 上传至 PyPI

确保已拥有 PyPI 账号并生成了 API Token。

```bash
twine upload dist/*
```

当提示输入用户名时，输入 `__token__`。
当提示输入密码时，粘贴你的 API Token（以 `pypi-` 开头）。

## 5. 常见运维问题

### 5.1 版本号冲突
错误：`HTTPError: 400 Client Error: File already exists`
解决：PyPI 不允许覆盖已发布的版本。请增加版本号后重新构建并发布。

### 5.2 依赖缺失
如果用户反馈 `ModuleNotFoundError`，请检查 `pyproject.toml` 中的 `dependencies` 列表是否完整。

### 5.3 权限问题
如果上传失败提示 403 Forbidden，请检查 API Token 是否有对应项目的上传权限。
