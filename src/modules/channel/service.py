"""Servicio para la gestión de canales."""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta

from sqlalchemy import select, update, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.interfaces.IEventBus import IEvent, IEventBus
from src.core.interfaces.ICoreService import ICoreService
from src.modules.channel.events import (
    ChannelJoinRequestEvent,
    ChannelJoinApprovedEvent,
    ChannelJoinRejectedEvent,
    ChannelContentPublishedEvent,
    ChannelMembershipExpiredEvent,
    UserReactionEvent
)
from src.bot.database.engine import get_session
from src.bot.database.models.user import User
from src.bot.database.models.channel import (
    Channel,
    ChannelMembership,
    ChannelAccess,
    ChannelContent
)


class ChannelService(ICoreService):
    """
    Servicio para manejar la lógica de canales.
    
    Responsabilidades:
    - Gestionar canales y sus configuraciones
    - Controlar acceso a canales (membresías)
    - Administrar contenido de canales
    - Procesar solicitudes de acceso
    """
    
    def __init__(self, event_bus: IEventBus):
        self._event_bus = event_bus
        self.channels = {}  # Cache en memoria para canales
        self.logger = logging.getLogger(__name__)
    
    async def setup(self) -> None:
        """Suscribe el servicio a los eventos relevantes y carga datos iniciales."""
        # Suscribirse a eventos
        self._event_bus.subscribe(ChannelJoinRequestEvent, self.handle_join_request)
        self._event_bus.subscribe(UserReactionEvent, self.handle_user_reaction)
        
        # Cargar datos iniciales
        await self._load_initial_data()
    
    async def _load_initial_data(self) -> None:
        """Carga datos iniciales de canales."""
        try:
            # Cargar canales activos en cache
            async for session in get_session():
                query = select(Channel).where(Channel.is_active == True)
                result = await session.execute(query)
                channels = result.scalars().all()
                
                for channel in channels:
                    self.channels[channel.telegram_id] = {
                        "id": channel.id,
                        "name": channel.name,
                        "type": channel.type,
                        "description": channel.description
                    }
                
                self.logger.info(f"Cargados {len(self.channels)} canales activos en cache")
        except Exception as e:
            self.logger.error(f"Error al cargar datos iniciales: {e}")
    
    async def handle_join_request(self, event: ChannelJoinRequestEvent) -> None:
        """
        Maneja el evento de solicitud de unión a un canal.
        
        Args:
            event: Evento de solicitud de unión.
        """
        try:
            async for session in get_session():
                # Verificar que el usuario existe
                user_query = select(User).where(User.id == event.user_id)
                user_result = await session.execute(user_query)
                user = user_result.scalars().first()
                
                if not user:
                    self.logger.error(f"Usuario {event.user_id} no existe en la base de datos. No se puede procesar solicitud.")
                    return
                
                # Obtener canal
                channel_query = select(Channel).options(
                    selectinload(Channel.access_rules)
                ).where(Channel.id == event.channel_id)
                channel_result = await session.execute(channel_query)
                channel = channel_result.scalars().first()
                
                if not channel:
                    self.logger.error(f"Canal {event.channel_id} no existe en la base de datos.")
                    return
                
                # Verificar si el usuario ya es miembro
                membership_query = select(ChannelMembership).where(
                    and_(
                        ChannelMembership.user_id == event.user_id,
                        ChannelMembership.channel_id == event.channel_id,
                        ChannelMembership.is_active == True
                    )
                )
                membership_result = await session.execute(membership_query)
                existing_membership = membership_result.scalars().first()
                
                if existing_membership:
                    self.logger.info(f"Usuario {event.user_id} ya es miembro del canal {event.channel_id}.")
                    return
                
                # Verificar reglas de acceso
                access_rules = channel.access_rules
                can_join = True
                rejection_reason = ""
                
                if channel.type == "vip" and access_rules:
                    # Verificar nivel mínimo si está configurado
                    if access_rules.min_level and user.level < access_rules.min_level:
                        can_join = False
                        rejection_reason = f"Se requiere nivel {access_rules.min_level} para unirse a este canal."
                    
                    # Verificar requisitos VIP si están configurados
                    if access_rules.requires_vip and not user.is_vip:
                        can_join = False
                        rejection_reason = "Este canal requiere membresía VIP."
                    
                    # Verificar tokens requeridos si están configurados
                    if access_rules.tokens_required > 0:
                        # Aquí iría la verificación de tokens disponibles del usuario
                        # Por ahora asumimos que no tiene suficientes tokens
                        can_join = False
                        rejection_reason = f"Se requieren {access_rules.tokens_required} tokens para unirse a este canal."
                
                if can_join:
                    # Crear membresía
                    expires_at = None
                    if channel.type == "vip" and access_rules and access_rules.duration_days:
                        expires_at = datetime.now() + timedelta(days=access_rules.duration_days)
                    
                    new_membership = ChannelMembership(
                        user_id=event.user_id,
                        channel_id=event.channel_id,
                        is_active=True,
                        join_date=datetime.now(),
                        expires_at=expires_at,
                        role="member"
                    )
                    
                    session.add(new_membership)
                    await session.commit()
                    
                    # Publicar evento de aprobación
                    approval_event = ChannelJoinApprovedEvent(
                        user_id=event.user_id,
                        channel_id=event.channel_id
                    )
                    await self._event_bus.publish(approval_event)
                    
                    self.logger.info(f"Usuario {event.user_id} añadido al canal {event.channel_id}.")
                else:
                    # Publicar evento de rechazo
                    rejection_event = ChannelJoinRejectedEvent(
                        user_id=event.user_id,
                        channel_id=event.channel_id,
                        reason=rejection_reason
                    )
                    await self._event_bus.publish(rejection_event)
                    
                    self.logger.info(f"Solicitud de unión de usuario {event.user_id} al canal {event.channel_id} rechazada: {rejection_reason}")
        
        except Exception as e:
            self.logger.error(f"Error al procesar solicitud de unión a canal: {e}")
    
    async def handle_user_reaction(self, event: UserReactionEvent) -> None:
        """
        Maneja el evento de reacción de usuario a contenido en un canal.
        
        Args:
            event: Evento de reacción.
        """
        try:
            async for session in get_session():
                # Verificar que el usuario existe
                user_query = select(User).where(User.id == event.user_id)
                user_result = await session.execute(user_query)
                user = user_result.scalars().first()
                
                if not user:
                    self.logger.error(f"Usuario {event.user_id} no existe en la base de datos. No se puede procesar reacción.")
                    return
                
                # Verificar que el contenido existe
                content_query = select(ChannelContent).where(ChannelContent.id == event.content_id)
                content_result = await session.execute(content_query)
                content = content_result.scalars().first()
                
                if not content:
                    self.logger.error(f"Contenido {event.content_id} no existe en la base de datos.")
                    return
                
                # Registrar reacción en el contenido
                if "reactions" not in content.metadata:
                    content.metadata["reactions"] = {}
                
                if event.reaction_type not in content.metadata["reactions"]:
                    content.metadata["reactions"][event.reaction_type] = 0
                
                content.metadata["reactions"][event.reaction_type] += 1
                
                # Si hay un contador de engagement, incrementarlo
                if "engagement" not in content.metadata:
                    content.metadata["engagement"] = 0
                
                content.metadata["engagement"] += 1
                
                await session.commit()
                self.logger.info(f"Usuario {event.user_id} reaccionó con {event.reaction_type} al contenido {event.content_id}.")
        
        except Exception as e:
            self.logger.error(f"Error al procesar reacción de usuario: {e}")
    
    async def create_channel(self, telegram_id: str, name: str, description: str, channel_type: str) -> Optional[int]:
        """
        Crea un nuevo canal.
        
        Args:
            telegram_id: ID de Telegram del canal.
            name: Nombre del canal.
            description: Descripción del canal.
            channel_type: Tipo de canal ('free' o 'vip').
            
        Returns:
            ID del canal creado o None si hubo un error.
        """
        try:
            async for session in get_session():
                # Verificar si el canal ya existe
                query = select(Channel).where(Channel.telegram_id == telegram_id)
                result = await session.execute(query)
                existing_channel = result.scalars().first()
                
                if existing_channel:
                    self.logger.info(f"Canal con telegram_id {telegram_id} ya existe.")
                    return existing_channel.id
                
                # Crear nuevo canal
                new_channel = Channel(
                    telegram_id=telegram_id,
                    name=name,
                    description=description,
                    type=channel_type,
                    is_active=True,
                    settings={}
                )
                
                session.add(new_channel)
                await session.commit()
                
                # Refrescar para obtener el ID
                await session.refresh(new_channel)
                
                # Actualizar cache
                self.channels[telegram_id] = {
                    "id": new_channel.id,
                    "name": name,
                    "type": channel_type,
                    "description": description
                }
                
                self.logger.info(f"Canal {name} creado con ID {new_channel.id}.")
                return new_channel.id
        
        except Exception as e:
            self.logger.error(f"Error al crear canal: {e}")
            return None
    
    async def update_channel(self, channel_id: int, **kwargs) -> bool:
        """
        Actualiza la información de un canal.
        
        Args:
            channel_id: ID del canal.
            **kwargs: Campos a actualizar.
            
        Returns:
            True si se actualizó correctamente, False en caso contrario.
        """
        try:
            async for session in get_session():
                # Obtener canal
                query = select(Channel).where(Channel.id == channel_id)
                result = await session.execute(query)
                channel = result.scalars().first()
                
                if not channel:
                    self.logger.error(f"Canal {channel_id} no existe en la base de datos.")
                    return False
                
                # Actualizar campos
                for field, value in kwargs.items():
                    if hasattr(channel, field):
                        setattr(channel, field, value)
                
                await session.commit()
                
                # Actualizar cache si telegram_id está en ella
                if channel.telegram_id in self.channels:
                    if "name" in kwargs:
                        self.channels[channel.telegram_id]["name"] = kwargs["name"]
                    if "type" in kwargs:
                        self.channels[channel.telegram_id]["type"] = kwargs["type"]
                    if "description" in kwargs:
                        self.channels[channel.telegram_id]["description"] = kwargs["description"]
                
                self.logger.info(f"Canal {channel_id} actualizado.")
                return True
        
        except Exception as e:
            self.logger.error(f"Error al actualizar canal: {e}")
            return False
    
    async def delete_channel(self, channel_id: int) -> bool:
        """
        Marca un canal como inactivo (eliminación lógica).
        
        Args:
            channel_id: ID del canal.
            
        Returns:
            True si se eliminó correctamente, False en caso contrario.
        """
        try:
            async for session in get_session():
                # Obtener canal
                query = select(Channel).where(Channel.id == channel_id)
                result = await session.execute(query)
                channel = result.scalars().first()
                
                if not channel:
                    self.logger.error(f"Canal {channel_id} no existe en la base de datos.")
                    return False
                
                # Marcar como inactivo
                channel.is_active = False
                await session.commit()
                
                # Eliminar de la cache
                if channel.telegram_id in self.channels:
                    del self.channels[channel.telegram_id]
                
                self.logger.info(f"Canal {channel_id} eliminado (marcado como inactivo).")
                return True
        
        except Exception as e:
            self.logger.error(f"Error al eliminar canal: {e}")
            return False
    
    async def get_channel(self, channel_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene información de un canal.
        
        Args:
            channel_id: ID del canal.
            
        Returns:
            Diccionario con información del canal o None si no existe.
        """
        try:
            async for session in get_session():
                # Obtener canal con relaciones
                query = select(Channel).options(
                    selectinload(Channel.access_rules),
                    selectinload(Channel.content)
                ).where(Channel.id == channel_id)
                result = await session.execute(query)
                channel = result.scalars().first()
                
                if not channel:
                    return None
                
                # Contar miembros
                members_count_query = select(func.count(ChannelMembership.id)).where(
                    and_(
                        ChannelMembership.channel_id == channel_id,
                        ChannelMembership.is_active == True
                    )
                )
                members_count_result = await session.execute(members_count_query)
                members_count = members_count_result.scalar()
                
                # Armar respuesta
                channel_data = {
                    "id": channel.id,
                    "telegram_id": channel.telegram_id,
                    "name": channel.name,
                    "description": channel.description,
                    "type": channel.type,
                    "is_active": channel.is_active,
                    "settings": channel.settings,
                    "members_count": members_count,
                    "access_rules": None,
                    "content_count": len(channel.content)
                }
                
                # Agregar reglas de acceso si existen
                if channel.access_rules:
                    channel_data["access_rules"] = {
                        "min_level": channel.access_rules.min_level,
                        "requires_vip": channel.access_rules.requires_vip,
                        "tokens_required": channel.access_rules.tokens_required,
                        "duration_days": channel.access_rules.duration_days
                    }
                
                return channel_data
        
        except Exception as e:
            self.logger.error(f"Error al obtener información del canal: {e}")
            return None
    
    async def get_user_channels(self, user_id: int) -> Dict[str, List[Dict[str, Any]]]:
        """
        Obtiene los canales a los que pertenece un usuario.
        
        Args:
            user_id: ID del usuario.
            
        Returns:
            Diccionario con canales agrupados por tipo.
        """
        result = {
            "free": [],
            "vip": []
        }
        
        try:
            async for session in get_session():
                # Verificar que el usuario existe
                user_query = select(User).where(User.id == user_id)
                user_result = await session.execute(user_query)
                user = user_result.scalars().first()
                
                if not user:
                    self.logger.error(f"Usuario {user_id} no existe en la base de datos.")
                    return result
                
                # Obtener membresías activas
                query = select(ChannelMembership).options(
                    selectinload(ChannelMembership.channel)
                ).where(
                    and_(
                        ChannelMembership.user_id == user_id,
                        ChannelMembership.is_active == True
                    )
                )
                query_result = await session.execute(query)
                memberships = query_result.scalars().all()
                
                # Organizar por tipo de canal
                for membership in memberships:
                    channel = membership.channel
                    
                    # Verificar si ha expirado
                    if membership.expires_at and membership.expires_at < datetime.now():
                        # Marcar como inactiva
                        membership.is_active = False
                        await session.commit()
                        
                        # Publicar evento de expiración
                        expiry_event = ChannelMembershipExpiredEvent(
                            user_id=user_id,
                            channel_id=channel.id
                        )
                        await self._event_bus.publish(expiry_event)
                        
                        continue
                    
                    channel_data = {
                        "id": channel.id,
                        "telegram_id": channel.telegram_id,
                        "name": channel.name,
                        "description": channel.description,
                        "joined_at": membership.join_date.isoformat(),
                        "expires_at": membership.expires_at.isoformat() if membership.expires_at else None,
                        "role": membership.role
                    }
                    
                    if channel.type == "free":
                        result["free"].append(channel_data)
                    elif channel.type == "vip":
                        result["vip"].append(channel_data)
        
        except Exception as e:
            self.logger.error(f"Error al obtener canales del usuario: {e}")
        
        return result
    
    async def add_channel_content(self, channel_id: int, content_type: str, content_data: Dict[str, Any], scheduled_time: Optional[datetime] = None) -> Optional[int]:
        """
        Añade contenido a un canal.
        
        Args:
            channel_id: ID del canal.
            content_type: Tipo de contenido ('text', 'image', 'video', etc.).
            content_data: Datos del contenido.
            scheduled_time: Fecha y hora programada para publicación.
            
        Returns:
            ID del contenido creado o None si hubo un error.
        """
        try:
            async for session in get_session():
                # Obtener canal
                query = select(Channel).where(Channel.id == channel_id)
                result = await session.execute(query)
                channel = result.scalars().first()
                
                if not channel:
                    self.logger.error(f"Canal {channel_id} no existe en la base de datos.")
                    return None
                
                # Crear contenido
                new_content = ChannelContent(
                    channel_id=channel_id,
                    content_type=content_type,
                    content_data=content_data,
                    scheduled_time=scheduled_time,
                    is_published=scheduled_time is None,  # Si no hay tiempo programado, se publica de inmediato
                    metadata={"reactions": {}, "engagement": 0}
                )
                
                session.add(new_content)
                await session.commit()
                
                # Refrescar para obtener el ID
                await session.refresh(new_content)
                
                # Si se publica de inmediato, emitir evento
                if new_content.is_published:
                    publish_event = ChannelContentPublishedEvent(
                        channel_id=channel_id,
                        content_id=new_content.id,
                        content_type=content_type
                    )
                    await self._event_bus.publish(publish_event)
                
                self.logger.info(f"Contenido añadido al canal {channel_id} con ID {new_content.id}.")
                return new_content.id
        
        except Exception as e:
            self.logger.error(f"Error al añadir contenido al canal: {e}")
            return None
    
    async def get_channel_content(self, channel_id: int, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Obtiene el contenido de un canal.
        
        Args:
            channel_id: ID del canal.
            limit: Límite de contenidos a devolver.
            offset: Desplazamiento para paginación.
            
        Returns:
            Lista de contenidos del canal.
        """
        result = []
        
        try:
            async for session in get_session():
                # Obtener canal
                channel_query = select(Channel).where(Channel.id == channel_id)
                channel_result = await session.execute(channel_query)
                channel = channel_result.scalars().first()
                
                if not channel:
                    self.logger.error(f"Canal {channel_id} no existe en la base de datos.")
                    return result
                
                # Obtener contenido publicado
                query = select(ChannelContent).where(
                    and_(
                        ChannelContent.channel_id == channel_id,
                        ChannelContent.is_published == True
                    )
                ).order_by(
                    ChannelContent.publish_time.desc()
                ).offset(offset).limit(limit)
                
                query_result = await session.execute(query)
                contents = query_result.scalars().all()
                
                # Armar respuesta
                for content in contents:
                    content_data = {
                        "id": content.id,
                        "content_type": content.content_type,
                        "content_data": content.content_data,
                        "publish_time": content.publish_time.isoformat(),
                        "reactions": content.metadata.get("reactions", {}),
                        "engagement": content.metadata.get("engagement", 0)
                    }
                    
                    result.append(content_data)
        
        except Exception as e:
            self.logger.error(f"Error al obtener contenido del canal: {e}")
        
        return result
    
    async def set_channel_access_rules(self, channel_id: int, min_level: Optional[int] = None, 
                                       requires_vip: bool = False, tokens_required: int = 0,
                                       duration_days: Optional[int] = None) -> bool:
        """
        Establece reglas de acceso para un canal.
        
        Args:
            channel_id: ID del canal.
            min_level: Nivel mínimo requerido.
            requires_vip: Si requiere membresía VIP.
            tokens_required: Tokens requeridos para unirse.
            duration_days: Duración de la membresía en días.
            
        Returns:
            True si se configuró correctamente, False en caso contrario.
        """
        try:
            async for session in get_session():
                # Obtener canal
                query = select(Channel).options(
                    selectinload(Channel.access_rules)
                ).where(Channel.id == channel_id)
                result = await session.execute(query)
                channel = result.scalars().first()
                
                if not channel:
                    self.logger.error(f"Canal {channel_id} no existe en la base de datos.")
                    return False
                
                # Actualizar o crear reglas de acceso
                if channel.access_rules:
                    # Actualizar existente
                    if min_level is not None:
                        channel.access_rules.min_level = min_level
                    channel.access_rules.requires_vip = requires_vip
                    channel.access_rules.tokens_required = tokens_required
                    if duration_days is not None:
                        channel.access_rules.duration_days = duration_days
                else:
                    # Crear nuevo
                    access_rules = ChannelAccess(
                        channel_id=channel_id,
                        min_level=min_level,
                        requires_vip=requires_vip,
                        tokens_required=tokens_required,
                        duration_days=duration_days
                    )
                    channel.access_rules = access_rules
                
                await session.commit()
                self.logger.info(f"Reglas de acceso configuradas para canal {channel_id}.")
                return True
        
        except Exception as e:
            self.logger.error(f"Error al configurar reglas de acceso: {e}")
            return False
    
    async def check_scheduled_content(self) -> None:
        """Verifica y publica contenido programado que debe ser publicado."""
        try:
            async for session in get_session():
                # Buscar contenido programado para publicación
                now = datetime.now()
                query = select(ChannelContent).where(
                    and_(
                        ChannelContent.is_published == False,
                        ChannelContent.scheduled_time <= now
                    )
                )
                result = await session.execute(query)
                scheduled_contents = result.scalars().all()
                
                for content in scheduled_contents:
                    # Marcar como publicado
                    content.is_published = True
                    content.publish_time = now
                    
                    # Emitir evento de publicación
                    publish_event = ChannelContentPublishedEvent(
                        channel_id=content.channel_id,
                        content_id=content.id,
                        content_type=content.content_type
                    )
                    await self._event_bus.publish(publish_event)
                    
                    self.logger.info(f"Contenido programado {content.id} publicado en canal {content.channel_id}.")
                
                if scheduled_contents:
                    await session.commit()
        
        except Exception as e:
            self.logger.error(f"Error al verificar contenido programado: {e}")