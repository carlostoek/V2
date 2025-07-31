import pytest

from src.core.event_bus import EventBus
from src.modules.gamification.service import GamificationService
from src.modules.events import ReactionAddedEvent, UserStartedBotEvent

@pytest.mark.asyncio
async def test_gamification_service_awards_points_on_reaction():
    """
    Verifica que el GamificationService reacciona a un ReactionAddedEvent
    y otorga los puntos correspondientes.
    """
    # Arrange
    event_bus = EventBus()
    gamification_service = GamificationService(event_bus)
    await gamification_service.setup()

    user_id = 123
    message_id = 456
    points_to_award = 5
    event = ReactionAddedEvent(user_id, message_id, points_to_award)

    # Act
    await event_bus.publish(event)

    # Assert
    assert gamification_service.get_points(user_id) == points_to_award

@pytest.mark.asyncio
async def test_gamification_service_awards_welcome_points():
    """
    Verifica que el GamificationService otorga puntos de bienvenida
    cuando un usuario inicia el bot por primera vez.
    """
    # Arrange
    event_bus = EventBus()
    gamification_service = GamificationService(event_bus)
    await gamification_service.setup()

    user_id = 456
    event = UserStartedBotEvent(user_id, "testuser")

    # Act
    await event_bus.publish(event)

    # Assert
    assert gamification_service.get_points(user_id) == 10

@pytest.mark.asyncio
async def test_gamification_service_awards_welcome_points_only_once():
    """
    Verifica que el GamificationService otorga puntos de bienvenida solo una vez.
    """
    # Arrange
    event_bus = EventBus()
    gamification_service = GamificationService(event_bus)
    await gamification_service.setup()

    user_id = 789
    event = UserStartedBotEvent(user_id, "testuser")

    # Act
    await event_bus.publish(event) # Primera vez
    await event_bus.publish(event) # Segunda vez

    # Assert
    assert gamification_service.get_points(user_id) == 10
