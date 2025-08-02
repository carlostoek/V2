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
    # MENÚ PRINCIPAL DE USUARIO
    # ============================================
    
    async def show_main_user_menu(self, message_or_query, user_data=None):
        """Mostrar menú principal para usuarios"""
        if isinstance(message_or_query, types.CallbackQuery):
            user_id = message_or_query.from_user.id
            message = message_or_query.message
        else:
            user_id = message_or_query.from_user.id
            message = message_or_query
        
        # Obtener datos del usuario
        if not user_data:
            user_data = await self.get_user_data(user_id)
        
        # Mensaje de bienvenida dinámico con reacción de Diana
        diana_reaction = await self.get_diana_reaction(user_data)
        
        menu_text = f"""
🎭 **DIANA BOT - MENÚ PRINCIPAL**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{diana_reaction}

📊 **Tu Progreso:**
💰 Besitos: {user_data['points']:,}
🎯 Nivel: {user_data['level']} ({user_data['experience']}/100 XP)
🔥 Racha: {user_data['streak']} días
📖 Historia: {user_data['narrative_progress']}%

{await self.get_progress_bars(user_data)}

🎁 **Estado VIP:** {user_data['vip_status']}
⏰ Última conexión: {user_data['last_seen']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        # Teclado contextual basado en el estado del usuario
        keyboard = await self.build_user_menu_keyboard(user_data)
        
        # Editar mensaje existente o crear nuevo
        await self.edit_or_send_menu(
            message, menu_text, keyboard, 
            menu_id="main_user"
        )
        
        log.user_action(f"Menú principal accedido", user_id=user_id, action="user_menu_open")
    
    # ============================================
    # DASHBOARD DE PROGRESO PERSONAL
    # ============================================
    
    async def show_user_dashboard(self, query: types.CallbackQuery):
        """Dashboard completo del progreso personal"""
        user_id = query.from_user.id
        user_data = await self.get_user_data(user_id)
        achievements = await self.get_user_achievements(user_id)
        
        menu_text = f"""
📊 **DASHBOARD PERSONAL - {user_data['name']}**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 **Progreso Narrativo:**
📖 Historia completada: {user_data['narrative_progress']}%
🧩 Pistas en mochila: {user_data['clues_count']}
🔗 Combinaciones realizadas: {user_data['combinations_made']}
🎭 Nivel Diana actual: {user_data['diana_level']}

🎮 **Estadísticas de Juego:**
💰 Total besitos ganados: {user_data['total_points_earned']:,}
🎯 Misiones completadas: {user_data['missions_completed']}
❓ Trivias respondidas: {user_data['trivia_answered']}
🏆 Tasa de acierto: {user_data['success_rate']}%

📈 **Actividad Reciente:**
{await self.get_recent_activity(user_id)}

🏆 **Logros Recientes:**
{achievements['recent_text']}

📅 **Próximos Objetivos:**
{await self.get_next_objectives(user_data)}
        """
        
        keyboard = [
            [
                InlineKeyboardButton(text="🎯 Misiones", callback_data="user_missions"),
                InlineKeyboardButton(text="🎒 Mochila", callback_data="user_backpack")
            ],
            [
                InlineKeyboardButton(text="🏆 Logros", callback_data="user_achievements"),
                InlineKeyboardButton(text="📊 Estadísticas", callback_data="user_stats")
            ],
            [
                InlineKeyboardButton(text="🔙 Volver", callback_data="user_main"),
                InlineKeyboardButton(text="🔄 Actualizar", callback_data="refresh_dashboard")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        
        await self.edit_or_send_menu(query.message, menu_text, reply_markup)
    
    # ============================================
    # GESTIÓN DE USUARIO - PERFIL
    # ============================================
    
    async def show_user_profile(self, query: types.CallbackQuery):
        """Perfil detallado del usuario con opciones de personalización"""
        user_id = query.from_user.id
        profile_data = await self.get_detailed_profile(user_id)
        
        menu_text = f"""
👤 **PERFIL DE USUARIO**
━━━━━━━━━━━━━━━━━━━━━━━━━━

🆔 **Información Básica:**
• Nombre: {profile_data['display_name']}
• Username: @{profile_data['username']}
• ID: {profile_data['user_id']}
• Registro: {profile_data['join_date']}

📊 **Estadísticas:**
• Nivel: {profile_data['level']} ({profile_data['rank']})
• Experiencia: {profile_data['experience']}/100 XP
• Besitos totales: {profile_data['total_points']:,}
• Tiempo en bot: {profile_data['total_time']}

🎭 **Estado Narrativo:**
• Nivel Diana: {profile_data['diana_level']}
• Fragmentos completados: {profile_data['fragments_completed']}
• Pistas encontradas: {profile_data['clues_found']}

👑 **Estado VIP:**
{profile_data['vip_details']}

⚙️ **Configuración:**
• Notificaciones: {profile_data['notifications_enabled']}
• Horario preferido: {profile_data['preferred_time']}
• Dificultad: {profile_data['difficulty_level']}
        """
        
        keyboard = [
            [
                InlineKeyboardButton(text="✏️ Editar Perfil", callback_data="edit_profile"),
                InlineKeyboardButton(text="⚙️ Configuración", callback_data="user_settings")
            ],
            [
                InlineKeyboardButton(text="🏆 Ver Logros", callback_data="profile_achievements"),
                InlineKeyboardButton(text="📈 Estadísticas", callback_data="profile_stats")
            ],
            [
                InlineKeyboardButton(text="🔙 Volver", callback_data="user_main"),
                InlineKeyboardButton(text="📤 Compartir", callback_data="share_profile")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        
        await self.edit_or_send_menu(query.message, menu_text, reply_markup)
    
    # ============================================
    # MOCHILA DE PISTAS (LOREPIECES)
    # ============================================
    
    async def show_user_backpack(self, query: types.CallbackQuery):
        """Mochila con pistas narrativas y opciones de combinación"""
        user_id = query.from_user.id
        backpack_data = await self.get_backpack_data(user_id)
        
        menu_text = f"""
