"""Filtros personalizados para el bot."""

from .is_admin import IsAdminFilter
from .role import RoleFilter, IsAdminFilter as NewIsAdminFilter, IsVIPFilter, IsVIPOrAdminFilter, PermissionFilter

__all__ = [
    "IsAdminFilter", 
    "RoleFilter", 
    "NewIsAdminFilter", 
    "IsVIPFilter", 
    "IsVIPOrAdminFilter", 
    "PermissionFilter"
]