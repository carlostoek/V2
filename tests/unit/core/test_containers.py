"""Tests for the dependency injection container."""

import pytest
from unittest.mock import patch

from src.bot.core.containers import container, ApplicationContainer
from src.core.event_bus import EventBus
from src.core.services.config import CentralConfig


@pytest.mark.asyncio
async def test_container_initialization():
    """Test that the container is properly initialized."""
    # The container should be an instance of ApplicationContainer
    assert isinstance(container, ApplicationContainer)
    
    # The core container should have the essential services
    with patch.dict("os.environ", {"BOT_TOKEN": "test-token"}):
        # Create a new container for this test
        test_container = ApplicationContainer()
        
        # Access core services to ensure they are created
        event_bus = test_container.core.event_bus()
        central_config = test_container.core.central_config()
        
        # Verify instances
        assert isinstance(event_bus, EventBus)
        assert isinstance(central_config, CentralConfig)


@pytest.mark.asyncio
async def test_service_dependencies():
    """Test that services are created with the correct dependencies."""
    with patch.dict("os.environ", {"BOT_TOKEN": "test-token"}):
        # Create a new container for this test
        test_container = ApplicationContainer()
        
        # Get core services
        event_bus = test_container.core.event_bus()
        
        # Get application services
        narrative_service = test_container.services.narrative_service()
        gamification_service = test_container.services.gamification_service()
        
        # Verify dependencies
        assert narrative_service._event_bus is event_bus
        assert gamification_service._event_bus is event_bus


@pytest.mark.asyncio
async def test_config_loading():
    """Test that the configuration is loaded properly."""
    with patch.dict("os.environ", {
        "BOT_TOKEN": "test-token-from-env",
        "PARSE_MODE": "Markdown"
    }):
        # Create a new container for this test
        test_container = ApplicationContainer()
        
        # Access the config through central_config
        central_config = test_container.core.central_config()
        
        # Verify config values
        assert central_config.get("bot.token") == "test-token-from-env"
        assert central_config.get("bot.parse_mode") == "Markdown"


@pytest.mark.asyncio
async def test_container_singleton_services():
    """Test that singleton services are properly reused."""
    with patch.dict("os.environ", {"BOT_TOKEN": "test-token"}):
        # Create a new container for this test
        test_container = ApplicationContainer()
        
        # Get core services multiple times
        event_bus1 = test_container.core.event_bus()
        event_bus2 = test_container.core.event_bus()
        central_config1 = test_container.core.central_config()
        central_config2 = test_container.core.central_config()
        
        # Verify instances are the same (singletons)
        assert event_bus1 is event_bus2
        assert central_config1 is central_config2
        
        # But factory services should be different
        narrative_service1 = test_container.services.narrative_service()
        narrative_service2 = test_container.services.narrative_service()
        
        # Factory providers create new instances each time
        assert narrative_service1 is not narrative_service2