🎒 **TU MOCHILA DE PISTAS**
━━━━━━━━━━━━━━━━━━━━━━━━━━

🧩 **Pistas Disponibles ({backpack_data['total_clues']}):**
{backpack_data['clues_list']}

🔗 **Combinaciones Posibles:**
{backpack_data['available_combinations']}

📚 **Progreso Narrativo:**
• Fragmentos desbloqueados: {backpack_data['unlocked_fragments']}
• Siguiente objetivo: {backpack_data['next_goal']}

💡 **Pista de Diana:**
"{backpack_data['diana_hint']}"

⚡ **Acciones Rápidas:**
{backpack_data['quick_actions']}
        """
        
        keyboard = []
        
        # Botones dinámicos para combinaciones disponibles
        if backpack_data['combinations']:
            for combo in backpack_data['combinations']:
                keyboard.append([
                    InlineKeyboardButton(
                        text=f"🔗 {combo['name']}", 
                        callback_data=f"combine_{combo['id']}"
                    )
                ])
        
        # Botones de navegación
        keyboard.extend([
            [
                InlineKeyboardButton(text="🔍 Explorar", callback_data="explore_clues"),
                InlineKeyboardButton(text="📖 Leer Fragmento", callback_data="read_fragment")
            ],
            [
                InlineKeyboardButton(text="🎁 Usar Pista", callback_data="use_clue"),
                InlineKeyboardButton(text="📊 Ver Progreso", callback_data="narrative_progress")
            ],
            [
                InlineKeyboardButton(text="🔙 Volver", callback_data="user_main"),
                InlineKeyboardButton(text="🔄 Actualizar", callback_data="refresh_backpack")
            ]
        ])
        
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        await self.edit_or_send_menu(query.message, menu_text, reply_markup)
    
    # ============================================
    # MISIONES Y DESAFÍOS
    # ============================================
    
    async def show_user_missions(self, query: types.CallbackQuery):
        """Menú de misiones con progreso y recompensas"""
        user_id = query.from_user.id
        missions_data = await self.get_user_missions_data(user_id)
        
        menu_text = f"""
🎯 **TUS MISIONES ACTIVAS**
━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 **Estado General:**
• Misiones activas: {missions_data['active_count']}
• Completadas hoy: {missions_data['completed_today']}
• Puntos ganados: {missions_data['points_earned']} besitos

🎮 **Misiones Diarias:**
{missions_data['daily_missions']}

🏆 **Misiones Semanales:**
{missions_data['weekly_missions']}

✨ **Misiones Especiales:**
{missions_data['special_missions']}

🎁 **Recompensas Disponibles:**
{missions_data['available_rewards']}
        """
        
        keyboard = []
        
        # Botones dinámicos para misiones
        for mission in missions_data['actionable_missions']:
            keyboard.append([
                InlineKeyboardButton(
                    text=f"{mission['icon']} {mission['name']}", 
                    callback_data=f"mission_{mission['id']}"
                )
            ])
        
        # Botones de navegación
        keyboard.extend([
            [
                InlineKeyboardButton(text="🎁 Reclamar Todo", callback_data="claim_all_rewards"),
                InlineKeyboardButton(text="📊 Ver Progreso", callback_data="missions_progress")
            ],
            [
                InlineKeyboardButton(text="🔙 Volver", callback_data="user_main"),
                InlineKeyboardButton(text="🔄 Actualizar", callback_data="refresh_missions")
            ]
        ])
        
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        await self.edit_or_send_menu(query.message, menu_text, reply_markup)
    
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
        elif data == "user_main":
            await self.show_main_user_menu(query)
        
        # Callbacks de usuario
        elif data == "user_dashboard":
            await self.show_user_dashboard(query)
        elif data == "user_profile":
            await self.show_user_profile(query)
        elif data == "user_backpack":
            await self.show_user_backpack(query)
        elif data == "user_missions":
            await self.show_user_missions(query)
        elif data == "daily_gift":
            await self.handle_daily_gift(query)
        elif data == "user_games":
            await self.show_user_games(query)
        elif data == "user_shop":
            await self.show_user_shop(query)
        
        # Callbacks de admin
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
        """Manejar callbacks específicos de funcionalidades administrativas"""
        user_id = query.from_user.id
        
        # ============ GESTIÓN DE USUARIOS ============
        if data == "admin_users_search":
            await self.show_user_search_menu(query)
        elif data == "admin_users_vip":
            await self.show_vip_management_menu(query)
        elif data == "admin_users_tokens":
            await self.show_token_management_menu(query)
        elif data == "admin_users_stats":
            await self.show_user_statistics(query)
        elif data == "admin_users_moderation":
            await self.show_moderation_menu(query)
        elif data == "admin_users_broadcast":
            await self.show_broadcast_menu(query)
        
        # ============ GESTIÓN DE CANALES ============
        elif data == "admin_channels_add":
            await self.show_add_channel_menu(query)
        elif data == "admin_channels_edit":
            await self.show_edit_channels_menu(query)
        elif data == "admin_channels_free":
            await self.show_free_channels_menu(query)
        elif data == "admin_channels_vip":
            await self.show_vip_channels_menu(query)
        elif data == "admin_channels_monitor":
            await self.show_channel_monitoring(query)
        elif data == "admin_channels_validate":
            await self.show_channel_validations(query)
        
        # ============ GAMIFICACIÓN ============
        elif data == "admin_game_missions":
            await self.show_missions_management(query)
        elif data == "admin_game_trivia":
            await self.show_trivia_management(query)
        elif data == "admin_game_gifts":
            await self.show_gifts_management(query)
        elif data == "admin_game_shop":
            await self.show_shop_management(query)
        elif data == "admin_game_points":
            await self.show_points_management(query)
        elif data == "admin_game_achievements":
            await self.show_achievements_management(query)
        elif data == "admin_game_reports":
            await self.show_gamification_reports(query)
        elif data == "admin_game_config":
            await self.show_gamification_config(query)
        
        # ============ NARRATIVA ============
        elif data == "admin_narrative_fragments":
            await self.show_fragments_management(query)
        elif data == "admin_narrative_clues":
            await self.show_clues_management(query)
        elif data == "admin_narrative_levels":
            await self.show_diana_levels_management(query)
        elif data == "admin_narrative_validations":
            await self.show_narrative_validations(query)
        elif data == "admin_narrative_backpacks":
            await self.show_backpack_management(query)
        elif data == "admin_narrative_progress":
            await self.show_narrative_progress(query)
        
        # ============ CONFIGURACIÓN ============
        elif data == "admin_config_game":
            await self.show_game_config(query)
        elif data == "admin_config_narrative":
            await self.show_narrative_config(query)
        elif data == "admin_config_vip":
            await self.show_vip_config(query)
        elif data == "admin_config_notifications":
            await self.show_notifications_config(query)
        elif data == "admin_config_security":
            await self.show_security_config(query)
        elif data == "admin_config_performance":
            await self.show_performance_config(query)
        elif data == "admin_config_backup":
            await self.show_backup_system(query)
        elif data == "admin_config_restart":
            await self.restart_bot_system(query)
        
        # ============ ESTADÍSTICAS ============
        elif data == "admin_stats":
            await self.show_statistics_menu(query)
        elif data == "admin_stats_dashboard":
            await self.show_analytics_dashboard(query)
        elif data == "admin_stats_users":
            await self.show_user_analytics(query)
        elif data == "admin_stats_engagement":
            await self.show_engagement_analytics(query)
        elif data == "admin_stats_economy":
            await self.show_economy_analytics(query)
        elif data == "admin_stats_channels":
            await self.show_channel_analytics(query)
        
        else:
            await query.answer("🚧 Funcionalidad específica en desarrollo", show_alert=True)
    
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
    
    # ============================================
    # FUNCIONALIDADES ADMINISTRATIVAS ESPECÍFICAS
    # ============================================
    
    # ========== GESTIÓN DE USUARIOS ==========
    
    async def show_user_search_menu(self, query: types.CallbackQuery):
        """Menú para buscar usuarios específicos"""
        menu_text = """
