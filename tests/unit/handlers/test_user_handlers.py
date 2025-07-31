import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from aiogram import types
from aiogram.fsm.context import FSMContext

# Importar los handlers directamente
from src.bot.handlers.user.start import handle_start
from src.bot.handlers.user.help import handle_help
from src.bot.handlers.user.profile import handle_profile_command, handle_profile_callback

# Usar fixtures del conftest.py
@pytest.fixture
def mock_message():
    message = AsyncMock(spec=types.Message)
    message.from_user = MagicMock(id=123, username="test_user")
    return message

@pytest.fixture
def mock_query():
    query = AsyncMock(spec=types.CallbackQuery)
    query.from_user = MagicMock(id=123, username="test_user")
    query.message = AsyncMock(spec=types.Message)
    return query

@pytest.fixture
def mock_command():
    command = MagicMock()
    command.args = None
    return command

@pytest.mark.asyncio
async def test_handle_start_without_token(mock_message, mock_command, mock_event_bus, mock_admin_service):
    """Verifica que el handler de start publica el evento correcto y envía el mensaje de bienvenida."""
    await handle_start(mock_message, mock_command, mock_event_bus, mock_admin_service)
    
    # Verificar que se publicó el evento correcto
    mock_event_bus.publish.assert_called_once()
    
    # Verificar que se envió el mensaje de bienvenida
    mock_message.answer.assert_called_once()
    assert "¡Bienvenido a Diana V2!" in mock_message.answer.call_args[0][0]

@pytest.mark.asyncio
async def test_handle_start_with_valid_token(mock_message, mock_event_bus, mock_admin_service):
    """Verifica que el handler de start valida correctamente un token VIP."""
    command = MagicMock(args="valid_token")
    
    # Configurar el servicio para devolver un token válido
    tariff = {"id": 1, "name": "Premium", "price": 9.99, "duration_days": 30}
    mock_admin_service.validate_token.return_value = {"tariff_id": 1}
    mock_admin_service.get_tariff.return_value = tariff
    
    await handle_start(mock_message, command, mock_event_bus, mock_admin_service)
    
    # Verificar que se llamó al servicio para validar el token
    mock_admin_service.validate_token.assert_called_once_with("valid_token", 123)
    
    # Verificar que se envió el mensaje de confirmación
    mock_message.answer.assert_called_once()
    assert "¡Felicidades!" in mock_message.answer.call_args[0][0]
    assert "Premium" in mock_message.answer.call_args[0][0]

@pytest.mark.asyncio
async def test_handle_start_with_invalid_token(mock_message, mock_event_bus, mock_admin_service):
    """Verifica que el handler de start maneja correctamente un token inválido."""
    command = MagicMock(args="invalid_token")
    
    # Configurar el servicio para devolver un token inválido
    mock_admin_service.validate_token.return_value = None
    
    await handle_start(mock_message, command, mock_event_bus, mock_admin_service)
    
    # Verificar que se llamó al servicio para validar el token
    mock_admin_service.validate_token.assert_called_once_with("invalid_token", 123)
    
    # Verificar que se envió el mensaje de error
    mock_message.answer.assert_called_once()
    assert "no es válido" in mock_message.answer.call_args[0][0]

@pytest.mark.asyncio
async def test_handle_help(mock_message):
    """Verifica que el handler de help envía el mensaje de ayuda correcto."""
    await handle_help(mock_message)
    
    # Verificar que se envió el mensaje de ayuda
    mock_message.answer.assert_called_once()
    assert "Ayuda de Diana V2" in mock_message.answer.call_args[0][0]
    assert "Comandos básicos" in mock_message.answer.call_args[0][0]

@pytest.mark.asyncio
async def test_handle_profile_command(mock_message, mock_gamification_service):
    """Verifica que el handler de profile command muestra los puntos correctos."""
    await handle_profile_command(mock_message, mock_gamification_service)
    
    # Verificar que se consultaron los puntos del usuario
    mock_gamification_service.get_points.assert_called_once_with(123)
    
    # Verificar que se envió el mensaje de perfil
    mock_message.answer.assert_called_once()
    assert "Tu Perfil" in mock_message.answer.call_args[0][0]
    assert "Puntos: 10" in mock_message.answer.call_args[0][0]

@pytest.mark.asyncio
async def test_handle_profile_callback(mock_query, mock_gamification_service):
    """Verifica que el handler de profile callback muestra los puntos correctos."""
    await handle_profile_callback(mock_query, mock_gamification_service)
    
    # Verificar que se consultaron los puntos del usuario
    mock_gamification_service.get_points.assert_called_once_with(123)
    
    # Verificar que se editó el mensaje
    mock_query.message.edit_text.assert_called_once()
    assert "Tu Perfil" in mock_query.message.edit_text.call_args[0][0]
    assert "Puntos: 10" in mock_query.message.edit_text.call_args[0][0]
    
    # Verificar que se respondió al callback
    mock_query.answer.assert_called_once()