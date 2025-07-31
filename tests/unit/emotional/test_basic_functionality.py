"""Tests básicos para verificar funcionalidad del módulo emocional."""

import pytest
from unittest.mock import MagicMock

from src.modules.emotional.diana_state import (
    DianaStateMachine, 
    EmotionalState, 
    EmotionalTrigger,
    DianaStateData
)


class TestBasicEmotionalFunctionality:
    """Tests básicos sin dependencias externas."""
    
    def test_emotional_state_enum(self):
        """Test que verifica que los estados emocionales están correctamente definidos."""
        assert EmotionalState.VULNERABLE.value == "vulnerable"
        assert EmotionalState.ENIGMATICA.value == "enigmatica"
        assert EmotionalState.PROVOCADORA.value == "provocadora"
        assert EmotionalState.ANALITICA.value == "analitica"
        assert EmotionalState.SILENCIOSA.value == "silenciosa"
    
    def test_emotional_trigger_enum(self):
        """Test que verifica que los triggers están correctamente definidos."""
        assert EmotionalTrigger.RESPUESTA_EMOCIONAL.value == "respuesta_emocional"
        assert EmotionalTrigger.PREGUNTA_PROFUNDA.value == "pregunta_profunda"
        assert EmotionalTrigger.BROMA_COQUETA.value == "broma_coqueta"
        assert EmotionalTrigger.ANALISIS_SOLICITADO.value == "analisis_solicitado"
        assert EmotionalTrigger.SILENCIO_REQUERIDO.value == "silencio_requerido"
    
    def test_diana_state_machine_creation(self):
        """Test que verifica la creación de la máquina de estados."""
        machine = DianaStateMachine(user_id=123)
        
        assert machine.user_id == 123
        assert machine.get_current_state() == EmotionalState.ENIGMATICA
        assert len(machine.states) == 5
        assert len(machine.transitions) > 10  # Debe tener múltiples transiciones
    
    def test_state_machine_basic_transitions(self):
        """Test que verifica transiciones básicas funcionan."""
        machine = DianaStateMachine(user_id=456)
        
        # Estado inicial
        assert machine.get_current_state() == EmotionalState.ENIGMATICA
        
        # Transición válida: ENIGMATICA -> VULNERABLE
        success = machine.trigger_transition(EmotionalTrigger.RESPUESTA_EMOCIONAL)
        assert success == True
        assert machine.get_current_state() == EmotionalState.VULNERABLE
        
        # Transición válida: VULNERABLE -> PROVOCADORA  
        success = machine.trigger_transition(EmotionalTrigger.BROMA_COQUETA)
        assert success == True
        assert machine.get_current_state() == EmotionalState.PROVOCADORA
    
    def test_response_modifiers_generation(self):
        """Test que verifica la generación de modificadores de respuesta."""
        machine = DianaStateMachine(user_id=789)
        
        # Verificar modificadores para cada estado
        states_to_test = [
            (EmotionalState.ENIGMATICA, "mysterious"),
            (EmotionalState.VULNERABLE, "gentle"),
            (EmotionalState.PROVOCADORA, "playful"),
            (EmotionalState.ANALITICA, "analytical"),
            (EmotionalState.SILENCIOSA, "quiet")
        ]
        
        for state, expected_tone in states_to_test:
            # Cambiar al estado deseado
            machine.state_data.current_state = state
            machine.state = state.value
            
            # Verificar modificadores
            modifiers = machine.get_response_modifiers()
            assert modifiers["tone"] == expected_tone
            assert "formality" in modifiers
            assert "emotion_intensity" in modifiers
            assert "response_length" in modifiers
    
    def test_text_analysis_functionality(self):
        """Test que verifica el análisis de texto funciona correctamente."""
        machine = DianaStateMachine(user_id=999)
        
        # Test casos conocidos
        test_cases = [
            ("estoy muy triste", EmotionalTrigger.RESPUESTA_EMOCIONAL),
            ("¿cuál es el sentido de la vida?", EmotionalTrigger.PREGUNTA_PROFUNDA),
            ("jaja eres divertida", EmotionalTrigger.BROMA_COQUETA),
            ("analiza esta situación", EmotionalTrigger.ANALISIS_SOLICITADO),
            ("necesito que te calles", EmotionalTrigger.SILENCIO_REQUERIDO),
            ("hola ¿cómo estás?", None)  # Texto neutro
        ]
        
        for text, expected_trigger in test_cases:
            result = machine.analyze_user_input(text)
            assert result == expected_trigger, f"Failed for text: '{text}'"
    
    def test_state_data_serialization(self):
        """Test que verifica la serialización de datos de estado."""
        data = DianaStateData()
        data.current_state = EmotionalState.PROVOCADORA
        data.transition_count = 5
        data.user_interactions = 10
        
        # Convertir a diccionario
        data_dict = data.to_dict()
        assert data_dict["current_state"] == "provocadora"
        assert data_dict["transition_count"] == 5
        assert data_dict["user_interactions"] == 10
        
        # Crear desde diccionario
        restored_data = DianaStateData.from_dict(data_dict)
        assert restored_data.current_state == EmotionalState.PROVOCADORA
        assert restored_data.transition_count == 5
        assert restored_data.user_interactions == 10
    
    def test_universal_reset_functionality(self):
        """Test que verifica el reset universal funciona desde cualquier estado."""
        machine = DianaStateMachine(user_id=111)
        
        # Cambiar a varios estados diferentes
        states_to_test = [
            EmotionalState.VULNERABLE,
            EmotionalState.PROVOCADORA,
            EmotionalState.ANALITICA,
            EmotionalState.SILENCIOSA
        ]
        
        for target_state in states_to_test:
            # Cambiar manualmente al estado (simulando transición)
            machine.state_data.current_state = target_state
            machine.state = target_state.value
            
            # Aplicar reset universal
            success = machine.trigger_transition(EmotionalTrigger.MOOD_RESET)
            assert success == True
            assert machine.get_current_state() == EmotionalState.ENIGMATICA
    
    def test_context_preservation(self):
        """Test que verifica que el contexto se preserva durante transiciones."""
        machine = DianaStateMachine(user_id=222)
        
        context = {"emotion": "sadness", "intensity": 0.8, "source": "user_message"}
        
        # Realizar transición con contexto
        success = machine.trigger_transition(
            EmotionalTrigger.RESPUESTA_EMOCIONAL, 
            context=context
        )
        
        assert success == True
        assert machine.state_data.context_data["emotion"] == "sadness"
        assert machine.state_data.context_data["intensity"] == 0.8
        assert machine.state_data.context_data["source"] == "user_message"
    
    def test_statistics_generation(self):
        """Test que verifica la generación de estadísticas."""
        machine = DianaStateMachine(user_id=333)
        
        # Realizar algunas transiciones
        machine.trigger_transition(EmotionalTrigger.RESPUESTA_EMOCIONAL)
        machine.trigger_transition(EmotionalTrigger.BROMA_COQUETA)
        
        # Obtener estadísticas
        stats = machine.get_state_statistics()
        
        # Verificar estructura de estadísticas
        required_fields = [
            "current_state", "previous_state", "state_duration_minutes",
            "total_transitions", "user_interactions", "intensity_level", "context_data"
        ]
        
        for field in required_fields:
            assert field in stats, f"Missing field in stats: {field}"
        
        # Verificar valores
        assert stats["current_state"] == "provocadora"
        assert stats["total_transitions"] == 2
        assert stats["user_interactions"] == 2