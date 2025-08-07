"""
⚡ DIANA ADMIN POWER FEATURES
============================

Silicon Valley-grade power user features and advanced functionality.
Command palette, shortcuts, guided tours, and elite admin tools.

Author: The Most Epic Silicon Valley Developer
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import re
import structlog

from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from .diana_admin_elite_ui import EliteUIBuilder, UITheme
from .diana_admin_callbacks import create_navigation_callback, create_action_callback, AdminAction

logger = structlog.get_logger()

# === COMMAND PALETTE ===

class CommandType(Enum):
    """Types of commands in the palette"""
    NAVIGATION = "navigation"
    ACTION = "action"
    SEARCH = "search"
    QUICK_STAT = "quick_stat"
    SYSTEM = "system"

@dataclass
class Command:
    """A command in the command palette"""
    id: str
    name: str
    description: str
    type: CommandType
    keywords: List[str]
    callback: str
    permission_required: Optional[str] = None
    section: Optional[str] = None
    
    def matches_query(self, query: str) -> bool:
        """Check if command matches search query"""
        query_lower = query.lower()
        return (
            query_lower in self.name.lower() or
            query_lower in self.description.lower() or
            any(query_lower in keyword.lower() for keyword in self.keywords)
        )

class CommandPalette:
    """Advanced command palette for power users"""
    
    def __init__(self):
        self.commands: List[Command] = []
        self.user_favorites: Dict[int, List[str]] = {}  # user_id -> command_ids
        self.usage_stats: Dict[str, int] = {}  # command_id -> usage_count
        
        self._initialize_commands()
    
    def _initialize_commands(self):
        """Initialize all available commands"""
        
        # Navigation commands
        nav_commands = [
            Command("nav_vip", "VIP Panel", "Navigate to VIP management", CommandType.NAVIGATION,
                   ["vip", "subscription", "premium"], create_navigation_callback(AdminAction.SECTION, section="vip")),
            Command("nav_gamification", "Gamification", "Navigate to gamification controls", CommandType.NAVIGATION,
                   ["gamification", "points", "achievements", "missions"], create_navigation_callback(AdminAction.SECTION, section="gamification")),
            Command("nav_channels", "Free Channels", "Navigate to free channel management", CommandType.NAVIGATION,
                   ["channels", "free", "public"], create_navigation_callback(AdminAction.SECTION, section="free_channel")),
            Command("nav_config", "Global Config", "Navigate to global configuration", CommandType.NAVIGATION,
                   ["config", "settings", "global"], create_navigation_callback(AdminAction.SECTION, section="global_config")),
            Command("nav_auctions", "Auctions", "Navigate to auction management", CommandType.NAVIGATION,
                   ["auctions", "bids"], create_navigation_callback(AdminAction.SECTION, section="auctions")),
            Command("nav_events", "Events", "Navigate to events and raffles", CommandType.NAVIGATION,
                   ["events", "raffles", "contests"], create_navigation_callback(AdminAction.SECTION, section="events")),
            Command("nav_trivia", "Trivia", "Navigate to trivia management", CommandType.NAVIGATION,
                   ["trivia", "questions", "quiz"], create_navigation_callback(AdminAction.SECTION, section="trivia")),
        ]
        
        # Quick action commands
        action_commands = [
            Command("action_gen_token", "Generate VIP Token", "Quickly generate a VIP invitation token", CommandType.ACTION,
                   ["token", "invite", "vip", "generate"], create_action_callback(AdminAction.VIP_GENERATE_TOKEN)),
            Command("action_vip_stats", "VIP Statistics", "View VIP statistics quickly", CommandType.QUICK_STAT,
                   ["vip", "stats", "revenue", "subscribers"], create_navigation_callback(AdminAction.SUBSECTION, section="vip", subsection="stats")),
            Command("action_gamif_stats", "Gamification Stats", "View gamification statistics", CommandType.QUICK_STAT,
                   ["gamification", "stats", "users", "points"], create_navigation_callback(AdminAction.SUBSECTION, section="gamification", subsection="stats")),
            Command("action_user_search", "Search Users", "Search for users in the system", CommandType.SEARCH,
                   ["users", "search", "find", "lookup"], create_action_callback(AdminAction.SEARCH, target="users")),
        ]
        
        # System commands
        system_commands = [
            Command("sys_health", "System Health", "Check overall system health", CommandType.SYSTEM,
                   ["health", "status", "system", "services"], create_action_callback(AdminAction.SYSTEM_HEALTH)),
            Command("sys_refresh", "Refresh Data", "Refresh all data and statistics", CommandType.SYSTEM,
                   ["refresh", "reload", "update"], create_action_callback(AdminAction.REFRESH)),
            Command("sys_export", "Export Data", "Export system data and reports", CommandType.SYSTEM,
                   ["export", "download", "backup"], create_action_callback(AdminAction.EXPORT)),
            Command("sys_logs", "View Logs", "View system and admin logs", CommandType.SYSTEM,
                   ["logs", "audit", "history"], create_action_callback(AdminAction.SYSTEM_LOGS)),
        ]
        
        self.commands = nav_commands + action_commands + system_commands
    
    def search_commands(self, query: str, user_id: int = None, limit: int = 8) -> List[Command]:
        """Search commands with intelligent ranking"""
        if not query:
            # Return favorites or most used commands
            return self._get_default_commands(user_id, limit)
        
        matches = []
        for command in self.commands:
            if command.matches_query(query):
                # Calculate relevance score
                score = self._calculate_relevance(command, query, user_id)
                matches.append((score, command))
        
        # Sort by relevance (descending)
        matches.sort(key=lambda x: x[0], reverse=True)
        
        return [cmd for _, cmd in matches[:limit]]
    
    def _calculate_relevance(self, command: Command, query: str, user_id: int = None) -> float:
        """Calculate command relevance score"""
        score = 0.0
        query_lower = query.lower()
        
        # Exact name match gets highest score
        if query_lower == command.name.lower():
            score += 100
        elif query_lower in command.name.lower():
            score += 50
        
        # Keyword matches
        for keyword in command.keywords:
            if query_lower == keyword.lower():
                score += 30
            elif query_lower in keyword.lower():
                score += 15
        
        # Description match
        if query_lower in command.description.lower():
            score += 10
        
        # Usage frequency boost
        usage_count = self.usage_stats.get(command.id, 0)
        score += min(usage_count * 2, 20)  # Cap at 20 points
        
        # User favorites boost
        if user_id and command.id in self.user_favorites.get(user_id, []):
            score += 25
        
        return score
    
    def _get_default_commands(self, user_id: int = None, limit: int = 8) -> List[Command]:
        """Get default commands when no query"""
        # Combine favorites and most used
        commands = []
        
        # User favorites first
        if user_id and user_id in self.user_favorites:
            fav_commands = [cmd for cmd in self.commands if cmd.id in self.user_favorites[user_id]]
            commands.extend(fav_commands[:4])
        
        # Most used commands
        most_used = sorted(self.commands, key=lambda c: self.usage_stats.get(c.id, 0), reverse=True)
        for cmd in most_used:
            if cmd not in commands:
                commands.append(cmd)
            if len(commands) >= limit:
                break
        
        # Fill with navigation commands if needed
        if len(commands) < limit:
            nav_commands = [c for c in self.commands if c.type == CommandType.NAVIGATION and c not in commands]
            commands.extend(nav_commands[:limit - len(commands)])
        
        return commands[:limit]
    
    def track_usage(self, command_id: str):
        """Track command usage"""
        self.usage_stats[command_id] = self.usage_stats.get(command_id, 0) + 1
    
    def add_favorite(self, user_id: int, command_id: str):
        """Add command to user favorites"""
        if user_id not in self.user_favorites:
            self.user_favorites[user_id] = []
        
        if command_id not in self.user_favorites[user_id]:
            self.user_favorites[user_id].append(command_id)
    
    def remove_favorite(self, user_id: int, command_id: str):
        """Remove command from user favorites"""
        if user_id in self.user_favorites and command_id in self.user_favorites[user_id]:
            self.user_favorites[user_id].remove(command_id)

# === GUIDED TOURS ===

@dataclass
class TourStep:
    """A step in a guided tour"""
    title: str
    description: str
    action: Optional[str] = None  # callback to execute
    highlight: Optional[str] = None  # what to highlight
    tip: Optional[str] = None

class GuidedTour:
    """Guided tours for new admins"""
    
    def __init__(self):
        self.tours: Dict[str, List[TourStep]] = {}
        self.user_progress: Dict[int, Dict[str, int]] = {}  # user_id -> tour_name -> step
        
        self._initialize_tours()
    
    def _initialize_tours(self):
        """Initialize guided tours"""
        
        # Basic admin tour
        self.tours["basic_admin"] = [
            TourStep(
                "¡Bienvenido al Panel de Administración!",
                "Este es el centro de control de Diana Bot. Desde aquí puedes gestionar todos los aspectos del bot.",
                tip="💡 Usa /admin en cualquier momento para volver aquí"
            ),
            TourStep(
                "Panel VIP 💎",
                "Gestiona suscripciones VIP, genera tokens de invitación y controla el acceso premium.",
                action=create_navigation_callback(AdminAction.SECTION, section="vip"),
                highlight="vip"
            ),
            TourStep(
                "Gamificación 🎮",
                "Controla el sistema de puntos, misiones, logros y niveles de usuarios.",
                action=create_navigation_callback(AdminAction.SECTION, section="gamification"),
                highlight="gamification"
            ),
            TourStep(
                "Estadísticas en Tiempo Real 📊",
                "Todas las estadísticas se actualizan automáticamente. Usa 'Actualizar' para datos más recientes.",
                tip="⚡ Los datos se actualizan cada 30 segundos automáticamente"
            ),
            TourStep(
                "¡Tour Completado! 🎉",
                "Ya conoces los conceptos básicos. ¡Explora libremente el sistema!",
                tip="🚀 Usa Ctrl+K (próximamente) para abrir la paleta de comandos"
            )
        ]
        
        # Advanced features tour
        self.tours["advanced_features"] = [
            TourStep(
                "Funciones Avanzadas ⚡",
                "Descubre las características más potentes del sistema de administración."
            ),
            TourStep(
                "Paleta de Comandos",
                "Accede rápidamente a cualquier función escribiendo comandos directamente.",
                tip="💡 Próximamente: Ctrl+K para abrir la paleta"
            ),
            TourStep(
                "Analytics Avanzados 📈",
                "Ve tendencias, patrones y métricas detalladas de rendimiento del bot.",
                action=create_action_callback(AdminAction.SYSTEM_HEALTH)
            ),
            TourStep(
                "Exportación de Datos 📤",
                "Exporta reportes, estadísticas y datos para análisis externos.",
                action=create_action_callback(AdminAction.EXPORT)
            )
        ]
    
    def start_tour(self, user_id: int, tour_name: str) -> Optional[TourStep]:
        """Start a guided tour"""
        if tour_name not in self.tours:
            return None
        
        if user_id not in self.user_progress:
            self.user_progress[user_id] = {}
        
        self.user_progress[user_id][tour_name] = 0
        return self.tours[tour_name][0]
    
    def next_step(self, user_id: int, tour_name: str) -> Optional[TourStep]:
        """Get next tour step"""
        if (user_id not in self.user_progress or 
            tour_name not in self.user_progress[user_id] or
            tour_name not in self.tours):
            return None
        
        current_step = self.user_progress[user_id][tour_name]
        next_step = current_step + 1
        
        if next_step >= len(self.tours[tour_name]):
            # Tour completed
            del self.user_progress[user_id][tour_name]
            return None
        
        self.user_progress[user_id][tour_name] = next_step
        return self.tours[tour_name][next_step]
    
    def get_available_tours(self, user_id: int) -> List[str]:
        """Get available tours for user"""
        # Could be based on user level, completed tours, etc.
        return ["basic_admin", "advanced_features"]

# === SHORTCUTS SYSTEM ===

class ShortcutsManager:
    """Manage keyboard shortcuts and quick actions"""
    
    def __init__(self):
        self.shortcuts: Dict[str, str] = {}
        self.user_shortcuts: Dict[int, Dict[str, str]] = {}
        
        self._initialize_default_shortcuts()
    
    def _initialize_default_shortcuts(self):
        """Initialize default shortcuts"""
        self.shortcuts = {
            "vip": create_navigation_callback(AdminAction.SECTION, section="vip"),
            "gamif": create_navigation_callback(AdminAction.SECTION, section="gamification"),
            "stats": create_action_callback(AdminAction.SYSTEM_HEALTH),
            "refresh": create_action_callback(AdminAction.REFRESH),
            "help": create_action_callback(AdminAction.HELP),
            "home": create_navigation_callback(AdminAction.MAIN),
            "back": create_navigation_callback(AdminAction.BACK),
        }
    
    def get_shortcuts_for_user(self, user_id: int) -> Dict[str, str]:
        """Get shortcuts for specific user"""
        user_shortcuts = self.user_shortcuts.get(user_id, {})
        return {**self.shortcuts, **user_shortcuts}
    
    def add_user_shortcut(self, user_id: int, shortcut: str, callback: str):
        """Add custom shortcut for user"""
        if user_id not in self.user_shortcuts:
            self.user_shortcuts[user_id] = {}
        
        self.user_shortcuts[user_id][shortcut] = callback

# === CONTEXTUAL HELP ===

class ContextualHelp:
    """Provide contextual help and tips"""
    
    def __init__(self):
        self.help_content: Dict[str, Dict[str, str]] = {}
        self._initialize_help_content()
    
    def _initialize_help_content(self):
        """Initialize help content"""
        self.help_content = {
            "main": {
                "title": "Panel Principal",
                "description": "Centro de control de Diana Bot con acceso a todas las funciones administrativas.",
                "tips": [
                    "💡 Las estadísticas se actualizan automáticamente cada 30 segundos",
                    "⚡ Usa los botones de acceso rápido para funciones frecuentes",
                    "🎨 Cambia el tema visual desde el botón Theme"
                ]
            },
            "vip": {
                "title": "Gestión VIP",
                "description": "Administra suscripciones premium, tokens y contenido exclusivo.",
                "tips": [
                    "🏷️ Los tokens de invitación tienen validez limitada",
                    "📊 Revisa las estadísticas para optimizar conversiones",
                    "💰 Los ingresos se muestran en tiempo real"
                ]
            },
            "gamification": {
                "title": "Sistema de Gamificación",
                "description": "Controla puntos, misiones, logros y niveles de usuarios.",
                "tips": [
                    "🎮 Las misiones diarias se resetean automáticamente",
                    "🏅 Los logros aumentan el engagement de usuarios",
                    "📈 Los puntos se pueden canjear por recompensas"
                ]
            }
        }
    
    def get_help_for_context(self, context: str) -> Dict[str, str]:
        """Get help for specific context"""
        return self.help_content.get(context, {
            "title": "Ayuda",
            "description": "No hay ayuda específica disponible para este contexto.",
            "tips": ["💡 Usa el botón Atrás para navegar al menú anterior"]
        })

# === POWER USER INTERFACE BUILDER ===

def build_command_palette_interface(commands: List[Command], query: str = "", theme: UITheme = UITheme.EXECUTIVE) -> Tuple[str, InlineKeyboardMarkup]:
    """Build command palette interface"""
    builder = EliteUIBuilder(theme)
    
    builder.header(
        "⚡ PALETA DE COMANDOS",
        f"Búsqueda: '{query}'" if query else "Comandos Disponibles",
        level=1
    )
    
    if not commands:
        builder.alert("No se encontraron comandos para la búsqueda", "info")
    else:
        # Group commands by type
        command_groups = {}
        for cmd in commands:
            if cmd.type not in command_groups:
                command_groups[cmd.type] = []
            command_groups[cmd.type].append(cmd)
        
        actions = []
        for cmd_type, cmds in command_groups.items():
            # Add type header
            type_names = {
                CommandType.NAVIGATION: "🧭 Navegación",
                CommandType.ACTION: "⚡ Acciones",
                CommandType.SEARCH: "🔍 Búsqueda", 
                CommandType.QUICK_STAT: "📊 Estadísticas",
                CommandType.SYSTEM: "⚙️ Sistema"
            }
            
            for cmd in cmds:
                # Add icon based on command type
                icon = {
                    CommandType.NAVIGATION: "→",
                    CommandType.ACTION: "⚡",
                    CommandType.SEARCH: "🔍",
                    CommandType.QUICK_STAT: "📊",
                    CommandType.SYSTEM: "⚙️"
                }.get(cmd.type, "▫️")
                
                actions.append({
                    "text": f"{icon} {cmd.name}",
                    "callback": cmd.callback
                })
    
    # Add navigation
    actions.append({
        "text": "← Cerrar Paleta",
        "callback": create_navigation_callback(AdminAction.MAIN)
    })
    
    builder.actions(actions, columns=1)  # Single column for better readability
    
    return builder.build()

def build_guided_tour_interface(step: TourStep, step_num: int, total_steps: int, theme: UITheme = UITheme.EXECUTIVE) -> Tuple[str, InlineKeyboardMarkup]:
    """Build guided tour interface"""
    builder = EliteUIBuilder(theme)
    
    builder.header(
        f"🎯 TOUR GUIADO ({step_num}/{total_steps})",
        step.title,
        level=1
    )
    
    # Progress bar
    progress = step_num / total_steps
    builder.progress("Progreso del Tour", step_num, total_steps)
    
    # Step content
    builder.alert(step.description, "info", "Información")
    
    if step.tip:
        builder.alert(step.tip, "info", "Consejo")
    
    # Actions
    actions = []
    
    if step.action:
        actions.append({
            "text": "▶️ Continuar Tour",
            "callback": step.action + ":tour_continue"
        })
    else:
        actions.append({
            "text": "▶️ Siguiente",
            "callback": create_action_callback(AdminAction.HELP, target="tour_next")
        })
    
    actions.extend([
        {
            "text": "⏸️ Pausar Tour",
            "callback": create_action_callback(AdminAction.HELP, target="tour_pause")
        },
        {
            "text": "❌ Salir del Tour",
            "callback": create_navigation_callback(AdminAction.MAIN)
        }
    ])
    
    builder.actions(actions, columns=2)
    
    return builder.build()

def build_contextual_help_interface(context: str, theme: UITheme = UITheme.EXECUTIVE) -> Tuple[str, InlineKeyboardMarkup]:
    """Build contextual help interface"""
    help_manager = ContextualHelp()
    help_content = help_manager.get_help_for_context(context)
    
    builder = EliteUIBuilder(theme)
    
    builder.header(
        "❓ AYUDA CONTEXTUAL",
        help_content["title"],
        level=1
    )
    
    # Description
    builder.alert(help_content["description"], "info", "Descripción")
    
    # Tips
    if "tips" in help_content:
        tips_text = "\n".join(help_content["tips"])
        builder.alert(tips_text, "info", "Consejos Útiles")
    
    # Actions
    actions = [
        {
            "text": "🎯 Iniciar Tour",
            "callback": create_action_callback(AdminAction.HELP, target="tour_basic")
        },
        {
            "text": "⚡ Paleta de Comandos",
            "callback": create_action_callback(AdminAction.HELP, target="command_palette")
        },
        {
            "text": "← Volver",
            "callback": create_navigation_callback(AdminAction.BACK)
        }
    ]
    
    builder.actions(actions, columns=2)
    
    return builder.build()

# === GLOBAL INSTANCES ===

command_palette = CommandPalette()
guided_tours = GuidedTour()
shortcuts_manager = ShortcutsManager()
contextual_help = ContextualHelp()