from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_admin_main_keyboard() -> InlineKeyboardMarkup:
    """Devuelve el teclado principal del panel de administración."""
    buttons = [
        [InlineKeyboardButton(text="Gestionar Tarifas", callback_data="admin:tariffs")],
        [InlineKeyboardButton(text="Generar Token", callback_data="admin:tokens")],
        [InlineKeyboardButton(text="Estadísticas", callback_data="admin:stats")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
