import pytest
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Update, Message, User, Chat, CallbackQuery

from src.core.event_bus import EventBus
from src.modules.gamification.service import GamificationService
from src.modules.user.service import UserService
from src.modules.admin.service import AdminService
from src.bot.database.models import Tariff, SubscriptionToken
from src.infrastructure.telegram.handlers import setup_handlers
from tests.integration.conftest import MockedBot


@pytest.mark.asyncio
async def test_user_registration_and_profile_check(mocked_bot: MockedBot):
    """
    Verifica que un usuario se registra al enviar /start y puede consultar su perfil.
    """
    # Arrange
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    event_bus = EventBus()
    user_service = UserService(event_bus)
    gamification_service = GamificationService(event_bus)
    admin_service = AdminService(event_bus)
    
    # Pre-configurar puntos para el usuario
    gamification_service.points[123] = 100
    
    await user_service.setup()
    await gamification_service.setup()
    await admin_service.setup()
    
    setup_handlers(dp, event_bus, gamification_service, admin_service)

    user = User(id=123, is_bot=False, first_name="Test")
    chat = Chat(id=123, type="private")

    # Act: Simular el comando /start
    start_message = Message(message_id=1, date=1234567890, chat=chat, from_user=user, text="/start")
    start_update = Update(update_id=1, message=start_message)
    await dp.feed_update(mocked_bot, start_update)

    # Assert: Verificar que el usuario fue registrado
    assert user.id in user_service.users

    # Act: Simular el callback de perfil
    callback_message = Message(message_id=1, date=1234567891, chat=chat, from_user=user, text="...")
    callback_query = CallbackQuery(id="1", from_user=user, message=callback_message, chat_instance="1", data="main_menu:profile")
    callback_update = Update(update_id=2, callback_query=callback_query)
    await dp.feed_update(mocked_bot, callback_update)

    # Assert: Verificar que se editó el mensaje
    edited_message = mocked_bot.requests[1]
    assert edited_message.text == "Este es tu perfil:\n\nPuntos: 100"