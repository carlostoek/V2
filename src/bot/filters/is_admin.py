"""Filtro para verificar si un usuario es administrador."""

from typing import Any
from aiogram.filters.base import Filter
from aiogram.types import Message, CallbackQuery

from ..config.settings import settings


class IsAdminFilter(Filter):
    """
    Filtro que verifica si el usuario es administrador.
    
    Verifica tanto:
    1. Variable de entorno ADMIN_USER_IDS
    2. Campo is_admin en la base de datos (opcional, para futuro)
    
    Usage:
        @router.message(Command("admin"), IsAdminFilter())
        async def admin_command(message: Message):
            # Solo ejecutado por administradores
            pass
    """
    
    def __init__(self):
        """Inicializa el filtro."""
        pass
    
    async def __call__(self, obj: Any) -> bool:
        """
        Verifica si el usuario es administrador.
        
        Args:
            obj: Objeto de aiogram (Message, CallbackQuery, etc.)
            
        Returns:
            bool: True si es administrador, False en caso contrario
        """
        # Extraer user_id del objeto
        user_id = None
        
        if isinstance(obj, (Message, CallbackQuery)):
            if obj.from_user:
                user_id = obj.from_user.id
        
        if user_id is None:
            return False
        
        # Verificar si está en la lista de administradores de la configuración
        admin_ids = settings.admin_ids
        is_admin_by_config = user_id in admin_ids
        
        if is_admin_by_config:
            return True
            
        # TODO: En el futuro, también verificar is_admin en la base de datos
        # Por ahora solo usamos la configuración
        
        return False
    
    def __repr__(self) -> str:
        """Representación del filtro."""
        return f"IsAdminFilter(admin_ids={settings.admin_ids})"