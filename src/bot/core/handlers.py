"""Configuración de manejadores de eventos."""

import structlog
from aiogram import Dispatcher

from src.core.interfaces.IEventBus import IEventBus
from src.modules.narrative.service import NarrativeService
from src.modules.gamification.service import GamificationService
from ..services.admin import AdminService

from ..handlers.user import register_user_handlers
from ..handlers.admin import register_admin_handlers
# from ..handlers.vip import register_vip_handlers  # Módulo no existe
from ..handlers.narrative import register_narrative_handlers
from ..handlers.gamification import register_gamification_handlers

logger = structlog.get_logger()

def setup_handlers(dp: Dispatcher, event_bus: IEventBus = None, gamification_service: GamificationService = None, admin_service = None) -> None:
    """Configura todos los manejadores de eventos."""
    
    # Si no se pasan servicios, obtenerlos del contenedor de dependencias
    if event_bus is None or gamification_service is None or admin_service is None:
        container = dp["di"]
        event_bus = event_bus or container.resolve(IEventBus)
        gamification_service = gamification_service or container.resolve(GamificationService)
        narrative_service = container.resolve(NarrativeService)
        admin_service = admin_service or container.resolve(AdminService)
    else:
        # Usar servicios pasados directamente (para compatibilidad con TelegramAdapter)
        narrative_service = None  # Por ahora
    
    # Registrar manejadores de usuarios regulares
    register_user_handlers(dp, event_bus, gamification_service, admin_service)
    logger.info("Manejadores de usuarios registrados")
    
    # Registrar manejadores de administradores
    register_admin_handlers(dp, admin_service)
    logger.info("Manejadores de administradores registrados")
    
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