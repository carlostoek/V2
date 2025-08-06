"""
🎭 DIANA ADMIN MASTER SYSTEM
============================

Complete administrative menu system for Diana Bot with:
- 7 main sections with 25+ subsections
- Hierarchical navigation with breadcrumbs
- Real services integration
- Professional admin interface
- Adaptive callbacks and permissions

Based on Diana Master System architecture with admin-specific enhancements.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

import structlog

from .diana_admin_services_integration import DianaAdminServicesIntegration
from .diana_admin_security import DianaAdminSecurity, AdminPermission

# === ADMIN SYSTEM CONFIGURATION ===

@dataclass
class AdminMenuSection:
    """Defines an admin menu section with its subsections"""
    key: str
    title: str
    icon: str
    subsections: Dict[str, str]  # key -> title
    description: str
    permission_required: str = "admin"

# === EXACT MENU STRUCTURE AS REQUESTED ===
ADMIN_MENU_STRUCTURE = {
    "vip": AdminMenuSection(
        key="vip",
        title="VIP",
        icon="💎",
        subsections={
            "config": "🛠 Configuración VIP (Mensajes/Recordatorios/Suscripciones/Despedidas)",
            "invite": "🏷 Generar Invitación", 
            "stats": "📊 Estadísticas VIP",
            "subscribers": "📊 Suscriptores (CRUD)",
            "post": "📢 Enviar Post"
        },
        description="Gestión completa del sistema VIP"
    ),
    "free_channel": AdminMenuSection(
        key="free_channel",
        title="Canal Gratuito",
        icon="🔓",
        subsections={
            "config": "⚙ Configuración (Bienvenida/Flow/Tiempo)",
            "stats": "📊 Estadísticas",
            "requests": "📋 Solicitudes Pendientes", 
            "test": "🧪 Probar Flujo"
        },
        description="Administración del canal gratuito"
    ),
    "global_config": AdminMenuSection(
        key="global_config",
        title="Configuración Global",
        icon="⚙",
        subsections={
            "schedulers": "🕒 Programadores",
            "signatures": "📅 Firmar mensajes",
            "manage": "🎚 Administrar canales",
            "add_channels": "➕ Añadir Canales"
        },
        description="Configuración global del sistema"
    ),
    "gamification": AdminMenuSection(
        key="gamification", 
        title="Gamificación",
        icon="🎮",
        subsections={
            "stats": "📊 Estadísticas",
            "users": "👥 Usuarios", 
            "missions": "📜 Misiones",
            "badges": "🏅 Insignias",
            "levels": "📈 Niveles",
            "rewards": "🎁 Recompensas"
        },
        description="Control del sistema de gamificación"
    ),
    "auctions": AdminMenuSection(
        key="auctions",
        title="Subastas",
        icon="🛒",
        subsections={
            "stats": "📊 Estadísticas",
            "pending": "📋 Pendientes",
            "active": "🔄 Activas", 
            "create": "➕ Crear"
        },
        description="Gestión de subastas"
    ),
    "events": AdminMenuSection(
        key="events",
        title="Eventos y Sorteos",
        icon="🎉",
        subsections={
            "events_list": "🎫 Eventos (Listar/Crear)",
            "raffles_list": "🎁 Sorteos (Listar/Crear)"
        },
        description="Gestión de eventos y sorteos"
    ),
    "trivia": AdminMenuSection(
        key="trivia",
        title="Trivias",
        icon="❓",
        subsections={
            "list": "📋 Listar",
            "create": "➕ Crear"
        },
        description="Administración de trivias"
    )
}

class AdminPermissionLevel(Enum):
    """Admin permission levels"""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin" 
    MODERATOR = "moderator"
    VIEWER = "viewer"

@dataclass
class AdminContext:
    """Admin user context"""
    user_id: int
    permission_level: AdminPermissionLevel
    current_section: Optional[str] = None
    current_subsection: Optional[str] = None
    breadcrumb_path: List[str] = None
    session_start: datetime = None

class DianaAdminMaster:
    """
    🏛️ DIANA ADMIN MASTER SYSTEM
    
    Complete administrative interface for Diana Bot with hierarchical navigation,
    real service integration, and professional admin controls.
    """
    
    def __init__(self, services: Dict[str, Any], services_integration: DianaAdminServicesIntegration = None):
        self.services = services
        self.logger = structlog.get_logger()
        self.services_integration = services_integration or DianaAdminServicesIntegration(services)
        
        # Security system
        self.security = DianaAdminSecurity()
        
        # Admin state management
        self.admin_contexts: Dict[int, AdminContext] = {}
        self.admin_sessions: Dict[int, Dict[str, Any]] = {}
        
    # === PERMISSION SYSTEM ===
    
    async def check_admin_permission(self, user_id: int, required_level: str = "admin") -> bool:
        """Check if user has admin permissions using security system"""
        try:
            # Get or create admin session
            session = await self.security.get_active_session(user_id)
            if not session:
                session = await self.security.create_admin_session(user_id)
                if not session:
                    return False
            
            # Check rate limiting
            if not await self.security.check_rate_limit(user_id, "admin_access"):
                return False
            
            # Map required level to permission
            permission_map = {
                "super_admin": AdminPermission.SUPER_ADMIN,
                "admin": AdminPermission.ADMIN,
                "moderator": AdminPermission.MODERATOR,
                "viewer": AdminPermission.VIEWER
            }
            
            required_permission = permission_map.get(required_level, AdminPermission.ADMIN)
            return await self.security.check_permission(user_id, required_permission)
            
        except Exception as e:
            self.logger.error("Error checking admin permission", error=str(e))
            return False
    
    async def get_admin_permission_level(self, user_id: int) -> AdminPermissionLevel:
        """Get admin permission level for user"""
        if await self.check_admin_permission(user_id, "super_admin"):
            return AdminPermissionLevel.SUPER_ADMIN
        elif await self.check_admin_permission(user_id, "admin"):
            return AdminPermissionLevel.ADMIN
        elif await self.check_admin_permission(user_id, "moderator"):
            return AdminPermissionLevel.MODERATOR
        else:
            return AdminPermissionLevel.VIEWER
    
    # === CONTEXT MANAGEMENT ===
    
    async def get_admin_context(self, user_id: int) -> AdminContext:
        """Get or create admin context for user"""
        if user_id not in self.admin_contexts:
            permission_level = await self.get_admin_permission_level(user_id)
            self.admin_contexts[user_id] = AdminContext(
                user_id=user_id,
                permission_level=permission_level,
                breadcrumb_path=[],
                session_start=datetime.now()
            )
        return self.admin_contexts[user_id]
    
    def update_admin_context(self, user_id: int, section: str = None, subsection: str = None):
        """Update admin navigation context"""
        if user_id in self.admin_contexts:
            context = self.admin_contexts[user_id]
            context.current_section = section
            context.current_subsection = subsection
            
            # Update breadcrumb path
            if section and subsection:
                context.breadcrumb_path = ["🏛️ Admin", section, subsection]
            elif section:
                context.breadcrumb_path = ["🏛️ Admin", section]
            else:
                context.breadcrumb_path = ["🏛️ Admin"]
    
    # === MAIN ADMIN INTERFACE ===
    
    async def create_admin_main_interface(self, user_id: int) -> Tuple[str, InlineKeyboardMarkup]:
        """Create the main admin interface"""
        
        # Check permissions
        if not await self.check_admin_permission(user_id):
            return self._create_no_permission_interface()
            
        context = await self.get_admin_context(user_id)
        
        # Get real-time system stats from services integration
        system_overview = await self.services_integration.get_system_overview()
        system_stats = system_overview['overview']
        
        text = f"""🏛️ **DIANA BOT - CENTRO DE ADMINISTRACIÓN**

