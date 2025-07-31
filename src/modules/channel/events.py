"""Eventos relacionados con el sistema de administración de canales."""

from src.core.interfaces.IEventBus import IEvent
from typing import Dict, Optional, Any


class ChannelJoinRequestEvent(IEvent):
    """Evento que se dispara cuando un usuario solicita unirse a un canal."""
    def __init__(self, user_id: int, channel_id: int):
        self.user_id = user_id
        self.channel_id = channel_id


class ChannelJoinApprovedEvent(IEvent):
    """Evento que se dispara cuando se aprueba la solicitud de un usuario para unirse a un canal."""
    def __init__(self, user_id: int, channel_id: int):
        self.user_id = user_id
        self.channel_id = channel_id


class ChannelJoinRejectedEvent(IEvent):
    """Evento que se dispara cuando se rechaza la solicitud de un usuario para unirse a un canal."""
    def __init__(self, user_id: int, channel_id: int, reason: str):
        self.user_id = user_id
        self.channel_id = channel_id
        self.reason = reason


class ChannelContentPublishedEvent(IEvent):
    """Evento que se dispara cuando se publica contenido en un canal."""
    def __init__(self, channel_id: int, content_id: int, content_type: str):
        self.channel_id = channel_id
        self.content_id = content_id
        self.content_type = content_type


class ChannelMembershipExpiredEvent(IEvent):
    """Evento que se dispara cuando expira la membresía de un usuario en un canal."""
    def __init__(self, user_id: int, channel_id: int):
        self.user_id = user_id
        self.channel_id = channel_id


class UserReactionEvent(IEvent):
    """Evento que se dispara cuando un usuario reacciona a contenido en un canal."""
    def __init__(self, user_id: int, channel_id: int, content_id: int, reaction_type: str, points: int = 5):
        self.user_id = user_id
        self.channel_id = channel_id
        self.content_id = content_id
        self.reaction_type = reaction_type
        self.points = points