import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram.types import User, Chat, Message, CallbackQuery

from src.core.event_bus import EventBus
from src.infrastructure.telegram.adapter import TelegramAdapter
from src.modules.gamification.service import GamificationService
from src.modules.user.service import UserService


@pytest.fixture
def mock_bot():
    """Crea un mock del Bot de aiogram."""
    bot = MagicMock()
    bot.send_message = AsyncMock()
    bot.edit_message_text = AsyncMock()
    return bot


@pytest.fixture
def event_bus():
    """Crea una instancia del bus de eventos para el test."""
    return EventBus()


@pytest.fixture
def user_service(event_bus):
    """Crea una instancia del UserService."""
    service = UserService()
    service.setup(event_bus)
    return service


@pytest.fixture
def gamification_service(event_bus):
    """Crea una instancia del GamificationService."""
    service = GamificationService()
    service.setup(event_bus)
    # Pre-configurar puntos para el usuario
    service.points[123] = 100
    return service


@pytest.fixture
def telegram_adapter(mock_bot, event_bus, user_service, gamification_service):
    """Configura el adaptador de Telegram con todas las dependencias."""
    adapter = TelegramAdapter(bot=mock_bot, event_bus=event_bus)
    adapter.register_services(
        user_service=user_service,
        gamification_service=gamification_service
    )
    adapter.register_handlers()
    return adapter


@pytest.mark.asyncio
async def test_full_user_flow(telegram_adapter, mock_bot, user_service, gamification_service):
    """
    Valida el flujo completo: /start -> botón -> consulta de puntos.
    """
    # 1. Simular el comando /start
    user = User(id=123, is_bot=False, first_name="Test")
    chat = Chat(id=456, type="private")
    start_message = Message(message_id=789, chat=chat, from_user=user, text="/start")

    # En lugar de usar feed_update, llamamos directamente al handler
    await telegram_adapter.dp.message.trigger(start_message)
    await asyncio.sleep(0.1)  # Dar tiempo a que los eventos se procesen

    # Verificar que el usuario fue registrado
    assert 123 in user_service.registered_users

    # Verificar que se envió el menú
    mock_bot.send_message.assert_called_once()
    args, kwargs = mock_bot.send_message.call_args
    assert "Aquí tienes tu menú" in args[1]
    assert kwargs["reply_markup"] is not None

    # 2. Simular el callback de "Consultar mis puntos"
    callback_query = CallbackQuery(
        id="test_callback",
        from_user=user,
        message=start_message,
        data="get_points"
    )

    # En lugar de usar feed_update, llamamos directamente al handler
    await telegram_adapter.dp.callback_query.trigger(callback_query)
    await asyncio.sleep(0.1)

    # Verificar que se editó el mensaje con los puntos
    mock_bot.edit_message_text.assert_called_once()
    args, kwargs = mock_bot.edit_message_text.call_args
    assert "Tus puntos actuales son: 100" in args[0]
    assert kwargs["chat_id"] == 456
    assert kwargs["message_id"] == 789
