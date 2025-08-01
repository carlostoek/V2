# diana_admin_menu_system.py
"""
Sistema de Menú Administrativo Elegante para Diana Bot
¡Navegación fluida con edición de mensajes y auto-limpieza!
"""

import asyncio
from typing import Dict, List, Optional, Callable
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Message
from telegram.ext import ContextTypes, CallbackQueryHandler
from datetime import datetime, timedelta
import json

from src.utils.sexy_logger import log

class AdminMenuSystem:
    """
    Sistema de menús administrativos elegante con:
    - Edición de mensajes (no spam)
    - Auto-eliminación de notificaciones
    - Navegación fluida
    - Breadcrumbs y historial
    """
    
    def __init__(self, bot_application):
        self.app = bot_application
        self.active_menus: Dict[int, Dict] = {}  # user_id -> menu_data
        self.temp_messages: List[Dict] = []  # Mensajes temporales para eliminar
        
        # Configuración de auto-eliminación
        self.notification_delete_time = 8  # segundos
        self.success_delete_time = 5       # segundos
        self.error_delete_time = 10        # segundos
        
        self.setup_handlers()
        
        log.startup("Sistema de Menú Administrativo inicializado")
    
    def setup_handlers(self):
        """Configurar handlers para el sistema de menús"""
        self.app.add_handler(CallbackQueryHandler(
            self.handle_admin_callback, 
            pattern=r"^admin_"
        ))
        
        # Task para limpiar mensajes temporales
        asyncio.create_task(self.cleanup_temp_messages())
    
    # ============================================
    # MENÚ PRINCIPAL ADMINISTRATIVO
    # ============================================
    
    async def show_main_admin_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mostrar menú principal administrativo"""
        user_id = update.effective_user.id
        
        # Verificar permisos de admin
        if not await self.is_admin(user_id):
            await self.send_temp_message(
                update, "❌ No tienes permisos de administrador", 
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
🏆 Subastas Activas: {system_info['active_auctions']}

⏰ Última actualización: {datetime.now().strftime('%H:%M:%S')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Selecciona una categoría para administrar:
        """
        
        keyboard = [
            [
                InlineKeyboardButton("👥 Usuarios", callback_data="admin_users"),
                InlineKeyboardButton("📺 Canales", callback_data="admin_channels")
            ],
            [
                InlineKeyboardButton("🎮 Gamificación", callback_data="admin_gamification"),
                InlineKeyboardButton("📖 Narrativa", callback_data="admin_narrative")
            ],
            [
                InlineKeyboardButton("🏆 Subastas VIP", callback_data="admin_auctions"),
                InlineKeyboardButton("⚙️ Configuración", callback_data="admin_config")
            ],
            [
                InlineKeyboardButton("📊 Estadísticas", callback_data="admin_stats"),
                InlineKeyboardButton("🔔 Notificaciones", callback_data="admin_notifications")
            ],
            [
                InlineKeyboardButton("🔄 Actualizar", callback_data="admin_refresh"),
                InlineKeyboardButton("❌ Cerrar", callback_data="admin_close")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Editar mensaje existente o crear nuevo
        await self.edit_or_send_menu(
            update, context, menu_text, reply_markup, 
            menu_id="main_admin"
        )
        
        log.user_action(f"Panel administrativo accedido", user_id=user_id, action="admin_menu_open")
    
    # ============================================
    # GESTIÓN DE USUARIOS
    # ============================================
    
    async def show_users_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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
                InlineKeyboardButton("🔍 Buscar Usuario", callback_data="admin_users_search"),
                InlineKeyboardButton("👑 Gestionar VIP", callback_data="admin_users_vip")
            ],
            [
                InlineKeyboardButton("🎟️ Tokens VIP", callback_data="admin_users_tokens"),
                InlineKeyboardButton("📊 Estadísticas", callback_data="admin_users_stats")
            ],
            [
                InlineKeyboardButton("⚠️ Moderación", callback_data="admin_users_moderation"),
                InlineKeyboardButton("📤 Envío Masivo", callback_data="admin_users_broadcast")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="admin_main"),
                InlineKeyboardButton("🔄 Actualizar", callback_data="admin_users_refresh")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await self.edit_or_send_menu(
            update, context, menu_text, reply_markup,
            menu_id="users", breadcrumb="👥 Usuarios"
        )
    
    # ============================================
    # GESTIÓN DE CANALES
    # ============================================
    
    async def show_channels_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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
                InlineKeyboardButton("➕ Agregar Canal", callback_data="admin_channels_add"),
                InlineKeyboardButton("✏️ Editar Canal", callback_data="admin_channels_edit")
            ],
            [
                InlineKeyboardButton("🔗 Canales Gratuitos", callback_data="admin_channels_free"),
                InlineKeyboardButton("💎 Canales VIP", callback_data="admin_channels_vip")
            ],
            [
                InlineKeyboardButton("🔍 Monitoreo", callback_data="admin_channels_monitor"),
                InlineKeyboardButton("⚠️ Validaciones", callback_data="admin_channels_validate")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="admin_main"),
                InlineKeyboardButton("🔄 Actualizar", callback_data="admin_channels_refresh")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await self.edit_or_send_menu(
            update, context, menu_text, reply_markup,
            menu_id="channels", breadcrumb="📺 Canales"
        )
    
    # ============================================
    # GAMIFICACIÓN
    # ============================================
    
    async def show_gamification_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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
                InlineKeyboardButton("🎯 Misiones", callback_data="admin_game_missions"),
                InlineKeyboardButton("❓ Trivias", callback_data="admin_game_trivia")
            ],
            [
                InlineKeyboardButton("🎁 Regalos Diarios", callback_data="admin_game_gifts"),
                InlineKeyboardButton("🏪 Tienda", callback_data="admin_game_shop")
            ],
            [
                InlineKeyboardButton("💎 Besitos", callback_data="admin_game_points"),
                InlineKeyboardButton("🏆 Logros", callback_data="admin_game_achievements")
            ],
            [
                InlineKeyboardButton("📊 Reportes", callback_data="admin_game_reports"),
                InlineKeyboardButton("⚙️ Configurar", callback_data="admin_game_config")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="admin_main"),
                InlineKeyboardButton("🔄 Actualizar", callback_data="admin_game_refresh")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await self.edit_or_send_menu(
            update, context, menu_text, reply_markup,
            menu_id="gamification", breadcrumb="🎮 Gamificación"
        )
    
    # ============================================
    # NARRATIVA
    # ============================================
    
    async def show_narrative_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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
                InlineKeyboardButton("📄 Fragmentos", callback_data="admin_narrative_fragments"),
                InlineKeyboardButton("🗝️ Pistas", callback_data="admin_narrative_clues")
            ],
            [
                InlineKeyboardButton("🎭 Niveles Diana", callback_data="admin_narrative_levels"),
                InlineKeyboardButton("👑 Validaciones", callback_data="admin_narrative_validations")
            ],
            [
                InlineKeyboardButton("🎒 Mochilas", callback_data="admin_narrative_backpacks"),
                InlineKeyboardButton("📊 Progresión", callback_data="admin_narrative_progress")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="admin_main"),
                InlineKeyboardButton("🔄 Actualizar", callback_data="admin_narrative_refresh")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await self.edit_or_send_menu(
            update, context, menu_text, reply_markup,
            menu_id="narrative", breadcrumb="📖 Narrativa"
        )
    
    # ============================================
    # SUBASTAS VIP
    # ============================================
    
    async def show_auctions_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Menú de subastas VIP"""
        
        auction_stats = await self.get_auction_stats()
        
        menu_text = f"""
