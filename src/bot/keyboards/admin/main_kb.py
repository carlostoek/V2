from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_admin_main_keyboard() -> InlineKeyboardMarkup:
    """Devuelve el teclado principal del panel de administración."""
    buttons = [
        [
            InlineKeyboardButton(text="📊 Estadísticas", callback_data="admin:stats"),
            InlineKeyboardButton(text="💰 Tarifas", callback_data="admin:tariffs")
        ],
        [
            InlineKeyboardButton(text="🎫 Tokens VIP", callback_data="admin:tokens"),
            InlineKeyboardButton(text="👥 Usuarios", callback_data="admin:users")
        ],
        [
            InlineKeyboardButton(text="📢 Canales", callback_data="admin:channels"),
            InlineKeyboardButton(text="🔔 Notificaciones", callback_data="admin:notifications")
        ],
        [
            InlineKeyboardButton(text="⚙️ Configuración", callback_data="admin:settings"),
            InlineKeyboardButton(text="📊 Exportar Datos", callback_data="admin:export")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_admin_stats_keyboard() -> InlineKeyboardMarkup:
    """Devuelve el teclado para la sección de estadísticas."""
    buttons = [
        [
            InlineKeyboardButton(text="🔄 Actualizar", callback_data="admin:refresh_stats"),
            InlineKeyboardButton(text="📈 Gráficos", callback_data="admin:charts")
        ],
        [
            InlineKeyboardButton(text="📤 Exportar", callback_data="admin:export_stats"),
            InlineKeyboardButton(text="🎯 Métricas", callback_data="admin:metrics")
        ],
        [InlineKeyboardButton(text="⬅️ Volver", callback_data="admin:main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_tariff_management_keyboard() -> InlineKeyboardMarkup:
    """Devuelve el teclado para gestión de tarifas."""
    buttons = [
        [
            InlineKeyboardButton(text="➕ Nueva Tarifa", callback_data="tariff:create"),
            InlineKeyboardButton(text="📋 Ver Todas", callback_data="tariff:list")
        ],
        [
            InlineKeyboardButton(text="✏️ Editar", callback_data="tariff:edit"),
            InlineKeyboardButton(text="❌ Desactivar", callback_data="tariff:deactivate")
        ],
        [
            InlineKeyboardButton(text="📊 Estadísticas", callback_data="tariff:stats"),
            InlineKeyboardButton(text="💰 Precios", callback_data="tariff:pricing")
        ],
        [InlineKeyboardButton(text="⬅️ Volver", callback_data="admin:main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_token_management_keyboard() -> InlineKeyboardMarkup:
    """Devuelve el teclado para gestión de tokens."""
    buttons = [
        [
            InlineKeyboardButton(text="🎫 Generar Token", callback_data="token:generate"),
            InlineKeyboardButton(text="📋 Ver Tokens", callback_data="token:list")
        ],
        [
            InlineKeyboardButton(text="🔍 Buscar Token", callback_data="token:search"),
            InlineKeyboardButton(text="📊 Estadísticas", callback_data="token:stats")
        ],
        [
            InlineKeyboardButton(text="📦 Generar Lote", callback_data="token:bulk_generate"),
            InlineKeyboardButton(text="📤 Exportar", callback_data="token:export")
        ],
        [InlineKeyboardButton(text="⬅️ Volver", callback_data="admin:main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_user_management_keyboard() -> InlineKeyboardMarkup:
    """Devuelve el teclado para gestión de usuarios."""
    buttons = [
        [
            InlineKeyboardButton(text="🔍 Buscar Usuario", callback_data="user:search"),
            InlineKeyboardButton(text="📋 Lista VIP", callback_data="user:list_vip")
        ],
        [
            InlineKeyboardButton(text="👑 Otorgar VIP", callback_data="user:grant_vip"),
            InlineKeyboardButton(text="❌ Revocar VIP", callback_data="user:revoke_vip")
        ],
        [
            InlineKeyboardButton(text="🚫 Banear", callback_data="user:ban"),
            InlineKeyboardButton(text="✅ Desbanear", callback_data="user:unban")
        ],
        [
            InlineKeyboardButton(text="📊 Estadísticas", callback_data="user:stats"),
            InlineKeyboardButton(text="📤 Exportar", callback_data="user:export")
        ],
        [InlineKeyboardButton(text="⬅️ Volver", callback_data="admin:main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_channel_management_keyboard() -> InlineKeyboardMarkup:
    """Devuelve el teclado para gestión de canales."""
    buttons = [
        [
            InlineKeyboardButton(text="📢 Canal VIP", callback_data="channel:vip"),
            InlineKeyboardButton(text="🆓 Canal Free", callback_data="channel:free")
        ],
        [
            InlineKeyboardButton(text="➕ Nuevo Canal", callback_data="channel:create"),
            InlineKeyboardButton(text="⚙️ Configurar", callback_data="channel:config")
        ],
        [
            InlineKeyboardButton(text="👥 Miembros", callback_data="channel:members"),
            InlineKeyboardButton(text="📊 Actividad", callback_data="channel:activity")
        ],
        [InlineKeyboardButton(text="⬅️ Volver", callback_data="admin:main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
