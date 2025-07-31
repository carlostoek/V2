from src.core.interfaces.IEventBus import IEvent, IEventBus
from src.core.interfaces.ICoreService import ICoreService
from src.modules.events import ReactionAddedEvent, PointsAwardedEvent, UserStartedBotEvent

class GamificationService(ICoreService):
    """Servicio para manejar la lógica de gamificación."""

    def __init__(self, event_bus: IEventBus):
        self._event_bus = event_bus
        self.points = {}

    async def setup(self) -> None:
        """Suscribe el servicio a los eventos relevantes."""
        self._event_bus.subscribe(ReactionAddedEvent, self.handle_reaction_added)
        self._event_bus.subscribe(UserStartedBotEvent, self.handle_user_started)

    async def _award_points(self, user_id: int, points_to_award: int, source_event: IEvent):
        """Otorga puntos a un usuario y publica un evento."""
        print(f"[Gamification] Evento {source_event.__class__.__name__} para {user_id}. Otorgando {points_to_award} puntos.")
        self.points[user_id] = self.points.get(user_id, 0) + points_to_award
        
        points_event = PointsAwardedEvent(
            user_id=user_id, 
            points=points_to_award, 
            source_event=source_event.__class__.__name__
        )
        await self._event_bus.publish(points_event)

    async def handle_reaction_added(self, event: ReactionAddedEvent) -> None:
        """Maneja el evento de reacción para otorgar puntos."""
        await self._award_points(event.user_id, event.points_to_award, event)

    async def handle_user_started(self, event: UserStartedBotEvent) -> None:
        """Maneja el evento de inicio de bot para otorgar puntos de bienvenida."""
        # Solo otorga puntos la primera vez
        if self.points.get(event.user_id, 0) == 0:
            await self._award_points(event.user_id, 10, event)

    def get_points(self, user_id: int) -> int:
        """Consulta los puntos de un usuario."""
        return self.points.get(user_id, 0)
