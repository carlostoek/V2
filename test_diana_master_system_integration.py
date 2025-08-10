#!/usr/bin/env python3
"""
🎭 DIANA MASTER SYSTEM - INTEGRATION TEST
========================================

Test para validar la integración completa del Diana Master System 
refactorizado con funcionalidades de conversión FREE→VIP y upsell VIP→Premium.
"""

import asyncio
import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

async def test_diana_master_system_integration():
    """Prueba la integración completa del sistema refactorizado"""
    print("🎭 PRUEBA DEL SISTEMA DIANA MASTER REFACTORIZADO")
    print("=" * 70)
    
    success_count = 0
    total_tests = 0
    
    try:
        # Test 1: Import del sistema refactorizado
        print("📦 Test 1: Importando Diana Master System refactorizado...")
        total_tests += 1
        
        from src.bot.core.diana_master_system import (
            DianaMasterInterface, AdaptiveContextEngine, UserMoodState,
            register_diana_master_system, CONTENT_PACKAGES
        )
        
        print("   ✅ Sistema refactorizado importado correctamente")
        success_count += 1
        
        # Test 2: Verificar nuevos mood states
        print("🎭 Test 2: Verificando mood states de conversión...")
        total_tests += 1
        
        assert hasattr(UserMoodState, 'FREE_CONVERSION'), "Mood FREE_CONVERSION no encontrado"
        assert hasattr(UserMoodState, 'VIP_UPSELL'), "Mood VIP_UPSELL no encontrado"
        assert UserMoodState.FREE_CONVERSION.value == "free_conversion"
        assert UserMoodState.VIP_UPSELL.value == "vip_upsell"
        
        print("   ✅ Mood states de conversión verificados")
        success_count += 1
        
        # Test 3: Verificar paquetes de contenido
        print("🎁 Test 3: Verificando paquetes de contenido...")
        total_tests += 1
        
        required_packages = ["intimate_conversations", "exclusive_photos", "custom_videos", "vip_experiences"]
        for package in required_packages:
            assert package in CONTENT_PACKAGES, f"Paquete {package} no encontrado"
            package_data = CONTENT_PACKAGES[package]
            assert 'title' in package_data, f"Paquete {package} sin título"
            assert 'price' in package_data, f"Paquete {package} sin precio"
            assert 'diana_seduction' in package_data, f"Paquete {package} sin seducción de Diana"
        
        print(f"   ✅ {len(CONTENT_PACKAGES)} paquetes de contenido verificados")
        success_count += 1
        
        # Test 4: Crear servicios mock
        print("🔧 Test 4: Creando servicios mock...")
        total_tests += 1
        
        from unittest.mock import AsyncMock, MagicMock
        
        mock_services = {
            'gamification': AsyncMock(),
            'admin': AsyncMock(),
            'narrative': AsyncMock(),
            'event_bus': AsyncMock()
        }
        
        # Configurar servicios mock para FREE user
        mock_services['gamification'].get_user_stats = AsyncMock(return_value={
            'level': 6, 'points': 1200, 'achievements_count': 10,
            'streak': 15, 'points_today': 85, 'total_interactions': 320, 'active_missions': 3
        })
        
        mock_services['admin'].is_vip_user = AsyncMock(return_value=False)  # FREE user
        mock_services['admin'].send_admin_notification = AsyncMock()
        mock_services['narrative'].get_user_narrative_progress = AsyncMock(return_value={'progress': 45})
        
        print("   ✅ Servicios mock configurados")
        success_count += 1
        
        # Test 5: Crear sistema Diana Master
        print("🧠 Test 5: Creando Diana Master Interface...")
        total_tests += 1
        
        master_interface = DianaMasterInterface(mock_services)
        assert master_interface is not None
        assert hasattr(master_interface, 'create_adaptive_interface')
        assert hasattr(master_interface, 'context_engine')
        
        print("   ✅ Diana Master Interface creado correctamente")
        success_count += 1
        
        # Test 6: Probar detección de mood FREE_CONVERSION
        print("🌙 Test 6: Probando detección de mood FREE_CONVERSION...")
        total_tests += 1
        
        test_user_id = 123456789
        
        # Simular interacciones para activar FREE_CONVERSION mood
        from datetime import datetime, timedelta
        now = datetime.now()
        master_interface.context_engine.interaction_patterns[test_user_id] = [
            ('start', now - timedelta(days=1)), 
            ('shop', now - timedelta(days=2)), 
            ('story', now - timedelta(days=1)), 
            ('trivia', now - timedelta(hours=12)), 
            ('daily', now - timedelta(hours=6)),
            ('profile', now - timedelta(hours=2))  # 6+ interactions = high engagement
        ]
        
        context = await master_interface.context_engine.analyze_user_context(test_user_id)
        
        assert context.current_mood == UserMoodState.FREE_CONVERSION, f"Expected FREE_CONVERSION, got {context.current_mood}"
        
        print("   ✅ Mood FREE_CONVERSION detectado correctamente")
        success_count += 1
        
        # Test 7: Probar interfaz adaptativa para FREE_CONVERSION
        print("🎭 Test 7: Probando interfaz adaptativa FREE_CONVERSION...")
        total_tests += 1
        
        text, keyboard = await master_interface.create_adaptive_interface(test_user_id)
        
        assert isinstance(text, str)
        assert "Diana te reconoce" in text or "Diana se acerca" in text or "Diana te susurra" in text
        assert "Alma Libre" in text  # FREE user indicator
        assert keyboard is not None
        assert len(keyboard.inline_keyboard) > 0
        
        # Verificar botones específicos para FREE_CONVERSION
        button_texts = []
        for row in keyboard.inline_keyboard:
            for button in row:
                button_texts.append(button.text)
        
        assert "💎 El Diván VIP" in button_texts, "Botón VIP no encontrado en FREE_CONVERSION"
        assert "🎁 Tesoros Especiales" in button_texts, "Botón paquetes no encontrado en FREE_CONVERSION"
        
        print("   ✅ Interfaz FREE_CONVERSION creada correctamente")
        success_count += 1
        
        # Test 8: Probar usuario VIP con mood VIP_UPSELL
        print("👑 Test 8: Probando detección VIP_UPSELL...")
        total_tests += 1
        
        # Cambiar mock para usuario VIP con high engagement
        mock_services['admin'].is_vip_user = AsyncMock(return_value=True)
        mock_services['gamification'].get_user_stats = AsyncMock(return_value={
            'level': 8, 'points': 2500, 'achievements_count': 20,  # High stats
            'streak': 25, 'active_missions': 5
        })
        
        vip_interface = DianaMasterInterface(mock_services)
        vip_interface.context_engine.interaction_patterns[test_user_id] = [
            ('vip_chat', now - timedelta(hours=1)), 
            ('premium_content', now - timedelta(hours=3)), 
            ('exclusive', now - timedelta(minutes=30))
        ]
        
        vip_context = await vip_interface.context_engine.analyze_user_context(test_user_id)
        vip_text, vip_keyboard = await vip_interface.create_adaptive_interface(test_user_id)
        
        assert vip_context.current_mood == UserMoodState.VIP_UPSELL, f"Expected VIP_UPSELL, got {vip_context.current_mood}"
        assert "Elegido del Círculo" in vip_text, "VIP status not shown"
        
        # Verificar botones VIP específicos
        vip_button_texts = []
        for row in vip_keyboard.inline_keyboard:
            for button in row:
                vip_button_texts.append(button.text)
        
        assert "💬 Chat Privado" in vip_button_texts, "Botón Chat Privado no encontrado"
        assert "🌟 Premium Plus" in vip_button_texts, "Botón Premium Plus no encontrado"
        
        print("   ✅ Interfaz VIP_UPSELL verificada")
        success_count += 1
        
        # Test 9: Probar sistema de notificaciones
        print("📱 Test 9: Probando sistema de notificaciones...")
        total_tests += 1
        
        from src.bot.core.diana_master_system import send_admin_notification
        
        # Simular interés de usuario
        await send_admin_notification(
            master_interface, 
            test_user_id, 
            "vip_channel", 
            context
        )
        
        # Verificar que se llamó send_admin_notification
        mock_services['admin'].send_admin_notification.assert_called()
        call_args = mock_services['admin'].send_admin_notification.call_args[0][0]
        assert "INTERÉS DE USUARIO" in call_args
        assert f"User ID: {test_user_id}" in call_args
        assert "INTERÉS EN DIVÁN VIP" in call_args
        
        print("   ✅ Sistema de notificaciones verificado")
        success_count += 1
        
        # Test 10: Probar registro del sistema
        print("🛣️ Test 10: Probando registro del router...")
        total_tests += 1
        
        mock_dp = MagicMock()
        mock_dp.include_router = MagicMock()
        
        registered_system = register_diana_master_system(mock_dp, mock_services)
        
        assert registered_system is not None
        mock_dp.include_router.assert_called()
        
        print("   ✅ Router registrado correctamente")
        success_count += 1
        
        print("\n" + "=" * 70)
        print("🎉 VALIDACIÓN COMPLETA DEL SISTEMA REFACTORIZADO!")
        print("=" * 70)
        
        print(f"\n📊 RESULTADOS:")
        print(f"   ✅ Tests exitosos: {success_count}/{total_tests}")
        print(f"   📈 Tasa de éxito: {(success_count/total_tests)*100:.1f}%")
        
        print(f"\n🎭 CARACTERÍSTICAS REFACTORIZADAS VALIDADAS:")
        print(f"   • Mood states FREE_CONVERSION y VIP_UPSELL ✅")
        print(f"   • Detección automática VIP/FREE ✅") 
        print(f"   • Templates dinámicos con Diana & Lucien ✅")
        print(f"   • {len(CONTENT_PACKAGES)} paquetes de contenido integrados ✅")
        print(f"   • Sistema de notificaciones admin ✅")
        print(f"   • Keyboards adaptativos por mood ✅")
        print(f"   • Integración completa en DMS ✅")
        
        print(f"\n🌹 VENTAJAS DE LA REFACTORIZACIÓN:")
        print(f"   • Un solo sistema dinámico vs dos sistemas separados")
        print(f"   • Context engine automático para FREE/VIP detection") 
        print(f"   • Templates adaptativos en lugar de interfaces fijas")
        print(f"   • Integración nativa con mood detection existente")
        print(f"   • Mantenimiento simplificado y escalabilidad mejorada")
        
        if success_count == total_tests:
            print(f"\n🎉 REFACTORIZACIÓN PERFECTA - DIANA MASTER SYSTEM UNIFIED! 🎉")
            return True
        else:
            print(f"\n⚠️ Algunos tests fallaron - Revisar antes de producción")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR EN VALIDACIÓN: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run comprehensive integration validation"""
    print("🎭 DIANA MASTER SYSTEM - VALIDACIÓN DE REFACTORIZACIÓN")
    print("=" * 70)
    
    success = await test_diana_master_system_integration()
    
    if success:
        print(f"\n🎭🌹 Diana Master System Refactorizado - ¡Perfección Técnica Lograda! 🎭🌹")
        print("✨ Un solo sistema dinámico que maneja conversión y upsell automáticamente! ✨")
        print("🚀 Ready to convert FREE users and upsell VIPs with intelligent templates!")
    else:
        print(f"\n⚠️ Sistema necesita ajustes antes de conquistar corazones")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())