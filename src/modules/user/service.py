from src.core.interfaces.IEventBus import IEventBus
from src.core.interfaces.ICoreService import ICoreService
from src.modules.events import UserStartedBotEvent

class UserService(ICoreService):
    """Servicio para manejar la lógica de usuarios."""

    def __init__(self, event_bus: IEventBus):
        self._event_bus = event_bus
        self.users = set()

    async def setup(self) -> None:
        self._event_bus.subscribe(UserStartedBotEvent, self.handle_user_started)

    async def handle_user_started(self, event: UserStartedBotEvent) -> None:
        if event.user_id not in self.users:
            print(f"[User Service] Nuevo usuario registrado: {event.user_id} (@{event.username})")
            self.users.add(event.user_id)
        else:
            print(f"[User Service] Usuario recurrente: {event.user_id}")
