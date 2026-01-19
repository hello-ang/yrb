# 贡献指南

感谢您有兴趣为 **yrb** 做出贡献！我们需要您的帮助来让这个工具变得更好。

## 🛠️ 开发环境搭建

1. **克隆仓库**
   ```bash
   git clone https://github.com/hello-ang/yrb.git
   cd yrb
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # Linux/macOS
   source venv/bin/activate
   ```

3. **安装开发依赖**
   ```bash
   pip install -e .
   pip install pytest build twine click platformdirs requests
   ```

## 🧪 运行测试

在提交代码前，请确保通过所有测试。本项目支持 `unittest` 和 `pytest`。

```bash
# 使用 unittest (推荐)
python -m unittest discover tests

# 或者使用 pytest
pytest
```

我们配置了 GitHub Actions CI，每次提交都会自动运行测试。请确保您的修改不会破坏现有功能。

## 📝 代码规范

- 代码风格遵循 **PEP 8**。
- 请为新功能添加相应的注释和文档字符串。
- 保持代码简洁，避免冗余逻辑。
- 所有的适配器模块应放在 `yrb/adapter/` 目录下。

## 🚀 提交 Pull Request

1. Fork 本仓库。
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)。
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)。
4. 推送到分支 (`git push origin feature/AmazingFeature`)。
5. 开启一个 Pull Request。

## 🐛 发现 Bug？

如果您发现了 Bug，请在 Issues 中提交报告，并包含以下信息：
- 操作系统版本
- Python 版本
- `yrb` 版本 (`yrb info`)
- 复现步骤
- 错误日志

感谢您的贡献！
