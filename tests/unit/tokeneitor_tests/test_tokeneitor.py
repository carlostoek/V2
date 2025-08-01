"""Tests para el servicio Tokeneitor."""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture
def event_bus_mock():
    """Mock para el event bus."""
    mock = AsyncMock()
    mock.subscribe = MagicMock()
    mock.publish = AsyncMock()
    return mock


@pytest.fixture
async def tokeneitor_service(event_bus_mock):
    """Fixture para el servicio Tokeneitor."""
    # Lazy import para evitar problemas de configuración
    from src.modules.token.tokeneitor import Tokeneitor
    
    service = Tokeneitor(event_bus_mock, bot_username="TestBot")
    await service.setup()
    return service


@pytest.mark.asyncio
async def test_create_tariff(tokeneitor_service, event_bus_mock):
    """Test que verifica la creación de una tarifa."""
    # Lazy imports
    from src.modules.token.events import TariffCreatedEvent
    from src.bot.database.models.token import Tariff
    channel_id = 1
    name = "Tarifa Premium"
    duration_days = 30
    price = 9.99
    admin_id = 123
    
    # Mock para session y resultados
    session_mock = AsyncMock()
    
    # Mock para Channel y Admin
    channel_mock = MagicMock()
    channel_mock.id = channel_id
    
    admin_mock = MagicMock()
    admin_mock.id = admin_id
    
    # Configurar session mock para simular queries
    session_result_mock = MagicMock()
    session_result_mock.scalars().first.side_effect = [
        channel_mock,  # Para channel_query
        admin_mock     # Para admin_query
    ]
    session_mock.execute.return_value = session_result_mock
    
    # Mock para el ID generado
    tariff_id = 1
    def refresh_side_effect(tariff):
        tariff.id = tariff_id
    session_mock.refresh.side_effect = refresh_side_effect
    
    # Mock para get_session
    get_session_mock = MagicMock()
    get_session_mock.return_value.__aenter__.return_value = None
    get_session_mock.return_value.__aexit__.return_value = None
    get_session_mock.return_value.__aiter__.return_value = [session_mock]
    
    # Ejecutar con el mock
    with patch('src.modules.token.tokeneitor.get_session', return_value=get_session_mock()):
        result = await tokeneitor_service.create_tariff(
            channel_id=channel_id,
            name=name,
            duration_days=duration_days,
            price=price,
            admin_id=admin_id
        )
    
    # Verificar resultado
    assert result == tariff_id
    
    # Verificar que se añadió la tarifa a la sesión
    session_mock.add.assert_called_once()
    added_tariff = session_mock.add.call_args[0][0]
    assert isinstance(added_tariff, Tariff)
    assert added_tariff.channel_id == channel_id
    assert added_tariff.name == name
    assert added_tariff.duration_days == duration_days
    assert added_tariff.price == price
    
    # Verificar que se publicó el evento
    event_bus_mock.publish.assert_called_once()
    published_event = event_bus_mock.publish.call_args[0][0]
    assert isinstance(published_event, TariffCreatedEvent)
    assert published_event.tariff_id == tariff_id
    assert published_event.channel_id == channel_id
    assert published_event.admin_id == admin_id


@pytest.mark.asyncio
async def test_generate_token(tokeneitor_service, event_bus_mock):
    """Test que verifica la generación de un token."""
    # Lazy imports
    from src.modules.token.events import TokenGeneratedEvent
    from src.bot.database.models.token import SubscriptionToken
    tariff_id = 1
    admin_id = 123
    
    # Mock para session y resultados
    session_mock = AsyncMock()
    
    # Mock para Tariff y Admin
    tariff_mock = MagicMock()
    tariff_mock.id = tariff_id
    tariff_mock.token_validity_days = 7
    
    admin_mock = MagicMock()
    admin_mock.id = admin_id
    
    # Configurar session mock para simular queries
    session_result_mock = MagicMock()
    session_result_mock.scalars().first.side_effect = [
        tariff_mock,  # Para tariff_query
        admin_mock    # Para admin_query
    ]
    session_mock.execute.return_value = session_result_mock
    
    # Mock para el ID generado
    token_id = 101
    def refresh_side_effect(token):
        token.id = token_id
    session_mock.refresh.side_effect = refresh_side_effect
    
    # Mock para get_session
    get_session_mock = MagicMock()
    get_session_mock.return_value.__aenter__.return_value = None
    get_session_mock.return_value.__aexit__.return_value = None
    get_session_mock.return_value.__aiter__.return_value = [session_mock]
    
    # Ejecutar con el mock
    with patch('src.modules.token.tokeneitor.get_session', return_value=get_session_mock()):
        with patch('src.modules.token.tokeneitor.secrets.token_urlsafe', return_value="test_token"):
            result = await tokeneitor_service.generate_token(
                tariff_id=tariff_id,
                admin_id=admin_id
            )
    
    # Verificar resultado
    assert result is not None
    assert "https://t.me/TestBot?start=token_test_token" == result
    
    # Verificar que se añadió el token a la sesión
    session_mock.add.assert_called_once()
    added_token = session_mock.add.call_args[0][0]
    assert isinstance(added_token, SubscriptionToken)
    assert added_token.tariff_id == tariff_id
    assert added_token.generated_by == admin_id
    assert added_token.token == "test_token"
    assert added_token.is_used == False
    
    # Verificar que se publicó el evento
    event_bus_mock.publish.assert_called_once()
    published_event = event_bus_mock.publish.call_args[0][0]
    assert isinstance(published_event, TokenGeneratedEvent)
    assert published_event.token_id == token_id
    assert published_event.tariff_id == tariff_id
    assert published_event.admin_id == admin_id


