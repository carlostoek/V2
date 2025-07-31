import pytest

from src.core.event_bus import EventBus
from src.modules.narrative.service import NarrativeService
from src.modules.events import UserStartedBotEvent

@pytest.mark.asyncio
async def test_narrative_service_delivers_welcome_message():
    """
    Verifica que el NarrativeService entrega un mensaje de bienvenida
    cuando un usuario inicia el bot por primera vez.
    """
    # Arrange
    event_bus = EventBus()
    narrative_service = NarrativeService(event_bus)
    await narrative_service.setup()

    user_id = 123
    event = UserStartedBotEvent(user_id, "testuser")

    # Act
    await event_bus.publish(event)

    # Assert
    assert narrative_service.story_fragments_to_send.get(user_id) == "welcome_story_fragment"
