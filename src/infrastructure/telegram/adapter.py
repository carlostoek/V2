from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from src.core.interfaces.IEventBus import IEventBus
from src.modules.gamification.service import GamificationService
from src.modules.admin.service import AdminService
from src.modules.narrative.service import NarrativeService
from src.modules.tariff.service import TariffService
from src.modules.daily_rewards.service import DailyRewardsService
from src.modules.token.tokeneitor import Tokeneitor
from src.bot.core.diana_admin_master import register_diana_admin_master
from src.bot.core.diana_master_system import register_diana_master_system
from src.bot.core.diana_user_master_system import register_diana_user_master_system

class TelegramAdapter:
    def __init__(self, bot_token: str, event_bus: IEventBus, gamification_service: GamificationService, admin_service: AdminService, narrative_service: NarrativeService = None):
        self.bot = Bot(token=bot_token, default_parse_mode=ParseMode.HTML)
        self.dp = Dispatcher()
        self._event_bus = event_bus
        self._gamification_service = gamification_service
        self._admin_service = admin_service
        self._narrative_service = narrative_service
        
        # Initialize additional services
        self._tariff_service = TariffService(event_bus)
        self._daily_rewards_service = DailyRewardsService(gamification_service)
        self._tokeneitor_service = Tokeneitor(event_bus)
        
        # Prepare services dictionary for Diana Master System
        self._services = {
            'gamification': gamification_service,
            'admin': admin_service,
            'narrative': narrative_service,
            'tariff': self._tariff_service,
            'event_bus': event_bus,
            'daily_rewards': self._daily_rewards_service,
            'tokeneitor': self._tokeneitor_service
        }

    def _register_handlers(self):
        """🚀 Unified Diana Systems Integration"""
        # Setup services
        import asyncio
        asyncio.create_task(self._tariff_service.setup())
        asyncio.create_task(self._daily_rewards_service.setup())
        asyncio.create_task(self._tokeneitor_service.setup())
        
        print("🎭 Starting Diana Integration Specialists Activation...")
        print("🌟 Unifying three Diana systems into one cohesive bot...")
        
        # Register all three Diana systems with shared services
        self.diana_admin_master = register_diana_admin_master(self.dp, self._services)
        print("🏛️ Diana Admin Master System: Professional admin interface activated!")
        
        self.diana_user_system = register_diana_user_master_system(self.dp, self._services)
        print("🎭 Diana User Master System: Sophisticated user interface activated!")
        
        # Register the unified Diana Master System (resolves command conflicts)
        self.diana_master_system = register_diana_master_system(self.dp, self._services) 
        print("🎪 Diana Master System: Adaptive context engine activated!")
        
        print("✅ All three Diana systems successfully integrated as one!")
        print("🚀 Bot ready with unified functionality and enhanced UI!")

    async def start(self):
        """Inicia el bot."""
        self._register_handlers()
        await self.dp.start_polling(self.bot)
