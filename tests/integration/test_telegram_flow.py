import pytest
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple, Union

from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.methods import TelegramMethod
from aiogram.types import Update, Message, User, Chat, CallbackQuery

from src.core.event_bus import EventBus
from src.modules.gamification.service import GamificationService
from src.modules.user.service import UserService
from src.infrastructure.telegram.handlers import setup_handlers

class MockedBot(Bot):
    """Bot mockeado para interceptar llamadas a la API en tests."""
    def __init__(self, **kwargs):
        super().__init__(token="8426456639:AAHgA6kNgAUxT1l3EZJNKlwoE4xdcytbMLw", **kwargs)
        self.requests: List[TelegramMethod] = []

    async def __call__(self, method: TelegramMethod) -> Any:
        self.requests.append(method)
        return True # Simula una respuesta exitosa de la API

@pytest.fixture
async def mocked_bot() -> AsyncGenerator[MockedBot, None]:
    yield MockedBot()

@pytest.mark.asyncio
async def test_start_command_and_get_points_callback(mocked_bot: MockedBot):
    """Verifica el flujo completo desde un comando /start hasta un callback."""
    # Arrange
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    event_bus = EventBus()
    user_service = UserService(event_bus)
    gamification_service = GamificationService(event_bus)
    
    await user_service.setup()
    await gamification_service.setup()
    
    setup_handlers(dp, event_bus, gamification_service)

    user = User(id=123, is_bot=False, first_name="Test")
    chat = Chat(id=123, type="private")

    # Act: Simular el comando /start
    start_message = Message(message_id=1, date=1234567890, chat=chat, from_user=user, text="/start")
    start_update = Update(update_id=1, message=start_message)
    await dp.feed_update(mocked_bot, start_update)

    # Assert: Verificar que se envió el mensaje de bienvenida
    assert len(mocked_bot.requests) == 1
    sent_message = mocked_bot.requests[0]
    assert sent_message.text == "¡Bienvenido al bot de prueba V2!"
    assert sent_message.reply_markup is not None

    # Act: Simular el callback
    callback_message = Message(message_id=1, date=1234567891, chat=chat, from_user=user, text="...")
    callback_query = CallbackQuery(id="1", from_user=user, message=callback_message, chat_instance="1", data="get_points")
    callback_update = Update(update_id=2, callback_query=callback_query)
    await dp.feed_update(mocked_bot, callback_update)

    # Assert: Verificar que se editó el mensaje con los puntos
    assert len(mocked_bot.requests) == 2
    edited_message = mocked_bot.requests[1]
    assert edited_message.text == "Tienes 0 puntos."