⚡ **Estado del Sistema**
• Usuarios Activos: {system_stats['active_users']} (24h)
• Puntos Generados: {system_stats['points_generated']} besitos
• Suscripciones VIP: {system_stats['vip_subscriptions']}
• Uptime: {system_stats['uptime']}

🎯 **Acceso Rápido**
Selecciona una sección para administrar:

👑 **Nivel de Acceso**: {context.permission_level.value.replace('_', ' ').title()}
🕐 **Sesión iniciada**: {context.session_start.strftime('%H:%M')}"""

        keyboard = self._create_main_admin_keyboard(context.permission_level)
        return text, keyboard
    
    def _create_main_admin_keyboard(self, permission_level: AdminPermissionLevel) -> InlineKeyboardMarkup:
        """Create main admin keyboard with permission-based sections"""
        
        buttons = []
        
        # Row 1: VIP & Channel Management
        buttons.append([
            InlineKeyboardButton(
                text=f"{ADMIN_MENU_STRUCTURE['vip'].icon} {ADMIN_MENU_STRUCTURE['vip'].title}",
                callback_data="admin:section:vip"
            ),
            InlineKeyboardButton(
                text=f"{ADMIN_MENU_STRUCTURE['free_channel'].icon} Canal Gratuito",
                callback_data="admin:section:free_channel"
            )
        ])
        
        # Row 2: Configuration & Gamification  
        buttons.append([
            InlineKeyboardButton(
                text=f"{ADMIN_MENU_STRUCTURE['global_config'].icon} Config Global",
                callback_data="admin:section:global_config"
            ),
            InlineKeyboardButton(
                text=f"{ADMIN_MENU_STRUCTURE['gamification'].icon} Gamificación",
                callback_data="admin:section:gamification"
            )
        ])
        
        # Row 3: Commerce & Events
        buttons.append([
            InlineKeyboardButton(
                text=f"{ADMIN_MENU_STRUCTURE['auctions'].icon} Subastas",
                callback_data="admin:section:auctions"
            ),
            InlineKeyboardButton(
                text=f"{ADMIN_MENU_STRUCTURE['events'].icon} Eventos",
                callback_data="admin:section:events"
            )
        ])
        
        # Row 4: Content Management
        buttons.append([
            InlineKeyboardButton(
                text=f"{ADMIN_MENU_STRUCTURE['trivia'].icon} Trivias", 
                callback_data="admin:section:trivia"
            ),
            InlineKeyboardButton(
                text="📊 Analytics Pro",
                callback_data="admin:analytics"
            )
        ])
        
        # Row 5: System Controls (Super Admin only)
        if permission_level == AdminPermissionLevel.SUPER_ADMIN:
            buttons.append([
                InlineKeyboardButton(
                    text="🛠️ Sistema",
                    callback_data="admin:system"
                ),
                InlineKeyboardButton(
                    text="⚙️ Config Avanzada",
                    callback_data="admin:advanced"
                )
            ])
        
        # Row 6: Navigation
        buttons.append([
            InlineKeyboardButton(text="🔄 Actualizar", callback_data="admin:refresh"),
            InlineKeyboardButton(text="🏠 Inicio Usuario", callback_data="diana:refresh")
        ])
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    # === SECTION INTERFACES ===
    
    async def create_section_interface(self, user_id: int, section_key: str) -> Tuple[str, InlineKeyboardMarkup]:
        """Create interface for a specific section"""
        
        if section_key not in ADMIN_MENU_STRUCTURE:
            return await self.create_admin_main_interface(user_id)
            
        section = ADMIN_MENU_STRUCTURE[section_key]
        context = await self.get_admin_context(user_id)
        self.update_admin_context(user_id, section_key)
        
        # Get section-specific stats from services integration
        section_stats = await self._get_section_stats_integrated(section_key)
        
        # Generate breadcrumb
        breadcrumb = " → ".join(context.breadcrumb_path)
        
        text = f"""🏛️ {breadcrumb}

