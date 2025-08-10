from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession

from ...keyboards.admin.main_kb import get_admin_main_keyboard, get_admin_stats_keyboard, get_tariff_management_keyboard
from ...filters.role import IsAdminFilter
from src.modules.admin.service import AdminService
from src.modules.token.tokeneitor import Tokeneitor
from src.modules.channel.service import ChannelService
from src.core.event_bus import EventBus

admin_main_router = Router()

@admin_main_router.message(Command("admin"), IsAdminFilter())
async def admin_start(message: Message, session: AsyncSession):
    """Handler para el comando /admin."""
    user_id = message.from_user.id
    username = message.from_user.username or f"User_{user_id}"
    
    # Obtener estadísticas rápidas
    event_bus = EventBus()
    tokeneitor = Tokeneitor(event_bus)
    
    # Mensaje de bienvenida completo
    welcome_text = "👑 **PANEL DE ADMINISTRACIÓN - DIANA BOT V2**\n\n"
    welcome_text += "🎯 **Sistema Monetario Completo**\n"
    welcome_text += "• Gestión de Tarifas y Precios\n"
    welcome_text += "• Generación y Control de Tokens VIP\n"
    welcome_text += "• Estadísticas de Ventas en Tiempo Real\n"
    welcome_text += "• Control de Usuarios y Suscripciones\n"
    welcome_text += "• Gestión de Canales VIP/Free\n\n"
    welcome_text += f"👨‍💼 **Admin:** {username}\n"
    welcome_text += f"🕐 **Sesión iniciada:** {message.date.strftime('%H:%M:%S')}\n\n"
    welcome_text += "🚀 **¡Sistema listo para generar ingresos!**\n"
    welcome_text += "Selecciona una opción del menú:"
    
    await message.answer(
        welcome_text,
        parse_mode="Markdown",
        reply_markup=get_admin_main_keyboard()
    )

@admin_main_router.callback_query(F.data.startswith("admin:"))
async def handle_admin_callbacks(callback_query: CallbackQuery, session: AsyncSession):
    """Handler para callbacks del panel administrativo."""
    data = callback_query.data.split(":")
    section = data[1]
    
    if section == "stats":
        await show_admin_stats(callback_query, session)
    elif section == "tariffs":
        # Redirigir al handler de tariff_management
        from .tariff_management import show_tariff_management
        await show_tariff_management(callback_query, session)
    elif section == "tokens":
        # Redirigir al handler de token_management
        from .token_management import show_token_management
        await show_token_management(callback_query, session)
    elif section == "users":
        # Será implementado en user_management.py
        await callback_query.answer("👥 Gestión de usuarios - En construcción...")
    elif section == "channels":
        # Será implementado en channel_management.py
        await callback_query.answer("📢 Gestión de canales - En construcción...")
    elif section == "settings":
        await callback_query.answer("⚙️ Configuraciones - En construcción...")
    elif section == "main":
        # Volver al menú principal
        await admin_start(callback_query.message, session)
        await callback_query.answer()
    else:
        await callback_query.answer("Opción no disponible")

async def show_admin_stats(callback_query: CallbackQuery, session: AsyncSession):
    """Muestra estadísticas principales del bot."""
    try:
        event_bus = EventBus()
        tokeneitor = Tokeneitor(event_bus)
        
        # Obtener estadísticas básicas (simuladas por ahora)
        stats_text = "📊 **ESTADÍSTICAS DEL BOT**\n\n"
        stats_text += "👥 **Usuarios:**\n"
        stats_text += "• Total: 1,234\n"
        stats_text += "• VIP Activos: 89\n"
        stats_text += "• Free: 1,145\n"
        stats_text += "• Nuevos Hoy: 23\n\n"
        
        stats_text += "💰 **Ingresos (Mes Actual):**\n"
        stats_text += "• Tokens Generados: 156\n"
        stats_text += "• Tokens Canjeados: 142\n"
        stats_text += "• Tasa de Conversión: 91.0%\n"
        stats_text += "• Ingresos Estimados: $4,260.00\n\n"
        
        stats_text += "🏷️ **Tarifas Populares:**\n"
        stats_text += "• VIP 1 Mes: 67 ventas\n"
        stats_text += "• VIP 1 Semana: 45 ventas\n"
        stats_text += "• VIP 3 Meses: 30 ventas\n\n"
        
        stats_text += "📈 **Actividad:**\n"
        stats_text += "• Mensajes Hoy: 2,847\n"
        stats_text += "• Canal VIP: 892 mensajes\n"
        stats_text += "• Canal Free: 1,955 mensajes\n"
        
        await callback_query.message.edit_text(
            stats_text,
            parse_mode="Markdown",
            reply_markup=get_admin_stats_keyboard()
        )
        await callback_query.answer()
        
    except Exception as e:
        await callback_query.answer(f"Error al obtener estadísticas: {str(e)}")

@admin_main_router.callback_query(F.data == "admin:refresh_stats")
async def refresh_stats(callback_query: CallbackQuery, session: AsyncSession):
    """Actualiza las estadísticas."""
    await show_admin_stats(callback_query, session)
    await callback_query.answer("📊 Estadísticas actualizadas")
