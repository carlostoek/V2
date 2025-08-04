"""Callbacks adicionales para el panel de administración."""

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from ...keyboards.admin.main_kb import (
    get_admin_main_keyboard,
    get_admin_stats_keyboard, 
    get_admin_settings_keyboard,
    get_admin_roles_keyboard
)
from ...filters.role import IsAdminFilter

admin_callbacks_router = Router()

# =============================================================================
# CALLBACKS DE ESTADÍSTICAS
# =============================================================================

@admin_callbacks_router.callback_query(F.data == "stats:users")
async def stats_users_callback(callback: CallbackQuery):
    """Muestra estadísticas de usuarios activos."""
    text = (
        "👥 **Usuarios Activos**\n\n"
        "📊 **Estadísticas generales:**\n"
        "• Total de usuarios: 1,234\n"
        "• Usuarios activos (7 días): 456\n"
        "• Usuarios activos (30 días): 789\n"
        "• Nuevos usuarios (hoy): 12\n\n"
        "🎯 **Engagement:**\n"
        "• Tasa de retención: 78%\n"
        "• Promedio mensajes/usuario: 15.3\n"
        "• Usuarios más activos: Top 10"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📈 Ver Tendencias", callback_data="stats:trends")],
        [InlineKeyboardButton(text="🔍 Análisis Detallado", callback_data="stats:detailed")],
        [InlineKeyboardButton(text="🔙 Volver a Stats", callback_data="admin:stats")]
    ])
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer()

@admin_callbacks_router.callback_query(F.data == "stats:conversions")
async def stats_conversions_callback(callback: CallbackQuery):
    """Muestra estadísticas de conversiones VIP."""
    text = (
        "💎 **Conversiones VIP**\n\n"
        "📊 **Métricas de conversión:**\n"
        "• Total VIPs: 89\n"
        "• Conversiones este mes: 23\n"
        "• Tasa de conversión: 12.5%\n"
        "• Revenue mensual: $1,456\n\n"
        "📈 **Tendencias:**\n"
        "• Crecimiento vs mes anterior: +18%\n"
        "• Tarifa más popular: Premium Mensual\n"
        "• Mejor día para conversiones: Viernes"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Revenue Detallado", callback_data="stats:revenue")],
        [InlineKeyboardButton(text="📊 Por Tarifa", callback_data="stats:by_tariff")],
        [InlineKeyboardButton(text="🔙 Volver a Stats", callback_data="admin:stats")]
    ])
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer()

@admin_callbacks_router.callback_query(F.data == "stats:narrative")
async def stats_narrative_callback(callback: CallbackQuery):
    """Muestra estadísticas de engagement narrativo."""
    text = (
        "📖 **Engagement Narrativo**\n\n"
        "📚 **Progreso de historias:**\n"
        "• Usuarios activos en narrativa: 456\n"
        "• Fragmentos completados hoy: 89\n"
        "• Tasa de finalización: 67%\n"
        "• Historia más popular: \"El Misterio\"\n\n"
        "🎯 **Interacciones:**\n"
        "• Reacciones promedio/fragmento: 8.5\n"
        "• Decisiones tomadas hoy: 234\n"
        "• Tiempo promedio/sesión: 12 min"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📚 Por Historia", callback_data="stats:by_story")],
        [InlineKeyboardButton(text="🎯 Decisiones", callback_data="stats:decisions")],
        [InlineKeyboardButton(text="🔙 Volver a Stats", callback_data="admin:stats")]
    ])
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer()

