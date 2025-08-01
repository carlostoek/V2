# menu_system.py
"""
Sistema de Menú Administrativo Elegante para Diana Bot
¡Navegación fluida con edición de mensajes y auto-limpieza!
Adaptado para funcionar con aiogram v3
"""

import asyncio
from typing import Dict, List, Optional, Callable
from aiogram import types, F, Dispatcher
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime, timedelta
import json

from src.utils.sexy_logger import log
from src.modules.admin.service import AdminService
from src.modules.gamification.service import GamificationService
from src.modules.narrative.service import NarrativeService
from src.modules.channel.service import ChannelService

class AdminMenuSystem:
    """
    Sistema de menús administrativos elegante con:
    - Edición de mensajes (no spam)
    - Auto-eliminación de notificaciones
    - Navegación fluida
    - Breadcrumbs y historial
    """
    
    def __init__(self, admin_service: AdminService, gamification_service: GamificationService, 
                 narrative_service: NarrativeService, channel_service: ChannelService):
        self.admin_service = admin_service
        self.gamification_service = gamification_service
        self.narrative_service = narrative_service
        self.channel_service = channel_service
        
        self.active_menus: Dict[int, Dict] = {}  # user_id -> menu_data
        self.temp_messages: List[Dict] = []  # Mensajes temporales para eliminar
        
        # Configuración de auto-eliminación
        self.notification_delete_time = 8  # segundos
        self.success_delete_time = 5       # segundos
        self.error_delete_time = 10        # segundos
        
        log.startup("Sistema de Menú Administrativo inicializado")
    
    def register_handlers(self, dp: Dispatcher):
        """Registrar handlers para el sistema de menús"""
        dp.callback_query.register(
            self.handle_admin_callback, 
            F.data.startswith("admin_")
        )
        
        # Iniciar task para limpiar mensajes temporales
        asyncio.create_task(self.cleanup_temp_messages())
    
    # ============================================
    # MENÚ PRINCIPAL ADMINISTRATIVO
    # ============================================
    
    async def show_main_admin_menu(self, message_or_query):
        """Mostrar menú principal administrativo"""
        if isinstance(message_or_query, types.CallbackQuery):
            user_id = message_or_query.from_user.id
            message = message_or_query.message
        else:
            user_id = message_or_query.from_user.id
            message = message_or_query
        
        # Verificar permisos de admin
        if not await self.is_admin(user_id):
            await self.send_temp_message(
                message, "❌ No tienes permisos de administrador", 
                delete_time=self.error_delete_time
            )
            return
        
        # Header con información del sistema
        system_info = await self.get_system_info()
        
        menu_text = f"""
🎭 **DIANA BOT - PANEL ADMINISTRATIVO**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 **Estado del Sistema:**
👥 Usuarios Activos: {system_info['active_users']}
💎 Usuarios VIP: {system_info['vip_users']}
🎮 Misiones Activas: {system_info['active_missions']}
📺 Canales Monitoreados: {system_info['monitored_channels']}

⏰ Última actualización: {datetime.now().strftime('%H:%M:%S')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Selecciona una categoría para administrar:
        """
        
        keyboard = [
            [
                InlineKeyboardButton(text="👥 Usuarios", callback_data="admin_users"),
                InlineKeyboardButton(text="📺 Canales", callback_data="admin_channels")
            ],
            [
                InlineKeyboardButton(text="🎮 Gamificación", callback_data="admin_gamification"),
                InlineKeyboardButton(text="📖 Narrativa", callback_data="admin_narrative")
            ],
            [
                InlineKeyboardButton(text="⚙️ Configuración", callback_data="admin_config"),
                InlineKeyboardButton(text="📊 Estadísticas", callback_data="admin_stats")
            ],
            [
                InlineKeyboardButton(text="🔄 Actualizar", callback_data="admin_refresh"),
                InlineKeyboardButton(text="❌ Cerrar", callback_data="admin_close")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        
        # Editar mensaje existente o crear nuevo
        await self.edit_or_send_menu(
            message, menu_text, reply_markup, 
            menu_id="main_admin"
        )
        
        log.user_action(f"Panel administrativo accedido", user_id=user_id, action="admin_menu_open")
    
    # ============================================
    # GESTIÓN DE USUARIOS
    # ============================================
    
    async def show_users_menu(self, query: types.CallbackQuery):
        """Menú de gestión de usuarios"""
        
        user_stats = await self.get_user_stats()
        
        menu_text = f"""
👥 **GESTIÓN DE USUARIOS**
━━━━━━━━━━━━━━━━━━━━━━━━━

📈 **Estadísticas de Usuarios:**
• Total de usuarios: {user_stats['total_users']}
• Usuarios activos (7 días): {user_stats['active_7d']}
• Usuarios VIP activos: {user_stats['vip_active']}
• Nuevos registros (hoy): {user_stats['new_today']}

🏆 **Top 5 por Besitos:**
{user_stats['top_users_text']}

💎 **Tokens VIP:**
• Tokens activos: {user_stats['active_tokens']}
• Expirarán en 24h: {user_stats['expiring_tokens']}
        """
        
        keyboard = [
            [
                InlineKeyboardButton(text="🔍 Buscar Usuario", callback_data="admin_users_search"),
                InlineKeyboardButton(text="👑 Gestionar VIP", callback_data="admin_users_vip")
            ],
            [
                InlineKeyboardButton(text="🎟️ Tokens VIP", callback_data="admin_users_tokens"),
                InlineKeyboardButton(text="📊 Estadísticas", callback_data="admin_users_stats")
            ],
            [
                InlineKeyboardButton(text="⚠️ Moderación", callback_data="admin_users_moderation"),
                InlineKeyboardButton(text="📤 Envío Masivo", callback_data="admin_users_broadcast")
            ],
            [
                InlineKeyboardButton(text="🔙 Volver", callback_data="admin_main"),
                InlineKeyboardButton(text="🔄 Actualizar", callback_data="admin_users_refresh")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        
        await self.edit_or_send_menu(
            query.message, menu_text, reply_markup,
            menu_id="users", breadcrumb="👥 Usuarios"
        )
    
    # ============================================
    # GESTIÓN DE CANALES
    # ============================================
    
    async def show_channels_menu(self, query: types.CallbackQuery):
        """Menú de gestión de canales"""
        
        channels_info = await self.get_channels_info()
        
        menu_text = f"""
📺 **GESTIÓN DE CANALES**
━━━━━━━━━━━━━━━━━━━━━━━━━

📊 **Estado de Canales:**
• Canales gratuitos: {channels_info['free_channels']}
• Canales VIP: {channels_info['vip_channels']}
• Total monitoreados: {channels_info['total_monitored']}

🔗 **Canales Activos:**
{channels_info['channels_list']}

⚡ **Actividad Reciente:**
• Nuevas uniones (24h): {channels_info['new_joins_24h']}
• Validaciones pendientes: {channels_info['pending_validations']}
        """
        
        keyboard = [
            [
                InlineKeyboardButton(text="➕ Agregar Canal", callback_data="admin_channels_add"),
                InlineKeyboardButton(text="✏️ Editar Canal", callback_data="admin_channels_edit")
            ],
            [
                InlineKeyboardButton(text="🔗 Canales Gratuitos", callback_data="admin_channels_free"),
                InlineKeyboardButton(text="💎 Canales VIP", callback_data="admin_channels_vip")
            ],
            [
                InlineKeyboardButton(text="🔍 Monitoreo", callback_data="admin_channels_monitor"),
                InlineKeyboardButton(text="⚠️ Validaciones", callback_data="admin_channels_validate")
            ],
            [
                InlineKeyboardButton(text="🔙 Volver", callback_data="admin_main"),
                InlineKeyboardButton(text="🔄 Actualizar", callback_data="admin_channels_refresh")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        
        await self.edit_or_send_menu(
            query.message, menu_text, reply_markup,
            menu_id="channels", breadcrumb="📺 Canales"
        )
    
    # ============================================
    # GAMIFICACIÓN
    # ============================================
    
    async def show_gamification_menu(self, query: types.CallbackQuery):
        """Menú de gamificación"""
        
        game_stats = await self.get_gamification_stats()
        
        menu_text = f"""
🎮 **GESTIÓN DE GAMIFICACIÓN**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 **Estadísticas Generales:**
• Besitos distribuidos hoy: {game_stats['points_today']}
• Misiones completadas (24h): {game_stats['missions_completed_24h']}
• Trivias respondidas: {game_stats['trivia_responses']}
• Regalos reclamados: {game_stats['gifts_claimed']}

🎯 **Misiones Activas:**
{game_stats['active_missions_text']}

🏆 **Engagement:**
• Usuarios activos en juegos: {game_stats['active_gamers']}
• Tasa de completado de misiones: {game_stats['mission_completion_rate']}%
        """
        
        keyboard = [
            [
                InlineKeyboardButton(text="🎯 Misiones", callback_data="admin_game_missions"),
                InlineKeyboardButton(text="❓ Trivias", callback_data="admin_game_trivia")
            ],
            [
                InlineKeyboardButton(text="🎁 Regalos Diarios", callback_data="admin_game_gifts"),
                InlineKeyboardButton(text="🏪 Tienda", callback_data="admin_game_shop")
            ],
            [
                InlineKeyboardButton(text="💎 Besitos", callback_data="admin_game_points"),
                InlineKeyboardButton(text="🏆 Logros", callback_data="admin_game_achievements")
            ],
            [
                InlineKeyboardButton(text="📊 Reportes", callback_data="admin_game_reports"),
                InlineKeyboardButton(text="⚙️ Configurar", callback_data="admin_game_config")
            ],
            [
                InlineKeyboardButton(text="🔙 Volver", callback_data="admin_main"),
                InlineKeyboardButton(text="🔄 Actualizar", callback_data="admin_game_refresh")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        
        await self.edit_or_send_menu(
            query.message, menu_text, reply_markup,
            menu_id="gamification", breadcrumb="🎮 Gamificación"
        )
    
    # ============================================
    # NARRATIVA
    # ============================================
    
    async def show_narrative_menu(self, query: types.CallbackQuery):
        """Menú de gestión narrativa"""
        
        narrative_stats = await self.get_narrative_stats()
        
        menu_text = f"""
📖 **GESTIÓN NARRATIVA**
━━━━━━━━━━━━━━━━━━━━━━━━━

📚 **Estado de la Narrativa:**
• Fragmentos totales: {narrative_stats['total_fragments']}
• Pistas disponibles: {narrative_stats['total_clues']}
• Usuarios en progreso: {narrative_stats['users_in_progress']}

🎭 **Progresión Diana:**
• Nivel 1 (Los Kinkys): {narrative_stats['level_1_users']} usuarios
• Nivel 4 (El Diván): {narrative_stats['level_4_users']} usuarios
• Círculo Íntimo: {narrative_stats['inner_circle_users']} usuarios

📊 **Engagement Narrativo:**
• Fragmentos completados (24h): {narrative_stats['fragments_completed_24h']}
• Pistas combinadas: {narrative_stats['clues_combined']}
• Tasa de progresión: {narrative_stats['progression_rate']}%
        """
        
        keyboard = [
            [
                InlineKeyboardButton(text="📄 Fragmentos", callback_data="admin_narrative_fragments"),
                InlineKeyboardButton(text="🗝️ Pistas", callback_data="admin_narrative_clues")
            ],
            [
                InlineKeyboardButton(text="🎭 Niveles Diana", callback_data="admin_narrative_levels"),
                InlineKeyboardButton(text="👑 Validaciones", callback_data="admin_narrative_validations")
            ],
            [
                InlineKeyboardButton(text="🎒 Mochilas", callback_data="admin_narrative_backpacks"),
                InlineKeyboardButton(text="📊 Progresión", callback_data="admin_narrative_progress")
            ],
            [
                InlineKeyboardButton(text="🔙 Volver", callback_data="admin_main"),
                InlineKeyboardButton(text="🔄 Actualizar", callback_data="admin_narrative_refresh")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        
        await self.edit_or_send_menu(
            query.message, menu_text, reply_markup,
            menu_id="narrative", breadcrumb="📖 Narrativa"
        )
    
    # ============================================
    # CONFIGURACIÓN
    # ============================================
    
    async def show_config_menu(self, query: types.CallbackQuery):
        """Menú de configuración del sistema"""
        
        config_info = await self.get_config_info()
        
        menu_text = f"""
⚙️ **CONFIGURACIÓN DEL SISTEMA**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔧 **Configuraciones Activas:**
• Modo de operación: {config_info['operation_mode']}
• Auto-limpieza de mensajes: {config_info['auto_cleanup']}
• Validaciones automáticas: {config_info['auto_validations']}
• Notificaciones push: {config_info['push_notifications']}

📋 **Parámetros Principales:**
• Besitos por reacción: {config_info['points_per_reaction']}
• Límite diario de regalos: {config_info['daily_gift_limit']}
• Duración token VIP: {config_info['vip_token_duration']} días
• Tiempo de cache: {config_info['cache_duration']} min

⚡ **Sistema:**
• Versión del bot: {config_info['bot_version']}
• Última actualización: {config_info['last_update']}
        """
        
        keyboard = [
            [
                InlineKeyboardButton(text="🎮 Gamificación", callback_data="admin_config_game"),
                InlineKeyboardButton(text="📖 Narrativa", callback_data="admin_config_narrative")
            ],
            [
                InlineKeyboardButton(text="💎 Tokens VIP", callback_data="admin_config_vip"),
                InlineKeyboardButton(text="🔔 Notificaciones", callback_data="admin_config_notifications")
            ],
            [
                InlineKeyboardButton(text="🛡️ Seguridad", callback_data="admin_config_security"),
                InlineKeyboardButton(text="⚡ Performance", callback_data="admin_config_performance")
            ],
            [
                InlineKeyboardButton(text="💾 Backup", callback_data="admin_config_backup"),
                InlineKeyboardButton(text="🔄 Restart Bot", callback_data="admin_config_restart")
            ],
            [
                InlineKeyboardButton(text="🔙 Volver", callback_data="admin_main"),
                InlineKeyboardButton(text="🔄 Actualizar", callback_data="admin_config_refresh")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        
        await self.edit_or_send_menu(
            query.message, menu_text, reply_markup,
            menu_id="config", breadcrumb="⚙️ Configuración"
        )
    
    # ============================================
    # HANDLER PRINCIPAL DE CALLBACKS
    # ============================================
    async def handle_admin_callback(self, query: types.CallbackQuery):
        """Handler principal para todos los callbacks administrativos"""
        user_id = query.from_user.id
        data = query.data
        
        await query.answer()  # Responder inmediatamente para evitar timeout
        
        # Verificar permisos
        if not await self.is_admin(user_id):
            await self.send_temp_message(
                query.message, "❌ No tienes permisos de administrador",
                delete_time=self.error_delete_time
            )
            return
        
        # Log de acción administrativa
        log.user_action(f"Admin callback: {data}", user_id=user_id, action="admin_callback")
        
        # Router de callbacks
        if data == "admin_main":
            await self.show_main_admin_menu(query)
        
        elif data == "admin_users":
            await self.show_users_menu(query)
        elif data == "admin_channels":
            await self.show_channels_menu(query)
        elif data == "admin_gamification":
            await self.show_gamification_menu(query)
        elif data == "admin_narrative":
            await self.show_narrative_menu(query)
        elif data == "admin_config":
            await self.show_config_menu(query)
        
        # Refresh callbacks
        elif data.endswith("_refresh"):
            await self.handle_refresh_callback(query, data)
        
        # Acciones específicas
        elif data == "admin_close":
            await self.close_admin_menu(query)
        
        else:
            # Delegar a handlers específicos
            await self.handle_specific_callback(query, data)
    
    async def handle_refresh_callback(self, query: types.CallbackQuery, data: str):
        """Manejar callbacks de refresh"""
        
        # Mostrar notificación de actualización
        await self.send_temp_message(
            query.message, "🔄 Actualizando información...",
            delete_time=2
        )
        
        # Determinar qué menú refrescar
        if data == "admin_refresh":
            await self.show_main_admin_menu(query)
        elif data == "admin_users_refresh":
            await self.show_users_menu(query)
        elif data == "admin_channels_refresh":
            await self.show_channels_menu(query)
        elif data == "admin_game_refresh":
            await self.show_gamification_menu(query)
        elif data == "admin_narrative_refresh":
            await self.show_narrative_menu(query)
        elif data == "admin_config_refresh":
            await self.show_config_menu(query)
    
    # ============================================
    # UTILIDADES AUXILIARES
    # ============================================
    
    async def edit_or_send_menu(self, message: types.Message, text: str, 
                               reply_markup: InlineKeyboardMarkup, menu_id: str = None, 
                               breadcrumb: str = None):
        """Editar mensaje existente o enviar nuevo"""
        try:
            await message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        except Exception as e:
            # Si no se puede editar, enviar nuevo mensaje
            log.error(f"No se pudo editar mensaje: {e}")
            await message.answer(text, reply_markup=reply_markup, parse_mode="Markdown")
    
    async def send_temp_message(self, message: types.Message, text: str, delete_time: int = 5):
        """Enviar mensaje temporal que se auto-elimina"""
        temp_msg = await message.answer(text)
        
        # Agregar a lista de mensajes temporales
        self.temp_messages.append({
            'message': temp_msg,
            'delete_at': datetime.now() + timedelta(seconds=delete_time)
        })
    
    async def cleanup_temp_messages(self):
        """Limpiar mensajes temporales vencidos"""
        while True:
            try:
                current_time = datetime.now()
                messages_to_remove = []
                
                for i, temp_msg in enumerate(self.temp_messages):
                    if current_time >= temp_msg['delete_at']:
                        try:
                            await temp_msg['message'].delete()
                            messages_to_remove.append(i)
                        except Exception as e:
                            log.error(f"Error eliminando mensaje temporal: {e}")
                            messages_to_remove.append(i)
                
                # Remover mensajes procesados de la lista
                for i in reversed(messages_to_remove):
                    self.temp_messages.pop(i)
                
                await asyncio.sleep(10)  # Revisar cada 10 segundos
                
            except Exception as e:
                log.error(f"Error en cleanup_temp_messages: {e}")
                await asyncio.sleep(30)  # Esperar más tiempo si hay error
    
    async def close_admin_menu(self, query: types.CallbackQuery):
        """Cerrar menú administrativo"""
        try:
            await query.message.delete()
        except Exception as e:
            log.error(f"Error cerrando menú admin: {e}")
    
    async def handle_specific_callback(self, query: types.CallbackQuery, data: str):
        """Manejar callbacks específicos no implementados aún"""
        await query.answer("🚧 Funcionalidad en desarrollo", show_alert=True)
    
    # ============================================
    # MÉTODOS DE INFORMACIÓN (PLACEHOLDERS)
    # ============================================
    
    async def is_admin(self, user_id: int) -> bool:
        """Verificar si el usuario es administrador"""
        # TODO: Implementar verificación real de admin basada en roles/configuración
        # Por ahora permitir acceso a ciertos user_ids específicos o todos para testing
        admin_users = [123456789]  # Lista de IDs de administradores
        return user_id in admin_users or True  # True por ahora para testing
    
    async def get_system_info(self) -> Dict:
        """Obtener información del sistema"""
        try:
            # Get basic system info using available services
            active_users = 0
            vip_users = 0
            active_missions = 0
            monitored_channels = 0
            
            # Try to get real data from services if available
            if self.gamification_service:
                try:
                    # Get basic gamification stats - these methods might not exist yet
                    active_missions = getattr(self.gamification_service, 'get_active_missions_count', lambda: 0)()
                except:
                    active_missions = 0
            
            if self.channel_service:
                try:
                    monitored_channels = len(getattr(self.channel_service, 'channels', {}))
                except:
                    monitored_channels = 0
            
            return {
                'active_users': active_users or 42,  # Fallback to mock data
                'vip_users': vip_users or 8,
                'active_missions': active_missions or 15,
                'monitored_channels': monitored_channels or 3,
            }
        except Exception as e:
            log.error(f"Error obteniendo información del sistema: {e}")
            # Return mock data as fallback
            return {
                'active_users': 42,
                'vip_users': 8,
                'active_missions': 15,
                'monitored_channels': 3,
            }
    
    async def get_user_stats(self) -> Dict:
        """Obtener estadísticas de usuarios"""
        try:
            # Try to get real stats, fallback to mock data
            total_users = 125
            active_7d = 89
            vip_active = 12
            new_today = 5
            active_tokens = 15
            expiring_tokens = 3
            
            # Try to get real token stats from admin service
            if self.admin_service:
                try:
                    # These methods might not exist yet
                    all_tariffs = await self.admin_service.get_all_tariffs()
                    active_tokens = len(all_tariffs) * 5  # Mock calculation
                except:
                    pass
            
            return {
                'total_users': total_users,
                'active_7d': active_7d,
                'vip_active': vip_active,
                'new_today': new_today,
                'top_users_text': "1. @user1 - 2,450 besitos\n2. @user2 - 1,890 besitos\n3. @user3 - 1,567 besitos",
                'active_tokens': active_tokens,
                'expiring_tokens': expiring_tokens
            }
        except Exception as e:
            log.error(f"Error obteniendo estadísticas de usuarios: {e}")
            return {
                'total_users': 125,
                'active_7d': 89,
                'vip_active': 12,
                'new_today': 5,
                'top_users_text': "1. @user1 - 2,450 besitos\n2. @user2 - 1,890 besitos\n3. @user3 - 1,567 besitos",
                'active_tokens': 15,
                'expiring_tokens': 3
            }
    
    async def get_channels_info(self) -> Dict:
        """Obtener información de canales"""
        try:
            free_channels = 0
            vip_channels = 0
            total_monitored = 0
            channels_list = "No hay canales configurados"
            
            if self.channel_service:
                try:
                    channels = getattr(self.channel_service, 'channels', {})
                    total_monitored = len(channels)
                    
                    # Count by type
                    for channel_data in channels.values():
                        if channel_data.get('type') == 'free':
                            free_channels += 1
                        elif channel_data.get('type') == 'vip':
                            vip_channels += 1
                    
                    # Build channels list
                    if channels:
                        channel_names = []
                        for channel_data in channels.values():
                            emoji = "🆓" if channel_data.get('type') == 'free' else "💎"
                            channel_names.append(f"{emoji} {channel_data.get('name', 'Canal sin nombre')}")
                        channels_list = "\n".join(channel_names)
                        
                except Exception as e:
                    log.error(f"Error accediendo a datos de canales: {e}")
            
            return {
                'free_channels': free_channels or 2,
                'vip_channels': vip_channels or 3,
                'total_monitored': total_monitored or 5,
                'channels_list': channels_list if channels_list != "No hay canales configurados" else "🆓 Canal Gratuito\n💎 VIP Premium\n💎 VIP Gold",
                'new_joins_24h': 18,
                'pending_validations': 4
            }
        except Exception as e:
            log.error(f"Error obteniendo información de canales: {e}")
            return {
                'free_channels': 2,
                'vip_channels': 3,
                'total_monitored': 5,
                'channels_list': "🆓 Canal Gratuito\n💎 VIP Premium\n💎 VIP Gold",
                'new_joins_24h': 18,
                'pending_validations': 4
            }
    
    async def get_gamification_stats(self) -> Dict:
        """Obtener estadísticas de gamificación"""
        # TODO: Implementar con GamificationService real
        return {
            'points_today': 1250,
            'missions_completed_24h': 34,
            'trivia_responses': 89,
            'gifts_claimed': 67,
            'active_missions_text': "• Interactuar 10 veces (8/10)\n• Completar trivia (5/5)\n• Enviar foto del día (3/3)",
            'active_gamers': 78,
            'mission_completion_rate': 85
        }
    
    async def get_narrative_stats(self) -> Dict:
        """Obtener estadísticas narrativas"""
        # TODO: Implementar con NarrativeService real
        return {
            'total_fragments': 156,
            'total_clues': 89,
            'users_in_progress': 45,
            'level_1_users': 67,
            'level_4_users': 23,
            'inner_circle_users': 8,
            'fragments_completed_24h': 28,
            'clues_combined': 15,
            'progression_rate': 76
        }
    
    async def get_config_info(self) -> Dict:
        """Obtener información de configuración"""
        try:
            # Get basic config info
            return {
                'operation_mode': 'Desarrollo',  # Can be determined from environment
                'auto_cleanup': 'Activado' if self.temp_messages else 'Desactivado',
                'auto_validations': 'Activado',
                'push_notifications': 'Activado',
                'points_per_reaction': 5,
                'daily_gift_limit': 3,
                'vip_token_duration': 30,
                'cache_duration': 15,
                'bot_version': '2.0.0',
                'last_update': datetime.now().strftime('%Y-%m-%d')
            }
        except Exception as e:
            log.error(f"Error obteniendo información de configuración: {e}")
            return {
                'operation_mode': 'Desarrollo',
                'auto_cleanup': 'Activado',
                'auto_validations': 'Activado',
                'push_notifications': 'Activado',
                'points_per_reaction': 5,
                'daily_gift_limit': 3,
                'vip_token_duration': 30,
                'cache_duration': 15,
                'bot_version': '2.0.0',
                'last_update': '2025-08-01'
            }