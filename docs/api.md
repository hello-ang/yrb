# yrb API 文档

本文档主要面向开发者，介绍 `yrb.core` 模块中的关键函数接口。

## 1. 测速模块 (`yrb.core.speed_test`)

### `get_best_mirror`

获取当前网络环境下最优的镜像源。

```python
def get_best_mirror(mirrors: list, cache_ttl: int = 3600, force: bool = False, tool_name: str = None) -> dict
```

- **参数**:
  - `mirrors` (list): 镜像配置字典列表，每个字典需包含 `name`, `url` 等字段。
  - `cache_ttl` (int): 测速结果缓存有效期（秒），默认 3600。
  - `force` (bool): 是否强制重新测速，忽略缓存。
  - `tool_name` (str): 工具名称（如 "pip", "conda"），用于检查用户是否在配置中锁定了镜像。
- **返回**: 
  - `dict`: 最优镜像配置字典，包含 `delay` (ms) 字段。
- **异常**:
  - `ConnectionError`: 如果所有镜像都不可用。

## 2. 配置管理模块 (`yrb.core.config_manager`)

### `load_config`

加载用户配置。

```python
def load_config() -> dict
```
- **返回**: 配置字典。

### `set_config_value`

设置配置项，支持嵌套键（如 `pip.mirror`）。

```python
def set_config_value(key: str, value: str)
```
- **参数**:
  - `key` (str): 配置键，支持点号分隔。
  - `value` (str): 配置值。

### `get_config_value`

获取配置项。

```python
def get_config_value(key: str) -> str | None
```
- **参数**:
  - `key` (str): 配置键。
- **返回**: 配置值，若不存在返回 `None`。

## 3. 缓存管理模块 (`yrb.core.cache_manager`)

### `get_cached_package`

查询本地是否有已缓存的包。

```python
def get_cached_package(pkg_name: str, version: str) -> str
```
- **参数**:
  - `pkg_name` (str): 包名。
  - `version` (str): 版本号。
- **返回**: 本地文件绝对路径，若无缓存返回空字符串。

### `cache_package`

将下载的文件存入缓存。

```python
def cache_package(pkg_name: str, version: str, file_path: str, file_hash: str = "") -> bool
```
- **参数**:
  - `pkg_name` (str): 包名。
  - `version` (str): 版本号。
  - `file_path` (str): 源文件路径。
- **返回**: 缓存是否成功。

## 4. 镜像池模块 (`yrb.core.mirror_pool`)

### `get_mirrors`

获取指定工具的可用镜像列表。

```python
def get_mirrors(tool_type: str) -> list
```
- **参数**:
  - `tool_type` (str): 工具类型，如 "pip", "conda"。
- **返回**: 镜像配置字典列表。
