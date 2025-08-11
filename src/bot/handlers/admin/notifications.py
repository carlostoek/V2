"""Sistema de notificaciones y alertas para administradores."""

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from datetime import datetime, timedelta
import asyncio
import logging

from ...filters.role import IsAdminFilter
from src.modules.admin.service import AdminService, AdminActionEvent, VipStatusChangedEvent, UserStatusChangedEvent
from src.modules.user.service import UserService
from src.core.event_bus import EventBus, IEvent

notifications_router = Router()
logger = logging.getLogger(__name__)

class NotificationService:
    """Servicio para manejar notificaciones administrativas."""
    
    def __init__(self, event_bus: EventBus, bot: Bot):
        self.event_bus = event_bus
        self.bot = bot
        self.admin_users = set()  # Lista de IDs de administradores
        self.notification_settings = {
            "critical_alerts": True,
            "user_activity": True,
            "revenue_updates": True,
            "system_events": True,
            "subscription_alerts": True
        }
        
    async def setup(self):
        """Configura los listeners de eventos."""
        # Suscribirse a eventos importantes
        await self.event_bus.subscribe("admin_action", self.handle_admin_action)
        await self.event_bus.subscribe("vip_status_changed", self.handle_vip_status_change)
        await self.event_bus.subscribe("user_status_changed", self.handle_user_status_change)
        await self.event_bus.subscribe("token_generated", self.handle_token_generated)
        await self.event_bus.subscribe("token_redeemed", self.handle_token_redeemed)
        
        logger.info("NotificationService configurado exitosamente")
        
    def add_admin(self, user_id: int):
        """Agrega un administrador a la lista de notificaciones."""
        self.admin_users.add(user_id)
        
    def remove_admin(self, user_id: int):
        """Remueve un administrador de la lista de notificaciones."""
        self.admin_users.discard(user_id)
        
    async def send_alert_to_admins(self, message: str, alert_type: str = "info", keyboard: InlineKeyboardMarkup = None):
        """Envía una alerta a todos los administradores."""
        if not self.admin_users:
            return
            
        # Iconos por tipo de alerta
        icons = {
            "critical": "🚨",
            "warning": "⚠️",
            "info": "ℹ️",
            "success": "✅",
            "money": "💰",
            "user": "👤"
        }
        
        icon = icons.get(alert_type, "ℹ️")
        formatted_message = f"{icon} **ALERTA ADMINISTRATIVA**\n\n{message}\n\n🕐 {datetime.now().strftime('%H:%M:%S')}"
        
        # Enviar a todos los admins
        for admin_id in list(self.admin_users):  # Crear copia para evitar modificación durante iteración
            try:
                await self.bot.send_message(
                    admin_id,
                    formatted_message,
                    parse_mode="Markdown",
                    reply_markup=keyboard
                )
            except Exception as e:
                logger.warning(f"Error enviando notificación a admin {admin_id}: {e}")
                # Si el admin bloqueó el bot, removerlo
                if "bot was blocked" in str(e).lower():
                    self.remove_admin(admin_id)
                    
    async def handle_admin_action(self, event: AdminActionEvent):
        """Maneja eventos de acciones administrativas."""
        try:
            action_messages = {
                "user_banned": f"Usuario {event.target_id} fue baneado",
                "user_unbanned": f"Usuario {event.target_id} fue desbaneado", 
                "tariff_created": f"Nueva tarifa creada: {event.details.get('name', 'Sin nombre')}",
                "tariff_updated": f"Tarifa {event.target_id} actualizada",
                "tariff_deleted": f"Tarifa {event.target_id} eliminada",
                "token_generated": f"Token generado para tarifa {event.details.get('tariff_id')}",
                "bulk_tokens_generated": f"{event.details.get('quantity', 0)} tokens generados masivamente",
                "token_redeemed": f"Token canjeado por usuario {event.details.get('user_id')}",
                "user_vip_changed": f"Status VIP cambiado para usuario {event.target_id}",
                "config_updated": "Configuración del bot actualizada"
            }
            
            message = action_messages.get(event.action, f"Acción administrativa: {event.action}")
            
            # Determinar tipo de alerta
            alert_type = "info"
            if event.action in ["user_banned", "config_updated"]:
                alert_type = "warning"
            elif event.action in ["bulk_tokens_generated", "token_redeemed"]:
                alert_type = "money"
            elif event.action in ["tariff_created", "user_vip_changed"]:
                alert_type = "success"
                
            # No notificar todas las acciones para evitar spam
            if event.action in ["token_generated"]:  # Acciones muy frecuentes
                return
                
            await self.send_alert_to_admins(message, alert_type)
            
        except Exception as e:
            logger.error(f"Error manejando admin action: {e}")
            
    async def handle_vip_status_change(self, event: VipStatusChangedEvent):
        """Maneja cambios de status VIP."""
        try:
            if event.is_vip:
                message = f"✨ **NUEVO USUARIO VIP**\n\nUsuario: {event.user_id}\nCambiado por: Admin {event.changed_by}"
                if event.expires_at:
                    expires_str = event.expires_at.strftime('%d/%m/%Y')
                    message += f"\nExpira: {expires_str}"
                alert_type = "success"
            else:
                message = f"❌ **VIP REMOVIDO**\n\nUsuario: {event.user_id}\nCambiado por: Admin {event.changed_by}"
                alert_type = "warning"
                
            await self.send_alert_to_admins(message, alert_type)
            
        except Exception as e:
            logger.error(f"Error manejando VIP status change: {e}")
            
    async def handle_user_status_change(self, event: UserStatusChangedEvent):
        """Maneja cambios de status de usuarios."""
        try:
            if event.new_status == "banned":
                message = f"🚫 **USUARIO BANEADO**\n\nUsuario: {event.user_id}\nPor: Admin {event.changed_by}\nAnterior: {event.old_status}"
                alert_type = "critical"
            elif event.new_status == "active" and event.old_status == "banned":
                message = f"✅ **USUARIO DESBANEADO**\n\nUsuario: {event.user_id}\nPor: Admin {event.changed_by}"
                alert_type = "success"
            else:
                return  # No notificar otros cambios de status
                
            await self.send_alert_to_admins(message, alert_type)
            
        except Exception as e:
            logger.error(f"Error manejando user status change: {e}")
            
    async def handle_token_generated(self, event):
        """Maneja generación de tokens (solo para tokens importantes)."""
        # Solo notificar generaciones masivas
        pass
        
    async def handle_token_redeemed(self, event):
        """Maneja tokens canjeados."""
        try:
            message = f"💎 **TOKEN CANJEADO**\n\nUsuario: {event.user_id}\nTarifa: {event.details.get('tariff_name', 'Desconocida')}\nDuración: {event.details.get('duration_days', 0)} días"
            await self.send_alert_to_admins(message, "money")
            
        except Exception as e:
            logger.error(f"Error manejando token redeemed: {e}")
            
    async def send_daily_report(self):
        """Envía reporte diario a administradores."""
        try:
            event_bus = EventBus()
            admin_service = AdminService(event_bus)
            
            # Obtener estadísticas del día
            user_stats = await admin_service.get_user_statistics()
            revenue_stats = await admin_service.get_revenue_statistics()
            
            message = "📊 **REPORTE DIARIO**\n\n"
            message += f"👥 **Usuarios:**\n"
            message += f"• Nuevos hoy: {user_stats['today_new_users']}\n"
            message += f"• Total VIP: {user_stats['vip_users']}\n"
            message += f"• Total activos: {user_stats['active_users']}\n\n"
            
            message += f"💰 **Ingresos (mes actual):**\n"
            message += f"• Tokens generados: {revenue_stats['tokens_generated']}\n"
            message += f"• Tokens canjeados: {revenue_stats['tokens_redeemed']}\n"
            message += f"• Ingresos: ${revenue_stats['estimated_revenue']:.2f}\n\n"
            
            message += f"📈 **Tasa de conversión:** {revenue_stats['conversion_rate']:.1f}%"
            
            await self.send_alert_to_admins(message, "info")
            
        except Exception as e:
            logger.error(f"Error enviando reporte diario: {e}")
            
    async def check_expiring_subscriptions(self):
        """Verifica suscripciones próximas a expirar."""
        try:
            event_bus = EventBus()
            admin_service = AdminService(event_bus)
            
            # Usuarios que expiran en 1 día
            expiring_tomorrow = await admin_service.get_expiring_subscriptions(1)
            
            if expiring_tomorrow:
                message = f"⏰ **SUSCRIPCIONES POR EXPIRAR MAÑANA**\n\n"
                message += f"Total: {len(expiring_tomorrow)} usuarios\n\n"
                
                for user in expiring_tomorrow[:5]:  # Mostrar solo los primeros 5
                    username = user.get('username', 'Sin username')
                    message += f"• {user['first_name']} (@{username})\n"
                
                if len(expiring_tomorrow) > 5:
                    message += f"\n... y {len(expiring_tomorrow) - 5} más"
                    
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📋 Ver Lista Completa", callback_data="admin:users")]
                ])
                
                await self.send_alert_to_admins(message, "warning", keyboard)
                
        except Exception as e:
            logger.error(f"Error verificando suscripciones: {e}")
            
    async def check_system_health(self):
        """Verifica la salud del sistema."""
        try:
            event_bus = EventBus()
            admin_service = AdminService(event_bus)
            
            # Verificar métricas críticas
            user_stats = await admin_service.get_user_statistics()
            revenue_stats = await admin_service.get_revenue_statistics()
            
            alerts = []
            
            # Alerta si no hay usuarios nuevos en 24h
            if user_stats['today_new_users'] == 0:
                alerts.append("⚠️ Sin usuarios nuevos hoy")
                
            # Alerta si tasa de conversión es muy baja
            if revenue_stats['conversion_rate'] < 50:
                alerts.append(f"📉 Tasa de conversión baja: {revenue_stats['conversion_rate']:.1f}%")
                
            # Alerta si hay muchos usuarios baneados
            if user_stats['banned_users'] > user_stats['total_users'] * 0.1:
                alerts.append(f"🚫 Muchos usuarios baneados: {user_stats['banned_users']}")
                
            if alerts:
                message = "🏥 **ALERTA DE SALUD DEL SISTEMA**\n\n" + "\n".join(alerts)
                await self.send_alert_to_admins(message, "critical")
                
        except Exception as e:
            logger.error(f"Error verificando salud del sistema: {e}")

