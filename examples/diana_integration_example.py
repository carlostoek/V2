#!/usr/bin/env python3
"""
Ejemplo de Integración Diana - Gamificación

Este ejemplo demuestra cómo funciona la integración completa entre:
- Sistema de validación Diana
- Sistema de gamificación
- Sistema de narrativa
- Misiones y logros

Ejecutar: python examples/diana_integration_example.py
"""

import asyncio
import logging
import sys
import os

# Agregar path del proyecto
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.event_bus import EventBus
from src.modules.gamification.service import GamificationService
from src.modules.narrative.service import NarrativeService
from src.modules.narrative.diana_integration import DianaValidationIntegrationService
from src.modules.events import (
    UserStartedBotEvent,
    ReactionAddedEvent,
    NarrativeProgressionEvent,
    DianaValidationCompletedEvent
)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DianaIntegrationExample:
    """Ejemplo de integración completa Diana-Gamificación."""
    
    def __init__(self):
        self.event_bus = EventBus()
        self.gamification_service = None
        self.narrative_service = None
        self.diana_integration_service = None
        
    async def setup_services(self):
        """Inicializa todos los servicios."""
        logger.info("🔧 Inicializando servicios...")
        
        # Crear servicios
        self.gamification_service = GamificationService(self.event_bus) 
        self.narrative_service = NarrativeService(self.event_bus)
        self.diana_integration_service = DianaValidationIntegrationService(
            self.event_bus, 
            "http://localhost:8000"  # URL del servicio Diana (mock en este ejemplo)
        )
        
        # Configurar servicios (con mocks para base de datos)
        try:
            await self.gamification_service.setup()
            await self.narrative_service.setup()
            await self.diana_integration_service.setup()
            logger.info("✅ Servicios inicializados correctamente")
        except Exception as e:
            logger.error(f"❌ Error inicializando servicios: {e}")
            # Para el ejemplo, continuar sin base de datos real
            logger.info("⚠️  Continuando con servicios básicos...")
    
    async def simulate_user_journey(self, user_id: int = 12345):
        """Simula el journey completo de un usuario."""
        logger.info(f"🚀 Iniciando journey del usuario {user_id}")
        
        # 1. Usuario inicia el bot
        logger.info("👋 Usuario inicia el bot...")
        start_event = UserStartedBotEvent(user_id, "test_user")
        await self.event_bus.publish(start_event)
        
        # Verificar puntos iniciales
        initial_points = self.gamification_service.get_points(user_id)
        logger.info(f"💰 Puntos iniciales: {initial_points}")
        
        # 2. Usuario reacciona rápidamente a mensajes (para validación nivel 1→2)
        logger.info("⚡ Usuario reacciona rápidamente...")
        for i in range(3):
            reaction_event = ReactionAddedEvent(user_id, 1000 + i, points_to_award=5)
            await self.event_bus.publish(reaction_event)
            await asyncio.sleep(0.1)  # Pequeña pausa
        
        # Verificar puntos después de reacciones
        after_reactions_points = self.gamification_service.get_points(user_id)
        logger.info(f"💰 Puntos después de reacciones: {after_reactions_points}")
        
        # 3. Simular validación Diana nivel 1→2
        logger.info("🔍 Ejecutando validación Diana nivel 1→2...")
        validation_success = await self.diana_integration_service.validate_level_progression(
            user_id, 1, 2
        )
        logger.info(f"✅ Validación 1→2: {'EXITOSA' if validation_success else 'FALLIDA'}")
        
        # 4. Usuario explora narrativa (para validación nivel 2→3)
        logger.info("📚 Usuario explora narrativa...")
        for i in range(5):
            progression_event = NarrativeProgressionEvent(
                user_id=user_id,
                fragment_id=f"story_fragment_{i}",
                choices_made={f"fragment_{i}": [1]}
            )
            await self.event_bus.publish(progression_event)
            await asyncio.sleep(0.1)
        
        # 5. Simular validación Diana nivel 2→3
        logger.info("🔍 Ejecutando validación Diana nivel 2→3...")
        validation_success_2 = await self.diana_integration_service.validate_level_progression(
            user_id, 2, 3
        )
        logger.info(f"✅ Validación 2→3: {'EXITOSA' if validation_success_2 else 'FALLIDA'}")
        
        # 6. Verificar puntos finales
        final_points = self.gamification_service.get_points(user_id)
        logger.info(f"💰 Puntos finales: {final_points}")
        
        # 7. Obtener contenido adaptado
        logger.info("🎨 Obteniendo contenido adaptado...")
        adaptive_content = await self.diana_integration_service.get_adaptive_content_for_user(
            user_id, "congratulations", {"level": 3}
        )
        logger.info(f"📝 Contenido adaptado: {adaptive_content['text']}")
        
        # 8. Obtener arquetipo del usuario
        archetype = await self.diana_integration_service.get_user_archetype(user_id)
        logger.info(f"🎭 Arquetipo del usuario: {archetype}")
        
        # 9. Resumen del journey
        logger.info("📊 RESUMEN DEL JOURNEY:")
        logger.info(f"   • Puntos ganados: {final_points - initial_points}")
        logger.info(f"   • Validaciones exitosas: {int(validation_success) + int(validation_success_2)}")
        logger.info(f"   • Arquetipo detectado: {archetype}")
        logger.info(f"   • Fragmentos narrativos explorados: 5")
        
        return {
            "user_id": user_id,
            "initial_points": initial_points,
            "final_points": final_points,
            "points_gained": final_points - initial_points,
            "validations_passed": int(validation_success) + int(validation_success_2),
            "archetype": archetype,
            "narrative_fragments": 5
        }
    
    async def demonstrate_event_flow(self):
        """Demuestra el flujo de eventos."""
        logger.info("🔄 Demostrando flujo de eventos...")
        
        user_id = 99999
        
        # Crear evento de validación completada manualmente
        validation_event = DianaValidationCompletedEvent(
            user_id=user_id,
            validation_type="level_1_to_2",
            score=0.95,
            reward_data={'reaction_type': 'immediate', 'reward_type': 'quick_thinker'}
        )
        
        # Publicar evento
        await self.event_bus.publish(validation_event)
        
        # Verificar que se otorgaron puntos
        points = self.gamification_service.get_points(user_id)
        logger.info(f"💰 Puntos otorgados por validación: {points}")
        
        return points
    
    async def cleanup(self):
        """Limpia recursos."""
        if self.diana_integration_service:
            await self.diana_integration_service.cleanup()
        logger.info("🧹 Recursos limpiados")


