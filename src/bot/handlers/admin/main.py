from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

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
        # Redirigir al handler de user_management
        from .user_management import show_user_management
        await show_user_management(callback_query, session)
    elif section == "channels":
        # Será implementado en channel_management.py
        await callback_query.answer("📢 Gestión de canales - En construcción...")
    elif section == "notifications":
        # Redirigir al handler de notifications
        from .notifications import show_notification_panel
        await show_notification_panel(callback_query, session)
    elif section == "export":
        # Redirigir al handler de exportación
        await handle_data_export(callback_query, session)
    elif section == "settings":
        # Redirigir al handler de configuration
        from .configuration import show_configuration_panel
        await show_configuration_panel(callback_query, session)
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
        admin_service = AdminService(event_bus)
        
        # Obtener estadísticas reales
        user_stats = await admin_service.get_user_statistics()
        revenue_stats = await admin_service.get_revenue_statistics()
        top_tariffs = await admin_service.get_top_tariffs(3)
        
        stats_text = "📊 **ESTADÍSTICAS DEL BOT EN TIEMPO REAL**\n\n"
        stats_text += "👥 **Usuarios:**\n"
        stats_text += f"• Total: {user_stats['total_users']:,}\n"
        stats_text += f"• VIP Activos: {user_stats['vip_users']:,}\n"
        stats_text += f"• Free: {user_stats['free_users']:,}\n"
        stats_text += f"• Activos (7 días): {user_stats['active_users']:,}\n"
        stats_text += f"• Nuevos Hoy: {user_stats['today_new_users']:,}\n"
        stats_text += f"• Baneados: {user_stats['banned_users']:,}\n\n"
        
        stats_text += "💰 **Ingresos (Mes Actual):**\n"
        stats_text += f"• Tokens Generados: {revenue_stats['tokens_generated']:,}\n"
        stats_text += f"• Tokens Canjeados: {revenue_stats['tokens_redeemed']:,}\n"
        stats_text += f"• Tasa de Conversión: {revenue_stats['conversion_rate']:.1f}%\n"
        stats_text += f"• Ingresos Estimados: ${revenue_stats['estimated_revenue']:,.2f}\n\n"
        
        if top_tariffs:
            stats_text += "🏷️ **Tarifas Más Populares:**\n"
            for tariff in top_tariffs:
                stats_text += f"• {tariff['name']}: {tariff['sales']} ventas (${tariff['revenue']:.2f})\n"
            stats_text += "\n"
        
        # Métricas calculadas
        total_users = user_stats['total_users']
        if total_users > 0:
            vip_rate = (user_stats['vip_users'] / total_users) * 100
            activity_rate = (user_stats['active_users'] / total_users) * 100
            
            stats_text += "📈 **Métricas de Rendimiento:**\n"
            stats_text += f"• Tasa de Conversión VIP: {vip_rate:.1f}%\n"
            stats_text += f"• Tasa de Actividad: {activity_rate:.1f}%\n"
            if revenue_stats['tokens_generated'] > 0:
                stats_text += f"• Eficiencia de Tokens: {revenue_stats['conversion_rate']:.1f}%\n"
        
        stats_text += f"\n🕐 **Última actualización:** {datetime.now().strftime('%H:%M:%S')}"
        
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

async def handle_data_export(callback_query: CallbackQuery, session: AsyncSession):
    """Maneja la exportación de datos."""
    try:
        event_bus = EventBus()
        admin_service = AdminService(event_bus)
        
        text = "📊 **EXPORTACIÓN DE DATOS**\n\n"
        text += "Exporta estadísticas y datos para análisis externo\n\n"
        
        text += "📈 **Datos Disponibles:**\n"
        text += "• Estadísticas de usuarios\n"
        text += "• Datos de ingresos y tokens\n"
        text += "• Información de tarifas\n"
        text += "• Historial de suscripciones\n"
        text += "• Métricas de engagement\n\n"
        
        text += "🔄 **Formatos:**\n"
        text += "• JSON para análisis programático\n"
        text += "• Texto formateado para reportes\n\n"
        
        text += "⚠️ **Nota:**\n"
        text += "Los datos exportados contienen información sensible.\n"
        text += "Manéjalos con cuidado y siguiendo políticas de privacidad."
        
        keyboard = [
            [
                InlineKeyboardButton(text="📊 Exportar JSON", callback_data="export:json"),
                InlineKeyboardButton(text="📄 Exportar Texto", callback_data="export:text")
            ],
            [
                InlineKeyboardButton(text="📈 Reporte Completo", callback_data="export:full_report"),
                InlineKeyboardButton(text="💰 Solo Ingresos", callback_data="export:revenue")
            ],
            [InlineKeyboardButton(text="⬅️ Panel Admin", callback_data="admin:main")]
        ]
        
        await callback_query.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
        await callback_query.answer()
        
    except Exception as e:
        await callback_query.answer(f"Error: {str(e)}")