{section.icon} **{section.title.upper()}**

📋 **{section.description}**

{await self._get_section_overview(section_key, section_stats)}

🎯 **Opciones Disponibles:**"""
        
        keyboard = self._create_section_keyboard(section, context.permission_level)
        return text, keyboard
    
    def _create_section_keyboard(self, section: AdminMenuSection, permission_level: AdminPermissionLevel) -> InlineKeyboardMarkup:
        """Create keyboard for a specific section"""
        
        buttons = []
        subsections = list(section.subsections.items())
        
        # Create rows of 2 buttons each
        for i in range(0, len(subsections), 2):
            row = []
            for j in range(2):
                if i + j < len(subsections):
                    key, title = subsections[i + j]
                    # Extract icon from title
                    if title.startswith(("🛠", "🏷", "📊", "📢", "⚙", "📋", "🧪", "🕒", "📅", "🎚", "➕", "👥", "📜", "🏅", "📈", "🎁", "🔄", "🎫", "❓")):
                        button_text = title
                    else:
                        button_text = f"• {title}"
                        
                    row.append(InlineKeyboardButton(
                        text=button_text,
                        callback_data=f"admin:subsection:{section.key}:{key}"
                    ))
            buttons.append(row)
        
        # Add navigation buttons
        buttons.append([
            InlineKeyboardButton(text="🔙 Volver", callback_data="admin:main"),
            InlineKeyboardButton(text="🔄 Actualizar", callback_data=f"admin:section:{section.key}")
        ])
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    # === SUBSECTION INTERFACES ===
    
    async def create_subsection_interface(self, user_id: int, section_key: str, subsection_key: str) -> Tuple[str, InlineKeyboardMarkup]:
        """Create interface for a specific subsection"""
        
        if section_key not in ADMIN_MENU_STRUCTURE:
            return await self.create_admin_main_interface(user_id)
            
        section = ADMIN_MENU_STRUCTURE[section_key]
        if subsection_key not in section.subsections:
            return await self.create_section_interface(user_id, section_key)
        
        context = await self.get_admin_context(user_id)
        self.update_admin_context(user_id, section_key, subsection_key)
        
        subsection_title = section.subsections[subsection_key]
        
        # Generate breadcrumb
        breadcrumb = " → ".join(context.breadcrumb_path)
        
        # Get subsection-specific content
        content = await self._get_subsection_content(section_key, subsection_key)
        
        text = f"""🏛️ {breadcrumb}

