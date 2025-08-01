from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from src.core.interfaces.IEventBus import IEventBus
from src.modules.gamification.service import GamificationService
from src.modules.admin.service import AdminService
from src.modules.narrative.service import NarrativeService
from src.modules.channel.service import ChannelService
from .handlers import setup_handlers

class TelegramAdapter:
    def __init__(self, bot_token: str, event_bus: IEventBus, gamification_service: GamificationService, admin_service: AdminService,
                 narrative_service: NarrativeService = None, channel_service: ChannelService = None):
        self.bot = Bot(token=bot_token, default_parse_mode=ParseMode.HTML)
        self.dp = Dispatcher()
        self._event_bus = event_bus
        self._gamification_service = gamification_service
        self._admin_service = admin_service
        self._narrative_service = narrative_service
        self._channel_service = channel_service

    def _register_handlers(self):
        """Registra los handlers de Telegram."""
        # Pasa las dependencias (event_bus, servicios) a los handlers
        setup_handlers(self.dp, self._event_bus, self._gamification_service, self._admin_service, 
                      self._narrative_service, self._channel_service)

    async def start(self):
        """Inicia el bot."""
        self._register_handlers()
        await self.dp.start_polling(self.bot)
