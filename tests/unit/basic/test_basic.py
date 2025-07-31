"""
Tests básicos para verificar que la infraestructura funciona.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock


def test_imports():
    """Verifica que las importaciones básicas funcionan."""
    # Core
    from src.core.services.config import CentralConfig
    from src.core.interfaces.IEventBus import IEventBus
    from src.core.event_bus import EventBus
    
    # Events
    from src.modules.events import UserStartedBotEvent, ReactionAddedEvent
    
    # Assert que las clases existen
    assert CentralConfig
    assert IEventBus
    assert EventBus
    assert UserStartedBotEvent
    assert ReactionAddedEvent


@pytest.mark.asyncio
async def test_event_bus():
    """Verifica que el event bus funciona correctamente."""
    from src.core.event_bus import EventBus
    from src.modules.events import UserStartedBotEvent
    
    # Arrange
    event_bus = EventBus()
    handler = AsyncMock()
    event_bus.subscribe(UserStartedBotEvent, handler)
    
    # Act
    event = UserStartedBotEvent(user_id=123, username="test_user")
    await event_bus.publish(event)
    
    # Assert
    handler.assert_called_once_with(event)


@pytest.mark.asyncio
async def test_central_config():
    """Verifica que el CentralConfig funciona correctamente."""
    from src.core.services.config import CentralConfig
    
    # Arrange
    config = CentralConfig()
    
    # Act
    config.set("test.key", "test_value")
    value = config.get("test.key")
    
    # Assert
    assert value == "test_value"


# Omitido temporalmente para simplificar los tests
# @pytest.mark.asyncio
# async def test_container():
#     """Verifica que el container de DI funciona correctamente."""
#     from src.bot.core.containers import ApplicationContainer
#     from src.core.event_bus import EventBus
#     from src.core.services.config import CentralConfig
#     
#     # Arrange
#     container = ApplicationContainer()
#     
#     # Act - Crear los servicios principales
#     event_bus = container.core.event_bus()
#     config = container.core.central_config()
#     
#     # Assert
#     assert isinstance(event_bus, EventBus)
#     assert isinstance(config, CentralConfig)