from abc import ABC, abstractmethod
from typing import Callable, Any, Type

class IEvent(ABC):
    """Clase base para todos los eventos del sistema."""
    pass

class IEventBus(ABC):
    """Define el contrato para el bus de eventos del sistema."""

    @abstractmethod
    async def publish(self, event: IEvent) -> None:
        """Publica un evento en el bus."""
        pass

    @abstractmethod
    def subscribe(self, event_type: Type[IEvent], handler: Callable) -> None:
        """Suscribe un manejador a un tipo de evento específico."""
        pass
