"""Handlers para usuarios VIP."""
from aiogram import Router, types
from aiogram.filters import Command

vip_router = Router()
vip_router.message.filter(flags={"role": "vip"})

@vip_router.message(Command("vip_feature"))
async def vip_feature_handler(message: types.Message):
    """Handler para una característica VIP de ejemplo."""
    await message.answer("¡Bienvenido, usuario VIP! Aquí tienes tu contenido exclusivo.")
