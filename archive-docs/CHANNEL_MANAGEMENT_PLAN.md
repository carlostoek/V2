# Plan de Implementación: Sistema de Administración de Canales

## Visión General

El Sistema de Administración de Canales es una parte crítica de DianaBot V2, que conecta los sistemas de Narrativa y Gamificación, permitiendo el control de acceso y la gestión de contenido tanto para canales gratuitos como VIP. Este documento detalla la estrategia de implementación para este sistema, basándose en la arquitectura limpia y los patrones de diseño ya establecidos.

## Componentes Principales

### 1. Estructura del Sistema de Canales

#### 1.1 Modelos de Datos
- `Channel`: Información básica del canal (ID, tipo, nombre, descripción)
- `ChannelMembership`: Relación entre usuarios y canales
- `ChannelAccess`: Reglas de acceso al canal (requisitos de nivel, VIP, etc.)
- `ChannelContent`: Contenido programado para publicación

#### 1.2 Servicios Core
- `ChannelService`: Gestión de canales y sus configuraciones
- `MembershipService`: Control de membresías y accesos
- `ContentService`: Programación y gestión de contenido
- `NotificationService`: Sistema de notificaciones relacionadas con canales

#### 1.3 Interfaces de Usuario
- Comandos administrativos para gestión de canales
- Teclados personalizados para navegación
- Handlers para gestión de solicitudes de acceso
- Interfaces para programación de contenido

## Implementación Detallada

### Fase 1: Modelos y Servicios Básicos

#### 1. Modelos de Base de Datos

```python
# src/bot/database/models/channel.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from ..base import Base

class Channel(Base):
    __tablename__ = "channels"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(String, unique=True)
    name = Column(String)
    description = Column(String, nullable=True)
    type = Column(String)  # "free" o "vip"
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    is_active = Column(Boolean, default=True)
    settings = Column(JSON, default=dict)
    
    memberships = relationship("ChannelMembership", back_populates="channel")
    access_rules = relationship("ChannelAccess", back_populates="channel")
    content = relationship("ChannelContent", back_populates="channel")

class ChannelMembership(Base):
    __tablename__ = "channel_memberships"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    channel_id = Column(Integer, ForeignKey("channels.id"))
    joined_at = Column(DateTime, default=datetime.now)
    expires_at = Column(DateTime, nullable=True)
    status = Column(String)  # "active", "pending", "expired", "rejected"
    
    user = relationship("User", back_populates="channel_memberships")
    channel = relationship("Channel", back_populates="memberships")

class ChannelAccess(Base):
    __tablename__ = "channel_access"
    
    id = Column(Integer, primary_key=True)
    channel_id = Column(Integer, ForeignKey("channels.id"))
    level_required = Column(Integer, default=1)
    is_vip_only = Column(Boolean, default=False)
    narrative_progress_required = Column(String, nullable=True)
    wait_time_minutes = Column(Integer, default=0)
    
    channel = relationship("Channel", back_populates="access_rules")

class ChannelContent(Base):
    __tablename__ = "channel_content"
    
    id = Column(Integer, primary_key=True)
    channel_id = Column(Integer, ForeignKey("channels.id"))
    content_type = Column(String)  # "post", "trivia", "mission", "narrative"
    content = Column(JSON)
    scheduled_for = Column(DateTime, nullable=True)
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    is_published = Column(Boolean, default=False)
    
    channel = relationship("Channel", back_populates="content")
```

#### 2. Servicios Básicos