🔍 **BÚSQUEDA DE USUARIOS**
━━━━━━━━━━━━━━━━━━━━━━━━━

Buscar usuario por:
• ID de Telegram
• Username (@usuario)
• Nombre completo

Envía el criterio de búsqueda:
        """
        
        keyboard = [
            [InlineKeyboardButton(text="🔙 Volver", callback_data="admin_users")]
        ]
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        
        await self.edit_or_send_menu(query.message, menu_text, reply_markup)
        await self.send_temp_message(query.message, "💬 Envía el ID o @username para buscar", 5)
    
    async def show_vip_management_menu(self, query: types.CallbackQuery):
        """Gestión de usuarios VIP"""
        vip_stats = await self.get_vip_stats()
        
        menu_text = f"""
👑 **GESTIÓN DE USUARIOS VIP**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 **Estado VIP:**
• Usuarios VIP activos: {vip_stats['active_vip']}
• Tokens generados hoy: {vip_stats['tokens_today']}
• Expirarán en 24h: {vip_stats['expiring_24h']}

🏆 **Top VIP por Actividad:**
{vip_stats['top_vip_users']}

⚡ **Acciones Rápidas:**
        """
        
        keyboard = [
            [
                InlineKeyboardButton(text="➕ Promover a VIP", callback_data="promote_vip"),
                InlineKeyboardButton(text="➖ Revocar VIP", callback_data="revoke_vip")
            ],
            [
                InlineKeyboardButton(text="🎟️ Generar Token", callback_data="generate_token"),
                InlineKeyboardButton(text="⏰ Extender VIP", callback_data="extend_vip")
            ],
            [
                InlineKeyboardButton(text="📊 Lista VIP", callback_data="list_vip_users"),
                InlineKeyboardButton(text="🔍 Validar Token", callback_data="validate_token")
            ],
            [InlineKeyboardButton(text="🔙 Volver", callback_data="admin_users")]
        ]
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        
        await self.edit_or_send_menu(query.message, menu_text, reply_markup)
    
    async def show_token_management_menu(self, query: types.CallbackQuery):
        """Gestión de tokens VIP"""
        token_stats = await self.get_token_stats()
        
        menu_text = f"""
🎟️ **GESTIÓN DE TOKENS VIP**
━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 **Estadísticas de Tokens:**
• Tokens activos: {token_stats['active_tokens']}
• Tokens usados hoy: {token_stats['used_today']}
• Tokens por expirar: {token_stats['expiring']}

🔄 **Últimos Tokens Generados:**
{token_stats['recent_tokens']}

💎 **Configuración Actual:**
• Duración por defecto: {token_stats['default_duration']} días
• Uso múltiple: {token_stats['multi_use_enabled']}
        """
        
        keyboard = [
            [
                InlineKeyboardButton(text="🆕 Generar Token", callback_data="new_token"),
                InlineKeyboardButton(text="📋 Lista Tokens", callback_data="list_tokens")
            ],
            [
                InlineKeyboardButton(text="🗑️ Revocar Token", callback_data="revoke_token"),
                InlineKeyboardButton(text="📊 Estadísticas", callback_data="token_stats")
            ],
            [
                InlineKeyboardButton(text="⚙️ Configurar", callback_data="config_tokens"),
                InlineKeyboardButton(text="🔄 Limpiar Expirados", callback_data="cleanup_tokens")
            ],
            [InlineKeyboardButton(text="🔙 Volver", callback_data="admin_users")]
        ]
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        
        await self.edit_or_send_menu(query.message, menu_text, reply_markup)
    
    # ========== GESTIÓN DE CANALES ==========
    
    async def show_add_channel_menu(self, query: types.CallbackQuery):
        """Menú para agregar nuevo canal"""
        menu_text = """
