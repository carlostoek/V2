from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_admin_main_keyboard() -> InlineKeyboardMarkup:
    """Devuelve el teclado principal del panel de administración."""
    buttons = [
        [InlineKeyboardButton(text="🏷️ Gestionar Tarifas", callback_data="admin:tariffs")],
        [InlineKeyboardButton(text="🔗 Generar Tokens", callback_data="admin:tokens")],
        [InlineKeyboardButton(text="👑 Gestión de Roles", callback_data="admin:roles")],
        [InlineKeyboardButton(text="📊 Estadísticas", callback_data="admin:stats")],
        [InlineKeyboardButton(text="⚙️ Configuración", callback_data="admin:settings")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
