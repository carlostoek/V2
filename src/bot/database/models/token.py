"""Modelos para el sistema de tokens y tarifas."""

from datetime import datetime
from typing import Dict, List, Optional, Any

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, BigInteger
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship

from src.bot.database.base import Base, TimestampMixin


class Tariff(Base, TimestampMixin):
    """Modelo para almacenar tarifas de suscripción."""
    
    __tablename__ = "tariffs"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    duration_days = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    token_validity_days = Column(Integer, default=7)
    description = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=False)
    
    # Relaciones
    channel = relationship("Channel", back_populates="tariffs")
    tokens = relationship("SubscriptionToken", back_populates="tariff", cascade="all, delete-orphan")


class SubscriptionToken(Base, TimestampMixin):
    """Modelo para almacenar tokens de suscripción."""
    
    __tablename__ = "subscription_tokens"
    
    id = Column(Integer, primary_key=True)
    token = Column(String(64), unique=True, nullable=False)
    tariff_id = Column(Integer, ForeignKey("tariffs.id"), nullable=False)
    generated_by = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    is_used = Column(Boolean, default=False)
    used_by = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    used_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=False)
    
    # Relaciones
    tariff = relationship("Tariff", back_populates="tokens")
    generator = relationship("User", foreign_keys=[generated_by])
    user = relationship("User", foreign_keys=[used_by])