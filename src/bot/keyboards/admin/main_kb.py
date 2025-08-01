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

def get_admin_stats_keyboard() -> InlineKeyboardMarkup:
    """Devuelve el teclado de estadísticas del administrador."""
    buttons = [
        [InlineKeyboardButton(text="👥 Usuarios Activos", callback_data="stats:users")],
        [InlineKeyboardButton(text="💎 Conversiones VIP", callback_data="stats:conversions")],
        [InlineKeyboardButton(text="📖 Engagement Narrativo", callback_data="stats:narrative")],
        [InlineKeyboardButton(text="🎮 Gamificación", callback_data="stats:gamification")],
        [InlineKeyboardButton(text="🔄 Resumen General", callback_data="stats:general")],
        [InlineKeyboardButton(text="🔙 Volver", callback_data="admin:main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_admin_settings_keyboard() -> InlineKeyboardMarkup:
    """Devuelve el teclado de configuración del administrador."""
    buttons = [
        [InlineKeyboardButton(text="💬 Mensajes Auto", callback_data="settings:auto_messages")],
        [InlineKeyboardButton(text="⏰ Timeouts", callback_data="settings:timeouts")],
        [InlineKeyboardButton(text="📺 Canales", callback_data="settings:channels")],
        [InlineKeyboardButton(text="🎯 Gamificación", callback_data="settings:gamification")],
        [InlineKeyboardButton(text="🔧 Sistema", callback_data="settings:system")],
        [InlineKeyboardButton(text="🔙 Volver", callback_data="admin:main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_admin_roles_keyboard() -> InlineKeyboardMarkup:
    """Devuelve el teclado de gestión de roles."""
    buttons = [
        [InlineKeyboardButton(text="👤 Buscar Usuario", callback_data="roles:search")],
        [InlineKeyboardButton(text="👑 Listar Admins", callback_data="roles:list_admins")],
        [InlineKeyboardButton(text="💎 Listar VIPs", callback_data="roles:list_vips")],
        [InlineKeyboardButton(text="📊 Estadísticas Roles", callback_data="roles:stats")],
        [InlineKeyboardButton(text="🔧 Mantenimiento", callback_data="roles:maintenance")],
        [InlineKeyboardButton(text="🔙 Volver", callback_data="admin:main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
