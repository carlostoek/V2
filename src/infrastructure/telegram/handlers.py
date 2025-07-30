from aiogram import types, F, Dispatcher
from aiogram.filters import CommandStart

from src.core.interfaces.IEventBus import IEventBus
from src.modules.events import UserStartedBotEvent
from src.modules.gamification.service import GamificationService

class Handlers:
    def __init__(self, event_bus: IEventBus, gamification_service: GamificationService):
        self._event_bus = event_bus
        self._gamification_service = gamification_service

    def get_main_menu_keyboard(self):
        buttons = [
            [types.InlineKeyboardButton(text="Consultar mis puntos", callback_data="get_points")]
        ]
        return types.InlineKeyboardMarkup(inline_keyboard=buttons)

    async def handle_start(self, message: types.Message):
        event = UserStartedBotEvent(user_id=message.from_user.id, username=message.from_user.username)
        await self._event_bus.publish(event)
        await message.answer(
            "¡Bienvenido al bot de prueba V2!",
            reply_markup=self.get_main_menu_keyboard()
        )

    async def handle_get_points_callback(self, query: types.CallbackQuery):
        user_id = query.from_user.id
        points = self._gamification_service.get_points(user_id)
        await query.message.edit_text(f"Tienes {points} puntos.")
        await query.answer()

    def register(self, dp: Dispatcher):
        dp.message.register(self.handle_start, CommandStart())
        dp.callback_query.register(self.handle_get_points_callback, F.data == "get_points")

def setup_handlers(dp: Dispatcher, event_bus: IEventBus, gamification_service: GamificationService):
    """Configura todos los handlers de la aplicación."""
    handler_instance = Handlers(event_bus, gamification_service)
    handler_instance.register(dp)