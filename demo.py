#!/usr/bin/env python3
"""
Prompts Tool 功能演示脚本
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from prompts_tool.core.config import Config
from prompts_tool.core.repo import PromptRepo
from prompts_tool.core.parser import PromptParser
from prompts_tool.utils.clipboard import ClipboardManager

def demo_config():
    """演示配置管理"""
    print("🔧 配置管理演示")
    print("=" * 50)
    
    config = Config.load()
    print(f"仓库 URL: {config.repo.url}")
    print(f"本地路径: {config.repo.local_path}")
    print(f"模型名称: {config.model.name}")
    print(f"UI 端口: {config.ui.port}")
    print()

def demo_parser():
    """演示占位符解析"""
    print("📝 占位符解析演示")
    print("=" * 50)
    
    parser = PromptParser()
    
    # 测试文本
    test_text = "请帮我写一个关于 {{topic}} 的 {{style}} 文章，长度约 {{length}} 字。"
    print(f"原始文本: {test_text}")
    
    # 提取变量
    variables = parser.extract_variables(test_text)
    print(f"提取的变量: {variables}")
    
    # 填充变量
    var_values = {"topic": "人工智能", "style": "科普", "length": "1000"}
    filled_text = parser.fill_variables(test_text, var_values)
    print(f"填充后: {filled_text}")
    print()

def demo_repo():
    """演示仓库管理"""
    print("📁 仓库管理演示")
    print("=" * 50)
    
    config = Config.load()
    repo = PromptRepo(config)
    
    print(f"仓库路径: {repo.repo_path}")
    print(f"仓库存在: {repo.exists()}")
    
    if repo.exists():
        prompt_files = repo.get_prompt_files()
        print(f"Prompt 文件数量: {len(prompt_files)}")
        for f in prompt_files:
            print(f"  - {f.name}")
    print()

def demo_clipboard():
    """演示剪贴板功能"""
    print("📋 剪贴板功能演示")
    print("=" * 50)
    
    clipboard = ClipboardManager()
    print(f"系统信息: {clipboard.get_system_info()}")
    print(f"剪贴板可用: {clipboard.is_available()}")
    
    if clipboard.is_available():
        # 测试复制
        test_text = "这是一个测试文本"
        if clipboard.copy(test_text):
            print(f"✅ 成功复制: {test_text}")
            
            # 测试粘贴
            pasted_text = clipboard.paste()
            if pasted_text:
                print(f"✅ 成功粘贴: {pasted_text}")
            else:
                print("❌ 粘贴失败")
        else:
            print("❌ 复制失败")
    print()

def demo_search():
    """演示搜索功能"""
    print("🔍 搜索功能演示")
    print("=" * 50)
    
    config = Config.load()
    repo = PromptRepo(config)
    parser = PromptParser()
    
    if not repo.exists():
        print("❌ 仓库不存在，跳过搜索演示")
        return
    
    # 搜索 "Python"
    query = "Python"
    print(f"搜索查询: {query}")
    
    all_prompts = repo.list_prompts()
    results = []
    
    for prompt in all_prompts:
        score = 0
        content = repo.get_prompt_content(prompt["file_path"])
        
        # 检查文件名
        if query.lower() in prompt["name"].lower():
            score += 2
        
        # 检查内容
        if query.lower() in content.lower():
            score += 1
        
        # 检查路径
        if query.lower() in prompt["relative_path"].lower():
            score += 1
        
        if score > 0:
            results.append({
                **prompt,
                "score": score,
                "content": content
            })
    
    # 按分数排序
    results.sort(key=lambda x: x["score"], reverse=True)
    
    if results:
        print(f"找到 {len(results)} 个相关结果:")
        for i, result in enumerate(results[:2], 1):  # 只显示前2个
            print(f"  #{i} {result['name']} (相关度: {result['score']})")
            print(f"    路径: {result['relative_path']}")
            print(f"    内容预览: {result['content'][:100]}...")
            print()
    else:
        print("没有找到相关结果")
    print()

def main():
    """运行所有演示"""
    print("🚀 Prompts Tool 功能演示")
    print("=" * 60)
    print()
    
    demos = [
        ("配置管理", demo_config),
        ("占位符解析", demo_parser),
        ("仓库管理", demo_repo),
        ("剪贴板功能", demo_clipboard),
        ("搜索功能", demo_search),
    ]
    
    for demo_name, demo_func in demos:
        try:
            demo_func()
        except Exception as e:
            print(f"❌ {demo_name} 演示失败: {e}")
            print()
    
    print("🎉 演示完成！")
    print()
    print("💡 使用提示:")
    print("  1. 运行 'python -m prompts_tool.cli_simple --help' 查看 CLI 帮助")
    print("  2. 运行 'python -m prompts_tool.cli_simple --list' 列出所有 Prompt")
    print("  3. 运行 'python -m prompts_tool.cli_simple \"关键词\"' 搜索 Prompt")
    print("  4. 运行 'python -m prompts_tool.cli_simple --update' 更新仓库")

if __name__ == "__main__":
    main()
