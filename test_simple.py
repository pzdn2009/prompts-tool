#!/usr/bin/env python3
"""Simplified feature tests - only basic functionality."""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_config():
    """Test configuration management."""
    try:
        from prompts_tool.core.config import Config
        
        # Create default configuration
        config = Config()
        print("✅ Configuration created successfully")
        print(f"   Repository URL: {config.repo.url}")
        print(f"   Local paths: {config.repo.local_paths}")
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

def test_repo():
    """Test repository management (without Git)."""
    try:
        from prompts_tool.core.config import Config
        from prompts_tool.core.repo import PromptRepo
        
        config = Config()
        repo = PromptRepo(config)
        
        print("✅ Repository management initialized")
        print(f"   Repository path: {repo.repo_path}")
        print(f"   Index path: {repo.index_path}")
        
        # Test path generation
        repo_path = config.get_repo_path()
        index_path = config.get_index_path()
        print(f"   Config path: {repo_path}")
        print(f"   Config index: {index_path}")
        
        return True
    except Exception as e:
        print(f"❌ Repository management test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Starting simplified feature tests...\n")
    
    tests = [
        ("Configuration", test_config),
        ("Placeholder parsing", test_parser),
        ("Clipboard", test_clipboard),
        ("Repository", test_repo),
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