# Instancia global del servicio de notificaciones
notification_service: NotificationService = None

async def init_notification_service(bot: Bot):
    """Inicializa el servicio de notificaciones."""
    global notification_service
    event_bus = EventBus()
    notification_service = NotificationService(event_bus, bot)
    await notification_service.setup()
    
    # Iniciar tareas periódicas
    asyncio.create_task(periodic_checks())
    
async def periodic_checks():
    """Ejecuta verificaciones periódicas."""
    while True:
        try:
            # Verificar cada 6 horas
            await asyncio.sleep(6 * 3600)
            
            if notification_service:
                await notification_service.check_expiring_subscriptions()
                await notification_service.check_system_health()
                
        except Exception as e:
            logger.error(f"Error en verificaciones periódicas: {e}")
            await asyncio.sleep(300)  # Esperar 5 minutos antes de reintentar

@notifications_router.callback_query(F.data == "admin:notifications")
async def show_notification_panel(callback_query: CallbackQuery, session: AsyncSession):
    """Muestra el panel de notificaciones administrativas."""
    try:
        global notification_service
        
        # Agregar el admin a la lista si no está
        if notification_service:
            notification_service.add_admin(callback_query.from_user.id)
        
        text = "🔔 **CENTRO DE NOTIFICACIONES**\n\n"
        text += "Configuración de alertas y notificaciones administrativas\n\n"
        
        text += "✅ **Notificaciones Activas:**\n"
        text += "• Alertas críticas del sistema\n"
        text += "• Actividad de usuarios VIP\n"
        text += "• Actualizaciones de ingresos\n"
        text += "• Eventos del sistema\n"
        text += "• Alertas de suscripciones\n\n"
        
        text += "📊 **Reportes Automáticos:**\n"
        text += "• Reporte diario de estadísticas\n"
        text += "• Alertas de suscripciones por expirar\n"
        text += "• Verificación de salud del sistema\n\n"
        
        text += "🔧 **Configuración:**\n"
        text += "Puedes activar/desactivar tipos específicos de notificaciones"
        
        keyboard = [
            [InlineKeyboardButton(text="🔔 Configurar Alertas", callback_data="notif:config")],
            [InlineKeyboardButton(text="📊 Enviar Reporte Manual", callback_data="notif:manual_report")],
            [InlineKeyboardButton(text="🧪 Probar Notificación", callback_data="notif:test")],
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

@notifications_router.callback_query(F.data.startswith("notif:"))
async def handle_notification_actions(callback_query: CallbackQuery, session: AsyncSession):
    """Maneja acciones del panel de notificaciones."""
    try:
        global notification_service
        action = callback_query.data.split(":")[-1]
        
        if action == "config":
            text = "⚙️ **CONFIGURAR NOTIFICACIONES**\n\n"
            text += "🔄 Esta funcionalidad está en desarrollo\n\n"
            text += "Próximamente podrás configurar:\n"
            text += "• Tipos de alertas a recibir\n"
            text += "• Horarios de reportes\n"
            text += "• Umbrales de alertas críticas\n"
            text += "• Canales de notificación\n"
            
            keyboard = [
                [InlineKeyboardButton(text="⬅️ Volver", callback_data="admin:notifications")]
            ]
            
        elif action == "manual_report":
            if notification_service:
                await notification_service.send_daily_report()
                await callback_query.answer("📊 Reporte enviado exitosamente")
                return
            else:
                await callback_query.answer("❌ Servicio de notificaciones no disponible")
                return
                
        elif action == "test":
            if notification_service:
                await notification_service.send_alert_to_admins(
                    "🧪 **PRUEBA DE NOTIFICACIÓN**\n\nEste es un mensaje de prueba del sistema de alertas administrativas.",
                    "info"
                )
                await callback_query.answer("✅ Notificación de prueba enviada")
                return
            else:
                await callback_query.answer("❌ Servicio de notificaciones no disponible")
                return
        else:
            text = "❌ Acción no reconocida"
            keyboard = [
                [InlineKeyboardButton(text="⬅️ Volver", callback_data="admin:notifications")]
            ]
            
        await callback_query.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
        await callback_query.answer()
        
    except Exception as e:
        await callback_query.answer(f"Error: {str(e)}")