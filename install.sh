#!/bin/bash

# Prompts Tool 安装脚本

set -e

echo "🚀 开始安装 Prompts Tool..."

# 检查 Python 版本
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ 需要 Python 3.8 或更高版本，当前版本: $python_version"
    exit 1
fi

echo "✅ Python 版本检查通过: $python_version"

# 检查 pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ 未找到 pip3，请先安装 pip"
    exit 1
fi

echo "✅ pip3 检查通过"

# 创建虚拟环境（可选）
read -p "是否创建虚拟环境？(y/n): " create_venv
if [[ $create_venv =~ ^[Yy]$ ]]; then
    echo "🔧 创建虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✅ 虚拟环境已创建并激活"
    echo "💡 使用 'source venv/bin/activate' 来激活虚拟环境"
fi

# 升级 pip
echo "🔄 升级 pip..."
pip3 install --upgrade pip

# 安装依赖
echo "📦 安装依赖包..."
pip3 install -r requirements.txt

# 安装开发依赖（可选）
read -p "是否安装开发依赖？(y/n): " install_dev
if [[ $install_dev =~ ^[Yy]$ ]]; then
    echo "🔧 安装开发依赖..."
    pip3 install -e ".[dev]"
else
    echo "🔧 安装基本依赖..."
    pip3 install -e .
fi

# 创建配置目录
echo "⚙️ 创建配置目录..."
mkdir -p ~/.prompts

# 运行基本测试
echo "🧪 运行基本测试..."
python3 test_basic.py

echo ""
echo "🎉 安装完成！"
echo ""
echo "📖 使用方法:"
echo "  prompts --help                    # 查看帮助"
echo "  prompts '需求描述'                # 搜索 Prompt"
echo "  prompts --list                    # 列出所有 Prompt"
echo "  prompts --update                  # 更新仓库"
echo "  prompts --ui                      # 启动 Web 界面"
echo ""
echo "📁 配置文件位置: ~/.prompts/config.yaml"
echo "📁 示例 Prompt: example-prompts/"
echo ""
echo "🚀 开始使用 Prompts Tool 吧！"
