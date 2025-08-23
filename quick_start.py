#!/usr/bin/env python3
"""
Prompts Tool 快速启动脚本
"""

import sys
import os
from pathlib import Path

def print_banner():
    """打印欢迎横幅"""
    banner = """
    🚀 Prompts Tool v0.1.0
    ========================
    智能 Prompt 管理助手
    
    快速开始指南：
    """
    print(banner)

def check_environment():
    """检查环境"""
    print("🔍 检查环境...")
    
    # 检查 Python 版本
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ 需要 Python 3.8 或更高版本")
        return False
    
    print(f"✅ Python 版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # 检查项目文件
    project_root = Path(__file__).parent
    required_files = [
        "prompts_tool/core/config.py",
        "prompts_tool/core/parser.py",
        "prompts_tool/core/repo.py",
        "prompts_tool/utils/clipboard.py",
        "prompts_tool/cli_simple.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not (project_root / file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ 缺少文件: {missing_files}")
        return False
    
    print("✅ 项目文件完整")
    return True

def setup_example_prompts():
    """设置示例 Prompt"""
    print("\n📁 设置示例 Prompt...")
    
    config_dir = Path.home() / ".prompts" / "repo"
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # 检查是否已有示例文件
    if list(config_dir.glob("*.txt")) or list(config_dir.glob("*.md")) or list(config_dir.glob("*.prompt")):
        print("✅ 示例 Prompt 已存在")
        return True
    
    # 复制示例文件
    example_dir = Path(__file__).parent / "example-prompts"
    if example_dir.exists():
        import shutil
        for file_path in example_dir.glob("*"):
            if file_path.is_file():
                shutil.copy2(file_path, config_dir)
        print("✅ 示例 Prompt 设置完成")
        return True
    else:
        print("⚠️ 示例 Prompt 目录不存在")
        return False

def run_demo():
    """运行演示"""
    print("\n🎬 运行功能演示...")
    
    try:
        # 添加项目根目录到 Python 路径
        project_root = Path(__file__).parent
        sys.path.insert(0, str(project_root))
        
        from prompts_tool.core.config import Config
        from prompts_tool.core.repo import PromptRepo
        from prompts_tool.core.parser import PromptParser
        
        # 加载配置
        config = Config.load()
        print("✅ 配置加载成功")
        
        # 检查仓库
        repo = PromptRepo(config)
        if repo.exists():
            print("✅ 仓库检查成功")
            
            # 列出 Prompt
            prompts = repo.list_prompts()
            print(f"📚 找到 {len(prompts)} 个 Prompt 文件")
            
            # 测试解析器
            parser = PromptParser()
            test_text = "这是一个测试 {{variable}} 的文本"
            variables = parser.extract_variables(test_text)
            print(f"🔧 解析器测试: 提取到 {len(variables)} 个变量")
            
        else:
            print("⚠️ 仓库不存在，请先设置示例 Prompt")
            
    except Exception as e:
        print(f"❌ 演示运行失败: {e}")
        return False
    
    return True

def show_usage():
    """显示使用方法"""
    print("\n📖 使用方法:")
    print("=" * 50)
    
    print("1. 查看帮助:")
    print("   python -m prompts_tool.cli_simple --help")
    
    print("\n2. 列出所有 Prompt:")
    print("   python -m prompts_tool.cli_simple --list")
    
    print("\n3. 搜索 Prompt:")
    print("   python -m prompts_tool.cli_simple \"Python 函数\"")
    
    print("\n4. 带预览的列表:")
    print("   python -m prompts_tool.cli_simple --list --preview 3")
    
    print("\n5. 过滤结果:")
    print("   python -m prompts_tool.cli_simple --list --filter \"AI\"")
    
    print("\n6. 运行完整演示:")
    print("   python demo.py")
    
    print("\n💡 提示:")
    print("- 工具会自动识别 {{variable}} 格式的变量")
    print("- 搜索完成后会自动复制到剪贴板")
    print("- 配置文件位置: ~/.prompts/config.yaml")

def main():
    """主函数"""
    print_banner()
    
    # 检查环境
    if not check_environment():
        print("\n❌ 环境检查失败，请检查安装")
        return 1
    
    # 设置示例 Prompt
    if not setup_example_prompts():
        print("\n⚠️ 示例 Prompt 设置失败")
    
    # 运行演示
    if not run_demo():
        print("\n⚠️ 演示运行失败")
    
    # 显示使用方法
    show_usage()
    
    print("\n🎉 快速启动完成！")
    print("现在你可以开始使用 Prompts Tool 了！")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