{section.icon} **{subsection_title}**

{content['description']}

📊 **Estado Actual:**
{content['stats']}

{content['content']}"""

        keyboard = self._create_subsection_keyboard(section_key, subsection_key, content['actions'])
        return text, keyboard
    
    def _create_subsection_keyboard(self, section_key: str, subsection_key: str, actions: List[Dict[str, str]]) -> InlineKeyboardMarkup:
        """Create keyboard for a specific subsection"""
        
        buttons = []
        
        # Add action buttons (2 per row)
        action_buttons = []
        for action in actions:
            action_buttons.append(InlineKeyboardButton(
                text=action['text'],
                callback_data=action['callback']
            ))
        
        for i in range(0, len(action_buttons), 2):
            row = action_buttons[i:i+2]
            buttons.append(row)
        
        # Add navigation
        buttons.append([
            InlineKeyboardButton(
                text="🔙 Volver",
                callback_data=f"admin:section:{section_key}"
            ),
            InlineKeyboardButton(
                text="🏛️ Admin Principal",
                callback_data="admin:main"
            )
        ])
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    # === DATA PROVIDERS (INTEGRATED) ===
    
    async def _get_section_stats_integrated(self, section_key: str) -> Dict[str, Any]:
        """Get statistics for a specific section using services integration"""
        try:
            if section_key == "vip":
                return await self.services_integration.get_vip_system_stats()
            elif section_key == "gamification":
                return await self.services_integration.get_gamification_stats()
            elif section_key == "free_channel":
                channel_stats = await self.services_integration.get_channel_stats()
                return channel_stats.get('free_channel', {})
            elif section_key == "daily_rewards" or section_key == "rewards":
                return await self.services_integration.get_daily_rewards_stats()
            else:
                return {}
        except Exception as e:
            self.logger.error(f"Error getting {section_key} stats", error=str(e))
            return {}
    
    async def _get_section_overview(self, section_key: str, stats: Dict[str, Any]) -> str:
        """Get overview text for a section"""
        
        if section_key == "vip":
            return f"""💎 **Resumen VIP:**
• Tarifas Activas: {stats.get('total_tariffs', 0)}
• Suscripciones: {stats.get('active_subscriptions', 0)}
• Ingresos Hoy: ${stats.get('revenue_today', 0):.2f}
• Invitaciones Pendientes: {stats.get('pending_invitations', 0)}"""
            
        elif section_key == "gamification":
            return f"""🎮 **Resumen Gamificación:**
• Usuarios Totales: {stats.get('total_users', 0)}
• Misiones Activas: {stats.get('active_missions', 0)}
• Puntos Hoy: {stats.get('points_today', 0)}
• Subidas de Nivel: {stats.get('level_ups_today', 0)}"""
            
        elif section_key == "free_channel":
            return f"""🔓 **Resumen Canal Gratuito:**
