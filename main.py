import asyncio
import logging
import os

from src.core.event_bus import EventBus
from src.core.services.config import settings
from src.infrastructure.telegram.adapter import TelegramAdapter
from src.modules.gamification.service import GamificationService
from src.modules.narrative.service import NarrativeService
from src.modules.user.service import UserService
from src.modules.admin.service import AdminService
from src.bot.database.engine import init_db

async def main():
    """Punto de entrada principal de la aplicación V2."""
    logging.basicConfig(level=logging.INFO)
    
    # Inicializar la base de datos (creará tablas si CREATE_TABLES=True)
    await init_db()
    
    event_bus = EventBus()

    # Instanciar servicios
    user_service = UserService(event_bus)
    gamification_service = GamificationService(event_bus)
    narrative_service = NarrativeService(event_bus)
    admin_service = AdminService(event_bus)

    # Conectar servicios al bus
    await user_service.setup()
    await gamification_service.setup()
    await narrative_service.setup()
    await admin_service.setup()

    # Iniciar el adaptador de Telegram
    adapter = TelegramAdapter(
        bot_token=settings.bot_token, 
        event_bus=event_bus, 
        gamification_service=gamification_service,
        admin_service=admin_service
    )
    await adapter.start()

if __name__ == "__main__":
    asyncio.run(main())
