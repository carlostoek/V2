"""Servicio para gestionar roles y verificaciones de usuarios."""

import structlog
from typing import Optional, Dict, Any, List, Set
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, and_, or_

from .base import BaseService
from ..database.models.user import User
from ..database.models.channel import ChannelMembership
from ..config.settings import settings

logger = structlog.get_logger()

class RoleType:
    """Tipos de roles disponibles en el sistema."""
    ADMIN = "admin"
    VIP = "vip"
    FREE = "free"

class RoleService(BaseService[User]):
    """Servicio para gestionar roles y verificaciones de usuarios."""
    
    def __init__(self):
        super().__init__(User)
        self.logger = structlog.get_logger(service="RoleService")
    
    async def get_user_role(self, session: AsyncSession, user_id: int) -> str:
        """
        Obtiene el rol principal de un usuario.
        
        Args:
            session: Sesión de base de datos.
            user_id: ID del usuario.
            
        Returns:
            Rol del usuario (admin, vip, free).
        """
        self.logger.debug("Obteniendo rol de usuario", user_id=user_id)
        
        # Verificar si es administrador por configuración
        if self.is_admin_by_config(user_id):
            return RoleType.ADMIN
        
        # Obtener usuario de la base de datos
        user = await self.get_by_id(session, user_id)
        
        if not user:
            self.logger.warning("Usuario no encontrado", user_id=user_id)
            return RoleType.FREE
        
        # Verificar si es administrador en la base de datos
        if user.is_admin:
            return RoleType.ADMIN
        
        # Verificar si es VIP
        if await self.is_vip_active(session, user_id):
            return RoleType.VIP
        
        # Por defecto es usuario gratuito
        return RoleType.FREE
    
    def is_admin_by_config(self, user_id: int) -> bool:
        """
        Verifica si un usuario es administrador según la configuración.
        
        Args:
            user_id: ID del usuario.
            
        Returns:
            True si es administrador por configuración.
        """
        admin_ids = settings.admin_ids
        return user_id in admin_ids
    
    async def is_admin(self, session: AsyncSession, user_id: int) -> bool:
        """
        Verifica si un usuario es administrador.
        
        Args:
            session: Sesión de base de datos.
            user_id: ID del usuario.
            
        Returns:
            True si es administrador.
        """
        # Verificar por configuración primero
        if self.is_admin_by_config(user_id):
            return True
        
        # Verificar en la base de datos
        user = await self.get_by_id(session, user_id)
        return user is not None and user.is_admin
    
    async def is_vip_active(self, session: AsyncSession, user_id: int) -> bool:
        """
        Verifica si un usuario tiene membresía VIP activa.
        
        Args:
            session: Sesión de base de datos.
            user_id: ID del usuario.
            
        Returns:
            True si tiene VIP activo.
        """
        self.logger.debug("Verificando VIP activo", user_id=user_id)
        
        user = await self.get_by_id(session, user_id)
        
        if not user:
            return False
        
        # Verificar flag VIP y fecha de expiración
        if not user.is_vip:
            return False
        
        # Si no tiene fecha de expiración, es VIP permanente
        if not user.vip_expires_at:
            return True
        
        # Verificar si no ha expirado
        now = datetime.now()
        if user.vip_expires_at > now:
            return True
        
        # Si expiró, actualizar el estado
        await self.revoke_vip_status(session, user_id)
        return False
    
    async def is_free_user(self, session: AsyncSession, user_id: int) -> bool:
        """
        Verifica si un usuario es de tipo gratuito.
        
        Args:
            session: Sesión de base de datos.
            user_id: ID del usuario.
            
        Returns:
            True si es usuario gratuito.
        """
        role = await self.get_user_role(session, user_id)
        return role == RoleType.FREE
    
    async def grant_admin_status(self, session: AsyncSession, user_id: int, granted_by: int) -> bool:
        """
        Otorga estado de administrador a un usuario.
        
        Args:
            session: Sesión de base de datos.
            user_id: ID del usuario.
            granted_by: ID del administrador que otorga el estado.
            
        Returns:
            True si se otorgó correctamente.
        """
        self.logger.info("Otorgando estado de administrador", user_id=user_id, granted_by=granted_by)
        
        # Verificar que quien otorga es administrador
        if not await self.is_admin(session, granted_by):
            self.logger.warning("Usuario no autorizado para otorgar admin", granted_by=granted_by)
            return False
        
        # Obtener o crear usuario
        user = await self.get_by_id(session, user_id)
        if not user:
            self.logger.warning("Usuario no encontrado para otorgar admin", user_id=user_id)
            return False
        
        # Actualizar estado
        user.is_admin = True
        await session.flush()
        
        self.logger.info("Estado de administrador otorgado", user_id=user_id)
        return True
    
    async def revoke_admin_status(self, session: AsyncSession, user_id: int, revoked_by: int) -> bool:
        """
        Revoca estado de administrador a un usuario.
        
        Args:
            session: Sesión de base de datos.
            user_id: ID del usuario.
            revoked_by: ID del administrador que revoca el estado.
            
        Returns:
            True si se revocó correctamente.
        """
        self.logger.info("Revocando estado de administrador", user_id=user_id, revoked_by=revoked_by)
        
        # Verificar que quien revoca es administrador
        if not await self.is_admin(session, revoked_by):
            self.logger.warning("Usuario no autorizado para revocar admin", revoked_by=revoked_by)
            return False
        
        # No permitir auto-revocación
        if user_id == revoked_by:
            self.logger.warning("No se permite auto-revocación de admin", user_id=user_id)
            return False
        
        # Obtener usuario
        user = await self.get_by_id(session, user_id)
        if not user:
            self.logger.warning("Usuario no encontrado para revocar admin", user_id=user_id)
            return False
        
        # Actualizar estado
        user.is_admin = False
        await session.flush()
        
        self.logger.info("Estado de administrador revocado", user_id=user_id)
        return True
    
    async def grant_vip_status(self, session: AsyncSession, user_id: int, 
                              duration_days: Optional[int] = None, 
                              granted_by: Optional[int] = None) -> bool:
        """
        Otorga estado VIP a un usuario.
        
        Args:
            session: Sesión de base de datos.
            user_id: ID del usuario.
            duration_days: Duración en días (None para permanente).
            granted_by: ID del administrador que otorga el estado.
            
        Returns:
            True si se otorgó correctamente.
        """
        self.logger.info("Otorgando estado VIP", user_id=user_id, duration_days=duration_days)
        
        # Verificar autorización si se especifica granted_by
        if granted_by and not await self.is_admin(session, granted_by):
            self.logger.warning("Usuario no autorizado para otorgar VIP", granted_by=granted_by)
            return False
        
        # Obtener o crear usuario
        user = await self.get_by_id(session, user_id)
        if not user:
            self.logger.warning("Usuario no encontrado para otorgar VIP", user_id=user_id)
            return False
        
        # Calcular fecha de expiración
        expires_at = None
        if duration_days:
            expires_at = datetime.now() + timedelta(days=duration_days)
        
        # Actualizar estado
        user.is_vip = True
        user.vip_expires_at = expires_at
        await session.flush()
        
        self.logger.info("Estado VIP otorgado", user_id=user_id, expires_at=expires_at)
        return True
    
    async def revoke_vip_status(self, session: AsyncSession, user_id: int, 
                               revoked_by: Optional[int] = None) -> bool:
        """
        Revoca estado VIP a un usuario.
        
        Args:
            session: Sesión de base de datos.
            user_id: ID del usuario.
            revoked_by: ID del administrador que revoca el estado.
            
        Returns:
            True si se revocó correctamente.
        """
        self.logger.info("Revocando estado VIP", user_id=user_id)
        
        # Verificar autorización si se especifica revoked_by
        if revoked_by and not await self.is_admin(session, revoked_by):
            self.logger.warning("Usuario no autorizado para revocar VIP", revoked_by=revoked_by)
            return False
        
        # Obtener usuario
        user = await self.get_by_id(session, user_id)
        if not user:
            self.logger.warning("Usuario no encontrado para revocar VIP", user_id=user_id)
            return False
        
        # Actualizar estado
        user.is_vip = False
        user.vip_expires_at = None
        await session.flush()
        
        self.logger.info("Estado VIP revocado", user_id=user_id)
        return True
    
    async def extend_vip_status(self, session: AsyncSession, user_id: int, 
                               additional_days: int) -> bool:
        """
        Extiende la membresía VIP de un usuario.
        
        Args:
            session: Sesión de base de datos.
            user_id: ID del usuario.
            additional_days: Días adicionales a agregar.
            
        Returns:
            True si se extendió correctamente.
        """
        self.logger.info("Extendiendo VIP", user_id=user_id, additional_days=additional_days)
        
        user = await self.get_by_id(session, user_id)
        if not user:
            self.logger.warning("Usuario no encontrado para extender VIP", user_id=user_id)
            return False
        
        # Calcular nueva fecha de expiración
        now = datetime.now()
        
        if user.vip_expires_at and user.vip_expires_at > now:
            # Extender desde la fecha actual de expiración
            new_expires_at = user.vip_expires_at + timedelta(days=additional_days)
        else:
            # Extender desde ahora
            new_expires_at = now + timedelta(days=additional_days)
        
        # Actualizar estado
        user.is_vip = True
        user.vip_expires_at = new_expires_at
        await session.flush()
        
        self.logger.info("VIP extendido", user_id=user_id, new_expires_at=new_expires_at)
        return True
    
    async def get_user_permissions(self, session: AsyncSession, user_id: int) -> Dict[str, bool]:
        """
        Obtiene los permisos de un usuario basados en su rol.
        
        Args:
            session: Sesión de base de datos.
            user_id: ID del usuario.
            
        Returns:
            Diccionario con permisos del usuario.
        """
        role = await self.get_user_role(session, user_id)
        
        # Permisos base para todos los usuarios
        permissions = {
            "can_use_bot": True,
            "can_view_profile": True,
            "can_participate_missions": True,
            "can_access_narrative": True,
            "can_earn_points": True,
            "can_use_daily_gift": True,
            "can_access_free_channels": True,
            "can_access_vip_channels": False,
            "can_access_admin_panel": False,
            "can_manage_users": False,
            "can_manage_channels": False,
            "can_manage_tariffs": False,
            "can_generate_tokens": False,
            "can_view_analytics": False,
            "can_moderate_content": False,
            "can_access_vip_content": False,
            "can_participate_auctions": False,
            "can_access_exclusive_missions": False
        }
        
        # Permisos específicos por rol
        if role == RoleType.ADMIN:
            permissions.update({
                "can_access_vip_channels": True,
                "can_access_admin_panel": True,
                "can_manage_users": True,
                "can_manage_channels": True,
                "can_manage_tariffs": True,
                "can_generate_tokens": True,
                "can_view_analytics": True,
                "can_moderate_content": True,
                "can_access_vip_content": True,
                "can_participate_auctions": True,
                "can_access_exclusive_missions": True
            })
        elif role == RoleType.VIP:
            permissions.update({
                "can_access_vip_channels": True,
                "can_access_vip_content": True,
                "can_participate_auctions": True,
                "can_access_exclusive_missions": True
            })
        
        return permissions
    
    async def check_permission(self, session: AsyncSession, user_id: int, permission: str) -> bool:
        """
        Verifica si un usuario tiene un permiso específico.
        
        Args:
            session: Sesión de base de datos.
            user_id: ID del usuario.
            permission: Nombre del permiso a verificar.
            
        Returns:
            True si tiene el permiso.
        """
        permissions = await self.get_user_permissions(session, user_id)
        return permissions.get(permission, False)
    
    async def get_users_by_role(self, session: AsyncSession, role: str) -> List[Dict[str, Any]]:
        """
        Obtiene usuarios por rol.
        
        Args:
            session: Sesión de base de datos.
            role: Rol a buscar.
            
        Returns:
            Lista de usuarios con el rol especificado.
        """
        self.logger.debug("Obteniendo usuarios por rol", role=role)
        
        users = []
        
        if role == RoleType.ADMIN:
            # Obtener administradores por configuración
            admin_ids = settings.admin_ids
            
            # Obtener administradores de la base de datos
            query = select(User).where(
                or_(
                    User.id.in_(admin_ids),
                    User.is_admin == True
                )
            )
            result = await session.execute(query)
            db_admins = result.scalars().all()
            
            for user in db_admins:
                users.append({
                    "id": user.id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "role": RoleType.ADMIN,
                    "source": "config" if user.id in admin_ids else "database"
                })
        
        elif role == RoleType.VIP:
            # Obtener usuarios VIP activos
            now = datetime.now()
            query = select(User).where(
                and_(
                    User.is_vip == True,
                    or_(
                        User.vip_expires_at.is_(None),
                        User.vip_expires_at > now
                    )
                )
            )
            result = await session.execute(query)
            vip_users = result.scalars().all()
            
            for user in vip_users:
                users.append({
                    "id": user.id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "role": RoleType.VIP,
                    "expires_at": user.vip_expires_at.isoformat() if user.vip_expires_at else None
                })
        
        elif role == RoleType.FREE:
            # Obtener usuarios gratuitos (no admin, no VIP activo)
            now = datetime.now()
            admin_ids = settings.admin_ids
            
            query = select(User).where(
                and_(
                    ~User.id.in_(admin_ids),
                    User.is_admin == False,
                    or_(
                        User.is_vip == False,
                        and_(
                            User.is_vip == True,
                            User.vip_expires_at <= now
                        )
                    )
                )
            )
            result = await session.execute(query)
            free_users = result.scalars().all()
            
            for user in free_users:
                users.append({
                    "id": user.id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "role": RoleType.FREE
                })
        
        return users
    
    async def sync_admin_from_config(self, session: AsyncSession, user_id: int, 
                                    user_data: Dict[str, Any]) -> None:
        """
        Sincroniza el estado de administrador desde la configuración.
        
        Args:
            session: Sesión de base de datos.
            user_id: ID del usuario.
            user_data: Datos del usuario de Telegram.
        """
        is_config_admin = self.is_admin_by_config(user_id)
        
        if is_config_admin:
            # Obtener o crear usuario
            user = await self.get_by_id(session, user_id)
            
            if not user:
                # Crear usuario administrador
                user_data.update({
                    "id": user_id,
                    "is_admin": True
                })
                user = await self.create(session, user_data)
                self.logger.info("Usuario administrador creado desde configuración", user_id=user_id)
            else:
                # Actualizar si no es admin en la base de datos
                if not user.is_admin:
                    user.is_admin = True
                    await session.flush()
                    self.logger.info("Usuario sincronizado como administrador", user_id=user_id)
    
    async def check_vip_expiration(self, session: AsyncSession) -> List[int]:
        """
        Verifica y actualiza usuarios VIP expirados.
        
        Args:
            session: Sesión de base de datos.
            
        Returns:
            Lista de IDs de usuarios cuyo VIP expiró.
        """
        self.logger.debug("Verificando expiraciones VIP")
        
        now = datetime.now()
        
        # Buscar usuarios VIP expirados
        query = select(User).where(
            and_(
                User.is_vip == True,
                User.vip_expires_at <= now
            )
        )
        result = await session.execute(query)
        expired_users = result.scalars().all()
        
        expired_user_ids = []
        
        for user in expired_users:
            # Revocar estado VIP
            user.is_vip = False
            user.vip_expires_at = None
            expired_user_ids.append(user.id)
            
            self.logger.info("VIP expirado automáticamente", user_id=user.id)
        
        if expired_user_ids:
            await session.flush()
            self.logger.info(f"Procesados {len(expired_user_ids)} usuarios VIP expirados")
        
        return expired_user_ids
    
    async def get_role_statistics(self, session: AsyncSession) -> Dict[str, Any]:
        """
        Obtiene estadísticas de roles en el sistema.
        
        Args:
            session: Sesión de base de datos.
            
        Returns:
            Estadísticas de roles.
        """
        self.logger.debug("Obteniendo estadísticas de roles")
        
        # Contar administradores
        admin_ids = settings.admin_ids
        admin_query = select(User).where(
            or_(
                User.id.in_(admin_ids),
                User.is_admin == True
            )
        )
        admin_result = await session.execute(admin_query)
        admin_count = len(admin_result.scalars().all())
        
        # Contar usuarios VIP activos
        now = datetime.now()
        vip_query = select(User).where(
            and_(
                User.is_vip == True,
                or_(
                    User.vip_expires_at.is_(None),
                    User.vip_expires_at > now
                )
            )
        )
        vip_result = await session.execute(vip_query)
        vip_count = len(vip_result.scalars().all())
        
        # Contar usuarios totales
        total_query = select(User)
        total_result = await session.execute(total_query)
        total_count = len(total_result.scalars().all())
        
        # Calcular usuarios gratuitos
        free_count = total_count - admin_count - vip_count
        
        return {
            "total_users": total_count,
            "admins": admin_count,
            "vip_users": vip_count,
            "free_users": free_count,
            "admin_percentage": round((admin_count / total_count) * 100, 2) if total_count > 0 else 0,
            "vip_percentage": round((vip_count / total_count) * 100, 2) if total_count > 0 else 0,
            "free_percentage": round((free_count / total_count) * 100, 2) if total_count > 0 else 0
        }