"""
配置管理模块
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field


@dataclass
class RepoConfig:
    """Prompt repository configuration"""
    url: str = "https://github.com/yourusername/prompts-repo.git"
    local_paths: List[str] = field(default_factory=lambda: ["~/.prompts/repo"])
    branch: str = "main"


@dataclass
class UIConfig:
    """UI configuration"""
    port: int = 8501
    host: str = "localhost"


@dataclass
class Config:
    """Main configuration class"""
    repo: RepoConfig = field(default_factory=RepoConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    
    def __post_init__(self):
        # Expand user paths
        self.repo.local_paths = [os.path.expanduser(p) for p in self.repo.local_paths]
    
    @classmethod
    def load(cls, config_path: Optional[str] = None) -> "Config":
        """加载配置文件"""
        if config_path is None:
            config_path = os.path.expanduser("~/.prompts/config.yaml")
        
        config_file = Path(config_path)
        
        if not config_file.exists():
            # 创建默认配置
            config = cls()
            config.save(config_path)
            return config
        
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f)
            
            # 创建配置对象
            config = cls()
            
            # Update repo configuration
            if "repo" in config_data:
                repo_data = config_data["repo"]
                if "url" in repo_data:
                    config.repo.url = repo_data["url"]
                if "local_paths" in repo_data:
                    config.repo.local_paths = repo_data["local_paths"]
                elif "local_path" in repo_data:
                    # Backward compatibility
                    config.repo.local_paths = [repo_data["local_path"]]
                if "branch" in repo_data:
                    config.repo.branch = repo_data["branch"]
            
            # Update UI configuration
            if "ui" in config_data:
                ui_data = config_data["ui"]
                if "port" in ui_data:
                    config.ui.port = ui_data["port"]
                if "host" in ui_data:
                    config.ui.host = ui_data["host"]
            
            return config
            
        except Exception as e:
            print(f"警告: 无法加载配置文件 {config_path}: {e}")
            return cls()
    
    def save(self, config_path: Optional[str] = None) -> None:
        """保存配置文件"""
        if config_path is None:
            config_path = os.path.expanduser("~/.prompts/config.yaml")
        
        config_file = Path(config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        config_data = {
            "repo": {
                "url": self.repo.url,
                "local_paths": self.repo.local_paths,
                "branch": self.repo.branch,
            },
            "ui": {
                "port": self.ui.port,
                "host": self.ui.host,
            },
        }
        
        try:
            with open(config_file, "w", encoding="utf-8") as f:
                yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
        except Exception as e:
            print(f"警告: 无法保存配置文件 {config_path}: {e}")
    
    def get_repo_path(self) -> Path:
        """Get the primary local repository path"""
        return Path(self.repo.local_paths[0])

    def get_repo_paths(self) -> List[Path]:
        """Get all configured repository paths"""
        return [Path(p) for p in self.repo.local_paths]

    def get_index_path(self) -> Path:
        """Get the index file path"""
        return self.get_repo_path() / ".prompts_index"
