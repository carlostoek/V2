"""Middleware para la autorización de usuarios."""
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from src.bot.security.authorization import AuthorizationService

class AuthMiddleware(BaseMiddleware):
    def __init__(self, auth_service: AuthorizationService):
        self._auth_service = auth_service

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        role = data.get("role")
        if not role:
            return await handler(event, data)

        user = data.get("event_from_user")
        if not user:
            return await handler(event, data)

        session = data.get("session")
        has_permission = False
        if role == "admin":
            has_permission = await self._auth_service.is_admin(session, user.id)
        elif role == "vip":
            has_permission = await self._auth_service.is_vip(session, user.id)

        if not has_permission:
            await event.answer("No tienes permiso para realizar esta acción.")
            return

        return await handler(event, data)
