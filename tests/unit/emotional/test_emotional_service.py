"""Tests para el servicio emocional."""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

# Mock de configuración antes de importar
with patch('src.bot.config.settings.Settings') as mock_settings:
    mock_settings.return_value = MagicMock(
        BOT_TOKEN="test_token",
        DATABASE_URL="sqlite:///:memory:",
        USE_SQLITE=True,
        DATABASE_ECHO=False,
        CREATE_TABLES=True
    )
    
    from src.modules.emotional.service import EmotionalService
    from src.modules.emotional.diana_state import EmotionalState, EmotionalTrigger
    from src.modules.emotional.events import (
        EmotionalStateChangedEvent,
        UserInteractionAnalyzedEvent
    )
    from src.modules.events import UserStartedBotEvent


@pytest.fixture
def event_bus_mock():
    """Mock para el event bus."""
    mock = AsyncMock()
    mock.subscribe = MagicMock()
    mock.publish = AsyncMock()
    return mock


@pytest.fixture
async def emotional_service(event_bus_mock):
    """Fixture para el servicio emocional."""
    service = EmotionalService(event_bus_mock)
    await service.setup()
    return service


@pytest.mark.asyncio
async def test_service_setup(event_bus_mock):
    """Test que verifica la configuración del servicio."""
    service = EmotionalService(event_bus_mock)
    await service.setup()
    
    # Verificar suscripción a eventos
    event_bus_mock.subscribe.assert_called_once_with(UserStartedBotEvent, service.handle_user_started)


@pytest.mark.asyncio
async def test_get_or_create_state_machine(emotional_service):
    """Test que verifica la creación de máquinas de estado."""
    user_id = 123
    
    # Primera llamada debe crear la máquina
    machine1 = await emotional_service.get_or_create_state_machine(user_id)
    assert machine1.user_id == user_id
    assert machine1.get_current_state() == EmotionalState.ENIGMATICA
    
    # Segunda llamada debe devolver la misma máquina
    machine2 = await emotional_service.get_or_create_state_machine(user_id)
    assert machine1 is machine2


@pytest.mark.asyncio
async def test_handle_user_started(emotional_service, event_bus_mock):
    """Test que verifica el manejo de usuarios nuevos."""
    user_id = 456
    event = UserStartedBotEvent(user_id=user_id, username="test_user")
    
    # Antes del evento, no debe existir la máquina
    assert user_id not in emotional_service.state_machines
    
    # Manejar evento
    await emotional_service.handle_user_started(event)
    
    # Después del evento, debe existir la máquina
    assert user_id in emotional_service.state_machines
    machine = emotional_service.state_machines[user_id]
    assert machine.user_id == user_id


@pytest.mark.asyncio
async def test_analyze_user_interaction(emotional_service, event_bus_mock):
    """Test que verifica el análisis de interacciones."""
    user_id = 789
    message_text = "estoy muy triste"
    
    # Analizar interacción
    trigger = await emotional_service.analyze_user_interaction(user_id, message_text)
    
    # Debe detectar trigger emocional
    assert trigger == EmotionalTrigger.RESPUESTA_EMOCIONAL
    
    # Debe publicar evento de análisis
    event_bus_mock.publish.assert_called()
    published_event = event_bus_mock.publish.call_args[0][0]
    assert isinstance(published_event, UserInteractionAnalyzedEvent)
    assert published_event.user_id == user_id
    assert published_event.message_text == message_text
    assert published_event.detected_trigger == EmotionalTrigger.RESPUESTA_EMOCIONAL


@pytest.mark.asyncio
async def test_trigger_state_change(emotional_service, event_bus_mock):
    """Test que verifica el cambio de estado."""
    user_id = 999
    
    # Crear máquina de estado
    await emotional_service.get_or_create_state_machine(user_id)
    
    # Verificar estado inicial
    machine = emotional_service.state_machines[user_id]
    assert machine.get_current_state() == EmotionalState.ENIGMATICA
    
    # Disparar cambio de estado
    success = await emotional_service.trigger_state_change(
        user_id=user_id,
        trigger=EmotionalTrigger.RESPUESTA_EMOCIONAL,
        context={"message": "test"}
    )
    
    # Verificar cambio exitoso
    assert success == True
    assert machine.get_current_state() == EmotionalState.VULNERABLE
    
    # Verificar que se publicó evento
    event_bus_mock.publish.assert_called()
    published_event = event_bus_mock.publish.call_args[0][0]
    assert isinstance(published_event, EmotionalStateChangedEvent)
    assert published_event.user_id == user_id
    assert published_event.new_state == EmotionalState.VULNERABLE


