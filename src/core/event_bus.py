import asyncio
from collections import defaultdict
from typing import Callable, List, Type, Dict

from .interfaces.IEventBus import IEvent, IEventBus

class EventBus(IEventBus):
    """Implementación concreta del bus de eventos."""

    def __init__(self):
        self._subscribers: Dict[Type[IEvent], List[Callable]] = defaultdict(list)

    def subscribe(self, event_type: Type[IEvent], handler: Callable) -> None:
        """Suscribe un manejador a un evento."""
        self._subscribers[event_type].append(handler)

    async def publish(self, event: IEvent) -> None:
        """Publica un evento, notificando a todos los suscriptores."""
        event_type = type(event)
        if event_type in self._subscribers:
            tasks = [handler(event) for handler in self._subscribers[event_type]]
            await asyncio.gather(*tasks)
