from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from ...keyboards.admin.main_kb import get_admin_main_keyboard
from ...filters.is_admin import IsAdminFilter

admin_main_router = Router()

@admin_main_router.message(Command("admin"), IsAdminFilter())
async def admin_start(message: Message):
    """Handler para el comando /admin."""
    await message.answer(
        "Bienvenido al panel de administración.",
        reply_markup=get_admin_main_keyboard()
    )