@pytest.mark.asyncio
async def test_get_response_modifiers(emotional_service):
    """Test que verifica la obtención de modificadores."""
    user_id = 111
    
    # Obtener modificadores para estado inicial
    modifiers = await emotional_service.get_response_modifiers(user_id)
    
    # Verificar modificadores por defecto (enigmática)
    assert modifiers["tone"] == "mysterious"
    assert "keywords" in modifiers
    assert "formality" in modifiers
    assert "emotion_intensity" in modifiers


@pytest.mark.asyncio
async def test_modify_response(emotional_service):
    """Test que verifica la modificación de respuestas."""
    user_id = 222
    original_response = "Hola, ¿cómo estás?"
    
    # Cambiar a estado vulnerable
    await emotional_service.trigger_state_change(
        user_id=user_id,
        trigger=EmotionalTrigger.RESPUESTA_EMOCIONAL
    )
    
    # Modificar respuesta
    modified_response = await emotional_service.modify_response(
        user_id=user_id,
        original_response=original_response
    )
    
    # La respuesta debe ser diferente (aplicado tono gentil)
    assert modified_response != original_response
    # Debe contener elementos del tono gentil
    assert any(word in modified_response.lower() for word in ["entiendo", "comprendo", "siento"])


@pytest.mark.asyncio
async def test_get_user_emotional_stats(emotional_service):
    """Test que verifica la obtención de estadísticas."""
    user_id = 333
    
    # Realizar algunas transiciones
    await emotional_service.trigger_state_change(
        user_id=user_id,
        trigger=EmotionalTrigger.RESPUESTA_EMOCIONAL
    )
    await emotional_service.trigger_state_change(
        user_id=user_id,
        trigger=EmotionalTrigger.BROMA_COQUETA
    )
    
    # Obtener estadísticas
    stats = await emotional_service.get_user_emotional_stats(user_id)
    
    # Verificar estadísticas
    assert stats["current_state"] == "provocadora"
    assert stats["total_transitions"] == 2
    assert stats["user_interactions"] == 2
    assert "state_duration_minutes" in stats


@pytest.mark.asyncio
async def test_reset_emotional_state(emotional_service, event_bus_mock):
    """Test que verifica el reset de estado emocional."""
    user_id = 444
    
    # Cambiar a estado diferente al inicial
    await emotional_service.trigger_state_change(
        user_id=user_id,
        trigger=EmotionalTrigger.RESPUESTA_EMOCIONAL
    )
    
    machine = emotional_service.state_machines[user_id]
    assert machine.get_current_state() == EmotionalState.VULNERABLE
    
    # Resetear estado
    success = await emotional_service.reset_emotional_state(user_id)
    
    # Verificar reset
    assert success == True
    assert machine.get_current_state() == EmotionalState.ENIGMATICA


@pytest.mark.asyncio
async def test_cleanup_inactive_machines(emotional_service):
    """Test que verifica la limpieza de máquinas inactivas."""
    user_id1 = 555
    user_id2 = 666
    
    # Crear dos máquinas
    await emotional_service.get_or_create_state_machine(user_id1)
    await emotional_service.get_or_create_state_machine(user_id2)
    
    assert len(emotional_service.state_machines) == 2
    
    # Simular máquinas muy antiguas
    with patch.object(emotional_service.state_machines[user_id1], 'get_state_duration') as mock_duration1:
        with patch.object(emotional_service.state_machines[user_id2], 'get_state_duration') as mock_duration2:
            from datetime import timedelta
            mock_duration1.return_value = timedelta(hours=25)  # Muy antigua
            mock_duration2.return_value = timedelta(hours=1)   # Reciente
            
            # Limpiar máquinas inactivas
            cleaned = await emotional_service.cleanup_inactive_machines(max_age_hours=24)
            
            # Solo debe limpiar una máquina
            assert cleaned == 1
            assert len(emotional_service.state_machines) == 1
            assert user_id2 in emotional_service.state_machines
            assert user_id1 not in emotional_service.state_machines