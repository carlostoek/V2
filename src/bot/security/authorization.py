"""Módulo para el servicio de autorización."""
from sqlalchemy.ext.asyncio import AsyncSession
from src.bot.services.user import UserService

class AuthorizationService:
    """Servicio para manejar la lógica de autorización."""

    def __init__(self, user_service: UserService):
        self._user_service = user_service

    async def is_admin(self, session: AsyncSession, user_id: int) -> bool:
        """Verifica si un usuario es administrador."""
        return await self._user_service.is_admin(session, user_id)

    async def is_vip(self, session: AsyncSession, user_id: int) -> bool:
        """Verifica si un usuario es VIP."""
        user = await self._user_service.get_user(session, user_id)
        return user.is_vip if user else False
