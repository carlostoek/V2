from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from ...keyboards.admin.main_kb import get_admin_main_keyboard, get_admin_stats_keyboard, get_admin_settings_keyboard, get_admin_roles_keyboard
from ...filters.role import IsAdminFilter

admin_main_router = Router()

@admin_main_router.message(Command("admin"))
async def admin_start(message: Message):
    """Handler para el comando /admin."""
    user_id = message.from_user.id
    print(f"🎯 ADMIN HANDLER MODERNO: Ejecutando comando admin para user_id: {user_id}")
    
    # Verificar admin hardcodeado
    if user_id != 1280444712:
        print(f"🚫 ADMIN MODERNO: Usuario {user_id} no es administrador")
        await message.answer("❌ No tienes permisos de administrador.")
        return
    
    print(f"✅ ADMIN MODERNO: Usuario admin autenticado: {user_id}")
    
    # Mensaje personalizado del panel moderno
    welcome_text = "🛠️ **Panel de Administración Moderno**\n\n"
    welcome_text += "• Gestión completa de usuarios y roles\n"
    welcome_text += "• Administración de canales VIP y gratuitos\n"
    welcome_text += "• Gestión de tarifas y tokens\n"
    welcome_text += "• Acceso a estadísticas y analíticas\n"
    welcome_text += "\n🆕 **SISTEMA MODERNO ACTIVO**\n"
    welcome_text += "Selecciona una opción del menú:"
    
    await message.answer(
        welcome_text,
        parse_mode="Markdown",
        reply_markup=get_admin_main_keyboard()
    )

@admin_main_router.callback_query(F.data == "admin:main")
async def admin_main_callback(callback: CallbackQuery):
    """Callback para volver al menú principal del admin."""
    user_role = getattr(callback.message, 'user_role', 'free')
    user_permissions = getattr(callback.message, 'user_permissions', {})
    
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
    
    await callback.message.edit_text(
        welcome_text,
        parse_mode="Markdown",
        reply_markup=get_admin_main_keyboard()
    )
    await callback.answer()

@admin_main_router.callback_query(F.data == "admin:tariffs")
async def admin_tariffs_callback(callback: CallbackQuery):
    """Callback para gestión de tarifas."""
    # NOTE: AdminKeyboardFactory import removed - using inline keyboard instead
    
    text = (
        "🏷️ **Gestión de Tarifas**\n\n"
        "Desde aquí puedes crear nuevas tarifas, generar enlaces de invitación "
        "y ver estadísticas de uso.\n\n"
        "**Funciones disponibles:**\n"
        "• Crear nuevas tarifas VIP\n"
        "• Generar enlaces de invitación\n"
        "• Ver estadísticas de tokens\n"
        "• Administrar tarifas existentes"
    )
    
    # Crear teclado inline para tarifas
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🆕 Nueva Tarifa", callback_data="tariff:new")],
        [InlineKeyboardButton(text="🔗 Generar Token", callback_data="tariff:generate")],
        [InlineKeyboardButton(text="📊 Estadísticas", callback_data="tariff:stats")],
        [InlineKeyboardButton(text="📋 Ver Tarifas", callback_data="tariff:list")],
        [InlineKeyboardButton(text="🔙 Volver", callback_data="admin:main")]
    ])
    
    await callback.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    await callback.answer()

@admin_main_router.callback_query(F.data == "admin:tokens")
async def admin_tokens_callback(callback: CallbackQuery):
    """Callback para generación de tokens."""
    text = (
        "🔑 **Generación de Tokens**\n\n"
        "Genera tokens de acceso para usuarios VIP.\n\n"
        "**Opciones disponibles:**\n"
        "• Generar token individual\n"
        "• Generar tokens masivos\n"
        "• Ver tokens activos\n"
        "• Invalidar tokens"
    )
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎯 Token Individual", callback_data="token:individual")],
        [InlineKeyboardButton(text="📦 Tokens Masivos", callback_data="token:bulk")],
        [InlineKeyboardButton(text="👀 Ver Activos", callback_data="token:active")],
        [InlineKeyboardButton(text="🚫 Invalidar Token", callback_data="token:invalidate")],
        [InlineKeyboardButton(text="🔙 Volver", callback_data="admin:main")]
    ])
    
    await callback.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    await callback.answer()

@admin_main_router.callback_query(F.data == "admin:stats")
async def admin_stats_callback(callback: CallbackQuery):
    """Callback para estadísticas del sistema."""
    text = (
        "📊 **Estadísticas del Sistema**\n\n"
        "Analíticas completas de tu bot y usuarios.\n\n"
        "**Estadísticas disponibles:**\n"
        "• Usuarios activos\n"
        "• Conversiones VIP\n"
        "• Engagement narrativo\n"
        "• Performance de gamificación"
    )
    
    await callback.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=get_admin_stats_keyboard()
    )
    await callback.answer()

@admin_main_router.callback_query(F.data == "admin:settings")
async def admin_settings_callback(callback: CallbackQuery):
    """Callback para configuración del sistema."""
    text = (
        "⚙️ **Configuración del Sistema**\n\n"
        "Ajustes generales del bot y funcionalidades.\n\n"
        "**Configuraciones disponibles:**\n"
        "• Mensajes automáticos\n"
        "• Timeouts y eliminación\n"
        "• Configuración de canales\n"
        "• Ajustes de gamificación"
    )
    
    await callback.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=get_admin_settings_keyboard()
    )
    await callback.answer()

@admin_main_router.callback_query(F.data == "admin:roles")
async def admin_roles_callback(callback: CallbackQuery):
    """Callback para gestión de roles."""
    text = (
        "👑 **Gestión de Roles**\n\n"
        "Administra usuarios, roles y permisos del sistema.\n\n"
        "**Funciones disponibles:**\n"
        "• Buscar y modificar usuarios\n"
        "• Otorgar/revocar roles VIP\n"
        "• Gestionar administradores\n"
        "• Ver estadísticas de roles\n"
        "• Mantenimiento automático"
    )
    
    await callback.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=get_admin_roles_keyboard()
    )
    await callback.answer()
