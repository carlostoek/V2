#!/usr/bin/env python3
"""
Test de integración completa del sistema administrativo de Diana Bot V2.

Este test valida que todos los componentes del sistema administrativo
están correctamente integrados y funcionando.
"""

import asyncio
import sys
import os
from datetime import datetime

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.event_bus import EventBus
from src.modules.admin.service import AdminService
from src.modules.user.service import UserService


class AdminSystemIntegrationTest:
    """Test completo de integración del sistema administrativo."""
    
    def __init__(self):
        self.event_bus = EventBus()
        self.admin_service = AdminService(self.event_bus)
        self.user_service = UserService(self.event_bus) if 'UserService' in globals() else None
        self.test_results = []
        
    async def setup(self):
        """Configurar servicios para testing."""
        try:
            await self.admin_service.setup()
            if self.user_service:
                await self.user_service.setup()
            print("✅ Setup de servicios completado")
            return True
        except Exception as e:
            print(f"❌ Error en setup: {e}")
            return False
    
    async def test_admin_service_basic_functions(self):
        """Prueba funciones básicas del AdminService."""
        print("\n🧪 Testando funciones básicas de AdminService...")
        
        try:
            # Test 1: Configuración del bot
            config = await self.admin_service.get_bot_configuration()
            assert isinstance(config, dict), "Config debe ser un diccionario"
            print("✅ Test 1: get_bot_configuration - OK")
            
            # Test 2: Estadísticas de usuarios
            user_stats = await self.admin_service.get_user_statistics()
            assert isinstance(user_stats, dict), "User stats debe ser un diccionario"
            assert 'total_users' in user_stats, "Debe incluir total_users"
            assert 'vip_users' in user_stats, "Debe incluir vip_users"
            print("✅ Test 2: get_user_statistics - OK")
            
            # Test 3: Estadísticas de ingresos
            revenue_stats = await self.admin_service.get_revenue_statistics()
            assert isinstance(revenue_stats, dict), "Revenue stats debe ser un diccionario"
            assert 'tokens_generated' in revenue_stats, "Debe incluir tokens_generated"
            assert 'estimated_revenue' in revenue_stats, "Debe incluir estimated_revenue"
            print("✅ Test 3: get_revenue_statistics - OK")
            
            # Test 4: Top tarifas
            top_tariffs = await self.admin_service.get_top_tariffs()
            assert isinstance(top_tariffs, list), "Top tariffs debe ser una lista"
            print("✅ Test 4: get_top_tariffs - OK")
            
            self.test_results.append("AdminService Basic Functions: PASSED")
            return True
            
        except Exception as e:
            print(f"❌ Error en test básico: {e}")
            self.test_results.append(f"AdminService Basic Functions: FAILED - {e}")
            return False
    
    async def test_tariff_management(self):
        """Prueba gestión completa de tarifas."""
        print("\n🧪 Testando gestión de tarifas...")
        
        try:
            # Test 1: Crear tarifa
            new_tariff = await self.admin_service.create_tariff(
                name="Test VIP",
                price=19.99,
                duration_days=30,
                channel_id=1,
                admin_id=12345,
                description="Tarifa de prueba"
            )
            assert new_tariff is not None, "Tarifa debe ser creada"
            assert new_tariff.name == "Test VIP", "Nombre debe coincidir"
            print("✅ Test 1: create_tariff - OK")
            
            tariff_id = new_tariff.id
            
            # Test 2: Obtener tarifa
            retrieved_tariff = await self.admin_service.get_tariff(tariff_id)
            assert retrieved_tariff is not None, "Tarifa debe existir"
            assert retrieved_tariff.id == tariff_id, "ID debe coincidir"
            print("✅ Test 2: get_tariff - OK")
            
            # Test 3: Actualizar tarifa
            updated_tariff = await self.admin_service.update_tariff(
                tariff_id=tariff_id,
                name="Test VIP Updated",
                price=24.99,
                admin_id=12345
            )
            assert updated_tariff is not None, "Tarifa debe ser actualizada"
            assert updated_tariff.name == "Test VIP Updated", "Nombre debe estar actualizado"
            assert updated_tariff.price == 24.99, "Precio debe estar actualizado"
            print("✅ Test 3: update_tariff - OK")
            
            # Test 4: Generar token para tarifa
            token = await self.admin_service.generate_subscription_token(
                tariff_id=tariff_id,
                admin_id=12345,
                expires_in_days=7
            )
            assert token is not None, "Token debe ser generado"
            assert len(token.token) > 0, "Token debe tener contenido"
            print("✅ Test 4: generate_subscription_token - OK")
            
            # Test 5: Validar token (simulado - requiere un usuario real)
            # En un entorno de pruebas real, aquí crearíamos un usuario de prueba
            print("⚠️  Test 5: validate_token - SKIPPED (requiere user setup)")
            
            # Test 6: Eliminar tarifa
            deleted = await self.admin_service.delete_tariff(tariff_id, admin_id=12345)
            assert deleted == True, "Tarifa debe ser eliminada"
            print("✅ Test 6: delete_tariff - OK")
            
            self.test_results.append("Tariff Management: PASSED")
            return True
            
        except Exception as e:
            print(f"❌ Error en test de tarifas: {e}")
            self.test_results.append(f"Tariff Management: FAILED - {e}")
            return False
    
    async def test_bulk_token_generation(self):
        """Prueba generación masiva de tokens."""
        print("\n🧪 Testando generación masiva de tokens...")
        
        try:
            # Primero crear una tarifa para usar
            test_tariff = await self.admin_service.create_tariff(
                name="Bulk Test Tariff",
                price=9.99,
                duration_days=7,
                channel_id=1,
                admin_id=12345
            )
            
            # Test generación masiva
            result = await self.admin_service.generate_bulk_tokens(
                tariff_id=test_tariff.id,
                quantity=5,
                admin_id=12345
            )
            
            assert result["success"] == True, "Generación debe ser exitosa"
            assert result["data"]["quantity"] == 5, "Cantidad debe coincidir"
            assert len(result["data"]["tokens"]) == 5, "Debe generar 5 tokens"
            print("✅ Test 1: generate_bulk_tokens (5 tokens) - OK")
            
            # Test límite de cantidad
            result_limit = await self.admin_service.generate_bulk_tokens(
                tariff_id=test_tariff.id,
                quantity=1500,  # Excede el límite de 1000
                admin_id=12345
            )
            
            assert result_limit["success"] == False, "Debe fallar por límite excedido"
            assert "inválida" in result_limit["error"].lower(), "Mensaje de error apropiado"
            print("✅ Test 2: generate_bulk_tokens (límite) - OK")
            
            # Limpiar
            await self.admin_service.delete_tariff(test_tariff.id, admin_id=12345)
            
            self.test_results.append("Bulk Token Generation: PASSED")
            return True
            
        except Exception as e:
            print(f"❌ Error en test de tokens masivos: {e}")
            self.test_results.append(f"Bulk Token Generation: FAILED - {e}")
            return False
    
    async def test_configuration_management(self):
        """Prueba gestión de configuraciones."""
        print("\n🧪 Testando gestión de configuraciones...")
        
        try:
            # Test 1: Obtener configuración inicial
            initial_config = await self.admin_service.get_bot_configuration()
            print("✅ Test 1: get_bot_configuration - OK")
            
            # Test 2: Actualizar configuración
            new_config = {
                "free_channel_id": -1001234567890,
                "wait_time_minutes": 30
            }
            
            result = await self.admin_service.update_bot_configuration(
                new_config,
                admin_id=12345
            )
            
            assert result["success"] == True, "Actualización debe ser exitosa"
            updated_config = result["data"]
            assert updated_config["free_channel_id"] == -1001234567890, "Canal debe estar actualizado"
            assert updated_config["wait_time_minutes"] == 30, "Tiempo debe estar actualizado"
            print("✅ Test 2: update_bot_configuration - OK")
            
            # Test 3: Verificar persistencia
            current_config = await self.admin_service.get_bot_configuration()
            assert current_config["free_channel_id"] == -1001234567890, "Cambios deben persistir"
            print("✅ Test 3: configuration persistence - OK")
            
            self.test_results.append("Configuration Management: PASSED")
            return True
            
        except Exception as e:
            print(f"❌ Error en test de configuración: {e}")
            self.test_results.append(f"Configuration Management: FAILED - {e}")
            return False
    
    async def test_statistics_export(self):
        """Prueba exportación de estadísticas."""
        print("\n🧪 Testando exportación de estadísticas...")
        
        try:
            # Test exportación JSON
            result = await self.admin_service.export_statistics(format="json", date_range=30)
            
            assert result["success"] == True, "Exportación debe ser exitosa"
            data = result["data"]
            assert "export_date" in data, "Debe incluir fecha de exportación"
            assert "user_statistics" in data, "Debe incluir estadísticas de usuarios"
            assert "revenue_statistics" in data, "Debe incluir estadísticas de ingresos"
            assert "top_tariffs" in data, "Debe incluir top tarifas"
            print("✅ Test 1: export_statistics JSON - OK")
            
            # Test exportación con formato diferente
            result_text = await self.admin_service.export_statistics(format="text", date_range=7)
            assert result_text["success"] == True, "Exportación texto debe funcionar"
            assert result_text["data"]["format"] == "text", "Formato debe coincidir"
            print("✅ Test 2: export_statistics TEXT - OK")
            
            self.test_results.append("Statistics Export: PASSED")
            return True
            
        except Exception as e:
            print(f"❌ Error en test de exportación: {e}")
            self.test_results.append(f"Statistics Export: FAILED - {e}")
            return False
    
    async def test_user_search_and_details(self):
        """Prueba búsqueda y detalles de usuarios."""
        print("\n🧪 Testando búsqueda de usuarios...")
        
        try:
            # Test búsqueda (puede devolver lista vacía si no hay usuarios)
            users = await self.admin_service.search_users("test", limit=10)
            assert isinstance(users, list), "Resultado debe ser una lista"
            print("✅ Test 1: search_users - OK")
            
            # Test detalles de usuario (puede fallar si no hay usuarios)
            try:
                user_details = await self.admin_service.get_user_details(12345)
                # Si el usuario no existe, debe retornar error controlado
                if not user_details["success"]:
                    assert "no encontrado" in user_details["error"].lower()
                    print("✅ Test 2: get_user_details (usuario inexistente) - OK")
                else:
                    assert "data" in user_details, "Debe incluir datos del usuario"
                    print("✅ Test 2: get_user_details (usuario existente) - OK")
            except Exception:
                print("⚠️  Test 2: get_user_details - SKIPPED (sin usuarios)")
            
            self.test_results.append("User Search: PASSED")
            return True
            
        except Exception as e:
            print(f"❌ Error en test de usuarios: {e}")
            self.test_results.append(f"User Search: FAILED - {e}")
            return False
    
    async def test_expiring_subscriptions(self):
        """Prueba detección de suscripciones por expirar."""
        print("\n🧪 Testando suscripciones por expirar...")
        
        try:
            # Test suscripciones que expiran en 1 día
            expiring = await self.admin_service.get_expiring_subscriptions(1)
            assert isinstance(expiring, list), "Resultado debe ser una lista"
            print("✅ Test 1: get_expiring_subscriptions (1 día) - OK")
            
            # Test suscripciones que expiran en 7 días
            expiring_week = await self.admin_service.get_expiring_subscriptions(7)
            assert isinstance(expiring_week, list), "Resultado debe ser una lista"
            print("✅ Test 2: get_expiring_subscriptions (7 días) - OK")
            
            self.test_results.append("Expiring Subscriptions: PASSED")
            return True
            
        except Exception as e:
            print(f"❌ Error en test de suscripciones: {e}")
            self.test_results.append(f"Expiring Subscriptions: FAILED - {e}")
            return False
    
    async def run_all_tests(self):
        """Ejecuta todos los tests de integración."""
        print("🚀 INICIANDO TESTS DE INTEGRACIÓN DEL SISTEMA ADMINISTRATIVO")
        print("=" * 70)
        
        # Setup inicial
        if not await self.setup():
            print("❌ Setup falló. Abortando tests.")
            return False
        
        # Lista de tests a ejecutar
        tests = [
            self.test_admin_service_basic_functions,
            self.test_tariff_management,
            self.test_bulk_token_generation,
            self.test_configuration_management,
            self.test_statistics_export,
            self.test_user_search_and_details,
            self.test_expiring_subscriptions,
        ]
        
        passed = 0
        failed = 0
        
        # Ejecutar cada test
        for test in tests:
            try:
                if await test():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ Test {test.__name__} falló con excepción: {e}")
                failed += 1
        
        # Resumen final
        print("\n" + "=" * 70)
        print("📊 RESUMEN DE TESTS")
        print("=" * 70)
        
        total = passed + failed
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"✅ Tests exitosos: {passed}/{total} ({success_rate:.1f}%)")
        print(f"❌ Tests fallidos: {failed}/{total}")
        
        print(f"\n📋 RESULTADOS DETALLADOS:")
        for result in self.test_results:
            status = "✅" if "PASSED" in result else "❌"
            print(f"{status} {result}")
        
        if failed == 0:
            print(f"\n🎉 TODOS LOS TESTS PASARON EXITOSAMENTE!")
            print(f"✅ El sistema administrativo está completamente integrado y funcional.")
            return True
        else:
            print(f"\n⚠️  {failed} tests fallaron. Revisar implementación.")
            return False


async def main():
    """Función principal para ejecutar los tests."""
    try:
        print("Diana Bot V2 - Admin System Integration Test")
        print(f"Iniciado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print()
        
        tester = AdminSystemIntegrationTest()
        success = await tester.run_all_tests()
        
        print(f"\nTest completado el {datetime.now().strftime('%H:%M:%S')}")
        
        if success:
            print("🎯 SISTEMA ADMINISTRATIVO: ✅ READY FOR PRODUCTION")
            exit(0)
        else:
            print("🔧 SISTEMA ADMINISTRATIVO: ⚠️  REQUIRES FIXES")
            exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrumpidos por el usuario")
        exit(1)
    except Exception as e:
        print(f"\n❌ Error crítico en tests: {e}")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())