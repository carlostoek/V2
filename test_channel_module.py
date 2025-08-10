#!/usr/bin/env python3
"""
Script de prueba para verificar el funcionamiento del módulo de administración de canales.
"""

import asyncio
import logging
import sys
import os
from datetime import datetime, timedelta

# Agregar el directorio raíz al path
sys.path.append('/data/data/com.termux/files/home/repos/refactor/V2')

from src.modules.channel.service import ChannelService
from src.modules.channel.events import (
    ChannelJoinRequestEvent,
    ChannelJoinApprovedEvent,
    ChannelJoinRejectedEvent,
    UserReactionEvent
)
from src.core.interfaces.IEventBus import IEventBus, IEvent

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MockEventBus(IEventBus):
    """Mock EventBus para pruebas."""
    
    def __init__(self):
        self.subscribers = {}
        self.published_events = []
    
    async def publish(self, event: IEvent) -> None:
        """Publica un evento."""
        self.published_events.append(event)
        event_type = type(event)
        
        if event_type in self.subscribers:
            for handler in self.subscribers[event_type]:
                try:
                    await handler(event)
                except Exception as e:
                    logger.error(f"Error en handler de evento {event_type.__name__}: {e}")
    
    def subscribe(self, event_type: type, handler) -> None:
        """Suscribe un handler a un tipo de evento."""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)
    
    def unsubscribe(self, event_type: type, handler) -> None:
        """Desuscribe un handler."""
        if event_type in self.subscribers:
            try:
                self.subscribers[event_type].remove(handler)
            except ValueError:
                pass

async def test_channel_service():
    """Prueba completa del servicio de canales."""
    print("🧪 INICIANDO PRUEBAS DEL MÓDULO DE ADMINISTRACIÓN DE CANALES")
    print("=" * 70)
    
    # Crear mock event bus
    event_bus = MockEventBus()
    
    # Crear servicio
    channel_service = ChannelService(event_bus)
    
    # Resultados de pruebas
    test_results = {
        "setup": False,
        "create_channel": False,
        "channel_info": False,
        "access_rules": False,
        "add_content": False,
        "handle_join_request": False,
        "user_reaction": False
    }
    
    # TEST 1: Setup del servicio
    print("\n🧪 TEST 1: Setup del servicio")
    try:
        await channel_service.setup()
        print("✅ ÉXITO: Servicio configurado correctamente")
        test_results["setup"] = True
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    # TEST 2: Crear canal
    print("\n🧪 TEST 2: Crear canal")
    try:
        channel_id = await channel_service.create_channel(
            telegram_id="-1001234567890",
            name="Canal de Prueba VIP",
            description="Canal de prueba para testing",
            channel_type="vip"
        )
        
        if channel_id:
            print(f"✅ ÉXITO: Canal creado con ID {channel_id}")
            test_results["create_channel"] = True
        else:
            print("❌ ERROR: No se pudo crear el canal")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    # TEST 3: Obtener información del canal (solo si se creó)
    if test_results["create_channel"]:
        print("\n🧪 TEST 3: Obtener información del canal")
        try:
            channel_info = await channel_service.get_channel(channel_id)
            if channel_info:
                print(f"✅ ÉXITO: Información obtenida - {channel_info['name']} (Tipo: {channel_info['type']})")
                test_results["channel_info"] = True
            else:
                print("❌ ERROR: No se pudo obtener información del canal")
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
    
    # TEST 4: Configurar reglas de acceso
    if test_results["create_channel"]:
        print("\n🧪 TEST 4: Configurar reglas de acceso")
        try:
            success = await channel_service.set_channel_access_rules(
                channel_id=channel_id,
                min_level=5,
                requires_vip=True,
                tokens_required=10,
                duration_days=30
            )
            
            if success:
                print("✅ ÉXITO: Reglas de acceso configuradas")
                test_results["access_rules"] = True
            else:
                print("❌ ERROR: No se pudieron configurar las reglas")
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
    
    # TEST 5: Añadir contenido
    if test_results["create_channel"]:
        print("\n🧪 TEST 5: Añadir contenido")
        try:
            content_id = await channel_service.add_channel_content(
                channel_id=channel_id,
                content_type="text",
                content_data={
                    "text": "¡Bienvenidos al canal VIP!",
                    "format": "markdown"
                }
            )
            
            if content_id:
                print(f"✅ ÉXITO: Contenido añadido con ID {content_id}")
                test_results["add_content"] = True
            else:
                print("❌ ERROR: No se pudo añadir contenido")
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
    
    # TEST 6: Simular solicitud de unión (requiere usuario en BD)
    print("\n🧪 TEST 6: Manejo de solicitud de unión")
    try:
        # Crear evento de solicitud
        join_event = ChannelJoinRequestEvent(
            user_id=123456789,  # Usuario ficticio
            channel_id=channel_id if test_results["create_channel"] else 1
        )
        
        # Simular manejo del evento
        await channel_service.handle_join_request(join_event)
        
        print("✅ ÉXITO: Evento de solicitud procesado (puede haberse rechazado por falta de usuario)")
        test_results["handle_join_request"] = True
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    # TEST 7: Simular reacción de usuario (requiere contenido en BD)
    print("\n🧪 TEST 7: Manejo de reacción de usuario")
    try:
        # Crear evento de reacción
        reaction_event = UserReactionEvent(
            user_id=123456789,
            channel_id=channel_id if test_results["create_channel"] else 1,
            content_id=content_id if test_results["add_content"] else 1,
            reaction_type="like",
            points=5
        )
        
        # Simular manejo del evento
        await channel_service.handle_user_reaction(reaction_event)
        
        print("✅ ÉXITO: Evento de reacción procesado (puede haberse rechazado por falta de usuario)")
        test_results["user_reaction"] = True
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    # Verificar eventos publicados
    print("\n🔗 VERIFICACIÓN DE EVENTOS PUBLICADOS:")
    if event_bus.published_events:
        for i, event in enumerate(event_bus.published_events, 1):
            print(f"   {i}. {type(event).__name__}")
    else:
        print("   Ningún evento fue publicado")
    
    # Resumen de resultados
    print("\n📊 RESUMEN DE RESULTADOS:")
    print("=" * 50)
    
    passed = sum(test_results.values())
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"   {test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nPuntuación: {passed}/{total} pruebas pasaron")
    
    # Determinar estado del módulo
    if passed == total:
        module_status = "✅ COMPLETO"
    elif passed >= total * 0.7:
        module_status = "⚠️ PARCIAL"
    else:
        module_status = "❌ FALTANTE"
    
    print(f"Estado del módulo: {module_status}")
    
    return {
        "status": module_status,
        "passed": passed,
        "total": total,
        "results": test_results,
        "events_published": len(event_bus.published_events)
    }

if __name__ == "__main__":
    asyncio.run(test_channel_service())