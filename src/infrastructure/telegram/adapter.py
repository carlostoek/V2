from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from src.core.interfaces.IEventBus import IEventBus
from src.modules.gamification.service import GamificationService
from src.modules.admin.service import AdminService
from src.modules.narrative.service import NarrativeService
from src.modules.tariff.service import TariffService
from src.bot.core.diana_master_system import register_diana_master_system

class TelegramAdapter:
    def __init__(self, bot_token: str, event_bus: IEventBus, gamification_service: GamificationService, admin_service: AdminService, narrative_service: NarrativeService = None):
        self.bot = Bot(token=bot_token, default_parse_mode=ParseMode.HTML)
        self.dp = Dispatcher()
        self._event_bus = event_bus
        self._gamification_service = gamification_service
        self._admin_service = admin_service
        self._narrative_service = narrative_service
        
        # Initialize TariffService
        self._tariff_service = TariffService(event_bus)
        
        # Prepare services dictionary for Diana Master System
        self._services = {
            'gamification': gamification_service,
            'admin': admin_service,
            'narrative': narrative_service,
            'tariff': self._tariff_service,
            'event_bus': event_bus,
            'daily_rewards': gamification_service  # Assuming daily rewards are part of gamification
        }

    def _register_handlers(self):
        """🚀 Registra el sistema maestro Diana."""
        # Setup tariff service
        import asyncio
        asyncio.create_task(self._tariff_service.setup())
        
        # Register the Diana Master System
        self.diana_master = register_diana_master_system(self.dp, self._services)
        print("🎭 Diana Master System successfully integrated!")

    async def start(self):
        """Inicia el bot."""
        self._register_handlers()
        await self.dp.start_polling(self.bot)
