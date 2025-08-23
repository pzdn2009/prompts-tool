# 🚀 Prompts Tool

一个本地安装的 CLI 工具，用于检索、填充变量、生成最终 Prompt，并提供 Web UI 作为交互式界面。

## ✨ 功能特性

- 🔍 **智能检索**: 使用本地模型做 Embedding，在 Prompt Repo 中检索最相关的 Prompt
- 📝 **变量填充**: 自动解析 `{{variable}}` 占位符，支持 CLI 和 Web UI 两种模式
- 📋 **自动复制**: 生成完整 Prompt 后自动复制到剪贴板
- 📚 **Prompt 管理**: 列出、更新、同步远程 Prompt Repo
- 🌐 **Web 界面**: 基于 Streamlit 的交互式界面
- 🚀 **快速响应**: 搜索延迟 < 1s（本地索引）
- 💻 **跨平台**: 支持 Mac / Linux / Windows

## 🛠️ 安装

### 从源码安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/prompts-tool.git
cd prompts-tool

# 安装依赖
pip install -e .

# 或者安装开发依赖
pip install -e ".[dev]"
```

### 从 PyPI 安装（未来）

```bash
pip install prompts-tool
```

## 🚀 使用方法

### 1. 搜索 Prompt

```bash
# 搜索最相关的 Prompt 并填充变量
prompts "帮我写一个 Python 函数的文档字符串"
```

### 2. 列出所有 Prompt

```bash
# 列出所有 Prompt 文件
prompts list

# 显示前 5 行预览
prompts list --preview 5

# 按关键词过滤
prompts list --filter "python"
```

### 3. 更新 Prompt Repo

```bash
# 更新远程仓库的 Prompt Repo
prompts --update
```

### 4. 启动 Web 界面

```bash
# 启动 Web 界面（搜索+填充）
prompts --ui
```

## ⚙️ 配置

配置文件位置：`~/.prompts/config.yaml`

```yaml
# Prompt Repo 配置
repo:
  url: "https://github.com/yourusername/prompts-repo.git"
  local_path: "~/.prompts/repo"
  branch: "main"

# 模型配置
model:
  name: "all-MiniLM-L6-v2"
  device: "cpu"  # 或 "cuda"

# UI 配置
ui:
  port: 8501
  host: "localhost"
```

## 🏗️ 项目结构

```
prompts-tool/
├── prompts_tool/
│   ├── __init__.py
│   ├── cli.py              # CLI 主入口
│   ├── core/
│   │   ├── __init__.py
│   │   ├── search.py       # 搜索逻辑
│   │   ├── parser.py       # 占位符解析
│   │   ├── repo.py         # 仓库管理
│   │   └── config.py       # 配置管理
│   ├── ui/
│   │   ├── __init__.py
│   │   └── streamlit_app.py # Streamlit 应用
│   └── utils/
│       ├── __init__.py
│       └── clipboard.py    # 剪贴板操作
├── pyproject.toml
├── README.md
└── requirements.txt
```

## 🔧 开发

### 设置开发环境

```bash
# 克隆仓库
git clone https://github.com/yourusername/prompts-tool.git
cd prompts-tool

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装开发依赖
pip install -e ".[dev]"
```

### 运行测试

```bash
pytest
```

### 代码格式化

```bash
black .
isort .
```

## 📝 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 支持

如果你遇到问题或有建议，请：

1. 查看 [Issues](https://github.com/yourusername/prompts-tool/issues)
2. 创建新的 Issue
3. 提交 Pull Request
