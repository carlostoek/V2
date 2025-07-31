"""Servicio de administración para el bot."""

import structlog
from src.core.interfaces.IEventBus import IEventBus

logger = structlog.get_logger()

class AdminService:
    """Servicio para manejar la lógica de administración."""

    def __init__(self, event_bus: IEventBus):
        self._event_bus = event_bus
        self.free_channel_id = None
        self.wait_time_minutes = 15

    async def setup(self) -> None:
        """Suscribe el servicio a los eventos relevantes."""
        logger.info("AdminService configurado")
        
    def set_free_channel_id(self, channel_id: int) -> None:
        """Guarda el ID del canal gratuito."""
        logger.info(f"Canal gratuito configurado con ID: {channel_id}")
        self.free_channel_id = channel_id

    def get_free_channel_id(self) -> int:
        """Recupera el ID del canal gratuito."""
        return self.free_channel_id

    def set_wait_time(self, minutes: int) -> None:
        """Guarda el tiempo de espera para el canal gratuito."""
        logger.info(f"Tiempo de espera configurado a: {minutes} minutos")
        self.wait_time_minutes = minutes

    def get_wait_time(self) -> int:
        """Recupera el tiempo de espera para el canal gratuito."""
        return self.wait_time_minutes