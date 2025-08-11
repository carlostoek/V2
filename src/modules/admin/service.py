import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update, func, and_, or_, desc
from sqlalchemy.orm import selectinload

from src.core.interfaces.IEventBus import IEventBus, IEvent
from src.core.interfaces.ICoreService import ICoreService
from src.bot.database.models import Tariff, SubscriptionToken
from src.bot.database.models.user import User
from src.bot.database.models.gamification import UserPoints, UserMission, UserAchievement
from src.bot.database.models.channel import Channel, ChannelMembership
from src.bot.database.engine import get_session

# Events for Admin Service
class UserStatusChangedEvent(IEvent):
    def __init__(self, user_id: int, old_status: str, new_status: str, changed_by: int):
        self.user_id = user_id
        self.old_status = old_status
        self.new_status = new_status
        self.changed_by = changed_by
        self.timestamp = datetime.now()

class VipStatusChangedEvent(IEvent):
    def __init__(self, user_id: int, is_vip: bool, expires_at: Optional[datetime], changed_by: int):
        self.user_id = user_id
        self.is_vip = is_vip
        self.expires_at = expires_at
        self.changed_by = changed_by
        self.timestamp = datetime.now()

class AdminActionEvent(IEvent):
    def __init__(self, admin_id: int, action: str, target_id: Optional[int], details: Dict[str, Any]):
        self.admin_id = admin_id
        self.action = action
        self.target_id = target_id
        self.details = details
        self.timestamp = datetime.now()

