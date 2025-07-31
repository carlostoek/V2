"""Sistema de estados emocionales para Diana usando Transitions."""

import logging
from enum import Enum
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from transitions import Machine
from transitions.extensions import GraphMachine

from src.core.interfaces.IEventBus import IEvent


class EmotionalState(Enum):
    """Estados emocionales disponibles para Diana."""
    VULNERABLE = "vulnerable"
    ENIGMATICA = "enigmatica"
    PROVOCADORA = "provocadora"
    ANALITICA = "analitica"
    SILENCIOSA = "silenciosa"


class EmotionalTrigger(Enum):
    """Triggers que pueden causar cambios de estado emocional."""
    RESPUESTA_EMOCIONAL = "respuesta_emocional"
    PREGUNTA_PROFUNDA = "pregunta_profunda"
    BROMA_COQUETA = "broma_coqueta"
    ANALISIS_SOLICITADO = "analisis_solicitado"
    SILENCIO_REQUERIDO = "silencio_requerido"
    TIEMPO_TRANSCURRIDO = "tiempo_transcurrido"
    INTERACCION_INTENSA = "interaccion_intensa"
    MOOD_RESET = "mood_reset"


class DianaStateData:
    """Datos asociados con el estado emocional actual."""
    
    def __init__(self):
        self.current_state = EmotionalState.ENIGMATICA
        self.previous_state = None
        self.state_start_time = datetime.now()
        self.transition_count = 0
        self.context_data = {}
        self.user_interactions = 0
        self.intensity_level = 0.5  # 0.0 - 1.0
        
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el estado a diccionario para serialización."""
        return {
            "current_state": self.current_state.value,
            "previous_state": self.previous_state.value if self.previous_state else None,
            "state_start_time": self.state_start_time.isoformat(),
            "transition_count": self.transition_count,
            "context_data": self.context_data,
            "user_interactions": self.user_interactions,
            "intensity_level": self.intensity_level
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DianaStateData':
        """Crea instancia desde diccionario."""
        instance = cls()
        instance.current_state = EmotionalState(data["current_state"])
        instance.previous_state = EmotionalState(data["previous_state"]) if data["previous_state"] else None
        instance.state_start_time = datetime.fromisoformat(data["state_start_time"])
        instance.transition_count = data["transition_count"]
        instance.context_data = data["context_data"]
        instance.user_interactions = data["user_interactions"]
        instance.intensity_level = data["intensity_level"]
        return instance


class DianaStateMachine:
    """
    Máquina de estados emocionales para Diana.
    
    Gestiona las transiciones entre diferentes estados emocionales
    basados en interacciones del usuario y contexto de conversación.
    """
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.logger = logging.getLogger(__name__)
        self.state_data = DianaStateData()
        
        # Definir estados
        self.states = [state.value for state in EmotionalState]
        
        # Definir transiciones
        self.transitions = [
            # Desde ENIGMATICA
            {
                'trigger': EmotionalTrigger.RESPUESTA_EMOCIONAL.value,
                'source': EmotionalState.ENIGMATICA.value,
                'dest': EmotionalState.VULNERABLE.value,
                'before': 'on_before_transition',
                'after': 'on_after_transition'
            },
            {
                'trigger': EmotionalTrigger.BROMA_COQUETA.value,
                'source': EmotionalState.ENIGMATICA.value,
                'dest': EmotionalState.PROVOCADORA.value,
                'before': 'on_before_transition',
                'after': 'on_after_transition'
            },
            {
                'trigger': EmotionalTrigger.ANALISIS_SOLICITADO.value,
                'source': EmotionalState.ENIGMATICA.value,
                'dest': EmotionalState.ANALITICA.value,
                'before': 'on_before_transition',
                'after': 'on_after_transition'
            },
            
            # Desde VULNERABLE
            {
                'trigger': EmotionalTrigger.PREGUNTA_PROFUNDA.value,
                'source': EmotionalState.VULNERABLE.value,
                'dest': EmotionalState.ANALITICA.value,
                'before': 'on_before_transition',
                'after': 'on_after_transition'
            },
            {
                'trigger': EmotionalTrigger.BROMA_COQUETA.value,
                'source': EmotionalState.VULNERABLE.value,
                'dest': EmotionalState.PROVOCADORA.value,
                'before': 'on_before_transition',
                'after': 'on_after_transition'
            },
            {
                'trigger': EmotionalTrigger.SILENCIO_REQUERIDO.value,
                'source': EmotionalState.VULNERABLE.value,
                'dest': EmotionalState.SILENCIOSA.value,
                'before': 'on_before_transition',
                'after': 'on_after_transition'
            },
            
            # Desde PROVOCADORA
            {
                'trigger': EmotionalTrigger.RESPUESTA_EMOCIONAL.value,
                'source': EmotionalState.PROVOCADORA.value,
                'dest': EmotionalState.VULNERABLE.value,
                'before': 'on_before_transition',
                'after': 'on_after_transition'
            },
            {
                'trigger': EmotionalTrigger.ANALISIS_SOLICITADO.value,
                'source': EmotionalState.PROVOCADORA.value,
                'dest': EmotionalState.ANALITICA.value,
                'before': 'on_before_transition',
                'after': 'on_after_transition'
            },
            {
                'trigger': EmotionalTrigger.TIEMPO_TRANSCURRIDO.value,
                'source': EmotionalState.PROVOCADORA.value,
                'dest': EmotionalState.ENIGMATICA.value,
                'before': 'on_before_transition',
                'after': 'on_after_transition'
            },
            
            # Desde ANALITICA
            {
                'trigger': EmotionalTrigger.BROMA_COQUETA.value,
                'source': EmotionalState.ANALITICA.value,
                'dest': EmotionalState.PROVOCADORA.value,
                'before': 'on_before_transition',
                'after': 'on_after_transition'
            },
            {
                'trigger': EmotionalTrigger.RESPUESTA_EMOCIONAL.value,
                'source': EmotionalState.ANALITICA.value,
                'dest': EmotionalState.VULNERABLE.value,
                'before': 'on_before_transition',
                'after': 'on_after_transition'
            },
            {
                'trigger': EmotionalTrigger.TIEMPO_TRANSCURRIDO.value,
                'source': EmotionalState.ANALITICA.value,
                'dest': EmotionalState.ENIGMATICA.value,
                'before': 'on_before_transition',
                'after': 'on_after_transition'
            },
            
            # Desde SILENCIOSA
            {
                'trigger': EmotionalTrigger.INTERACCION_INTENSA.value,
                'source': EmotionalState.SILENCIOSA.value,
                'dest': EmotionalState.ENIGMATICA.value,
                'before': 'on_before_transition',
                'after': 'on_after_transition'
            },
            {
                'trigger': EmotionalTrigger.PREGUNTA_PROFUNDA.value,
                'source': EmotionalState.SILENCIOSA.value,
                'dest': EmotionalState.ANALITICA.value,
                'before': 'on_before_transition',
                'after': 'on_after_transition'
            },
            
            # Transiciones universales de reset
            {
                'trigger': EmotionalTrigger.MOOD_RESET.value,
                'source': '*',
                'dest': EmotionalState.ENIGMATICA.value,
                'before': 'on_before_transition',
                'after': 'on_after_transition'
            }
        ]
        
        # Inicializar máquina de estados
        self.machine = Machine(
            model=self,
            states=self.states,
            transitions=self.transitions,
            initial=EmotionalState.ENIGMATICA.value,
            auto_transitions=False,
            ordered_transitions=False,
            ignore_invalid_triggers=True
        )
        
        self.logger.info(f"Máquina de estados emocionales inicializada para usuario {user_id}")
    
    def on_before_transition(self, *args, **kwargs):
        """Callback ejecutado antes de cada transición."""
        self.state_data.previous_state = self.state_data.current_state
        self.logger.debug(f"Usuario {self.user_id}: Transición desde {self.state_data.current_state.value}")
    
    def on_after_transition(self, *args, **kwargs):
        """Callback ejecutado después de cada transición."""
        self.state_data.current_state = EmotionalState(self.state)
        self.state_data.state_start_time = datetime.now()
        self.state_data.transition_count += 1
        
        self.logger.info(
            f"Usuario {self.user_id}: Nueva transición a {self.state_data.current_state.value} "
            f"(transición #{self.state_data.transition_count})"
        )
    
    def trigger_transition(self, trigger: EmotionalTrigger, context: Dict[str, Any] = None) -> bool:
        """
        Dispara una transición de estado.
        
        Args:
            trigger: El trigger que causa la transición.
            context: Datos contextuales adicionales.
            
        Returns:
            True si la transición fue exitosa, False en caso contrario.
        """
        try:
            if context:
                self.state_data.context_data.update(context)
            
            # Incrementar contador de interacciones
            self.state_data.user_interactions += 1
            
            # Ejecutar transición
            trigger_method = getattr(self, trigger.value, None)
            if trigger_method and callable(trigger_method):
                trigger_method()
                return True
            else:
                self.logger.warning(f"Trigger {trigger.value} no encontrado o transición inválida")
                return False
        
        except Exception as e:
            self.logger.error(f"Error al ejecutar transición {trigger.value}: {e}")
            return False
    
    def get_current_state(self) -> EmotionalState:
        """Obtiene el estado emocional actual."""
        return self.state_data.current_state
    
    def get_state_duration(self) -> timedelta:
        """Obtiene la duración del estado actual."""
        return datetime.now() - self.state_data.state_start_time
    
    def should_auto_transition(self) -> Optional[EmotionalTrigger]:
        """
        Determina si debería ocurrir una transición automática basada en tiempo u otros factores.
        
        Returns:
            Trigger para transición automática o None si no se requiere.
        """
        duration = self.get_state_duration()
        
        # Transición automática después de mucho tiempo en ciertos estados
        if duration > timedelta(hours=2):
            if self.state_data.current_state in [
                EmotionalState.PROVOCADORA,
                EmotionalState.ANALITICA
            ]:
                return EmotionalTrigger.TIEMPO_TRANSCURRIDO
        
        # Reset automático después de mucho tiempo sin interacciones
        if duration > timedelta(hours=6) and self.state_data.user_interactions == 0:
            return EmotionalTrigger.MOOD_RESET
        
        return None
    
    def get_response_modifiers(self) -> Dict[str, Any]:
        """
        Obtiene modificadores para respuestas basados en el estado actual.
        
        Returns:
            Diccionario con modificadores de tono, estilo, etc.
        """
        modifiers = {
            "tone": "neutral",
            "formality": 0.5,  # 0.0 = muy informal, 1.0 = muy formal
            "emotion_intensity": self.state_data.intensity_level,
            "response_length": "medium",
            "use_emojis": True
        }
        
        if self.state_data.current_state == EmotionalState.VULNERABLE:
            modifiers.update({
                "tone": "gentle",
                "formality": 0.3,
                "emotion_intensity": 0.8,
                "response_length": "long",
                "keywords": ["comprendo", "siento", "entiendo", "me pasa también"]
            })
        
        elif self.state_data.current_state == EmotionalState.ENIGMATICA:
            modifiers.update({
                "tone": "mysterious",
                "formality": 0.6,
                "emotion_intensity": 0.5,
                "response_length": "medium",
                "keywords": ["quizás", "interesante", "curioso", "me pregunto"]
            })
        
        elif self.state_data.current_state == EmotionalState.PROVOCADORA:
            modifiers.update({
                "tone": "playful",
                "formality": 0.2,
                "emotion_intensity": 0.7,
                "response_length": "short",
                "keywords": ["jeje", "traviesa", "atrevida", "😏", "¿en serio?"]
            })
        
        elif self.state_data.current_state == EmotionalState.ANALITICA:
            modifiers.update({
                "tone": "analytical",
                "formality": 0.8,
                "emotion_intensity": 0.3,
                "response_length": "long",
                "keywords": ["analicemos", "desde mi perspectiva", "considerando", "objetivamente"]
            })
        
        elif self.state_data.current_state == EmotionalState.SILENCIOSA:
            modifiers.update({
                "tone": "quiet",
                "formality": 0.7,
                "emotion_intensity": 0.2,
                "response_length": "short",
                "keywords": ["...", "mmm", "entiendo", "*silencio*"]
            })
        
        return modifiers
    
    def analyze_user_input(self, text: str, context: Dict[str, Any] = None) -> Optional[EmotionalTrigger]:
        """
        Analiza entrada del usuario para determinar posibles triggers emocionales.
        
        Args:
            text: Texto del usuario.
            context: Contexto adicional (sentimiento, intención, etc.).
            
        Returns:
            Trigger sugerido basado en el análisis o None.
        """
        text_lower = text.lower()
        
        # Detectar solicitudes de silencio o pausa (prioridad alta)
        silence_keywords = [
            "cállate", "silencio", "no hables", "déjame", "tranquilo",
            "necesito espacio", "no responder", "te calles"
        ]
        if any(keyword in text_lower for keyword in silence_keywords):
            return EmotionalTrigger.SILENCIO_REQUERIDO
        
        # Detectar respuestas emocionales
        emotional_keywords = [
            "triste", "llorar", "deprimido", "angustiado", "solo", "mal",
            "duele", "dolor", "sufriendo", "herido", "vulnerable"
        ]
        if any(keyword in text_lower for keyword in emotional_keywords):
            return EmotionalTrigger.RESPUESTA_EMOCIONAL
        
        # Detectar preguntas profundas o filosóficas
        deep_keywords = [
            "por qué", "sentido", "propósito", "existencia", "vida", "muerte",
            "amor", "felicidad", "realidad", "consciencia", "alma"
        ]
        if any(keyword in text_lower for keyword in deep_keywords) and "?" in text:
            return EmotionalTrigger.PREGUNTA_PROFUNDA
        
        # Detectar bromas o coqueteo
        playful_keywords = [
            "jaja", "jeje", "lol", "gracioso", "divertido", "bromear",
            "coquetear", "guapo", "linda", "hermosa", "sexy"
        ]
        if any(keyword in text_lower for keyword in playful_keywords):
            return EmotionalTrigger.BROMA_COQUETA
        
        # Detectar solicitudes de análisis
        analytical_keywords = [
            "analiza", "explica", "razona", "lógica", "piensas", "opinas",
            "estudia", "evalúa", "compara", "pros y contras"
        ]
        if any(keyword in text_lower for keyword in analytical_keywords):
            return EmotionalTrigger.ANALISIS_SOLICITADO
        
        
        return None
    
    def get_state_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas del estado emocional."""
        return {
            "current_state": self.state_data.current_state.value,
            "previous_state": self.state_data.previous_state.value if self.state_data.previous_state else None,
            "state_duration_minutes": self.get_state_duration().total_seconds() / 60,
            "total_transitions": self.state_data.transition_count,
            "user_interactions": self.state_data.user_interactions,
            "intensity_level": self.state_data.intensity_level,
            "context_data": self.state_data.context_data
        }