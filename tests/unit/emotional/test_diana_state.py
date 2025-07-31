"""Tests para la máquina de estados emocionales de Diana."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from src.modules.emotional.diana_state import (
    DianaStateMachine,
    EmotionalState,
    EmotionalTrigger,
    DianaStateData
)


class TestDianaStateData:
    """Tests para la clase DianaStateData."""
    
    def test_initialization(self):
        """Test que verifica la inicialización correcta."""
        data = DianaStateData()
        
        assert data.current_state == EmotionalState.ENIGMATICA
        assert data.previous_state is None
        assert data.transition_count == 0
        assert data.user_interactions == 0
        assert data.intensity_level == 0.5
        assert isinstance(data.context_data, dict)
        assert isinstance(data.state_start_time, datetime)
    
    def test_to_dict_conversion(self):
        """Test que verifica la conversión a diccionario."""
        data = DianaStateData()
        data.current_state = EmotionalState.VULNERABLE
        data.previous_state = EmotionalState.ENIGMATICA
        data.transition_count = 3
        
        result = data.to_dict()
        
        assert result["current_state"] == "vulnerable"
        assert result["previous_state"] == "enigmatica"
        assert result["transition_count"] == 3
        assert "state_start_time" in result
    
    def test_from_dict_creation(self):
        """Test que verifica la creación desde diccionario."""
        data_dict = {
            "current_state": "provocadora",
            "previous_state": "vulnerable",
            "state_start_time": datetime.now().isoformat(),
            "transition_count": 5,
            "context_data": {"test": "value"},
            "user_interactions": 10,
            "intensity_level": 0.8
        }
        
        data = DianaStateData.from_dict(data_dict)
        
        assert data.current_state == EmotionalState.PROVOCADORA
        assert data.previous_state == EmotionalState.VULNERABLE
        assert data.transition_count == 5
        assert data.user_interactions == 10
        assert data.intensity_level == 0.8
        assert data.context_data == {"test": "value"}


class TestDianaStateMachine:
    """Tests para la máquina de estados emocionales."""
    
    @pytest.fixture
    def state_machine(self):
        """Fixture que crea una máquina de estados para testing."""
        return DianaStateMachine(user_id=123)
    
    def test_initialization(self, state_machine):
        """Test que verifica la inicialización correcta de la máquina."""
        assert state_machine.user_id == 123
        assert state_machine.state == EmotionalState.ENIGMATICA.value
        assert state_machine.state_data.current_state == EmotionalState.ENIGMATICA
        assert len(state_machine.states) == 5
        assert len(state_machine.transitions) > 0
    
    def test_get_current_state(self, state_machine):
        """Test que verifica la obtención del estado actual."""
        current = state_machine.get_current_state()
        assert current == EmotionalState.ENIGMATICA
    
    def test_successful_transition(self, state_machine):
        """Test que verifica una transición exitosa."""
        # Transición de ENIGMATICA a VULNERABLE
        success = state_machine.trigger_transition(
            EmotionalTrigger.RESPUESTA_EMOCIONAL,
            context={"message": "estoy triste"}
        )
        
        assert success == True
        assert state_machine.get_current_state() == EmotionalState.VULNERABLE
        assert state_machine.state_data.previous_state == EmotionalState.ENIGMATICA
        assert state_machine.state_data.transition_count == 1
        assert state_machine.state_data.user_interactions == 1
    
    def test_invalid_transition(self, state_machine):
        """Test que verifica el manejo de transiciones inválidas."""
        # Intentar una transición que no existe
        success = state_machine.trigger_transition(
            EmotionalTrigger.SILENCIO_REQUERIDO  # No válido desde ENIGMATICA
        )
        
        # La máquina debe ignorar triggers inválidos y mantener el estado
        assert state_machine.get_current_state() == EmotionalState.ENIGMATICA
    
    def test_multiple_transitions(self, state_machine):
        """Test que verifica múltiples transiciones secuenciales."""
        # ENIGMATICA -> VULNERABLE
        state_machine.trigger_transition(EmotionalTrigger.RESPUESTA_EMOCIONAL)
        assert state_machine.get_current_state() == EmotionalState.VULNERABLE
        
        # VULNERABLE -> PROVOCADORA
        state_machine.trigger_transition(EmotionalTrigger.BROMA_COQUETA)
        assert state_machine.get_current_state() == EmotionalState.PROVOCADORA
        
        # PROVOCADORA -> ANALITICA
        state_machine.trigger_transition(EmotionalTrigger.ANALISIS_SOLICITADO)
        assert state_machine.get_current_state() == EmotionalState.ANALITICA
        
        assert state_machine.state_data.transition_count == 3
    
    def test_universal_reset_transition(self, state_machine):
        """Test que verifica la transición de reset universal."""
        # Cambiar a cualquier estado
        state_machine.trigger_transition(EmotionalTrigger.RESPUESTA_EMOCIONAL)
        assert state_machine.get_current_state() == EmotionalState.VULNERABLE
        
        # Reset desde cualquier estado
        success = state_machine.trigger_transition(EmotionalTrigger.MOOD_RESET)
        assert success == True
        assert state_machine.get_current_state() == EmotionalState.ENIGMATICA
    
    def test_state_duration_calculation(self, state_machine):
        """Test que verifica el cálculo de duración del estado."""
        # La duración inicial debe ser muy pequeña
        duration = state_machine.get_state_duration()
        assert duration.total_seconds() < 1
        
        # Simular paso de tiempo
        with patch('src.modules.emotional.diana_state.datetime') as mock_datetime:
            # Tiempo actual + 1 hora
            future_time = datetime.now() + timedelta(hours=1)
            mock_datetime.now.return_value = future_time
            
            duration = state_machine.get_state_duration()
            assert duration.total_seconds() >= 3600  # 1 hora en segundos
    
    def test_auto_transition_detection(self, state_machine):
        """Test que verifica la detección de transiciones automáticas."""
        # Cambiar a estado PROVOCADORA
        state_machine.trigger_transition(EmotionalTrigger.BROMA_COQUETA)
        
        # Simular mucho tiempo transcurrido
        with patch.object(state_machine, 'get_state_duration') as mock_duration:
            mock_duration.return_value = timedelta(hours=3)
            
            auto_trigger = state_machine.should_auto_transition()
            assert auto_trigger == EmotionalTrigger.TIEMPO_TRANSCURRIDO
    
    def test_response_modifiers(self, state_machine):
        """Test que verifica los modificadores de respuesta."""
        # Estado inicial (ENIGMATICA)
        modifiers = state_machine.get_response_modifiers()
        assert modifiers["tone"] == "mysterious"
        assert "keywords" in modifiers
        
        # Cambiar a VULNERABLE
        state_machine.trigger_transition(EmotionalTrigger.RESPUESTA_EMOCIONAL)
        modifiers = state_machine.get_response_modifiers()
        assert modifiers["tone"] == "gentle"
        assert modifiers["emotion_intensity"] == 0.8
        
        # Cambiar a PROVOCADORA
        state_machine.trigger_transition(EmotionalTrigger.BROMA_COQUETA)
        modifiers = state_machine.get_response_modifiers()
        assert modifiers["tone"] == "playful"
        assert modifiers["response_length"] == "short"
    
    def test_user_input_analysis(self, state_machine):
        """Test que verifica el análisis de entrada del usuario."""
        # Texto emocional
        trigger = state_machine.analyze_user_input("estoy muy triste y solo")
        assert trigger == EmotionalTrigger.RESPUESTA_EMOCIONAL
        
        # Pregunta filosófica
        trigger = state_machine.analyze_user_input("¿cuál es el sentido de la vida?")
        assert trigger == EmotionalTrigger.PREGUNTA_PROFUNDA
        
        # Broma o coqueteo
        trigger = state_machine.analyze_user_input("jaja eres muy divertida")
        assert trigger == EmotionalTrigger.BROMA_COQUETA
        
        # Solicitud de análisis
        trigger = state_machine.analyze_user_input("analiza esta situación por favor")
        assert trigger == EmotionalTrigger.ANALISIS_SOLICITADO
        
        # Solicitud de silencio
        trigger = state_machine.analyze_user_input("necesito que te calles un momento")
        assert trigger == EmotionalTrigger.SILENCIO_REQUERIDO
        
        # Texto neutro
        trigger = state_machine.analyze_user_input("hola, ¿cómo estás?")
        assert trigger is None
    
    def test_state_statistics(self, state_machine):
        """Test que verifica las estadísticas del estado."""
        # Realizar algunas transiciones
        state_machine.trigger_transition(
            EmotionalTrigger.RESPUESTA_EMOCIONAL,
            context={"test": "data"}
        )
        state_machine.trigger_transition(EmotionalTrigger.BROMA_COQUETA)
        
        stats = state_machine.get_state_statistics()
        
        assert stats["current_state"] == "provocadora"
        assert stats["previous_state"] == "vulnerable"
        assert stats["total_transitions"] == 2
        assert stats["user_interactions"] == 2
        assert "state_duration_minutes" in stats
        assert "intensity_level" in stats
        assert "context_data" in stats
    
    def test_context_data_persistence(self, state_machine):
        """Test que verifica la persistencia de datos de contexto."""
        context = {"emotion": "sadness", "intensity": 0.8}
        
        state_machine.trigger_transition(
            EmotionalTrigger.RESPUESTA_EMOCIONAL,
            context=context
        )
        
        # El contexto debe persistir en state_data
        assert "emotion" in state_machine.state_data.context_data
        assert state_machine.state_data.context_data["emotion"] == "sadness"
        assert state_machine.state_data.context_data["intensity"] == 0.8