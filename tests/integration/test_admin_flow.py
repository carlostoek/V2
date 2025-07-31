import pytest
from datetime import datetime, timedelta
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
from tests.unit.test_admin_service import db_session, admin_service

@pytest.mark.asyncio
async def test_free_channel_setup_flow(mocked_bot: MockedBot, admin_service: AdminService):
    """Verifica el flujo de configuración del canal gratuito."""
    # Arrange
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    event_bus = EventBus()
    user_service = UserService(event_bus)
    gamification_service = GamificationService(event_bus)
    
    await user_service.setup()
    await gamification_service.setup()
    await admin_service.setup()
    
    setup_handlers(dp, event_bus, gamification_service, admin_service)

    admin_user = User(id=123, is_bot=False, first_name="Admin")
    chat = Chat(id=123, type="private")

    # 1. Admin envía /admin
    admin_command_message = Message(message_id=1, date=1234567890, chat=chat, from_user=admin_user, text="/admin")
    await dp.feed_update(mocked_bot, Update(update_id=1, message=admin_command_message))

    assert len(mocked_bot.requests) == 1
    assert "Menú de Administración" in mocked_bot.requests[0].text

    # 2. Admin pulsa "Administrar Canal Gratuito"
    sent_message_data = mocked_bot.requests[0]
    message_for_callback = Message(message_id=1, date=1234567891, chat=chat, from_user=admin_user, text=sent_message_data.text)
    callback_query = CallbackQuery(id="1", from_user=admin_user, message=message_for_callback, chat_instance="1", data="admin:free_channel_menu")
    await dp.feed_update(mocked_bot, Update(update_id=2, callback_query=callback_query))

    assert len(mocked_bot.requests) == 3 # sendMessage, editMessageText, answerCallbackQuery
    assert "Administración Canal Gratuito" in mocked_bot.requests[1].text

    # 3. Admin pulsa "Configurar Canal"
    callback_query_2 = CallbackQuery(id="2", from_user=admin_user, message=message_for_callback, chat_instance="1", data="admin:setup_free_channel")
    await dp.feed_update(mocked_bot, Update(update_id=3, callback_query=callback_query_2))

    assert len(mocked_bot.requests) == 5 # + editMessageText, answerCallbackQuery
    assert "Por favor, reenvía un mensaje" in mocked_bot.requests[3].text

    # 4. Admin reenvía un mensaje del canal
    channel = Chat(id=-100123456789, type="channel", title="Test Channel")
    forwarded_message = Message(
        message_id=2, 
        date=1234567891, 
        chat=chat, 
        from_user=admin_user, 
        forward_from_chat=channel, 
        text="test message"
    )
    await dp.feed_update(mocked_bot, Update(update_id=4, message=forwarded_message))

    assert len(mocked_bot.requests) == 7 # + 2 sendMessage (confirmación y nuevo menú)
    assert f"Canal gratuito configurado con ID: {channel.id}" in mocked_bot.requests[5].text
    assert admin_service.get_free_channel_id() == channel.id

@pytest.mark.asyncio
async def test_set_wait_time_flow(mocked_bot: MockedBot, admin_service: AdminService):
    """Verifica el flujo de configuración del tiempo de espera."""
    # Arrange
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    event_bus = EventBus()
    user_service = UserService(event_bus)
    gamification_service = GamificationService(event_bus)
    admin_service.set_free_channel_id(-100123456789) # Pre-configurar canal
    
    await user_service.setup()
    await gamification_service.setup()
    await admin_service.setup()
    
    setup_handlers(dp, event_bus, gamification_service, admin_service)

    admin_user = User(id=123, is_bot=False, first_name="Admin")
    chat = Chat(id=123, type="private")

    # 1. Admin va al menú del canal gratuito
    message_for_callback = Message(message_id=1, date=1234567891, chat=chat, from_user=admin_user, text="...")
    callback_query = CallbackQuery(id="1", from_user=admin_user, message=message_for_callback, chat_instance="1", data="admin:free_channel_menu")
    await dp.feed_update(mocked_bot, Update(update_id=1, callback_query=callback_query))

    # 2. Admin pulsa "Configurar Tiempo de Espera"
    callback_query_2 = CallbackQuery(id="2", from_user=admin_user, message=message_for_callback, chat_instance="1", data="admin:set_wait_time")
    await dp.feed_update(mocked_bot, Update(update_id=2, callback_query=callback_query_2))

    assert "Configurar Tiempo de Espera" in mocked_bot.requests[2].text

    # 3. Admin selecciona "1 hora"
    callback_query_3 = CallbackQuery(id="3", from_user=admin_user, message=message_for_callback, chat_instance="1", data="admin:set_wait_time_60")
    await dp.feed_update(mocked_bot, Update(update_id=3, callback_query=callback_query_3))

    assert admin_service.get_wait_time() == 60
    assert "Administración Canal Gratuito" in mocked_bot.requests[5].text # Debería volver al menú

