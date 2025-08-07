from src.core.interfaces.IEventBus import IEvent
from typing import Dict, List, Optional, Any

class UserMessageEvent(IEvent):
    """Evento que se dispara cuando un usuario envía un mensaje."""
    def __init__(self, user_id: int, message: str, timestamp: str):
        self.user_id = user_id
        self.message = message
        self.timestamp = timestamp

class CommandExecutedEvent(IEvent):
    """Evento que se dispara cuando un usuario ejecuta un comando."""
    def __init__(self, user_id: int, command: str, args: List[str], timestamp: str):
        self.user_id = user_id
        self.command = command
        self.args = args
        self.timestamp = timestamp

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

class DianaValidationCompletedEvent(IEvent):
    """Evento que se dispara cuando un usuario completa una validación de Diana."""
    def __init__(self, user_id: int, validation_type: str, score: float, reward_data: Dict[str, Any] = None):
        self.user_id = user_id
        self.validation_type = validation_type  # 'level_1_to_2', 'level_2_to_3', etc.
        self.score = score
        self.reward_data = reward_data or {}

class DianaValidationFailedEvent(IEvent):
    """Evento que se dispara cuando un usuario falla una validación de Diana."""
    def __init__(self, user_id: int, validation_type: str, score: float, retry_allowed: bool = True):
        self.user_id = user_id
        self.validation_type = validation_type
        self.score = score
        self.retry_allowed = retry_allowed

class NarrativeValidationProgressEvent(IEvent):
    """Evento que se dispara cuando hay progreso en validaciones narrativas."""
    def __init__(self, user_id: int, validation_type: str, progress_data: Dict[str, Any]):
        self.user_id = user_id
        self.validation_type = validation_type
        self.progress_data = progress_data

class RoleChangedEvent(IEvent):
    """Evento que se dispara cuando cambia el rol de un usuario."""
    def __init__(self, user_id: int, old_role: str, new_role: str, changed_by: Optional[int] = None):
        self.user_id = user_id
        self.old_role = old_role
        self.new_role = new_role
        self.changed_by = changed_by
        self.timestamp = datetime.now().isoformat()

class VIPStatusChangedEvent(IEvent):
    """Evento que se dispara cuando cambia el estado VIP de un usuario."""
    def __init__(self, user_id: int, is_vip: bool, expires_at: Optional[str] = None, changed_by: Optional[int] = None):
        self.user_id = user_id
        self.is_vip = is_vip
        self.expires_at = expires_at
        self.changed_by = changed_by
        self.timestamp = datetime.now().isoformat()

class AdminStatusChangedEvent(IEvent):
    """Evento que se dispara cuando cambia el estado de administrador de un usuario."""
    def __init__(self, user_id: int, is_admin: bool, changed_by: Optional[int] = None):
        self.user_id = user_id
        self.is_admin = is_admin
        self.changed_by = changed_by
        self.timestamp = datetime.now().isoformat()

@dataclass
class UserCreatedEvent(IEvent):
    """Evento lanzado cuando se crea un nuevo usuario."""
    user_id: int
    telegram_id: int
    username: str
    is_admin: bool = False
    is_vip: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: dict = field(default_factory=dict)

@dataclass
class UserProfileUpdatedEvent(IEvent):
    """Evento lanzado cuando se actualiza el perfil de usuario."""
    user_id: int
    changed_fields: List[str]
    old_values: dict
    new_values: dict
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class UserRoleChangedEvent(IEvent):
    """Evento lanzado cuando cambian roles de usuario."""
    user_id: int
    role_type: str  # 'admin' o 'vip'
    old_value: bool
    new_value: bool
    changed_by: Optional[int] = None  # ID del admin que hizo el cambio
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
