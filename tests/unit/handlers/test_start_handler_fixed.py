import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import os

# Definir variables de entorno necesarias para tests
os.environ["BOT_TOKEN"] = "test_token"
os.environ["DATABASE_URL"] = "postgresql+asyncpg://test:test@localhost:5432/testdb"

# Patch para evitar cargar la configuración de la base de datos
@pytest.fixture(autouse=True)
def mock_admin_service():
    with patch('src.modules.admin.service.AdminService') as mock:
        service = MagicMock()
        service.validate_token = MagicMock(return_value=None)
        service.get_tariff = MagicMock(return_value={"name": "Premium", "duration_days": 30})
        mock.return_value = service
        yield service

@pytest.fixture(autouse=True)
def mock_gamification_service():
    with patch('src.modules.gamification.service.GamificationService') as mock:
        service = MagicMock()
        service.get_points = MagicMock(return_value=10)
        mock.return_value = service
        yield service

@pytest.mark.asyncio
async def test_start_handler_basic():
    """Test básico del handler de start."""
    from aiogram import types
    
    # Arrange
    message = AsyncMock(spec=types.Message)
    message.from_user = MagicMock(id=123, username="test_user")
    message.answer = AsyncMock()
    
    command = MagicMock()
    command.args = None
    
    event_bus = AsyncMock()
    
    admin_service = MagicMock()
    admin_service.validate_token.return_value = None
    
    # Importar después de configurar los mocks
    from src.bot.handlers.user.start import handle_start
    
    # Act
    await handle_start(message, command, event_bus, admin_service)
    
    # Assert
    event_bus.publish.assert_called_once()
    message.answer.assert_called_once()
    
    # Verificar el contenido del mensaje
    call_args = message.answer.call_args
    assert call_args is not None
    assert "¡Bienvenido a Diana V2!" in call_args[0][0]