"""Bootstrap del bot, inicializa todos los componentes."""

import logging
import structlog
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from ..config import settings
from ..database import init_db
from .bot import setup_bot
from .middleware import setup_middlewares
from .containers import ApplicationContainer
from .handlers import setup_handlers
from .errors import setup_error_handlers
from .scheduler import setup_scheduler
from .diana_master_system import register_diana_master_system
from .diana_admin_master import register_diana_admin_master
from src.modules.tariff.service import TariffService
from src.modules.daily_rewards.service import DailyRewardsService

logger = structlog.get_logger()

async def bootstrap():
    """Inicializa todos los componentes del bot."""
    logger.info("Inicializando componentes del bot")

    # Crear contenedor de aplicación
    container = ApplicationContainer()
    container.core.config.from_dict(settings.model_dump())

    # Inicializar base de datos
    logger.info("Inicializando base de datos")
    await init_db()

    # Obtener bot y dispatcher del contenedor
    bot = container.core.bot()
    dp = container.core.dispatcher()

    # Configurar contenedor de dependencias
    dp["di"] = container

    # Configurar bot
    logger.info("Configurando bot")
    await setup_bot(bot)

    # Configurar manejadores de errores
    logger.info("Configurando manejadores de errores")
    setup_error_handlers(dp)

    # Configurar middlewares
    logger.info("Configurando middlewares")
    setup_middlewares(dp)

    # Configurar manejadores - DESHABILITADO: Diana Master System maneja todo ahora
    # logger.info("Configurando manejadores")
    # setup_handlers(dp)
    logger.info("Manejadores legacy DESHABILITADOS - Se requiere Diana Master System")
    
    # Registrar Diana Master System
    logger.info("Registrando Diana Master System")
    try:
        # Inicializar servicios adicionales requeridos
        event_bus = container.core.event_bus()
        gamification_service = container.services.gamification_service()
        tariff_service = TariffService(event_bus)
        daily_rewards_service = DailyRewardsService(gamification_service)
        
        # Setup de servicios adicionales
        await tariff_service.setup()
        await daily_rewards_service.setup()
        
        # Preparar servicios necesarios para Diana Master System
        services = {
            'gamification': gamification_service,
            'admin': container.services.admin_service(),
            'narrative': container.services.narrative_service(),
            'event_bus': event_bus,
            'tariff': tariff_service,
            'daily_rewards': daily_rewards_service
        }
        
        # Registrar Diana Admin Master System
        register_diana_admin_master(dp, services)
        logger.info("✅ Diana Admin Master System registrado correctamente")
        
        # Registrar Diana Master System  
        register_diana_master_system(dp, services)
        logger.info("✅ Diana Master System registrado correctamente")
        
    except Exception as e:
        logger.error("❌ Error registrando Diana Master System", error=str(e))
        raise

    # Configurar programador de tareas
    logger.info("Configurando programador de tareas")
    admin_service = container.services.admin_service()
    scheduler = setup_scheduler(admin_service)
    
    try:
        # Iniciar programador de tareas
        if settings.ENABLE_BACKGROUND_TASKS:
            logger.info("Iniciando programador de tareas")
            scheduler.start()
        
        # Iniciar polling
        logger.info("Iniciando polling")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        # Detener programador de tareas
        if settings.ENABLE_BACKGROUND_TASKS:
            logger.info("Deteniendo programador de tareas")
            scheduler.shutdown(wait=True)
        
        # Cerrar sesión del bot
        logger.info("Cerrando sesión del bot")
        await bot.session.close()