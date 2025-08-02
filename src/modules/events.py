from src.core.interfaces.IEventBus import IEvent
from typing import Dict, List, Optional, Any
from datetime import datetime

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

# ============================================
# EVENTOS DEL SISTEMA DE CANALES
# ============================================

class ChannelJoinRequestEvent(IEvent):
    """Evento que se dispara cuando un usuario solicita unirse a un canal."""
    def __init__(self, user_id: int, channel_id: int, request_metadata: Optional[Dict[str, Any]] = None):
        self.user_id = user_id
        self.channel_id = channel_id
        self.request_metadata = request_metadata or {}
        self.timestamp = datetime.now().isoformat()

class ChannelJoinApprovedEvent(IEvent):
    """Evento que se dispara cuando se aprueba la solicitud de unión a un canal."""
    def __init__(self, user_id: int, channel_id: int, approved_by: Optional[int] = None):
        self.user_id = user_id
        self.channel_id = channel_id
        self.approved_by = approved_by
        self.timestamp = datetime.now().isoformat()

class ChannelJoinRejectedEvent(IEvent):
    """Evento que se dispara cuando se rechaza la solicitud de unión a un canal."""
    def __init__(self, user_id: int, channel_id: int, reason: str, rejected_by: Optional[int] = None):
        self.user_id = user_id
        self.channel_id = channel_id
        self.reason = reason
        self.rejected_by = rejected_by
        self.timestamp = datetime.now().isoformat()

class ChannelContentPublishedEvent(IEvent):
    """Evento que se dispara cuando se publica contenido en un canal."""
    def __init__(self, channel_id: int, content_id: int, content_type: str, published_by: Optional[int] = None):
        self.channel_id = channel_id
        self.content_id = content_id
        self.content_type = content_type
        self.published_by = published_by
        self.timestamp = datetime.now().isoformat()

class UserReactionEvent(IEvent):
    """Evento que se dispara cuando un usuario reacciona a contenido de canal."""
    def __init__(self, user_id: int, channel_id: int, content_id: int, reaction_type: str, points: int = 0):
        self.user_id = user_id
        self.channel_id = channel_id
        self.content_id = content_id
        self.reaction_type = reaction_type
        self.points = points
        self.timestamp = datetime.now().isoformat()

# ============================================
# EVENTOS DEL SISTEMA DE TOKENS
# ============================================

class TokenCreatedEvent(IEvent):
    """Evento que se dispara cuando se crea un nuevo token."""
    def __init__(self, token_id: int, token_value: str, token_type: str, created_by: Optional[int] = None):
        self.token_id = token_id
        self.token_value = token_value
        self.token_type = token_type
        self.created_by = created_by
        self.timestamp = datetime.now().isoformat()

class TokenRedeemedEvent(IEvent):
    """Evento que se dispara cuando un usuario canjea un token."""
    def __init__(self, token_id: int, user_id: int, subscription_id: int, expires_at: str):
        self.token_id = token_id
        self.user_id = user_id
        self.subscription_id = subscription_id
        self.expires_at = expires_at
        self.timestamp = datetime.now().isoformat()

class SubscriptionExpiredEvent(IEvent):
    """Evento que se dispara cuando una suscripción expira."""
    def __init__(self, subscription_id: int, user_id: int, subscription_type: str):
        self.subscription_id = subscription_id
        self.user_id = user_id
        self.subscription_type = subscription_type
        self.timestamp = datetime.now().isoformat()

class ChannelMembershipChangedEvent(IEvent):
    """Evento que se dispara cuando cambia la membresía de un usuario a un canal."""
    def __init__(self, user_id: int, channel_id: int, old_status: str, new_status: str, changed_by: Optional[int] = None):
        self.user_id = user_id
        self.channel_id = channel_id
        self.old_status = old_status
        self.new_status = new_status
        self.changed_by = changed_by
        self.timestamp = datetime.now().isoformat()