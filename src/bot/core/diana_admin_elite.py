"""
🎭 DIANA ADMIN ELITE SYSTEM
===========================

The most epic Silicon Valley-grade admin system ever built.
Elegant, blazingly fast, and beautifully designed.

This is the masterpiece - where all components come together in perfect harmony.

Author: The Most Epic Silicon Valley Developer
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
import structlog

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

# Import all our elite components
from .diana_admin_elite_ui import (
    EliteUIBuilder, UITheme, theme_manager, ui_cache,
    build_dashboard_ui, build_menu_ui, build_stats_ui
)
from .diana_admin_callbacks import (
    CallbackRouter, NavigationHandler, ActionHandler, AdminAction, AdminCallbackData,
    create_navigation_callback, create_action_callback, get_callback_router
)
from .diana_admin_analytics import (
    get_analytics_engine, get_real_time_updater, track_admin_action, ChartGenerator
)

# Original components (enhanced)
from .diana_admin_services_integration import DianaAdminServicesIntegration
from .diana_admin_security import DianaAdminSecurity, AdminPermission
from .diana_admin_master import AdminMenuSection, ADMIN_MENU_STRUCTURE

logger = structlog.get_logger()

# === ELITE ADMIN CONTEXT ===

@dataclass
class EliteAdminContext:
    """Enhanced admin context with more sophisticated state"""
    user_id: int
    current_section: Optional[str] = None
    current_subsection: Optional[str] = None
    breadcrumb_path: List[str] = field(default_factory=list)
    last_activity: datetime = field(default_factory=datetime.now)
    theme: UITheme = UITheme.EXECUTIVE
    shortcuts_enabled: bool = True
    real_time_updates: bool = True
    preferred_columns: int = 2
    compact_mode: bool = False

# === ELITE ADMIN MASTER ===

class DianaAdminElite:
    """The most epic admin system in Silicon Valley"""
    
    def __init__(self, services: Dict[str, Any]):
        self.services = services
        self.services_integration = DianaAdminServicesIntegration(services)
        self.security = DianaAdminSecurity()
        
        # Elite components
        self.analytics = get_analytics_engine()
        self.real_time_updater = get_real_time_updater()
        self.callback_router = get_callback_router()
        
        # Enhanced context management
        self.admin_contexts: Dict[int, EliteAdminContext] = {}
        
        # Performance optimization
        self.response_cache = {}
        self.cache_ttl = 60  # seconds
        
        # Initialize elite features
        self._initialize_elite_features()
        
        logger.info("🚀 Diana Admin Elite System initialized")
    
    def _initialize_elite_features(self):
        """Initialize elite Silicon Valley features"""
        # Register elite callback handlers
        nav_handler = NavigationHandler(self)
        action_handler = ActionHandler(self)
        
        self.callback_router.add_route(
            AdminAction.MAIN, nav_handler, rate_limit=30,
            description="Navigate to main admin panel"
        )
        self.callback_router.add_route(
            AdminAction.SECTION, nav_handler, rate_limit=60,
            description="Navigate to admin section"
        )
        self.callback_router.add_route(
            AdminAction.SUBSECTION, nav_handler, rate_limit=60,
            description="Navigate to admin subsection"
        )
        self.callback_router.add_route(
            AdminAction.BACK, nav_handler, rate_limit=120,
            description="Navigate back"
        )
        
        # Register action handlers
        for action in AdminAction:
            if action not in [AdminAction.MAIN, AdminAction.SECTION, AdminAction.SUBSECTION, AdminAction.BACK]:
                self.callback_router.add_route(
                    action, action_handler, rate_limit=30,
                    description=f"Execute {action.value} action"
                )
        
        logger.info("Elite callback handlers registered")
    
    async def get_admin_context(self, user_id: int) -> EliteAdminContext:
        """Get or create admin context"""
        if user_id not in self.admin_contexts:
            self.admin_contexts[user_id] = EliteAdminContext(user_id=user_id)
            
            # Set user theme
            user_theme = theme_manager.get_user_theme(user_id)
            self.admin_contexts[user_id].theme = user_theme
        
        # Update last activity
        self.admin_contexts[user_id].last_activity = datetime.now()
        return self.admin_contexts[user_id]
    
    def _update_context_navigation(self, context: EliteAdminContext, section: str = None, subsection: str = None):
        """Update context navigation state"""
        # Update breadcrumbs
        if section and section != context.current_section:
            if section == "main":
                context.breadcrumb_path = ["Admin"]
            else:
                section_title = ADMIN_MENU_STRUCTURE.get(section, {}).get("title", section)
                context.breadcrumb_path = ["Admin", section_title]
        
        if subsection:
            section_obj = ADMIN_MENU_STRUCTURE.get(section, {})
            if hasattr(section_obj, 'subsections') and subsection in section_obj.subsections:
                subsection_title = section_obj.subsections[subsection]
                # Clean up title (remove emojis and extra text)
                clean_title = subsection_title.split("(")[0].strip()
                if len(context.breadcrumb_path) == 2:
                    context.breadcrumb_path.append(clean_title)
                else:
                    context.breadcrumb_path[-1] = clean_title
        
        context.current_section = section
        context.current_subsection = subsection
    
    @track_admin_action("create_main_interface")
    async def create_admin_main_interface(self, user_id: int) -> Tuple[str, InlineKeyboardMarkup]:
        """Create the main admin interface with Silicon Valley polish"""
        
        # Get context and theme
        context = await self.get_admin_context(user_id)
        self._update_context_navigation(context, "main")
        
        # Check cache first
        cache_key = f"main_interface_{user_id}_{context.theme.value}_{context.compact_mode}"
        cached = ui_cache.get(cache_key)
        if cached:
            return cached
        
        # Get system overview with analytics
        system_overview = await self.services_integration.get_system_overview()
        
        # Track analytics
        self.analytics.set_gauge("admin_sessions_active", len(self.admin_contexts))
        self.analytics.increment_metric("admin_interface_requests")
        
        # Build elite UI
        builder = EliteUIBuilder(context.theme)
        
        # Epic header with real-time status
        builder.header(
            "CENTRO DE ADMINISTRACIÓN DIANA", 
            f"Sistema de Control Avanzado • {datetime.now().strftime('%H:%M')}",
            level=1,
            animated=True
        )
        
        # System overview stats
        if system_overview and "overview" in system_overview:
            overview_stats = {
                "Estado": "🟢 Operativo" if system_overview["overview"].get("status") == "healthy" else "🟡 Degradado",
                "Usuarios Activos": system_overview["overview"].get("active_users", 0),
                "Servicios": f"{system_overview['overview'].get('healthy_services', 0)}/{system_overview['overview'].get('total_services', 0)}",
                "Rendimiento": f"{system_overview['overview'].get('avg_response_time', 0):.0f}ms"
            }
            builder.stats_card("Estado del Sistema", overview_stats, compact=True)
        
        # Main sections as elegant action grid
        sections = []
        for key, section in ADMIN_MENU_STRUCTURE.items():
            sections.append({
                "text": f"{section.icon} {section.title}",
                "callback": create_navigation_callback(AdminAction.SECTION, section=key)
            })
        
        # Add system actions
        sections.extend([
            {
                "text": "📊 Analytics",
                "callback": create_action_callback(AdminAction.SYSTEM_HEALTH)
            },
            {
                "text": "🔄 Refresh",
                "callback": create_action_callback(AdminAction.REFRESH)
            },
            {
                "text": "🎨 Theme",
                "callback": create_action_callback(AdminAction.THEME)
            },
            {
                "text": "❓ Help",
                "callback": create_action_callback(AdminAction.HELP)
            }
        ])
        
        # Build with dynamic columns based on screen preference
        columns = 2 if context.compact_mode else 2
        builder.actions(sections, columns=columns)
        
        # Build final interface
        text, keyboard = builder.build()
        
        # Cache the result
        ui_cache.set(cache_key, (text, keyboard), ttl=30)
        
        return text, keyboard
    
    @track_admin_action("create_section_interface")
    async def create_section_interface(self, user_id: int, section_key: str) -> Tuple[str, InlineKeyboardMarkup]:
        """Create section interface with epic design"""
        
        context = await self.get_admin_context(user_id)
        self._update_context_navigation(context, section_key)
        
        # Validate section
        if section_key not in ADMIN_MENU_STRUCTURE:
            return await self._create_error_interface("Sección no encontrada")
        
        section = ADMIN_MENU_STRUCTURE[section_key]
        
        # Check cache
        cache_key = f"section_{section_key}_{user_id}_{context.theme.value}"
        cached = ui_cache.get(cache_key)
        if cached:
            return cached
        
        # Get section-specific stats
        section_stats = await self._get_section_stats(section_key)
        
        # Build elite interface
        builder = EliteUIBuilder(context.theme)
        
        # Section header with breadcrumbs
        builder.header(
            f"{section.icon} {section.title.upper()}",
            section.description if hasattr(section, 'description') else "Panel de Control",
            level=1
        )
        
        builder.navigation(context.breadcrumb_path)
        
        # Section-specific stats
        if section_stats:
            builder.stats_card(f"Estadísticas {section.title}", section_stats)
        
        # Subsection actions
        subsection_actions = []
        for sub_key, sub_title in section.subsections.items():
            subsection_actions.append({
                "text": sub_title,
                "callback": create_navigation_callback(AdminAction.SUBSECTION, section=section_key, subsection=sub_key)
            })
        
        # Add section-specific quick actions
        quick_actions = self._get_section_quick_actions(section_key)
        subsection_actions.extend(quick_actions)
        
        # Navigation actions
        subsection_actions.extend([
            {
                "text": "🔄 Actualizar",
                "callback": create_action_callback(AdminAction.REFRESH, target=section_key)
            },
            {
                "text": "← Atrás",
                "callback": create_navigation_callback(AdminAction.BACK)
            }
        ])
        
        builder.actions(subsection_actions, columns=2)
        
        text, keyboard = builder.build()
        ui_cache.set(cache_key, (text, keyboard), ttl=60)
        
        return text, keyboard
    
    @track_admin_action("create_subsection_interface")
    async def create_subsection_interface(self, user_id: int, section_key: str, subsection_key: str) -> Tuple[str, InlineKeyboardMarkup]:
        """Create subsection interface with maximum elegance"""
        
        context = await self.get_admin_context(user_id)
        self._update_context_navigation(context, section_key, subsection_key)
        
        # Validate
        if section_key not in ADMIN_MENU_STRUCTURE:
            return await self._create_error_interface("Sección no encontrada")
        
        section = ADMIN_MENU_STRUCTURE[section_key]
        if subsection_key not in section.subsections:
            return await self._create_error_interface("Subsección no encontrada")
        
        # Check cache
        cache_key = f"subsection_{section_key}_{subsection_key}_{user_id}_{context.theme.value}"
        cached = ui_cache.get(cache_key)
        if cached:
            return cached
        
        # Get subsection data
        subsection_data = await self._get_subsection_data(section_key, subsection_key)
        
        # Build interface
        builder = EliteUIBuilder(context.theme)
        
        # Header
        subsection_title = section.subsections[subsection_key]
        clean_title = subsection_title.split("(")[0].strip()
        
        builder.header(
            clean_title,
            f"Panel de Control • {section.title}",
            level=2
        )
        
        builder.navigation(context.breadcrumb_path)
        
        # Subsection-specific content
        if subsection_data:
            # Multiple stat groups for complex subsections
            if isinstance(subsection_data, list):
                for group in subsection_data:
                    if "title" in group and "stats" in group:
                        builder.stats_card(group["title"], group["stats"])
            elif isinstance(subsection_data, dict):
                if "stats" in subsection_data:
                    builder.stats_card("Estadísticas", subsection_data["stats"])
                if "chart_data" in subsection_data:
                    # Add chart
                    chart = ChartGenerator.create_bar_chart(subsection_data["chart_data"])
                    builder.alert(f"📊 Gráfico:\n```\n{chart}\n```", "info")
        
        # Subsection actions
        actions = self._get_subsection_actions(section_key, subsection_key)
        
        # Always add navigation
        actions.extend([
            {
                "text": "🔄 Actualizar",
                "callback": create_action_callback(AdminAction.REFRESH, target=f"{section_key}_{subsection_key}")
            },
            {
                "text": f"← {section.title}",
                "callback": create_navigation_callback(AdminAction.SECTION, section=section_key)
            },
            {
                "text": "🏠 Inicio",
                "callback": create_navigation_callback(AdminAction.MAIN)
            }
        ])
        
        builder.actions(actions, columns=2)
        
        text, keyboard = builder.build()
        ui_cache.set(cache_key, (text, keyboard), ttl=30)
        
        return text, keyboard
    
    async def _get_section_stats(self, section_key: str) -> Optional[Dict[str, Any]]:
        """Get section-specific statistics"""
        try:
            if section_key == "vip":
                stats = await self.services_integration.get_vip_system_stats()
                return {
                    "Suscriptores VIP": stats.get("active_subscriptions", 0),
                    "Ingresos Hoy": f"${stats.get('revenue_today', 0):.2f}",
                    "Tokens Activos": stats.get("pending_tokens", 0),
                    "Conversión": f"{stats.get('conversion_rate', 0):.1f}%"
                }
            elif section_key == "gamification":
                stats = await self.services_integration.get_gamification_stats()
                return {
                    "Usuarios Activos": stats.get("active_users_today", 0),
                    "Puntos Hoy": stats.get("points_distributed_today", 0),
                    "Misiones Completadas": stats.get("completed_missions_today", 0),
                    "Logros Desbloqueados": stats.get("achievements_earned_today", 0)
                }
            elif section_key == "free_channel":
                return {
                    "Solicitudes Pendientes": 5,
                    "Mensajes Hoy": 150,
                    "Nuevos Usuarios": 12,
                    "Engagement": "87%"
                }
            # Add more sections as needed
            return None
        except Exception as e:
            logger.error("Failed to get section stats", section=section_key, error=str(e))
            return None
    
    def _get_section_quick_actions(self, section_key: str) -> List[Dict[str, str]]:
        """Get quick actions for section"""
        quick_actions = {
            "vip": [
                {"text": "⚡ Generar Token", "callback": create_action_callback(AdminAction.VIP_GENERATE_TOKEN)}
            ],
            "gamification": [
                {"text": "⚡ Ver Top Users", "callback": create_action_callback(AdminAction.GAMIF_USERS)}
            ]
        }
        return quick_actions.get(section_key, [])
    
    async def _get_subsection_data(self, section_key: str, subsection_key: str) -> Any:
        """Get subsection-specific data"""
        try:
            # VIP subsections
            if section_key == "vip" and subsection_key == "stats":
                stats = await self.services_integration.get_vip_system_stats()
                return {
                    "stats": stats,
                    "chart_data": {
                        "Básico": stats.get("basic_subscriptions", 0),
                        "Premium": stats.get("premium_subscriptions", 0),
                        "Elite": stats.get("elite_subscriptions", 0)
                    }
                }
            
            # Gamification subsections
            elif section_key == "gamification" and subsection_key == "stats":
                stats = await self.services_integration.get_gamification_stats()
                return [
                    {
                        "title": "Usuarios",
                        "stats": {
                            "Total": stats.get("total_users", 0),
                            "Activos Hoy": stats.get("active_users_today", 0),
                            "Nuevos": stats.get("new_users_today", 0)
                        }
                    },
                    {
                        "title": "Puntos y Logros",
                        "stats": {
                            "Puntos Distribuidos": stats.get("total_points_distributed", 0),
                            "Puntos Hoy": stats.get("points_distributed_today", 0),
                            "Logros Desbloqueados": stats.get("achievements_earned_today", 0)
                        }
                    }
                ]
            
            return None
        except Exception as e:
            logger.error("Failed to get subsection data", section=section_key, subsection=subsection_key, error=str(e))
            return None
    
    def _get_subsection_actions(self, section_key: str, subsection_key: str) -> List[Dict[str, str]]:
        """Get subsection-specific actions"""
        actions = []
        
        # Common actions based on subsection type
        if "stats" in subsection_key:
            actions.append({"text": "📤 Exportar", "callback": create_action_callback(AdminAction.EXPORT, target=f"{section_key}_{subsection_key}")})
        
        if "config" in subsection_key:
            actions.append({"text": "⚙️ Configurar", "callback": create_action_callback(AdminAction.VIP_CONFIG if section_key == "vip" else AdminAction.SYSTEM_CONFIG)})
        
        if "users" in subsection_key or "subscribers" in subsection_key:
            actions.append({"text": "🔍 Buscar", "callback": create_action_callback(AdminAction.SEARCH, target="users")})
        
        return actions
    
    async def _create_error_interface(self, error_message: str) -> Tuple[str, InlineKeyboardMarkup]:
        """Create error interface"""
        builder = EliteUIBuilder()
        builder.header("Error", "Sistema de Administración", level=1)
        builder.alert(error_message, "error", "Error")
        builder.actions([
            {"text": "← Volver", "callback": create_navigation_callback(AdminAction.MAIN)}
        ])
        
        return builder.build()
    
    async def check_admin_permission(self, user_id: int, required_level: str = "admin") -> bool:
        """Check admin permission with elite security"""
        return await self.security.check_permission(user_id, AdminPermission.ADMIN)
    
    async def handle_elite_callback(self, callback_query: CallbackQuery) -> Any:
        """Handle callback with elite router"""
        return await self.callback_router.route(callback_query)

# === ELITE ROUTER SETUP ===

elite_admin_router = Router()

@elite_admin_router.message(Command("admin"))
async def elite_admin_command(message: Message):
    """Elite /admin command handler"""
    user_id = message.from_user.id
    
    # Get the elite admin system (would be injected in real implementation)
    admin_system = message.bot.get("diana_admin_elite")
    if not admin_system:
        await message.answer("❌ Sistema admin no disponible")
        return
    
    # Check permissions
    has_permission = await admin_system.check_admin_permission(user_id)
    if not has_permission:
        await message.answer("🚫 Sin permisos de administrador")
        return
    
    # Create elite main interface
    text, keyboard = await admin_system.create_admin_main_interface(user_id)
    
    await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")
    
    # Track analytics
    admin_system.analytics.increment_metric("admin_sessions_started")
    admin_system.analytics.track_event("admin_session_start", {"user_id": user_id})

@elite_admin_router.callback_query(F.data.startswith("admin:"))
async def elite_admin_callback(callback: CallbackQuery):
    """Elite callback handler"""
    admin_system = callback.bot.get("diana_admin_elite")
    if not admin_system:
        await callback.answer("❌ Sistema admin no disponible")
        return
    
    # Route through elite callback system
    await admin_system.handle_elite_callback(callback)

# === REGISTRATION FUNCTION ===

def register_diana_admin_elite(dp, services: Dict[str, Any]) -> DianaAdminElite:
    """Register the elite admin system"""
    # Create elite admin system
    admin_system = DianaAdminElite(services)
    
    # Store in bot context for access in handlers
    dp["diana_admin_elite"] = admin_system
    
    # Register router
    dp.include_router(elite_admin_router)
    
    logger.info("🎭 Diana Admin Elite System registered and ready!")
    
    return admin_system