➕ **AGREGAR NUEVO CANAL**
━━━━━━━━━━━━━━━━━━━━━━━━━

📝 **Información Requerida:**
• ID del canal de Telegram
• Nombre descriptivo
• Tipo (VIP/Free)
• Descripción

Envía el ID del canal para comenzar:
        """
        
        keyboard = [
            [
                InlineKeyboardButton(text="📺 Canal Gratuito", callback_data="add_free_channel"),
                InlineKeyboardButton(text="💎 Canal VIP", callback_data="add_vip_channel")
            ],
            [InlineKeyboardButton(text="🔙 Volver", callback_data="admin_channels")]
        ]
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        
        await self.edit_or_send_menu(query.message, menu_text, reply_markup)
    
    async def show_channel_monitoring(self, query: types.CallbackQuery):
        """Monitoreo en tiempo real de canales"""
        monitoring_data = await self.get_channel_monitoring_data()
        
        menu_text = f"""
🔍 **MONITOREO DE CANALES**
━━━━━━━━━━━━━━━━━━━━━━━━━━

⚡ **Estado en Tiempo Real:**
• Usuarios conectados: {monitoring_data['connected_users']}
• Actividad última hora: {monitoring_data['activity_1h']} mensajes
• Validaciones pendientes: {monitoring_data['pending_validations']}

📊 **Actividad por Canal:**
{monitoring_data['channel_activity']}

🚨 **Alertas:**
{monitoring_data['alerts']}
        """
        
        keyboard = [
            [
                InlineKeyboardButton(text="🔄 Actualizar", callback_data="refresh_monitoring"),
                InlineKeyboardButton(text="⚡ Auto-refresh", callback_data="toggle_auto_refresh")
            ],
            [
                InlineKeyboardButton(text="📊 Estadísticas", callback_data="channel_stats"),
                InlineKeyboardButton(text="🚨 Ver Alertas", callback_data="view_alerts")
            ],
            [InlineKeyboardButton(text="🔙 Volver", callback_data="admin_channels")]
        ]
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        
        await self.edit_or_send_menu(query.message, menu_text, reply_markup)
    
    # ========== GAMIFICACIÓN ==========
    
    async def show_missions_management(self, query: types.CallbackQuery):
        """Gestión completa de misiones"""
        missions_data = await self.get_missions_data()
        
        menu_text = f"""
🎯 **GESTIÓN DE MISIONES**
━━━━━━━━━━━━━━━━━━━━━━━━━

📊 **Estado Actual:**
• Misiones activas: {missions_data['active_missions']}
• Completadas hoy: {missions_data['completed_today']}
• Usuarios participando: {missions_data['participating_users']}

🎮 **Misiones Populares:**
{missions_data['popular_missions']}

⚡ **Estadísticas:**
• Tasa de completado: {missions_data['completion_rate']}%
• Puntos distribuidos: {missions_data['points_distributed']}
        """
        
        keyboard = [
            [
                InlineKeyboardButton(text="🆕 Nueva Misión", callback_data="create_mission"),
                InlineKeyboardButton(text="✏️ Editar Misión", callback_data="edit_mission")
            ],
            [
                InlineKeyboardButton(text="🗑️ Eliminar Misión", callback_data="delete_mission"),
                InlineKeyboardButton(text="⏰ Programar", callback_data="schedule_mission")
            ],
            [
                InlineKeyboardButton(text="📊 Estadísticas", callback_data="mission_stats"),
                InlineKeyboardButton(text="🏆 Rankings", callback_data="mission_rankings")
            ],
            [InlineKeyboardButton(text="🔙 Volver", callback_data="admin_gamification")]
        ]
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        
        await self.edit_or_send_menu(query.message, menu_text, reply_markup)
    
    async def show_trivia_management(self, query: types.CallbackQuery):
        """Gestión de trivias"""
        trivia_data = await self.get_trivia_data()
        
        menu_text = f"""
🧩 **GESTIÓN DE TRIVIAS**
━━━━━━━━━━━━━━━━━━━━━━━━━

📚 **Banco de Preguntas:**
• Total preguntas: {trivia_data['total_questions']}
• Por dificultad: Fácil ({trivia_data['easy']}) | Media ({trivia_data['medium']}) | Difícil ({trivia_data['hard']})
• Respondidas hoy: {trivia_data['answered_today']}

🏆 **Estadísticas:**
• Tasa de acierto promedio: {trivia_data['avg_success_rate']}%
• Top scorer: {trivia_data['top_scorer']}
        """
        
        keyboard = [
            [
                InlineKeyboardButton(text="➕ Nueva Pregunta", callback_data="add_question"),
                InlineKeyboardButton(text="📝 Editar Pregunta", callback_data="edit_question")
            ],
            [
                InlineKeyboardButton(text="🎯 Trivia Especial", callback_data="special_trivia"),
                InlineKeyboardButton(text="🏆 Tournament", callback_data="trivia_tournament")
            ],
            [
                InlineKeyboardButton(text="📊 Estadísticas", callback_data="trivia_stats"),
                InlineKeyboardButton(text="⚙️ Configurar", callback_data="trivia_config")
            ],
            [InlineKeyboardButton(text="🔙 Volver", callback_data="admin_gamification")]
        ]
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        
        await self.edit_or_send_menu(query.message, menu_text, reply_markup)
    
    # ========== NARRATIVA ==========
    
    async def show_fragments_management(self, query: types.CallbackQuery):
        """Gestión de fragmentos narrativos"""
        fragments_data = await self.get_fragments_data()
        
        menu_text = f"""
