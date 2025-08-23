#!/bin/bash

# 🚀 Prompts Tool 全局安装脚本
# 用于强制重新安装和修复全局安装问题

set -e  # 遇到错误立即退出

echo "🚀 开始全局安装 Prompts Tool..."

# 检查 Python 版本
echo "📋 检查 Python 版本..."
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
echo "✅ Python 版本: $python_version"

# 检查 pip 是否可用
echo "📋 检查 pip 是否可用..."
if ! command -v pip &> /dev/null; then
    echo "❌ pip 不可用，尝试使用 pip3..."
    if ! command -v pip3 &> /dev/null; then
        echo "❌ pip3 也不可用，请先安装 pip"
        exit 1
    fi
    PIP_CMD="pip3"
else
    PIP_CMD="pip"
fi

echo "✅ 使用 pip 命令: $PIP_CMD"

# 检查当前安装状态
echo "📋 检查当前安装状态..."
if $PIP_CMD list | grep -q "prompts-tool"; then
    echo "⚠️  发现已安装的 prompts-tool，准备重新安装..."
    echo "📦 当前版本信息:"
    $PIP_CMD list | grep "prompts-tool"
else
    echo "✅ 未发现已安装的 prompts-tool，将进行全新安装"
fi

# 检查虚拟环境
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "⚠️  检测到虚拟环境: $VIRTUAL_ENV"
    echo "💡 建议在虚拟环境中进行开发，但全局安装也可以"
    read -p "是否继续全局安装？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ 安装已取消"
        exit 1
    fi
fi

# 强制重新安装
echo "🔄 开始强制重新安装..."
echo "📦 安装命令: $PIP_CMD install -e . --force-reinstall"

if $PIP_CMD install -e . --force-reinstall; then
    echo "✅ 安装成功！"
else
    echo "❌ 安装失败，尝试使用 --upgrade 参数..."
    if $PIP_CMD install -e . --upgrade; then
        echo "✅ 使用 --upgrade 安装成功！"
    else
        echo "❌ 安装仍然失败，请检查错误信息"
        exit 1
    fi
fi

# 验证安装
echo "📋 验证安装..."
if $PIP_CMD list | grep -q "prompts-tool"; then
    echo "✅ prompts-tool 已成功安装"
    echo "📦 版本信息:"
    $PIP_CMD list | grep "prompts-tool"
else
    echo "❌ 安装验证失败"
    exit 1
fi

# 测试基本功能
echo "🧪 测试基本功能..."
echo "📋 测试帮助命令..."

if prompts --help &> /dev/null; then
    echo "✅ 帮助命令测试成功"
else
    echo "❌ 帮助命令测试失败，错误信息："
    prompts --help
    echo ""
    echo "💡 虽然安装成功，但可能有配置问题需要修复"
fi

# 显示使用说明
echo ""
echo "🎉 安装完成！"
echo ""
echo "📖 使用方法："
echo "  prompts --help          # 查看帮助"
echo "  prompts --ui            # 启动 Web 界面"
echo "  prompts --list          # 列出所有 Prompt"
echo "  prompts '关键词'        # 搜索 Prompt"
echo "  prompts --update        # 更新仓库"
echo ""
echo "🌐 Web 界面："
echo "  启动后访问: http://localhost:8501"
echo ""
echo "🔧 如果遇到问题："
echo "  1. 检查配置文件: ~/.prompts/config.yaml"
echo "  2. 重新运行此脚本: ./install_global.sh"
echo "  3. 使用简化版: python -m prompts_tool.cli_simple --ui"
echo ""
echo "🚀 开始使用 Prompts Tool 吧！"