@admin_callbacks_router.callback_query(F.data == "stats:gamification")
async def stats_gamification_callback(callback: CallbackQuery):
    """Muestra estadísticas de gamificación."""
    text = (
        "🎮 **Gamificación**\n\n"
        "🏆 **Puntos y logros:**\n"
        "• Total \"besitos\" otorgados: 15,678\n"
        "• Promedio puntos/usuario: 45.2\n"
        "• Logros desbloqueados hoy: 34\n"
        "• Top usuario: @usuario123 (890 pts)\n\n"
        "🎯 **Misiones:**\n"
        "• Misiones activas: 12\n"
        "• Tasa de completado: 73%\n"
        "• Recompensas canjeadas: 156"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏆 Top Usuarios", callback_data="stats:leaderboard")],
        [InlineKeyboardButton(text="🎯 Misiones", callback_data="stats:missions")],
        [InlineKeyboardButton(text="🔙 Volver a Stats", callback_data="admin:stats")]
    ])
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer()

@admin_callbacks_router.callback_query(F.data == "stats:general")
async def stats_general_callback(callback: CallbackQuery):
    """Muestra resumen general de estadísticas."""
    text = (
        "🔄 **Resumen General**\n\n"
        "📊 **Estado del Sistema:**\n"
        "• Sistema: ✅ Operativo\n"
        "• Uptime: 99.8%\n"
        "• Último backup: Hace 2 horas\n"
        "• Memoria uso: 45%\n\n"
        "📈 **KPIs Principales:**\n"
        "• DAU (Usuarios activos diarios): 456\n"
        "• Engagement rate: 78%\n"
        "• Conversion rate: 12.5%\n"
        "• Revenue mensual: $1,456"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Dashboard Completo", callback_data="stats:dashboard")],
        [InlineKeyboardButton(text="⚠️ Alertas", callback_data="stats:alerts")],
        [InlineKeyboardButton(text="🔙 Volver a Stats", callback_data="admin:stats")]
    ])
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer()

# =============================================================================
# CALLBACKS DE CONFIGURACIÓN
# =============================================================================

@admin_callbacks_router.callback_query(F.data == "settings:auto_messages")
async def settings_auto_messages_callback(callback: CallbackQuery):
    """Configuración de mensajes automáticos."""
    text = (
        "💬 **Mensajes Automáticos**\n\n"
        "⚙️ **Estado actual:**\n"
        "• Mensajes de bienvenida: ✅ Activo\n"
        "• Notificaciones de logros: ✅ Activo\n"
        "• Recordatorios de misiones: ✅ Activo\n"
        "• Auto-eliminación sistema: ✅ Activo (10s)\n\n"
        "📝 **Configuraciones:**\n"
        "• Intervalo recordatorios: 24h\n"
        "• Timeout mensajes: 10 segundos\n"
        "• Idioma por defecto: Español"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Editar Mensajes", callback_data="settings:edit_messages")],
        [InlineKeyboardButton(text="⏰ Configurar Timeouts", callback_data="settings:timeouts")],
        [InlineKeyboardButton(text="🔧 Avanzado", callback_data="settings:advanced_messages")],
        [InlineKeyboardButton(text="🔙 Volver", callback_data="admin:settings")]
    ])
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer()

@admin_callbacks_router.callback_query(F.data == "settings:timeouts")
async def settings_timeouts_callback(callback: CallbackQuery):
    """Configuración de timeouts."""
    text = (
        "⏰ **Configuración de Timeouts**\n\n"
        "⚙️ **Timeouts actuales:**\n"
        "• Mensajes de sistema: 10 segundos\n"
        "• Notificaciones: 15 segundos\n"
        "• Mensajes de error: 8 segundos\n"
        "• Confirmaciones: 5 segundos\n\n"
        "🔧 **Configuraciones especiales:**\n"
        "• No eliminar mensajes VIP: ✅\n"
        "• Eliminar en canales públicos: ✅\n"
        "• Respetar mensajes fijados: ✅"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏱️ Ajustar Sistema", callback_data="timeout:system")],
        [InlineKeyboardButton(text="📢 Ajustar Notificaciones", callback_data="timeout:notifications")],
        [InlineKeyboardButton(text="🔙 Volver", callback_data="admin:settings")]
    ])
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer()

