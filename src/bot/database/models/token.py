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


class Subscription(Base, TimestampMixin):
    """Modelo para almacenar suscripciones activas de usuarios."""
    
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    token_id = Column(Integer, ForeignKey("subscription_tokens.id"), nullable=True)
    
    # Información de la suscripción
    type = Column(String(50), nullable=False)  # "vip", "premium", etc.
    starts_at = Column(DateTime, nullable=False, default=datetime.now)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Metadatos adicionales
    extra_data = Column(JSON, default={})
    
    # Relaciones
    user = relationship("User", back_populates="subscriptions")
    token = relationship("SubscriptionToken")
    
    def __repr__(self) -> str:
        """Representación de texto de la suscripción."""
        return f"<Subscription(id={self.id}, user_id={self.user_id}, type={self.type}, active={self.is_active})>"


class Token(Base, TimestampMixin):
    """Modelo genérico para tokens de acceso."""
    
    __tablename__ = "tokens"
    
    id = Column(Integer, primary_key=True)
    token = Column(String(64), unique=True, nullable=False)
    type = Column(String(50), nullable=False)  # "vip", "channel_access", "reward"
    
    # Configuración del token
    duration_days = Column(Integer, nullable=False)
    max_uses = Column(Integer, default=1)
    uses_left = Column(Integer, nullable=False)
    
    # Control de uso
    created_by = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    last_used_by = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    last_used_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    
    # Metadatos
    extra_data = Column(JSON, default={})
    
    # Relaciones
    creator = relationship("User", foreign_keys=[created_by])
    last_user = relationship("User", foreign_keys=[last_used_by])
    
    def __repr__(self) -> str:
        """Representación de texto del token."""
        return f"<Token(id={self.id}, type={self.type}, uses_left={self.uses_left})>"