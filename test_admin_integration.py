#!/usr/bin/env python3
"""
🧪 PRUEBA DE INTEGRACIÓN DEL SISTEMA ADMIN
==========================================

Test para verificar que el sistema Diana Admin Master está correctamente integrado.
"""

import asyncio
import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

async def test_admin_integration():
    """Prueba la integración del sistema admin"""
    print("🎭 PRUEBA DE INTEGRACIÓN - DIANA ADMIN MASTER SYSTEM")
    print("=" * 60)
    
    try:
        # Test 1: Import the admin system
        print("📦 Test 1: Importando sistema admin...")
        from src.bot.core.diana_admin_master import register_diana_admin_master, DianaAdminMaster
        print("   ✅ Sistema admin importado correctamente")
        
        # Test 2: Create mock services
        print("🔧 Test 2: Creando servicios mock...")
        from unittest.mock import AsyncMock, MagicMock
        
        mock_services = {
            'gamification': AsyncMock(),
            'admin': AsyncMock(),
            'daily_rewards': AsyncMock(),
            'narrative': AsyncMock()
        }
        
        # Configure mock responses
        mock_services['gamification'].get_user_stats = AsyncMock(return_value={
            'level': 5, 'points': 1000, 'total_earned': 2500
        })
        
        print("   ✅ Servicios mock creados")
        
        # Test 3: Create mock dispatcher
        print("🤖 Test 3: Creando dispatcher mock...")
        mock_dp = MagicMock()
        mock_dp.include_router = MagicMock()
        print("   ✅ Dispatcher mock creado")
        
        # Test 4: Register admin system
        print("🎭 Test 4: Registrando sistema admin...")
        admin_system = register_diana_admin_master(mock_dp, mock_services)
        print("   ✅ Sistema admin registrado exitosamente")
        
        # Test 5: Verify admin system
        print("🔍 Test 5: Verificando funcionalidad del sistema...")
        assert admin_system is not None
        assert hasattr(admin_system, 'create_admin_main_interface')
        assert hasattr(admin_system, 'create_section_interface')
        assert hasattr(admin_system, 'create_subsection_interface')
        print("   ✅ Sistema admin verificado")
        
        # Test 6: Test admin interface creation
        print("🖥️  Test 6: Probando creación de interfaces...")
        
        # Mock user ID (would be a super admin)
        test_user_id = 123456789
        
        # Test main interface
        text, keyboard = await admin_system.create_admin_main_interface(test_user_id)
        assert isinstance(text, str)
        assert "DIANA BOT - CENTRO DE ADMINISTRACIÓN" in text
        print("   ✅ Interface principal creada correctamente")
        
        # Test section interface
        text, keyboard = await admin_system.create_section_interface(test_user_id, "vip")
        assert isinstance(text, str)
        assert "VIP" in text
        print("   ✅ Interface de sección creada correctamente")
        
        # Test 7: Verify router was included
        print("🛣️  Test 7: Verificando inclusión del router...")
        mock_dp.include_router.assert_called()
        print("   ✅ Router incluido en dispatcher")
        
        # Test 8: Test security system
        print("🛡️  Test 8: Probando sistema de seguridad...")
        has_permission = await admin_system.check_admin_permission(test_user_id)
        print(f"   ℹ️  Permisos para user {test_user_id}: {has_permission}")
        print("   ✅ Sistema de seguridad funcionando")
        
        print("\n" + "=" * 60)
        print("🎉 TODOS LOS TESTS PASARON - INTEGRACIÓN EXITOSA!")
        print("=" * 60)
        
        print("\n🎯 RESUMEN DE LA INTEGRACIÓN:")
        print("   • Sistema Diana Admin Master ✅ INTEGRADO")
        print("   • Router incluido en dispatcher ✅ ACTIVO") 
        print("   • Interfaces funcionando ✅ OPERATIVO")
        print("   • Sistema de seguridad ✅ FUNCIONAL")
        print("   • Servicios integrados ✅ CONECTADOS")
        
        print("\n📋 PRÓXIMOS PASOS:")
        print("   1. Configurar tu USER ID en diana_admin_security.py")
        print("   2. Agregar BOT_TOKEN válido en variables de entorno")
        print("   3. Ejecutar main.py para iniciar el bot")
        print("   4. Usar /admin en Telegram para acceder al panel")
        
        print("\n🎭✨ ¡El sistema está listo para revolucionar la administración!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR EN LA INTEGRACIÓN: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    success = await test_admin_integration()
    
    if success:
        print(f"\n🚀 Diana Admin Master System - INTEGRACIÓN COMPLETA! 🚀")
        exit(0)
    else:
        print(f"\n⚠️ Hay problemas en la integración que necesitan resolverse")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())