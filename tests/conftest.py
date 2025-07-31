"""Test fixtures and configuration for Diana Bot V2."""

import sys
import os
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, AsyncGenerator, List, Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

# Ensure pytest-asyncio is installed
import pytest_asyncio


@pytest.fixture(scope="session", autouse=True)
def test_settings():
    """Configure test environment variables."""
    with patch.dict(
        "os.environ",
        {
            "USE_SQLITE": "True",
            "DATABASE_URL": "sqlite+aiosqlite:///:memory:",
            "CREATE_TABLES": "True",
            "BOT_TOKEN": "fake-token-for-tests",
            "PARSE_MODE": "HTML",
        },
    ):
        yield

@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provides a clean, isolated database session for each test function.
    Creates all tables before the test and drops them after.
    """
    from src.bot.database.engine import engine, Base, async_session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
def mock_bot():
    """
    Patches the Bot instance to avoid real Telegram API calls.
    Provides an AsyncMock object to simulate bot methods.
    """
    with patch("src.bot.core.bootstrap.Bot", new_callable=AsyncMock) as mock:
        yield mock

@pytest.fixture
def mock_event_bus() -> AsyncMock:
    """
    Provides a mocked EventBus for testing event-driven functionality.
    """
    mock = AsyncMock()
    mock.publish = AsyncMock()
    mock.subscribe = MagicMock()
    return mock

@pytest.fixture
def mock_central_config() -> MagicMock:
    """
    Provides a mocked CentralConfig for testing configuration-dependent code.
    """
    mock = MagicMock()
    
    # Setup default config values
    config_values = {
        "bot.token": "fake-token-for-tests",
        "bot.parse_mode": "HTML",
        "narrative.starting_fragment": "welcome_1",
        "gamification.welcome_points": 10,
        "admin.wait_time_minutes": 15,
    }
    
    # Create get method that returns values from the dict
    def mock_get(key_path, default=None):
        return config_values.get(key_path, default)
    
    # Create set method that updates the dict
    def mock_set(key_path, value):
        config_values[key_path] = value
    
    mock.get = MagicMock(side_effect=mock_get)
    mock.set = MagicMock(side_effect=mock_set)
    mock.get_all = MagicMock(return_value=config_values)
    
    return mock

@pytest.fixture
def mock_di_container(mock_event_bus, mock_central_config) -> MagicMock:
    """
    Provides a mocked DI container with all required services.
    """
    from src.bot.core.containers import ApplicationContainer
    
    # Create mock container
    container = MagicMock(spec=ApplicationContainer)
    
    # Setup core sub-container
    container.core = MagicMock()
    container.core.event_bus = mock_event_bus
    container.core.central_config = mock_central_config
    container.core.bot = AsyncMock()
    container.core.dispatcher = AsyncMock()
    
    # Setup services sub-container
    container.services = MagicMock()
    container.services.narrative_service = AsyncMock()
    container.services.gamification_service = AsyncMock()
    container.services.user_service = AsyncMock()
    container.services.emotional_service = AsyncMock()
    container.services.admin_service = AsyncMock()
    
    return container

@pytest.fixture
def sample_user() -> Dict[str, Any]:
    """
    Provides a sample user for testing.
    """
    return {
        "id": 123456789,
        "username": "test_user",
        "first_name": "Test",
        "last_name": "User",
        "is_vip": False,
        "level": 1,
        "created_at": datetime.now() - timedelta(days=7),
    }

@pytest.fixture
def sample_narrative_fragment() -> Dict[str, Any]:
    """
    Provides a sample narrative fragment for testing.
    """
    return {
        "key": "welcome_1",
        "title": "Bienvenido a Diana",
        "character": "Diana",
        "text": "Hola, soy Diana. Bienvenido a mi mundo.",
        "level_required": 1,
        "is_vip_only": False,
        "choices": [
            {
                "id": 1,
                "text": "Hola Diana, un placer conocerte",
                "target_fragment_key": "welcome_2",
                "required_items": None
            },
            {
                "id": 2,
                "text": "¿Qué es este lugar?",
                "target_fragment_key": "welcome_explanation",
                "required_items": None
            }
        ]
    }

@pytest.fixture
def sample_mission() -> Dict[str, Any]:
    """
    Provides a sample mission for testing.
    """
    return {
        "id": 1,
        "key": "daily_interactions",
        "title": "Interacciones Diarias",
        "description": "Interactúa con Diana para conocerla mejor",
        "mission_type": "daily",
        "category": "engagement",
        "level_required": 1,
        "is_vip_only": False,
        "objectives": [
            {
                "id": "obj_1",
                "type": "reactions",
                "required": 3,
                "description": "Reacciona a 3 mensajes"
            }
        ],
        "points_reward": 20,
        "item_rewards": None,
        "time_limit_hours": 24
    }

# Create factory fixtures for more complex test data
class UserFactory:
    @staticmethod
    def create(id=123456789, username="test_user", is_vip=False, level=1):
        """
        Creates a user dictionary with the specified parameters.
        """
        return {
            "id": id,
            "username": username,
            "first_name": f"Test_{username}",
            "last_name": "User",
            "is_vip": is_vip,
            "level": level,
            "created_at": datetime.now() - timedelta(days=7),
        }

@pytest.fixture
def user_factory() -> UserFactory:
    """
    Provides a factory for creating test users.
    """
    return UserFactory