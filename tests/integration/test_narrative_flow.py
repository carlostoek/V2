import pytest
import unittest.mock as mock
from datetime import datetime

from src.core.event_bus import EventBus
from src.modules.narrative.service import NarrativeService
from src.modules.events import (
    UserStartedBotEvent, 
    PointsAwardedEvent, 
    NarrativeProgressionEvent,
    PieceUnlockedEvent,
    MissionCompletedEvent
)
from src.bot.database.models.narrative import StoryFragment, NarrativeChoice, UserNarrativeState
from src.bot.database.models.user import User

@pytest.mark.asyncio
async def test_narrative_service_delivers_welcome_message():
    """
    Verifica que el NarrativeService entrega un mensaje de bienvenida
    cuando un usuario inicia el bot por primera vez.
    """
    # Arrange
    event_bus = EventBus()
    narrative_service = NarrativeService(event_bus)
    
    # Mock para el método _init_starting_fragment
    with mock.patch.object(narrative_service, '_init_starting_fragment') as mock_init:
        mock_init.return_value = None
        narrative_service._starting_fragment_key = "welcome_story_fragment"
        
        # Mock para el método _ensure_user_narrative_state
        with mock.patch.object(narrative_service, '_ensure_user_narrative_state') as mock_ensure:
            mock_ensure.return_value = None
            
            await narrative_service.setup()
            
            user_id = 123
            event = UserStartedBotEvent(user_id, "testuser")
            
            # Act
            await event_bus.publish(event)
            
            # Assert
            assert narrative_service.story_fragments_to_send.get(user_id) == "welcome_story_fragment"
            mock_ensure.assert_called_once_with(user_id, "welcome_story_fragment")

@pytest.mark.asyncio
async def test_handle_points_awarded_for_reaction():
    """
    Verifica que el NarrativeService responde correctamente cuando
    se otorgan puntos por una reacción.
    """
    # Arrange
    event_bus = EventBus()
    narrative_service = NarrativeService(event_bus)
    
    # Mock para el método _get_appropriate_fragment
    with mock.patch.object(narrative_service, '_get_appropriate_fragment') as mock_get_fragment:
        mock_get_fragment.return_value = "reaction_fragment_123"
        
        # Mock para el método _maybe_unlock_lore_piece
        with mock.patch.object(narrative_service, '_maybe_unlock_lore_piece') as mock_unlock:
            mock_unlock.return_value = True
            
            await narrative_service.setup()
            
            user_id = 123
            event = PointsAwardedEvent(user_id, 5, "ReactionAddedEvent")
            
            # Act
            await event_bus.publish(event)
            
            # Assert
            assert narrative_service.story_fragments_to_send.get(user_id) == "reaction_fragment_123"
            mock_get_fragment.assert_called_once_with(user_id, "reaction")
            mock_unlock.assert_called_once_with(user_id, "reaction")

@pytest.mark.asyncio
async def test_handle_mission_completed():
    """
    Verifica que el NarrativeService responde correctamente cuando
    se completa una misión.
    """
    # Arrange
    event_bus = EventBus()
    narrative_service = NarrativeService(event_bus)
    
    # Mock para el método _get_appropriate_fragment
    with mock.patch.object(narrative_service, '_get_appropriate_fragment') as mock_get_fragment:
        mock_get_fragment.return_value = "mission_fragment_456"
        
        # Mock para el método _maybe_unlock_lore_piece
        with mock.patch.object(narrative_service, '_maybe_unlock_lore_piece') as mock_unlock:
            mock_unlock.return_value = True
            
            await narrative_service.setup()
            
            user_id = 123
            mission_id = "daily_mission_1"
            completion_time = datetime.now().isoformat()
            event = MissionCompletedEvent(user_id, mission_id, completion_time, 10)
            
            # Act
            await narrative_service.handle_mission_completed(event)
            
            # Assert
            assert narrative_service.story_fragments_to_send.get(user_id) == "mission_fragment_456"
            mock_get_fragment.assert_called_once_with(user_id, "mission")
            mock_unlock.assert_called_once_with(user_id, "mission", high_chance=True)

