from src.core.interfaces.IEventBus import IEventBus
from src.core.interfaces.ICoreService import ICoreService
from src.modules.events import ReactionAddedEvent, PointsAwardedEvent

class GamificationService(ICoreService):
    """Servicio para manejar la lógica de gamificación."""

    def __init__(self, event_bus: IEventBus):
        self._event_bus = event_bus
        self.points = {}

    async def setup(self) -> None:
        """Suscribe el servicio a los eventos relevantes."""
        self._event_bus.subscribe(ReactionAddedEvent, self.handle_reaction_added)

    async def handle_reaction_added(self, event: ReactionAddedEvent) -> None:
        """Maneja el evento de reacción, otorga puntos y publica un nuevo evento."""
        user_id = event.user_id
        points = event.points_to_award
        
        print(f"[Gamification] Reacción de {user_id}. Otorgando {points} puntos.")
        self.points[user_id] = self.points.get(user_id, 0) + points
        
        points_event = PointsAwardedEvent(
            user_id=user_id, 
            points=points, 
            source_event=ReactionAddedEvent.__name__
        )
        await self._event_bus.publish(points_event)

    def get_points(self, user_id: int) -> int:
        """Consulta los puntos de un usuario."""
        return self.points.get(user_id, 0)
