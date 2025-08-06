#!/usr/bin/env python3
"""
🗡️ HANDLER ELIMINATION TEST
============================
Test that the old start handler has been completely eliminated
and Diana Master System is now the sole controller of /start.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_old_handler_elimination():
    """Test that old handler is completely eliminated."""
    print("🗡️ Testing old handler elimination...")
    
    try:
        # Try to import the old handler - should fail or be empty
        from src.bot.handlers.user.start import handle_start
        print("❌ Old handler still exists!")
        return False
    except ImportError:
        print("✅ Old handler import failed (expected)")
    except Exception as e:
        print(f"✅ Old handler eliminated: {e}")
    
    try:
        from src.bot.handlers.user.start import register_start_handler
        print("❌ Old handler registration still exists!")
        return False
    except ImportError:
        print("✅ Old handler registration eliminated")
    except Exception as e:
        print(f"✅ Old handler registration eliminated: {e}")
    
    return True

def test_diana_handler_exists():
    """Test that Diana Master System handler exists."""
    print("\n🎭 Testing Diana Master System handler...")
    
    try:
        from src.bot.core.diana_master_system import cmd_start, master_router
        print("✅ Diana Master System cmd_start handler exists")
        return True
    except ImportError as e:
        print(f"❌ Diana Master System handler missing: {e}")
        return False

def test_user_handlers_registration():
    """Test that user handlers registration is updated."""
    print("\n📝 Testing user handlers registration...")
    
    try:
        from src.bot.handlers.user import register_user_handlers
        print("✅ register_user_handlers exists")
        
        # Check the source to see if start handler is commented out
        import inspect
        source = inspect.getsource(register_user_handlers)
        if "register_start_handler(dp" not in source or "# register_start_handler" in source:
            print("✅ Old start handler registration eliminated from user handlers")
            return True
        else:
            print("❌ Old start handler still being registered")
            return False
            
    except Exception as e:
        print(f"❌ Error checking user handlers: {e}")
        return False

def test_event_publication():
    """Test that Diana Master System can publish events."""
    print("\n📡 Testing event publication capability...")
    
    try:
        from src.modules.events import UserStartedBotEvent
        print("✅ UserStartedBotEvent import works")
        
        # Create a test event
        event = UserStartedBotEvent(user_id=12345, username="test_user")
        print("✅ UserStartedBotEvent creation works")
        
        return True
    except Exception as e:
        print(f"❌ Event system error: {e}")
        return False

if __name__ == "__main__":
    print("🗡️ HANDLER ELIMINATION VALIDATION")
    print("=" * 40)
    
    tests_passed = 0
    
    if test_old_handler_elimination():
        tests_passed += 1
    
    if test_diana_handler_exists():
        tests_passed += 1
        
    if test_user_handlers_registration():
        tests_passed += 1
        
    if test_event_publication():
        tests_passed += 1
    
    print(f"\n🏆 RESULTS: {tests_passed}/4 tests passed")
    
    if tests_passed == 4:
        print("✅ OLD HANDLER COMPLETELY ELIMINATED!")
        print("🎭 DIANA MASTER SYSTEM IS NOW SUPREME!")
        print("🚀 /start command is now 100% Diana-powered!")
    else:
        print("❌ Some issues remain - check output above")
        print("🔧 Manual fixes may be required")