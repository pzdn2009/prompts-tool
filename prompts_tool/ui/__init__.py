"""
UI 模块 - 包含 Streamlit Web 界面
"""

# 避免导入有问题的模块
# from .streamlit_app import create_app

# 简化版应用
from .streamlit_app_simple import create_app

__all__ = ["create_app"]