@pytest.mark.asyncio
async def test_unlock_lore_piece_emits_event():
    """
    Verifica que cuando se desbloquea una pista narrativa,
    se emite el evento correspondiente.
    """
    # Arrange
    event_bus = EventBus()
    narrative_service = NarrativeService(event_bus)
    
    # Rastrear eventos emitidos
    emitted_events = []
    
    # Mock para el bus de eventos
    async def mock_publish(event):
        emitted_events.append(event)
    
    event_bus.publish = mock_publish
    
    # Mock para la función random que siempre devuelve 0.1 (menor que cualquier chance)
    with mock.patch('random.random', return_value=0.1):
        # Mock para el acceso a la base de datos
        with mock.patch('src.modules.narrative.service.get_session') as mock_get_session:
            # Crear un generador mock para simular async for
            mock_session = mock.AsyncMock()
            mock_session_gen = mock.AsyncMock()
            mock_session_gen.__aiter__.return_value = [mock_session]
            mock_get_session.return_value = mock_session_gen
            
            # Mock para la consulta y resultado
            mock_result = mock.AsyncMock()
            mock_result.scalars().first.return_value = mock.AsyncMock(
                narrative_items={"lore_pieces": {}}
            )
            mock_session.execute.return_value = mock_result
            
            user_id = 123
            context_type = "reaction"
            
            # Act
            result = await narrative_service._maybe_unlock_lore_piece(user_id, context_type)
            
            # Assert
            assert result is True
            assert len(emitted_events) == 1
            assert isinstance(emitted_events[0], PieceUnlockedEvent)
            assert emitted_events[0].user_id == user_id
            assert emitted_events[0].unlock_method == context_type

@pytest.mark.asyncio
async def test_make_narrative_choice_emits_event():
    """
    Verifica que cuando un usuario toma una decisión narrativa,
    se emite el evento correspondiente.
    """
    # Arrange
    event_bus = EventBus()
    narrative_service = NarrativeService(event_bus)
    
    # Rastrear eventos emitidos
    emitted_events = []
    
    # Mock para el bus de eventos
    async def mock_publish(event):
        emitted_events.append(event)
    
    event_bus.publish = mock_publish
    
    # Mock para el acceso a la base de datos
    with mock.patch('src.modules.narrative.service.get_session') as mock_get_session:
        # Crear un generador mock para simular async for
        mock_session = mock.AsyncMock()
        mock_session_gen = mock.AsyncMock()
        mock_session_gen.__aiter__.return_value = [mock_session]
        mock_get_session.return_value = mock_session_gen
        
        # Mock para la consulta y resultado de la opción
        choice = mock.Mock()
        choice.id = 456
        choice.fragment.key = "fragment_1"
        choice.target_fragment_key = "fragment_2"
        
        mock_choice_result = mock.AsyncMock()
        mock_choice_result.scalars().first.return_value = choice
        
        # Mock para la consulta y resultado del estado narrativo
        state = mock.Mock()
        state.user_id = 123
        state.current_fragment_key = "fragment_1"
        state.decisions_made = {}
        state.visited_fragments = ["fragment_1"]
        
        mock_state_result = mock.AsyncMock()
        mock_state_result.scalars().first.return_value = state
        
        # Configurar las llamadas a execute para devolver los resultados adecuados
        mock_session.execute.side_effect = [mock_choice_result, mock_state_result]
        
        user_id = 123
        choice_id = 456
        
        # Act
        result = await narrative_service.make_narrative_choice(user_id, choice_id)
        
        # Assert
        assert result is True
        assert len(emitted_events) == 1
        assert isinstance(emitted_events[0], NarrativeProgressionEvent)
        assert emitted_events[0].user_id == user_id
        assert emitted_events[0].fragment_id == "fragment_2"
        assert "fragment_1" in emitted_events[0].choices_made

