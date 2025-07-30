import pytest

from src.core.event_bus import EventBus
from src.modules.gamification.service import GamificationService, UserJoinedEvent

@pytest.mark.asyncio
async def test_gamification_service_integration_with_event_bus():
    """
    Verifica que el GamificationService se suscribe al EventBus
    y reacciona a los eventos correctamente.
    """
    # Arrange
    event_bus = EventBus()
    gamification_service = GamificationService(event_bus)
    await gamification_service.setup()  # El servicio se suscribe a los eventos

    user_id = 123
    event = UserJoinedEvent(user_id)

    # Act
    await event_bus.publish(event)

    # Assert
    assert gamification_service.points.get(user_id) == 10
