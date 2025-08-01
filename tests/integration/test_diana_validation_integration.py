"""
Tests de integración para el sistema de validación Diana con gamificación.

Estos tests verifican que la integración entre el sistema de validación Diana
y el sistema de gamificación funcione correctamente.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

from src.core.event_bus import EventBus
from src.modules.gamification.service import GamificationService
from src.modules.narrative.diana_integration import DianaValidationIntegrationService
from src.modules.events import (
    ReactionAddedEvent,
    DianaValidationCompletedEvent,
    DianaValidationFailedEvent,
    NarrativeValidationProgressEvent,
    PointsAwardedEvent
)

# Mock del Diana Validator para tests
class MockDianaValidator:
    """Mock del validador Diana para tests."""
    
    def __init__(self, service_url: str = "http://localhost:8000"):
        self.service_url = service_url
        self.session = None
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
    
    async def can_advance_to_level_2(self, user_id: int, reaction_data: Dict) -> MagicMock:
        """Mock de validación nivel 1→2."""
        result = MagicMock()
        # Simular validación exitosa si la reacción es rápida
        speed = reaction_data.get('speed_seconds', 0)
        if speed < 5:  # Reacción rápida
            result.result.value = "passed"
            result.score = 0.9
            result.data = {'reaction_type': 'immediate', 'reward_type': 'quick_thinker'}
        else:
            result.result.value = "failed"
            result.score = 0.3
            result.data = {'reaction_type': 'slow', 'reward_type': 'none'}
        
        result.message = "Test validation result"
        result.next_action = "continue"
        return result
    
    async def can_advance_to_level_3(self, user_id: int, observation_events: list) -> MagicMock:
        """Mock de validación nivel 2→3."""
        result = MagicMock()
        # Simular validación exitosa si hay suficientes eventos de observación
        if len(observation_events) >= 3:
            result.result.value = "passed"
            result.score = 0.8
            result.data = {'observation_type': 'methodical', 'reward_items': ['clue_1']}
        else:
            result.result.value = "failed"
            result.score = 0.4
            result.data = {'observation_type': 'insufficient', 'reward_items': []}
        
        result.message = "Test observation validation"
        result.next_action = "continue"
        return result
    
    async def track_user_event(self, user_id: int, event_type: str, event_data: Dict) -> None:
        """Mock de tracking de eventos."""
        pass
    
    async def get_adaptive_content(self, user_id: int, content_type: str, context: Dict = None) -> Dict:
        """Mock de contenido adaptado."""
        return {
            'text': f'Mock content for {content_type}',
            'buttons': [],
            'media': None,
            'archetype': 'test_archetype'
        }
    
    async def get_user_archetype(self, user_id: int) -> str:
        """Mock de arquetipo de usuario."""
        return 'explorer'


@pytest.fixture
async def event_bus():
    """Fixture para el event bus."""
    return EventBus()


@pytest.fixture
async def gamification_service(event_bus):
    """Fixture para el servicio de gamificación."""
    service = GamificationService(event_bus)
    
    # Mock de la base de datos para evitar dependencias
    with patch('src.modules.gamification.service.get_session'):
        await service.setup()
    
    return service


@pytest.fixture
async def diana_integration_service(event_bus):
    """Fixture para el servicio de integración Diana."""
    service = DianaValidationIntegrationService(event_bus, "http://mock:8000")
    
    # Reemplazar el validator real con nuestro mock
    service.validator = MockDianaValidator()
    
    await service.setup()
    return service


@pytest.mark.asyncio
async def test_reaction_tracking_and_validation(event_bus, diana_integration_service, gamification_service):
    """
    Test que verifica el tracking de reacciones y su posterior validación.
    """
    user_id = 123
    message_id = 456
    
    # Simular una reacción rápida
    reaction_event = ReactionAddedEvent(user_id, message_id, points_to_award=5)
    
    # Publicar evento de reacción
    await event_bus.publish(reaction_event)
    
    # Verificar que se registró la reacción en el cache
    assert user_id in diana_integration_service.reaction_data_cache
    assert len(diana_integration_service.reaction_data_cache[user_id]) == 1
    
    # Simular validación de nivel 1→2
    success = await diana_integration_service.validate_level_progression(user_id, 1, 2)
    
    # La validación debería ser exitosa (reacción rápida)
    assert success is True


@pytest.mark.asyncio
async def test_diana_validation_completed_awards_points(event_bus, gamification_service):
    """
    Test que verifica que las validaciones Diana completadas otorgan puntos.
    """
    user_id = 123
    
    # Crear evento de validación completada
    validation_event = DianaValidationCompletedEvent(
        user_id=user_id,
        validation_type="level_1_to_2",
        score=0.9,
        reward_data={'reaction_type': 'immediate'}
    )
    
    # Publicar evento
    await event_bus.publish(validation_event)
    
    # Verificar que se otorgaron puntos
    # Puntos base (25) * score (0.9) + bonus (5) = 27.5 -> 27 puntos
    expected_points = 27  # int((25 * 0.9) + 5)
    assert gamification_service.get_points(user_id) >= expected_points


@pytest.mark.asyncio
async def test_diana_validation_failed_awards_consolation_points(event_bus, gamification_service):
    """
    Test que verifica que las validaciones Diana fallidas otorgan puntos de consolación.
    """
    user_id = 124
    
    # Crear evento de validación fallida
    validation_event = DianaValidationFailedEvent(
        user_id=user_id,
        validation_type="level_1_to_2",
        score=0.3,
        retry_allowed=True
    )
    
    # Publicar evento
    await event_bus.publish(validation_event)
    
    # Verificar que se otorgaron puntos de consolación
    # max(1, int(0.3 * 2)) = 1 punto
    assert gamification_service.get_points(user_id) >= 1


@pytest.mark.asyncio
async def test_narrative_validation_progress_awards_small_points(event_bus, gamification_service):
    """
    Test que verifica que el progreso en validaciones narrativas otorga puntos pequeños.
    """
    user_id = 125
    
    # Crear evento de progreso en validación narrativa
    progress_event = NarrativeValidationProgressEvent(
        user_id=user_id,
        validation_type="level_2_to_3",
        progress_data={'exploration_time': 120}
    )
    
    # Publicar evento
    await event_bus.publish(progress_event)
    
    # Verificar que se otorgaron puntos de progreso (2 puntos)
    assert gamification_service.get_points(user_id) == 2


@pytest.mark.asyncio
async def test_observation_events_validation(event_bus, diana_integration_service):
    """
    Test que verifica la acumulación de eventos de observación y su validación.
    """
    user_id = 126
    
    # Simular múltiples eventos de progreso narrativo (observación)
    from src.modules.events import NarrativeProgressionEvent
    
    for i in range(4):  # Suficientes eventos para pasar validación
        progression_event = NarrativeProgressionEvent(
            user_id=user_id,
            fragment_id=f"fragment_{i}",
            choices_made={}
        )
        await event_bus.publish(progression_event)
    
    # Verificar que se acumularon eventos de observación
    assert user_id in diana_integration_service.observation_events_cache
    assert len(diana_integration_service.observation_events_cache[user_id]) == 4
    
    # Simular validación de nivel 2→3
    success = await diana_integration_service.validate_level_progression(user_id, 2, 3)
    
    # La validación debería ser exitosa (suficientes eventos de observación)
    assert success is True


@pytest.mark.asyncio
async def test_adaptive_content_retrieval(diana_integration_service):
    """
    Test que verifica la obtención de contenido adaptado.
    """
    user_id = 127
    content_type = "diana_welcome"
    
    # Obtener contenido adaptado
    content = await diana_integration_service.get_adaptive_content_for_user(
        user_id, content_type, {'level': 2}
    )
    
    # Verificar estructura del contenido
    assert 'text' in content
    assert 'buttons' in content
    assert 'media' in content
    assert 'archetype' in content
    assert content['text'] == f'Mock content for {content_type}'


@pytest.mark.asyncio
async def test_user_archetype_retrieval(diana_integration_service):
    """
    Test que verifica la obtención del arquetipo de usuario.
    """
    user_id = 128
    
    # Obtener arquetipo
    archetype = await diana_integration_service.get_user_archetype(user_id)
    
    # Verificar que se obtiene un arquetipo válido
    assert archetype == 'explorer'


@pytest.mark.asyncio
async def test_validation_points_calculation():
    """
    Test que verifica el cálculo correcto de puntos para diferentes tipos de validación.
    """
    from src.modules.gamification.service import GamificationService
    
    # Crear instancia temporal para testear método privado
    event_bus = EventBus()
    service = GamificationService(event_bus)
    
    # Test validación nivel 1→2 con score alto
    points = service._calculate_diana_validation_points(
        "level_1_to_2", 0.9, {'reaction_type': 'immediate'}
    )
    expected = int((25 * 0.9) + 5)  # Base 25, score 0.9, bonus 5
    assert points == expected
    
    # Test validación nivel 2→3 con score medio
    points = service._calculate_diana_validation_points(
        "level_2_to_3", 0.6, {'observation_type': 'methodical'}
    )
    expected = int((40 * 0.6) + 10)  # Base 40, score 0.6, bonus 10
    assert points == expected
    
    # Test validación nivel 5→6 con score perfecto
    points = service._calculate_diana_validation_points(
        "level_5_to_6", 1.0, {'empathy_type': 'genuine'}
    )
    expected = int((80 * 1.0) + 15)  # Base 80, score 1.0, bonus 15
    assert points == expected


@pytest.mark.asyncio
async def test_full_integration_flow(event_bus, diana_integration_service, gamification_service):
    """
    Test de integración completo que simula el flujo de un usuario.
    """
    user_id = 200
    
    # 1. Usuario reacciona a un mensaje (reacción rápida)
    reaction_event = ReactionAddedEvent(user_id, 999, points_to_award=5)
    await event_bus.publish(reaction_event)
    
    # 2. Usuario progresa en la narrativa (múltiples exploraciones)
    from src.modules.events import NarrativeProgressionEvent
    for i in range(5):
        progression_event = NarrativeProgressionEvent(
            user_id=user_id,
            fragment_id=f"story_fragment_{i}",
            choices_made={f"fragment_{i}": [1]}
        )
        await event_bus.publish(progression_event)
    
    # 3. Validar progresión nivel 1→2 (debería ser exitosa)
    success_1_to_2 = await diana_integration_service.validate_level_progression(user_id, 1, 2)
    assert success_1_to_2 is True
    
    # 4. Validar progresión nivel 2→3 (debería ser exitosa)
    success_2_to_3 = await diana_integration_service.validate_level_progression(user_id, 2, 3)
    assert success_2_to_3 is True
    
    # 5. Verificar que el usuario acumuló puntos de múltiples fuentes
    total_points = gamification_service.get_points(user_id)
    
    # Puntos de reacciones iniciales + puntos de validaciones + puntos de progreso
    # Debería tener más de 50 puntos acumulados
    assert total_points > 50
    
    # 6. Obtener contenido adaptado para el usuario
    content = await diana_integration_service.get_adaptive_content_for_user(
        user_id, "congratulations", {'level': 3}
    )
    assert content['text'] == "Mock content for congratulations"
    assert content['archetype'] == 'test_archetype'


@pytest.mark.asyncio
async def test_service_cleanup(diana_integration_service):
    """
    Test que verifica la limpieza correcta del servicio.
    """
    user_id = 300
    
    # Agregar algunos datos a los caches
    diana_integration_service.reaction_data_cache[user_id] = [{'test': 'data'}]
    diana_integration_service.observation_events_cache[user_id] = [{'test': 'event'}]
    diana_integration_service.validation_attempts[user_id] = {'test': 'attempt'}
    
    # Verificar que hay datos
    assert len(diana_integration_service.reaction_data_cache) > 0
    assert len(diana_integration_service.observation_events_cache) > 0
    assert len(diana_integration_service.validation_attempts) > 0
    
    # Limpiar servicio
    await diana_integration_service.cleanup()
    
    # Verificar que los caches están vacíos
    assert len(diana_integration_service.reaction_data_cache) == 0
    assert len(diana_integration_service.observation_events_cache) == 0
    assert len(diana_integration_service.validation_attempts) == 0


if __name__ == "__main__":
    # Ejecutar tests básicos de forma manual
    async def run_basic_tests():
        print("Ejecutando tests básicos de integración Diana...")
        
        # Test de cálculo de puntos
        await test_validation_points_calculation()
        print("✓ Test de cálculo de puntos completado")
        
        # Crear instancias para otros tests
        event_bus = EventBus()
        
        # Test de integración Diana
        diana_service = DianaValidationIntegrationService(event_bus)
        diana_service.validator = MockDianaValidator()
        await diana_service.setup()
        
        # Test de contenido adaptado
        await test_adaptive_content_retrieval(diana_service)
        print("✓ Test de contenido adaptado completado")
        
        # Test de arquetipo
        await test_user_archetype_retrieval(diana_service)
        print("✓ Test de arquetipo completado")
        
        # Limpiar
        await diana_service.cleanup()
        print("✓ Test de limpieza completado")
        
        print("Todos los tests básicos completados exitosamente!")
    
    # Ejecutar si se llama directamente
    asyncio.run(run_basic_tests())