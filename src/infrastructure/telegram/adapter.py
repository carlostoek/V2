from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from src.core.interfaces.IEventBus import IEventBus
from src.modules.gamification.service import GamificationService
from src.modules.admin.service import AdminService
from src.modules.narrative.service import NarrativeService
from src.modules.user.service import UserService
from src.modules.tariff.service import TariffService
from src.modules.daily_rewards.service import DailyRewardsService
from src.bot.core.diana_master_system import register_diana_master_system

class TelegramAdapter:
    from typing import Dict, Any

class TelegramAdapter:
    def __init__(self, bot_token: str, event_bus: IEventBus, diana_interface: Any, services: Dict[str, Any]):
        self.bot = Bot(token=bot_token, default_parse_mode=ParseMode.HTML)
        self.dp = Dispatcher()
        self._event_bus = event_bus
        self._services = services
        self.diana_master = diana_interface # Store the initialized DianaMasterInterface

    def _register_handlers(self):
        """🚀 Registra el sistema maestro Diana."""
        # Register the Diana Master System
        # The diana_master is already initialized and passed in __init__
        register_diana_master_system(self.dp, self._services)
        print("🎭 Diana Master System successfully integrated!")

    async def start(self):
        """Inicia el bot."""
        self._register_handlers()
        await self.dp.start_polling(self.bot)
