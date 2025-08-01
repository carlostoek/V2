"""Filtros para verificar roles de usuarios."""

from typing import Any, Union
from aiogram.filters.base import Filter
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from ..services.role import RoleService, RoleType
from ..database.engine import get_session


class RoleFilter(Filter):
    """
    Filtro base para verificar roles de usuarios.
    
    Usage:
        @router.message(Command("admin"), RoleFilter(RoleType.ADMIN))
        async def admin_command(message: Message):
            # Solo ejecutado por administradores
            pass
    """
    
    def __init__(self, required_role: str):
        """
        Inicializa el filtro.
        
        Args:
            required_role: Rol requerido (admin, vip, free).
        """
        self.required_role = required_role
        self.role_service = RoleService()
    
    async def __call__(self, obj: Union[Message, CallbackQuery]) -> bool:
        """
        Verifica si el usuario tiene el rol requerido.
        
        Args:
            obj: Objeto de aiogram (Message, CallbackQuery, etc.)
            
        Returns:
            bool: True si tiene el rol requerido, False en caso contrario
        """
        # Extraer user_id del objeto
        user_id = None
        
        if isinstance(obj, (Message, CallbackQuery)):
            if obj.from_user:
                user_id = obj.from_user.id
        
        if user_id is None:
            return False
        
        # Verificar rol usando la base de datos
        try:
            async for session in get_session():
                user_role = await self.role_service.get_user_role(session, user_id)
                return user_role == self.required_role
        except Exception:
            # En caso de error, denegar acceso
            return False
    
    def __repr__(self) -> str:
        """Representación del filtro."""
        return f"RoleFilter(required_role={self.required_role})"


class IsAdminFilter(RoleFilter):
    """
    Filtro específico para administradores.
    
    Usage:
        @router.message(Command("admin"), IsAdminFilter())
        async def admin_command(message: Message):
            # Solo ejecutado por administradores
            pass
    """
    
    def __init__(self):
        """Inicializa el filtro para administradores."""
        super().__init__(RoleType.ADMIN)


class IsVIPFilter(RoleFilter):
    """
    Filtro específico para usuarios VIP.
    
    Usage:
        @router.message(Command("vip"), IsVIPFilter())
        async def vip_command(message: Message):
            # Solo ejecutado por usuarios VIP
            pass
    """
    
    def __init__(self):
        """Inicializa el filtro para usuarios VIP."""
        super().__init__(RoleType.VIP)


class IsVIPOrAdminFilter(Filter):
    """
    Filtro que permite acceso a usuarios VIP o administradores.
    
    Usage:
        @router.message(Command("premium"), IsVIPOrAdminFilter())
        async def premium_command(message: Message):
            # Solo ejecutado por VIP o administradores
            pass
    """
    
    def __init__(self):
        """Inicializa el filtro."""
        self.role_service = RoleService()
    
    async def __call__(self, obj: Union[Message, CallbackQuery]) -> bool:
        """
        Verifica si el usuario es VIP o administrador.
        
        Args:
            obj: Objeto de aiogram.
            
        Returns:
            bool: True si es VIP o administrador.
        """
        # Extraer user_id del objeto
        user_id = None
        
        if isinstance(obj, (Message, CallbackQuery)):
            if obj.from_user:
                user_id = obj.from_user.id
        
        if user_id is None:
            return False
        
        # Verificar rol
        try:
            async for session in get_session():
                user_role = await self.role_service.get_user_role(session, user_id)
                return user_role in [RoleType.ADMIN, RoleType.VIP]
        except Exception:
            return False
    
    def __repr__(self) -> str:
        """Representación del filtro."""
        return "IsVIPOrAdminFilter()"


class PermissionFilter(Filter):
    """
    Filtro que verifica permisos específicos.
    
    Usage:
        @router.message(Command("manage"), PermissionFilter("can_manage_channels"))
        async def manage_command(message: Message):
            # Solo ejecutado por usuarios con permiso de gestión
            pass
    """
    
    def __init__(self, required_permission: str):
        """
        Inicializa el filtro.
        
        Args:
            required_permission: Permiso requerido.
        """
        self.required_permission = required_permission
        self.role_service = RoleService()
    
    async def __call__(self, obj: Union[Message, CallbackQuery]) -> bool:
        """
        Verifica si el usuario tiene el permiso requerido.
        
        Args:
            obj: Objeto de aiogram.
            
        Returns:
            bool: True si tiene el permiso.
        """
        # Extraer user_id del objeto
        user_id = None
        
        if isinstance(obj, (Message, CallbackQuery)):
            if obj.from_user:
                user_id = obj.from_user.id
        
        if user_id is None:
            return False
        
        # Verificar permiso
        try:
            async for session in get_session():
                return await self.role_service.check_permission(session, user_id, self.required_permission)
        except Exception:
            return False
    
    def __repr__(self) -> str:
        """Representación del filtro."""
        return f"PermissionFilter(required_permission={self.required_permission})"