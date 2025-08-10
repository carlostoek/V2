
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock
from src.modules.channel.service import ChannelService
from src.modules.channel.events import ChannelJoinRequestEvent, ChannelJoinApprovedEvent

@pytest.fixture
def event_bus_mock():
    return AsyncMock()

@pytest.mark.asyncio
async def test_create_channel(event_bus_mock):
    """Tests creating a new channel."""
    service = ChannelService(event_bus_mock)
    
    # Mocking the database session
    service.get_session = MagicMock()
    
    # Simulate creating a new channel
    channel_id = await service.create_channel(
        telegram_id="-1001234567890",
        name="Test VIP Channel",
        description="A channel for testing purposes.",
        channel_type="vip"
    )
    
    assert channel_id is not None
    assert service.channels["-1001234567890"]["name"] == "Test VIP Channel"

@pytest.mark.asyncio
async def test_handle_join_request(event_bus_mock):
    """Tests handling a user's request to join a channel."""
    service = ChannelService(event_bus_mock)
    
    # Mocking the database session and initial data
    service.get_session = MagicMock()
    await service._load_initial_data()
    
    # Create a test channel
    await service.create_channel(
        telegram_id="-1001234567890",
        name="Test VIP Channel",
        description="A channel for testing purposes.",
        channel_type="vip"
    )
    
    # Simulate a join request event
    join_request = ChannelJoinRequestEvent(user_id=123, channel_id=1)
    await service.handle_join_request(join_request)
    
    # Verify that the approval event was published
    event_bus_mock.publish.assert_called_once()
    published_event = event_bus_mock.publish.call_args[0][0]
    assert isinstance(published_event, ChannelJoinApprovedEvent)
    assert published_event.user_id == 123
    assert published_event.channel_id == 1

if __name__ == "__main__":
    pytest.main()
