#!/usr/bin/env python3
"""
基本功能测试
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """测试模块导入"""
    try:
        from prompts_tool.core.config import Config
        from prompts_tool.core.repo import PromptRepo
        from prompts_tool.core.parser import PromptParser
        from prompts_tool.core.search import PromptSearcher
        from prompts_tool.utils.clipboard import ClipboardManager
        print("✅ 所有模块导入成功")
        return True
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def test_config():
    """测试配置管理"""
    try:
        from prompts_tool.core.config import Config
        
        # 创建默认配置
        config = Config()
        print(f"✅ 配置创建成功")
        print(f"   仓库 URL: {config.repo.url}")
        print(f"   本地路径: {config.repo.local_path}")
        print(f"   模型名称: {config.model.name}")
        
        return True
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return False

def test_parser():
    """测试占位符解析"""
    try:
        from prompts_tool.core.parser import PromptParser
        
        parser = PromptParser()
        
        # 测试文本
        test_text = "请帮我写一个关于 {{topic}} 的 {{style}} 文章，长度约 {{length}} 字。"
        
        # 提取变量
        variables = parser.extract_variables(test_text)
        print(f"✅ 变量提取成功: {variables}")
        
        # 测试变量填充
        var_values = {"topic": "人工智能", "style": "科普", "length": "1000"}
        filled_text = parser.fill_variables(test_text, var_values)
        print(f"✅ 变量填充成功")
        print(f"   填充后: {filled_text}")
        
        return True
    except Exception as e:
        print(f"❌ 解析器测试失败: {e}")
        return False

def test_clipboard():
    """测试剪贴板功能"""
    try:
        from prompts_tool.utils.clipboard import ClipboardManager
        
        clipboard = ClipboardManager()
        print(f"✅ 剪贴板初始化成功: {clipboard.get_system_info()}")
        
        if clipboard.is_available():
            print("✅ 剪贴板可用")
            return True
        else:
            print("⚠️ 剪贴板不可用")
            return False
    except Exception as e:
        print(f"❌ 剪贴板测试失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("🧪 开始运行基本功能测试...\n")
    
    tests = [
        ("模块导入", test_imports),
        ("配置管理", test_config),
        ("占位符解析", test_parser),
        ("剪贴板功能", test_clipboard),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"🔍 测试: {test_name}")
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
        print("🎉 所有测试通过！")
        return 0
    else:
        print("⚠️ 部分测试失败，请检查安装和配置")
        return 1

if __name__ == "__main__":
    sys.exit(main())
