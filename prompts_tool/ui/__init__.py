"""UI module containing Streamlit web interfaces."""

# Avoid importing problematic modules
# from .streamlit_app import create_app

# Simplified application
from .streamlit_app_simple import create_app

__all__ = ["create_app"]
