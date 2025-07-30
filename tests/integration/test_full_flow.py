import pytest

from src.core.event_bus import EventBus
from src.infrastructure.telegram.listener import TelegramListener
from src.modules.gamification.service import GamificationService
from src.modules.narrative.service import NarrativeService

@pytest.mark.asyncio
async def test_full_reaction_to_story_flow():
    """
    Verifica el flujo completo: una reacción de Telegram otorga puntos
    y desbloquea un fragmento de historia.
    """
    # Arrange: Configurar todo el sistema en memoria
    event_bus = EventBus()
    gamification_service = GamificationService(event_bus)
    narrative_service = NarrativeService(event_bus)
    telegram_listener = TelegramListener(event_bus)

    await gamification_service.setup()
    await narrative_service.setup()

    user_id = 777
    message_id = 101

    # Act: Simular el evento inicial que desencadena el flujo
    await telegram_listener.simulate_reaction(user_id, message_id)

    # Assert: Verificar el estado final de cada servicio
    # 1. Gamificación: ¿Se otorgaron los puntos?
    assert gamification_service.points.get(user_id) == 5

    # 2. Narrativa: ¿Se asignó la historia correcta?
    assert narrative_service.story_fragments_to_send.get(user_id) == "intro_story_fragment_1"
