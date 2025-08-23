#!/usr/bin/env python3
"""Basic functionality tests."""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test module imports."""
    try:
        from prompts_tool.core.config import Config
        from prompts_tool.core.repo import PromptRepo
        from prompts_tool.core.parser import PromptParser
        from prompts_tool.core.search import PromptSearcher
        from prompts_tool.utils.clipboard import ClipboardManager
        print("✅ All modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Module import failed: {e}")
        return False

def test_config():
    """Test configuration management."""
    try:
        from prompts_tool.core.config import Config
        
        # Create default configuration
        config = Config()
        print("✅ Configuration created successfully")
        print(f"   Repository URL: {config.repo.url}")
        print(f"   Local path: {config.repo.local_path}")
        print(f"   Model name: {config.model.name}")
        
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_parser():
    """Test placeholder parsing."""
    try:
        from prompts_tool.core.parser import PromptParser
        
        parser = PromptParser()
        
        # Test text
        test_text = "Please help me write a {{style}} article about {{topic}} around {{length}} words."
        
        # Extract variables
        variables = parser.extract_variables(test_text)
        print(f"✅ Variable extraction succeeded: {variables}")
        
        # Test variable filling
        var_values = {"topic": "AI", "style": "popular science", "length": "1000"}
        filled_text = parser.fill_variables(test_text, var_values)
        print("✅ Variable filling succeeded")
        print(f"   Filled: {filled_text}")
        
        return True
    except Exception as e:
        print(f"❌ Parser test failed: {e}")
        return False

def test_clipboard():
    """Test clipboard functionality."""
    try:
        from prompts_tool.utils.clipboard import ClipboardManager
        
        clipboard = ClipboardManager()
        print(f"✅ Clipboard initialized: {clipboard.get_system_info()}")
        
        if clipboard.is_available():
            print("✅ Clipboard available")
            return True
        else:
            print("⚠️ Clipboard unavailable")
            return False
    except Exception as e:
        print(f"❌ Clipboard test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Starting basic functionality tests...\n")
    
    tests = [
        ("Module imports", test_imports),
        ("Configuration", test_config),
        ("Placeholder parsing", test_parser),
        ("Clipboard", test_clipboard),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"🔍 Testing: {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} passed\n")
            else:
                print(f"❌ {test_name} failed\n")
        except Exception as e:
            print(f"❌ {test_name} raised an exception: {e}\n")
    
    print("=" * 50)
    print(f"📊 Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️ Some tests failed, please check installation and configuration")
        return 1

if __name__ == "__main__":
    sys.exit(main())
