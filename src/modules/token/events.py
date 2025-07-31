"""Eventos relacionados con el sistema de tokens."""

from datetime import datetime
from src.core.interfaces.IEventBus import IEvent
from typing import Dict, Optional, Any


class TokenGeneratedEvent(IEvent):
    """Evento que se dispara cuando se genera un token de suscripción."""
    def __init__(self, token_id: int, tariff_id: int, admin_id: int):
        self.token_id = token_id
        self.tariff_id = tariff_id
        self.admin_id = admin_id


class TokenRedeemedEvent(IEvent):
    """Evento que se dispara cuando se canjea un token de suscripción."""
    def __init__(self, token_id: int, user_id: int, channel_id: int, expiry_date: datetime):
        self.token_id = token_id
        self.user_id = user_id
        self.channel_id = channel_id
        self.expiry_date = expiry_date


class TokenExpiredEvent(IEvent):
    """Evento que se dispara cuando expira un token sin usar."""
    def __init__(self, token_id: int, tariff_id: int):
        self.token_id = token_id
        self.tariff_id = tariff_id


class TariffCreatedEvent(IEvent):
    """Evento que se dispara cuando se crea una nueva tarifa."""
    def __init__(self, tariff_id: int, channel_id: int, admin_id: int):
        self.tariff_id = tariff_id
        self.channel_id = channel_id
        self.admin_id = admin_id


class TariffUpdatedEvent(IEvent):
    """Evento que se dispara cuando se actualiza una tarifa."""
    def __init__(self, tariff_id: int, admin_id: int, changes: Dict[str, Any]):
        self.tariff_id = tariff_id
        self.admin_id = admin_id
        self.changes = changes