```python
# src/modules/channel/service.py
import structlog
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union

from src.core.interfaces.IEventBus import IEventBus
from src.core.interfaces.ICoreService import ICoreService
from src.modules.events import (
    ChannelJoinRequestEvent,
    ChannelJoinApprovedEvent,
    ChannelJoinRejectedEvent,
    ChannelContentPublishedEvent
)
from src.bot.database.models.channel import (
    Channel, ChannelMembership, ChannelAccess, ChannelContent
)
from src.bot.database.engine import get_session

logger = structlog.get_logger(__name__)

class ChannelService(ICoreService):
    """Servicio para gestionar canales y accesos."""
    
    def __init__(self, event_bus: IEventBus):
        self._event_bus = event_bus
        
    async def setup(self) -> None:
        """Configura suscripciones a eventos."""
        self._event_bus.subscribe(ChannelJoinRequestEvent, self.handle_join_request)
        
    async def get_all_channels(self) -> List[Dict[str, Any]]:
        """Obtiene todos los canales configurados."""
        async with get_session() as session:
            query = select(Channel).where(Channel.is_active == True)
            result = await session.execute(query)
            channels = result.scalars().all()
            
            return [
                {
                    "id": channel.id,
                    "telegram_id": channel.telegram_id,
                    "name": channel.name,
                    "type": channel.type,
                    "description": channel.description
                }
                for channel in channels
            ]
    
    async def create_channel(self, 
                            telegram_id: str, 
                            name: str, 
                            channel_type: str, 
                            description: str = None) -> Channel:
        """Crea un nuevo canal."""
        async with get_session() as session:
            channel = Channel(
                telegram_id=telegram_id,
                name=name,
                type=channel_type,
                description=description
            )
            session.add(channel)
            await session.commit()
            
            logger.info(f"Canal creado: {name} ({telegram_id})")
            return channel
    
    async def update_channel(self, 
                           channel_id: int, 
                           **kwargs) -> Optional[Channel]:
        """Actualiza un canal existente."""
        async with get_session() as session:
            channel = await session.get(Channel, channel_id)
            if not channel:
                return None
            
            for key, value in kwargs.items():
                if hasattr(channel, key):
                    setattr(channel, key, value)
            
            await session.commit()
            logger.info(f"Canal actualizado: {channel.name}")
            return channel
    
    async def delete_channel(self, channel_id: int) -> bool:
        """Elimina un canal (marca como inactivo)."""
        async with get_session() as session:
            channel = await session.get(Channel, channel_id)
            if not channel:
                return False
            
            channel.is_active = False
            await session.commit()
            logger.info(f"Canal eliminado: {channel.name}")
            return True
    
    async def set_access_rules(self, 
                             channel_id: int, 
                             level_required: int = 1, 
                             is_vip_only: bool = False,
                             narrative_progress_required: str = None,
                             wait_time_minutes: int = 0) -> Optional[ChannelAccess]:
        """Configura reglas de acceso para un canal."""
        async with get_session() as session:
            channel = await session.get(Channel, channel_id)
            if not channel:
                return None
            
            # Buscar reglas existentes
            query = select(ChannelAccess).where(ChannelAccess.channel_id == channel_id)
            result = await session.execute(query)
            access = result.scalars().first()
            
            if access:
                # Actualizar reglas existentes
                access.level_required = level_required
                access.is_vip_only = is_vip_only
                access.narrative_progress_required = narrative_progress_required
                access.wait_time_minutes = wait_time_minutes
            else:
                # Crear nuevas reglas
                access = ChannelAccess(
                    channel_id=channel_id,
                    level_required=level_required,
                    is_vip_only=is_vip_only,
                    narrative_progress_required=narrative_progress_required,
                    wait_time_minutes=wait_time_minutes
                )
                session.add(access)
            
            await session.commit()
            logger.info(f"Reglas de acceso configuradas para canal {channel.name}")
            return access
    
    async def handle_join_request(self, event: ChannelJoinRequestEvent) -> None:
        """Maneja solicitud de unión a un canal."""
        user_id = event.user_id
        channel_id = event.channel_id
        
        can_join, reason = await self.check_user_can_join(user_id, channel_id)
        
        if can_join:
            await self.add_user_to_channel(user_id, channel_id)
            await self._event_bus.publish(ChannelJoinApprovedEvent(
                user_id=user_id,
                channel_id=channel_id
            ))
        else:
            await self._event_bus.publish(ChannelJoinRejectedEvent(
                user_id=user_id,
                channel_id=channel_id,
                reason=reason
            ))
    
    async def check_user_can_join(self, user_id: int, channel_id: int) -> tuple[bool, str]:
        """Verifica si un usuario puede unirse a un canal."""
        async with get_session() as session:
            # Obtener canal y reglas de acceso
            channel_query = select(Channel).where(Channel.id == channel_id)
            channel_result = await session.execute(channel_query)
            channel = channel_result.scalars().first()
            
            if not channel:
                return False, "Canal no encontrado"
            
            if not channel.is_active:
                return False, "Canal inactivo"
            
            # Obtener reglas de acceso
            access_query = select(ChannelAccess).where(ChannelAccess.channel_id == channel_id)
            access_result = await session.execute(access_query)
            access = access_result.scalars().first()
            
            if not access:
                # Sin reglas de acceso, permitir unirse
                return True, ""
            
            # Verificar nivel del usuario
            from src.bot.database.models.user import User
            user_query = select(User).where(User.id == user_id)
            user_result = await session.execute(user_query)
            user = user_result.scalars().first()
            
            if not user:
                return False, "Usuario no encontrado"
            
            if user.level < access.level_required:
                return False, f"Nivel insuficiente. Necesitas nivel {access.level_required}"
            
            if access.is_vip_only and not user.is_vip:
                return False, "Este canal es solo para usuarios VIP"
            
            # Verificar progreso narrativo si es necesario
            if access.narrative_progress_required:
                from src.bot.database.models.narrative import UserNarrativeState
                narrative_query = select(UserNarrativeState).where(
                    UserNarrativeState.user_id == user_id
                )
                narrative_result = await session.execute(narrative_query)
                narrative_state = narrative_result.scalars().first()
                
                if (not narrative_state or 
                    access.narrative_progress_required not in narrative_state.visited_fragments):
                    return False, "Necesitas avanzar más en la historia"
            
            return True, ""
    
    async def add_user_to_channel(self, user_id: int, channel_id: int, 
                                 expires_at: datetime = None) -> ChannelMembership:
        """Añade un usuario a un canal."""
        async with get_session() as session:
            # Verificar si ya existe una membresía
            query = select(ChannelMembership).where(
                and_(
                    ChannelMembership.user_id == user_id,
                    ChannelMembership.channel_id == channel_id
                )
            )
            result = await session.execute(query)
            membership = result.scalars().first()
            
            if membership:
                # Actualizar membresía existente
                membership.status = "active"
                membership.expires_at = expires_at
            else:
                # Crear nueva membresía
                membership = ChannelMembership(
                    user_id=user_id,
                    channel_id=channel_id,
                    status="active",
                    expires_at=expires_at
                )
                session.add(membership)
            
            await session.commit()
            logger.info(f"Usuario {user_id} añadido al canal {channel_id}")
            return membership
    
    async def remove_user_from_channel(self, user_id: int, channel_id: int) -> bool:
        """Elimina a un usuario de un canal."""
        async with get_session() as session:
            query = select(ChannelMembership).where(
                and_(
                    ChannelMembership.user_id == user_id,
                    ChannelMembership.channel_id == channel_id
                )
            )
            result = await session.execute(query)
            membership = result.scalars().first()
            
            if not membership:
                return False
            
            membership.status = "expired"
            await session.commit()
            logger.info(f"Usuario {user_id} eliminado del canal {channel_id}")
            return True
    
    async def schedule_content(self, 
                              channel_id: int, 
                              content_type: str, 
                              content: Dict[str, Any], 
                              scheduled_for: datetime) -> ChannelContent:
        """Programa contenido para publicación en un canal."""
        async with get_session() as session:
            channel = await session.get(Channel, channel_id)
            if not channel:
                raise ValueError(f"Canal {channel_id} no encontrado")
            
            content_item = ChannelContent(
                channel_id=channel_id,
                content_type=content_type,
                content=content,
                scheduled_for=scheduled_for
            )
            session.add(content_item)
            await session.commit()
            
            logger.info(f"Contenido programado para canal {channel.name} a las {scheduled_for}")
            return content_item
    
    async def get_pending_content(self) -> List[ChannelContent]:
        """Obtiene contenido pendiente de publicación."""
        now = datetime.now()
        
        async with get_session() as session:
            query = select(ChannelContent).where(
                and_(
                    ChannelContent.scheduled_for <= now,
                    ChannelContent.is_published == False
                )
            )
            result = await session.execute(query)
            return result.scalars().all()
    
    async def publish_content(self, content_id: int) -> Optional[ChannelContent]:
        """Marca contenido como publicado."""
        async with get_session() as session:
            content = await session.get(ChannelContent, content_id)
            if not content:
                return None
            
            content.is_published = True
            content.published_at = datetime.now()
            await session.commit()
            
            # Publicar evento
            await self._event_bus.publish(ChannelContentPublishedEvent(
                channel_id=content.channel_id,
                content_id=content.id,
                content_type=content.content_type
            ))
            
            logger.info(f"Contenido {content_id} publicado en canal {content.channel_id}")
            return content
```

