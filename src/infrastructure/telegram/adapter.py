from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from src.core.interfaces.IEventBus import IEventBus
from src.modules.gamification.service import GamificationService
from src.modules.admin.service import AdminService
from src.modules.narrative.service import NarrativeService
from src.modules.tariff.service import TariffService
from src.modules.channel.service import ChannelService
from src.modules.daily_rewards.service import DailyRewardsService
from src.modules.emotional.service import EmotionalService
from src.modules.shop.service import ShopService
from src.modules.trivia.service import TriviaService
from src.modules.user.service import UserService
from src.modules.token.tokeneitor import Tokeneitor
from src.bot.core.diana_admin_master import register_diana_admin_master
from src.bot.core.diana_master_system import register_diana_master_system
from src.bot.core.diana_user_master_system import register_diana_user_master_system
from src.bot.middleware.user_experience import create_user_experience_middleware

class TelegramAdapter:
    def __init__(
        self, 
        bot_token: str, 
        event_bus: IEventBus, 
        gamification_service: GamificationService, 
        admin_service: AdminService, 
        narrative_service: NarrativeService = None,
        all_services: dict = None
    ):
        self.bot = Bot(token=bot_token, default_parse_mode=ParseMode.HTML)
        self.dp = Dispatcher()
        self._event_bus = event_bus
        
        # Core services (maintained for backward compatibility)
        self._gamification_service = gamification_service
        self._admin_service = admin_service
        self._narrative_service = narrative_service
        
        # If all_services is provided, use it; otherwise initialize services locally
        if all_services:
            self._services = all_services.copy()
            self._services['bot'] = self.bot  # Add bot instance
            print(f"🔗 TelegramAdapter: Received {len(all_services)} external services")
        else:
            # Initialize services locally (fallback for backward compatibility)
            self._tariff_service = TariffService(event_bus)
            self._channel_service = ChannelService(event_bus)
            self._daily_rewards_service = DailyRewardsService(gamification_service)
            self._tokeneitor_service = Tokeneitor(event_bus)
            self._emotional_service = EmotionalService()
            self._shop_service = ShopService(gamification_service)
            self._trivia_service = TriviaService(gamification_service)
            self._user_service = UserService(event_bus)
            
            # Prepare services dictionary for Diana Master System
            self._services = {
                'gamification': gamification_service,
                'admin': admin_service,
                'narrative': narrative_service,
                'tariff': self._tariff_service,
                'channel': self._channel_service,
                'event_bus': event_bus,
                'daily_rewards': self._daily_rewards_service,
                'tokeneitor': self._tokeneitor_service,
                'emotional': self._emotional_service,
                'shop': self._shop_service,
                'trivia': self._trivia_service,
                'user': self._user_service,
                'bot': self.bot
            }
            print(f"🔗 TelegramAdapter: Initialized {len(self._services)} local services")

    def _register_handlers(self):
        """🚀 Unified Diana Systems Integration"""
        # Setup services (only if not already setup)
        import asyncio
        if hasattr(self, '_tariff_service'):
            asyncio.create_task(self._tariff_service.setup())
        if hasattr(self, '_channel_service'):
            asyncio.create_task(self._channel_service.setup())
        if hasattr(self, '_daily_rewards_service'):
            asyncio.create_task(self._daily_rewards_service.setup())
        if hasattr(self, '_tokeneitor_service'):
            asyncio.create_task(self._tokeneitor_service.setup())
        if hasattr(self, '_shop_service'):
            asyncio.create_task(self._shop_service.setup())
        if hasattr(self, '_trivia_service'):
            asyncio.create_task(self._trivia_service.setup())
        if hasattr(self, '_user_service'):
            asyncio.create_task(self._user_service.setup())
        
        print("🎭 Starting Diana Integration Specialists Activation...")
        print("🌟 Unifying Diana systems with advanced UX enhancements...")
        
        # Register UX Enhancement Middleware
        ux_middleware = create_user_experience_middleware(self._services)
        self.dp.middleware.setup(ux_middleware)
        print("🌟 User Experience Middleware: Advanced journey tracking activated!")
        
        # Register all three Diana systems with shared services
        self.diana_admin_master = register_diana_admin_master(self.dp, self._services)
        print("🏛️ Diana Admin Master System: Professional admin interface activated!")
        
        self.diana_user_system = register_diana_user_master_system(self.dp, self._services)
        print("🎭 Diana User Master System: Sophisticated user interface activated!")
        
        # Register the unified Diana Master System (resolves command conflicts)
        self.diana_master_system = register_diana_master_system(self.dp, self._services) 
        print("🎪 Diana Master System: Adaptive context engine activated!")
        
        print("✅ All Diana systems successfully integrated with UX enhancements!")
        print("🚀 Bot ready with unified functionality and exceptional user experience!")

    async def start(self):
        """Inicia el bot."""
        self._register_handlers()
        await self.dp.start_polling(self.bot)
