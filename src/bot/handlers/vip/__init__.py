"""Registro de handlers VIP."""
from aiogram import Router
from .main import vip_router

vip_main_router = Router()
vip_main_router.include_router(vip_router)

def register_vip_handlers(dp):
    dp.include_router(vip_main_router)
