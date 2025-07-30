from src.core.interfaces.IEventBus import IEventBus
from src.core.interfaces.ICoreService import ICoreService
from src.modules.events import PointsAwardedEvent, ReactionAddedEvent

class NarrativeService(ICoreService):
    """Servicio para manejar la lógica de la narrativa."""

    def __init__(self, event_bus: IEventBus):
        self._event_bus = event_bus
        self.story_fragments_to_send = {}

    async def setup(self) -> None:
        """Suscribe el servicio a los eventos relevantes."""
        self._event_bus.subscribe(PointsAwardedEvent, self.handle_points_awarded)

    async def handle_points_awarded(self, event: PointsAwardedEvent) -> None:
        """Si los puntos vienen de una reacción, asigna una historia."""
        if event.source_event == ReactionAddedEvent.__name__:
            user_id = event.user_id
            print(f"[Narrative] Puntos por reacción para {user_id}. Asignando fragmento de historia.")
            self.story_fragments_to_send[user_id] = "intro_story_fragment_1"
