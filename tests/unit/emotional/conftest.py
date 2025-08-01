"""Test configuration for emotional system tests."""

import pytest
import asyncio
import sys
import os
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Set up test environment before any imports
os.environ.update({
    "BOT_TOKEN": "test_token_12345:ABCDEF_test_token_for_unit_tests",
    "DATABASE_URL": "sqlite+aiosqlite:///:memory:",
    "USE_SQLITE": "True",
    "DATABASE_ECHO": "False",
    "CREATE_TABLES": "True",
    "ADMIN_USER_IDS": "123456789",
    "VIP_CHANNEL_ID": "-1001234567890",
    "FREE_CHANNEL_ID": "-1001234567891",
    "ENABLE_ANALYTICS": "False",
    "ENABLE_BACKGROUND_TASKS": "False",
    "ENABLE_EMOTIONAL_SYSTEM": "True",
    "LOG_LEVEL": "DEBUG",
    "TASK_SCHEDULER_TIMEZONE": "UTC",
})


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment for all emotional tests."""
    # Ensure environment is set before any imports
    yield


@pytest.fixture
def event_bus_mock():
    """Mock for the event bus."""
    mock = AsyncMock()
    mock.subscribe = MagicMock()
    mock.publish = AsyncMock()
    return mock


@pytest.fixture
def mock_settings():
    """Mock settings for tests."""
    mock = MagicMock()
    mock.BOT_TOKEN = "test_token_12345:ABCDEF_test_token_for_unit_tests"
    mock.DATABASE_URL = "sqlite+aiosqlite:///:memory:"
    mock.USE_SQLITE = True
    mock.DATABASE_ECHO = False
    mock.CREATE_TABLES = True
    mock.ENABLE_EMOTIONAL_SYSTEM = True
    mock.admin_ids = {123456789}
    return mock


@pytest.fixture(autouse=True)
def patch_settings(mock_settings):
    """Automatically patch settings for all tests in this module."""
    with patch('src.bot.config.settings.settings', mock_settings):
        yield mock_settings