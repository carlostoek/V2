import asyncio
from collections import defaultdict
from typing import Callable, List, Type, Dict, Set
from inspect import getmembers, ismethod
import logging

from .interfaces.IEventBus import IEvent, IEventBus

logger = logging.getLogger(__name__)

class EventBus(IEventBus):
    """Implementación avanzada del bus de eventos con suscripción automática."""

    def __init__(self):
        self._subscribers: Dict[Type[IEvent], List[Callable]] = defaultdict(list)
        self._discovered_handlers: Set[str] = set()

    def subscribe(self, event_type: Type[IEvent], handler: Callable) -> None:
        """Suscribe un manejador a un evento."""
        self._subscribers[event_type].append(handler)
        logger.debug(f"Handler {handler.__name__} subscribed to {event_type.__name__}")

    async def publish(self, event: IEvent) -> None:
        """Publica un evento, notificando a todos los suscriptores.
        
        Args:
            event: Instancia del evento a publicar
            
        Note:
            Continúa ejecución incluso si algún handler falla
            Los errores son logueados pero no propagados
        """
        event_type = type(event)
        if event_type not in self._subscribers:
            logger.debug(f"No hay handlers para {event_type.__name__}")
            return

        logger.debug(f"Publicando {event_type.__name__} a {len(self._subscribers[event_type])} handlers")
        
        async def safe_handler(handler):
            try:
                return await handler(event)
            except Exception as e:
                logger.error(f"Error en handler {handler.__name__}",
                           event=event_type.__name__,
                           error=str(e),
                           exc_info=True)
                return None

        tasks = [safe_handler(handler) for handler in self._subscribers[event_type]]
        await asyncio.gather(*tasks)

    def auto_subscribe(self, instance: object) -> None:
        """Busca y suscribe automáticamente métodos que manejan eventos."""
        for _, method in getmembers(instance, ismethod):
            if hasattr(method, '_handles_event'):
                event_type = method._handles_event
                self.subscribe(event_type, method)
                logger.info(f"Auto-subscribed {instance.__class__.__name__}.{method.__name__} to {event_type.__name__}")

def handles_event(event_type: Type[IEvent]):
    """Decorador para marcar métodos como manejadores de eventos."""
    def decorator(method):
        method._handles_event = event_type
        return method
    return decorator