📝 **GESTIÓN DE FRAGMENTOS**
━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 **Historia de Diana:**
• Fragmentos totales: {fragments_data['total_fragments']}
• Por nivel: Nivel 1 ({fragments_data['level1']}) | Nivel 4 ({fragments_data['level4']}) | Íntimo ({fragments_data['intimate']})
• Completados hoy: {fragments_data['completed_today']}

🎭 **Progresión:**
• Usuarios en Nivel 1: {fragments_data['users_level1']}
• Usuarios en Nivel 4: {fragments_data['users_level4']}
• Círculo Íntimo: {fragments_data['users_intimate']}
        """
        
        keyboard = [
            [
                InlineKeyboardButton(text="✍️ Nuevo Fragmento", callback_data="create_fragment"),
                InlineKeyboardButton(text="📝 Editar Fragmento", callback_data="edit_fragment")
            ],
            [
                InlineKeyboardButton(text="🗺️ Mapa Narrativo", callback_data="narrative_map"),
                InlineKeyboardButton(text="🔄 Reorganizar", callback_data="reorganize_fragments")
            ],
            [
                InlineKeyboardButton(text="📊 Progresión", callback_data="fragment_progress"),
                InlineKeyboardButton(text="✨ Eventos", callback_data="narrative_events")
            ],
            [InlineKeyboardButton(text="🔙 Volver", callback_data="admin_narrative")]
        ]
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        
        await self.edit_or_send_menu(query.message, menu_text, reply_markup)
    
    async def show_clues_management(self, query: types.CallbackQuery):
        """Gestión de pistas (LorePieces)"""
        clues_data = await self.get_clues_data()
        
        menu_text = f"""
🧩 **GESTIÓN DE PISTAS (LOREPIECES)**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🗝️ **Sistema de Pistas:**
• Pistas totales: {clues_data['total_clues']}
• En mochilas: {clues_data['in_backpacks']}
• Combinaciones posibles: {clues_data['combinations']}
• Combinadas hoy: {clues_data['combined_today']}

