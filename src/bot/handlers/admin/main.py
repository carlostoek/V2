from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from ...keyboards.admin.main_kb import get_admin_main_keyboard
from ...filters.role import IsAdminFilter

admin_main_router = Router()

@admin_main_router.message(Command("admin"), IsAdminFilter())
async def admin_start(message: Message):
    """Handler para el comando /admin."""
    user_role = message.bot.data.get("user_role", "free")
    user_permissions = message.bot.data.get("user_permissions", {})
    
    # Mensaje personalizado según permisos
    welcome_text = "🛠️ **Panel de Administración**\n\n"
    
    if user_permissions.get("can_manage_users"):
        welcome_text += "• Gestión completa de usuarios y roles\n"
    if user_permissions.get("can_manage_channels"):
        welcome_text += "• Administración de canales VIP y gratuitos\n"
    if user_permissions.get("can_manage_tariffs"):
        welcome_text += "• Gestión de tarifas y tokens\n"
    if user_permissions.get("can_view_analytics"):
        welcome_text += "• Acceso a estadísticas y analíticas\n"
    
    welcome_text += "\nSelecciona una opción del menú:"
    
    await message.answer(
        welcome_text,
        parse_mode="Markdown",
        reply_markup=get_admin_main_keyboard()
    )
