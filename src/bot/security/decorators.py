"""Decoradores para la verificación de roles."""
import functools
from typing import Callable, Any
from aiogram import types
from src.bot.security.authorization import AuthorizationService

def require_role(role: str):
    """Decorador para verificar el rol de un usuario."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(self, message: types.Message, *args, **kwargs):
            auth_service: AuthorizationService = self._auth_service
            user_id = message.from_user.id
            session = kwargs.get("session") # Asume que la sesión está en los argumentos

            has_permission = False
            if role == "admin":
                has_permission = await auth_service.is_admin(session, user_id)
            elif role == "vip":
                has_permission = await auth_service.is_vip(session, user_id)

            if not has_permission:
                await message.answer("No tienes permiso para realizar esta acción.")
                return

            return await func(self, message, *args, **kwargs)
        return wrapper
    return decorator
