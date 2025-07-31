from aiogram import types

def get_main_menu_keyboard() -> types.InlineKeyboardMarkup:
    """Genera el teclado del menú principal."""
    buttons = [
        [types.InlineKeyboardButton(text="📜 Historia", callback_data="main_menu:narrative")],
        [
            types.InlineKeyboardButton(text="🏆 Perfil", callback_data="main_menu:profile"),
            types.InlineKeyboardButton(text="🎯 Misiones", callback_data="main_menu:missions")
        ],
        [types.InlineKeyboardButton(text="🎒 Mochila", callback_data="main_menu:inventory")],
        [types.InlineKeyboardButton(text="❓ Ayuda", callback_data="main_menu:help")]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)

def get_admin_menu_keyboard() -> types.InlineKeyboardMarkup:
    """Genera el teclado del menú principal de administración."""
    buttons = [
        [types.InlineKeyboardButton(text="🆓 Administrar Canal Gratuito", callback_data="admin:free_channel_menu")],
        [types.InlineKeyboardButton(text="💎 Administrar Canal VIP", callback_data="admin:vip_channel_menu")]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)

def get_free_channel_admin_kb(configured: bool) -> types.InlineKeyboardMarkup:
    """Genera el teclado para la administración del canal gratuito."""
    buttons = []
    if configured:
        buttons.extend([
            [types.InlineKeyboardButton(text="⏰ Configurar Tiempo de Espera", callback_data="admin:set_wait_time")],
            [types.InlineKeyboardButton(text="📝 Enviar Contenido al Canal", callback_data="admin:send_to_free_channel")]
        ])
    else:
        buttons.append([types.InlineKeyboardButton(text="⚙️ Configurar Canal", callback_data="admin:setup_free_channel")])
    
    buttons.append([types.InlineKeyboardButton(text="⬅️ Volver", callback_data="admin:main_menu")])
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)

def get_wait_time_selection_kb() -> types.InlineKeyboardMarkup:
    """Genera el teclado para seleccionar el tiempo de espera."""
    buttons = [
        [
            types.InlineKeyboardButton(text="Inmediato", callback_data="admin:set_wait_time_0"),
            types.InlineKeyboardButton(text="15 min", callback_data="admin:set_wait_time_15"),
            types.InlineKeyboardButton(text="1 hora", callback_data="admin:set_wait_time_60")
        ],
        [
            types.InlineKeyboardButton(text="12 horas", callback_data="admin:set_wait_time_720"),
            types.InlineKeyboardButton(text="24 horas", callback_data="admin:set_wait_time_1440")
        ],
        [types.InlineKeyboardButton(text="⬅️ Volver", callback_data="admin:free_channel_menu")]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)

def get_post_confirmation_kb() -> types.InlineKeyboardMarkup:
    """Genera el teclado para confirmar un post."""
    buttons = [
        [types.InlineKeyboardButton(text="✅ Enviar Post", callback_data="admin:confirm_post")],
        [types.InlineKeyboardButton(text="❌ Cancelar", callback_data="admin:cancel_post")]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)

def get_vip_admin_menu_kb(tariffs: list[dict]) -> types.InlineKeyboardMarkup:
    """Genera el teclado para la administración del canal VIP."""
    buttons = []
    for tariff in tariffs:
        text = f"{tariff['name']} - ${tariff['price']} - {tariff['duration_days']} días"
        buttons.append([types.InlineKeyboardButton(text=text, callback_data=f"admin:view_tariff_{tariff['id']}")])
    
    buttons.append([types.InlineKeyboardButton(text="➕ Crear Nueva Tarifa", callback_data="admin:create_tariff")])
    buttons.append([types.InlineKeyboardButton(text="⬅️ Volver", callback_data="admin:main_menu")])
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)

def get_tariff_view_kb(tariff_id: int) -> types.InlineKeyboardMarkup:
    """Genera el teclado para ver una tarifa."""
    buttons = [
        [types.InlineKeyboardButton(text="🎟️ Generar Token", callback_data=f"admin:generate_token_{tariff_id}")],
        [types.InlineKeyboardButton(text="🗑️ Eliminar Tarifa", callback_data=f"admin:delete_tariff_{tariff_id}")],
        [types.InlineKeyboardButton(text="⬅️ Volver", callback_data="admin:vip_channel_menu")]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)