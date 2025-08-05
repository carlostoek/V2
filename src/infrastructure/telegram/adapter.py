from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from src.core.interfaces.IEventBus import IEventBus
from src.modules.gamification.service import GamificationService
from src.modules.admin.service import AdminService
from src.modules.narrative.service import NarrativeService
from src.modules.tariff.service import TariffService
from src.modules.daily_rewards.service import DailyRewardsService
from src.modules.shop.service import ShopService
from src.modules.trivia.service import TriviaService
from src.bot.core.diana_master_system import DianaMasterInterface, register_diana_master_system

class TelegramAdapter:
    def __init__(self, bot_token: str, event_bus: IEventBus, gamification_service: GamificationService, admin_service: AdminService, narrative_service: NarrativeService, diana_interface: DianaMasterInterface):
        self.bot = Bot(token=bot_token, default_parse_mode=ParseMode.HTML)
        self.dp = Dispatcher()
        self._event_bus = event_bus
        self._gamification_service = gamification_service
        self._admin_service = admin_service
        self._narrative_service = narrative_service
        self._diana_interface = diana_interface
        
        # Initialize additional services
        self._tariff_service = TariffService(event_bus)
        self._daily_rewards_service = DailyRewardsService(gamification_service)
        self._shop_service = ShopService(gamification_service)
        self._trivia_service = TriviaService(gamification_service)
        
        # Prepare services dictionary for Diana Master System
        self._services = {
            'gamification': gamification_service,
            'admin': admin_service,
            'narrative': narrative_service,
            'tariff': self._tariff_service,
            'event_bus': event_bus,
            'daily_rewards': self._daily_rewards_service,
            'shop_service': self._shop_service,
            'trivia_service': self._trivia_service
        }

    def _register_handlers(self):
        """🚀 Registra el sistema maestro Diana."""
        # Setup services
        import asyncio
        asyncio.create_task(self._tariff_service.setup())
        asyncio.create_task(self._daily_rewards_service.setup())
        
        # Register the Diana Master System
        register_diana_master_system(self.dp, self._diana_interface, self._services)
        print("🎭 Diana Master System successfully integrated!")

    async def start(self):
        """Inicia el bot."""
        self._register_handlers()
        await self.dp.start_polling(self.bot)
