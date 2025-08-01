"""Registro de handlers de administración."""
from aiogram import Router
from .main import admin_main_router
from .tariff import tariff_router

admin_router = Router()
admin_router.include_router(admin_main_router)
admin_router.include_router(tariff_router)

def register_admin_handlers(dp):
    dp.include_router(admin_router)
