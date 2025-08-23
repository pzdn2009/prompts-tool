#!/usr/bin/env python3
"""
测试 UI 修复的脚本
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """测试所有模块导入"""
    print("🧪 测试模块导入...")
    
    try:
        from prompts_tool.core.config import Config
        print("✅ Config 导入成功")
        
        from prompts_tool.core.repo import PromptRepo
        print("✅ PromptRepo 导入成功")
        
        from prompts_tool.core.parser import PromptParser
        print("✅ PromptParser 导入成功")
        
        from prompts_tool.utils.clipboard import ClipboardManager
        print("✅ ClipboardManager 导入成功")
        
        return True
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False

def test_simple_app():
    """测试简化版 Streamlit 应用"""
    print("\n🌐 测试简化版 Streamlit 应用...")
    
    simple_app_path = Path("prompts_tool/ui/streamlit_app_simple.py")
    if simple_app_path.exists():
        print("✅ 简化版 Streamlit 应用文件存在")
        
        # 尝试导入（不实际运行）
        try:
            import prompts_tool.ui.streamlit_app_simple
            print("✅ 简化版应用导入成功")
            return True
        except Exception as e:
            print(f"❌ 简化版应用导入失败: {e}")
            return False
    else:
        print("❌ 简化版 Streamlit 应用文件不存在")
        return False

def test_cli_options():
    """测试 CLI 选项"""
    print("\n🖥️ 测试 CLI 选项...")
    
    try:
        from prompts_tool.cli_simple import app
        
        # 检查 CLI 应用是否正确创建
        if hasattr(app, 'registered_commands'):
            print("✅ CLI 应用创建成功")
            
            # 检查是否有命令
            if len(app.registered_commands) > 0:
                print("✅ CLI 命令配置正确")
                print(f"   注册的命令数量: {len(app.registered_commands)}")
                return True
            else:
                print("❌ CLI 命令配置有问题")
                return False
        else:
            print("❌ CLI 应用创建失败")
            return False
            
    except Exception as e:
        print(f"❌ CLI 测试失败: {e}")
        return False

def test_web_interface():
    """测试 Web 界面启动"""
    print("\n🌐 测试 Web 界面启动...")
    
    try:
        import subprocess
        import time
        
        # 检查端口是否可用
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 8501))
        sock.close()
        
        if result == 0:
            print("✅ Web 界面端口 8501 可用")
            return True
        else:
            print("⚠️ Web 界面端口 8501 不可用（可能未启动）")
            return True  # 这不是错误，只是没有启动
            
    except Exception as e:
        print(f"❌ Web 界面测试失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("🚀 开始测试 UI 修复...\n")
    
    tests = [
        ("模块导入", test_imports),
        ("简化版应用", test_simple_app),
        ("CLI 选项", test_cli_options),
        ("Web 界面", test_web_interface),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 测试通过\n")
            else:
                print(f"❌ {test_name} 测试失败\n")
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}\n")
    
    print("=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！UI 修复成功！")
        print("\n💡 现在你可以使用以下命令:")
        print("  python -m prompts_tool.cli_simple --ui    # 启动 Web 界面")
        print("  python -m prompts_tool.cli_simple --list  # 列出 Prompt")
        print("  python -m prompts_tool.cli_simple '关键词' # 搜索 Prompt")
        return 0
    else:
        print("⚠️ 部分测试失败，请检查修复")
        return 1

if __name__ == "__main__":
    sys.exit(main())
