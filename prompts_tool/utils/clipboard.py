"""
剪贴板管理模块 - 处理跨平台的剪贴板操作
"""

import platform
from typing import Optional


class ClipboardManager:
    """跨平台剪贴板管理器"""
    
    def __init__(self):
        self.system = platform.system()
        self._init_clipboard()
    
    def _init_clipboard(self):
        """初始化剪贴板"""
        try:
            if self.system == "Darwin":  # macOS
                import subprocess
                # 检查 pbcopy 是否可用
                subprocess.run(["which", "pbcopy"], capture_output=True, check=True)
                self._copy_method = "pbcopy"
                self._paste_method = "pbpaste"
            elif self.system == "Linux":
                try:
                    import pyperclip
                    pyperclip.copy("test")
                    self._copy_method = "pyperclip"
                except Exception:
                    # 尝试使用 xclip
                    import subprocess
                    try:
                        subprocess.run(["which", "xclip"], capture_output=True, check=True)
                        self._copy_method = "xclip"
                    except subprocess.CalledProcessError:
                        # 尝试使用 xsel
                        try:
                            subprocess.run(["which", "xsel"], capture_output=True, check=True)
                            self._copy_method = "xsel"
                        except subprocess.CalledProcessError:
                            raise Exception("Linux 系统需要安装 pyperclip, xclip 或 xsel")
            elif self.system == "Windows":
                import pyperclip
                pyperclip.copy("test")
                self._copy_method = "pyperclip"
            else:
                raise Exception(f"不支持的操作系统: {self.system}")
                
        except Exception as e:
            print(f"警告: 剪贴板初始化失败: {e}")
            self._copy_method = None
    
    def copy(self, text: str) -> bool:
        """复制文本到剪贴板"""
        if not self._copy_method:
            print("❌ 剪贴板不可用")
            return False
        
        try:
            if self._copy_method == "pyperclip":
                import pyperclip
                pyperclip.copy(text)
            elif self._copy_method == "pbcopy":
                import subprocess
                subprocess.run(["pbcopy"], input=text.encode(), check=True)
            elif self._copy_method == "xclip":
                import subprocess
                subprocess.run(["xclip", "-selection", "clipboard"], input=text.encode(), check=True)
            elif self._copy_method == "xsel":
                import subprocess
                subprocess.run(["xsel", "--input", "--clipboard"], input=text.encode(), check=True)
            
            print("✅ 已复制到剪贴板")
            return True
            
        except Exception as e:
            print(f"❌ 复制到剪贴板失败: {e}")
            return False
    
    def paste(self) -> Optional[str]:
        """从剪贴板粘贴文本"""
        if not self._copy_method:
            print("❌ 剪贴板不可用")
            return None
        
        try:
            if self._copy_method == "pyperclip":
                import pyperclip
                return pyperclip.paste()
            elif self._copy_method == "pbpaste":
                import subprocess
                result = subprocess.run(["pbpaste"], capture_output=True, text=True, check=True)
                return result.stdout
            elif self._copy_method == "xclip":
                import subprocess
                result = subprocess.run(["xclip", "-selection", "clipboard", "-o"], capture_output=True, text=True, check=True)
                return result.stdout
            elif self._copy_method == "xsel":
                import subprocess
                result = subprocess.run(["xsel", "--output", "--clipboard"], capture_output=True, text=True, check=True)
                return result.stdout
            
        except Exception as e:
            print(f"❌ 从剪贴板粘贴失败: {e}")
            return None
        
        return None
    
    def is_available(self) -> bool:
        """检查剪贴板是否可用"""
        return self._copy_method is not None
    
    def get_system_info(self) -> str:
        """获取系统信息"""
        return f"系统: {self.system}, 剪贴板方法: {self._copy_method or '不可用'}"