### Fase 2: Sistema de Tokens y Accesos VIP

```python
# src/modules/token/service.py
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

import structlog
from sqlalchemy import select, and_, or_

from src.core.interfaces.IEventBus import IEventBus
from src.core.interfaces.ICoreService import ICoreService
from src.modules.events import (
    TokenCreatedEvent,
    TokenRedeemedEvent,
    SubscriptionExpiredEvent
)
from src.bot.database.models.token import (
    Token, Subscription
)
from src.bot.database.models.user import User
from src.bot.database.engine import get_session

logger = structlog.get_logger(__name__)

class TokenService(ICoreService):
    """Servicio para gestionar tokens de acceso VIP."""
    
    def __init__(self, event_bus: IEventBus):
        self._event_bus = event_bus
        
    async def setup(self) -> None:
        """Configura suscripciones a eventos."""
        pass
    
    async def generate_token(self, 
                            token_type: str, 
                            duration_days: int = 30, 
                            max_uses: int = 1,
                            created_by: int = None) -> Token:
        """Genera un nuevo token."""
        token_value = secrets.token_urlsafe(16)
        
        async with get_session() as session:
            token = Token(
                token=token_value,
                type=token_type,
                duration_days=duration_days,
                max_uses=max_uses,
                uses_left=max_uses,
                created_by=created_by
            )
            session.add(token)
            await session.commit()
            
            await self._event_bus.publish(TokenCreatedEvent(
                token_id=token.id,
                token_value=token_value,
                token_type=token_type,
                created_by=created_by
            ))
            
            logger.info(f"Token generado: {token_value} ({token_type})")
            return token
    
    async def validate_token(self, token_value: str) -> Optional[Dict[str, Any]]:
        """Valida un token sin consumirlo."""
        async with get_session() as session:
            query = select(Token).where(Token.token == token_value)
            result = await session.execute(query)
            token = result.scalars().first()
            
            if not token:
                return None
            
            if token.uses_left <= 0:
                return {"valid": False, "reason": "Token agotado"}
            
            if token.expires_at and token.expires_at < datetime.now():
                return {"valid": False, "reason": "Token expirado"}
            
            return {
                "valid": True,
                "token_id": token.id,
                "type": token.type,
                "duration_days": token.duration_days,
                "uses_left": token.uses_left
            }
    
    async def redeem_token(self, token_value: str, user_id: int) -> Optional[Dict[str, Any]]:
        """Canjea un token y activa beneficios."""
        validation = await self.validate_token(token_value)
        if not validation or not validation["valid"]:
            return {"success": False, "reason": validation.get("reason", "Token inválido")}
        
        async with get_session() as session:
            # Obtener token
            token = await session.get(Token, validation["token_id"])
            
            # Reducir usos disponibles
            token.uses_left -= 1
            
            # Registrar uso
            token.last_used_at = datetime.now()
            token.last_used_by = user_id
            
            # Crear suscripción
            duration_days = token.duration_days
            expires_at = datetime.now() + timedelta(days=duration_days)
            
            # Verificar si ya existe una suscripción
            sub_query = select(Subscription).where(
                and_(
                    Subscription.user_id == user_id,
                    Subscription.type == token.type,
                    Subscription.is_active == True
                )
            )
            sub_result = await session.execute(sub_query)
            subscription = sub_result.scalars().first()
            
            if subscription:
                # Extender suscripción existente
                if subscription.expires_at < expires_at:
                    subscription.expires_at = expires_at
            else:
                # Crear nueva suscripción
                subscription = Subscription(
                    user_id=user_id,
                    token_id=token.id,
                    type=token.type,
                    starts_at=datetime.now(),
                    expires_at=expires_at,
                    is_active=True
                )
                session.add(subscription)
            
            # Actualizar estado VIP del usuario
            user_query = select(User).where(User.id == user_id)
            user_result = await session.execute(user_query)
            user = user_result.scalars().first()
            
            if user:
                user.is_vip = True
                user.vip_until = expires_at
            
            await session.commit()
            
            # Publicar evento
            await self._event_bus.publish(TokenRedeemedEvent(
                token_id=token.id,
                user_id=user_id,
                subscription_id=subscription.id,
                expires_at=expires_at.isoformat()
            ))
            
            logger.info(f"Token {token_value} canjeado por usuario {user_id}")
            
            return {
                "success": True,
                "subscription_id": subscription.id,
                "type": token.type,
                "expires_at": expires_at.isoformat()
            }
    
    async def check_expired_subscriptions(self) -> int:
        """Verifica y actualiza suscripciones expiradas."""
        now = datetime.now()
        count = 0
        
        async with get_session() as session:
            # Buscar suscripciones expiradas pero aún activas
            query = select(Subscription).where(
                and_(
                    Subscription.expires_at < now,
                    Subscription.is_active == True
                )
            )
            result = await session.execute(query)
            expired_subs = result.scalars().all()
            
            for sub in expired_subs:
                # Marcar como inactiva
                sub.is_active = False
                
                # Verificar si el usuario tiene otras suscripciones activas
                other_subs_query = select(Subscription).where(
                    and_(
                        Subscription.user_id == sub.user_id,
                        Subscription.id != sub.id,
                        Subscription.is_active == True,
                        Subscription.expires_at > now
                    )
                )
                other_subs_result = await session.execute(other_subs_query)
                has_other_active = other_subs_result.first() is not None
                
                if not has_other_active:
                    # Actualizar estado VIP del usuario
                    user_query = select(User).where(User.id == sub.user_id)
                    user_result = await session.execute(user_query)
                    user = user_result.scalars().first()
                    
                    if user:
                        user.is_vip = False
                        user.vip_until = None
                
                # Publicar evento
                await self._event_bus.publish(SubscriptionExpiredEvent(
                    subscription_id=sub.id,
                    user_id=sub.user_id,
                    subscription_type=sub.type
                ))
                
                count += 1
            
            await session.commit()
            
            if count > 0:
                logger.info(f"Procesadas {count} suscripciones expiradas")
            
            return count
    
    async def get_user_subscriptions(self, user_id: int) -> List[Dict[str, Any]]:
        """Obtiene todas las suscripciones de un usuario."""
        async with get_session() as session:
            query = select(Subscription).where(
                and_(
                    Subscription.user_id == user_id,
                    Subscription.is_active == True
                )
            )
            result = await session.execute(query)
            subscriptions = result.scalars().all()
            
            return [
                {
                    "id": sub.id,
                    "type": sub.type,
                    "starts_at": sub.starts_at.isoformat(),
                    "expires_at": sub.expires_at.isoformat(),
                    "days_left": (sub.expires_at - datetime.now()).days
                }
                for sub in subscriptions
            ]
```