🎒 **Estado de Mochilas:**
• Mochilas activas: {clues_data['active_backpacks']}
• Promedio pistas/usuario: {clues_data['avg_clues_per_user']}
        """
        
        keyboard = [
            [
                InlineKeyboardButton(text="🆕 Nueva Pista", callback_data="create_clue"),
                InlineKeyboardButton(text="🔗 Nueva Combinación", callback_data="create_combination")
            ],
            [
                InlineKeyboardButton(text="🎒 Ver Mochilas", callback_data="view_backpacks"),
                InlineKeyboardButton(text="🔄 Redistribuir", callback_data="redistribute_clues")
            ],
            [
                InlineKeyboardButton(text="📊 Estadísticas", callback_data="clues_stats"),
                InlineKeyboardButton(text="🎁 Reward System", callback_data="clue_rewards")
            ],
            [InlineKeyboardButton(text="🔙 Volver", callback_data="admin_narrative")]
        ]
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        
        await self.edit_or_send_menu(query.message, menu_text, reply_markup)
    
    # ========== MÉTODOS DE DATOS AUXILIARES ==========
    
    async def get_vip_stats(self) -> Dict:
        """Obtener estadísticas VIP"""
        return {
            'active_vip': 12,
            'tokens_today': 3,
            'expiring_24h': 2,
            'top_vip_users': "1. @user_vip1 - 89 días\n2. @user_vip2 - 67 días\n3. @user_vip3 - 45 días"
        }
    
    async def get_token_stats(self) -> Dict:
        """Obtener estadísticas de tokens"""
        return {
            'active_tokens': 15,
            'used_today': 2,
            'expiring': 3,
            'recent_tokens': "• VIP30-ABC123 (30 días)\n• VIP15-DEF456 (15 días)\n• VIP7-GHI789 (7 días)",
            'default_duration': 30,
            'multi_use_enabled': 'Activado'
        }
    
    async def get_channel_monitoring_data(self) -> Dict:
        """Obtener datos de monitoreo de canales"""
        return {
            'connected_users': 245,
            'activity_1h': 67,
            'pending_validations': 4,
            'channel_activity': "📺 Canal Free: 45 usuarios\n💎 VIP Gold: 23 usuarios\n💎 VIP Premium: 15 usuarios",
            'alerts': "⚠️ Usuario @spammer detectado\n🔔 Canal VIP cerca del límite"
        }
    
    async def get_missions_data(self) -> Dict:
        """Obtener datos de misiones"""
        return {
            'active_missions': 8,
            'completed_today': 34,
            'participating_users': 67,
            'popular_missions': "1. Interactuar 10 veces (78% completado)\n2. Enviar foto del día (65% completado)\n3. Responder trivia (89% completado)",
            'completion_rate': 73,
            'points_distributed': 2450
        }
    
    async def get_trivia_data(self) -> Dict:
        """Obtener datos de trivias"""
        return {
            'total_questions': 156,
            'easy': 67,
            'medium': 54,
            'hard': 35,
            'answered_today': 89,
            'avg_success_rate': 76,
            'top_scorer': '@trivia_master (98% aciertos)'
        }
    
    async def get_fragments_data(self) -> Dict:
        """Obtener datos de fragmentos narrativos"""
        return {
            'total_fragments': 89,
            'level1': 34,
            'level4': 28,
            'intimate': 15,
            'completed_today': 23,
            'users_level1': 78,
            'users_level4': 34,
            'users_intimate': 12
        }
    
    async def get_clues_data(self) -> Dict:
        """Obtener datos de pistas"""
        return {
            'total_clues': 134,
            'in_backpacks': 567,
            'combinations': 89,
            'combined_today': 15,
            'active_backpacks': 123,
            'avg_clues_per_user': 4.6
        }
    
    # Placeholder methods para funcionalidades no implementadas
    async def show_user_statistics(self, query): await query.answer("📊 Estadísticas de usuarios en desarrollo", show_alert=True)
    async def show_moderation_menu(self, query): await query.answer("🚫 Sistema de moderación en desarrollo", show_alert=True)
    async def show_broadcast_menu(self, query): await query.answer("📢 Sistema de envío masivo en desarrollo", show_alert=True)
    async def show_edit_channels_menu(self, query): await query.answer("✏️ Edición de canales en desarrollo", show_alert=True)
    async def show_free_channels_menu(self, query): await query.answer("🆓 Gestión canales gratuitos en desarrollo", show_alert=True)
    async def show_vip_channels_menu(self, query): await query.answer("💎 Gestión canales VIP en desarrollo", show_alert=True)
    async def show_channel_validations(self, query): await query.answer("✅ Sistema de validaciones en desarrollo", show_alert=True)
    async def show_gifts_management(self, query): await query.answer("🎁 Gestión de regalos en desarrollo", show_alert=True)
    async def show_shop_management(self, query): await query.answer("🏪 Gestión de tienda en desarrollo", show_alert=True)
    async def show_points_management(self, query): await query.answer("💰 Gestión de puntos en desarrollo", show_alert=True)
    async def show_achievements_management(self, query): await query.answer("🏆 Gestión de logros en desarrollo", show_alert=True)
    async def show_gamification_reports(self, query): await query.answer("📊 Reportes de gamificación en desarrollo", show_alert=True)
    async def show_gamification_config(self, query): await query.answer("⚙️ Configuración de gamificación en desarrollo", show_alert=True)
    async def show_diana_levels_management(self, query): await query.answer("🎭 Gestión niveles Diana en desarrollo", show_alert=True)
    async def show_narrative_validations(self, query): await query.answer("✅ Validaciones narrativas en desarrollo", show_alert=True)
    async def show_backpack_management(self, query): await query.answer("🎒 Gestión de mochilas en desarrollo", show_alert=True)
    async def show_narrative_progress(self, query): await query.answer("📈 Progreso narrativo en desarrollo", show_alert=True)
    async def show_game_config(self, query): await query.answer("🎮 Configuración de juegos en desarrollo", show_alert=True)
    async def show_narrative_config(self, query): await query.answer("📖 Configuración narrativa en desarrollo", show_alert=True)
    async def show_vip_config(self, query): await query.answer("👑 Configuración VIP en desarrollo", show_alert=True)
    async def show_notifications_config(self, query): await query.answer("🔔 Configuración notificaciones en desarrollo", show_alert=True)
    async def show_security_config(self, query): await query.answer("🛡️ Configuración de seguridad en desarrollo", show_alert=True)
    async def show_performance_config(self, query): await query.answer("⚡ Configuración de rendimiento en desarrollo", show_alert=True)
    async def show_backup_system(self, query): await query.answer("💾 Sistema de backup en desarrollo", show_alert=True)
    async def restart_bot_system(self, query): await query.answer("🔄 Reinicio del sistema en desarrollo", show_alert=True)
    async def show_statistics_menu(self, query): await query.answer("📊 Menú de estadísticas en desarrollo", show_alert=True)
    async def show_analytics_dashboard(self, query): await query.answer("📈 Dashboard de analytics en desarrollo", show_alert=True)
    async def show_user_analytics(self, query): await query.answer("👥 Analytics de usuarios en desarrollo", show_alert=True)
    async def show_engagement_analytics(self, query): await query.answer("🎮 Analytics de engagement en desarrollo", show_alert=True)
    async def show_economy_analytics(self, query): await query.answer("💰 Analytics de economía en desarrollo", show_alert=True)
    async def show_channel_analytics(self, query): await query.answer("📺 Analytics de canales en desarrollo", show_alert=True)
    
    # ============================================
    # FUNCIONES AUXILIARES PARA USUARIO
    # ============================================
    
    async def get_user_data(self, user_id: int) -> Dict:
        """Obtener datos completos del usuario"""
        try:
            # Aquí integrarías con tus servicios reales
            # Por ahora datos mock
            return {
                'name': 'Usuario Diana',
                'points': 1250,
                'level': 5,
                'experience': 67,
                'streak': 12,
                'narrative_progress': 45,
                'vip_status': '👑 VIP Gold (15 días restantes)',
                'last_seen': 'Hace 2 horas',
                'clues_count': 8,
                'combinations_made': 3,
                'diana_level': 'Nivel 1 - Los Kinkys',
                'total_points_earned': 15420,
                'missions_completed': 23,
                'trivia_answered': 45,
                'success_rate': 78
            }
        except Exception as e:
            log.error(f"Error obteniendo datos de usuario {user_id}: {e}")
            return self.get_default_user_data()
    
    def get_default_user_data(self) -> Dict:
        """Datos por defecto para nuevos usuarios"""
        return {
            'name': 'Nuevo Usuario',
            'points': 0,
            'level': 1,
            'experience': 0,
            'streak': 0,
            'narrative_progress': 0,
            'vip_status': 'Usuario Gratuito',
            'last_seen': 'Ahora',
            'clues_count': 0,
            'combinations_made': 0,
            'diana_level': 'Principiante',
            'total_points_earned': 0,
            'missions_completed': 0,
            'trivia_answered': 0,
            'success_rate': 0
        }
    
    async def get_diana_reaction(self, user_data: Dict) -> str:
        """Generar reacción dinámica de Diana basada en el progreso del usuario"""
        level = user_data['level']
        narrative_progress = user_data['narrative_progress']
        streak = user_data['streak']
        
        if narrative_progress >= 80:
            return "🎭 Diana te mira con una sonrisa misteriosa... 'Estás cerca de la verdad'"
        elif narrative_progress >= 50:
            return "🎭 'Interesante progreso', susurra Diana mientras revisa tus avances"
        elif streak >= 10:
            return f"🎭 Diana asiente aprobatoriamente: 'Tu constancia me impresiona ({streak} días seguidos)'"
        elif level >= 5:
            return "🎭 Diana observa tu nivel con curiosidad: 'Veo potencial en ti'"
        else:
            return "🎭 Diana te saluda con una mirada enigmática: 'Bienvenido a mi mundo'"
    
    async def get_progress_bars(self, user_data: Dict) -> str:
        """Generar barras de progreso visuales"""
        def create_bar(percentage: int, length: int = 10) -> str:
            filled = int(percentage / 100 * length)
            empty = length - filled
            return "█" * filled + "░" * empty
        
        level_progress = user_data['experience']
        narrative_progress = user_data['narrative_progress']
        
        return f"""
