"""
仓库管理模块 - 处理 Git 操作和 Prompt 文件管理
"""

import os
import subprocess
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from .config import Config


class PromptRepo:
    """Prompt 仓库管理类"""
    
    def __init__(self, config: Config):
        self.config = config
        self.repo_path = config.get_repo_path()
        self.index_path = config.get_index_path()
    
    def exists(self) -> bool:
        """检查本地仓库是否存在"""
        # 检查路径是否存在且包含 Prompt 文件
        if not self.repo_path.exists():
            return False
        
        # 检查是否有 Prompt 文件
        prompt_files = self.get_prompt_files()
        return len(prompt_files) > 0
    
    def clone(self) -> bool:
        """克隆远程仓库"""
        try:
            if self.repo_path.exists():
                shutil.rmtree(self.repo_path)
            
            self.repo_path.parent.mkdir(parents=True, exist_ok=True)
            
            cmd = [
                "git", "clone", 
                "-b", self.config.repo.branch,
                self.config.repo.url, 
                str(self.repo_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"✅ 成功克隆仓库到: {self.repo_path}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ 克隆仓库失败: {e}")
            print(f"错误输出: {e.stderr}")
            return False
        except Exception as e:
            print(f"❌ 克隆仓库时发生错误: {e}")
            return False
    
    def pull(self) -> bool:
        """拉取最新更新"""
        try:
            if not self.exists():
                return self.clone()
            
            # 检查是否是 Git 仓库
            if (self.repo_path / ".git").exists():
                # 切换到指定分支
                subprocess.run(
                    ["git", "checkout", self.config.repo.branch],
                    cwd=self.repo_path,
                    capture_output=True,
                    check=True
                )
                
                # 拉取最新更新
                result = subprocess.run(
                    ["git", "pull", "origin", self.config.repo.branch],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                print(f"✅ 成功更新仓库")
                if result.stdout.strip():
                    print(f"更新内容: {result.stdout.strip()}")
                return True
            else:
                print("⚠️ 本地目录不是 Git 仓库，跳过更新")
                return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ 更新仓库失败: {e}")
            print(f"错误输出: {e.stderr}")
            return False
        except Exception as e:
            print(f"❌ 更新仓库时发生错误: {e}")
            return False
    
    def update(self) -> bool:
        """更新仓库（clone 或 pull）"""
        print(f"🔄 正在更新 Prompt 仓库...")
        print(f"仓库地址: {self.config.repo.url}")
        print(f"本地路径: {self.repo_path}")
        
        if self.exists():
            print("📁 本地仓库已存在，正在拉取最新更新...")
            return self.pull()
        else:
            print("📁 本地仓库不存在，正在克隆...")
            return self.clone()
    
    def get_prompt_files(self, extensions: Optional[List[str]] = None) -> List[Path]:
        """获取所有 Prompt 文件"""
        if not self.repo_path.exists():
            return []
        
        if extensions is None:
            extensions = [".txt", ".md", ".prompt"]
        
        prompt_files = []
        
        for ext in extensions:
            prompt_files.extend(self.repo_path.rglob(f"*{ext}"))
        
        # 过滤掉隐藏文件和 .git 目录
        prompt_files = [
            f for f in prompt_files 
            if not f.name.startswith(".")  # 只过滤文件名，不过滤路径
            and ".git" not in f.parts
        ]
        
        return sorted(prompt_files)
    
    def get_prompt_content(self, file_path: Path) -> str:
        """获取 Prompt 文件内容"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"警告: 无法读取文件 {file_path}: {e}")
            return ""
    
    def get_prompt_summary(self, file_path: Path, max_lines: int = 3) -> str:
        """获取 Prompt 文件摘要（前几行）"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = []
                for i, line in enumerate(f):
                    if i >= max_lines:
                        break
                    line = line.strip()
                    if line:
                        lines.append(line)
                return " | ".join(lines)
        except Exception as e:
            return f"无法读取文件: {e}"
    
    def list_prompts(self, preview_lines: Optional[int] = None, 
                     filter_keyword: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出所有 Prompt 文件"""
        if not self.exists():
            print("❌ 本地仓库不存在，请先运行 `prompts --update`")
            return []
        
        prompt_files = self.get_prompt_files()
        
        if filter_keyword:
            prompt_files = [
                f for f in prompt_files 
                if filter_keyword.lower() in f.name.lower() or 
                   filter_keyword.lower() in self.get_prompt_content(f).lower()
            ]
        
        results = []
        for file_path in prompt_files:
            relative_path = file_path.relative_to(self.repo_path)
            
            result = {
                "file_path": file_path,
                "relative_path": str(relative_path),
                "name": file_path.name,
                "summary": self.get_prompt_summary(file_path, 1)
            }
            
            if preview_lines:
                result["preview"] = self.get_prompt_summary(file_path, preview_lines)
            
            results.append(result)
        
        return results
    
    def search_prompts(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """搜索相关的 Prompt（需要先建立索引）"""
        # 这个方法将在 search.py 中实现
        # 这里只是占位符
        pass
    
    def get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """获取文件信息"""
        if not file_path.exists():
            return {}
        
        try:
            stat = file_path.stat()
            return {
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "created": stat.st_ctime,
            }
        except Exception:
            return {}
