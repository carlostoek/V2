# diana_admin_epic_menu.py
"""
🧩 Sistema de Menú Administrativo Épico para Diana Bot V2
🛠️ Panel del Oráculo - Controla todos los hilos del multiverso
"""

import asyncio
import html
import time
import math
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum

from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardButton, 
    InlineKeyboardMarkup, User
)
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramBadRequest

import logging
logger = logging.getLogger(__name__)

# ============================================
# CALLBACK DATA FACTORIES
# ============================================

class AdminMenuCallback(CallbackData, prefix="admin_menu"):
    """Navegación entre módulos principales"""
    module: str
    action: str = "main"
    page: int = 1

class AdminActionCallback(CallbackData, prefix="admin_action"):
    """Acciones específicas dentro de módulos"""
    module: str
    action: str
    target_id: Optional[str] = None
    extra: Optional[str] = None
    page: int = 1

class AdminCRUDCallback(CallbackData, prefix="admin_crud"):
    """Operaciones CRUD estándar"""
    module: str
    operation: str  # create, read, update, delete
    item_id: Optional[str] = None
    page: int = 1

# ============================================
# ENUMS Y CONSTANTES
# ============================================

class UserRole(Enum):
    ADMIN = "admin"
    VIP = "vip"
    FREE = "free"

class AdminModule(Enum):
    NARRATIVE = "narrative"
    GAMIFICATION = "gamification"
    USERS = "users"
    CHANNELS = "channels"
    SHOP = "shop"
    CONFIG = "config"
    STATS = "stats"
    DEVTOOLS = "devtools"

# Iconos y títulos para cada módulo
MODULE_CONFIG = {
    AdminModule.NARRATIVE: {
        "icon": "📜",
        "title": "NARRATIVA",
        "subtitle": "Controla los hilos del multiverso",
        "color": "🌌"
    },
    AdminModule.GAMIFICATION: {
        "icon": "🎮",
        "title": "GAMIFICACIÓN", 
        "subtitle": "Porque sin juego, no hay deseo",
        "color": "🎯"
    },
    AdminModule.USERS: {
        "icon": "🧑‍🚀",
        "title": "USUARIOS",
        "subtitle": "Quién es quién en este teatro cósmico",
        "color": "👥"
    },
    AdminModule.CHANNELS: {
        "icon": "📺",
        "title": "CANALES",
        "subtitle": "Gestiona los portales de entrada",
        "color": "🌐"
    },
    AdminModule.SHOP: {
        "icon": "🛒",
        "title": "TIENDA & SUBASTAS",
        "subtitle": "Donde los deseos toman forma",
        "color": "💎"
    },
    AdminModule.CONFIG: {
        "icon": "⚙️",
        "title": "CONFIGURACIÓN",
        "subtitle": "Detrás del telón",
        "color": "🔧"
    },
    AdminModule.STATS: {
        "icon": "📊",
        "title": "ESTADÍSTICAS",
        "subtitle": "Los números también cuentan historias",
        "color": "📈"
    },
    AdminModule.DEVTOOLS: {
        "icon": "🧩",
        "title": "DEVTOOLS",
        "subtitle": "Para los guardianes del código",
        "color": "⚡"
    }
}

# ============================================
# SISTEMA PRINCIPAL DEL MENÚ ÉPICO
# ============================================

