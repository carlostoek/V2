"""Tests para el ChannelService."""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from src.modules.channel.service import ChannelService
from src.modules.channel.events import (
    ChannelJoinRequestEvent,
    ChannelJoinApprovedEvent,
    ChannelJoinRejectedEvent,
    ChannelContentPublishedEvent
)
from src.bot.database.models.channel import (
    Channel, 
    ChannelMembership,
    ChannelAccess,
    ChannelContent
)
from src.bot.database.models.user import User


@pytest.fixture
def event_bus_mock():
    """Mock para el event bus."""
    mock = AsyncMock()
    mock.subscribe = MagicMock()
    mock.publish = AsyncMock()
    return mock


@pytest.fixture
async def channel_service(event_bus_mock):
    """Fixture para el servicio de canales."""
    service = ChannelService(event_bus_mock)
    # Sobrescribir método para evitar cargar datos iniciales
    service._load_initial_data = AsyncMock()
    await service.setup()
    return service


@pytest.mark.asyncio
async def test_setup_subscribes_to_events(event_bus_mock):
    """Test que verifica que el servicio se suscribe a los eventos esperados."""
    service = ChannelService(event_bus_mock)
    service._load_initial_data = AsyncMock()
    
    await service.setup()
    
    # Verificar suscripciones
    assert event_bus_mock.subscribe.call_count >= 2
    event_bus_mock.subscribe.assert_any_call(ChannelJoinRequestEvent, service.handle_join_request)
    event_bus_mock.subscribe.assert_any_call(UserReactionEvent, service.handle_user_reaction)


@pytest.mark.asyncio
async def test_handle_join_request_approves_free_channel(channel_service, event_bus_mock):
    """Test que verifica la aprobación de solicitud para un canal gratuito."""
    user_id = 123
    channel_id = 1
    
    # Mock para session y resultados
    session_mock = AsyncMock()
    
    # Mock para User
    user_mock = MagicMock()
    user_mock.id = user_id
    user_mock.level = 1
    user_mock.is_vip = False
    
    # Mock para Channel
    channel_mock = MagicMock()
    channel_mock.id = channel_id
    channel_mock.type = "free"
    channel_mock.access_rules = None
    
    # Configurar session mock para simular queries
    session_result_mock = MagicMock()
    session_result_mock.scalars().first.side_effect = [
        user_mock,  # Para user_query
        channel_mock,  # Para channel_query
        None  # Para membership_query (no existe membresía previa)
    ]
    session_mock.execute.return_value = session_result_mock
    
    # Mock para get_session
    get_session_mock = MagicMock()
    get_session_mock.return_value.__aenter__.return_value = None
    get_session_mock.return_value.__aexit__.return_value = None
    get_session_mock.return_value.__aiter__.return_value = [session_mock]
    
    # Evento a procesar
    join_event = ChannelJoinRequestEvent(user_id=user_id, channel_id=channel_id)
    
    # Ejecutar con el mock
    with patch('src.modules.channel.service.get_session', return_value=get_session_mock()):
        await channel_service.handle_join_request(join_event)
    
    # Verificar que se ha publicado el evento de aprobación
    event_bus_mock.publish.assert_called_once()
    published_event = event_bus_mock.publish.call_args[0][0]
    assert isinstance(published_event, ChannelJoinApprovedEvent)
    assert published_event.user_id == user_id
    assert published_event.channel_id == channel_id
    
    # Verificar que se creó la membresía
    session_mock.add.assert_called_once()
    membership = session_mock.add.call_args[0][0]
    assert isinstance(membership, ChannelMembership)
    assert membership.user_id == user_id
    assert membership.channel_id == channel_id
    assert membership.is_active == True


