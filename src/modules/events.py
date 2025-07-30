from src.core.interfaces.IEventBus import IEvent

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