class DianaEpicAdminMenu:
    """
    🛠️ Panel del Oráculo - Sistema de administración épico
    """
    
    def __init__(self, bot: Bot, services: Dict[str, Any] = None):
        self.bot = bot
        self.services = services or {}
        self.page_size = 10  # Elementos por página
        
    # ============================================
    # MENÚ PRINCIPAL - PANEL DEL ORÁCULO
    # ============================================
    
    async def show_main_panel(self, message_or_query: Union[Message, CallbackQuery]) -> None:
        """Mostrar el Panel del Oráculo principal"""
        
        try:
            # Obtener estadísticas generales
            stats = await self._get_general_stats()
            
            # Construir texto épico
            text = self._build_main_panel_text(stats)
            
            # Construir teclado principal
            keyboard = self._build_main_panel_keyboard()
            
            # Mostrar menú
            await self._edit_or_send_message(
                message_or_query, 
                text, 
                keyboard
            )
            
        except Exception as e:
            logger.error(f"Error mostrando panel principal: {e}")
            await self._handle_error(message_or_query, "Error cargando Panel del Oráculo")
    
    def _build_main_panel_text(self, stats: Dict) -> str:
        """Construir texto épico del panel principal"""
        
        current_time = datetime.now().strftime("%H:%M:%S")
        
        text = f"""
🛠️ <b>PANEL DEL ORÁCULO</b> ⚡

<i>"Desde aquí se tejen los destinos del multiverso"</i>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 <b>ESTADO DEL UNIVERSO:</b>
🌌 Usuarios activos: <b>{stats.get('active_users', 0)}</b>
💎 Usuarios VIP: <b>{stats.get('vip_users', 0)}</b>
📖 En narrativa: <b>{stats.get('users_in_story', 0)}</b>
🎮 Misiones activas: <b>{stats.get('active_missions', 0)}</b>
📺 Canales sincronizados: <b>{stats.get('channels', 0)}</b>

⚡ <b>Última sincronización:</b> {current_time}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>Selecciona un módulo para administrar:</b>
        """
        
        return text.strip()
    
    def _build_main_panel_keyboard(self) -> InlineKeyboardMarkup:
        """Construir teclado del panel principal en grid 2x4"""
        
        builder = InlineKeyboardBuilder()
        
        # Organizar módulos en grid 2x4
        modules = [
            (AdminModule.NARRATIVE, AdminModule.GAMIFICATION),
            (AdminModule.USERS, AdminModule.CHANNELS),
            (AdminModule.SHOP, AdminModule.CONFIG),
            (AdminModule.STATS, AdminModule.DEVTOOLS)
        ]
        
        for row in modules:
            row_buttons = []
            for module in row:
                config = MODULE_CONFIG[module]
                row_buttons.append(InlineKeyboardButton(
                    text=f"{config['icon']} {config['title']}",
                    callback_data=AdminMenuCallback(
                        module=module.value,
                        action="main"
                    ).pack()
                ))
            builder.row(*row_buttons)
        
        # Fila de utilidades
        builder.row(
            InlineKeyboardButton(
                text="🔄 Actualizar",
                callback_data=AdminMenuCallback(module="main", action="refresh").pack()
            ),
            InlineKeyboardButton(
                text="❌ Cerrar",
                callback_data=AdminMenuCallback(module="main", action="close").pack()
            )
        )
        
        return builder.as_markup()
    
    # ============================================
    # MÓDULO NARRATIVA
    # ============================================
    
    async def show_narrative_module(self, query: CallbackQuery, action: str = "main", page: int = 1) -> None:
        """Módulo de gestión narrativa"""
        
        config = MODULE_CONFIG[AdminModule.NARRATIVE]
        
        if action == "main":
            text = f"""
{config['color']} <b>{config['title']}</b>

<i>"{config['subtitle']}"</i>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 <b>ESTADO NARRATIVO:</b>
📝 Fragmentos totales: <b>25</b>
🔓 Fragmentos activos: <b>18</b>
🔒 Fragmentos bloqueados: <b>7</b>
🧠 Estados narrativos: <b>42 usuarios</b>
🎭 Escenas secretas: <b>3</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>Gestión del Multiverso Narrativo:</b>
            """
            
            keyboard = InlineKeyboardBuilder()
            
            # Opciones principales
            narrative_options = [
                ("✏️ Fragmentos", "fragments"),
                ("🧠 Estados", "states"),
                ("🔍 Vista Previa", "preview"),
                ("🚪 Entradas Secretas", "secrets"),
                ("🔗 Conexiones", "connections"),
                ("📊 Estadísticas", "stats")
            ]
            
            # Organizar en 2 columnas
            for i in range(0, len(narrative_options), 2):
                row_buttons = []
                for j in range(2):
                    if i + j < len(narrative_options):
                        option = narrative_options[i + j]
                        row_buttons.append(InlineKeyboardButton(
                            text=option[0],
                            callback_data=AdminMenuCallback(
                                module="narrative",
                                action=option[1]
                            ).pack()
                        ))
                keyboard.row(*row_buttons)
        
        elif action == "fragments":
            fragments = await self._get_narrative_fragments(page)
            text = self._build_fragments_list(fragments, page)
            keyboard = self._build_fragments_keyboard(fragments, page)
            
        elif action == "states":
            states = await self._get_narrative_states(page)
            text = self._build_states_list(states, page)
            keyboard = self._build_states_keyboard(states, page)
            
        else:
            text = f"{config['icon']} Función '{action}' en desarrollo..."
            keyboard = self._build_back_keyboard("narrative")
        
        # Agregar botón de volver
        keyboard.row(
            InlineKeyboardButton(
                text="◀️ Panel Principal",
                callback_data=AdminMenuCallback(module="main").pack()
            )
        )
        
        await self._edit_message(query, text, keyboard.as_markup())
    
    # ============================================
    # MÓDULO GAMIFICACIÓN
    # ============================================
    
    async def show_gamification_module(self, query: CallbackQuery, action: str = "main", page: int = 1) -> None:
        """Módulo de gamificación"""
        
        config = MODULE_CONFIG[AdminModule.GAMIFICATION]
        
        if action == "main":
            text = f"""
{config['color']} <b>{config['title']}</b>

<i>"{config['subtitle']}"</i>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 <b>ESTADO DEL JUEGO:</b>
🏅 Logros disponibles: <b>15</b>
💥 Misiones activas: <b>8</b>
🎭 Arquetipos únicos: <b>6</b>
🎰 Trivias diarias: <b>12</b>
🪙 Tokens circulando: <b>1,247</b>
🎁 Regalos reclamados hoy: <b>89</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>Centro de Control del Juego:</b>
            """
            
            keyboard = InlineKeyboardBuilder()
            
            gamification_options = [
                ("🏅 Logros", "achievements"),
                ("💥 Misiones", "missions"), 
                ("🎭 Arquetipos", "archetypes"),
                ("🎰 Trivias", "trivia"),
                ("🪙 Tokens", "tokens"),
                ("🎁 Recompensas", "rewards")
            ]
            
            for i in range(0, len(gamification_options), 2):
                row_buttons = []
                for j in range(2):
                    if i + j < len(gamification_options):
                        option = gamification_options[i + j]
                        row_buttons.append(InlineKeyboardButton(
                            text=option[0],
                            callback_data=AdminMenuCallback(
                                module="gamification",
                                action=option[1]
                            ).pack()
                        ))
                keyboard.row(*row_buttons)
        
        elif action == "missions":
            missions = await self._get_missions(page)
            text = self._build_missions_list(missions, page)
            keyboard = self._build_missions_keyboard(missions, page)
            
        elif action == "achievements":
            achievements = await self._get_achievements(page)
            text = self._build_achievements_list(achievements, page)
            keyboard = self._build_achievements_keyboard(achievements, page)
            
        else:
            text = f"{config['icon']} Función '{action}' en desarrollo..."
            keyboard = self._build_back_keyboard("gamification")
        
        keyboard.row(
            InlineKeyboardButton(
                text="◀️ Panel Principal",
                callback_data=AdminMenuCallback(module="main").pack()
            )
        )
        
        await self._edit_message(query, text, keyboard.as_markup())
    
    # ============================================
    # MÓDULO USUARIOS
    # ============================================
    
    async def show_users_module(self, query: CallbackQuery, action: str = "main", page: int = 1) -> None:
        """Módulo de gestión de usuarios"""
        
        config = MODULE_CONFIG[AdminModule.USERS]
        
        if action == "main":
            text = f"""
{config['color']} <b>{config['title']}</b>

<i>"{config['subtitle']}"</i>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👥 <b>DEMOGRAFÍA DEL UNIVERSO:</b>
🧑‍🚀 Usuarios totales: <b>247</b>
💎 VIP activos: <b>23</b>
🆓 Free users: <b>224</b>
📈 Nuevos hoy: <b>5</b>
⏳ Últimos 7 días: <b>28</b>
🚫 Sancionados: <b>2</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>Teatro Cósmico de Usuarios:</b>
            """
            
            keyboard = InlineKeyboardBuilder()
            
            user_options = [
                ("🔍 Buscar", "search"),
                ("📄 Historial", "history"),
                ("📈 Progreso", "progress"),
                ("🏷️ Roles", "roles"),
                ("⚠️ Sanciones", "sanctions"),
                ("🔓 Forzar VIP", "force_vip")
            ]
            
            for i in range(0, len(user_options), 2):
                row_buttons = []
                for j in range(2):
                    if i + j < len(user_options):
                        option = user_options[i + j]
                        row_buttons.append(InlineKeyboardButton(
                            text=option[0],
                            callback_data=AdminMenuCallback(
                                module="users",
                                action=option[1]
                            ).pack()
                        ))
                keyboard.row(*row_buttons)
        
        elif action == "search":
            text = self._build_user_search_text()
            keyboard = self._build_user_search_keyboard()
            
        elif action == "roles":
            users = await self._get_users_by_role(page)
            text = self._build_users_roles_list(users, page)
            keyboard = self._build_users_roles_keyboard(users, page)
            
        else:
            text = f"{config['icon']} Función '{action}' en desarrollo..."
            keyboard = self._build_back_keyboard("users")
        
        keyboard.row(
            InlineKeyboardButton(
                text="◀️ Panel Principal",
                callback_data=AdminMenuCallback(module="main").pack()
            )
        )
        
        await self._edit_message(query, text, keyboard.as_markup())
    
    # ============================================
    # MÓDULO CANALES
    # ============================================
    
    async def show_channels_module(self, query: CallbackQuery, action: str = "main", page: int = 1) -> None:
        """Módulo de gestión de canales"""
        
        config = MODULE_CONFIG[AdminModule.CHANNELS]
        
        if action == "main":
            text = f"""
{config['color']} <b>{config['title']}</b>

<i>"{config['subtitle']}"</i>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌐 <b>PORTALES DIMENSIONALES:</b>
📺 Canales activos: <b>3</b>
🔐 Canal VIP: <b>@DianaVIP</b>
🆓 Canal Free: <b>@DianaFree</b>
📢 Canal Anuncios: <b>@DianaNews</b>
📌 Mensajes anclados: <b>5</b>
💬 Comentarios habilitados: <b>2/3</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>Control de Portales:</b>
            """
            
            keyboard = InlineKeyboardBuilder()
            
            channel_options = [
                ("🔄 Sincronizar", "sync"),
                ("🏷️ Renombrar", "rename"),
                ("📍 Anclar", "pin"),
                ("💬 Comentarios", "comments"),
                ("🔐 Config VIP", "vip_config"),
                ("📦 Importar", "import")
            ]
            
            for i in range(0, len(channel_options), 2):
                row_buttons = []
                for j in range(2):
                    if i + j < len(channel_options):
                        option = channel_options[i + j]
                        row_buttons.append(InlineKeyboardButton(
                            text=option[0],
                            callback_data=AdminMenuCallback(
                                module="channels",
                                action=option[1]
                            ).pack()
                        ))
                keyboard.row(*row_buttons)
        
        else:
            text = f"{config['icon']} Función '{action}' en desarrollo..."
            keyboard = self._build_back_keyboard("channels")
        
        keyboard.row(
            InlineKeyboardButton(
                text="◀️ Panel Principal",
                callback_data=AdminMenuCallback(module="main").pack()
            )
        )
        
        await self._edit_message(query, text, keyboard.as_markup())
    
    # ============================================
    # MÓDULO TIENDA & SUBASTAS
    # ============================================
    
    async def show_shop_module(self, query: CallbackQuery, action: str = "main", page: int = 1) -> None:
        """Módulo de tienda y subastas"""
        
        config = MODULE_CONFIG[AdminModule.SHOP]
        
        if action == "main":
            text = f"""
{config['color']} <b>{config['title']}</b>

<i>"{config['subtitle']}"</i>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💎 <b>ECONOMÍA DEL DESEO:</b>
📦 Ítems en catálogo: <b>42</b>
⏳ Subastas activas: <b>3</b>
🔁 Ventas hoy: <b>15</b>
💸 Ingresos besitos: <b>2,847</b>
🏆 Ítem más vendido: <b>"Susurro de Diana"</b>
📈 Precio dinámico: <b>Activado</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>Centro Comercial Multiversal:</b>
            """
            
            keyboard = InlineKeyboardBuilder()
            
            shop_options = [
                ("📦 Crear Ítem", "create_item"),
                ("🧾 Catálogo", "catalog"),
                ("⏳ Subastas", "auctions"),
                ("🔁 Historial", "history"),
                ("🗃️ Almacén", "storage"),
                ("💸 Precios", "pricing")
            ]
            
            for i in range(0, len(shop_options), 2):
                row_buttons = []
                for j in range(2):
                    if i + j < len(shop_options):
                        option = shop_options[i + j]
                        row_buttons.append(InlineKeyboardButton(
                            text=option[0],
                            callback_data=AdminMenuCallback(
                                module="shop",
                                action=option[1]
                            ).pack()
                        ))
                keyboard.row(*row_buttons)
        
        elif action == "catalog":
            items = await self._get_shop_items(page)
            text = self._build_shop_catalog(items, page)
            keyboard = self._build_shop_catalog_keyboard(items, page)
            
        else:
            text = f"{config['icon']} Función '{action}' en desarrollo..."
            keyboard = self._build_back_keyboard("shop")
        
        keyboard.row(
            InlineKeyboardButton(
                text="◀️ Panel Principal",
                callback_data=AdminMenuCallback(module="main").pack()
            )
        )
        
        await self._edit_message(query, text, keyboard.as_markup())
    
    # ============================================
    # MÓDULO CONFIGURACIÓN
    # ============================================
    
    async def show_config_module(self, query: CallbackQuery, action: str = "main", page: int = 1) -> None:
        """Módulo de configuración del sistema"""
        
        config = MODULE_CONFIG[AdminModule.CONFIG]
        
        if action == "main":
            text = f"""
{config['color']} <b>{config['title']}</b>

<i>"{config['subtitle']}"</i>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔧 <b>ENGRANAJES DEL UNIVERSO:</b>
🕹️ APIs conectadas: <b>5/5</b>
📂 Variables activas: <b>23</b>
🛡️ Nivel seguridad: <b>Alto</b>
📡 Webhooks: <b>3 activos</b>
📬 Notificaciones: <b>Activadas</b>
📅 Cron jobs: <b>7 programados</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>Sala de Máquinas:</b>
            """
            
            keyboard = InlineKeyboardBuilder()
            
            config_options = [
                ("🕹️ APIs", "apis"),
                ("📂 Variables", "variables"),
                ("🛡️ Seguridad", "security"),
                ("📡 Webhooks", "webhooks"),
                ("📬 Notificaciones", "notifications"),
                ("📅 Cron Jobs", "cron"),
                ("🧪 Experimental", "experimental")
            ]
            
            for i in range(0, len(config_options), 2):
                row_buttons = []
                for j in range(2):
                    if i + j < len(config_options):
                        option = config_options[i + j]
                        row_buttons.append(InlineKeyboardButton(
                            text=option[0],
                            callback_data=AdminMenuCallback(
                                module="config",
                                action=option[1]
                            ).pack()
                        ))
                keyboard.row(*row_buttons)
        
        else:
            text = f"{config['icon']} Función '{action}' en desarrollo..."
            keyboard = self._build_back_keyboard("config")
        
        keyboard.row(
            InlineKeyboardButton(
                text="◀️ Panel Principal",
                callback_data=AdminMenuCallback(module="main").pack()
            )
        )
        
        await self._edit_message(query, text, keyboard.as_markup())
    
    # ============================================
    # MÓDULO ESTADÍSTICAS
    # ============================================
    
    async def show_stats_module(self, query: CallbackQuery, action: str = "main", page: int = 1) -> None:
        """Módulo de estadísticas avanzadas"""
        
        config = MODULE_CONFIG[AdminModule.STATS]
        
        if action == "main":
            text = f"""
{config['color']} <b>{config['title']}</b>

<i>"{config['subtitle']}"</i>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 <b>PULSO DEL MULTIVERSO:</b>
👤 Usuarios activos (24h): <b>89</b>
⏳ Tiempo promedio narrativa: <b>45min</b>
🔁 Ciclos completados: <b>156</b>
💬 Reacciones por canal: <b>1,247</b>
💥 Misión más jugada: <b>"Primer Encuentro"</b>
📉 Drop usuarios escena 3: <b>12%</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>Observatorio de Datos:</b>
            """
            
            keyboard = InlineKeyboardBuilder()
            
            stats_options = [
                ("👤 Usuarios", "users_stats"),
                ("⏳ Narrativa", "narrative_stats"),
                ("🔁 Engagement", "engagement"),
                ("💬 Canales", "channels_stats"),
                ("💥 Misiones", "missions_stats"),
                ("📉 Drop Rates", "drop_rates"),
                ("📊 Dashboard", "dashboard"),
                ("📈 Reportes", "reports")
            ]
            
            for i in range(0, len(stats_options), 2):
                row_buttons = []
                for j in range(2):
                    if i + j < len(stats_options):
                        option = stats_options[i + j]
                        row_buttons.append(InlineKeyboardButton(
                            text=option[0],
                            callback_data=AdminMenuCallback(
                                module="stats",
                                action=option[1]
                            ).pack()
                        ))
                keyboard.row(*row_buttons)
        
        else:
            text = f"{config['icon']} Función '{action}' en desarrollo..."
            keyboard = self._build_back_keyboard("stats")
        
        keyboard.row(
            InlineKeyboardButton(
                text="◀️ Panel Principal",
                callback_data=AdminMenuCallback(module="main").pack()
            )
        )
        
        await self._edit_message(query, text, keyboard.as_markup())
    
    # ============================================
    # MÓDULO DEVTOOLS
    # ============================================
    
    async def show_devtools_module(self, query: CallbackQuery, action: str = "main", page: int = 1) -> None:
        """Módulo de herramientas de desarrollo"""
        
        config = MODULE_CONFIG[AdminModule.DEVTOOLS]
        
        if action == "main":
            text = f"""
{config['color']} <b>{config['title']}</b>

<i>"{config['subtitle']}"</i>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚡ <b>ARSENAL DEL DESARROLLADOR:</b>
🔧 Última build: <b>v2.1.5</b>
📦 Base de datos: <b>247 registros</b>
🧪 Tests pasados: <b>89/92</b>
🪛 Componentes UI: <b>15 activos</b>
🔍 Errores últimas 24h: <b>3</b>
👁️ Modo dios: <b>Desactivado</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>Laboratorio de Código:</b>
            """
            
            keyboard = InlineKeyboardBuilder()
            
            dev_options = [
                ("🔧 Editar Mensajes", "edit_messages"),
                ("📦 Dump DB", "dump_db"),
                ("🧪 Forzar Eventos", "force_events"),
                ("🪛 Test UI", "test_ui"),
                ("🔍 Error Logs", "error_logs"),
                ("👁️ Modo Dios", "god_mode")
            ]
            
            for i in range(0, len(dev_options), 2):
                row_buttons = []
                for j in range(2):
                    if i + j < len(dev_options):
                        option = dev_options[i + j]
                        row_buttons.append(InlineKeyboardButton(
                            text=option[0],
                            callback_data=AdminMenuCallback(
                                module="devtools",
                                action=option[1]
                            ).pack()
                        ))
                keyboard.row(*row_buttons)
        
        else:
            text = f"{config['icon']} Función '{action}' en desarrollo..."
            keyboard = self._build_back_keyboard("devtools")
        
        keyboard.row(
            InlineKeyboardButton(
                text="◀️ Panel Principal",
                callback_data=AdminMenuCallback(module="main").pack()
            )
        )
        
        await self._edit_message(query, text, keyboard.as_markup())
    
    # ============================================
    # SISTEMA CRUD UNIVERSAL
    # ============================================
    
    def _build_crud_keyboard(self, module: str, items: List, page: int, total_pages: int) -> InlineKeyboardBuilder:
        """Construir teclado CRUD universal con paginación"""
        
        builder = InlineKeyboardBuilder()
        
        # Botones CRUD principales
        crud_buttons = [
            ("➕ Crear", "create"),
            ("🔁 Editar", "edit"),
            ("🗑️ Eliminar", "delete"),
            ("👁️ Ver", "view")
        ]
        
        for i in range(0, len(crud_buttons), 2):
            row_buttons = []
            for j in range(2):
                if i + j < len(crud_buttons):
                    button = crud_buttons[i + j]
                    row_buttons.append(InlineKeyboardButton(
                        text=button[0],
                        callback_data=AdminCRUDCallback(
                            module=module,
                            operation=button[1],
                            page=page
                        ).pack()
                    ))
            builder.row(*row_buttons)
        
        # Paginación si hay múltiples páginas
        if total_pages > 1:
            pagination_buttons = []
            
            if page > 1:
                pagination_buttons.append(InlineKeyboardButton(
                    text="⬅️",
                    callback_data=AdminMenuCallback(
                        module=module,
                        action="main",
                        page=page-1
                    ).pack()
                ))
            
            pagination_buttons.append(InlineKeyboardButton(
                text=f"{page}/{total_pages}",
                callback_data="noop"
            ))
            
            if page < total_pages:
                pagination_buttons.append(InlineKeyboardButton(
                    text="➡️",
                    callback_data=AdminMenuCallback(
                        module=module,
                        action="main",
                        page=page+1
                    ).pack()
                ))
            
            builder.row(*pagination_buttons)
        
        return builder
    
    # ============================================
    # FUNCIONES DE DATOS (MOCK)
    # ============================================
    
    async def _get_general_stats(self) -> Dict:
        """Obtener estadísticas generales del sistema"""
        try:
            # Integrar con tus servicios reales aquí
            if self.services.get('user_service'):
                # Usar servicios reales
                user_service = self.services['user_service']
                stats = {
                    'active_users': await user_service.count_active_users(),
                    'vip_users': await user_service.count_vip_users(),
                    'users_in_story': 0,  # Implementar
                    'active_missions': 0,  # Implementar
                    'channels': 3
                }
            else:
                # Datos mock para desarrollo
                stats = {
                    'active_users': 247,
                    'vip_users': 23,
                    'users_in_story': 89,
                    'active_missions': 8,
                    'channels': 3
                }
            return stats
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {
                'active_users': 0,
                'vip_users': 0,
                'users_in_story': 0,
                'active_missions': 0,
                'channels': 0
            }
    
    async def _get_narrative_fragments(self, page: int = 1) -> Dict:
        """Obtener fragmentos narrativos con paginación"""
        try:
            # Mock data para desarrollo
            total_fragments = 25
            fragments_per_page = self.page_size
            start_idx = (page - 1) * fragments_per_page
            
            fragments = []
            for i in range(start_idx, min(start_idx + fragments_per_page, total_fragments)):
                fragments.append({
                    'id': f"frag_{i+1:03d}",
                    'title': f"Fragmento {i+1}",
                    'status': "activo" if i < 18 else "bloqueado",
                    'connections': i % 3 + 1,
                    'views': (i + 1) * 15
                })
            
            return {
                'fragments': fragments,
                'current_page': page,
                'total_pages': math.ceil(total_fragments / fragments_per_page),
                'total_items': total_fragments
            }
        except Exception as e:
            logger.error(f"Error obteniendo fragmentos: {e}")
            return {'fragments': [], 'current_page': 1, 'total_pages': 1, 'total_items': 0}
    
    async def _get_narrative_states(self, page: int = 1) -> Dict:
        """Obtener estados narrativos de usuarios"""
        try:
            # Mock data
            total_states = 42
            states_per_page = self.page_size
            start_idx = (page - 1) * states_per_page
            
            states = []
            for i in range(start_idx, min(start_idx + states_per_page, total_states)):
                states.append({
                    'user_id': 1000000 + i,
                    'username': f"user_{i+1}",
                    'current_fragment': f"frag_{(i % 25) + 1:03d}",
                    'progress': f"{(i * 7) % 100}%",
                    'decisions': i % 5 + 1
                })
            
            return {
                'states': states,
                'current_page': page,
                'total_pages': math.ceil(total_states / states_per_page),
                'total_items': total_states
            }
        except Exception as e:
            logger.error(f"Error obteniendo estados narrativos: {e}")
            return {'states': [], 'current_page': 1, 'total_pages': 1, 'total_items': 0}
    
    async def _get_missions(self, page: int = 1) -> Dict:
        """Obtener misiones activas"""
        try:
            # Mock data
            total_missions = 15
            missions_per_page = self.page_size
            start_idx = (page - 1) * missions_per_page
            
            missions = []
            mission_types = ["Diaria", "Semanal", "Especial", "VIP"]
            
            for i in range(start_idx, min(start_idx + missions_per_page, total_missions)):
                missions.append({
                    'id': f"mission_{i+1:03d}",
                    'title': f"Misión {i+1}",
                    'type': mission_types[i % len(mission_types)],
                    'active_players': (i + 1) * 12,
                    'completion_rate': f"{85 - (i * 3)}%",
                    'rewards': f"{(i + 1) * 50} besitos"
                })
            
            return {
                'missions': missions,
                'current_page': page,
                'total_pages': math.ceil(total_missions / missions_per_page),
                'total_items': total_missions
            }
        except Exception as e:
            logger.error(f"Error obteniendo misiones: {e}")
            return {'missions': [], 'current_page': 1, 'total_pages': 1, 'total_items': 0}
    
    async def _get_achievements(self, page: int = 1) -> Dict:
        """Obtener logros disponibles"""
        try:
            # Mock data
            achievements = [
                {"id": "ach_001", "name": "Primer Paso", "description": "Completa tu primera decisión", "unlocked": 200},
                {"id": "ach_002", "name": "Explorador", "description": "Visita 5 fragmentos diferentes", "unlocked": 150},
                {"id": "ach_003", "name": "Coleccionista", "description": "Obtén 10 pistas narrativas", "unlocked": 89},
                {"id": "ach_004", "name": "VIP Legend", "description": "Mantén VIP por 3 meses", "unlocked": 12},
                {"id": "ach_005", "name": "Socialite", "description": "Reacciona 100 veces en canales", "unlocked": 67}
            ]
            
            return {
                'achievements': achievements,
                'current_page': page,
                'total_pages': 1,
                'total_items': len(achievements)
            }
        except Exception as e:
            logger.error(f"Error obteniendo logros: {e}")
            return {'achievements': [], 'current_page': 1, 'total_pages': 1, 'total_items': 0}
    
    async def _get_users_by_role(self, page: int = 1) -> Dict:
        """Obtener usuarios filtrados por rol"""
        try:
            # Mock data
            users = [
                {"id": 1280444712, "username": "Corther1", "role": "admin", "last_active": "2025-08-03"},
                {"id": 1234567890, "username": "vip_user1", "role": "vip", "last_active": "2025-08-02"},
                {"id": 1234567891, "username": "vip_user2", "role": "vip", "last_active": "2025-08-01"},
                {"id": 1234567892, "username": "free_user1", "role": "free", "last_active": "2025-08-03"},
                {"id": 1234567893, "username": "free_user2", "role": "free", "last_active": "2025-07-30"}
            ]
            
            return {
                'users': users,
                'current_page': page,
                'total_pages': 1,
                'total_items': len(users)
            }
        except Exception as e:
            logger.error(f"Error obteniendo usuarios: {e}")
            return {'users': [], 'current_page': 1, 'total_pages': 1, 'total_items': 0}
    
    async def _get_shop_items(self, page: int = 1) -> Dict:
        """Obtener ítems de la tienda"""
        try:
            # Mock data
            items = [
                {"id": "item_001", "name": "Susurro de Diana", "price": 150, "rarity": "Legendario", "sales": 45},
                {"id": "item_002", "name": "Mirada Seductora", "price": 75, "rarity": "Épico", "sales": 89},
                {"id": "item_003", "name": "Toque Fantasmal", "price": 50, "rarity": "Raro", "sales": 156},
                {"id": "item_004", "name": "Secreto Íntimo", "price": 300, "rarity": "Mítico", "sales": 12},
                {"id": "item_005", "name": "Beso Etéreo", "price": 100, "rarity": "Épico", "sales": 67}
            ]
            
            return {
                'items': items,
                'current_page': page,
                'total_pages': 1,
                'total_items': len(items)
            }
        except Exception as e:
            logger.error(f"Error obteniendo ítems de tienda: {e}")
            return {'items': [], 'current_page': 1, 'total_pages': 1, 'total_items': 0}
    
    # ============================================
    # CONSTRUCTORES DE TEXTO ESPECÍFICOS
    # ============================================
    
    def _build_fragments_list(self, data: Dict, page: int) -> str:
        """Construir lista de fragmentos narrativos"""
        
        text = f"""
📜 <b>FRAGMENTOS NARRATIVOS</b>

<i>Hilos que tejen el destino</i>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 <b>Página {data['current_page']} de {data['total_pages']}</b>
📝 <b>Total de fragmentos:</b> {data['total_items']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        """
        
        for fragment in data['fragments']:
            status_icon = "🔓" if fragment['status'] == "activo" else "🔒"
            text += f"""
{status_icon} <b>{fragment['title']}</b>
   📋 ID: <code>{fragment['id']}</code>
   🔗 Conexiones: {fragment['connections']}
   👁️ Visualizaciones: {fragment['views']}
   
"""
        
        return text.strip()
    
    def _build_states_list(self, data: Dict, page: int) -> str:
        """Construir lista de estados narrativos"""
        
        text = f"""
🧠 <b>ESTADOS NARRATIVOS</b>

<i>La conciencia del multiverso</i>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 <b>Página {data['current_page']} de {data['total_pages']}</b>
👥 <b>Usuarios en narrativa:</b> {data['total_items']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        """
        
        for state in data['states']:
            text += f"""
👤 <b>@{state['username']}</b>
   🆔 ID: <code>{state['user_id']}</code>
   📍 Fragmento: {state['current_fragment']}
   📈 Progreso: {state['progress']}
   🎯 Decisiones: {state['decisions']}
   
"""
        
        return text.strip()
    
    def _build_missions_list(self, data: Dict, page: int) -> str:
        """Construir lista de misiones"""
        
        text = f"""
💥 <b>MISIONES ACTIVAS</b>

<i>Desafíos del cosmos</i>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 <b>Página {data['current_page']} de {data['total_pages']}</b>
🎯 <b>Total de misiones:</b> {data['total_items']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        """
        
        for mission in data['missions']:
            type_icon = {"Diaria": "📅", "Semanal": "📆", "Especial": "⭐", "VIP": "👑"}
            icon = type_icon.get(mission['type'], "🎯")
            
            text += f"""
{icon} <b>{mission['title']}</b>
   📋 Tipo: {mission['type']}
   👥 Jugadores activos: {mission['active_players']}
   ✅ Tasa de completado: {mission['completion_rate']}
   🎁 Recompensa: {mission['rewards']}
   
"""
        
        return text.strip()
    
    def _build_achievements_list(self, data: Dict, page: int) -> str:
        """Construir lista de logros"""
        
        text = f"""
🏅 <b>LOGROS DISPONIBLES</b>

<i>Emblemas de gloria</i>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 <b>Total de logros:</b> {data['total_items']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        """
        
        for achievement in data['achievements']:
            text += f"""
🏆 <b>{achievement['name']}</b>
   📝 {achievement['description']}
   🔓 Desbloqueado por: <b>{achievement['unlocked']} usuarios</b>
   
"""
        
        return text.strip()
    
    def _build_users_roles_list(self, data: Dict, page: int) -> str:
        """Construir lista de usuarios por roles"""
        
        text = f"""
🧑‍🚀 <b>GESTIÓN DE ROLES</b>

<i>Jerarquía del teatro cósmico</i>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 <b>Total de usuarios:</b> {data['total_items']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        """
        
        for user in data['users']:
            role_icon = {"admin": "⚡", "vip": "👑", "free": "🆓"}
            icon = role_icon.get(user['role'], "👤")
            
            text += f"""
{icon} <b>@{user['username']}</b>
   🆔 ID: <code>{user['id']}</code>
   🏷️ Rol: {user['role'].upper()}
   📅 Última actividad: {user['last_active']}
   
"""
        
        return text.strip()
    
    def _build_shop_catalog(self, data: Dict, page: int) -> str:
        """Construir catálogo de tienda"""
        
        text = f"""
🛒 <b>CATÁLOGO DE DESEOS</b>

<i>Donde los sueños toman forma</i>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 <b>Total de ítems:</b> {data['total_items']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        """
        
        for item in data['items']:
            rarity_icon = {
                "Común": "⚪", "Raro": "🔵", "Épico": "🟣", 
                "Legendario": "🟠", "Mítico": "🔴"
            }
            icon = rarity_icon.get(item['rarity'], "⚪")
            
            text += f"""
{icon} <b>{item['name']}</b>
   💰 Precio: {item['price']} besitos
   ⭐ Rareza: {item['rarity']}
   📊 Ventas: {item['sales']}
   
"""
        
        return text.strip()
    
    def _build_user_search_text(self) -> str:
        """Texto para búsqueda de usuarios"""
        return """
🔍 <b>BÚSQUEDA DE USUARIOS</b>

<i>Encuentra a cualquier habitante del multiverso</i>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔎 <b>Métodos de búsqueda:</b>
• Por ID de usuario
• Por username (@usuario)
• Por nombre completo
• Por rol (admin/vip/free)

💡 <b>Tip:</b> Usa los botones de filtro rápido
        """
    
    # ============================================
    # CONSTRUCTORES DE TECLADOS ESPECÍFICOS
    # ============================================
    
    def _build_fragments_keyboard(self, data: Dict, page: int) -> InlineKeyboardBuilder:
        """Teclado para gestión de fragmentos"""
        return self._build_crud_keyboard("narrative", data['fragments'], page, data['total_pages'])
    
    def _build_states_keyboard(self, data: Dict, page: int) -> InlineKeyboardBuilder:
        """Teclado para estados narrativos"""
        builder = InlineKeyboardBuilder()
        
        # Filtros especiales para estados
        builder.row(
            InlineKeyboardButton(
                text="🔍 Buscar Usuario",
                callback_data=AdminActionCallback(
                    module="narrative",
                    action="search_user_state"
                ).pack()
            ),
            InlineKeyboardButton(
                text="📊 Estadísticas",
                callback_data=AdminActionCallback(
                    module="narrative", 
                    action="states_stats"
                ).pack()
            )
        )
        
        # Paginación
        if data['total_pages'] > 1:
            pagination_buttons = []
            
            if page > 1:
                pagination_buttons.append(InlineKeyboardButton(
                    text="⬅️",
                    callback_data=AdminMenuCallback(
                        module="narrative",
                        action="states",
                        page=page-1
                    ).pack()
                ))
            
            pagination_buttons.append(InlineKeyboardButton(
                text=f"{page}/{data['total_pages']}",
                callback_data="noop"
            ))
            
            if page < data['total_pages']:
                pagination_buttons.append(InlineKeyboardButton(
                    text="➡️",
                    callback_data=AdminMenuCallback(
                        module="narrative",
                        action="states",
                        page=page+1
                    ).pack()
                ))
            
            builder.row(*pagination_buttons)
        
        return builder
    
    def _build_missions_keyboard(self, data: Dict, page: int) -> InlineKeyboardBuilder:
        """Teclado para gestión de misiones"""
        return self._build_crud_keyboard("gamification", data['missions'], page, data['total_pages'])
    
    def _build_achievements_keyboard(self, data: Dict, page: int) -> InlineKeyboardBuilder:
        """Teclado para gestión de logros"""
        return self._build_crud_keyboard("gamification", data['achievements'], page, data['total_pages'])
    
    def _build_users_roles_keyboard(self, data: Dict, page: int) -> InlineKeyboardBuilder:
        """Teclado para gestión de roles de usuarios"""
        builder = InlineKeyboardBuilder()
        
        # Filtros por rol
        builder.row(
            InlineKeyboardButton(
                text="⚡ Solo Admins",
                callback_data=AdminActionCallback(
                    module="users",
                    action="filter_role",
                    target_id="admin"
                ).pack()
            ),
            InlineKeyboardButton(
                text="👑 Solo VIP",
                callback_data=AdminActionCallback(
                    module="users",
                    action="filter_role",
                    target_id="vip"
                ).pack()
            ),
            InlineKeyboardButton(
                text="🆓 Solo Free",
                callback_data=AdminActionCallback(
                    module="users",
                    action="filter_role",
                    target_id="free"
                ).pack()
            )
        )
        
        # CRUD
        builder.row(
            InlineKeyboardButton(
                text="👑 Promover a VIP",
                callback_data=AdminActionCallback(
                    module="users",
                    action="promote_vip"
                ).pack()
            ),
            InlineKeyboardButton(
                text="⬇️ Degradar VIP",
                callback_data=AdminActionCallback(
                    module="users",
                    action="demote_vip"
                ).pack()
            )
        )
        
        return builder
    
    def _build_shop_catalog_keyboard(self, data: Dict, page: int) -> InlineKeyboardBuilder:
        """Teclado para catálogo de tienda"""
        return self._build_crud_keyboard("shop", data['items'], page, data['total_pages'])
    
    def _build_user_search_keyboard(self) -> InlineKeyboardBuilder:
        """Teclado para búsqueda de usuarios"""
        builder = InlineKeyboardBuilder()
        
        # Filtros rápidos
        builder.row(
            InlineKeyboardButton(
                text="⚡ Admins",
                callback_data=AdminActionCallback(
                    module="users",
                    action="quick_filter",
                    target_id="admin"
                ).pack()
            ),
            InlineKeyboardButton(
                text="👑 VIP",
                callback_data=AdminActionCallback(
                    module="users",
                    action="quick_filter",
                    target_id="vip"
                ).pack()
            ),
            InlineKeyboardButton(
                text="🆓 Free",
                callback_data=AdminActionCallback(
                    module="users",
                    action="quick_filter",
                    target_id="free"
                ).pack()
            )
        )
        
        builder.row(
            InlineKeyboardButton(
                text="📅 Activos Hoy",
                callback_data=AdminActionCallback(
                    module="users",
                    action="quick_filter",
                    target_id="active_today"
                ).pack()
            ),
            InlineKeyboardButton(
                text="📈 Nuevos (7d)",
                callback_data=AdminActionCallback(
                    module="users",
                    action="quick_filter",
                    target_id="new_week"
                ).pack()
            )
        )
        
        return builder
    
    def _build_back_keyboard(self, module: str) -> InlineKeyboardBuilder:
        """Teclado simple de volver"""
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(
                text="◀️ Volver",
                callback_data=AdminMenuCallback(module=module, action="main").pack()
            )
        )
        return builder
    
    # ============================================
    # UTILIDADES DE MENSAJERÍA
    # ============================================
    
    async def _edit_or_send_message(self, message_or_query: Union[Message, CallbackQuery], 
                                   text: str, keyboard: InlineKeyboardMarkup) -> None:
        """Editar mensaje existente o enviar nuevo"""
        
        if isinstance(message_or_query, CallbackQuery):
            await self._edit_message(message_or_query, text, keyboard)
        else:
            await self._send_new_message(message_or_query, text, keyboard)
    
    async def _edit_message(self, query: CallbackQuery, text: str, keyboard: InlineKeyboardMarkup) -> None:
        """Editar mensaje existente"""
        try:
            await query.message.edit_text(
                text=text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            await query.answer()
        except TelegramBadRequest as e:
            if "message is not modified" in str(e):
                await query.answer("✅ Actualizado")
            else:
                logger.error(f"Error editando mensaje: {e}")
                await query.answer(f"❌ Error: {str(e)[:100]}")
        except Exception as e:
            logger.error(f"Error inesperado editando mensaje: {e}")
            await query.answer("❌ Error inesperado")
    
    async def _send_new_message(self, message: Message, text: str, keyboard: InlineKeyboardMarkup) -> None:
        """Enviar nuevo mensaje"""
        try:
            await message.answer(
                text=text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"Error enviando mensaje: {e}")
            await message.answer("❌ Error enviando mensaje")
    
    async def _handle_error(self, message_or_query: Union[Message, CallbackQuery], error_text: str) -> None:
        """Manejar errores de forma elegante"""
        try:
            if isinstance(message_or_query, CallbackQuery):
                await message_or_query.answer(f"❌ {error_text}", show_alert=True)
            else:
                await message_or_query.answer(f"❌ {error_text}")
        except Exception as e:
            logger.error(f"Error manejando error: {e}")


# ============================================
# HANDLER PRINCIPAL DEL SISTEMA ÉPICO
# ============================================

class DianaEpicAdminHandler:
    """
    Handler principal para el sistema de administración épico
    """
    
    def __init__(self, bot: Bot, services: Dict[str, Any] = None):
        self.bot = bot
        self.menu_system = DianaEpicAdminMenu(bot, services)
        self.router = Router()
        self.services = services or {}
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Configurar todos los handlers de callback"""
        
        # Handler para navegación de menús
        self.router.callback_query.register(
            self.handle_menu_callback,
            AdminMenuCallback.filter()
        )
        
        # Handler para acciones específicas
        self.router.callback_query.register(
            self.handle_action_callback,
            AdminActionCallback.filter()
        )
        
        # Handler para operaciones CRUD
        self.router.callback_query.register(
            self.handle_crud_callback,
            AdminCRUDCallback.filter()
        )
    
    async def handle_menu_callback(self, query: CallbackQuery, callback_data: AdminMenuCallback):
        """Handler para navegación entre módulos"""
        try:
            user_id = query.from_user.id
            module = callback_data.module
            action = callback_data.action
            page = callback_data.page
            
            logger.info(f"🎛️ Menu callback: {module}.{action} | page: {page} | user: {user_id}")
            
            # Verificar permisos de admin
            if not await self._is_admin(user_id):
                await query.answer("⚡ Solo el Oráculo puede acceder", show_alert=True)
                return
            
            # Enrutar a módulo específico
            if module == "main":
                if action == "refresh":
                    await self.menu_system.show_main_panel(query)
                    await query.answer("🔄 Universo actualizado")
                elif action == "close":
                    await query.message.delete()
                    await query.answer("🛠️ Panel del Oráculo cerrado")
                else:
                    await self.menu_system.show_main_panel(query)
                    
            elif module == "narrative":
                await self.menu_system.show_narrative_module(query, action, page)
                
            elif module == "gamification":
                await self.menu_system.show_gamification_module(query, action, page)
                
            elif module == "users":
                await self.menu_system.show_users_module(query, action, page)
                
            elif module == "channels":
                await self.menu_system.show_channels_module(query, action, page)
                
            elif module == "shop":
                await self.menu_system.show_shop_module(query, action, page)
                
            elif module == "config":
                await self.menu_system.show_config_module(query, action, page)
                
            elif module == "stats":
                await self.menu_system.show_stats_module(query, action, page)
                
            elif module == "devtools":
                await self.menu_system.show_devtools_module(query, action, page)
                
            else:
                await query.answer(f"🧩 Módulo '{module}' no reconocido")
                
        except Exception as e:
            logger.error(f"Error en menu callback: {e}")
            await query.answer(f"❌ Error: {str(e)[:100]}", show_alert=True)
    
    async def handle_action_callback(self, query: CallbackQuery, callback_data: AdminActionCallback):
        """Handler para acciones específicas dentro de módulos"""
        try:
            user_id = query.from_user.id
            module = callback_data.module
            action = callback_data.action
            target_id = callback_data.target_id
            extra = callback_data.extra
            page = callback_data.page
            
            logger.info(f"⚡ Action callback: {module}.{action} | target: {target_id} | user: {user_id}")
            
            # Verificar permisos
            if not await self._is_admin(user_id):
                await query.answer("⚡ Acceso denegado", show_alert=True)
                return
            
            # Ejecutar acción específica
            await self._execute_specific_action(query, module, action, target_id, extra, page)
            
        except Exception as e:
            logger.error(f"Error en action callback: {e}")
            await query.answer(f"❌ Error ejecutando: {str(e)[:100]}")
    
    async def handle_crud_callback(self, query: CallbackQuery, callback_data: AdminCRUDCallback):
        """Handler para operaciones CRUD"""
        try:
            user_id = query.from_user.id
            module = callback_data.module
            operation = callback_data.operation
            item_id = callback_data.item_id
            page = callback_data.page
            
            logger.info(f"🔧 CRUD callback: {module}.{operation} | item: {item_id} | user: {user_id}")
            
            # Verificar permisos
            if not await self._is_admin(user_id):
                await query.answer("⚡ Operación no autorizada", show_alert=True)
                return
            
            # Ejecutar operación CRUD
            await self._execute_crud_operation(query, module, operation, item_id, page)
            
        except Exception as e:
            logger.error(f"Error en CRUD callback: {e}")
            await query.answer(f"❌ Error en operación: {str(e)[:100]}")
    
    async def _execute_specific_action(self, query: CallbackQuery, module: str, action: str, 
                                     target_id: Optional[str], extra: Optional[str], page: int):
        """Ejecutar acciones específicas de cada módulo"""
        
        if module == "narrative":
            await self._handle_narrative_actions(query, action, target_id, extra)
            
        elif module == "gamification":
            await self._handle_gamification_actions(query, action, target_id, extra)
            
        elif module == "users":
            await self._handle_users_actions(query, action, target_id, extra)
            
        elif module == "channels":
            await self._handle_channels_actions(query, action, target_id, extra)
            
        elif module == "shop":
            await self._handle_shop_actions(query, action, target_id, extra)
            
        elif module == "config":
            await self._handle_config_actions(query, action, target_id, extra)
            
        elif module == "stats":
            await self._handle_stats_actions(query, action, target_id, extra)
            
        elif module == "devtools":
            await self._handle_devtools_actions(query, action, target_id, extra)
            
        else:
            await query.answer(f"🧩 Acción '{action}' no implementada en '{module}'")
    
    async def _execute_crud_operation(self, query: CallbackQuery, module: str, operation: str, 
                                    item_id: Optional[str], page: int):
        """Ejecutar operaciones CRUD universales"""
        
        if operation == "create":
            await self._handle_create_operation(query, module)
        elif operation == "edit":
            await self._handle_edit_operation(query, module, item_id)
        elif operation == "delete":
            await self._handle_delete_operation(query, module, item_id)
        elif operation == "view":
            await self._handle_view_operation(query, module, item_id)
        else:
            await query.answer(f"🔧 Operación '{operation}' no reconocida")
    
    # ============================================
    # HANDLERS DE ACCIONES ESPECÍFICAS POR MÓDULO
    # ============================================
    
    async def _handle_narrative_actions(self, query: CallbackQuery, action: str, 
                                      target_id: Optional[str], extra: Optional[str]):
        """Manejar acciones del módulo narrativo"""
        
        if action == "search_user_state":
            await query.answer("🔍 Función de búsqueda en desarrollo")
            
        elif action == "states_stats":
            stats_text = """
📊 <b>ESTADÍSTICAS DE ESTADOS NARRATIVOS</b>

🧠 <b>Análisis de Conciencia Multiversal:</b>
• Usuarios en fragmento inicial: <b>12</b>
• Usuarios en fragmentos medios: <b>23</b>
• Usuarios en fragmentos finales: <b>7</b>
• Promedio de decisiones por usuario: <b>8.5</b>
• Fragmento más visitado: <b>"Primer Encuentro"</b>
• Tasa de abandono en decisiones: <b>5%</b>

⚡ <b>Insights del Oráculo:</b>
Los usuarios tienden a permanecer más tiempo en fragmentos con decisiones complejas.
            """
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(
                    text="◀️ Volver a Estados",
                    callback_data=AdminMenuCallback(module="narrative", action="states").pack()
                )
            ]])
            
            await query.message.edit_text(stats_text, reply_markup=keyboard, parse_mode='HTML')
            await query.answer("📊 Estadísticas generadas")
            
        else:
            await query.answer(f"📜 Acción narrativa '{action}' en desarrollo")
    
    async def _handle_gamification_actions(self, query: CallbackQuery, action: str, 
                                         target_id: Optional[str], extra: Optional[str]):
        """Manejar acciones del módulo de gamificación"""
        
        if action == "quick_mission_stats":
            await query.answer("🎯 Estadísticas rápidas de misiones cargadas")
            
        elif action == "toggle_mission":
            await query.answer(f"🎮 Misión {target_id} {'activada' if extra == 'on' else 'desactivada'}")
            
        else:
            await query.answer(f"🎮 Acción de gamificación '{action}' en desarrollo")
    
    async def _handle_users_actions(self, query: CallbackQuery, action: str, 
                                  target_id: Optional[str], extra: Optional[str]):
        """Manejar acciones del módulo de usuarios"""
        
        if action == "filter_role":
            role_names = {"admin": "Administradores", "vip": "Usuarios VIP", "free": "Usuarios Free"}
            role_name = role_names.get(target_id, target_id)
            await query.answer(f"🏷️ Filtrado por: {role_name}")
            
        elif action == "promote_vip":
            await query.answer("👑 Función de promoción a VIP en desarrollo")
            
        elif action == "demote_vip":
            await query.answer("⬇️ Función de degradación VIP en desarrollo")
            
        elif action == "quick_filter":
            filter_names = {
                "admin": "Administradores",
                "vip": "Usuarios VIP", 
                "free": "Usuarios Free",
                "active_today": "Activos hoy",
                "new_week": "Nuevos (7 días)"
            }
            filter_name = filter_names.get(target_id, target_id)
            await query.answer(f"🔍 Filtro aplicado: {filter_name}")
            
        else:
            await query.answer(f"🧑‍🚀 Acción de usuarios '{action}' en desarrollo")
    
    async def _handle_channels_actions(self, query: CallbackQuery, action: str, 
                                     target_id: Optional[str], extra: Optional[str]):
        """Manejar acciones del módulo de canales"""
        await query.answer(f"📺 Acción de canales '{action}' en desarrollo")
    
    async def _handle_shop_actions(self, query: CallbackQuery, action: str, 
                                 target_id: Optional[str], extra: Optional[str]):
        """Manejar acciones del módulo de tienda"""
        await query.answer(f"🛒 Acción de tienda '{action}' en desarrollo")
    
    async def _handle_config_actions(self, query: CallbackQuery, action: str, 
                                   target_id: Optional[str], extra: Optional[str]):
        """Manejar acciones del módulo de configuración"""
        await query.answer(f"⚙️ Acción de configuración '{action}' en desarrollo")
    
    async def _handle_stats_actions(self, query: CallbackQuery, action: str, 
                                  target_id: Optional[str], extra: Optional[str]):
        """Manejar acciones del módulo de estadísticas"""
        await query.answer(f"📊 Acción de estadísticas '{action}' en desarrollo")
    
    async def _handle_devtools_actions(self, query: CallbackQuery, action: str, 
                                     target_id: Optional[str], extra: Optional[str]):
        """Manejar acciones del módulo de devtools"""
        await query.answer(f"🧩 Acción de devtools '{action}' en desarrollo")
    
    # ============================================
    # HANDLERS DE OPERACIONES CRUD
    # ============================================
    
    async def _handle_create_operation(self, query: CallbackQuery, module: str):
        """Manejar operación de creación"""
        module_names = {
            "narrative": "fragmento narrativo",
            "gamification": "elemento de juego",
            "users": "usuario",
            "shop": "ítem de tienda"
        }
        item_name = module_names.get(module, "elemento")
        await query.answer(f"➕ Crear nuevo {item_name} - En desarrollo")
    
    async def _handle_edit_operation(self, query: CallbackQuery, module: str, item_id: Optional[str]):
        """Manejar operación de edición"""
        if item_id:
            await query.answer(f"🔁 Editar ítem {item_id} - En desarrollo")
        else:
            await query.answer("🔁 Selecciona un ítem para editar")
    
    async def _handle_delete_operation(self, query: CallbackQuery, module: str, item_id: Optional[str]):
        """Manejar operación de eliminación"""
        if item_id:
            await query.answer(f"🗑️ Eliminar ítem {item_id} - Confirmación requerida")
        else:
            await query.answer("🗑️ Selecciona un ítem para eliminar")
    
    async def _handle_view_operation(self, query: CallbackQuery, module: str, item_id: Optional[str]):
        """Manejar operación de visualización"""
        if item_id:
            await query.answer(f"👁️ Ver detalles de {item_id} - En desarrollo")
        else:
            await query.answer("👁️ Selecciona un ítem para ver")
    
    # ============================================
    # UTILIDADES Y VERIFICACIONES
    # ============================================
    
    async def _is_admin(self, user_id: int) -> bool:
        """Verificar si el usuario es administrador"""
        try:
            # Lista hardcoded de admins (puedes integrar con tu servicio de usuarios)
            ADMIN_IDS = [1280444712]  # Tu ID de los logs
            
            if user_id in ADMIN_IDS:
                return True
            
            # Verificar con servicio de usuarios si está disponible
            if self.services.get('user_service'):
                user_service = self.services['user_service']
                user = await user_service.get_user(user_id)
                return user and getattr(user, 'is_admin', False)
            
            return False
            
        except Exception as e:
            logger.error(f"Error verificando admin {user_id}: {e}")
            return False


# ============================================
# FUNCIÓN DE SETUP PARA INTEGRACIÓN
# ============================================

def setup_diana_epic_admin_system(dp: Dispatcher, bot: Bot, services: Dict[str, Any] = None):
    """
    Configurar el sistema de administración épico en tu dispatcher
    
    Args:
        dp: Dispatcher de Aiogram
        bot: Instancia del bot
        services: Diccionario con tus servicios (user_service, admin_service, etc.)
    
    Returns:
        DianaEpicAdminHandler: Handler configurado
    """
    
    # Crear handler principal
    admin_handler = DianaEpicAdminHandler(bot, services)
    
    # Registrar router
    dp.include_router(admin_handler.router)
    
    # Comando /admin para activar panel
    @dp.message(F.text.startswith('/admin'))
    async def admin_command(message: Message):
        """Comando /admin para abrir Panel del Oráculo"""
        user_id = message.from_user.id
        
        # Verificar permisos
        if not await admin_handler._is_admin(user_id):
            await message.answer("⚡ Solo el Oráculo puede acceder a este panel")
            return
        
        # Mostrar panel principal
        await admin_handler.menu_system.show_main_panel(message)
    
    logger.info("🛠️ Sistema de Administración Épico Diana configurado")
    logger.info("⚡ Comando disponible: /admin")
    
    return admin_handler


# ============================================
# EJEMPLO DE USO E INTEGRACIÓN
# ============================================

if __name__ == "__main__":
    """
    Ejemplo de cómo integrar el sistema épico en tu bot existente
    """
    
    print("🛠️ SISTEMA DE ADMINISTRACIÓN ÉPICO DIANA")
    print("=" * 50)
    print("🧩 Módulos implementados:")
    for module, config in MODULE_CONFIG.items():
        print(f"  {config['icon']} {config['title']}")
    
    print(f"\n📊 Total de módulos: {len(MODULE_CONFIG)}")
    print("✅ Sistema listo para integrar")
    print("\n🔧 Para integrar en tu bot:")
    print("1. Importa: from diana_admin_epic_menu import setup_diana_epic_admin_system")
    print("2. Configura: admin_handler = setup_diana_epic_admin_system(dp, bot, services)")
    print("3. Usa: /admin en Telegram")
    print("\n⚡ ¡El Oráculo te espera!")