@pytest.mark.asyncio
async def test_verify_token(tokeneitor_service, event_bus_mock):
    """Test que verifica el canje de un token."""
    # Lazy imports
    from src.modules.token.events import TokenRedeemedEvent
    from src.bot.database.models.channel import ChannelMembership
    token_value = "test_token"
    user_id = 456
    token_id = 101
    channel_id = 1
    tariff_id = 1
    
    # Mock para session y resultados
    session_mock = AsyncMock()
    
    # Mock para User
    user_mock = MagicMock()
    user_mock.id = user_id
    
    # Mock para Channel
    channel_mock = MagicMock()
    channel_mock.id = channel_id
    channel_mock.telegram_id = "test_channel"
    channel_mock.name = "Test Channel"
    
    # Mock para Tariff
    tariff_mock = MagicMock()
    tariff_mock.id = tariff_id
    tariff_mock.name = "Premium"
    tariff_mock.duration_days = 30
    tariff_mock.channel = channel_mock
    
    # Mock para Token
    token_mock = MagicMock()
    token_mock.id = token_id
    token_mock.tariff = tariff_mock
    token_mock.tariff_id = tariff_id
    token_mock.is_used = False
    token_mock.expires_at = datetime.now() + timedelta(days=7)
    
    # Configurar session mock para simular queries
    user_result_mock = MagicMock()
    user_result_mock.scalars().first.return_value = user_mock
    
    token_result_mock = MagicMock()
    token_result_mock.scalars().first.return_value = token_mock
    
    membership_result_mock = MagicMock()
    membership_result_mock.scalars().first.return_value = None  # No existe membresía previa
    
    session_mock.execute.side_effect = [user_result_mock, token_result_mock, membership_result_mock]
    
    # Mock para get_session
    get_session_mock = MagicMock()
    get_session_mock.return_value.__aenter__.return_value = None
    get_session_mock.return_value.__aexit__.return_value = None
    get_session_mock.return_value.__aiter__.return_value = [session_mock]
    
    # Ejecutar con el mock
    with patch('src.modules.token.tokeneitor.get_session', return_value=get_session_mock()):
        result = await tokeneitor_service.verify_token(
            token=token_value,
            user_id=user_id
        )
    
    # Verificar resultado
    assert result is not None
    assert result["channel_id"] == channel_id
    assert result["telegram_id"] == "test_channel"
    assert result["tariff_name"] == "Premium"
    assert result["duration_days"] == 30
    
    # Verificar que se actualizó el token
    assert token_mock.is_used == True
    assert token_mock.used_by == user_id
    
    # Verificar que se añadió la membresía a la sesión
    session_mock.add.assert_called_once()
    added_membership = session_mock.add.call_args[0][0]
    assert isinstance(added_membership, ChannelMembership)
    assert added_membership.user_id == user_id
    assert added_membership.channel_id == channel_id
    assert added_membership.status == "active"
    assert "is_vip" in added_membership.user_metadata
    assert added_membership.user_metadata["is_vip"] == True
    
    # Verificar que se publicó el evento
    event_bus_mock.publish.assert_called_once()
    published_event = event_bus_mock.publish.call_args[0][0]
    assert isinstance(published_event, TokenRedeemedEvent)
    assert published_event.token_id == token_id
    assert published_event.user_id == user_id
    assert published_event.channel_id == channel_id


@pytest.mark.asyncio
async def test_get_channel_tariffs(tokeneitor_service):
    """Test que verifica la obtención de tarifas de un canal."""
    channel_id = 1
    
    # Mock para session y resultados
    session_mock = AsyncMock()
    
    # Mock para Channel
    channel_mock = MagicMock()
    channel_mock.id = channel_id
    
    # Mock para Tariffs
    tariff1 = MagicMock()
    tariff1.id = 1
    tariff1.name = "Básico"
    tariff1.duration_days = 30
    tariff1.price = 4.99
    tariff1.token_validity_days = 7
    tariff1.description = "Plan básico mensual"
    
    tariff2 = MagicMock()
    tariff2.id = 2
    tariff2.name = "Premium"
    tariff2.duration_days = 90
    tariff2.price = 9.99
    tariff2.token_validity_days = 14
    tariff2.description = "Plan premium trimestral"
    
    # Configurar session mock para simular queries
    channel_result_mock = MagicMock()
    channel_result_mock.scalars().first.return_value = channel_mock
    
    tariffs_result_mock = MagicMock()
    tariffs_result_mock.scalars().all.return_value = [tariff1, tariff2]
    
    session_mock.execute.side_effect = [channel_result_mock, tariffs_result_mock]
    
    # Mock para get_session
    get_session_mock = MagicMock()
    get_session_mock.return_value.__aenter__.return_value = None
    get_session_mock.return_value.__aexit__.return_value = None
    get_session_mock.return_value.__aiter__.return_value = [session_mock]
    
    # Ejecutar con el mock
    with patch('src.modules.token.tokeneitor.get_session', return_value=get_session_mock()):
        result = await tokeneitor_service.get_channel_tariffs(channel_id)
    
    # Verificar resultado
    assert len(result) == 2
    
    # Verificar tarifa 1
    assert result[0]["id"] == 1
    assert result[0]["name"] == "Básico"
    assert result[0]["duration_days"] == 30
    assert result[0]["price"] == 4.99
    
    # Verificar tarifa 2
    assert result[1]["id"] == 2
    assert result[1]["name"] == "Premium"
    assert result[1]["duration_days"] == 90
    assert result[1]["price"] == 9.99