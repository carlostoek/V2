import pytest
import unittest.mock as mock

from src.core.event_bus import EventBus
from src.modules.gamification.service import GamificationService
from src.modules.narrative.service import NarrativeService
from src.infrastructure.telegram.listener import TelegramListener
from src.modules.events import (
    ReactionAddedEvent, 
    PointsAwardedEvent, 
    PieceUnlockedEvent, 
    NarrativeProgressionEvent,
    MissionCompletedEvent,
    LevelUpEvent
)

@pytest.mark.asyncio
async def test_full_integration_flow():
    """
    Verifica el flujo completo desde una reaccion en Telegram hasta
    la asignacion de puntos y la entrega de un fragmento narrativo.
    
    Flujo:
    1. Usuario reacciona a mensaje en canal (simulado)
    2. GamificationService otorga puntos
    3. NarrativeService debe actualizar el fragmento de historia
    """
    # Arrange
    event_bus = EventBus()
    
    # Servicios
    gamification_service = GamificationService(event_bus)
    
    # Mock para el acceso a la base de datos en NarrativeService
    with mock.patch('src.modules.narrative.service.get_session'):
        # Mock para el método _init_starting_fragment
        with mock.patch('src.modules.narrative.service.NarrativeService._init_starting_fragment'):
            # Mock para el método _ensure_user_narrative_state
            with mock.patch('src.modules.narrative.service.NarrativeService._ensure_user_narrative_state'):
                # Mock para el método _get_appropriate_fragment
                with mock.patch('src.modules.narrative.service.NarrativeService._get_appropriate_fragment', return_value="reaction_fragment_special"):
                    # Mock para el método _maybe_unlock_lore_piece
                    with mock.patch('src.modules.narrative.service.NarrativeService._maybe_unlock_lore_piece', return_value=False):
                        narrative_service = NarrativeService(event_bus)
                        telegram_listener = TelegramListener(event_bus)
                        
                        # Rastrear eventos emitidos
                        emitted_events = []
                        original_publish = event_bus.publish
                        
                        async def track_events(event):
                            emitted_events.append(event)
                            await original_publish(event)
                        
                        event_bus.publish = track_events
                        
                        # Configurar servicios
                        await gamification_service.setup()
                        await narrative_service.setup()
                        
                        # Usuario y mensaje de prueba
                        user_id = 12345
                        message_id = 67890
                        
                        # Act
                        await telegram_listener.simulate_reaction(user_id, message_id)
                        
                        # Assert
                        # Verificar que el usuario recibio puntos
                        assert gamification_service.get_points(user_id) == 5
                        
                        # Verificar que se asigno un fragmento de historia
                        assert user_id in narrative_service.story_fragments_to_send
                        assert narrative_service.story_fragments_to_send[user_id] == "reaction_fragment_special"
                        
                        # Verificar eventos emitidos
                        event_types = [type(event) for event in emitted_events]
                        assert ReactionAddedEvent in event_types
                        assert PointsAwardedEvent in event_types