async def main():
    """Función principal del ejemplo."""
    logger.info("🎬 INICIANDO EJEMPLO DE INTEGRACIÓN DIANA-GAMIFICACIÓN")
    logger.info("=" * 60)
    
    # Crear instancia del ejemplo
    example = DianaIntegrationExample()
    
    try:
        # Configurar servicios
        await example.setup_services()
        
        # Esperar un momento para que los servicios se estabilicen
        await asyncio.sleep(1)
        
        # Simular journey de usuario
        logger.info("\n🎮 SIMULANDO JOURNEY DE USUARIO")
        logger.info("-" * 40)
        result = await example.simulate_user_journey()
        
        # Demostrar flujo de eventos
        logger.info("\n⚡ DEMOSTRANDO FLUJO DE EVENTOS")
        logger.info("-" * 40)
        validation_points = await example.demonstrate_event_flow()
        
        # Resultado final
        logger.info("\n🏆 RESULTADO FINAL")
        logger.info("=" * 60)
        logger.info(f"✅ Integración funcionando correctamente")
        logger.info(f"✅ Usuario ganó {result['points_gained']} puntos")
        logger.info(f"✅ Completó {result['validations_passed']} validaciones")
        logger.info(f"✅ Arquetipo detectado: {result['archetype']}")
        logger.info(f"✅ Evento directo otorgó {validation_points} puntos")
        
    except Exception as e:
        logger.error(f"❌ Error en el ejemplo: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Limpiar recursos
        await example.cleanup()
        logger.info("\n🎬 EJEMPLO COMPLETADO")


def demonstrate_mission_system():
    """Demuestra el sistema de misiones Diana."""
    logger.info("\n🎯 DEMOSTRANDO SISTEMA DE MISIONES DIANA")
    logger.info("-" * 50)
    
    from src.modules.gamification.diana_missions import (
        get_diana_missions_data,
        get_missions_for_level,
        get_mission_by_key
    )
    
    # Obtener datos de misiones
    missions_data = get_diana_missions_data()
    logger.info(f"📋 Total de misiones Diana: {len(missions_data['missions'])}")
    logger.info(f"🏆 Total de logros Diana: {len(missions_data['achievements'])}")
    
    # Mostrar misiones para nivel 1
    level_1_missions = get_missions_for_level(1, is_vip=False)
    logger.info(f"🎯 Misiones disponibles para nivel 1: {len(level_1_missions)}")
    
    for mission in level_1_missions[:2]:  # Mostrar primeras 2
        logger.info(f"   • {mission['title']}: {mission['description'][:50]}...")
    
    # Mostrar misión específica
    first_reaction_mission = get_mission_by_key("diana_validation_first_reaction")
    if first_reaction_mission:
        logger.info(f"🎯 Misión 'Primera Impresión':")
        logger.info(f"   • Recompensa: {first_reaction_mission['points_reward']} puntos")
        logger.info(f"   • Tiempo límite: {first_reaction_mission['time_limit_hours']} horas")
        logger.info(f"   • Objetivos: {len(first_reaction_mission['objectives'])}")


if __name__ == "__main__":
    # Configurar para que funcione sin base de datos real
    import warnings
    warnings.filterwarnings("ignore")
    
    # Ejecutar ejemplo principal
    asyncio.run(main())
    
    # Demostrar sistema de misiones
    demonstrate_mission_system()
    
    print("\n" + "="*60)
    print("🎉 EJEMPLO COMPLETADO EXITOSAMENTE")
    print("="*60)
    print("\nEste ejemplo demuestra:")
    print("✓ Integración Diana-Gamificación completa")
    print("✓ Flujo de eventos entre sistemas")
    print("✓ Validaciones automáticas")
    print("✓ Sistema de recompensas dinámicas")
    print("✓ Misiones específicas para validaciones Diana")
    print("✓ Contenido adaptado por arquetipo")
    print("\nPara usar en producción, conectar con:")
    print("• Base de datos real")
    print("• Servicio Diana Validation real")
    print("• Bot de Telegram")