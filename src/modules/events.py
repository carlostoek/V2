from src.core.interfaces.IEventBus import IEvent
from typing import Dict, List, Optional, Any

class UserStartedBotEvent(IEvent):
    """Evento que se dispara cuando un usuario presiona /start por primera vez."""
    def __init__(self, user_id: int, username: str | None):
        self.user_id = user_id
        self.username = username

class ReactionAddedEvent(IEvent):
    """Evento que se dispara cuando un usuario reacciona a un mensaje."""
    def __init__(self, user_id: int, message_id: int, points_to_award: int = 5):
        self.user_id = user_id
        self.message_id = message_id
        self.points_to_award = points_to_award

class PointsAwardedEvent(IEvent):
    """Evento que se dispara cuando se otorgan puntos a un usuario."""
    def __init__(self, user_id: int, points: int, source_event: str):
        self.user_id = user_id
        self.points = points
        self.source_event = source_event # Para saber qué originó los puntos

class NarrativeProgressionEvent(IEvent):
    """Evento que se dispara cuando un usuario avanza en la narrativa."""
    def __init__(self, user_id: int, fragment_id: str, choices_made: Dict[str, List[int]]):
        self.user_id = user_id
        self.fragment_id = fragment_id
        self.choices_made = choices_made

class PieceUnlockedEvent(IEvent):
    """Evento que se dispara cuando un usuario desbloquea una pista narrativa."""
    def __init__(self, user_id: int, piece_id: str, unlock_method: str):
        self.user_id = user_id
        self.piece_id = piece_id
        self.unlock_method = unlock_method

class MissionCompletedEvent(IEvent):
    """Evento que se dispara cuando un usuario completa una misión."""
    def __init__(self, user_id: int, mission_id: str, completion_time: str, reward_points: int = 0):
        self.user_id = user_id
        self.mission_id = mission_id
        self.completion_time = completion_time
        self.reward_points = reward_points

class LevelUpEvent(IEvent):
    """Evento que se dispara cuando un usuario sube de nivel."""
    def __init__(self, user_id: int, new_level: int, rewards: Optional[Dict[str, Any]] = None):
        self.user_id = user_id
        self.new_level = new_level
        self.rewards = rewards or {}