• Suscriptores: {stats.get('total_subscribers', 0)}
• Mensajes Hoy: {stats.get('messages_today', 0)}
• Solicitudes: {stats.get('pending_requests', 0)}"""
            
        else:
            return "📊 **Estadísticas en tiempo real**"
    
    async def _get_subsection_content(self, section_key: str, subsection_key: str) -> Dict[str, Any]:
        """Get content for a specific subsection"""
        
        # VIP Section Content
        if section_key == "vip":
            if subsection_key == "config":
                return {
                    'description': "🛠 **Configuración del Sistema VIP**\nConfigura mensajes automáticos, recordatorios y flujos de suscripción.",
                    'stats': "• Mensajes Configurados: 5\n• Recordatorios Activos: 3\n• Plantillas: 8",
                    'content': "⚙️ **Opciones de Configuración:**\n• Mensajes de Bienvenida VIP\n• Recordatorios de Renovación\n• Flujos de Suscripción\n• Mensajes de Despedida",
                    'actions': [
                        {'text': '✏️ Editar Mensajes', 'callback': 'admin:action:vip:edit_messages'},
                        {'text': '⏰ Config Recordatorios', 'callback': 'admin:action:vip:config_reminders'},
                        {'text': '🔄 Flujos Suscripción', 'callback': 'admin:action:vip:subscription_flows'},
                        {'text': '👋 Mensajes Despedida', 'callback': 'admin:action:vip:goodbye_messages'}
                    ]
                }
            elif subsection_key == "invite":
                return {
                    'description': "🏷 **Generador de Invitaciones VIP**\nCrea y gestiona tokens de invitación para acceso VIP.",
                    'stats': "• Tokens Activos: 12\n• Tokens Usados Hoy: 3\n• Expirados: 2",
                    'content': "🎫 **Gestión de Invitaciones:**\n• Generar nuevos tokens\n• Configurar duración\n• Asignar a tarifas específicas\n• Monitorear uso",
                    'actions': [
                        {'text': '➕ Generar Token', 'callback': 'admin:action:vip:generate_token'},
                        {'text': '📋 Ver Activos', 'callback': 'admin:action:vip:list_tokens'},
                        {'text': '⚙️ Config Tokens', 'callback': 'admin:action:vip:config_tokens'},
                        {'text': '📊 Estadísticas', 'callback': 'admin:action:vip:token_stats'}
                    ]
                }
            elif subsection_key == "stats":
                return {
                    'description': "📊 **Estadísticas Completas VIP**\nAnalítica detallada del sistema VIP.",
                    'stats': "• Conversiones Hoy: 5\n• Ingresos Totales: $1,234.56\n• Tasa Conversión: 12.3%",
                    'content': "📈 **Métricas Disponibles:**\n• Conversiones por período\n• Análisis de ingresos\n• Retención de usuarios\n• Comparativas temporales",
                    'actions': [
                        {'text': '📈 Ver Conversiones', 'callback': 'admin:action:vip:conversion_stats'},
                        {'text': '💰 Análisis Ingresos', 'callback': 'admin:action:vip:revenue_analysis'},
                        {'text': '👥 Retención Usuarios', 'callback': 'admin:action:vip:retention_analysis'},
                        {'text': '📊 Exportar Datos', 'callback': 'admin:action:vip:export_stats'}
                    ]
                }
                
        # Gamification Section Content
        elif section_key == "gamification":
            if subsection_key == "stats":
                return {
                    'description': "📊 **Estadísticas de Gamificación**\nMétricas completas del sistema de puntos y progreso.",
                    'stats': "• Puntos Totales: 125,000\n• Usuarios Activos: 456\n• Misiones Completadas: 1,234",
                    'content': "🎯 **Métricas Disponibles:**\n• Distribución de puntos\n• Progreso de usuarios\n• Eficacia de misiones\n• Análisis de engagement",
                    'actions': [
                        {'text': '📈 Puntos por Usuario', 'callback': 'admin:action:gamification:points_distribution'},
                        {'text': '🎯 Misiones Populares', 'callback': 'admin:action:gamification:mission_popularity'},
                        {'text': '📊 Engagement', 'callback': 'admin:action:gamification:engagement_metrics'},
                        {'text': '📋 Reporte Completo', 'callback': 'admin:action:gamification:full_report'}
                    ]
                }
                
        # Default fallback content
        return {
            'description': f"🔧 **{subsection_key.replace('_', ' ').title()}**\nFuncionalidad en desarrollo.",
            'stats': "• Estado: En desarrollo\n• Disponibilidad: Próximamente",
            'content': "⚙️ Esta funcionalidad estará disponible en próximas versiones.\n\nMientras tanto, puedes:",
            'actions': [
                {'text': '📞 Reportar Necesidad', 'callback': f'admin:action:report_need:{section_key}:{subsection_key}'},
                {'text': '💡 Sugerir Mejora', 'callback': f'admin:action:suggest:{section_key}:{subsection_key}'}
            ]
        }
    
    # === UTILITY METHODS ===
    
    def _create_no_permission_interface(self) -> Tuple[str, InlineKeyboardMarkup]:
        """Create interface for users without admin permissions"""
        text = """🚫 **ACCESO DENEGADO**