@admin_main_router.callback_query(F.data.startswith("export:"))
async def handle_export_actions(callback_query: CallbackQuery, session: AsyncSession):
    """Maneja las acciones de exportación."""
    try:
        export_type = callback_query.data.split(":")[-1]
        
        event_bus = EventBus()
        admin_service = AdminService(event_bus)
        
        # Generar datos de exportación
        if export_type == "json":
            result = await admin_service.export_statistics(format="json", date_range=30)
        elif export_type == "text":
            result = await admin_service.export_statistics(format="text", date_range=30)
        elif export_type == "full_report":
            result = await admin_service.export_statistics(format="full", date_range=30)
        elif export_type == "revenue":
            result = await admin_service.export_statistics(format="revenue", date_range=30)
        else:
            await callback_query.answer("❌ Tipo de exportación no válido")
            return
        
        if not result["success"]:
            await callback_query.answer(f"❌ Error: {result.get('error', 'Error desconocido')}")
            return
        
        # Mostrar datos exportados
        data = result["data"]
        
        text = f"✅ **EXPORTACIÓN COMPLETADA**\n\n"
        text += f"📅 **Fecha de exportación:** {data['export_date'].strftime('%d/%m/%Y %H:%M')}\n"
        text += f"📊 **Período:** {data['date_range_days']} días\n"
        text += f"📄 **Formato:** {data['format']}\n\n"
        
        # Mostrar resumen de datos
        if 'user_statistics' in data:
            user_stats = data['user_statistics']
            text += f"👥 **Usuarios:**\n"
            text += f"• Total: {user_stats['total_users']:,}\n"
            text += f"• VIP: {user_stats['vip_users']:,}\n"
            text += f"• Activos: {user_stats['active_users']:,}\n\n"
        
        if 'revenue_statistics' in data:
            revenue_stats = data['revenue_statistics']
            text += f"💰 **Ingresos:**\n"
            text += f"• Tokens generados: {revenue_stats['tokens_generated']:,}\n"
            text += f"• Tokens canjeados: {revenue_stats['tokens_redeemed']:,}\n"
            text += f"• Ingresos estimados: ${revenue_stats['estimated_revenue']:,.2f}\n\n"
        
        if 'top_tariffs' in data:
            text += f"🏆 **Top Tarifas:**\n"
            for tariff in data['top_tariffs'][:3]:
                text += f"• {tariff['name']}: {tariff['sales']} ventas\n"
        
        text += f"\n💾 **Datos JSON:** Ver abajo\n"
        text += f"📋 **Copia el siguiente código para usar en análisis:**"
        
        # Crear archivo JSON simplificado
        import json
        json_data = json.dumps(data, indent=2, default=str)
        
        # Enviar primero el resumen
        keyboard = [
            [InlineKeyboardButton(text="🔄 Nueva Exportación", callback_data="admin:export")],
            [InlineKeyboardButton(text="⬅️ Panel Admin", callback_data="admin:main")]
        ]
        
        await callback_query.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
        
        # Enviar datos JSON por separado
        json_text = f"```json\n{json_data[:3000]}{'...' if len(json_data) > 3000 else ''}\n```"
        await callback_query.message.answer(
            f"📊 **DATOS EXPORTADOS ({export_type.upper()})**\n\n{json_text}",
            parse_mode="Markdown"
        )
        
        await callback_query.answer("✅ Datos exportados exitosamente")
        
    except Exception as e:
        await callback_query.answer(f"Error en exportación: {str(e)}")
