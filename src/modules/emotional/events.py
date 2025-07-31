"""Eventos relacionados con el sistema emocional."""

from datetime import datetime
from typing import Dict, Any, Optional
from src.core.interfaces.IEventBus import IEvent
from src.modules.emotional.diana_state import EmotionalState, EmotionalTrigger


class EmotionalStateChangedEvent(IEvent):
    """Evento que se dispara cuando cambia el estado emocional de Diana."""
    
    def __init__(self, 
                 user_id: int, 
                 previous_state: Optional[EmotionalState], 
                 new_state: EmotionalState, 
                 trigger: EmotionalTrigger,
                 context: Dict[str, Any] = None):
        self.user_id = user_id
        self.previous_state = previous_state
        self.new_state = new_state
        self.trigger = trigger
        self.context = context or {}
        self.timestamp = datetime.now()


class UserInteractionAnalyzedEvent(IEvent):
    """Evento que se dispara cuando se analiza una interacción del usuario."""
    
    def __init__(self, 
                 user_id: int, 
                 message_text: str, 
                 detected_trigger: Optional[EmotionalTrigger],
                 sentiment_score: float = 0.0,
                 context: Dict[str, Any] = None):
        self.user_id = user_id
        self.message_text = message_text
        self.detected_trigger = detected_trigger
        self.sentiment_score = sentiment_score  # -1.0 (negativo) a 1.0 (positivo)
        self.context = context or {}
        self.timestamp = datetime.now()


class EmotionalIntensityChangedEvent(IEvent):
    """Evento que se dispara cuando cambia la intensidad emocional."""
    
    def __init__(self, 
                 user_id: int, 
                 previous_intensity: float, 
                 new_intensity: float,
                 reason: str):
        self.user_id = user_id
        self.previous_intensity = previous_intensity
        self.new_intensity = new_intensity
        self.reason = reason
        self.timestamp = datetime.now()


class EmotionalResetEvent(IEvent):
    """Evento que se dispara cuando se resetea el estado emocional."""
    
    def __init__(self, user_id: int, reason: str = "manual_reset"):
        self.user_id = user_id
        self.reason = reason
        self.timestamp = datetime.now()


class ResponseModifiedEvent(IEvent):
    """Evento que se dispara cuando una respuesta es modificada por el estado emocional."""
    
    def __init__(self, 
                 user_id: int, 
                 original_response: str, 
                 modified_response: str,
                 emotional_state: EmotionalState,
                 modifiers_applied: Dict[str, Any]):
        self.user_id = user_id
        self.original_response = original_response
        self.modified_response = modified_response
        self.emotional_state = emotional_state
        self.modifiers_applied = modifiers_applied
        self.timestamp = datetime.now()