@pytest.mark.asyncio
async def test_handle_join_request_rejects_vip_channel(channel_service, event_bus_mock):
    """Test que verifica el rechazo de solicitud para un canal VIP cuando no cumple requisitos."""
    user_id = 123
    channel_id = 1
    
    # Mock para session y resultados
    session_mock = AsyncMock()
    
    # Mock para User
    user_mock = MagicMock()
    user_mock.id = user_id
    user_mock.level = 1
    user_mock.is_vip = False
    
    # Mock para ChannelAccess
    access_rules_mock = MagicMock()
    access_rules_mock.min_level = 3
    access_rules_mock.requires_vip = True
    access_rules_mock.tokens_required = 5
    
    # Mock para Channel
    channel_mock = MagicMock()
    channel_mock.id = channel_id
    channel_mock.type = "vip"
    channel_mock.access_rules = access_rules_mock
    
    # Configurar session mock para simular queries
    session_result_mock = MagicMock()
    session_result_mock.scalars().first.side_effect = [
        user_mock,  # Para user_query
        channel_mock,  # Para channel_query
        None  # Para membership_query (no existe membresía previa)
    ]
    session_mock.execute.return_value = session_result_mock
    
    # Mock para get_session
    get_session_mock = MagicMock()
    get_session_mock.return_value.__aenter__.return_value = None
    get_session_mock.return_value.__aexit__.return_value = None
    get_session_mock.return_value.__aiter__.return_value = [session_mock]
    
    # Evento a procesar
    join_event = ChannelJoinRequestEvent(user_id=user_id, channel_id=channel_id)
    
    # Ejecutar con el mock
    with patch('src.modules.channel.service.get_session', return_value=get_session_mock()):
        await channel_service.handle_join_request(join_event)
    
    # Verificar que se ha publicado el evento de rechazo
    event_bus_mock.publish.assert_called_once()
    published_event = event_bus_mock.publish.call_args[0][0]
    assert isinstance(published_event, ChannelJoinRejectedEvent)
    assert published_event.user_id == user_id
    assert published_event.channel_id == channel_id
    assert "nivel" in published_event.reason.lower()
    
    # Verificar que NO se creó la membresía
    session_mock.add.assert_not_called()


@pytest.mark.asyncio
async def test_create_channel(channel_service):
    """Test que verifica la creación de un canal."""
    telegram_id = "test_channel"
    name = "Test Channel"
    description = "A test channel"
    channel_type = "free"
    
    # Mock para session y resultados
    session_mock = AsyncMock()
    
    # Configurar session mock para simular no channel found (primer query)
    session_result_mock = MagicMock()
    session_result_mock.scalars().first.return_value = None
    session_mock.execute.return_value = session_result_mock
    
    # Mock para get_session
    get_session_mock = MagicMock()
    get_session_mock.return_value.__aenter__.return_value = None
    get_session_mock.return_value.__aexit__.return_value = None
    get_session_mock.return_value.__aiter__.return_value = [session_mock]
    
    # Mock para el ID generado
    channel_id = 1
    def refresh_side_effect(channel):
        channel.id = channel_id
    session_mock.refresh.side_effect = refresh_side_effect
    
    # Ejecutar con el mock
    with patch('src.modules.channel.service.get_session', return_value=get_session_mock()):
        result = await channel_service.create_channel(telegram_id, name, description, channel_type)
    
    # Verificar resultado
    assert result == channel_id
    
    # Verificar que se añadió el canal a la sesión
    session_mock.add.assert_called_once()
    added_channel = session_mock.add.call_args[0][0]
    assert isinstance(added_channel, Channel)
    assert added_channel.telegram_id == telegram_id
    assert added_channel.name == name
    assert added_channel.description == description
    assert added_channel.type == channel_type
    
    # Verificar que se actualizó la cache
    assert telegram_id in channel_service.channels
    assert channel_service.channels[telegram_id]["id"] == channel_id
    assert channel_service.channels[telegram_id]["name"] == name


