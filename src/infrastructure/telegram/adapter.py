from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from typing import Optional

from src.core.interfaces.IEventBus import IEventBus
from src.modules.gamification.service import GamificationService
from src.modules.admin.service import AdminService
from src.modules.emotional.service import EmotionalService
from src.modules.narrative.service import NarrativeService
from src.modules.channel.service import ChannelService
from src.modules.user.service import UserService
from src.modules.token.tokeneitor import Tokeneitor
from .handlers import setup_handlers

class TelegramAdapter:
    def __init__(
        self, 
        bot_token: str, 
        event_bus: IEventBus, 
        gamification_service: GamificationService, 
        admin_service: AdminService,
        emotional_service: Optional[EmotionalService] = None,
        narrative_service: Optional[NarrativeService] = None,
        channel_service: Optional[ChannelService] = None,
        user_service: Optional[UserService] = None,
        token_service: Optional[Tokeneitor] = None
    ):
        self.bot = Bot(token=bot_token, default_parse_mode=ParseMode.HTML)
        self.dp = Dispatcher()
        self._event_bus = event_bus
        self._gamification_service = gamification_service
        self._admin_service = admin_service
        self._emotional_service = emotional_service
        self._narrative_service = narrative_service
        self._channel_service = channel_service
        self._user_service = user_service
        self._token_service = token_service

    def _register_handlers(self):
        """Registra los handlers de Telegram."""
        # Pasa las dependencias (event_bus, servicios) a los handlers
        setup_handlers(
            self.dp, 
            self._event_bus, 
            self._gamification_service, 
            self._admin_service,
            self._emotional_service,
            self._narrative_service,
            self._channel_service,
            self._user_service,
            self._token_service
        )

    async def start(self):
        """Inicia el bot."""
        self._register_handlers()
        await self.dp.start_polling(self.bot)
