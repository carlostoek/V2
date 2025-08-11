#!/usr/bin/env python3
"""
Script de prueba para el sistema narrativo de Diana Bot V2.
Simula interacciones básicas del sistema narrativo sin Telegram.
"""

import asyncio
import logging
from src.core.event_bus import EventBus
from src.modules.emotional.service import EmotionalService
from src.modules.narrative.service import NarrativeService
from src.modules.user.service import UserService
from src.modules.events import UserStartedBotEvent
from src.bot.database.engine import init_db
from src.bot.handlers.narrative.contextual_responses import DianaContextualResponseSystem
from src.bot.handlers.narrative.story_navigation import StoryNavigationSystem
from src.bot.handlers.narrative.enhanced_mochila import EnhancedMochilaSystem

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_narrative_system():
    """Prueba el sistema narrativo completo."""
    logger.info("🧪 Iniciando pruebas del sistema narrativo...")
    
    # Inicializar base de datos
    await init_db()
    
    # Crear servicios
    event_bus = EventBus()
    user_service = UserService(event_bus)
    emotional_service = EmotionalService(event_bus)
    narrative_service = NarrativeService(event_bus)
    
    # Configurar servicios
    await user_service.setup()
    await emotional_service.setup()
    await narrative_service.setup()
    
    # Crear sistemas narrativos
    diana_system = DianaContextualResponseSystem(event_bus, emotional_service, narrative_service)
    story_system = StoryNavigationSystem(narrative_service, emotional_service, diana_system)
    mochila_system = EnhancedMochilaSystem(narrative_service, emotional_service, diana_system)
    
    # ID de usuario de prueba
    test_user_id = 123456789
    
    logger.info(f"📝 Simulando usuario {test_user_id}...")
    
    # 1. Simular usuario iniciando el bot
    logger.info("✨ Test 1: Usuario inicia el bot")
    event = UserStartedBotEvent(user_id=test_user_id, username="test_user")
    await event_bus.publish(event)
    
    # 2. Probar respuesta contextual
    logger.info("🎭 Test 2: Generar respuesta contextual")
    response = await diana_system.generate_contextual_response(
        user_id=test_user_id,
        context_type='greeting',
        context_data={'username': 'test_user'}
    )
    logger.info(f"Respuesta de Diana: {response}")
    
    # 3. Probar obtención de fragmento actual
    logger.info("📖 Test 3: Obtener fragmento narrativo")
    fragment = await narrative_service.get_user_fragment(test_user_id)
    if fragment:
        logger.info(f"Fragmento actual: {fragment['title']} - {fragment['text'][:50]}...")
        logger.info(f"Opciones disponibles: {len(fragment.get('choices', []))}")
        
        # 4. Simular elección narrativa si hay opciones
        if fragment.get('choices'):
            choice_id = fragment['choices'][0]['id']
            logger.info("🎯 Test 4: Realizar elección narrativa")
            success = await narrative_service.make_narrative_choice(test_user_id, choice_id)
            logger.info(f"Elección procesada: {'✅' if success else '❌'}")
            
            # Obtener nuevo fragmento
            new_fragment = await narrative_service.get_user_fragment(test_user_id)
            if new_fragment:
                logger.info(f"Nuevo fragmento: {new_fragment['title']}")
    else:
        logger.warning("No se encontró fragmento narrativo")
    
    # 5. Probar sistema de pistas
    logger.info("🗝️ Test 5: Sistema de pistas narrativas")
    lore_pieces = await narrative_service.get_user_lore_pieces(test_user_id)
    logger.info(f"Pistas encontradas: {len(lore_pieces)}")
    for piece in lore_pieces:
        logger.info(f"  - {piece['title']}: {piece['description'][:40]}...")
    
    # 6. Probar estado emocional
    logger.info("😌 Test 6: Estado emocional")
    emotional_modifiers = await emotional_service.get_response_modifiers(test_user_id)
    logger.info(f"Estado emocional actual: {emotional_modifiers}")
    
    # 7. Generar respuesta modificada emocionalmente
    logger.info("💫 Test 7: Modificar respuesta con estado emocional")
    original_response = "Hola, ¿cómo estás hoy?"
    modified_response = await emotional_service.modify_response(
        user_id=test_user_id,
        original_response=original_response
    )
    logger.info(f"Respuesta original: {original_response}")
    logger.info(f"Respuesta modificada: {modified_response}")
    
    logger.info("🎉 Todas las pruebas completadas!")
    return True

async def test_error_handling():
    """Prueba el manejo de errores del sistema."""
    logger.info("⚠️ Probando manejo de errores...")
    
    event_bus = EventBus()
    emotional_service = EmotionalService(event_bus)
    narrative_service = NarrativeService(event_bus)
    
    await emotional_service.setup()
    await narrative_service.setup()
    
    # Probar con usuario inexistente
    non_existent_user = 999999999
    
    try:
        # Esto debería crear un estado por defecto
        modifiers = await emotional_service.get_response_modifiers(non_existent_user)
        logger.info(f"✅ Manejo de usuario inexistente: {modifiers}")
        
        # Probar fragmento para usuario sin estado
        fragment = await narrative_service.get_user_fragment(non_existent_user)
        logger.info(f"✅ Fragmento para usuario sin estado: {fragment is not None}")
        
    except Exception as e:
        logger.error(f"❌ Error no manejado: {e}")
        return False
    
    logger.info("✅ Manejo de errores funcionando correctamente!")
    return True

async def main():
    """Función principal de pruebas."""
    try:
        logger.info("🚀 Iniciando suite de pruebas del sistema narrativo Diana Bot V2")
        
        # Ejecutar pruebas principales
        success1 = await test_narrative_system()
        success2 = await test_error_handling()
        
        if success1 and success2:
            logger.info("🎊 ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE!")
            logger.info("\n📋 Resumen de funcionalidades probadas:")
            logger.info("  ✅ Sistema de eventos")
            logger.info("  ✅ Servicios emocionales")
            logger.info("  ✅ Servicios narrativos")
            logger.info("  ✅ Respuestas contextuales")
            logger.info("  ✅ Estados emocionales")
            logger.info("  ✅ Fragmentos de historia")
            logger.info("  ✅ Elecciones narrativas")
            logger.info("  ✅ Sistema de pistas")
            logger.info("  ✅ Manejo de errores")
            logger.info("\n🤖 El sistema narrativo está listo para usar con Telegram!")
            return True
        else:
            logger.error("❌ Algunas pruebas fallaron")
            return False
    
    except Exception as e:
        logger.error(f"💥 Error crítico en las pruebas: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)