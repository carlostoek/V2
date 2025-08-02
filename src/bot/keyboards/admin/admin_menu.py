"""
Sistema de Menús de Administración Unificado
🛠️ Menú principal con estructura 2x3 y navegación lineal
"""

import asyncio
from typing import Dict, List, Callable, Optional, Any
from dataclasses import dataclass
from enum import Enum
import time

from aiogram import types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ...database.engine import get_session
from ...database.models.channel import Channel
from ...utils.sexy_logger import log

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

@dataclass
class MenuConfig:
    title: str
    description: str
    options: List[MenuOption]
    back_menu: Optional[str] = None

class AdminMenuSystem:
    """
    Sistema de menús de administración con navegación lineal
    Edita el mismo mensaje para evitar spam
    """
    
    def __init__(self):
        self.menus = self._initialize_menus()
        self.user_sessions = {}
        
    def _initialize_menus(self) -> Dict[str, MenuConfig]:
        """Inicializar todos los menús del sistema"""
        
        return {
            # ============================================
            # MENÚ PRINCIPAL ADMINISTRADOR (Estructura 2x3)
            # ============================================
            "main_admin": MenuConfig(
                title="🛠️ Panel de Administración",
                description="Bienvenido al centro de control del bot.\nDesde aquí puedes gestionar canales, configurar\nel juego, narrativa y configuración general.\n\nSelecciona una opción del menú:",
                options=[
                    MenuOption("Canal VIP", "admin:channel_vip", "💎", "Configuración y admin VIP", UserRole.ADMIN),
                    MenuOption("Canal Free", "admin:channel_free", "🆓", "Configuración y admin Free", UserRole.ADMIN),
                    MenuOption("Juego el Diván", "admin:gamification", "🎮", "Configuración de gamificación", UserRole.ADMIN),
                    MenuOption("Narrativa", "admin:narrative", "📖", "Configuración de narrativa", UserRole.ADMIN),
                    MenuOption("Configuración", "admin:settings", "⚙️", "Configuración general del bot", UserRole.ADMIN)
                ]
            ),
            
            # ============================================
            # SUBMENÚ CANAL VIP
            # ============================================
            "channel_vip": MenuConfig(
                title="💎 Configuración Canal VIP",
                description="Administra tu canal VIP desde este menú.",
                options=[
                    MenuOption("Configurar Canal", "vip:configure", "⚙️", "Configurar canal VIP", UserRole.ADMIN),
                    MenuOption("Gestionar Miembros", "vip:members", "👥", "Gestión de miembros VIP", UserRole.ADMIN),
                    MenuOption("Contenido Programado", "vip:content", "📅", "Programar contenido", UserRole.ADMIN),
                    MenuOption("Estadísticas", "vip:stats", "📊", "Ver estadísticas del canal", UserRole.ADMIN),
                    MenuOption("Configuración Acceso", "vip:access", "🔐", "Configurar accesos", UserRole.ADMIN),
                    MenuOption("Volver", "admin:main", "🔙", "Volver al menú principal", UserRole.ADMIN)
                ],
                back_menu="main_admin"
            ),
            
            # ============================================
            # SUBMENÚ CANAL FREE
            # ============================================
            "channel_free": MenuConfig(
                title="🆓 Configuración Canal Free",
                description="Administra tu canal gratuito desde este menú.",
                options=[
                    MenuOption("Configurar Canal", "free:configure", "⚙️", "Configurar canal Free", UserRole.ADMIN),
                    MenuOption("Gestionar Miembros", "free:members", "👥", "Gestión de miembros Free", UserRole.ADMIN),
                    MenuOption("Contenido Programado", "free:content", "📅", "Programar contenido", UserRole.ADMIN),
                    MenuOption("Estadísticas", "free:stats", "📊", "Ver estadísticas del canal", UserRole.ADMIN),
                    MenuOption("Moderación Auto", "free:moderation", "🤖", "Moderación automática", UserRole.ADMIN),
                    MenuOption("Volver", "admin:main", "🔙", "Volver al menú principal", UserRole.ADMIN)
                ],
                back_menu="main_admin"
            ),
            
            # ============================================
            # SUBMENÚ GAMIFICACIÓN
            # ============================================
            "gamification": MenuConfig(
                title="🎮 Configuración Juego el Diván",
                description="Administra el sistema de gamificación del bot.",
                options=[
                    MenuOption("Configurar Misiones", "game:missions", "🎯", "Gestionar misiones", UserRole.ADMIN),
                    MenuOption("Sistema de Puntos", "game:points", "🎆", "Configurar puntos", UserRole.ADMIN),
                    MenuOption("Recompensas", "game:rewards", "🏆", "Gestionar recompensas", UserRole.ADMIN),
                    MenuOption("Ranking", "game:ranking", "🏅", "Ver rankings", UserRole.ADMIN),
                    MenuOption("Eventos", "game:events", "🎉", "Eventos especiales", UserRole.ADMIN),
                    MenuOption("Volver", "admin:main", "🔙", "Volver al menú principal", UserRole.ADMIN)
                ],
                back_menu="main_admin"
            ),
            
            # ============================================
            # SUBMENÚ NARRATIVA
            # ============================================
            "narrative": MenuConfig(
                title="📖 Configuración de Narrativa",
                description="Administra el sistema narrativo del bot.",
                options=[
                    MenuOption("Configurar Historias", "narrative:stories", "📜", "Gestionar historias", UserRole.ADMIN),
                    MenuOption("Personajes", "narrative:characters", "👥", "Administrar personajes", UserRole.ADMIN),
                    MenuOption("Progreso", "narrative:progress", "📋", "Ver progreso narrativo", UserRole.ADMIN),
                    MenuOption("Integración Diana", "narrative:diana", "🤖", "Configurar Diana IA", UserRole.ADMIN),
                    MenuOption("Contenido Adaptativo", "narrative:adaptive", "🎭", "Contenido dinámico", UserRole.ADMIN),
                    MenuOption("Volver", "admin:main", "🔙", "Volver al menú principal", UserRole.ADMIN)
                ],
                back_menu="main_admin"
            ),
            
            # ============================================
            # SUBMENÚ CONFIGURACIÓN
            # ============================================
            "settings": MenuConfig(
                title="⚙️ Configuración General",
                description="Ajustes generales del bot y sistema.",
                options=[
                    MenuOption("Configuración Bot", "settings:bot", "🔧", "Parámetros del bot", UserRole.ADMIN),
                    MenuOption("Gestión Usuarios", "settings:users", "👑", "Administrar usuarios", UserRole.ADMIN),
                    MenuOption("Tarifas y Tokens", "settings:tariffs", "🏷️", "Gestionar tarifas", UserRole.ADMIN),
                    MenuOption("Notificaciones", "settings:notifications", "💌", "Configurar avisos", UserRole.ADMIN),
                    MenuOption("Mantenimiento", "settings:maintenance", "🔄", "Tareas de mantenimiento", UserRole.ADMIN),
                    MenuOption("Volver", "admin:main", "🔙", "Volver al menú principal", UserRole.ADMIN)
                ],
                back_menu="main_admin"
            )
        }
    
    # ============================================
    # OBTENER NOMBRES DE CANALES
    # ============================================
    
    async def get_channel_name(self, channel_type: str) -> str:
        """Obtiene el nombre del canal VIP o Free configurado."""
        try:
            session = next(get_session())
            channel = session.query(Channel).filter(
                Channel.type == channel_type,
                Channel.is_active == True
            ).first()
            
            if channel:
                return channel.name
            else:
                return "Canal VIP" if channel_type == "vip" else "Canal Free"
        except Exception:
            return "Canal VIP" if channel_type == "vip" else "Canal Free"
        finally:
            if 'session' in locals():
                session.close()
    
    # ============================================
    # ACTUALIZAR NOMBRES DE CANALES EN MENÚ
    # ============================================
    
    async def update_channel_names(self):
        """Actualiza los nombres de canales en el menú principal"""
        try:
            vip_name = await self.get_channel_name("vip")
            free_name = await self.get_channel_name("free")
            
            # Actualizar opciones del menú principal
            main_menu = self.menus["main_admin"]
            for option in main_menu.options:
                if option.callback == "admin:channel_vip":
                    option.text = vip_name
                elif option.callback == "admin:channel_free":
                    option.text = free_name
        except Exception as e:
            log.error("Error actualizando nombres de canales", error=e)
    
    # ============================================
    # MOSTRAR MENÚ
    # ============================================
    
    async def show_menu(self, callback: CallbackQuery, menu_name: str, user_role: UserRole = UserRole.ADMIN) -> None:
        """
        Muestra un menú editando el mensaje actual (navegación lineal)
        """
        try:
            # Actualizar nombres de canales si es el menú principal
            if menu_name == "main_admin":
                await self.update_channel_names()
            
            menu_config = self.menus.get(menu_name)
            if not menu_config:
                log.error(f"Menú no encontrado: {menu_name}")
                await callback.answer("❌ Menú no encontrado", show_alert=True)
                return
            
            user_id = callback.from_user.id
            
            log.user_action(
                f"Navegando a menú: {menu_name}",
                user_id=user_id,
                action="admin_menu_navigation"
            )
            
            # Filtrar opciones según rol del usuario
            available_options = [
                option for option in menu_config.options
                if self._user_has_access(user_role, option.required_role)
            ]
            
            # Crear texto del menú
            menu_text = self._build_menu_text(menu_config, available_options, user_role)
            
            # Crear teclado
            keyboard = self._build_keyboard(available_options, menu_name)
            
            # Editar mensaje existente
            await callback.message.edit_text(
                text=menu_text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            await callback.answer()
                
        except Exception as e:
            log.error(f"Error mostrando menú {menu_name}", error=e)
            await callback.answer("❌ Error mostrando menú", show_alert=True)
    
    # ============================================
    # CONSTRUCCIÓN DE MENÚS
    # ============================================
    
    def _build_menu_text(self, menu_config: MenuConfig, options: List[MenuOption], 
                        user_role: UserRole) -> str:
        """Construir texto del menú con formato simple para menú principal"""
        
        # Para el menú principal, usar formato simplificado
        if any(opt.callback == "admin:channel_vip" for opt in options):
            return f"<b>{menu_config.title}</b>\n\n{menu_config.description}"
        else:
            # Para submenús, formato más detallado
            lines = [
                f"<b>{menu_config.title}</b>",
                f"<i>{menu_config.description}</i>",
                "",
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                ""
            ]
            
            for option in options:
                if not option.callback.startswith(('admin:main', 'back_')):
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
    
    def _build_keyboard(self, options: List[MenuOption], menu_name: str) -> InlineKeyboardMarkup:
        """Construir teclado inline con disposición 2x3 para menú principal"""
        
        keyboard = []
        
        # Para el menú principal admin, usar estructura 2x3 específica
        if menu_name == "main_admin" and len(options) == 5:
            # Estructura 2x3 específica para menú principal
            vip_opt = next((opt for opt in options if opt.callback == "admin:channel_vip"), None)
            free_opt = next((opt for opt in options if opt.callback == "admin:channel_free"), None)
            game_opt = next((opt for opt in options if opt.callback == "admin:gamification"), None)
            narrative_opt = next((opt for opt in options if opt.callback == "admin:narrative"), None)
            config_opt = next((opt for opt in options if opt.callback == "admin:settings"), None)
            
            if all([vip_opt, free_opt, game_opt, narrative_opt, config_opt]):
                # Fila 1: Canal VIP | Canal Free
                keyboard.append([
                    InlineKeyboardButton(text=f"{vip_opt.icon} {vip_opt.text}", callback_data=vip_opt.callback),
                    InlineKeyboardButton(text=f"{free_opt.icon} {free_opt.text}", callback_data=free_opt.callback)
                ])
                
                # Fila 2: Juego el Diván | Narrativa  
                keyboard.append([
                    InlineKeyboardButton(text=f"{game_opt.icon} {game_opt.text}", callback_data=game_opt.callback),
                    InlineKeyboardButton(text=f"{narrative_opt.icon} {narrative_opt.text}", callback_data=narrative_opt.callback)
                ])
                
                # Fila 3: Configuración (centrado)
                keyboard.append([
                    InlineKeyboardButton(text=f"{config_opt.icon} {config_opt.text}", callback_data=config_opt.callback)
                ])
                
                return InlineKeyboardMarkup(inline_keyboard=keyboard)
        
        # Para otros menús, disposición estándar (máximo 2 por fila)
        main_options = [opt for opt in options if not opt.callback.startswith(('admin:main', 'back_'))]
        
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
        
        # Fila de navegación (volver)
        nav_row = []
        for option in options:
            if option.callback.startswith(('admin:main', 'back_')):
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

# ============================================
# INSTANCIA GLOBAL
# ============================================

admin_menu_system = AdminMenuSystem()

# ============================================
# FUNCIONES PARA OBTENER TECLADOS
# ============================================

async def get_admin_main_keyboard() -> InlineKeyboardMarkup:
    """Devuelve el teclado principal del panel de administración con estructura 2x3."""
    
    # Obtener nombres de canales dinámicamente
    vip_channel_name = await admin_menu_system.get_channel_name("vip")
    free_channel_name = await admin_menu_system.get_channel_name("free")
    
    buttons = [
        [
            InlineKeyboardButton(text=f"💎 {vip_channel_name}", callback_data="admin:channel_vip"),
            InlineKeyboardButton(text=f"🆓 {free_channel_name}", callback_data="admin:channel_free")
        ],
        [
            InlineKeyboardButton(text="🎮 Juego el Diván", callback_data="admin:gamification"),
            InlineKeyboardButton(text="📖 Narrativa", callback_data="admin:narrative")
        ],
        [
            InlineKeyboardButton(text="⚙️ Configuración", callback_data="admin:settings")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Funciones de compatibilidad con el sistema existente
def get_admin_stats_keyboard() -> InlineKeyboardMarkup:
    """Devuelve el teclado de estadísticas del administrador."""
    buttons = [
        [InlineKeyboardButton(text="👥 Usuarios Activos", callback_data="stats:users")],
        [InlineKeyboardButton(text="💎 Conversiones VIP", callback_data="stats:conversions")],
        [InlineKeyboardButton(text="📖 Engagement Narrativo", callback_data="stats:narrative")],
        [InlineKeyboardButton(text="🎮 Gamificación", callback_data="stats:gamification")],
        [InlineKeyboardButton(text="🔄 Resumen General", callback_data="stats:general")],
        [InlineKeyboardButton(text="🔙 Volver", callback_data="admin:main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_admin_settings_keyboard() -> InlineKeyboardMarkup:
    """Devuelve el teclado de configuración del administrador."""
    buttons = [
        [InlineKeyboardButton(text="💬 Mensajes Auto", callback_data="settings:auto_messages")],
        [InlineKeyboardButton(text="⏰ Timeouts", callback_data="settings:timeouts")],
        [InlineKeyboardButton(text="📺 Canales", callback_data="settings:channels")],
        [InlineKeyboardButton(text="🎯 Gamificación", callback_data="settings:gamification")],
        [InlineKeyboardButton(text="🔧 Sistema", callback_data="settings:system")],
        [InlineKeyboardButton(text="🔙 Volver", callback_data="admin:main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_admin_roles_keyboard() -> InlineKeyboardMarkup:
    """Devuelve el teclado de gestión de roles."""
    buttons = [
        [InlineKeyboardButton(text="👤 Buscar Usuario", callback_data="roles:search")],
        [InlineKeyboardButton(text="👑 Listar Admins", callback_data="roles:list_admins")],
        [InlineKeyboardButton(text="💎 Listar VIPs", callback_data="roles:list_vips")],
        [InlineKeyboardButton(text="📊 Estadísticas Roles", callback_data="roles:stats")],
        [InlineKeyboardButton(text="🔧 Mantenimiento", callback_data="roles:maintenance")],
        [InlineKeyboardButton(text="🔙 Volver", callback_data="admin:main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)