@pytest.mark.asyncio
async def test_get_user_fragment():
    """
    Verifica que el método get_user_fragment devuelve correctamente
    el fragmento actual del usuario con sus opciones.
    """
    # Arrange
    event_bus = EventBus()
    narrative_service = NarrativeService(event_bus)
    
    # Mock para el acceso a la base de datos
    with mock.patch('src.modules.narrative.service.get_session') as mock_get_session:
        # Crear un generador mock para simular async for
        mock_session = mock.AsyncMock()
        mock_session_gen = mock.AsyncMock()
        mock_session_gen.__aiter__.return_value = [mock_session]
        mock_get_session.return_value = mock_session_gen
        
        # Mock para la consulta y resultado del estado narrativo
        state = mock.Mock()
        state.current_fragment_key = "test_fragment"
        
        mock_state_result = mock.AsyncMock()
        mock_state_result.scalars().first.return_value = state
        
        # Mock para la consulta y resultado del fragmento
        fragment = mock.Mock()
        fragment.key = "test_fragment"
        fragment.title = "Test Fragment"
        fragment.character = "diana"
        fragment.text = "This is a test fragment"
        fragment.level_required = 1
        fragment.is_vip_only = False
        
        # Crear opciones para el fragmento
        choice1 = mock.Mock()
        choice1.id = 1
        choice1.text = "Option 1"
        choice1.target_fragment_key = "target_1"
        choice1.required_items = {}
        
        choice2 = mock.Mock()
        choice2.id = 2
        choice2.text = "Option 2"
        choice2.target_fragment_key = "target_2"
        choice2.required_items = {}
        
        fragment.choices = [choice1, choice2]
        
        mock_fragment_result = mock.AsyncMock()
        mock_fragment_result.scalars().first.return_value = fragment
        
        # Configurar las llamadas a execute para devolver los resultados adecuados
        mock_session.execute.side_effect = [mock_state_result, mock_fragment_result]
        
        user_id = 123
        
        # Act
        result = await narrative_service.get_user_fragment(user_id)
        
        # Assert
        assert result is not None
        assert result["key"] == "test_fragment"
        assert result["title"] == "Test Fragment"
        assert result["character"] == "diana"
        assert len(result["choices"]) == 2
        assert result["choices"][0]["id"] == 1
        assert result["choices"][1]["id"] == 2

@pytest.mark.asyncio
async def test_get_user_lore_pieces():
    """
    Verifica que el método get_user_lore_pieces devuelve correctamente
    las pistas narrativas desbloqueadas por el usuario.
    """
    # Arrange
    event_bus = EventBus()
    narrative_service = NarrativeService(event_bus)
    
    # Mock para el acceso a la base de datos
    with mock.patch('src.modules.narrative.service.get_session') as mock_get_session:
        # Crear un generador mock para simular async for
        mock_session = mock.AsyncMock()
        mock_session_gen = mock.AsyncMock()
        mock_session_gen.__aiter__.return_value = [mock_session]
        mock_get_session.return_value = mock_session_gen
        
        # Mock para la consulta y resultado del estado narrativo
        lore_pieces = {
            "piece_1": {
                "title": "Piece 1",
                "description": "Description 1",
                "unlocked_at": "2023-01-01",
                "source": "reaction"
            },
            "piece_2": {
                "title": "Piece 2",
                "description": "Description 2",
                "unlocked_at": "2023-01-02",
                "source": "mission"
            }
        }
        
        state = mock.Mock()
        state.narrative_items = {"lore_pieces": lore_pieces}
        
        mock_result = mock.AsyncMock()
        mock_result.scalars().first.return_value = state
        mock_session.execute.return_value = mock_result
        
        user_id = 123
        
        # Act
        result = await narrative_service.get_user_lore_pieces(user_id)
        
        # Assert
        assert len(result) == 2
        assert result[0]["key"] in ["piece_1", "piece_2"]
        assert result[1]["key"] in ["piece_1", "piece_2"]
        assert result[0]["key"] != result[1]["key"]