@pytest.mark.asyncio
async def test_get_user_channels(channel_service):
    """Test que verifica la obtención de canales de un usuario."""
    user_id = 123
    
    # Mock para session y resultados
    session_mock = AsyncMock()
    
    # Mock para User
    user_mock = MagicMock()
    user_mock.id = user_id
    
    # Mock para membresías
    membership1 = MagicMock()
    membership1.join_date = datetime.now() - timedelta(days=10)
    membership1.expires_at = None
    membership1.role = "member"
    
    channel1 = MagicMock()
    channel1.id = 1
    channel1.telegram_id = "channel1"
    channel1.name = "Free Channel"
    channel1.description = "A free channel"
    channel1.type = "free"
    membership1.channel = channel1
    
    membership2 = MagicMock()
    membership2.join_date = datetime.now() - timedelta(days=5)
    membership2.expires_at = datetime.now() + timedelta(days=25)
    membership2.role = "member"
    
    channel2 = MagicMock()
    channel2.id = 2
    channel2.telegram_id = "channel2"
    channel2.name = "VIP Channel"
    channel2.description = "A VIP channel"
    channel2.type = "vip"
    membership2.channel = channel2
    
    # Configurar session mock para simular queries
    user_result_mock = MagicMock()
    user_result_mock.scalars().first.return_value = user_mock
    
    memberships_result_mock = MagicMock()
    memberships_result_mock.scalars().all.return_value = [membership1, membership2]
    
    session_mock.execute.side_effect = [user_result_mock, memberships_result_mock]
    
    # Mock para get_session
    get_session_mock = MagicMock()
    get_session_mock.return_value.__aenter__.return_value = None
    get_session_mock.return_value.__aexit__.return_value = None
    get_session_mock.return_value.__aiter__.return_value = [session_mock]
    
    # Ejecutar con el mock
    with patch('src.modules.channel.service.get_session', return_value=get_session_mock()):
        result = await channel_service.get_user_channels(user_id)
    
    # Verificar resultado
    assert "free" in result
    assert "vip" in result
    assert len(result["free"]) == 1
    assert len(result["vip"]) == 1
    
    # Verificar canal gratuito
    free_channel = result["free"][0]
    assert free_channel["id"] == channel1.id
    assert free_channel["name"] == channel1.name
    assert free_channel["telegram_id"] == channel1.telegram_id
    
    # Verificar canal VIP
    vip_channel = result["vip"][0]
    assert vip_channel["id"] == channel2.id
    assert vip_channel["name"] == channel2.name
    assert vip_channel["telegram_id"] == channel2.telegram_id
    assert vip_channel["expires_at"] is not None


@pytest.mark.asyncio
async def test_add_channel_content(channel_service, event_bus_mock):
    """Test que verifica la adición de contenido a un canal."""
    channel_id = 1
    content_type = "text"
    content_data = {"text": "Test content", "media_id": None}
    
    # Mock para session y resultados
    session_mock = AsyncMock()
    
    # Mock para Channel
    channel_mock = MagicMock()
    channel_mock.id = channel_id
    
    # Configurar session mock para simular queries
    session_result_mock = MagicMock()
    session_result_mock.scalars().first.return_value = channel_mock
    session_mock.execute.return_value = session_result_mock
    
    # Mock para el ID generado
    content_id = 101
    def refresh_side_effect(content):
        content.id = content_id
    session_mock.refresh.side_effect = refresh_side_effect
    
    # Mock para get_session
    get_session_mock = MagicMock()
    get_session_mock.return_value.__aenter__.return_value = None
    get_session_mock.return_value.__aexit__.return_value = None
    get_session_mock.return_value.__aiter__.return_value = [session_mock]
    
    # Ejecutar con el mock
    with patch('src.modules.channel.service.get_session', return_value=get_session_mock()):
        result = await channel_service.add_channel_content(channel_id, content_type, content_data)
    
    # Verificar resultado
    assert result == content_id
    
    # Verificar que se añadió el contenido a la sesión
    session_mock.add.assert_called_once()
    added_content = session_mock.add.call_args[0][0]
    assert isinstance(added_content, ChannelContent)
    assert added_content.channel_id == channel_id
    assert added_content.content_type == content_type
    assert added_content.content_data == content_data
    assert added_content.is_published == True  # Sin tiempo programado, se publica de inmediato
    
    # Verificar que se publicó el evento
    event_bus_mock.publish.assert_called_once()
    published_event = event_bus_mock.publish.call_args[0][0]
    assert isinstance(published_event, ChannelContentPublishedEvent)
    assert published_event.channel_id == channel_id
    assert published_event.content_id == content_id