@pytest.mark.asyncio
async def test_send_post_flow(mocked_bot: MockedBot, admin_service: AdminService):
    """Verifica el flujo de envío de un post al canal gratuito."""
    # Arrange
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    event_bus = EventBus()
    user_service = UserService(event_bus)
    gamification_service = GamificationService(event_bus)
    admin_service.set_free_channel_id(-100123456789) # Pre-configurar canal
    
    await user_service.setup()
    await gamification_service.setup()
    await admin_service.setup()
    
    setup_handlers(dp, event_bus, gamification_service, admin_service)

    admin_user = User(id=123, is_bot=False, first_name="Admin")
    chat = Chat(id=123, type="private")

    # 1. Admin va al menú de envío
    message_for_callback = Message(message_id=1, date=1234567891, chat=chat, from_user=admin_user, text="...")
    callback_query = CallbackQuery(id="1", from_user=admin_user, message=message_for_callback, chat_instance="1", data="admin:send_to_free_channel")
    await dp.feed_update(mocked_bot, Update(update_id=1, callback_query=callback_query))

    # 2. Admin envía el texto del post
    post_text = "Este es un post de prueba."
    post_message = Message(message_id=2, date=1234567892, chat=chat, from_user=admin_user, text=post_text)
    await dp.feed_update(mocked_bot, Update(update_id=2, message=post_message))

    assert "Texto del post guardado" in mocked_bot.requests[2].text

    # 3. Admin confirma el envío
    callback_query_2 = CallbackQuery(id="2", from_user=admin_user, message=message_for_callback, chat_instance="1", data="admin:confirm_post")
    await dp.feed_update(mocked_bot, Update(update_id=3, callback_query=callback_query_2))

    assert "Post enviado al canal" in mocked_bot.requests[3].text

@pytest.mark.asyncio
async def test_create_tariff_flow(mocked_bot: MockedBot, admin_service: AdminService):
    """Verifica el flujo de creación de una tarifa."""
    # Arrange
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    event_bus = EventBus()
    user_service = UserService(event_bus)
    gamification_service = GamificationService(event_bus)
    
    await user_service.setup()
    await gamification_service.setup()
    await admin_service.setup()
    
    setup_handlers(dp, event_bus, gamification_service, admin_service)

    admin_user = User(id=123, is_bot=False, first_name="Admin")
    chat = Chat(id=123, type="private")

    # 1. Admin va al menú VIP
    message_for_callback = Message(message_id=1, date=1234567891, chat=chat, from_user=admin_user, text="...")
    callback_query = CallbackQuery(id="1", from_user=admin_user, message=message_for_callback, chat_instance="1", data="admin:vip_channel_menu")
    await dp.feed_update(mocked_bot, Update(update_id=1, callback_query=callback_query))

    # 2. Admin pulsa "Crear Nueva Tarifa"
    callback_query_2 = CallbackQuery(id="2", from_user=admin_user, message=message_for_callback, chat_instance="1", data="admin:create_tariff")
    await dp.feed_update(mocked_bot, Update(update_id=2, callback_query=callback_query_2))

    # 3. Admin envía el nombre
    name_message = Message(message_id=2, date=1234567892, chat=chat, from_user=admin_user, text="Test Tariff")
    await dp.feed_update(mocked_bot, Update(update_id=3, message=name_message))

    # 4. Admin envía el precio
    price_message = Message(message_id=3, date=1234567893, chat=chat, from_user=admin_user, text="10.99")
    await dp.feed_update(mocked_bot, Update(update_id=4, message=price_message))

    # 5. Admin envía la duración
    duration_message = Message(message_id=4, date=1234567894, chat=chat, from_user=admin_user, text="30")
    await dp.feed_update(mocked_bot, Update(update_id=5, message=duration_message))

    tariffs = await admin_service.get_all_tariffs()
    assert len(tariffs) == 1
    assert "¡Tarifa creada con éxito!" in mocked_bot.requests[6].text

