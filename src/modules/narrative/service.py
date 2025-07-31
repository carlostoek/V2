from src.core.interfaces.IEventBus import IEventBus
from src.core.interfaces.ICoreService import ICoreService
from src.modules.events import UserStartedBotEvent

class NarrativeService(ICoreService):
    """Servicio para manejar la lógica de la narrativa."""

    def __init__(self, event_bus: IEventBus):
        self._event_bus = event_bus
        self.story_fragments_to_send = {}

    async def setup(self) -> None:
        """Suscribe el servicio a los eventos relevantes."""
        self._event_bus.subscribe(UserStartedBotEvent, self.handle_user_started)

    async def handle_user_started(self, event: UserStartedBotEvent) -> None:
        """Entrega un mensaje de bienvenida al usuario."""
        user_id = event.user_id
        print(f"[Narrative] Entregando mensaje de bienvenida a {user_id}.")
        self.story_fragments_to_send[user_id] = "welcome_story_fragment"
