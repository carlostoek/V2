import pytest
from unittest.mock import AsyncMock, MagicMock

from aiogram import types

@pytest.mark.asyncio
async def test_start_handler_without_token():
    """Verifica que el handler de start publica el evento correcto y envía el mensaje de bienvenida."""
    # Arrange
    message = AsyncMock(spec=types.Message)
    message.from_user = MagicMock(id=123, username="test_user")
    
    command = MagicMock()
    command.args = None
    
    event_bus = AsyncMock()
    event_bus.publish = AsyncMock()
    
    admin_service = MagicMock()
    admin_service.validate_token.return_value = None
    
    # Importación local para evitar problemas de carga de dependencias
    from src.bot.handlers.user.start import handle_start
    
    # Act
    await handle_start(message, command, event_bus, admin_service)
    
    # Assert
    event_bus.publish.assert_called_once()
    message.answer.assert_called_once()
    assert "¡Bienvenido a Diana V2!" in message.answer.call_args[0][0]