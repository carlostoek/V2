"""Contenedor de inyección de dependencias."""

from typing import Dict, Type, TypeVar, Any, Optional
import structlog
from aiogram import Bot, Dispatcher

from src.core.event_bus import EventBus
from src.core.interfaces.IEventBus import IEventBus
from src.modules.narrative.service import NarrativeService
from src.modules.gamification.service import GamificationService
from ..services.user import UserService
from ..services.emotional import EmotionalService
from ..services.admin import AdminService
from ..database import get_session
from .diana_master_system import DianaMasterInterface, AdaptiveContextEngine

T = TypeVar('T')

logger = structlog.get_logger()

class Container:
    """Contenedor de inyección de dependencias."""
    
    def __init__(self):
        self._services: Dict[Type[Any], Any] = {}
        
    def register(self, service_type: Type[T], instance: T) -> None:
        """Registra una instancia de servicio."""
        self._services[service_type] = instance
        
    def resolve(self, service_type: Type[T]) -> Optional[T]:
        """Resuelve una instancia de servicio."""
        return self._services.get(service_type)

async def setup_di_container(bot: Bot, dp: Dispatcher) -> Container:
    """Configura el contenedor de inyección de dependencias."""
    container = Container()
    
    # Registrar servicios básicos
    container.register(Bot, bot)
    container.register(Dispatcher, dp)
    
    # Crear el bus de eventos
    event_bus = EventBus()
    container.register(IEventBus, event_bus)
    container.register(EventBus, event_bus)
    
    # Crear servicios de módulos
    narrative_service = NarrativeService(event_bus)
    gamification_service = GamificationService(event_bus)
    
    # Configurar servicios
    await narrative_service.setup()
    await gamification_service.setup()
    
    # Registrar servicios de módulos
    container.register(NarrativeService, narrative_service)
    container.register(GamificationService, gamification_service)
    
    # Crear sesión de base de datos
    async for session in get_session():
        # Crear servicios de aplicación
        user_service = UserService()
        emotional_service = EmotionalService()
        admin_service = AdminService(event_bus, session)
        
        # Registrar servicios de aplicación
        container.register(UserService, user_service)
        container.register(EmotionalService, emotional_service)
        container.register(AdminService, admin_service)
        
        # Configurar Diana Master System
        diana_services = {
            'gamification': gamification_service,
            'narrative': narrative_service,
            'user': user_service,
            'admin': admin_service,
            'event_bus': event_bus
        }
        
        # Crear y registrar Diana Master System
        diana_context_engine = AdaptiveContextEngine(diana_services)
        diana_interface = DianaMasterInterface(diana_services)
        
        container.register(AdaptiveContextEngine, diana_context_engine)
        container.register(DianaMasterInterface, diana_interface)
        
        break # Solo necesitamos una sesión para la inyección
    
    logger.info("Contenedor de inyección de dependencias configurado con Diana Master System")
    
    return container