### Fase 3: Sistema de Notificaciones y Eventos

```python
# src/modules/notification/service.py
import structlog
from datetime import datetime
from typing import Dict, List, Optional, Any

from src.core.interfaces.IEventBus import IEventBus
from src.core.interfaces.ICoreService import ICoreService
from src.modules.events import (
    ChannelJoinApprovedEvent,
    ChannelJoinRejectedEvent,
    TokenRedeemedEvent,
    SubscriptionExpiredEvent,
    UserReactionEvent
)
from src.bot.database.engine import get_session

logger = structlog.get_logger(__name__)

class NotificationService(ICoreService):
    """Servicio para gestionar notificaciones y mensajes a usuarios."""
    
    def __init__(self, event_bus: IEventBus):
        self._event_bus = event_bus
        self._bot = None
        self._notification_templates = {
            "channel_join_approved": "¡Felicidades! Tu solicitud para unirte al canal {channel_name} ha sido aprobada. Puedes acceder ahora.",
            "channel_join_rejected": "Lo sentimos, tu solicitud para unirte al canal {channel_name} ha sido rechazada. Motivo: {reason}",
            "token_redeemed": "¡Has activado tu token de acceso! Tu suscripción {subscription_type} está activa hasta {expires_at}.",
            "subscription_expired": "Tu suscripción {subscription_type} ha expirado. Puedes renovarla utilizando un nuevo token.",
            "reaction_received": "¡Has recibido {points} besitos por tu reacción en el canal!"
        }
        
    async def setup(self, bot) -> None:
        """Configura suscripciones a eventos y guarda referencia al bot."""
        self._bot = bot
        
        # Suscribirse a eventos
        self._event_bus.subscribe(ChannelJoinApprovedEvent, self.handle_channel_join_approved)
        self._event_bus.subscribe(ChannelJoinRejectedEvent, self.handle_channel_join_rejected)
        self._event_bus.subscribe(TokenRedeemedEvent, self.handle_token_redeemed)
        self._event_bus.subscribe(SubscriptionExpiredEvent, self.handle_subscription_expired)
        self._event_bus.subscribe(UserReactionEvent, self.handle_reaction)
    
    async def send_notification(self, user_id: int, message: str) -> bool:
        """Envía una notificación a un usuario."""
        if not self._bot:
            logger.error("Bot no configurado en NotificationService")
            return False
        
        try:
            await self._bot.send_message(chat_id=user_id, text=message)
            return True
        except Exception as e:
            logger.error(f"Error al enviar notificación: {e}")
            return False
    
    async def handle_channel_join_approved(self, event: ChannelJoinApprovedEvent) -> None:
        """Maneja notificación de aprobación de unión a canal."""
        # Obtener información del canal
        async with get_session() as session:
            from src.bot.database.models.channel import Channel
            query = select(Channel).where(Channel.id == event.channel_id)
            result = await session.execute(query)
            channel = result.scalars().first()
            
            if not channel:
                return
            
            # Preparar mensaje
            message = self._notification_templates["channel_join_approved"].format(
                channel_name=channel.name
            )
            
            # Enviar notificación
            await self.send_notification(event.user_id, message)
    
    async def handle_channel_join_rejected(self, event: ChannelJoinRejectedEvent) -> None:
        """Maneja notificación de rechazo de unión a canal."""
        # Obtener información del canal
        async with get_session() as session:
            from src.bot.database.models.channel import Channel
            query = select(Channel).where(Channel.id == event.channel_id)
            result = await session.execute(query)
            channel = result.scalars().first()
            
            if not channel:
                return
            
            # Preparar mensaje
            message = self._notification_templates["channel_join_rejected"].format(
                channel_name=channel.name,
                reason=event.reason
            )
            
            # Enviar notificación
            await self.send_notification(event.user_id, message)
    
    async def handle_token_redeemed(self, event: TokenRedeemedEvent) -> None:
        """Maneja notificación de token canjeado."""
        # Obtener información de la suscripción
        async with get_session() as session:
            from src.bot.database.models.token import Subscription
            query = select(Subscription).where(Subscription.id == event.subscription_id)
            result = await session.execute(query)
            subscription = result.scalars().first()
            
            if not subscription:
                return
            
            # Formatear fecha
            import datetime
            expires_at = datetime.datetime.fromisoformat(event.expires_at)
            formatted_date = expires_at.strftime("%d/%m/%Y")
            
            # Preparar mensaje
            message = self._notification_templates["token_redeemed"].format(
                subscription_type=subscription.type,
                expires_at=formatted_date
            )
            
            # Enviar notificación
            await self.send_notification(event.user_id, message)
    
    async def handle_subscription_expired(self, event: SubscriptionExpiredEvent) -> None:
        """Maneja notificación de suscripción expirada."""
        # Preparar mensaje
        message = self._notification_templates["subscription_expired"].format(
            subscription_type=event.subscription_type
        )
        
        # Enviar notificación
        await self.send_notification(event.user_id, message)
    
    async def handle_reaction(self, event: UserReactionEvent) -> None:
        """Maneja notificación de reacción recibida."""
        # Preparar mensaje
        message = self._notification_templates["reaction_received"].format(
            points=event.points
        )
        
        # Enviar notificación
        await self.send_notification(event.user_id, message)
```