📊 **Barras de Progreso:**
🎯 Nivel {user_data['level']}: {create_bar(level_progress)} {level_progress}%
📖 Historia: {create_bar(narrative_progress)} {narrative_progress}%"""
    
    async def build_user_menu_keyboard(self, user_data: Dict) -> InlineKeyboardMarkup:
        """Construir teclado contextual basado en el estado del usuario"""
        keyboard = []
        
        # Primera fila - acciones principales
        row1 = [
            InlineKeyboardButton(text="👤 Mi Perfil", callback_data="user_profile"),
            InlineKeyboardButton(text="📊 Dashboard", callback_data="user_dashboard")
        ]
        keyboard.append(row1)
        
        # Segunda fila - funcionalidades core
        row2 = [
            InlineKeyboardButton(text="🎒 Mochila", callback_data="user_backpack"),
            InlineKeyboardButton(text="🎯 Misiones", callback_data="user_missions")
        ]
        keyboard.append(row2)
        
        # Tercera fila - juegos y entretenimiento
        row3 = [
            InlineKeyboardButton(text="🎮 Juegos", callback_data="user_games"),
            InlineKeyboardButton(text="🎁 Regalo", callback_data="daily_gift")
        ]
        keyboard.append(row3)
        
        # Cuarta fila - tienda y VIP
        row4 = []
        if user_data.get('points', 0) > 0:
            row4.append(InlineKeyboardButton(text="🛍️ Tienda", callback_data="user_shop"))
        
        if 'VIP' not in user_data.get('vip_status', ''):
            row4.append(InlineKeyboardButton(text="👑 Ser VIP", callback_data="upgrade_vip"))
        else:
            row4.append(InlineKeyboardButton(text="👑 Mi VIP", callback_data="vip_status"))
        
        if row4:
            keyboard.append(row4)
        
        # Quinta fila - configuración y soporte
        row5 = [
            InlineKeyboardButton(text="⚙️ Configuración", callback_data="user_settings"),
            InlineKeyboardButton(text="❓ Ayuda", callback_data="user_help")
        ]
        keyboard.append(row5)
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    async def get_user_achievements(self, user_id: int) -> Dict:
        """Obtener logros del usuario"""
        return {
            'recent_text': "🏆 Primer Beso (hace 2 días)\n🎯 Misionero (hace 1 semana)\n📖 Explorador (hace 2 semanas)"
        }
    
    async def get_recent_activity(self, user_id: int) -> str:
        """Obtener actividad reciente del usuario"""
        return "• Completó misión 'Interactuar 10 veces'\n• Combinó pistas misteriosas\n• Respondió trivia correctamente\n• Reclamó regalo diario"
    
    async def get_next_objectives(self, user_data: Dict) -> str:
        """Obtener próximos objetivos para el usuario"""
        objectives = []
        
        if user_data['narrative_progress'] < 50:
            objectives.append("📖 Continuar explorando la historia de Diana")
        
        if user_data['clues_count'] >= 3:
            objectives.append("🔗 Intentar nueva combinación de pistas")
        
        if user_data['experience'] > 80:
            objectives.append("🎯 ¡Estás cerca del siguiente nivel!")
        
        objectives.append("🎁 Reclamar regalo diario")
        
        return "\n".join([f"• {obj}" for obj in objectives])
    
    async def get_detailed_profile(self, user_id: int) -> Dict:
        """Obtener perfil detallado del usuario"""
        return {
            'display_name': 'Usuario Diana',
            'username': 'diana_user',
            'user_id': user_id,
            'join_date': '15 de enero, 2025',
            'level': 5,
            'rank': 'Top 20%',
            'experience': 67,
            'total_points': 1250,
            'total_time': '2 semanas',
            'diana_level': 'Nivel 1 - Los Kinkys',
            'fragments_completed': 12,
            'clues_found': 8,
            'vip_details': '👑 VIP Gold hasta 2025-08-15',
            'notifications_enabled': 'Activadas',
            'preferred_time': '18:00 - 22:00',
            'difficulty_level': 'Intermedio'
        }
    
    async def get_backpack_data(self, user_id: int) -> Dict:
        """Obtener datos de la mochila del usuario"""
        return {
            'total_clues': 8,
            'clues_list': "🗝️ Pista del Espejo\n🧩 Fragmento Misterioso\n📜 Carta Antigua\n💎 Gema de la Verdad\n🔍 Lupa Encantada\n📸 Foto Reveladora\n🎭 Máscara de Diana\n⚡ Energía Oculta",
            'available_combinations': "🔗 Espejo + Carta (Desbloquea Nivel 2)\n🔗 Gema + Máscara (Secreto de Diana)\n🔗 Foto + Lupa (Pista Especial)",
            'unlocked_fragments': 12,
            'next_goal': "Encontrar la Llave Maestra",
            'diana_hint': "Las apariencias engañan, busca más allá de lo evidente...",
            'quick_actions': "✨ Tienes 3 combinaciones disponibles\n🎁 Nueva pista disponible en 2 horas",
            'combinations': [
                {'id': 1, 'name': 'Espejo + Carta'},
                {'id': 2, 'name': 'Gema + Máscara'},
                {'id': 3, 'name': 'Foto + Lupa'}
            ]
        }
    
    async def get_user_missions_data(self, user_id: int) -> Dict:
        """Obtener datos de misiones del usuario"""
        return {
            'active_count': 5,
            'completed_today': 2,
            'points_earned': 150,
            'daily_missions': "✅ Enviar saludo (completada) +20 besitos\n🔄 Interactuar 10 veces (7/10) +50 besitos\n⏳ Responder trivia (pendiente) +30 besitos",
            'weekly_missions': "🎯 Completar 5 misiones diarias (2/5) +200 besitos\n📖 Leer 3 fragmentos (1/3) +150 besitos",
            'special_missions': "✨ Descubrir secreto de Diana (en progreso) +500 besitos\n💎 Alcanzar 2000 besitos (1250/2000) +Premium 7 días",
            'available_rewards': "🎁 2 recompensas listas para reclamar (+70 besitos)",
            'actionable_missions': [
                {'id': 1, 'name': 'Responder Trivia', 'icon': '❓'},
                {'id': 2, 'name': 'Interactuar más', 'icon': '💬'},
                {'id': 3, 'name': 'Explorar mochila', 'icon': '🎒'}
            ]
        }
    
    # Funciones de usuario adicionales
    async def handle_daily_gift(self, query: types.CallbackQuery):
        """Manejar regalo diario"""
        await query.answer("🎁 Procesando regalo diario...", show_alert=False)
        
        # Simular procesamiento
        import asyncio
        await asyncio.sleep(1)
        
        # Mostrar resultado
        await self.send_temp_message(
            query.message, 
            "🎉 ¡Regalo reclamado! +50 besitos\n🔥 Racha: 13 días consecutivos", 
            7
        )
    
    async def show_user_games(self, query: types.CallbackQuery):
        """Mostrar menú de juegos para usuario"""
        menu_text = """
