"""Modelos para el sistema de administración."""

from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..base import Base, TimestampMixin

class Tariff(Base, TimestampMixin):
    """Define las tarifas para las suscripciones VIP."""
    __tablename__ = "tariffs"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    price = Column(Float, nullable=False)
    duration_days = Column(Integer, nullable=False)

    tokens = relationship("SubscriptionToken", back_populates="tariff")

    def __repr__(self) -> str:
        return f"<Tariff(name='{self.name}', price={self.price}, duration={self.duration_days})>"

class SubscriptionToken(Base, TimestampMixin):
    """Define los tokens de suscripción de un solo uso."""
    __tablename__ = "subscription_tokens"

    id = Column(Integer, primary_key=True)
    token = Column(String(64), nullable=False, unique=True, index=True)
    tariff_id = Column(Integer, ForeignKey("tariffs.id"), nullable=False)
    
    is_used = Column(Boolean, default=False, nullable=False)
    user_id = Column(ForeignKey("users.id"), nullable=True)
    used_at = Column(DateTime(timezone=True), nullable=True)

    tariff = relationship("Tariff", back_populates="tokens")
    user = relationship("User")

    def __repr__(self) -> str:
        return f"<SubscriptionToken(token='{self.token[:8]}...', is_used={self.is_used})>"
