"""Tests for the Bot Orchestrator."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from src.bot.core.orchestrator import BotOrchestrator
from src.core.interfaces.IEventBus import IEvent


@pytest.mark.asyncio
async def test_handle_user_message(mock_di_container):
    """Test that the orchestrator handles user messages correctly."""
    # Arrange
    orchestrator = BotOrchestrator(mock_di_container)
    
    # Setup user service mock
    user_service = mock_di_container.services.user_service
    user_service.get_or_create_user = AsyncMock(return_value={
        "id": 123,
        "username": "test_user",
        "level": 1
    })
    
    # Setup emotional service mock
    emotional_service = mock_di_container.services.emotional_service
    emotional_service.process_message = AsyncMock(return_value={
        "current_state": "Enigmática",
        "confidence": 0.8
    })
    
    # Setup narrative service mock
    narrative_service = mock_di_container.services.narrative_service
    narrative_service.record_interaction = AsyncMock()
    narrative_service.story_fragments_to_send = {}
    
    # Setup gamification service mock
    gamification_service = mock_di_container.services.gamification_service
    gamification_service.update_engagement = AsyncMock()
    gamification_service.get_points = AsyncMock(return_value=10)
    
    # Setup event bus mock
    event_bus = mock_di_container.core.event_bus
    
    # Act
    result = await orchestrator.handle_user_message(
        user_id=123,
        message_text="Hello Diana",
        username="test_user"
    )
    
    # Assert
    user_service.get_or_create_user.assert_called_once_with(123, "test_user")
    emotional_service.process_message.assert_called_once()
    event_bus.publish.assert_called_once()
    gamification_service.update_engagement.assert_called_once_with(123)
    narrative_service.record_interaction.assert_called_once_with(123, "Hello Diana")
    
    assert isinstance(result, dict)
    assert "text" in result
    assert result["user_id"] == 123
    assert result["emotional_state"] == "Enigmática"
    assert result["points"] == 10
    assert "timestamp" in result


@pytest.mark.asyncio
async def test_handle_command_start(mock_di_container):
    """Test that the orchestrator handles the start command correctly."""
    # Arrange
    orchestrator = BotOrchestrator(mock_di_container)
    
    # Setup user service mock
    user_service = mock_di_container.services.user_service
    user_service.get_or_create_user = AsyncMock(return_value={
        "id": 123,
        "username": "test_user",
        "level": 1
    })
    
    # Setup narrative service mock
    narrative_service = mock_di_container.services.narrative_service
    narrative_service.get_user_fragment = AsyncMock(return_value={
        "key": "welcome_1",
        "text": "Welcome to Diana's world",
        "choices": []
    })
    
    # Setup event bus mock
    event_bus = mock_di_container.core.event_bus
    
    # Act
    result = await orchestrator.handle_command(
        user_id=123,
        command="start"
    )
    
    # Assert
    user_service.get_or_create_user.assert_called_once_with(123)
    narrative_service.get_user_fragment.assert_called_once_with(123)
    assert event_bus.publish.call_count == 2  # CommandExecutedEvent and UserStartedBotEvent
    
    assert isinstance(result, dict)
    assert "text" in result
    assert "¡Bienvenido a Diana Bot!" in result["text"]
    assert result["user_id"] == 123
    assert result["command"] == "start"
    assert "narrative_fragment" in result
    assert result["narrative_fragment"]["key"] == "welcome_1"


@pytest.mark.asyncio
async def test_handle_reaction(mock_di_container):
    """Test that the orchestrator handles user reactions correctly."""
    # Arrange
    orchestrator = BotOrchestrator(mock_di_container)
    
    # Setup user service mock
    user_service = mock_di_container.services.user_service
    user_service.get_or_create_user = AsyncMock(return_value={
        "id": 123,
        "username": "test_user",
        "level": 1
    })
    
    # Setup emotional service mock
    emotional_service = mock_di_container.services.emotional_service
    emotional_service.process_reaction = AsyncMock(return_value={
        "current_state": "Provocadora",
        "response": "Me gusta tu entusiasmo"
    })
    
    # Setup event bus mock
    event_bus = mock_di_container.core.event_bus
    
    # Act
    result = await orchestrator.handle_reaction(
        user_id=123,
        message_id=456,
        reaction_type="love"
    )
    
    # Assert
    user_service.get_or_create_user.assert_called_once_with(123)
    emotional_service.process_reaction.assert_called_once()
    event_bus.publish.assert_called_once()
    
    assert isinstance(result, dict)
    assert result["success"] is True
    assert result["user_id"] == 123
    assert result["message_id"] == 456
    assert result["reaction"] == "love"
    assert result["points_awarded"] == 2  # love reaction awards 2 points
    assert result["emotional_response"] == "Me gusta tu entusiasmo"


@pytest.mark.asyncio
async def test_handle_narrative_choice(mock_di_container, mock_central_config):
    """Test that the orchestrator handles narrative choices correctly."""
    # Arrange
    orchestrator = BotOrchestrator(mock_di_container)
    
    # Setup narrative service mock
    narrative_service = mock_di_container.services.narrative_service
    narrative_service.make_narrative_choice = AsyncMock(return_value=True)
    narrative_service.get_user_fragment = AsyncMock(return_value={
        "key": "fragment_2",
        "text": "You entered the mysterious room",
        "choices": []
    })
    
    # Setup emotional service mock
    emotional_service = mock_di_container.services.emotional_service
    emotional_service.process_narrative_progression = AsyncMock()
    
    # Setup gamification service mock
    gamification_service = mock_di_container.services.gamification_service
    gamification_service.award_points_for_narrative = AsyncMock()
    
    # Setup config mock
    mock_central_config.get.return_value = 2  # narrative.progression_points
    mock_di_container.core.central_config = MagicMock(return_value=mock_central_config)
    
    # Act
    result = await orchestrator.handle_narrative_choice(
        user_id=123,
        choice_id=1
    )
    
    # Assert
    narrative_service.make_narrative_choice.assert_called_once_with(123, 1)
    narrative_service.get_user_fragment.assert_called_once_with(123)
    emotional_service.process_narrative_progression.assert_called_once()
    gamification_service.award_points_for_narrative.assert_called_once_with(123, 2)
    
    assert isinstance(result, dict)
    assert result["success"] is True
    assert result["user_id"] == 123
    assert result["narrative_fragment"]["key"] == "fragment_2"
    assert result["points_awarded"] == 2


@pytest.mark.asyncio
async def test_generate_response(mock_di_container):
    """Test that the orchestrator generates responses based on emotional state."""
    # Arrange
    orchestrator = BotOrchestrator(mock_di_container)
    
    user_profile = {
        "id": 123,
        "username": "test_user",
        "level": 1
    }
    
    emotional_states = [
        {"current_state": "Enigmática"},
        {"current_state": "Vulnerable"},
        {"current_state": "Provocadora"},
        {"current_state": "Analítica"},
        {"current_state": "Silenciosa"},
        {"current_state": "Neutral"}
    ]
    
    # Act & Assert
    for state in emotional_states:
        response = await orchestrator._generate_response(
            user_id=123,
            message="Test message",
            user_profile=user_profile,
            emotional_context=state
        )
        
        # Just verify we get a non-empty string response
        assert isinstance(response, str)
        assert len(response) > 0