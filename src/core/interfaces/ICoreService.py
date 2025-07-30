from abc import ABC, abstractmethod

class ICoreService(ABC):
    """Define el contrato para los servicios principales del sistema."""

    @abstractmethod
    async def setup(self) -> None:
        """Configura y suscribe el servicio al bus de eventos."""
        pass