### Fase 4: Comandos de Administración

```python
# src/bot/handlers/admin/channel_commands.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from src.bot.core.containers import container
from src.modules.channel.service import ChannelService
from src.bot.keyboards.admin.channel_kb import (
    create_channel_management_kb,
    create_channel_list_kb,
    create_channel_config_kb
)

# Crear router
router = Router()

# Estados para FSM
class ChannelForm(StatesGroup):
    waiting_for_channel_id = State()
    waiting_for_channel_name = State()
    waiting_for_channel_type = State()
    waiting_for_channel_description = State()
    
    waiting_for_level_required = State()
    waiting_for_vip_only = State()
    waiting_for_wait_time = State()

# Comando para listar canales
@router.message(Command("admin_channels"))
async def cmd_admin_channels(message: Message):
    """Muestra la lista de canales configurados."""
    # Verificar permisos de administrador
    # TODO: Implementar middleware de comprobación de admin
    
    channel_service = container.services.channel_service()
    channels = await channel_service.get_all_channels()
    
    if not channels:
        await message.answer("No hay canales configurados.")
        return
    
    text = "📢 Canales configurados:\n\n"
    for i, channel in enumerate(channels, 1):
        text += f"{i}. {channel['name']} ({channel['type']})\n"
    
    keyboard = create_channel_list_kb(channels)
    await message.answer(text, reply_markup=keyboard)

# Callback para gestionar un canal
@router.callback_query(F.data.startswith("channel_manage_"))
async def cb_channel_manage(callback: CallbackQuery):
    """Muestra opciones de gestión para un canal específico."""
    channel_id = int(callback.data.split("_")[2])
    
    channel_service = container.services.channel_service()
    channels = await channel_service.get_all_channels()
    
    channel = next((c for c in channels if c["id"] == channel_id), None)
    if not channel:
        await callback.answer("Canal no encontrado")
        return
    
    text = f"🛠️ Gestión del canal: {channel['name']}\n"
    text += f"Tipo: {channel['type']}\n"
    text += f"ID de Telegram: {channel['telegram_id']}\n"
    
    keyboard = create_channel_management_kb(channel_id)
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

# Comando para crear un nuevo canal
@router.message(Command("create_channel"))
async def cmd_create_channel(message: Message, state: FSMContext):
    """Inicia el proceso de creación de un canal."""
    await message.answer("Vamos a crear un nuevo canal. Por favor, envía el ID de Telegram del canal.")
    await state.set_state(ChannelForm.waiting_for_channel_id)

# Manejador para recibir ID de Telegram
@router.message(ChannelForm.waiting_for_channel_id)
async def process_channel_id(message: Message, state: FSMContext):
    """Procesa el ID de Telegram del canal."""
    telegram_id = message.text.strip()
    
    # Validar formato
    if not telegram_id.startswith("-100"):
        await message.answer("El ID debe comenzar con -100. Por favor, envía un ID válido.")
        return
    
    await state.update_data(telegram_id=telegram_id)
    await message.answer("Ahora, envía el nombre del canal.")
    await state.set_state(ChannelForm.waiting_for_channel_name)

# Continuar con los manejadores para el resto de estados...

# Manejador para finalizar creación de canal
@router.message(ChannelForm.waiting_for_channel_description)
async def process_channel_description(message: Message, state: FSMContext):
    """Procesa la descripción y crea el canal."""
    description = message.text.strip()
    
    # Obtener datos guardados
    data = await state.get_data()
    telegram_id = data.get("telegram_id")
    name = data.get("name")
    channel_type = data.get("type")
    
    # Crear canal
    channel_service = container.services.channel_service()
    try:
        channel = await channel_service.create_channel(
            telegram_id=telegram_id,
            name=name,
            channel_type=channel_type,
            description=description
        )
        
        await message.answer(f"✅ Canal creado correctamente:\n"
                           f"Nombre: {channel.name}\n"
                           f"Tipo: {channel.type}\n"
                           f"ID: {channel.telegram_id}")
    except Exception as e:
        await message.answer(f"❌ Error al crear el canal: {str(e)}")
    
    # Limpiar estado
    await state.clear()
```

