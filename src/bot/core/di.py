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
from ..services.role import RoleService
from ..database import get_session

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
    
    # Crear el bus de eventos con auto-suscripción
    event_bus = EventBus()
    container.register(IEventBus, event_bus)
    container.register(EventBus, event_bus)
    
    # Crear sesión de base de datos
    async for session in get_session():
        # Crear servicios con dependencias cruzadas
        user_service = UserService(event_bus, session)
        emotional_service = EmotionalService(event_bus, user_service, session)
        gamification_service = GamificationService(
            event_bus, 
            user_service,
            emotional_service,
            session
        )
        narrative_service = NarrativeService(
            event_bus,
            gamification_service,
            emotional_service,
            session
        )
        admin_service = AdminService(event_bus, user_service, session)
        role_service = RoleService(event_bus, user_service, session)
        
        # Auto-suscribir manejadores de eventos
        for service in [user_service, emotional_service, 
                       gamification_service, narrative_service,
                       admin_service, role_service]:
            event_bus.auto_subscribe(service)
        
        # Configurar servicios
        await narrative_service.setup()
        await gamification_service.setup()
        await emotional_service.setup()
        
        # Registrar servicios
        container.register(UserService, user_service)
        container.register(EmotionalService, emotional_service)
        container.register(GamificationService, gamification_service)
        container.register(NarrativeService, narrative_service)
        container.register(AdminService, admin_service)
        container.register(RoleService, role_service)
        
        break  # Solo necesitamos una sesión
    
    logger.info("DI Container configurado con dependencias cruzadas y auto-suscripción")
    
    return container