🎮 **JUEGOS Y ENTRETENIMIENTO**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🧠 **Trivias:**
❓ Trivia de Diana (disponible)
🏆 Trivia Semanal (3 días restantes)

🎯 **Desafíos:**
⚡ Desafío Rápido (15 preguntas)
🎭 Adivina la Frase de Diana

🎲 **Mini Juegos:**
🔍 Encuentra las Diferencias
🧩 Rompecabezas Narrativo

🏆 **Tu Record:**
• Mejor racha trivia: 8 aciertos
• Puntos en juegos: 450 besitos
        """
        
        keyboard = [
            [
                InlineKeyboardButton(text="❓ Trivia Diana", callback_data="play_trivia"),
                InlineKeyboardButton(text="🎯 Desafío", callback_data="play_challenge")
            ],
            [
                InlineKeyboardButton(text="🔍 Mini Juegos", callback_data="mini_games"),
                InlineKeyboardButton(text="🏆 Rankings", callback_data="game_rankings")
            ],
            [
                InlineKeyboardButton(text="🔙 Volver", callback_data="user_main"),
                InlineKeyboardButton(text="🎁 Premio Diario", callback_data="daily_game_reward")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        
        await self.edit_or_send_menu(query.message, menu_text, reply_markup)
    
    async def show_user_shop(self, query: types.CallbackQuery):
        """Mostrar tienda de besitos"""
        user_id = query.from_user.id
        user_data = await self.get_user_data(user_id)
        
        menu_text = f"""
🛍️ **TIENDA DE BESITOS**
━━━━━━━━━━━━━━━━━━━━━━━━━

💰 **Tus Besitos:** {user_data['points']:,}

🎁 **Artículos Disponibles:**

📦 **Paquetes de Pistas:**
🗝️ Pista Básica - 100 besitos
💎 Pista Premium - 250 besitos
✨ Pista Legendaria - 500 besitos

👑 **Mejoras VIP:**
⭐ VIP 7 días - 1,000 besitos
💎 VIP 15 días - 2,000 besitos
👑 VIP 30 días - 3,500 besitos

🎮 **Extras de Juego:**
🍀 Suerte x2 (1 día) - 200 besitos
⚡ XP Boost (3 días) - 300 besitos
🎯 Misiones Extra - 150 besitos

🎭 **Especiales de Diana:**
💌 Mensaje Personal - 800 besitos
🎪 Evento Privado - 1,500 besitos
        """
        
        keyboard = [
            [
                InlineKeyboardButton(text="🗝️ Pistas", callback_data="shop_clues"),
                InlineKeyboardButton(text="👑 VIP", callback_data="shop_vip")
            ],
            [
                InlineKeyboardButton(text="🎮 Extras", callback_data="shop_extras"),
                InlineKeyboardButton(text="🎭 Diana", callback_data="shop_diana")
            ],
            [
                InlineKeyboardButton(text="🛒 Mis Compras", callback_data="my_purchases"),
                InlineKeyboardButton(text="🎁 Ofertas", callback_data="shop_offers")
            ],
            [
                InlineKeyboardButton(text="🔙 Volver", callback_data="user_main"),
                InlineKeyboardButton(text="💰 Ganar Besitos", callback_data="earn_points")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        
        await self.edit_or_send_menu(query.message, menu_text, reply_markup)