# Changelog

All notable changes to this project will be documented in this file.

## [1.3.1] - 2026-01-19

### Fixed
- **CLI**: 修复 `yrb config` 命令中因导入缺失导致的 `NameError`。

## [1.3.0] - 2026-01-19

### Added
- **Feature**: 新增 `yrb config` 命令，支持配置持久化。
- **Feature**: 支持锁定镜像源（如 `yrb config set pip.mirror aliyun`），跳过自动测速。

## [1.2.2] - 2026-01-19

### Fixed
- **CLI**: 修复 `yrb info` 命令中版本号硬编码问题，现在动态读取包版本。

## [1.2.1] - 2026-01-19

### Changed
- **Doc**: 更新 Poetry 适配器提示信息，建议使用 `poetry source add` 进行永久配置。
- **Core**: 清理 `mirror_pool.py` 中遗留的冗余字段。

## [1.2.0] - 2026-01-19

### Added
- **Adapter**: 新增 `yrb pdm` 支持，自动注入国内镜像配置。
- **Adapter**: 新增 `yrb poetry` 支持（部分支持，尝试注入 pip 兼容变量）。
- **CLI**: `yrb info` 显示更多支持的工具列表。

## [1.1.3] - 2026-01-19

### Documentation
- **Doc**: 新增 `CONTRIBUTING.md` 贡献指南。
- **Doc**: 优化 `README.md`，添加 PyPI 版本/下载量徽章，完善版权与贡献说明。

## [1.1.2] - 2026-01-19

### Fixed
- **Core**: 修复 `adapter` 模块中残留的旧包名引用（`cn` -> `yrb`），解决 `ImportError`。
- **CLI**: 修复帮助文档和输出信息中的旧工具名称残留。

## [1.1.1] - 2026-01-19

### Fixed
- **CLI**: 修复 `exception_handler` 模块中异常类重命名不完整导致的 `NameError`。

## [1.1.0] - 2026-01-19

### Added
- **CLI**: 新增 `yrb python` 命令，智能识别并加速 `yrb python -m pip ...`，同时透传其他 Python 脚本执行。
- **Core**: 新增测速结果缓存机制（默认 1 小时），显著提升二次运行速度。
- **CLI**: `yrb test` 命令新增强制刷新缓存功能。

### Fixed
- **Adapter**: 修复 pip 适配器产生的 "pip is being invoked by an old script wrapper" 警告。
- **Adapter**: 修复 pip 适配器在虚拟环境中可能错误使用全局 pip 的问题（现在优先使用 PATH 中的 python）。
- **Adapter**: 修复手动指定 `-i` 源时可能与自动注入冲突的问题。

## [1.0.0] - 2026-01-19

### Added
- **Core**: 实现国内镜像池管理（阿里云/清华/腾讯/华为/中科大/豆瓣）
- **Core**: 实现 HTTP HEAD 毫秒级并发测速与最优镜像筛选
- **Core**: 实现基于 HTTP Range 的断点续传与 Hash 校验
- **Core**: 实现跨平台缓存管理，支持包文件本地缓存
- **Adapter**: 支持 `yrb pip` 前缀命令，自动注入加速配置，兼容原生参数
- **Adapter**: 支持 `yrb conda` 前缀命令，自动注入镜像 Channels
- **CLI**: 提供 `yrb clean` 缓存清理命令
- **CLI**: 提供 `yrb info` 配置查看命令
- **CLI**: 提供 `yrb test` 网络连通性自检命令

### Optimized
- 移除所有冗余依赖，安装包体积优化至 <500KB
- 优化跨平台兼容性（Windows/Linux/macOS）
- 增强异常处理，提供用户友好的错误提示
