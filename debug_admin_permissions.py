#!/usr/bin/env python3
"""
🔍 DEBUG DEL SISTEMA DE PERMISOS ADMIN
=====================================

Debug para verificar el sistema de permisos del admin.
"""

import asyncio
import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

async def debug_permissions():
    print("🔍 DEBUG - SISTEMA DE PERMISOS ADMIN")
    print("=" * 50)
    
    try:
        from src.bot.core.diana_admin_master import DianaAdminMaster
        from src.bot.core.diana_admin_security import DianaAdminSecurity
        from unittest.mock import AsyncMock
        
        # Create mock services
        mock_services = {
            'gamification': AsyncMock(),
            'admin': AsyncMock(),
        }
        
        # Create admin system
        admin_system = DianaAdminMaster(mock_services)
        
        test_user_id = 123456789
        
        print(f"🔍 Testing user ID: {test_user_id}")
        
        # Check security system directly
        print("\n🛡️ Checking security system:")
        print(f"   User roles configured: {admin_system.security.user_roles}")
        print(f"   Available roles: {list(admin_system.security.roles.keys())}")
        
        # Check if user has role
        user_role = admin_system.security.user_roles.get(test_user_id)
        print(f"   User {test_user_id} role: {user_role}")
        
        # Create session manually
        print("\n🔐 Creating admin session...")
        session = await admin_system.security.create_admin_session(test_user_id)
        if session:
            print(f"   ✅ Session created: {session.session_id}")
            print(f"   ✅ Role: {session.role.name}")
            print(f"   ✅ Permissions: {len(session.role.permissions)} permissions")
        else:
            print(f"   ❌ Failed to create session")
            
        # Test permission check
        print("\n🔍 Testing permission checks...")
        has_admin = await admin_system.check_admin_permission(test_user_id, "admin")
        print(f"   Admin permission: {has_admin}")
        
        has_super_admin = await admin_system.check_admin_permission(test_user_id, "super_admin")
        print(f"   Super admin permission: {has_super_admin}")
        
        # Test interface creation
        print("\n🖥️ Testing interface creation...")
        try:
            text, keyboard = await admin_system.create_admin_main_interface(test_user_id)
            print(f"   ✅ Interface created successfully")
            print(f"   📝 Text length: {len(text)} characters")
            print(f"   ⌨️ Keyboard: {'Yes' if keyboard else 'No'}")
            
            # Show first part of text
            print(f"   📄 Text preview: {text[:100]}...")
            
        except Exception as e:
            print(f"   ❌ Failed to create interface: {e}")
            
    except Exception as e:
        print(f"❌ Error in debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_permissions())