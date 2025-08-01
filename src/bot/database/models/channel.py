"""Modelos para el sistema de administración de canales."""

from sqlalchemy import Column, BigInteger, String, Boolean, Integer, DateTime, JSON, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from ..base import Base, TimestampMixin

class Channel(Base, TimestampMixin):
    """Modelo para almacenar información de canales."""
    
    __tablename__ = "channels"
    
    # Campos principales
    id = Column(Integer, primary_key=True)
    telegram_id = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    type = Column(String(50), nullable=False)  # "free" o "vip"
    
    # Configuración y estado
    is_active = Column(Boolean, default=True)
    settings = Column(JSON, default={})
    
    # Relaciones
    memberships = relationship("ChannelMembership", back_populates="channel", cascade="all, delete-orphan")
    access_rules = relationship("ChannelAccess", back_populates="channel", cascade="all, delete-orphan", uselist=False)
    content = relationship("ChannelContent", back_populates="channel", cascade="all, delete-orphan")
    tariffs = relationship("Tariff", back_populates="channel", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        """Representación de texto del canal."""
        return f"<Channel(id={self.id}, name={self.name}, type={self.type})>"


class ChannelMembership(Base, TimestampMixin):
    """Modelo para almacenar la relación entre usuarios y canales."""
    
    __tablename__ = "channel_memberships"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=False)
    
    # Estado de la membresía
    status = Column(String(50), default="active")  # "active", "pending", "expired", "rejected"
    joined_at = Column(DateTime(timezone=True), default=datetime.now)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Datos adicionales
    user_metadata = Column(JSON, default={})
    
    # Relaciones
    user = relationship("User", back_populates="channel_memberships")
    channel = relationship("Channel", back_populates="memberships")
    
    def __repr__(self) -> str:
        """Representación de texto de la membresía."""
        return f"<ChannelMembership(user_id={self.user_id}, channel_id={self.channel_id}, status={self.status})>"


class ChannelAccess(Base, TimestampMixin):
    """Modelo para almacenar reglas de acceso a canales."""
    
    __tablename__ = "channel_access"
    
    id = Column(Integer, primary_key=True)
    channel_id = Column(Integer, ForeignKey("channels.id"), unique=True, nullable=False)
    
    # Requisitos de acceso
    level_required = Column(Integer, default=1)
    is_vip_only = Column(Boolean, default=False)
    narrative_progress_required = Column(String(255), nullable=True)
    wait_time_minutes = Column(Integer, default=0)
    
    # Reglas adicionales
    max_members = Column(Integer, nullable=True)
    require_approval = Column(Boolean, default=False)
    auto_kick_expired = Column(Boolean, default=True)
    
    # Relaciones
    channel = relationship("Channel", back_populates="access_rules")
    
    def __repr__(self) -> str:
        """Representación de texto de las reglas de acceso."""
        return f"<ChannelAccess(channel_id={self.channel_id}, level={self.level_required}, vip={self.is_vip_only})>"


class ChannelContent(Base, TimestampMixin):
    """Modelo para almacenar contenido programado para canales."""
    
    __tablename__ = "channel_content"
    
    id = Column(Integer, primary_key=True)
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=False)
    
    # Información del contenido
    content_type = Column(String(50), nullable=False)  # "post", "trivia", "mission", "narrative"
    content = Column(JSON, nullable=False)
    message_id = Column(BigInteger, nullable=True)  # ID del mensaje en Telegram (después de publicar)
    
    # Programación
    scheduled_for = Column(DateTime(timezone=True), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    is_published = Column(Boolean, default=False)
    
    # Estadísticas
    views = Column(Integer, default=0)
    reactions = Column(Integer, default=0)
    interactions = Column(JSON, default={})
    
    # Relaciones
    channel = relationship("Channel", back_populates="content")
    
    def __repr__(self) -> str:
        """Representación de texto del contenido."""
        return f"<ChannelContent(id={self.id}, channel_id={self.channel_id}, type={self.content_type})>"