@pytest.mark.asyncio
async def test_delete_tariff_flow(mocked_bot: MockedBot, admin_service: AdminService):
    """Verifica el flujo de eliminación de una tarifa."""
    # Arrange
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    event_bus = EventBus()
    user_service = UserService(event_bus)
    gamification_service = GamificationService(event_bus)
    tariff = await admin_service.create_tariff("Test Tariff", 10.0, 30)
    
    await user_service.setup()
    await gamification_service.setup()
    await admin_service.setup()
    
    setup_handlers(dp, event_bus, gamification_service, admin_service)

    admin_user = User(id=123, is_bot=False, first_name="Admin")
    chat = Chat(id=123, type="private")

    # 1. Admin va al menú VIP
    message_for_callback = Message(message_id=1, date=1234567891, chat=chat, from_user=admin_user, text="...")
    callback_query = CallbackQuery(id="1", from_user=admin_user, message=message_for_callback, chat_instance="1", data="admin:vip_channel_menu")
    await dp.feed_update(mocked_bot, Update(update_id=1, callback_query=callback_query))

    # 2. Admin pulsa en la tarifa para verla
    callback_query_2 = CallbackQuery(id="2", from_user=admin_user, message=message_for_callback, chat_instance="1", data=f"admin:view_tariff_{tariff.id}")
    await dp.feed_update(mocked_bot, Update(update_id=2, callback_query=callback_query_2))

    # 3. Admin pulsa "Eliminar Tarifa"
    callback_query_3 = CallbackQuery(id="3", from_user=admin_user, message=message_for_callback, chat_instance="1", data=f"admin:delete_tariff_{tariff.id}")
    await dp.feed_update(mocked_bot, Update(update_id=3, callback_query=callback_query_3))

    tariffs = await admin_service.get_all_tariffs()
    assert len(tariffs) == 0
    assert "Tarifa eliminada con éxito" in mocked_bot.requests[3].text

@pytest.mark.asyncio
async def test_generate_token_flow(mocked_bot: MockedBot, admin_service: AdminService):
    """Verifica el flujo de generación de un token."""
    # Arrange
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    event_bus = EventBus()
    user_service = UserService(event_bus)
    gamification_service = GamificationService(event_bus)
    tariff = await admin_service.create_tariff("Test Tariff", 10.0, 30)
    
    await user_service.setup()
    await gamification_service.setup()
    await admin_service.setup()
    
    setup_handlers(dp, event_bus, gamification_service, admin_service)

    admin_user = User(id=123, is_bot=False, first_name="Admin")
    chat = Chat(id=123, type="private")

    # 1. Admin va al menú VIP
    message_for_callback = Message(message_id=1, date=1234567891, chat=chat, from_user=admin_user, text="...")
    callback_query = CallbackQuery(id="1", from_user=admin_user, message=message_for_callback, chat_instance="1", data="admin:vip_channel_menu")
    await dp.feed_update(mocked_bot, Update(update_id=1, callback_query=callback_query))

    # 2. Admin pulsa en la tarifa para verla
    callback_query_2 = CallbackQuery(id="2", from_user=admin_user, message=message_for_callback, chat_instance="1", data=f"admin:view_tariff_{tariff.id}")
    await dp.feed_update(mocked_bot, Update(update_id=2, callback_query=callback_query_2))

    # 3. Admin pulsa "Generar Token"
    callback_query_3 = CallbackQuery(id="3", from_user=admin_user, message=message_for_callback, chat_instance="1", data=f"admin:generate_token_{tariff.id}")
    await dp.feed_update(mocked_bot, Update(update_id=3, callback_query=callback_query_3))

    assert len(admin_service.tokens) == 1
    assert "Token generado:" in mocked_bot.requests[4].text

@pytest.mark.asyncio
async def test_redeem_token_flow(mocked_bot: MockedBot, admin_service: AdminService):
    """Verifica el flujo de canjeo de un token."""
    # Arrange
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    event_bus = EventBus()
    user_service = UserService(event_bus)
    gamification_service = GamificationService(event_bus)
    tariff = await admin_service.create_tariff("Test Tariff", 10.0, 30)
    token = await admin_service.generate_subscription_token(tariff.id)
    
    await user_service.setup()
    await gamification_service.setup()
    await admin_service.setup()
    
    setup_handlers(dp, event_bus, gamification_service, admin_service)

    user = User(id=456, is_bot=False, first_name="Test User")
    chat = Chat(id=456, type="private")

    # Act
    start_message = Message(message_id=1, date=1234567890, chat=chat, from_user=user, text=f"/start {token.token}")
    await dp.feed_update(mocked_bot, Update(update_id=1, message=start_message))

    # Assert
    assert "¡Felicidades!" in mocked_bot.requests[0].text
    validated_token = await admin_service.validate_token(token.token, user.id)
    assert validated_token.is_used is True

@pytest.mark.asyncio
async def test_get_expiring_subscriptions(admin_service: AdminService):
    """Verifica que se pueden obtener las suscripciones que expiran."""
    # Arrange
    tariff = await admin_service.create_tariff("Test Tariff", 10.0, 1)
    token = await admin_service.generate_subscription_token(tariff.id)
    await admin_service.validate_token(token.token, 123)

    # Act
    expiring_subs = await admin_service.get_expiring_subscriptions(2)

    # Assert
    assert len(expiring_subs) == 1
    assert expiring_subs[0].user_id == 123
