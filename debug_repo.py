#!/usr/bin/env python3
"""
调试仓库问题
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from prompts_tool.core.config import Config
from prompts_tool.core.repo import PromptRepo

def main():
    config = Config.load()
    repo = PromptRepo(config)
    
    print(f"仓库路径: {repo.repo_path}")
    print(f"仓库路径存在: {repo.repo_path.exists()}")
    
    # 列出所有文件
    all_files = list(repo.repo_path.rglob("*"))
    print(f"所有文件: {len(all_files)}")
    for f in all_files:
        if f.is_file():
            print(f"  - {f} (扩展名: {f.suffix})")
    
    # 测试 rglob 扩展名匹配
    extensions = [".txt", ".md", ".prompt"]
    for ext in extensions:
        files = list(repo.repo_path.rglob(f"*{ext}"))
        print(f"扩展名 {ext}: {len(files)} 个文件")
        for f in files:
            print(f"  - {f}")
    
    # 检查 Prompt 文件
    prompt_files = repo.get_prompt_files()
    print(f"找到的 Prompt 文件: {len(prompt_files)}")
    for f in prompt_files:
        print(f"  - {f}")
    
    # 检查仓库是否存在
    print(f"仓库存在: {repo.exists()}")
    
    # 列出 Prompt
    prompts = repo.list_prompts()
    print(f"列出的 Prompt: {len(prompts)}")

if __name__ == "__main__":
    main()
