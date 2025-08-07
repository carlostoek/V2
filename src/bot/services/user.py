"""Servicio de gestión de usuarios."""

from typing import Optional, Dict, Any, List
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, and_, or_

from .base import BaseService
from ..database.models.user import User
from ..database.models.gamification import UserPoints

logger = structlog.get_logger()

class UserService(BaseService[User]):
    """Servicio para gestionar usuarios."""
    
    def __init__(self):
        super().__init__(User)
    
    async def get_user(self, session: AsyncSession, user_id: int) -> Optional[User]:
        """Obtiene un usuario por su ID."""
        return await self.get_by_id(session, user_id)
    
    async def get_users_by_role(self, session: AsyncSession, is_admin: bool = False, is_vip: bool = False) -> List[User]:
        """Obtiene usuarios por rol."""
        self.logger.debug("Obteniendo usuarios por rol", is_admin=is_admin, is_vip=is_vip)
        
        query = select(User)
        conditions = []
        
        if is_admin:
            conditions.append(User.is_admin == True)
        
        if is_vip:
            conditions.append(User.is_vip == True)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        result = await session.execute(query)
        return list(result.scalars().all())
    
    async def search_users(
        self,
        search_term: str,
        *,
        is_active: bool = True,
        is_admin: Optional[bool] = None,
        is_vip: Optional[bool] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[User]:
        """Búsqueda avanzada de usuarios con filtros y paginación.
        
        Args:
            search_term: Término para buscar en username, first_name, last_name
            is_active: Filtrar por usuarios activos/inactivos
            is_admin: Filtrar por estado admin (None para ignorar)
            is_vip: Filtrar por estado VIP (None para ignorar)
            limit: Máximo de resultados
            offset: Desplazamiento para paginación
            
        Returns:
            Lista de usuarios que coinciden con los criterios
        """
        session = await self.session()
        try:
            query = select(User).where(
                and_(
                    User.is_active == is_active,
                    or_(
                        User.username.ilike(f"%{search_term}%"),
                        User.first_name.ilike(f"%{search_term}%"),
                        User.last_name.ilike(f"%{search_term}%")
                    ),
                    *([
                        User.is_admin == is_admin
                    ] if is_admin is not None else []),
                    *([
                        User.is_vip == is_vip
                    ] if is_vip is not None else [])
                )
            ).limit(limit).offset(offset)
            
            result = await session.execute(query)
            return list(result.scalars().all())
            
        except Exception as e:
            self.logger.error("Error en búsqueda de usuarios", 
                             error=str(e),
                             search_term=search_term)
            raise
    
    async def create_or_update_user(
        self, session: AsyncSession, user_id: int, user_data: Dict[str, Any]
    ) -> User:
        """Crea o actualiza un usuario."""
        self.logger.debug("Creando o actualizando usuario", user_id=user_id)
        
        user = await self.get_user(session, user_id)
        if user:
            # Actualizar usuario existente
            user = await self.update(session, user_id, user_data)
            self.logger.info("Usuario actualizado", user_id=user_id)
        else:
            # Crear nuevo usuario
            user_data["id"] = user_id
            user = await self.create(session, user_data)
            
            # Crear registro de puntos para el usuario
            points_data = {
                "user_id": user_id,
                "current_points": 0.0,
                "total_earned": 0.0,
            }
            
            user_points = UserPoints(**points_data)
            session.add(user_points)
            
            self.logger.info("Nuevo usuario creado", user_id=user_id)
        
        return user
    
    async def set_vip_status(self, session: AsyncSession, user_id: int, is_vip: bool) -> Optional[User]:
        """Establece el estado VIP de un usuario."""
        self.logger.debug("Estableciendo estado VIP", user_id=user_id, is_vip=is_vip)
        
        user = await self.get_user(session, user_id)
        if user:
            user.is_vip = is_vip
            await session.flush()
            
            self.logger.info("Estado VIP actualizado", user_id=user_id, is_vip=is_vip)
            return user
        
        return None
    
    async def set_admin_status(self, session: AsyncSession, user_id: int, is_admin: bool) -> Optional[User]:
        """Establece el estado de administrador de un usuario."""
        self.logger.debug("Estableciendo estado de administrador", user_id=user_id, is_admin=is_admin)
        
        user = await self.get_user(session, user_id)
        if user:
            user.is_admin = is_admin
            await session.flush()
            
            self.logger.info("Estado de administrador actualizado", user_id=user_id, is_admin=is_admin)
            return user
        
        return None
    
    async def increment_stats(self, session: AsyncSession, user_id: int, messages: int = 0, reactions: int = 0) -> None:
        """Incrementa las estadísticas de un usuario."""
        self.logger.debug("Incrementando estadísticas", user_id=user_id, messages=messages, reactions=reactions)
        
        if not messages and not reactions:
            return
            
        update_values = {}
        if messages:
            update_values["messages_count"] = User.messages_count + messages
        if reactions:
            update_values["reactions_count"] = User.reactions_count + reactions
            
        await session.execute(
            update(User)
            .where(User.id == user_id)
            .values(**update_values)
        )
    
    async def is_admin(self, session: AsyncSession, user_id: int) -> bool:
        """Verifica si un usuario es administrador."""
        user = await self.get_user(session, user_id)
        return user is not None and user.is_admin
