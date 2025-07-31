import os
import pytest
from unittest.mock import MagicMock, AsyncMock

# Configurar variables de entorno necesarias para los tests
os.environ["BOT_TOKEN"] = "test_token"
os.environ["DATABASE_URL"] = "postgresql+asyncpg://test:test@localhost:5432/testdb"

# Mock para AdminService
@pytest.fixture
def mock_admin_service():
    admin_service = MagicMock()
    admin_service.validate_token = MagicMock(return_value=None)
    admin_service.get_tariff = MagicMock(return_value={"name": "Test", "duration_days": 30})
    admin_service.get_free_channel_id = MagicMock(return_value=123456789)
    return admin_service

# Mock para GamificationService
@pytest.fixture
def mock_gamification_service():
    gamification_service = MagicMock()
    gamification_service.get_points = MagicMock(return_value=10)
    return gamification_service

# Mock para EventBus
@pytest.fixture
def mock_event_bus():
    event_bus = AsyncMock()
    event_bus.publish = AsyncMock()
    event_bus.subscribe = MagicMock()
    return event_bus