"""
配置管理模块
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class RepoConfig:
    """Prompt Repo 配置"""
    url: str = "https://github.com/yourusername/prompts-repo.git"
    local_path: str = "~/.prompts/repo"
    branch: str = "main"


@dataclass
class ModelConfig:
    """模型配置"""
    name: str = "all-MiniLM-L6-v2"
    device: str = "cpu"


@dataclass
class UIConfig:
    """UI 配置"""
    port: int = 8501
    host: str = "localhost"


@dataclass
class Config:
    """主配置类"""
    repo: RepoConfig = field(default_factory=RepoConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    
    def __post_init__(self):
        # 展开用户路径
        self.repo.local_path = os.path.expanduser(self.repo.local_path)
    
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
            
            # 更新 repo 配置
            if "repo" in config_data:
                repo_data = config_data["repo"]
                if "url" in repo_data:
                    config.repo.url = repo_data["url"]
                if "local_path" in repo_data:
                    config.repo.local_path = repo_data["local_path"]
                if "branch" in repo_data:
                    config.repo.branch = repo_data["branch"]
            
            # 更新 model 配置
            if "model" in config_data:
                model_data = config_data["model"]
                if "name" in model_data:
                    config.model.name = model_data["name"]
                if "device" in model_data:
                    config.model.device = model_data["device"]
            
            # 更新 ui 配置
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
                "local_path": self.repo.local_path,
                "branch": self.repo.branch,
            },
            "model": {
                "name": self.model.name,
                "device": self.model.device,
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
        """获取本地仓库路径"""
        return Path(self.repo.local_path)
    
    def get_index_path(self) -> Path:
        """获取索引文件路径"""
        return Path(self.repo.local_path) / ".prompts_index"
