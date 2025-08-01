"""Servicio Tokeneitor para la gestión de tokens y tarifas."""

import logging
import secrets
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta

from sqlalchemy import select, update, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.interfaces.IEventBus import IEvent, IEventBus
from src.core.interfaces.ICoreService import ICoreService
from src.modules.token.events import (
    TokenGeneratedEvent,
    TokenRedeemedEvent,
    TokenExpiredEvent,
    TariffCreatedEvent,
    TariffUpdatedEvent
)
from src.bot.database.engine import get_session
from src.bot.database.models.user import User
from src.bot.database.models.channel import Channel, ChannelMembership
from src.bot.database.models.token import Tariff, SubscriptionToken


class Tokeneitor(ICoreService):
    """
    Servicio para manejar la lógica de tokens de suscripción.
    
    Responsabilidades:
    - Gestionar tarifas para canales
    - Generar y verificar tokens de suscripción
    - Manejar el proceso de canje de tokens
    - Proporcionar estadísticas sobre tokens y suscripciones
    """
    
    def __init__(self, event_bus: IEventBus, bot_username: str = "TestingRefactor_bot"):
        self._event_bus = event_bus
        self.bot_username = bot_username
        self.logger = logging.getLogger(__name__)
    
    async def setup(self) -> None:
        """Suscribe el servicio a los eventos relevantes y carga datos iniciales."""
        # No hay suscripciones específicas para este servicio
        # pero podría escuchar eventos del sistema en el futuro
        
        # Iniciar tarea periódica para verificar tokens expirados
        # Esta funcionalidad se implementaría en un sistema de tareas programadas
        pass
    
    async def create_tariff(self, 
                           channel_id: int, 
                           name: str, 
                           duration_days: int, 
                           price: float, 
                           admin_id: int,
                           token_validity_days: int = 7,
                           description: str = None) -> Optional[int]:
        """
        Crea una nueva tarifa para un canal.
        
        Args:
            channel_id: ID del canal.
            name: Nombre de la tarifa.
            duration_days: Duración de la suscripción en días.
            price: Precio de la tarifa.
            admin_id: ID del administrador que crea la tarifa.
            token_validity_days: Días de validez para los tokens generados.
            description: Descripción opcional de la tarifa.
            
        Returns:
            ID de la tarifa creada o None si hubo un error.
        """
        try:
            async for session in get_session():
                # Verificar que el canal existe
                channel_query = select(Channel).where(Channel.id == channel_id)
                channel_result = await session.execute(channel_query)
                channel = channel_result.scalars().first()
                
                if not channel:
                    self.logger.error(f"Canal {channel_id} no existe en la base de datos.")
                    return None
                
                # Verificar que el administrador existe
                admin_query = select(User).where(User.id == admin_id)
                admin_result = await session.execute(admin_query)
                admin = admin_result.scalars().first()
                
                if not admin:
                    self.logger.error(f"Administrador {admin_id} no existe en la base de datos.")
                    return None
                
                # Crear nueva tarifa
                new_tariff = Tariff(
                    channel_id=channel_id,
                    name=name,
                    duration_days=duration_days,
                    price=price,
                    token_validity_days=token_validity_days,
                    description=description,
                    is_active=True
                )
                
                session.add(new_tariff)
                await session.commit()
                
                # Refrescar para obtener el ID
                await session.refresh(new_tariff)
                
                # Publicar evento de creación de tarifa
                tariff_event = TariffCreatedEvent(
                    tariff_id=new_tariff.id,
                    channel_id=channel_id,
                    admin_id=admin_id
                )
                await self._event_bus.publish(tariff_event)
                
                self.logger.info(f"Tarifa '{name}' creada para canal {channel_id} con ID {new_tariff.id}.")
                return new_tariff.id
        
        except Exception as e:
            self.logger.error(f"Error al crear tarifa: {e}")
            return None
    
    async def update_tariff(self, 
                           tariff_id: int, 
                           admin_id: int, 
                           **kwargs) -> bool:
        """
        Actualiza una tarifa existente.
        
        Args:
            tariff_id: ID de la tarifa.
            admin_id: ID del administrador que actualiza la tarifa.
            **kwargs: Campos a actualizar.
            
        Returns:
            True si se actualizó correctamente, False en caso contrario.
        """
        try:
            async for session in get_session():
                # Verificar que la tarifa existe
                tariff_query = select(Tariff).where(Tariff.id == tariff_id)
                tariff_result = await session.execute(tariff_query)
                tariff = tariff_result.scalars().first()
                
                if not tariff:
                    self.logger.error(f"Tarifa {tariff_id} no existe en la base de datos.")
                    return False
                
                # Verificar que el administrador existe
                admin_query = select(User).where(User.id == admin_id)
                admin_result = await session.execute(admin_query)
                admin = admin_result.scalars().first()
                
                if not admin:
                    self.logger.error(f"Administrador {admin_id} no existe en la base de datos.")
                    return False
                
                # Actualizar campos
                changes = {}
                for field, value in kwargs.items():
                    if hasattr(tariff, field) and getattr(tariff, field) != value:
                        changes[field] = {
                            'old': getattr(tariff, field),
                            'new': value
                        }
                        setattr(tariff, field, value)
                
                if changes:
                    await session.commit()
                    
                    # Publicar evento de actualización
                    update_event = TariffUpdatedEvent(
                        tariff_id=tariff_id,
                        admin_id=admin_id,
                        changes=changes
                    )
                    await self._event_bus.publish(update_event)
                    
                    self.logger.info(f"Tarifa {tariff_id} actualizada por administrador {admin_id}.")
                
                return True
        
        except Exception as e:
            self.logger.error(f"Error al actualizar tarifa: {e}")
            return False
    
    async def delete_tariff(self, tariff_id: int, admin_id: int) -> bool:
        """
        Desactiva una tarifa existente (eliminación lógica).
        
        Args:
            tariff_id: ID de la tarifa.
            admin_id: ID del administrador que elimina la tarifa.
            
        Returns:
            True si se desactivó correctamente, False en caso contrario.
        """
        try:
            async for session in get_session():
                # Verificar que la tarifa existe
                tariff_query = select(Tariff).where(Tariff.id == tariff_id)
                tariff_result = await session.execute(tariff_query)
                tariff = tariff_result.scalars().first()
                
                if not tariff:
                    self.logger.error(f"Tarifa {tariff_id} no existe en la base de datos.")
                    return False
                
                # Desactivar tarifa
                tariff.is_active = False
                await session.commit()
                
                self.logger.info(f"Tarifa {tariff_id} desactivada por administrador {admin_id}.")
                return True
        
        except Exception as e:
            self.logger.error(f"Error al desactivar tarifa: {e}")
            return False
    
    async def generate_token(self, tariff_id: int, admin_id: int) -> Optional[str]:
        """
        Genera un nuevo token para una tarifa específica.
        
        Args:
            tariff_id: ID de la tarifa.
            admin_id: ID del administrador que genera el token.
            
        Returns:
            URL de invitación con el token o None si hubo un error.
        """
        try:
            async for session in get_session():
                # Verificar que la tarifa existe
                tariff_query = select(Tariff).where(
                    and_(
                        Tariff.id == tariff_id,
                        Tariff.is_active == True
                    )
                )
                tariff_result = await session.execute(tariff_query)
                tariff = tariff_result.scalars().first()
                
                if not tariff:
                    self.logger.error(f"Tarifa {tariff_id} no existe o no está activa.")
                    return None
                
                # Verificar que el administrador existe
                admin_query = select(User).where(User.id == admin_id)
                admin_result = await session.execute(admin_query)
                admin = admin_result.scalars().first()
                
                if not admin:
                    self.logger.error(f"Administrador {admin_id} no existe en la base de datos.")
                    return None
                
                # Generar token único
                token_value = secrets.token_urlsafe(32)
                
                # Calcular fecha de expiración
                expires_at = datetime.now() + timedelta(days=tariff.token_validity_days)
                
                # Crear token
                new_token = SubscriptionToken(
                    token=token_value,
                    tariff_id=tariff_id,
                    generated_by=admin_id,
                    expires_at=expires_at,
                    is_used=False
                )
                
                session.add(new_token)
                await session.commit()
                
                # Refrescar para obtener el ID
                await session.refresh(new_token)
                
                # Publicar evento
                token_event = TokenGeneratedEvent(
                    token_id=new_token.id,
                    tariff_id=tariff_id,
                    admin_id=admin_id
                )
                await self._event_bus.publish(token_event)
                
                # Generar enlace con vista previa
                start_param = f"token_{token_value}"
                token_url = f"https://t.me/{self.bot_username}?start={start_param}"
                
                self.logger.info(f"Token generado para tarifa {tariff_id} por administrador {admin_id}.")
                return token_url
        
        except Exception as e:
            self.logger.error(f"Error al generar token: {e}")
            return None
    
    async def verify_token(self, token: str, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Verifica la validez de un token y lo marca como utilizado si es válido.
        
        Args:
            token: Valor del token.
            user_id: ID del usuario que canjea el token.
            
        Returns:
            Información para crear la invitación o None si el token no es válido.
        """
        try:
            async for session in get_session():
                # Verificar que el usuario existe
                user_query = select(User).where(User.id == user_id)
                user_result = await session.execute(user_query)
                user = user_result.scalars().first()
                
                if not user:
                    self.logger.error(f"Usuario {user_id} no existe en la base de datos.")
                    return None
                
                # Buscar token no utilizado y no expirado
                token_query = select(SubscriptionToken).options(
                    selectinload(SubscriptionToken.tariff).selectinload(Tariff.channel)
                ).where(
                    and_(
                        SubscriptionToken.token == token,
                        SubscriptionToken.is_used == False,
                        SubscriptionToken.expires_at > datetime.now()
                    )
                )
                token_result = await session.execute(token_query)
                token_obj = token_result.scalars().first()
                
                if not token_obj:
                    self.logger.warning(f"Token {token} no válido o ya utilizado.")
                    return None
                
                # Marcar token como utilizado
                token_obj.is_used = True
                token_obj.used_by = user_id
                token_obj.used_at = datetime.now()
                
                # Obtener datos relevantes
                tariff = token_obj.tariff
                channel = tariff.channel
                
                # Calcular fecha de expiración de la membresía
                membership_expires_at = datetime.now() + timedelta(days=tariff.duration_days)
                
                # Crear o actualizar membresía
                membership_query = select(ChannelMembership).where(
                    and_(
                        ChannelMembership.user_id == user_id,
                        ChannelMembership.channel_id == channel.id
                    )
                )
                membership_result = await session.execute(membership_query)
                membership = membership_result.scalars().first()
                
                if membership:
                    # Actualizar membresía existente
                    membership.status = "active"
                    membership.expires_at = membership_expires_at
                    membership.user_metadata = {
                        **membership.user_metadata,
                        "is_vip": True,
                        "tariff_id": tariff.id,
                        "last_token_id": token_obj.id
                    }
                else:
                    # Crear nueva membresía
                    membership = ChannelMembership(
                        user_id=user_id,
                        channel_id=channel.id,
                        status="active",
                        joined_at=datetime.now(),
                        expires_at=membership_expires_at,
                        user_metadata={
                            "is_vip": True,
                            "tariff_id": tariff.id,
                            "last_token_id": token_obj.id
                        }
                    )
                    session.add(membership)
                
                await session.commit()
                
                # Publicar evento
                redemption_event = TokenRedeemedEvent(
                    token_id=token_obj.id,
                    user_id=user_id,
                    channel_id=channel.id,
                    expiry_date=membership_expires_at
                )
                await self._event_bus.publish(redemption_event)
                
                # Devolver información para la invitación
                self.logger.info(f"Token {token} canjeado por usuario {user_id} para canal {channel.id}.")
                return {
                    "channel_id": channel.id,
                    "telegram_id": channel.telegram_id,
                    "name": channel.name,
                    "expiry_date": membership_expires_at,
                    "tariff_name": tariff.name,
                    "duration_days": tariff.duration_days
                }
        
        except Exception as e:
            self.logger.error(f"Error al verificar token: {e}")
            return None
    
    async def get_channel_tariffs(self, channel_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene las tarifas disponibles para un canal.
        
        Args:
            channel_id: ID del canal.
            
        Returns:
            Lista de tarifas activas.
        """
        result = []
        
        try:
            async for session in get_session():
                # Verificar que el canal existe
                channel_query = select(Channel).where(Channel.id == channel_id)
                channel_result = await session.execute(channel_query)
                channel = channel_result.scalars().first()
                
                if not channel:
                    self.logger.error(f"Canal {channel_id} no existe en la base de datos.")
                    return result
                
                # Obtener tarifas activas
                tariffs_query = select(Tariff).where(
                    and_(
                        Tariff.channel_id == channel_id,
                        Tariff.is_active == True
                    )
                ).order_by(Tariff.price.asc())
                
                tariffs_result = await session.execute(tariffs_query)
                tariffs = tariffs_result.scalars().all()
                
                # Formatear resultado
                for tariff in tariffs:
                    result.append({
                        "id": tariff.id,
                        "name": tariff.name,
                        "duration_days": tariff.duration_days,
                        "price": tariff.price,
                        "token_validity_days": tariff.token_validity_days,
                        "description": tariff.description
                    })
        
        except Exception as e:
            self.logger.error(f"Error al obtener tarifas del canal: {e}")
        
        return result
    
    async def get_token_stats(self, channel_id: int) -> Dict[str, Any]:
        """
        Obtiene estadísticas de tokens para un canal.
        
        Args:
            channel_id: ID del canal.
            
        Returns:
            Estadísticas de tokens generados y canjeados.
        """
        stats = {
            "total_generated": 0,
            "total_redeemed": 0,
            "conversion_rate": 0,
            "by_tariff": {},
            "recent_tokens": []
        }
        
        try:
            async for session in get_session():
                # Obtener tarifas del canal
                tariffs_query = select(Tariff).where(Tariff.channel_id == channel_id)
                tariffs_result = await session.execute(tariffs_query)
                tariffs = {t.id: t.name for t in tariffs_result.scalars().all()}
                
                if not tariffs:
                    return stats
                
                # Estadísticas generales
                tokens_query = select(
                    SubscriptionToken.tariff_id,
                    func.count().label("total"),
                    func.sum(SubscriptionToken.is_used.cast(Integer)).label("used")
                ).where(
                    SubscriptionToken.tariff_id.in_(tariffs.keys())
                ).group_by(SubscriptionToken.tariff_id)
                
                tokens_result = await session.execute(tokens_query)
                
                total_generated = 0
                total_redeemed = 0
                
                for row in tokens_result:
                    tariff_id, total, used = row
                    total_generated += total
                    total_redeemed += used or 0
                    
                    stats["by_tariff"][tariffs[tariff_id]] = {
                        "generated": total,
                        "redeemed": used or 0,
                        "conversion_rate": round((used or 0) / total * 100, 2) if total > 0 else 0
                    }
                
                stats["total_generated"] = total_generated
                stats["total_redeemed"] = total_redeemed
                stats["conversion_rate"] = round(total_redeemed / total_generated * 100, 2) if total_generated > 0 else 0
                
                # Tokens recientes
                recent_query = select(SubscriptionToken).options(
                    selectinload(SubscriptionToken.tariff),
                    selectinload(SubscriptionToken.generator),
                    selectinload(SubscriptionToken.user)
                ).where(
                    SubscriptionToken.tariff_id.in_(tariffs.keys())
                ).order_by(
                    SubscriptionToken.created_at.desc()
                ).limit(10)
                
                recent_result = await session.execute(recent_query)
                recent_tokens = recent_result.scalars().all()
                
                for token in recent_tokens:
                    stats["recent_tokens"].append({
                        "id": token.id,
                        "tariff": token.tariff.name,
                        "generated_by": token.generator.username or f"User_{token.generated_by}",
                        "is_used": token.is_used,
                        "used_by": token.user.username if token.user else None,
                        "created_at": token.created_at.isoformat(),
                        "used_at": token.used_at.isoformat() if token.used_at else None,
                        "expires_at": token.expires_at.isoformat()
                    })
        
        except Exception as e:
            self.logger.error(f"Error al obtener estadísticas de tokens: {e}")
        
        return stats
    
    async def check_expired_tokens(self) -> int:
        """
        Verifica tokens expirados y publica eventos correspondientes.
        
        Returns:
            Número de tokens expirados encontrados.
        """
        expired_count = 0
        
        try:
            async for session in get_session():
                # Buscar tokens expirados y no utilizados
                now = datetime.now()
                query = select(SubscriptionToken).where(
                    and_(
                        SubscriptionToken.is_used == False,
                        SubscriptionToken.expires_at <= now
                    )
                )
                result = await session.execute(query)
                expired_tokens = result.scalars().all()
                
                for token in expired_tokens:
                    # Publicar evento de expiración
                    expiry_event = TokenExpiredEvent(
                        token_id=token.id,
                        tariff_id=token.tariff_id
                    )
                    await self._event_bus.publish(expiry_event)
                    expired_count += 1
                
                self.logger.info(f"Verificados {expired_count} tokens expirados.")
        
        except Exception as e:
            self.logger.error(f"Error al verificar tokens expirados: {e}")
        
        return expired_count