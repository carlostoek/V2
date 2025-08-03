"""Handlers de administración."""

from .main import admin_main_router
from .callbacks import admin_callbacks_router
from .token_callbacks import token_callbacks_router
from .tariff import register_tariff_handlers
from .role_management import register_role_management_handlers
from .narrativa import router as narrativa_router

def register_admin_handlers(dp, admin_service):
    """Registra todos los handlers de administración."""
    # Router principal de admin
    dp.include_router(admin_main_router)
    
    # Router de callbacks adicionales
    dp.include_router(admin_callbacks_router)
    
    # Router de callbacks de tokens
    dp.include_router(token_callbacks_router)
    
    # Handlers de tarifas
    register_tariff_handlers(dp, admin_service)
    
    # Handlers de gestión de roles
    register_role_management_handlers(dp)