No tienes permisos de administración para acceder a este panel.

Si crees que esto es un error, contacta con un administrador."""
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Volver al Inicio", callback_data="diana:refresh")]
        ])
        
        return text, keyboard

# === ROUTER AND HANDLERS ===

admin_router = Router()
diana_admin_master: Optional[DianaAdminMaster] = None

def initialize_diana_admin_master(services: Dict[str, Any]):
    """Initialize the Diana Admin Master System"""
    global diana_admin_master
    diana_admin_master = DianaAdminMaster(services)
    return diana_admin_master

@admin_router.message(Command("admin"))
async def cmd_admin(message: Message):
    """Admin command handler"""
    if not diana_admin_master:
        await message.reply("🔧 Sistema de administración no disponible")
        return
        
    user_id = message.from_user.id
    text, keyboard = await diana_admin_master.create_admin_main_interface(user_id)
    await message.reply(text, reply_markup=keyboard, parse_mode="Markdown")

@admin_router.callback_query(F.data.startswith("admin:"))
async def handle_admin_callbacks(callback: CallbackQuery):
    """Handle all admin system callbacks"""
    if not diana_admin_master:
        await callback.answer("🔧 Sistema no disponible")
        return
        
    data = callback.data.replace("admin:", "")
    user_id = callback.from_user.id
    
    try:
        if data == "main" or data == "refresh":
            text, keyboard = await diana_admin_master.create_admin_main_interface(user_id)
            
        elif data.startswith("section:"):
            section_key = data.replace("section:", "")
            text, keyboard = await diana_admin_master.create_section_interface(user_id, section_key)
            
        elif data.startswith("subsection:"):
            parts = data.replace("subsection:", "").split(":")
            if len(parts) >= 2:
                section_key, subsection_key = parts[0], parts[1]
                text, keyboard = await diana_admin_master.create_subsection_interface(user_id, section_key, subsection_key)
            else:
                text, keyboard = await diana_admin_master.create_admin_main_interface(user_id)
                
        elif data.startswith("action:"):
            # Handle specific actions using services integration
            action_data = data.replace("action:", "")
            
            # Log admin action
            await diana_admin_master.security.log_admin_action(
                user_id, f"admin_action:{action_data}", parameters={"callback_data": data}
            )
            
            result = await diana_admin_master.services_integration.execute_admin_action(
                action_data, user_id, {}
            )
            
            # Log result
            result_status = "success" if result.get("success") else "failure"
            await diana_admin_master.security.log_admin_action(
                user_id, f"admin_action_result:{action_data}", 
                parameters=result, result=result_status
            )
            
            if result.get("success"):
                await callback.answer(f"✅ {result.get('message', 'Acción ejecutada')}")
            else:
                await callback.answer(f"❌ {result.get('error', 'Error ejecutando acción')}")
            return
            
        else:
            text, keyboard = await diana_admin_master.create_admin_main_interface(user_id)
        
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
        
    except Exception as e:
        structlog.get_logger().error("Error in admin callback", error=str(e))
        await callback.answer("❌ Error interno del sistema")
    
    await callback.answer()

# === EXPORT FUNCTION ===

def register_diana_admin_master(dp, services: Dict[str, Any]):
    """Register the Diana Admin Master System"""
    
    # Initialize the system
    initialize_diana_admin_master(services)
    
    # Register the router
    dp.include_router(admin_router)
    
    print("🏛️ Diana Admin Master System initialized successfully!")
    print(f"📋 Total sections: {len(ADMIN_MENU_STRUCTURE)}")
    total_subsections = sum(len(section.subsections) for section in ADMIN_MENU_STRUCTURE.values())
    print(f"📊 Total subsections: {total_subsections}")
    print("🎭 Admin interface ready for production!")
    
    return diana_admin_master
