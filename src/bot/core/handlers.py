"""Configuración de manejadores de eventos."""

import structlog
from aiogram import Dispatcher

from src.core.interfaces.IEventBus import IEventBus
from src.modules.narrative.service import NarrativeService
from src.modules.gamification.service import GamificationService
from ..services.admin import AdminService

from ..handlers.user import register_user_handlers
# from ..handlers.admin import register_admin_handlers  # ELIMINADO - Será reemplazado por menú maestro
# from ..handlers.vip import register_vip_handlers  # Módulo no existe
from ..handlers.narrative import register_narrative_handlers
from ..handlers.gamification import register_gamification_handlers

logger = structlog.get_logger()

def setup_handlers(dp: Dispatcher) -> None:
    """Configura todos los manejadores de eventos."""
    
    # Obtener servicios del contenedor de dependencias
    container = dp["di"]
    event_bus = container.resolve(IEventBus)
    gamification_service = container.resolve(GamificationService)
    narrative_service = container.resolve(NarrativeService)
    admin_service = container.resolve(AdminService)
    
    # Registrar manejadores de usuarios regulares
    # register_user_handlers(dp, event_bus, gamification_service, admin_service)  # DESACTIVADO - Diana Master System maneja esto ahora
    logger.info("Manejadores de usuarios legacy DESACTIVADOS - Diana Master System los reemplaza")
    
    # Registrar manejadores de administradores
    # register_admin_handlers(dp, admin_service)  # ELIMINADO - Será manejado por menú maestro
    # logger.info("Manejadores de administradores registrados")
    
    # Registrar manejadores de usuarios VIP
    # register_vip_handlers(dp)  # Módulo no existe
    # logger.info("Manejadores de usuarios VIP registrados")
    
    # Registrar manejadores de narrativa
    register_narrative_handlers(dp, event_bus, narrative_service)
    logger.info("Manejadores de narrativa registrados")
    
    # Registrar manejadores de gamificación
    register_gamification_handlers(dp, event_bus, gamification_service)
    logger.info("Manejadores de gamificación registrados")
    
    logger.info("Todos los manejadores configurados")