🏆 **GESTIÓN DE SUBASTAS VIP**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 **Estado de Subastas:**
• Subastas activas: {auction_stats['active_auctions']}
• Próximas a finalizar: {auction_stats['ending_soon']}
• Participantes únicos: {auction_stats['unique_bidders']}

💰 **Actividad Económica:**
• Besitos en juego: {auction_stats['total_bids']}
• Subasta más activa: {auction_stats['most_active_auction']}
• Promedio de ofertas: {auction_stats['average_bids']}

🏅 **Subastas Recientes:**
{auction_stats['recent_auctions_text']}
        """
        
        keyboard = [
            [
                InlineKeyboardButton("➕ Nueva Subasta", callback_data="admin_auctions_create"),
                InlineKeyboardButton("📝 Editar Subasta", callback_data="admin_auctions_edit")
            ],
            [
                InlineKeyboardButton("🔴 Subastas Activas", callback_data="admin_auctions_active"),
                InlineKeyboardButton("📋 Historial", callback_data="admin_auctions_history")
            ],
            [
                InlineKeyboardButton("🏆 Ganadores", callback_data="admin_auctions_winners"),
                InlineKeyboardButton("📊 Estadísticas", callback_data="admin_auctions_stats")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="admin_main"),
                InlineKeyboardButton("🔄 Actualizar", callback_data="admin_auctions_refresh")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await self.edit_or_send_menu(
            update, context, menu_text, reply_markup,
            menu_id="auctions", breadcrumb="🏆 Subastas VIP"
        )
    
    # ============================================
    # CONFIGURACIÓN
    # ============================================
    
    async def show_config_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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
                InlineKeyboardButton("🎮 Gamificación", callback_data="admin_config_game"),
                InlineKeyboardButton("📖 Narrativa", callback_data="admin_config_narrative")
            ],
            [
                InlineKeyboardButton("💎 Tokens VIP", callback_data="admin_config_vip"),
                InlineKeyboardButton("🔔 Notificaciones", callback_data="admin_config_notifications")
            ],
            [
                InlineKeyboardButton("🛡️ Seguridad", callback_data="admin_config_security"),
                InlineKeyboardButton("⚡ Performance", callback_data="admin_config_performance")
            ],
            [
                InlineKeyboardButton("💾 Backup", callback_data="admin_config_backup"),
                InlineKeyboardButton("🔄 Restart Bot", callback_data="admin_config_restart")
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="admin_main"),
                InlineKeyboardButton("🔄 Actualizar", callback_data="admin_config_refresh")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await self.edit_or_send_menu(
            update, context, menu_text, reply_markup,
            menu_id="config", breadcrumb="⚙️ Configuración"
        )
    
    # ============================================
    # HANDLER PRINCIPAL DE CALLBACKS
    # ============================================
    
    async def handle_admin_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler principal para todos los callbacks administrativos"""
        query = update.callback_query
        user_id = update.effective_user.id
        data = query.data
        
        await query.answer()  # Responder inmediatamente para evitar timeout
        
        # Verificar permisos
        if not await self.is_admin(user_id):
            await self.send_temp_message(
                update, "❌ No tienes permisos de administrador",
                delete_time=self.error_delete_time
            )
            return
        
        # Log de acción administrativa
        log.user_action(f"Admin callback: {data}", user_id=user_id, action="admin_callback")
        
        # Router de callbacks
        if data == "admin_main":
            await self.show_main_admin_menu(update, context)
        
        elif data == "admin_users":
            await self.show_users_menu(update, context)
        elif data == "admin_channels":
            await self.show_channels_menu(update, context)
        elif data == "admin_gamification":
            await self.show_gamification_menu(update, context)
        elif data == "admin_narrative":
            await self.show_narrative_menu(update, context)
        elif data == "admin_auctions":
            await self.show_auctions_menu(update, context)
        elif data == "admin_config":
            await self.show_config_menu(update, context)
        
        # Refresh callbacks
        elif data.endswith("_refresh"):
            await self.handle_refresh_callback(update, context, data)
        
        # Acciones específicas
        elif data == "admin_close":
            await self.close_admin_menu(update, context)
        
        else:
            # Delegar a handlers específicos
            await self.handle_specific_callback(update, context, data)
    
    async def handle_refresh_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
        """Manejar callbacks de refresh"""
        
        # Mostrar notificación de actualización
        await self.send_temp_message(
            update, "🔄 Actualizando información...",
            delete_time=2
        )
        
        # Determinar qué menú refrescar
        if data == "admin_refresh":
            await self.show_main_admin_menu(update, context)
        elif data == "admin_users_refresh":
            await self.show_users_menu(update, context)
        elif data == "admin_channels_refresh":
            await self.show_channels_menu(update, context)
        elif data == "admin_game_refresh":
            await self.show_gamification_menu(update, context)
        elif data == "admin_narrative_refresh":
    