class AdminService(ICoreService):
    """Servicio para manejar la lógica de administración."""

    def __init__(self, event_bus: IEventBus):
        self._event_bus = event_bus
        self.free_channel_id: int | None = None
        self.wait_time_minutes: int = 15

    async def setup(self) -> None:
        """Suscribe el servicio a los eventos relevantes."""
        pass

    def set_free_channel_id(self, channel_id: int) -> None:
        """Guarda el ID del canal gratuito."""
        print(f"[Admin] Canal gratuito configurado con ID: {channel_id}")
        self.free_channel_id = channel_id

    def get_free_channel_id(self) -> int | None:
        """Recupera el ID del canal gratuito."""
        return self.free_channel_id

    def set_wait_time(self, minutes: int) -> None:
        """Guarda el tiempo de espera para el canal gratuito."""
        print(f"[Admin] Tiempo de espera configurado a: {minutes} minutos")
        self.wait_time_minutes = minutes

    def get_wait_time(self) -> int:
        """Recupera el tiempo de espera para el canal gratuito."""
        return self.wait_time_minutes

    def send_message_to_channel(self, text: str, media: list | None = None) -> bool:
        """Simula el envío de un mensaje al canal gratuito."""
        print(f"[Admin] Enviando mensaje al canal {self.free_channel_id}:")
        print(f"[Admin] Texto: {text}")
        if media:
            print(f"[Admin] Media: {media}")
        return True

    async def create_tariff(self, name: str, price: float, duration_days: int, channel_id: int = 1, admin_id: int = 0, description: str = None) -> Tariff:
        """Crea una nueva tarifa."""
        new_tariff = Tariff(
            name=name, 
            price=price, 
            duration_days=duration_days,
            channel_id=channel_id,
            description=description
        )
        async for session in get_session():
            session.add(new_tariff)
            await session.commit()
            await session.refresh(new_tariff)
            
            # Publicar evento
            await self._event_bus.publish(AdminActionEvent(
                admin_id=admin_id,
                action="tariff_created",
                target_id=new_tariff.id,
                details={"name": name, "price": price, "duration_days": duration_days}
            ))
            
            print(f"[Admin] Tarifa creada: {new_tariff}")
            return new_tariff

    async def get_tariff(self, tariff_id: int) -> Tariff | None:
        """Recupera una tarifa por su ID."""
        async for session in get_session():
            return await session.get(Tariff, tariff_id)

    async def get_all_tariffs(self) -> List[Tariff]:
        """Recupera todas las tarifas."""
        async for session in get_session():
            result = await session.execute(
                select(Tariff).options(selectinload(Tariff.channel))
            )
            return result.scalars().all()

    async def update_tariff(self, tariff_id: int, name: str = None, price: float = None, duration_days: int = None, admin_id: int = 0, **kwargs) -> Tariff | None:
        """Actualiza una tarifa existente."""
        async for session in get_session():
            tariff = await session.get(Tariff, tariff_id)
            if not tariff:
                return None
                
            old_values = {"name": tariff.name, "price": tariff.price, "duration_days": tariff.duration_days}
            
            if name is not None:
                tariff.name = name
            if price is not None:
                tariff.price = price
            if duration_days is not None:
                tariff.duration_days = duration_days
            for key, value in kwargs.items():
                if hasattr(tariff, key):
                    setattr(tariff, key, value)
                    
            await session.commit()
            await session.refresh(tariff)
            
            # Publicar evento
            await self._event_bus.publish(AdminActionEvent(
                admin_id=admin_id,
                action="tariff_updated",
                target_id=tariff_id,
                details={"old": old_values, "new": {"name": tariff.name, "price": tariff.price, "duration_days": tariff.duration_days}}
            ))
            
            print(f"[Admin] Tarifa actualizada: {tariff}")
            return tariff

    async def delete_tariff(self, tariff_id: int, admin_id: int = 0) -> bool:
        """Elimina una tarifa por su ID."""
        async for session in get_session():
            tariff = await session.get(Tariff, tariff_id)
            if not tariff:
                return False
                
            tariff_data = {"name": tariff.name, "price": tariff.price}
            await session.delete(tariff)
            await session.commit()
            
            # Publicar evento
            await self._event_bus.publish(AdminActionEvent(
                admin_id=admin_id,
                action="tariff_deleted",
                target_id=tariff_id,
                details=tariff_data
            ))
            
            print(f"[Admin] Tarifa eliminada: {tariff_id}")
            return True

    async def generate_subscription_token(self, tariff_id: int, admin_id: int, expires_in_days: int = 7) -> SubscriptionToken | None:
        """Genera un token de suscripción para una tarifa."""
        tariff = await self.get_tariff(tariff_id)
        if not tariff:
            return None
        
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(days=expires_in_days)
        
        new_token = SubscriptionToken(
            token=token, 
            tariff_id=tariff_id,
            generated_by=admin_id,
            expires_at=expires_at
        )
        
        async for session in get_session():
            session.add(new_token)
            await session.commit()
            await session.refresh(new_token)
            
            # Publicar evento
            await self._event_bus.publish(AdminActionEvent(
                admin_id=admin_id,
                action="token_generated",
                target_id=new_token.id,
                details={"tariff_id": tariff_id, "token": token[:10] + "..."}
            ))
            
            print(f"[Admin] Token generado: {new_token}")
            return new_token

    async def validate_token(self, token: str, user_id: int) -> Dict[str, Any]:
        """Valida un token de suscripción y activa la suscripción."""
        async for session in get_session():
            # Buscar el token
            result = await session.execute(
                select(SubscriptionToken)
                .options(selectinload(SubscriptionToken.tariff))
                .where(SubscriptionToken.token == token)
            )
            token_data = result.scalars().first()

            if not token_data:
                return {"success": False, "error": "Token no encontrado"}
                
            if token_data.is_used:
                return {"success": False, "error": "Token ya utilizado"}
                
            if token_data.expires_at < datetime.now():
                return {"success": False, "error": "Token expirado"}
            
            # Marcar token como usado
            token_data.is_used = True
            token_data.used_by = user_id
            token_data.used_at = datetime.now()
            
            # Activar suscripción VIP
            user_result = await session.execute(select(User).where(User.id == user_id))
            user = user_result.scalars().first()
            
            if user:
                old_vip_status = user.is_vip
                user.is_vip = True
                user.vip_expires_at = datetime.now() + timedelta(days=token_data.tariff.duration_days)
                
                await session.commit()
                
                # Publicar eventos
                await self._event_bus.publish(VipStatusChangedEvent(
                    user_id=user_id,
                    is_vip=True,
                    expires_at=user.vip_expires_at,
                    changed_by=0  # System
                ))
                
                await self._event_bus.publish(AdminActionEvent(
                    admin_id=0,
                    action="token_redeemed",
                    target_id=token_data.id,
                    details={
                        "user_id": user_id,
                        "tariff_name": token_data.tariff.name,
                        "duration_days": token_data.tariff.duration_days
                    }
                ))
                
                return {
                    "success": True,
                    "data": {
                        "tariff_name": token_data.tariff.name,
                        "duration_days": token_data.tariff.duration_days,
                        "expires_at": user.vip_expires_at
                    }
                }
            
            return {"success": False, "error": "Usuario no encontrado"}

    async def get_expiring_subscriptions(self, days_to_expire: int) -> List[Dict[str, Any]]:
        """Recupera las suscripciones que expiran en un número de días."""
        target_date = datetime.now() + timedelta(days=days_to_expire)
        
        async for session in get_session():
            result = await session.execute(
                select(User)
                .where(
                    and_(
                        User.is_vip == True,
                        User.vip_expires_at <= target_date,
                        User.vip_expires_at >= datetime.now()
                    )
                )
            )
            expiring_users = result.scalars().all()
            
            return [{
                "user_id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "expires_at": user.vip_expires_at,
                "days_remaining": (user.vip_expires_at - datetime.now()).days
            } for user in expiring_users]
    
    # === MÉTODOS DE GESTIÓN DE USUARIOS ===
    
    async def get_user_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas generales de usuarios."""
        async for session in get_session():
            # Total de usuarios
            total_users = await session.scalar(select(func.count(User.id)))
            
            # Usuarios VIP activos
            vip_users = await session.scalar(
                select(func.count(User.id))
                .where(
                    and_(
                        User.is_vip == True,
                        or_(
                            User.vip_expires_at.is_(None),
                            User.vip_expires_at > datetime.now()
                        )
                    )
                )
            )
            
            # Usuarios activos (última actividad en 7 días)
            active_users = await session.scalar(
                select(func.count(User.id))
                .where(
                    and_(
                        User.is_active == True,
                        User.last_activity_at >= datetime.now() - timedelta(days=7)
                    )
                )
            )
            
            # Nuevos usuarios hoy
            today_users = await session.scalar(
                select(func.count(User.id))
                .where(User.created_at >= datetime.now().replace(hour=0, minute=0, second=0))
            )
            
            # Usuarios baneados
            banned_users = await session.scalar(
                select(func.count(User.id)).where(User.is_banned == True)
            )
            
            return {
                "total_users": total_users or 0,
                "vip_users": vip_users or 0,
                "free_users": (total_users or 0) - (vip_users or 0),
                "active_users": active_users or 0,
                "today_new_users": today_users or 0,
                "banned_users": banned_users or 0
            }
    
    async def get_revenue_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas de ingresos."""
        async for session in get_session():
            # Tokens generados en el mes actual
            current_month = datetime.now().replace(day=1, hour=0, minute=0, second=0)
            
            tokens_this_month = await session.scalar(
                select(func.count(SubscriptionToken.id))
                .where(SubscriptionToken.created_at >= current_month)
            )
            
            # Tokens canjeados en el mes actual
            redeemed_tokens = await session.scalar(
                select(func.count(SubscriptionToken.id))
                .where(
                    and_(
                        SubscriptionToken.is_used == True,
                        SubscriptionToken.used_at >= current_month
                    )
                )
            )
            
            # Calcular ingresos estimados
            revenue_query = await session.execute(
                select(func.sum(Tariff.price))
                .select_from(SubscriptionToken)
                .join(Tariff)
                .where(
                    and_(
                        SubscriptionToken.is_used == True,
                        SubscriptionToken.used_at >= current_month
                    )
                )
            )
            estimated_revenue = revenue_query.scalar() or 0.0
            
            # Tasa de conversión
            conversion_rate = (redeemed_tokens / tokens_this_month * 100) if tokens_this_month else 0
            
            return {
                "tokens_generated": tokens_this_month or 0,
                "tokens_redeemed": redeemed_tokens or 0,
                "conversion_rate": round(conversion_rate, 1),
                "estimated_revenue": round(estimated_revenue, 2)
            }
    
    async def get_top_tariffs(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Obtiene las tarifas más populares."""
        async for session in get_session():
            result = await session.execute(
                select(
                    Tariff.id,
                    Tariff.name,
                    Tariff.price,
                    func.count(SubscriptionToken.id).label("token_count"),
                    func.sum(Tariff.price).label("total_revenue")
                )
                .select_from(Tariff)
                .outerjoin(SubscriptionToken)
                .where(SubscriptionToken.is_used == True)
                .group_by(Tariff.id, Tariff.name, Tariff.price)
                .order_by(desc(func.count(SubscriptionToken.id)))
                .limit(limit)
            )
            
            return [{
                "id": row.id,
                "name": row.name,
                "price": row.price,
                "sales": row.token_count or 0,
                "revenue": row.total_revenue or 0.0
            } for row in result]
    
    async def set_user_vip_status(self, user_id: int, is_vip: bool, duration_days: int = None, admin_id: int = 0) -> Dict[str, Any]:
        """Establece el estado VIP de un usuario."""
        async for session in get_session():
            user = await session.get(User, user_id)
            if not user:
                return {"success": False, "error": "Usuario no encontrado"}
            
            old_status = user.is_vip
            user.is_vip = is_vip
            
            if is_vip and duration_days:
                user.vip_expires_at = datetime.now() + timedelta(days=duration_days)
            elif not is_vip:
                user.vip_expires_at = None
                
            await session.commit()
            
            # Publicar evento
            await self._event_bus.publish(VipStatusChangedEvent(
                user_id=user_id,
                is_vip=is_vip,
                expires_at=user.vip_expires_at,
                changed_by=admin_id
            ))
            
            await self._event_bus.publish(AdminActionEvent(
                admin_id=admin_id,
                action="user_vip_changed",
                target_id=user_id,
                details={"old_status": old_status, "new_status": is_vip}
            ))
            
            return {
                "success": True,
                "data": {
                    "user_id": user_id,
                    "is_vip": is_vip,
                    "expires_at": user.vip_expires_at
                }
            }
    
    async def ban_user(self, user_id: int, admin_id: int, reason: str = None) -> Dict[str, Any]:
        """Banea a un usuario."""
        async for session in get_session():
            user = await session.get(User, user_id)
            if not user:
                return {"success": False, "error": "Usuario no encontrado"}
            
            if user.is_banned:
                return {"success": False, "error": "Usuario ya está baneado"}
            
            user.is_banned = True
            user.is_active = False
            await session.commit()
            
            # Publicar evento
            await self._event_bus.publish(UserStatusChangedEvent(
                user_id=user_id,
                old_status="active",
                new_status="banned",
                changed_by=admin_id
            ))
            
            await self._event_bus.publish(AdminActionEvent(
                admin_id=admin_id,
                action="user_banned",
                target_id=user_id,
                details={"reason": reason or "No especificada"}
            ))
            
            return {"success": True, "data": {"user_id": user_id, "status": "banned"}}
    
    async def unban_user(self, user_id: int, admin_id: int) -> Dict[str, Any]:
        """Desbanea a un usuario."""
        async for session in get_session():
            user = await session.get(User, user_id)
            if not user:
                return {"success": False, "error": "Usuario no encontrado"}
            
            if not user.is_banned:
                return {"success": False, "error": "Usuario no está baneado"}
            
            user.is_banned = False
            user.is_active = True
            await session.commit()
            
            # Publicar evento
            await self._event_bus.publish(UserStatusChangedEvent(
                user_id=user_id,
                old_status="banned",
                new_status="active",
                changed_by=admin_id
            ))
            
            await self._event_bus.publish(AdminActionEvent(
                admin_id=admin_id,
                action="user_unbanned",
                target_id=user_id,
                details={}
            ))
            
            return {"success": True, "data": {"user_id": user_id, "status": "active"}}
    
    async def search_users(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Busca usuarios por nombre de usuario o nombre."""
        async for session in get_session():
            search_term = f"%{query}%"
            
            result = await session.execute(
                select(User)
                .where(
                    or_(
                        User.username.ilike(search_term),
                        User.first_name.ilike(search_term),
                        User.last_name.ilike(search_term)
                    )
                )
                .limit(limit)
            )
            
            users = result.scalars().all()
            
            return [{
                "id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_vip": user.is_vip,
                "is_banned": user.is_banned,
                "is_admin": user.is_admin,
                "last_activity_at": user.last_activity_at,
                "created_at": user.created_at
            } for user in users]
    
    async def get_user_details(self, user_id: int) -> Dict[str, Any]:
        """Obtiene detalles completos de un usuario."""
        async for session in get_session():
            # Obtener usuario con relaciones
            result = await session.execute(
                select(User)
                .options(
                    selectinload(User.points),
                    selectinload(User.achievements),
                    selectinload(User.missions),
                    selectinload(User.channel_memberships)
                )
                .where(User.id == user_id)
            )
            
            user = result.scalars().first()
            if not user:
                return {"success": False, "error": "Usuario no encontrado"}
            
            # Obtener tokens usados por el usuario
            tokens_result = await session.execute(
                select(SubscriptionToken)
                .options(selectinload(SubscriptionToken.tariff))
                .where(SubscriptionToken.used_by == user_id)
            )
            used_tokens = tokens_result.scalars().all()
            
            return {
                "success": True,
                "data": {
                    "id": user.id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "language_code": user.language_code,
                    "is_admin": user.is_admin,
                    "is_vip": user.is_vip,
                    "is_active": user.is_active,
                    "is_banned": user.is_banned,
                    "vip_expires_at": user.vip_expires_at,
                    "level": user.level,
                    "experience_points": user.experience_points,
                    "messages_count": user.messages_count,
                    "reactions_count": user.reactions_count,
                    "last_activity_at": user.last_activity_at,
                    "created_at": user.created_at,
                    "points": {
                        "current": user.points.current_points if user.points else 0,
                        "total_earned": user.points.total_earned if user.points else 0,
                        "total_spent": user.points.total_spent if user.points else 0
                    } if user.points else None,
                    "achievements_count": len(user.achievements),
                    "missions_completed": len([m for m in user.missions if m.status == "COMPLETED"]),
                    "channels_count": len(user.channel_memberships),
                    "tokens_used": len(used_tokens),
                    "subscription_history": [{
                        "token_id": token.id,
                        "tariff_name": token.tariff.name,
                        "used_at": token.used_at,
                        "price": token.tariff.price
                    } for token in used_tokens]
                }
            }
    
    # === MÉTODOS DE CONFIGURACIÓN AVANZADA ===
    
    async def get_bot_configuration(self) -> Dict[str, Any]:
        """Obtiene la configuración actual del bot."""
        return {
            "free_channel_id": self.free_channel_id,
            "wait_time_minutes": self.wait_time_minutes,
            "system_status": "active",
            "last_updated": datetime.now()
        }
    
    async def update_bot_configuration(self, config: Dict[str, Any], admin_id: int) -> Dict[str, Any]:
        """Actualiza la configuración del bot."""
        old_config = await self.get_bot_configuration()
        
        if "free_channel_id" in config:
            self.set_free_channel_id(config["free_channel_id"])
        
        if "wait_time_minutes" in config:
            self.set_wait_time(config["wait_time_minutes"])
        
        # Publicar evento
        await self._event_bus.publish(AdminActionEvent(
            admin_id=admin_id,
            action="config_updated",
            target_id=None,
            details={"old": old_config, "new": config}
        ))
        
        return {"success": True, "data": await self.get_bot_configuration()}
    
    async def generate_bulk_tokens(self, tariff_id: int, quantity: int, admin_id: int) -> Dict[str, Any]:
        """Genera múltiples tokens para una tarifa."""
        if quantity <= 0 or quantity > 1000:
            return {"success": False, "error": "Cantidad inválida (máximo 1000 tokens)"}
        
        tariff = await self.get_tariff(tariff_id)
        if not tariff:
            return {"success": False, "error": "Tarifa no encontrada"}
        
        tokens = []
        expires_at = datetime.now() + timedelta(days=7)
        
        async for session in get_session():
            for _ in range(quantity):
                token = secrets.token_urlsafe(32)
                new_token = SubscriptionToken(
                    token=token,
                    tariff_id=tariff_id,
                    generated_by=admin_id,
                    expires_at=expires_at
                )
                session.add(new_token)
                tokens.append(token)
            
            await session.commit()
        
        # Publicar evento
        await self._event_bus.publish(AdminActionEvent(
            admin_id=admin_id,
            action="bulk_tokens_generated",
            target_id=tariff_id,
            details={"quantity": quantity, "tariff_name": tariff.name}
        ))
        
        return {
            "success": True,
            "data": {
                "quantity": quantity,
                "tariff_name": tariff.name,
                "tokens": tokens[:10],  # Solo los primeros 10 para preview
                "total_generated": len(tokens)
            }
        }
    
    async def get_admin_activity_log(self, days: int = 7, limit: int = 50) -> List[Dict[str, Any]]:
        """Obtiene el log de actividad administrativa."""
        # Esta funcionalidad se implementaría con una tabla de logs específica
        # Por ahora retornamos datos simulados
        return [
            {
                "timestamp": datetime.now() - timedelta(hours=1),
                "admin_id": 12345,
                "action": "token_generated",
                "details": "Token generado para tarifa VIP 1 Mes"
            },
            {
                "timestamp": datetime.now() - timedelta(hours=2),
                "admin_id": 12345,
                "action": "user_banned",
                "details": "Usuario 98765 baneado por spam"
            }
        ]
    
    async def export_statistics(self, format: str = "json", date_range: int = 30) -> Dict[str, Any]:
        """Exporta estadísticas del bot."""
        user_stats = await self.get_user_statistics()
        revenue_stats = await self.get_revenue_statistics()
        top_tariffs = await self.get_top_tariffs()
        
        export_data = {
            "export_date": datetime.now(),
            "date_range_days": date_range,
            "user_statistics": user_stats,
            "revenue_statistics": revenue_stats,
            "top_tariffs": top_tariffs,
            "format": format
        }
        
        return {"success": True, "data": export_data}