@admin_callbacks_router.callback_query(F.data == "settings:channels")
async def settings_channels_callback(callback: CallbackQuery):
    """Configuración de canales."""
    text = (
        "📺 **Configuración de Canales**\n\n"
        "📋 **Canales registrados:**\n"
        "• @canal_vip_principal - VIP (1,234 miembros)\n"
        "• @canal_free_general - Free (5,678 miembros)\n"
        "• @canal_admins - Admin (5 miembros)\n\n"
        "⚙️ **Configuraciones:**\n"
        "• Auto-moderación: ✅ Activa\n"
        "• Verificación ingreso: ✅ Activa\n"
        "• Logs de actividad: ✅ Activos"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Agregar Canal", callback_data="channels:add")],
        [InlineKeyboardButton(text="✏️ Editar Canal", callback_data="channels:edit")],
        [InlineKeyboardButton(text="📊 Estadísticas", callback_data="channels:stats")],
        [InlineKeyboardButton(text="🔙 Volver", callback_data="admin:settings")]
    ])
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer()

@admin_callbacks_router.callback_query(F.data == "settings:gamification")
async def settings_gamification_callback(callback: CallbackQuery):
    """Configuración de gamificación."""
    text = (
        "🎯 **Configuración de Gamificación**\n\n"
        "⚙️ **Sistema de puntos:**\n"
        "• Nombre moneda: \"besitos\" 💋\n"
        "• Puntos por reacción: 5\n"
        "• Puntos por narrativa: 10\n"
        "• Multiplicador VIP: 2x\n\n"
        "🏆 **Logros y misiones:**\n"
        "• Auto-generación misiones: ✅\n"
        "• Notificar logros: ✅\n"
        "• Leaderboard público: ✅"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Configurar Puntos", callback_data="gamif:points")],
        [InlineKeyboardButton(text="🏆 Gestionar Logros", callback_data="gamif:achievements")],
        [InlineKeyboardButton(text="🎯 Crear Misiones", callback_data="gamif:missions")],
        [InlineKeyboardButton(text="🔙 Volver", callback_data="admin:settings")]
    ])
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer()

@admin_callbacks_router.callback_query(F.data == "settings:system")
async def settings_system_callback(callback: CallbackQuery):
    """Configuración del sistema."""
    text = (
        "🔧 **Configuración del Sistema**\n\n"
        "⚙️ **Estado general:**\n"
        "• Versión: DianaBot V2.1.0\n"
        "• Base de datos: ✅ Conectada\n"
        "• Diana AI: ✅ Operativa\n"
        "• Event Bus: ✅ Funcionando\n\n"
        "🔧 **Configuraciones técnicas:**\n"
        "• Debug mode: ❌ Desactivado\n"
        "• Logs nivel: INFO\n"
        "• Cache TTL: 300s"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Ver Logs", callback_data="system:logs")],
        [InlineKeyboardButton(text="💾 Backup Manual", callback_data="system:backup")],
        [InlineKeyboardButton(text="🔄 Reiniciar Servicios", callback_data="system:restart")],
        [InlineKeyboardButton(text="🔙 Volver", callback_data="admin:settings")]
    ])
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer()

# =============================================================================
# CALLBACKS PLACEHOLDER PARA FUNCIONALIDADES AVANZADAS
# =============================================================================

@admin_callbacks_router.callback_query(F.data.startswith("placeholder:"))
async def placeholder_callback(callback: CallbackQuery):
    """Callback placeholder para funcionalidades en desarrollo."""
    feature = callback.data.split(":")[1]
    
    text = (
        "🚧 **Funcionalidad en Desarrollo**\n\n"
        f"La función **{feature}** está siendo implementada.\n\n"
        "Estará disponible en una próxima actualización.\n"
        "¡Gracias por tu paciencia! 🚀"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Volver", callback_data="admin:main")]
    ])
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer("🚧 Funcionalidad en desarrollo")
