"""Middleware para gestionar roles y sincronización automática."""

from typing import Callable, Dict, Any, Awaitable
import structlog
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession

from ..services.role import RoleService
from ..config.settings import settings

logger = structlog.get_logger()

class RoleMiddleware(BaseMiddleware):
    """
    Middleware que gestiona roles y sincronización automática.
    
    Responsabilidades:
    - Sincronizar administradores desde configuración
    - Verificar expiraciones VIP
    - Añadir información de rol al contexto
    """
    
    def __init__(self):
        """Inicializa el middleware."""
        self.role_service = RoleService()
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """
        Procesa el evento y gestiona roles.
        
        Args:
            handler: Handler a ejecutar
            event: Evento de aiogram
            data: Datos del contexto
            
        Returns:
            Resultado del handler
        """
        # Solo procesar si es un usuario
        user = None
        if isinstance(event, (Message, CallbackQuery)):
            user = event.from_user
        
        if not user:
            return await handler(event, data)
        
        user_id = user.id
        session = data.get("session")
        
        if not isinstance(session, AsyncSession):
            return await handler(event, data)
        
        try:
            # Datos del usuario de Telegram
            user_data = {
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "language_code": user.language_code,
            }
            
            # Sincronizar administrador desde configuración
            await self.role_service.sync_admin_from_config(session, user_id, user_data)
            
            # Obtener rol actual del usuario
            user_role = await self.role_service.get_user_role(session, user_id)
            
            # Obtener permisos del usuario
            permissions = await self.role_service.get_user_permissions(session, user_id)
            
            # Añadir información de rol al contexto
            data["user_role"] = user_role
            data["user_permissions"] = permissions
            data["role_service"] = self.role_service
            
            # Commit para guardar cambios de sincronización
            await session.commit()
            
        except Exception as e:
            logger.error("Error en middleware de roles", error=str(e), user_id=user_id)
            await session.rollback()
            
            # Añadir datos por defecto en caso de error
            data["user_role"] = "free"
            data["user_permissions"] = {"can_use_bot": True}
            data["role_service"] = self.role_service
        
        # Continuar con el handler normal
        return await handler(event, data)


class RoleCheckMiddleware(BaseMiddleware):
    """
    Middleware que verifica roles antes de ejecutar handlers.
    
    Este middleware se puede usar para bloquear automáticamente
    acceso a handlers que requieren roles específicos.
    """
    
    def __init__(self, required_role: str = None, required_permission: str = None):
        """
        Inicializa el middleware.
        
        Args:
            required_role: Rol requerido para acceder.
            required_permission: Permiso requerido para acceder.
        """
        self.required_role = required_role
        self.required_permission = required_permission
        self.role_service = RoleService()
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """
        Verifica roles antes de ejecutar el handler.
        
        Args:
            handler: Handler a ejecutar
            event: Evento de aiogram
            data: Datos del contexto
            
        Returns:
            Resultado del handler o None si no tiene permisos
        """
        # Solo verificar si hay requisitos configurados
        if not self.required_role and not self.required_permission:
            return await handler(event, data)
        
        # Obtener información del usuario
        user = None
        if isinstance(event, (Message, CallbackQuery)):
            user = event.from_user
        
        if not user:
            return await handler(event, data)
        
        user_id = user.id
        session = data.get("session")
        
        if not isinstance(session, AsyncSession):
            return await handler(event, data)
        
        try:
            # Verificar rol si es requerido
            if self.required_role:
                user_role = await self.role_service.get_user_role(session, user_id)
                if user_role != self.required_role:
                    logger.warning(
                        "Acceso denegado por rol", 
                        user_id=user_id, 
                        required_role=self.required_role,
                        user_role=user_role
                    )
                    
                    # Enviar mensaje de error si es posible
                    if isinstance(event, Message):
                        await event.answer("❌ No tienes permisos para usar este comando.")
                    elif isinstance(event, CallbackQuery):
                        await event.answer("❌ No tienes permisos para esta acción.", show_alert=True)
                    
                    return None
            
            # Verificar permiso si es requerido
            if self.required_permission:
                has_permission = await self.role_service.check_permission(
                    session, user_id, self.required_permission
                )
                if not has_permission:
                    logger.warning(
                        "Acceso denegado por permiso", 
                        user_id=user_id, 
                        required_permission=self.required_permission
                    )
                    
                    # Enviar mensaje de error si es posible
                    if isinstance(event, Message):
                        await event.answer("❌ No tienes permisos para usar este comando.")
                    elif isinstance(event, CallbackQuery):
                        await event.answer("❌ No tienes permisos para esta acción.", show_alert=True)
                    
                    return None
            
            # Si pasa todas las verificaciones, ejecutar handler
            return await handler(event, data)
            
        except Exception as e:
            logger.error("Error en verificación de roles", error=str(e), user_id=user_id)
            return await handler(event, data)