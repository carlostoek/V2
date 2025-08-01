"""Middleware para sincronizar administradores."""

from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from ..config.settings import settings
from ..services.user import UserService
from ..database.engine import get_session


class AdminSyncMiddleware(BaseMiddleware):
    """
    Middleware que sincroniza automáticamente los administradores
    desde la configuración hacia la base de datos.
    """
    
    def __init__(self):
        """Inicializa el middleware."""
        self.user_service = UserService()
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        """
        Procesa el evento y sincroniza administradores si es necesario.
        
        Args:
            handler: Handler a ejecutar
            event: Evento de aiogram
            data: Datos del contexto
            
        Returns:
            Resultado del handler
        """
        # Solo procesar si es un usuario
        if not event.from_user:
            return await handler(event, data)
        
        user_id = event.from_user.id
        
        # Verificar si está en la lista de admin IDs de configuración
        admin_ids = settings.admin_ids
        is_config_admin = user_id in admin_ids
        
        if is_config_admin:
            # Sincronizar con la base de datos
            try:
                async for session in get_session():
                    # Obtener o crear usuario
                    user_data = {
                        "username": event.from_user.username,
                        "first_name": event.from_user.first_name,
                        "last_name": event.from_user.last_name,
                        "language_code": event.from_user.language_code,
                    }
                    
                    user = await self.user_service.create_or_update_user(
                        session, user_id, user_data
                    )
                    
                    # Asegurar que tenga privilegios de admin en DB
                    if not user.is_admin:
                        await self.user_service.set_admin_status(session, user_id, True)
                        await session.commit()
                    
                    break
            except Exception as e:
                # No fallar si hay problemas con la DB
                print(f"Error sincronizando admin {user_id}: {e}")
        
        # Continuar con el handler normal
        return await handler(event, data)