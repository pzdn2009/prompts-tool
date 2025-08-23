"""Clipboard management utilities for cross-platform clipboard operations."""

import platform
from typing import Optional


class ClipboardManager:
    """Cross-platform clipboard manager."""
    
    def __init__(self):
        self.system = platform.system()
        self._init_clipboard()
    
    def _init_clipboard(self):
        """Initialize clipboard support for current platform."""
        try:
            if self.system == "Darwin":  # macOS
                import subprocess
                # Ensure pbcopy is available
                subprocess.run(["which", "pbcopy"], capture_output=True, check=True)
                self._copy_method = "pbcopy"
                self._paste_method = "pbpaste"
            elif self.system == "Linux":
                try:
                    import pyperclip
                    pyperclip.copy("test")
                    self._copy_method = "pyperclip"
                except Exception:
                    # Try using xclip
                    import subprocess
                    try:
                        subprocess.run(["which", "xclip"], capture_output=True, check=True)
                        self._copy_method = "xclip"
                    except subprocess.CalledProcessError:
                        # Fallback to xsel
                        try:
                            subprocess.run(["which", "xsel"], capture_output=True, check=True)
                            self._copy_method = "xsel"
                        except subprocess.CalledProcessError:
                            raise Exception("Linux requires pyperclip, xclip, or xsel to be installed")
            elif self.system == "Windows":
                import pyperclip
                pyperclip.copy("test")
                self._copy_method = "pyperclip"
            else:
                raise Exception(f"Unsupported operating system: {self.system}")
                
        except Exception as e:
            print(f"Warning: clipboard initialization failed: {e}")
            self._copy_method = None
    
    def copy(self, text: str) -> bool:
        """Copy text to the clipboard."""
        if not self._copy_method:
            print("❌ Clipboard unavailable")
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
            
            print("✅ Copied to clipboard")
            return True
            
        except Exception as e:
            print(f"❌ Failed to copy to clipboard: {e}")
            return False
    
    def paste(self) -> Optional[str]:
        """Paste text from the clipboard."""
        if not self._copy_method:
            print("❌ Clipboard unavailable")
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
            print(f"❌ Failed to paste from clipboard: {e}")
            return None
        
        return None
    
    def is_available(self) -> bool:
        """Check whether the clipboard is available."""
        return self._copy_method is not None
    
    def get_system_info(self) -> str:
        """Get clipboard-related system information."""
        return f"System: {self.system}, Method: {self._copy_method or 'Unavailable'}"