@pytest.mark.asyncio
async def test_narrative_mission_integration():
    """
    Verifica la integración entre misiones completadas y el sistema narrativo.
    
    Flujo:
    1. Usuario completa una misión
    2. Se otorgan puntos
    3. Se asigna un fragmento narrativo
    4. Se desbloquea una pista narrativa
    """
    # Arrange
    event_bus = EventBus()
    
    # Servicios
    gamification_service = GamificationService(event_bus)
    
    # Mock para el acceso a la base de datos en NarrativeService
    with mock.patch('src.modules.narrative.service.get_session'):
        # Mock para el método _init_starting_fragment
        with mock.patch('src.modules.narrative.service.NarrativeService._init_starting_fragment'):
            # Mock para el método _get_appropriate_fragment
            with mock.patch('src.modules.narrative.service.NarrativeService._get_appropriate_fragment', return_value="mission_fragment_123"):
                # Mock para el método _maybe_unlock_lore_piece que siempre devuelve True
                with mock.patch('src.modules.narrative.service.NarrativeService._maybe_unlock_lore_piece', return_value=True):
                    narrative_service = NarrativeService(event_bus)
                    
                    # Rastrear eventos emitidos
                    emitted_events = []
                    original_publish = event_bus.publish
                    
                    async def track_events(event):
                        emitted_events.append(event)
                        await original_publish(event)
                    
                    event_bus.publish = track_events
                    
                    # Configurar servicios
                    await gamification_service.setup()
                    await narrative_service.setup()
                    
                    # Usuario y misión de prueba
                    user_id = 12345
                    mission_id = "daily_mission_1"
                    
                    # Act
                    # 1. Emitir evento de misión completada
                    mission_event = MissionCompletedEvent(
                        user_id=user_id,
                        mission_id=mission_id,
                        completion_time="2023-01-01T12:00:00",
                        reward_points=10
                    )
                    await event_bus.publish(mission_event)
                    
                    # 2. Emitir evento de puntos otorgados
                    points_event = PointsAwardedEvent(
                        user_id=user_id,
                        points=10,
                        source_event="MissionCompletedEvent"
                    )
                    await event_bus.publish(points_event)
                    
                    # Assert
                    # Verificar que se asignó un fragmento narrativo
                    assert user_id in narrative_service.story_fragments_to_send
                    assert narrative_service.story_fragments_to_send[user_id] == "mission_fragment_123"
                    
                    # Verificar eventos emitidos (debe incluir PieceUnlockedEvent)
                    event_types = [type(event) for event in emitted_events]
                    assert MissionCompletedEvent in event_types
                    assert PointsAwardedEvent in event_types
                    assert PieceUnlockedEvent in event_types

@pytest.mark.asyncio
async def test_narrative_progression_integration():
    """
    Verifica la integración entre la progresión narrativa y el sistema de niveles.
    
    Flujo:
    1. Usuario avanza en la narrativa
    2. Se emite evento de progresión narrativa
    3. Usuario sube de nivel
    4. Se asigna fragmento especial por subir de nivel
    """
    # Arrange
    event_bus = EventBus()
    
    # Mock para el acceso a la base de datos en NarrativeService
    with mock.patch('src.modules.narrative.service.get_session'):
        # Mock para el método _init_starting_fragment
        with mock.patch('src.modules.narrative.service.NarrativeService._init_starting_fragment'):
            # Mock para el método _get_level_specific_fragment
            with mock.patch('src.modules.narrative.service.NarrativeService._get_level_specific_fragment', return_value="level_up_fragment_2"):
                # Mock para el método _maybe_unlock_lore_piece
                with mock.patch('src.modules.narrative.service.NarrativeService._maybe_unlock_lore_piece', return_value=True):
                    narrative_service = NarrativeService(event_bus)
                    
                    # Rastrear eventos emitidos
                    emitted_events = []
                    original_publish = event_bus.publish
                    
                    async def track_events(event):
                        emitted_events.append(event)
                        await original_publish(event)
                    
                    event_bus.publish = track_events
                    
                    # Configurar servicios
                    await narrative_service.setup()
                    
                    # Usuario de prueba
                    user_id = 12345
                    
                    # Act
                    # 1. Emitir evento de progresión narrativa
                    progression_event = NarrativeProgressionEvent(
                        user_id=user_id,
                        fragment_id="story_fragment_final",
                        choices_made={"fragment_1": [1, 2], "fragment_2": [3]}
                    )
                    await event_bus.publish(progression_event)
                    
                    # 2. Emitir evento de subida de nivel
                    level_up_event = LevelUpEvent(
                        user_id=user_id,
                        new_level=2,
                        rewards={"besitos": 100, "items": ["badge_level_2"]}
                    )
                    await event_bus.publish(level_up_event)
                    
                    # Assert
                    # Verificar que se asignó un fragmento por subir de nivel
                    assert user_id in narrative_service.story_fragments_to_send
                    assert narrative_service.story_fragments_to_send[user_id] == "level_up_fragment_2"
                    
                    # Verificar eventos emitidos (debe incluir PieceUnlockedEvent)
                    event_types = [type(event) for event in emitted_events]
                    assert NarrativeProgressionEvent in event_types
                    assert LevelUpEvent in event_types
                    assert PieceUnlockedEvent in event_types