from src.core.interfaces.IEventBus import IEventBus
from src.modules.events import ReactionAddedEvent

class TelegramListener:
    """Simula la recepción de eventos desde la API de Telegram."""

    def __init__(self, event_bus: IEventBus):
        self._event_bus = event_bus

    async def simulate_reaction(self, user_id: int, message_id: int) -> None:
        """Simula una reacción y publica el evento correspondiente."""
        print(f"[Telegram Listener] Reacción recibida del usuario {user_id}")
        event = ReactionAddedEvent(user_id=user_id, message_id=message_id)
        await self._event_bus.publish(event)
