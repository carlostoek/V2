from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from src.core.interfaces.IEventBus import IEventBus
from src.modules.gamification.service import GamificationService
from src.modules.admin.service import AdminService
from src.modules.narrative.service import NarrativeService
from src.bot.core.handlers import setup_handlers as setup_modern_handlers
from src.bot.core.di import Container
# from .handlers import setup_handlers  # Sistema viejo comentado

class TelegramAdapter:
    def __init__(self, bot_token: str, event_bus: IEventBus, gamification_service: GamificationService, admin_service: AdminService, narrative_service: NarrativeService = None):
        self.bot = Bot(token=bot_token, default_parse_mode=ParseMode.HTML)
        self.dp = Dispatcher()
        self._event_bus = event_bus
        self._gamification_service = gamification_service
        self._admin_service = admin_service
        self._narrative_service = narrative_service

    def _register_handlers(self):
        """Registra los handlers de Telegram usando el sistema moderno."""
        print("🔧 TelegramAdapter: Registrando sistema moderno de handlers...")
        
        # Configurar contenedor de dependencias
        container = Container()
        container.register(IEventBus, self._event_bus)
        container.register(GamificationService, self._gamification_service)
        container.register(NarrativeService, self._narrative_service)
        container.register(AdminService, self._admin_service)
        
        # Asignar al dispatcher
        self.dp["di"] = container
        
        # Usar el sistema moderno de handlers
        setup_modern_handlers(self.dp)

    async def start(self):
        """Inicia el bot."""
        self._register_handlers()
        await self.dp.start_polling(self.bot)
