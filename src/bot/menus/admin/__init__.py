"""
Módulo principal del sistema de menús administrativos unificados.

Este sistema reemplaza los 5 sistemas anteriores y proporciona:
- Gestión centralizada de todos los flujos administrativos
- Teclados dinámicos basados en permisos
- Integración con todos los servicios existentes
"""
from .keyboards import AdminKeyboardFactory
from .handlers import setup_admin_handlers
from .service import AdminMenuService

__all__ = ['AdminKeyboardFactory', 'setup_admin_handlers', 'AdminMenuService']