## Implementación por Etapas

### Etapa 1: Modelos y Servicios Básicos (Días 1-3)
1. Implementar modelos de base de datos para Canales
2. Desarrollar `ChannelService` básico
3. Crear eventos relacionados con canales
4. Implementar pruebas unitarias básicas

### Etapa 2: Sistema de Tokens y Accesos VIP (Días 4-6)
1. Implementar modelos para Tokens y Suscripciones
2. Desarrollar `TokenService`
3. Integrar con el sistema de usuarios
4. Añadir pruebas unitarias para la gestión de tokens

### Etapa 3: Notificaciones y Eventos (Días 7-8)
1. Implementar `NotificationService`
2. Configurar manejadores de eventos
3. Desarrollar plantillas de mensajes
4. Añadir pruebas para notificaciones

### Etapa 4: Comandos y UI Admin (Días 9-11)
1. Implementar comandos de administración
2. Crear teclados personalizados
3. Implementar formularios para gestión de canales
4. Desarrollar interfaz para tokens y suscripciones

### Etapa 5: Integración y Pruebas (Días 12-14)
1. Integrar con sistemas de Narrativa y Gamificación
2. Implementar pruebas de integración
3. Realizar pruebas de flujo completo
4. Optimizar y refinar

## Diagrama de Componentes

