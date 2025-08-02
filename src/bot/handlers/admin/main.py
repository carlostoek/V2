from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from ...keyboards.admin.main_kb import get_admin_main_keyboard, get_admin_stats_keyboard, get_admin_settings_keyboard, get_admin_roles_keyboard
from ...filters.role import IsAdminFilter

admin_main_router = Router()

@admin_main_router.message(Command("admin"), IsAdminFilter())
async def admin_start(message: Message):
    """Handler para el comando /admin."""
    welcome_text = (
        "🛠️ **Panel de Administración**\n\n"
        "Bienvenido al centro de control del bot.\n"
        "Desde aquí puedes gestionar canales, configurar\n"
        "el juego, narrativa y configuración general.\n\n"
        "Selecciona una opción del menú:"
    )
    
    await message.answer(
        welcome_text,
        parse_mode="Markdown",
        reply_markup=await get_admin_main_keyboard()
    )

@admin_main_router.callback_query(F.data == "admin:main")
async def admin_main_callback(callback: CallbackQuery):
    """Callback para volver al menú principal del admin."""
    welcome_text = (
        "🛠️ **Panel de Administración**\n\n"
        "Bienvenido al centro de control del bot.\n"
        "Desde aquí puedes gestionar canales, configurar\n"
        "el juego, narrativa y configuración general.\n\n"
        "Selecciona una opción del menú:"
    )
    
    await callback.message.edit_text(
        welcome_text,
        parse_mode="Markdown",
        reply_markup=await get_admin_main_keyboard()
    )
    await callback.answer()

@admin_main_router.callback_query(F.data == "admin:channel_vip")
async def admin_channel_vip_callback(callback: CallbackQuery):
    """Callback para configuración del canal VIP."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    from ...keyboards.admin.main_kb import get_channel_name
    
    channel_name = await get_channel_name("vip")
    
    text = (
        f"💎 **Configuración Canal VIP: {channel_name}**\n\n"
        "Administra tu canal VIP desde este menú.\n\n"
        "**Opciones disponibles:**\n"
        "• Configurar canal\n"
        "• Gestionar miembros\n"
        "• Contenido programado\n"
        "• Estadísticas\n"
        "• Configuración de acceso"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚙️ Configurar Canal", callback_data="vip:configure")],
        [InlineKeyboardButton(text="👥 Gestionar Miembros", callback_data="vip:members")],
        [InlineKeyboardButton(text="📅 Contenido Programado", callback_data="vip:content")],
        [InlineKeyboardButton(text="📊 Estadísticas", callback_data="vip:stats")],
        [InlineKeyboardButton(text="🔐 Configuración Acceso", callback_data="vip:access")],
        [InlineKeyboardButton(text="🔙 Volver", callback_data="admin:main")]
    ])
    
    await callback.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    await callback.answer()

@admin_main_router.callback_query(F.data == "admin:channel_free")
async def admin_channel_free_callback(callback: CallbackQuery):
    """Callback para configuración del canal Free."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    from ...keyboards.admin.main_kb import get_channel_name
    
    channel_name = await get_channel_name("free")
    
    text = (
        f"🆓 **Configuración Canal Free: {channel_name}**\n\n"
        "Administra tu canal gratuito desde este menú.\n\n"
        "**Opciones disponibles:**\n"
        "• Configurar canal\n"
        "• Gestionar miembros\n"
        "• Contenido programado\n"
        "• Estadísticas\n"
        "• Moderación automática"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚙️ Configurar Canal", callback_data="free:configure")],
        [InlineKeyboardButton(text="👥 Gestionar Miembros", callback_data="free:members")],
        [InlineKeyboardButton(text="📅 Contenido Programado", callback_data="free:content")],
        [InlineKeyboardButton(text="📊 Estadísticas", callback_data="free:stats")],
        [InlineKeyboardButton(text="🤖 Moderación Auto", callback_data="free:moderation")],
        [InlineKeyboardButton(text="🔙 Volver", callback_data="admin:main")]
    ])
    
    await callback.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    await callback.answer()

@admin_main_router.callback_query(F.data == "admin:gamification")
async def admin_gamification_callback(callback: CallbackQuery):
    """Callback para configuración de gamificación."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    text = (
        "🎮 **Configuración Juego el Diván**\n\n"
        "Administra el sistema de gamificación del bot.\n\n"
        "**Opciones disponibles:**\n"
        "• Configurar misiones\n"
        "• Sistema de puntos\n"
        "• Recompensas y premios\n"
        "• Ranking de usuarios\n"
        "• Eventos especiales"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎯 Configurar Misiones", callback_data="game:missions")],
        [InlineKeyboardButton(text="🎆 Sistema de Puntos", callback_data="game:points")],
        [InlineKeyboardButton(text="🏆 Recompensas", callback_data="game:rewards")],
        [InlineKeyboardButton(text="🏅 Ranking", callback_data="game:ranking")],
        [InlineKeyboardButton(text="🎉 Eventos", callback_data="game:events")],
        [InlineKeyboardButton(text="🔙 Volver", callback_data="admin:main")]
    ])
    
    await callback.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    await callback.answer()

@admin_main_router.callback_query(F.data == "admin:narrative")
async def admin_narrative_callback(callback: CallbackQuery):
    """Callback para configuración de narrativa."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    text = (
        "📖 **Configuración de Narrativa**\n\n"
        "Administra el sistema narrativo del bot.\n\n"
        "**Opciones disponibles:**\n"
        "• Configurar historias\n"
        "• Personajes y diálogos\n"
        "• Progreso narrativo\n"
        "• Integración con Diana\n"
        "• Contenido adaptativo"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📜 Configurar Historias", callback_data="narrative:stories")],
        [InlineKeyboardButton(text="👥 Personajes", callback_data="narrative:characters")],
        [InlineKeyboardButton(text="📋 Progreso", callback_data="narrative:progress")],
        [InlineKeyboardButton(text="🤖 Integración Diana", callback_data="narrative:diana")],
        [InlineKeyboardButton(text="🎭 Contenido Adaptativo", callback_data="narrative:adaptive")],
        [InlineKeyboardButton(text="🔙 Volver", callback_data="admin:main")]
    ])
    
    await callback.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    await callback.answer()

@admin_main_router.callback_query(F.data == "admin:settings")
async def admin_settings_callback(callback: CallbackQuery):
    """Callback para configuración general del sistema."""
    text = (
        "⚙️ **Configuración General**\n\n"
        "Ajustes generales del bot y sistema.\n\n"
        "**Configuraciones disponibles:**\n"
        "• Configuración del bot\n"
        "• Gestión de usuarios\n"
        "• Tarifas y tokens\n"
        "• Notificaciones\n"
        "• Mantenimiento"
    )
    
    await callback.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=get_admin_settings_keyboard()
    )
    await callback.answer()
