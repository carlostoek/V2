from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.orm import Session
from ...database.engine import get_session
from ...database.models.channel import Channel

async def get_channel_name(channel_type: str) -> str:
    """Obtiene el nombre del canal VIP o Free configurado."""
    try:
        session: Session = next(get_session())
        channel = session.query(Channel).filter(
            Channel.type == channel_type,
            Channel.is_active == True
        ).first()
        
        if channel:
            return channel.name
        else:
            return "Canal VIP" if channel_type == "vip" else "Canal Free"
    except Exception:
        return "Canal VIP" if channel_type == "vip" else "Canal Free"
    finally:
        if 'session' in locals():
            session.close()

async def get_admin_main_keyboard() -> InlineKeyboardMarkup:
    """Devuelve el teclado principal del panel de administración con estructura 2x3."""
    
    # Obtener nombres de canales
    vip_channel_name = await get_channel_name("vip")
    free_channel_name = await get_channel_name("free")
    
    buttons = [
        [
            InlineKeyboardButton(text=f"💎 {vip_channel_name}", callback_data="admin:channel_vip"),
            InlineKeyboardButton(text=f"🆓 {free_channel_name}", callback_data="admin:channel_free")
        ],
        [
            InlineKeyboardButton(text="🎮 Juego el Diván", callback_data="admin:gamification"),
            InlineKeyboardButton(text="📖 Narrativa", callback_data="admin:narrative")
        ],
        [
            InlineKeyboardButton(text="⚙️ Configuración", callback_data="admin:settings")
        ]
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