```
                          +------------------+
                          |                  |
                          |  Bot Orchestrator|
                          |                  |
                          +--------+---------+
                                   |
                   +---------------+---------------+
                   |               |               |
        +----------v-----+ +-------v-------+ +----v-----------+
        |                | |               | |                |
        | Channel Service| | Token Service | |Notification Svc|
        |                | |               | |                |
        +----------+-----+ +-------+-------+ +----+-----------+
                   |               |               |
        +----------v---------------v---------------v-----------+
        |                                                      |
        |                  Database Layer                      |
        |                                                      |
        +------------------------------------------------------+
```

## Integraciones con Otros Sistemas

### Integración con Narrativa
- Verificación de progreso narrativo para acceso a canales
- Publicación de fragmentos narrativos en canales
- Desbloqueo de fragmentos especiales para usuarios VIP

### Integración con Gamificación
- Otorgar puntos por participación en canales
- Misiones relacionadas con canales
- Uso de besitos para accesos especiales

## Consideraciones de Seguridad

1. Validación de tokens con límite de usos
2. Expiración automática de suscripciones
3. Verificación de permisos para comandos administrativos
4. Protección contra spam en solicitudes de canales

## Conclusión

La implementación del Sistema de Administración de Canales proporcionará una base sólida para gestionar los diferentes tipos de acceso y contenido en DianaBot V2. La arquitectura modular permitirá una fácil expansión y la integración con los sistemas de Narrativa y Gamificación facilitará una experiencia de usuario coherente y enriquecedora.

Este sistema es una pieza fundamental del ecosistema del bot, actuando como puente entre la experiencia narrativa y los mecanismos de gamificación, permitiendo así una monetización efectiva y una gestión eficiente del contenido.