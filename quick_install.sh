#!/bin/bash

# 🚀 Prompts Tool 快速安装脚本
# 一键强制重新安装

echo "🚀 快速重新安装 Prompts Tool..."

# 强制重新安装
echo "📦 执行: pip install -e . --force-reinstall"
pip install -e . --force-reinstall

# 测试安装
echo "🧪 测试安装..."
if prompts --help &> /dev/null; then
    echo "✅ 安装成功！现在可以使用 prompts 命令了"
    echo ""
    echo "📖 快速开始："
    echo "  prompts --ui      # 启动 Web 界面"
    echo "  prompts --list    # 列出 Prompt"
    echo "  prompts 'Python'  # 搜索 Prompt"
else
    echo "❌ 安装可能有问题，错误信息："
    prompts --help
    echo ""
    echo "💡 建议使用简化版："
    echo "  python -m prompts_tool.cli_simple --ui"
fi
