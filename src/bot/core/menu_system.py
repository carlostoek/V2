# diana_menu_system.py
"""
Sistema de Menús Elegante para Diana Bot V2
🎛️ Menús fluidos, intuitivos y auto-actualizables
"""

import asyncio
from typing import Dict, List, Callable, Optional, Any
from dataclasses import dataclass
from enum import Enum
import time

from aiogram import types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from src.utils.sexy_logger import log

class MenuType(Enum):
    MAIN_ADMIN = "main_admin"
    MAIN_USER = "main_user"
    CHANNELS = "channels"
    GAMIFICATION = "gamification"
    NARRATIVE = "narrative"
    USERS = "users"
    CONFIG = "config"
    ANALYTICS = "analytics"

class UserRole(Enum):
    ADMIN = "admin"
    VIP = "vip" 
    FREE = "free"

@dataclass
class MenuOption:
    text: str
    callback: str
    icon: str
    description: str
    required_role: UserRole = UserRole.FREE
    submenu: Optional[str] = None

@dataclass
class MenuConfig:
    title: str
    description: str
    options: List[MenuOption]
    back_menu: Optional[str] = None
    auto_delete_seconds: int = 0  # 0 = no auto delete

class DianaMenuSystem:
    """
    Sistema de menús elegante con edición de mensajes
    ¡Navegación fluida sin spam de mensajes!
    """
    
    def __init__(self):
        self.menus = self._initialize_menus()
        self.user_sessions = {}  # Trackear sesiones de usuario
        self.temp_messages = {}  # Mensajes temporales para auto-eliminar
        
    def _initialize_menus(self) -> Dict[str, MenuConfig]:
        """Inicializar todos los menús del sistema"""
        
        return {
            # ============================================
            # MENÚ PRINCIPAL ADMINISTRADOR
            # ============================================
            "main_admin": MenuConfig(
                title="🎛️ PANEL DE ADMINISTRACIÓN DIANA",
                description="Sistema de control principal del bot",
                options=[
                    MenuOption("📺 Canales", "menu_channels", "📺", "Administrar canales y accesos", UserRole.ADMIN),
                    MenuOption("👥 Usuarios", "menu_users", "👥", "Gestión de usuarios y roles", UserRole.ADMIN),
                    MenuOption("🎮 Gamificación", "menu_gamification", "🎮", "Puntos, misiones y recompensas", UserRole.ADMIN),
                    MenuOption("📖 Narrativa", "menu_narrative", "📖", "Historia, pistas y fragmentos", UserRole.ADMIN),
                    MenuOption("⚙️ Configuración", "menu_config", "⚙️", "Ajustes del sistema", UserRole.ADMIN),
                    MenuOption("📊 Analytics", "menu_analytics", "📊", "Estadísticas y reportes", UserRole.ADMIN),
                    MenuOption("🔄 Refresh", "refresh_admin", "🔄", "Actualizar estado del bot", UserRole.ADMIN),
                    MenuOption("❌ Cerrar", "close_menu", "❌", "Cerrar panel de administración", UserRole.ADMIN)
                ]
            ),
            
            # ============================================
            # MENÚ PRINCIPAL USUARIO
            # ============================================
            "main_user": MenuConfig(
                title="🎭 DIANA BOT - MENÚ PRINCIPAL",
                description="Bienvenido al mundo de Diana",
                options=[
                    MenuOption("👤 Mi Perfil", "user_profile", "👤", "Ver perfil y estadísticas"),
                    MenuOption("🎒 Mochila", "user_inventory", "🎒", "Pistas narrativas desbloqueadas"),
                    MenuOption("🎮 Juegos", "user_games", "🎮", "Trivias y minijuegos"),
                    MenuOption("🎯 Misiones", "user_missions", "🎯", "Misiones y desafíos"),
                    MenuOption("🎁 Regalo Diario", "daily_gift", "🎁", "Reclamar regalo del día"),
                    MenuOption("🛍️ Tienda", "shop", "🛍️ ", "Tienda de besitos"),
                    MenuOption("👑 VIP", "vip_section", "👑", "Contenido exclusivo VIP", UserRole.VIP),
                    MenuOption("🔧 Admin", "admin_panel", "🔧", "Panel de administración", UserRole.ADMIN)
                ]
            ),
            
            # ============================================
            # MENÚ DE CANALES
            # ============================================
            "channels": MenuConfig(
                title="📺 ADMINISTRACIÓN DE CANALES",
                description="Gestión completa de canales y accesos",
                options=[
                    MenuOption("➕ Agregar Canal", "add_channel", "➕", "Añadir nuevo canal al sistema", UserRole.ADMIN),
                    MenuOption("📝 Editar Canales", "edit_channels", "📝", "Modificar canales existentes", UserRole.ADMIN),
                    MenuOption("🗑️ Eliminar Canal", "delete_channel", "🗑️", "Remover canal del sistema", UserRole.ADMIN),
                    MenuOption("🔍 Ver Estado", "channel_status", "🔍", "Estado de todos los canales", UserRole.ADMIN),
                    MenuOption("👥 Miembros", "channel_members", "👥", "Gestionar miembros de canales", UserRole.ADMIN),
                    MenuOption("🎟️ Tokens VIP", "vip_tokens", "🎟️", "Generar y gestionar tokens", UserRole.ADMIN),
                    MenuOption("⚡ Acciones Rápidas", "quick_actions", "⚡", "Expulsar/añadir usuarios", UserRole.ADMIN),
                    MenuOption("◀️ Volver", "main_admin", "◀️", "Volver al menú principal")
                ],
                back_menu="main_admin"
            ),
            
            # ============================================
            # MENÚ DE USUARIOS
            # ============================================
            "users": MenuConfig(
                title="👥 GESTIÓN DE USUARIOS",
                description="Control de usuarios y roles del sistema",
                options=[
                    MenuOption("🔍 Buscar Usuario", "search_user", "🔍", "Buscar por ID o username", UserRole.ADMIN),
                    MenuOption("📊 Top Usuarios", "top_users", "📊", "Rankings de puntos y actividad", UserRole.ADMIN),
                    MenuOption("👑 Gestión VIP", "manage_vip", "👑", "Promover/demover usuarios VIP", UserRole.ADMIN),
                    MenuOption("🎭 Roles", "manage_roles", "🎭", "Asignar roles especiales", UserRole.ADMIN),
                    MenuOption("🚫 Moderar", "moderate_user", "🚫", "Banear/desbanear usuarios", UserRole.ADMIN),
                    MenuOption("📈 Estadísticas", "user_stats", "📈", "Estadísticas generales", UserRole.ADMIN),
                    MenuOption("💌 Mensaje Masivo", "mass_message", "💌", "Enviar mensaje a todos", UserRole.ADMIN),
                    MenuOption("◀️ Volver", "main_admin", "◀️", "Volver al menú principal")
                ],
                back_menu="main_admin"
            ),
            
            # ============================================
            # MENÚ DE GAMIFICACIÓN
            # ============================================
            "gamification": MenuConfig(
                title="🎮 SISTEMA DE GAMIFICACIÓN",
                description="Puntos, misiones, recompensas y progresión",
                options=[
                    MenuOption("🎯 Misiones", "manage_missions", "🎯", "Crear y editar misiones", UserRole.ADMIN),
                    MenuOption("🧩 Trivias", "manage_trivia", "🧩", "Gestionar trivias y preguntas", UserRole.ADMIN),
                    MenuOption("🏆 Logros", "manage_achievements", "🏆", "Sistema de logros e insignias", UserRole.ADMIN),
                    MenuOption("🎁 Regalos", "manage_gifts", "🎁", "Configurar regalos diarios", UserRole.ADMIN),
                    MenuOption("💰 Puntos", "manage_points", "💰", "Ajustar puntos de usuarios", UserRole.ADMIN),
                    MenuOption("🏪 Tienda", "manage_shop", "🏪", "Configurar tienda de besitos", UserRole.ADMIN),
                    MenuOption("🎰 Subastas VIP", "manage_auctions", "🎰", "Gestionar subastas exclusivas", UserRole.ADMIN),
                    MenuOption("◀️ Volver", "main_admin", "◀️", "Volver al menú principal")
                ],
                back_menu="main_admin"
            ),
            
            # ============================================
            # MENÚ DE NARRATIVA
            # ============================================
            "narrative": MenuConfig(
                title="📖 SISTEMA NARRATIVO",
                description="Historia, fragmentos y progresión narrativa",
                options=[
                    MenuOption("📝 Fragmentos", "manage_fragments", "📝", "Crear y editar fragmentos", UserRole.ADMIN),
                    MenuOption("🧩 Pistas", "manage_clues", "🧩", "Gestionar LorePieces", UserRole.ADMIN),
                    MenuOption("🗺️ Mapa Narrativo", "narrative_map", "🗺️", "Visualizar progresión global", UserRole.ADMIN),
                    MenuOption("🎭 Personajes", "manage_characters", "🎭", "Diana, Lucien y otros", UserRole.ADMIN),
                    MenuOption("📊 Progreso Global", "narrative_progress", "📊", "Ver avance de usuarios", UserRole.ADMIN),
                    MenuOption("🔀 Combinaciones", "manage_combinations", "🔀", "Configurar combinaciones de pistas", UserRole.ADMIN),
                    MenuOption("✨ Eventos Especiales", "special_events", "✨", "Crear eventos narrativos", UserRole.ADMIN),
                    MenuOption("◀️ Volver", "main_admin", "◀️", "Volver al menú principal")
                ],
                back_menu="main_admin"
            ),
            
            # ============================================
            # MENÚ DE CONFIGURACIÓN
            # ============================================
            "config": MenuConfig(
                title="⚙️ CONFIGURACIÓN DEL SISTEMA",
                description="Ajustes generales y parámetros del bot",
                options=[
                    MenuOption("🔧 Parámetros", "system_params", "🔧", "Configurar parámetros globales", UserRole.ADMIN),
                    MenuOption("⏰ Horarios", "schedule_config", "⏰", "Configurar horarios automáticos", UserRole.ADMIN),
                    MenuOption("💌 Notificaciones", "notification_config", "💌", "Ajustar mensajes automáticos", UserRole.ADMIN),
                    MenuOption("🛡️ Seguridad", "security_config", "🛡️", "Configuración de seguridad", UserRole.ADMIN),
                    MenuOption("🔄 Backup", "backup_system", "🔄", "Respaldo de datos", UserRole.ADMIN),
                    MenuOption("📋 Logs", "system_logs", "📋", "Ver logs del sistema", UserRole.ADMIN),
                    MenuOption("🔌 Integraciones", "integrations", "🔌", "APIs y servicios externos", UserRole.ADMIN),
                    MenuOption("◀️ Volver", "main_admin", "◀️", "Volver al menú principal")
                ],
                back_menu="main_admin"
            ),
            
            # ============================================
            # MENÚ DE ANALYTICS
            # ============================================
            "analytics": MenuConfig(
                title="📊 ANALYTICS Y REPORTES",
                description="Estadísticas y métricas del bot",
                options=[
                    MenuOption("📈 Dashboard", "analytics_dashboard", "📈", "Dashboard principal", UserRole.ADMIN),
                    MenuOption("👥 Usuarios Activos", "user_analytics", "👥", "Métricas de usuarios", UserRole.ADMIN),
                    MenuOption("🎮 Engagement", "engagement_analytics", "🎮", "Participación en actividades", UserRole.ADMIN),
                    MenuOption("💰 Economía", "economy_analytics", "💰", "Flujo de puntos y recompensas", UserRole.ADMIN),
                    MenuOption("📖 Narrativa", "narrative_analytics", "📖", "Progreso narrativo global", UserRole.ADMIN),
                    MenuOption("📺 Canales", "channel_analytics", "📺", "Estadísticas de canales", UserRole.ADMIN),
                    MenuOption("📊 Reportes", "generate_reports", "📊", "Generar reportes personalizados", UserRole.ADMIN),
                    MenuOption("◀️ Volver", "main_admin", "◀️", "Volver al menú principal")
                ],
                back_menu="main_admin"
            )
        }
    
    # ============================================
    # MÉTODO PRINCIPAL: MOSTRAR MENÚ
    # ============================================
    
    async def show_menu(self, message_or_query, menu_name: str, user_role: UserRole = UserRole.FREE) -> None:
        """
        Muestra un menú editando el mensaje actual (no crear nuevo)
        """
        try:
            menu_config = self.menus.get(menu_name)
            if not menu_config:
                log.error(f"Menú no encontrado: {menu_name}")
                return
            
            if isinstance(message_or_query, types.CallbackQuery):
                user_id = message_or_query.from_user.id
                message = message_or_query.message
            else:
                user_id = message_or_query.from_user.id
                message = message_or_query
            
            # Log de navegación
            log.user_action(
                f"Navegando a menú: {menu_name}",
                user_id=user_id,
                action="menu_navigation"
            )
            
            # Filtrar opciones según rol del usuario
            available_options = [
                option for option in menu_config.options
                if self._user_has_access(user_role, option.required_role)
            ]
            
            # Crear texto del menú
            menu_text = self._build_menu_text(menu_config, available_options, user_role)
            
            # Crear teclado
            keyboard = self._build_keyboard(available_options, menu_config.back_menu)
            
            # Editar mensaje existente o enviar nuevo
            if isinstance(message_or_query, types.CallbackQuery):
                # Editar mensaje existente
                await message_or_query.edit_message_text(
                    text=menu_text,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
                await message_or_query.answer()  # Quitar loading
                
            else:
                # Enviar nuevo mensaje (desde comando)
                sent_message = await message.reply(
                    text=menu_text,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
                
                # Guardar referencia del mensaje para futuras ediciones
                self.user_sessions[user_id] = {
                    'message_id': sent_message.message_id,
                    'chat_id': sent_message.chat.id,
                    'menu_stack': [menu_name]
                }
            
            # Auto-eliminar si está configurado
            if menu_config.auto_delete_seconds > 0:
                await self._schedule_auto_delete(message_or_query, menu_config.auto_delete_seconds)
                
        except Exception as e:
            log.error(f"Error mostrando menú {menu_name}", error=e)
            await self._send_error_message(message_or_query, "Error mostrando menú")
    
    # ============================================
    # CONSTRUCCIÓN DE MENÚS
    # ============================================
    
    def _build_menu_text(self, menu_config: MenuConfig, options: List[MenuOption], 
                        user_role: UserRole) -> str:
        """Construir texto del menú con formato elegante"""
        
        lines = [
            f"<b>{menu_config.title}</b>",
            f"<i>{menu_config.description}</i>",
            "",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            ""
        ]
        
        # Agrupar opciones por categoría si es necesario
        for option in options:
            status_icon = self._get_status_icon(option, user_role)
            lines.append(f"{option.icon} <b>{option.text}</b> {status_icon}")
            lines.append(f"   <i>{option.description}</i>")
            lines.append("")
        
        lines.extend([
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"👤 <b>Rol:</b> {user_role.value.upper()}",
            f"🕐 <b>Última actualización:</b> {time.strftime('%H:%M:%S')}"
        ])
        
        return "\n".join(lines)
    
    def _build_keyboard(self, options: List[MenuOption], back_menu: Optional[str] = None) -> InlineKeyboardMarkup:
        """Construir teclado inline con disposición inteligente"""
        
        keyboard = []
        
        # Opciones principales (máximo 2 por fila)
        main_options = [opt for opt in options if not opt.callback.startswith(('close_', 'back_', 'main_admin'))]
        
        for i in range(0, len(main_options), 2):
            row = []
            for j in range(2):
                if i + j < len(main_options):
                    option = main_options[i + j]
                    row.append(InlineKeyboardButton(
                        text=f"{option.icon} {option.text}",
                        callback_data=option.callback
                    ))
            keyboard.append(row)
        
        # Fila de navegación (volver, cerrar, etc.)
        nav_row = []
        for option in options:
            if option.callback.startswith(('close_', 'main_admin', 'refresh_')):
                nav_row.append(InlineKeyboardButton(
                    text=f"{option.icon} {option.text}",
                    callback_data=option.callback
                ))
        
        if nav_row:
            keyboard.append(nav_row)
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    # ============================================
    # UTILIDADES
    # ============================================
    
    def _user_has_access(self, user_role: UserRole, required_role: UserRole) -> bool:
        """Verificar si el usuario tiene acceso a una opción"""
        role_hierarchy = {
            UserRole.FREE: 0,
            UserRole.VIP: 1,
            UserRole.ADMIN: 2
        }
        return role_hierarchy.get(user_role, 0) >= role_hierarchy.get(required_role, 0)
    
    def _get_status_icon(self, option: MenuOption, user_role: UserRole) -> str:
        """Obtener icono de estado para una opción"""
        if option.required_role == UserRole.ADMIN:
            return "🔒" if user_role != UserRole.ADMIN else "✅"
        elif option.required_role == UserRole.VIP:
            return "👑" if user_role == UserRole.FREE else "✅"
        return "✅"
    
    async def _schedule_auto_delete(self, message_or_query, seconds: int) -> None:
        """Programar auto-eliminación de mensaje"""
        async def delete_message():
            await asyncio.sleep(seconds)
            try:
                if isinstance(message_or_query, types.CallbackQuery):
                    await message_or_query.message.delete()
                else:
                    await message_or_query.delete()
            except:
                pass  # Mensaje ya eliminado o sin permisos
        
        asyncio.create_task(delete_message())
    
    async def _send_error_message(self, message_or_query, error_text: str) -> None:
        """Enviar mensaje de error temporal"""
        try:
            if isinstance(message_or_query, types.CallbackQuery):
                await message_or_query.answer(f"❌ {error_text}", show_alert=True)
            else:
                error_msg = await message_or_query.reply(f"❌ {error_text}")
                # Auto-eliminar error en 5 segundos
                await self._schedule_auto_delete(error_msg, 5)
        except Exception as e:
            log.error("Error enviando mensaje de error", error=e)
    
    # ============================================
    # NOTIFICACIONES TEMPORALES
    # ============================================
    
    async def send_temp_notification(self, message_or_query, text: str, 
                                   seconds: int = 5, alert: bool = False, bot=None) -> None:
        """Enviar notificación temporal que se auto-elimina"""
        
        try:
            if isinstance(message_or_query, types.CallbackQuery) and alert:
                # Mostrar como alert popup
                await message_or_query.answer(text, show_alert=True)
            else:
                # Enviar como mensaje temporal
                if isinstance(message_or_query, types.CallbackQuery):
                    chat_id = message_or_query.message.chat.id
                else:
                    chat_id = message_or_query.chat.id
                
                if bot:
                    message = await bot.send_message(
                        chat_id=chat_id,
                        text=f"💫 {text}",
                        parse_mode='HTML'
                    )
                    
                    # Auto-eliminar
                    await self._schedule_auto_delete(message, seconds)
                    
                    log.info(f"📨 Notificación temporal enviada: {text} (auto-delete en {seconds}s)")
                
        except Exception as e:
            log.error("Error enviando notificación temporal", error=e)


# Instancia global del sistema de menús
diana_menu_system = DianaMenuSystem()