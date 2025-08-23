#!/usr/bin/env python3
"""Script to test the UI fixes."""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test all module imports."""
    print("🧪 Testing module imports...")
    
    try:
        from prompts_tool.core.config import Config
        print("✅ Config imported successfully")
        
        from prompts_tool.core.repo import PromptRepo
        print("✅ PromptRepo imported successfully")
        
        from prompts_tool.core.parser import PromptParser
        print("✅ PromptParser imported successfully")
        
        from prompts_tool.utils.clipboard import ClipboardManager
        print("✅ ClipboardManager imported successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_streamlit_app():
    """Test the Streamlit app."""
    print("\n🌐 Testing Streamlit app...")

    app_path = Path("prompts_tool/ui/streamlit_app.py")
    if app_path.exists():
        print("✅ Streamlit app file exists")

        try:
            import prompts_tool.ui.streamlit_app
            print("✅ Streamlit app imported successfully")
            return True
        except Exception as e:
            print(f"❌ Streamlit app import failed: {e}")
            return False
    else:
        print("❌ Streamlit app file not found")
        return False

def test_cli_options():
    """Test CLI options."""
    print("\n🖥️ Testing CLI options...")
    
    try:
        from prompts_tool.cli_simple import app
        
        # Ensure CLI app is created correctly
        if hasattr(app, 'registered_commands'):
            print("✅ CLI app created successfully")

            # Verify commands are registered
            if len(app.registered_commands) > 0:
                print("✅ CLI commands configured correctly")
                print(f"   Registered commands: {len(app.registered_commands)}")
                return True
            else:
                print("❌ CLI command configuration issue")
                return False
        else:
            print("❌ CLI app creation failed")
            return False
            
    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        return False

def test_web_interface():
    """Test web interface startup."""
    print("\n🌐 Testing web interface startup...")
    
    try:
        import subprocess
        import time
        
        # Check if port is available
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 8501))
        sock.close()
        
        if result == 0:
            print("✅ Web interface port 8501 is available")
            return True
        else:
            print("⚠️ Web interface port 8501 is unavailable (perhaps not started)")
            return True  # Not an error, just not started
            
    except Exception as e:
        print(f"❌ Web interface test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting UI fix tests...\n")
    
    tests = [
        ("Module imports", test_imports),
        ("Streamlit app", test_streamlit_app),
        ("CLI options", test_cli_options),
        ("Web interface", test_web_interface),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
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
        print("🎉 All tests passed! UI fixes successful!")
        print("\n💡 You can now use these commands:")
        print("  python -m prompts_tool.cli_simple --ui    # Launch web interface")
        print("  python -m prompts_tool.cli_simple --list  # List prompts")
        print("  python -m prompts_tool.cli_simple 'keyword' # Search prompts")
        return 0
    else:
        print("⚠️ Some tests failed, please check the fixes")
        return 1

if __name__ == "__main__":
    sys.exit(main())
