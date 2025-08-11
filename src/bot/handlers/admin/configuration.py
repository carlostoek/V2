"""Sistema de configuración avanzada del bot."""

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
from datetime import datetime

from ...filters.role import IsAdminFilter
from src.modules.admin.service import AdminService
from src.core.event_bus import EventBus

configuration_router = Router()

class ConfigurationStates(StatesGroup):
    waiting_for_channel_id = State()
    waiting_for_wait_time = State()
    waiting_for_config_value = State()

@configuration_router.callback_query(F.data == "admin:settings")
async def show_configuration_panel(callback_query: CallbackQuery, session: AsyncSession):
    """Muestra el panel principal de configuración."""
    try:
        event_bus = EventBus()
        admin_service = AdminService(event_bus)
        
        # Obtener configuración actual
        config = await admin_service.get_bot_configuration()
        
        text = "⚙️ **CONFIGURACIÓN AVANZADA DEL BOT**\n\n"
        text += "Panel de control para ajustar el comportamiento del bot\n\n"
        
        text += "🔧 **Configuración Actual:**\n"
        text += f"• Canal Free ID: {config.get('free_channel_id', 'No configurado')}\n"
        text += f"• Tiempo de Espera: {config.get('wait_time_minutes', 15)} minutos\n"
        text += f"• Estado del Sistema: {config.get('system_status', 'unknown').title()}\n"
        
        if config.get('last_updated'):
            last_update = config['last_updated']
            if isinstance(last_update, str):
                text += f"• Última actualización: {last_update[:19]}\n"
            else:
                text += f"• Última actualización: {last_update.strftime('%d/%m/%Y %H:%M')}\n"
        
        text += "\n🎛️ **Configuraciones Disponibles:**\n"
        text += "• Canal gratuito y configuraciones de acceso\n"
        text += "• Tiempos de espera y delays del sistema\n"
        text += "• Configuraciones de notificaciones\n"
        text += "• Parámetros de gamificación\n"
        text += "• Configuraciones de seguridad\n\n"
        
        text += "⚠️ **Importante:**\n"
        text += "Cambios en la configuración afectan el comportamiento\n"
        text += "global del bot. Úsalos con precaución."
        
        keyboard = [
            [
                InlineKeyboardButton(text="📢 Canal Free", callback_data="config:free_channel"),
                InlineKeyboardButton(text="⏰ Tiempos", callback_data="config:timing")
            ],
            [
                InlineKeyboardButton(text="🔔 Notificaciones", callback_data="config:notifications"),
                InlineKeyboardButton(text="🎮 Gamificación", callback_data="config:gamification")
            ],
            [
                InlineKeyboardButton(text="🔐 Seguridad", callback_data="config:security"),
                InlineKeyboardButton(text="💾 Respaldo", callback_data="config:backup")
            ],
            [
                InlineKeyboardButton(text="🔄 Reiniciar Config", callback_data="config:reset"),
                InlineKeyboardButton(text="💾 Guardar Cambios", callback_data="config:save")
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

@configuration_router.callback_query(F.data.startswith("config:"))
async def handle_configuration_actions(callback_query: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Maneja las acciones de configuración."""
    try:
        action = callback_query.data.split(":")[-1]
        
        if action == "free_channel":
            await show_free_channel_config(callback_query, state, session)
        elif action == "timing":
            await show_timing_config(callback_query, state, session)
        elif action == "notifications":
            await show_notifications_config(callback_query, session)
        elif action == "gamification":
            await show_gamification_config(callback_query, session)
        elif action == "security":
            await show_security_config(callback_query, session)
        elif action == "backup":
            await show_backup_config(callback_query, session)
        elif action == "reset":
            await reset_configuration(callback_query, session)
        elif action == "save":
            await save_configuration(callback_query, session)
        else:
            await callback_query.answer("❌ Acción no reconocida")
            
    except Exception as e:
        await callback_query.answer(f"Error: {str(e)}")

async def show_free_channel_config(callback_query: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Muestra configuración del canal gratuito."""
    try:
        event_bus = EventBus()
        admin_service = AdminService(event_bus)
        
        config = await admin_service.get_bot_configuration()
        current_channel = config.get('free_channel_id', 'No configurado')
        
        text = "📢 **CONFIGURACIÓN DEL CANAL FREE**\n\n"
        text += f"Canal actual: `{current_channel}`\n\n"
        
        text += "🔧 **Configurar nuevo canal:**\n"
        text += "1. Agrega el bot como administrador al canal\n"
        text += "2. Copia el ID del canal (número negativo)\n"
        text += "3. Ingresa el ID aquí\n\n"
        
        text += "💡 **¿Cómo obtener el ID del canal?**\n"
        text += "• Forward un mensaje del canal a @userinfobot\n"
        text += "• O usa @getidsbot en el canal\n"
        text += "• El ID se ve como: -1001234567890\n\n"
        
        text += "Ingresa el nuevo ID del canal:"
        
        await state.set_state(ConfigurationStates.waiting_for_channel_id)
        
        keyboard = [
            [InlineKeyboardButton(text="❌ Cancelar", callback_data="admin:settings")]
        ]
        
        await callback_query.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
        await callback_query.answer()
        
    except Exception as e:
        await callback_query.answer(f"Error: {str(e)}")

@configuration_router.message(ConfigurationStates.waiting_for_channel_id)
async def process_channel_id(message: Message, state: FSMContext, session: AsyncSession):
    """Procesa el nuevo ID del canal."""
    try:
        channel_id_str = message.text.strip()
        
        try:
            channel_id = int(channel_id_str)
            
            # Validar que es un ID de canal válido (negativo)
            if channel_id >= 0:
                await message.answer(
                    "❌ **ID inválido**\n\n"
                    "Los IDs de canal deben ser números negativos.\n"
                    "Ejemplo: -1001234567890\n\n"
                    "Intenta nuevamente:"
                )
                return
                
        except ValueError:
            await message.answer(
                "❌ **Formato inválido**\n\n"
                "Por favor ingresa un número válido.\n"
                "Ejemplo: -1001234567890\n\n"
                "Intenta nuevamente:"
            )
            return
        
        # Actualizar configuración
        event_bus = EventBus()
        admin_service = AdminService(event_bus)
        
        result = await admin_service.update_bot_configuration(
            {"free_channel_id": channel_id},
            admin_id=message.from_user.id
        )
        
        await state.clear()
        
        if result["success"]:
            await message.answer(
                f"✅ **Canal Free Actualizado**\n\n"
                f"Nuevo canal ID: `{channel_id}`\n\n"
                f"⚠️ **Importante:**\n"
                f"Asegúrate de que el bot sea administrador del canal\n"
                f"para que funcione correctamente.",
                parse_mode="Markdown"
            )
        else:
            await message.answer(f"❌ Error al actualizar: {result.get('error', 'Error desconocido')}")
            
    except Exception as e:
        await message.answer(f"Error: {str(e)}")
        await state.clear()

async def show_timing_config(callback_query: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Muestra configuración de tiempos."""
    try:
        event_bus = EventBus()
        admin_service = AdminService(event_bus)
        
        config = await admin_service.get_bot_configuration()
        current_time = config.get('wait_time_minutes', 15)
        
        text = "⏰ **CONFIGURACIÓN DE TIEMPOS**\n\n"
        text += f"Tiempo de espera actual: {current_time} minutos\n\n"
        
        text += "🔧 **Configurar nuevo tiempo:**\n"
        text += "Tiempo en minutos antes de aprobar solicitudes\n"
        text += "del canal gratuito automáticamente.\n\n"
        
        text += "⚖️ **Valores recomendados:**\n"
        text += "• 0 minutos: Aprobación inmediata\n"
        text += "• 15 minutos: Tiempo estándar\n"
        text += "• 60 minutos: Tiempo moderado\n"
        text += "• 1440 minutos: 24 horas (máximo)\n\n"
        
        text += "Ingresa el nuevo tiempo en minutos:"
        
        await state.set_state(ConfigurationStates.waiting_for_wait_time)
        
        keyboard = [
            [
                InlineKeyboardButton(text="0 min", callback_data="set_time:0"),
                InlineKeyboardButton(text="15 min", callback_data="set_time:15")
            ],
            [
                InlineKeyboardButton(text="30 min", callback_data="set_time:30"),
                InlineKeyboardButton(text="60 min", callback_data="set_time:60")
            ],
            [InlineKeyboardButton(text="❌ Cancelar", callback_data="admin:settings")]
        ]
        
        await callback_query.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
        await callback_query.answer()
        
    except Exception as e:
        await callback_query.answer(f"Error: {str(e)}")

@configuration_router.callback_query(F.data.startswith("set_time:"))
async def set_wait_time_quick(callback_query: CallbackQuery, session: AsyncSession):
    """Establece tiempo de espera rápidamente."""
    try:
        wait_time = int(callback_query.data.split(":")[-1])
        
        event_bus = EventBus()
        admin_service = AdminService(event_bus)
        
        result = await admin_service.update_bot_configuration(
            {"wait_time_minutes": wait_time},
            admin_id=callback_query.from_user.id
        )
        
        if result["success"]:
            await callback_query.answer(f"✅ Tiempo actualizado a {wait_time} minutos")
            # Volver a mostrar panel de configuración
            await show_configuration_panel(callback_query, session)
        else:
            await callback_query.answer(f"❌ Error: {result.get('error', 'Error desconocido')}")
            
    except Exception as e:
        await callback_query.answer(f"Error: {str(e)}")

@configuration_router.message(ConfigurationStates.waiting_for_wait_time)
async def process_wait_time(message: Message, state: FSMContext, session: AsyncSession):
    """Procesa el nuevo tiempo de espera."""
    try:
        time_str = message.text.strip()
        
        try:
            wait_time = int(time_str)
            
            if wait_time < 0 or wait_time > 1440:
                await message.answer(
                    "❌ **Tiempo inválido**\n\n"
                    "El tiempo debe ser entre 0 y 1440 minutos (24 horas).\n\n"
                    "Intenta nuevamente:"
                )
                return
                
        except ValueError:
            await message.answer(
                "❌ **Formato inválido**\n\n"
                "Por favor ingresa un número entero.\n"
                "Ejemplo: 15\n\n"
                "Intenta nuevamente:"
            )
            return
        
        # Actualizar configuración
        event_bus = EventBus()
        admin_service = AdminService(event_bus)
        
        result = await admin_service.update_bot_configuration(
            {"wait_time_minutes": wait_time},
            admin_id=message.from_user.id
        )
        
        await state.clear()
        
        if result["success"]:
            time_text = f"{wait_time} minutos"
            if wait_time == 0:
                time_text = "inmediata (0 minutos)"
            elif wait_time >= 60:
                hours = wait_time // 60
                minutes = wait_time % 60
                time_text = f"{hours}h {minutes}m"
                
            await message.answer(
                f"✅ **Tiempo de Espera Actualizado**\n\n"
                f"Nueva configuración: {time_text}\n\n"
                f"Las solicitudes de canal free ahora se aprobarán\n"
                f"después de este tiempo de espera."
            )
        else:
            await message.answer(f"❌ Error al actualizar: {result.get('error', 'Error desconocido')}")
            
    except Exception as e:
        await message.answer(f"Error: {str(e)}")
        await state.clear()

async def show_notifications_config(callback_query: CallbackQuery, session: AsyncSession):
    """Muestra configuración de notificaciones."""
    text = "🔔 **CONFIGURACIÓN DE NOTIFICACIONES**\n\n"
    text += "🔄 Esta funcionalidad está en desarrollo\n\n"
    text += "Próximas configuraciones:\n"
    text += "• Habilitar/deshabilitar tipos de alertas\n"
    text += "• Configurar horarios de reportes\n"
    text += "• Establecer umbrales de alerta\n"
    text += "• Configurar canales de notificación\n"
    text += "• Personalizar mensajes de alerta\n"
    
    keyboard = [
        [InlineKeyboardButton(text="⬅️ Volver", callback_data="admin:settings")]
    ]
    
    await callback_query.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )
    await callback_query.answer()

async def show_gamification_config(callback_query: CallbackQuery, session: AsyncSession):
    """Muestra configuración de gamificación."""
    text = "🎮 **CONFIGURACIÓN DE GAMIFICACIÓN**\n\n"
    text += "🔄 Esta funcionalidad está en desarrollo\n\n"
    text += "Próximas configuraciones:\n"
    text += "• Multiplicadores de puntos (besitos)\n"
    text += "• Configuración de misiones\n"
    text += "• Niveles y experiencia requerida\n"
    text += "• Premios y recompensas\n"
    text += "• Configuración de la tienda\n"
    
    keyboard = [
        [InlineKeyboardButton(text="⬅️ Volver", callback_data="admin:settings")]
    ]
    
    await callback_query.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )
    await callback_query.answer()

async def show_security_config(callback_query: CallbackQuery, session: AsyncSession):
    """Muestra configuración de seguridad."""
    text = "🔐 **CONFIGURACIÓN DE SEGURIDAD**\n\n"
    text += "🔄 Esta funcionalidad está en desarrollo\n\n"
    text += "Próximas configuraciones:\n"
    text += "• Lista de administradores autorizados\n"
    text += "• Configuración de rate limiting\n"
    text += "• Filtros de contenido automático\n"
    text += "• Configuración de baneos automáticos\n"
    text += "• Logs de auditoría y seguridad\n"
    
    keyboard = [
        [InlineKeyboardButton(text="⬅️ Volver", callback_data="admin:settings")]
    ]
    
    await callback_query.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )
    await callback_query.answer()

async def show_backup_config(callback_query: CallbackQuery, session: AsyncSession):
    """Muestra configuración de respaldo."""
    text = "💾 **CONFIGURACIÓN DE RESPALDO**\n\n"
    text += "🔄 Esta funcionalidad está en desarrollo\n\n"
    text += "Próximas configuraciones:\n"
    text += "• Respaldos automáticos de base de datos\n"
    text += "• Exportación programada de datos\n"
    text += "• Restauración de configuraciones\n"
    text += "• Sincronización con servicios en la nube\n"
    text += "• Programación de backups\n"
    
    keyboard = [
        [InlineKeyboardButton(text="⬅️ Volver", callback_data="admin:settings")]
    ]
    
    await callback_query.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )
    await callback_query.answer()

async def reset_configuration(callback_query: CallbackQuery, session: AsyncSession):
    """Reinicia la configuración a valores por defecto."""
    text = "🔄 **REINICIAR CONFIGURACIÓN**\n\n"
    text += "⚠️ **ADVERTENCIA**\n\n"
    text += "Esta acción restaurará toda la configuración\n"
    text += "a los valores por defecto:\n\n"
    text += "• Canal Free ID: No configurado\n"
    text += "• Tiempo de espera: 15 minutos\n"
    text += "• Todas las configuraciones personalizadas se perderán\n\n"
    text += "Esta acción NO se puede deshacer.\n\n"
    text += "¿Estás seguro de continuar?"
    
    keyboard = [
        [
            InlineKeyboardButton(text="✅ Sí, Reiniciar", callback_data="confirm_reset:yes"),
            InlineKeyboardButton(text="❌ Cancelar", callback_data="admin:settings")
        ]
    ]
    
    await callback_query.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )
    await callback_query.answer()

@configuration_router.callback_query(F.data == "confirm_reset:yes")
async def confirm_reset_configuration(callback_query: CallbackQuery, session: AsyncSession):
    """Confirma el reinicio de configuración."""
    try:
        event_bus = EventBus()
        admin_service = AdminService(event_bus)
        
        # Configuración por defecto
        default_config = {
            "free_channel_id": None,
            "wait_time_minutes": 15
        }
        
        result = await admin_service.update_bot_configuration(
            default_config,
            admin_id=callback_query.from_user.id
        )
        
        if result["success"]:
            await callback_query.answer("✅ Configuración reiniciada exitosamente")
            # Mostrar panel de configuración actualizado
            await show_configuration_panel(callback_query, session)
        else:
            await callback_query.answer(f"❌ Error: {result.get('error', 'Error desconocido')}")
            
    except Exception as e:
        await callback_query.answer(f"Error: {str(e)}")

async def save_configuration(callback_query: CallbackQuery, session: AsyncSession):
    """Guarda la configuración actual."""
    try:
        # En una implementación real, esto podría guardar a un archivo o hacer backup
        await callback_query.answer("✅ Configuración guardada (funcionalidad simulada)")
        
    except Exception as e:
        await callback_query.answer(f"Error: {str(e)}")