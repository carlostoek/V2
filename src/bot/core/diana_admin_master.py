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
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from enum import Enum

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

import structlog

from .diana_admin_services_integration import DianaAdminServicesIntegration
from .diana_admin_security import DianaAdminSecurity, AdminPermission
# from .diana_core_system import DianaCoreSystem  # Removed to avoid circular import

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
            
            # Hierarchical permission checking - higher levels include lower levels
            user_role = self.security.user_roles.get(user_id)
            if not user_role:
                return False
                
            # Permission hierarchy (higher includes lower)
            hierarchy = {
                "super_admin": ["super_admin", "admin", "moderator", "viewer"],
                "admin": ["admin", "moderator", "viewer"],
                "moderator": ["moderator", "viewer"],
                "viewer": ["viewer"]
            }
            
            allowed_levels = hierarchy.get(user_role, [])
            return required_level in allowed_levels
            
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
        """Create the main admin interface with Lucien's voice"""
        
        # Check permissions
        if not await self.check_admin_permission(user_id):
            return self._create_no_permission_interface()
            
        context = await self.get_admin_context(user_id)
        
        # Get real-time system stats from services integration
        system_overview = await self.services_integration.get_system_overview()
        system_stats = system_overview['overview']
        
        # Lucien's elegant introduction
        text = f"""<b>🎩 Bienvenido al Sanctum Administrativo de Diana</b>

<i>Ah, ha regresado. Lucien a su servicio, guardián de los dominios administrativos de nuestra estimada Diana.</i>

<b>📊 Informe de Estado Actual:</b>
• <b>Visitantes bajo observación:</b> {system_stats['active_users']} almas inquietas (últimas 24h)
• <b>Besitos distribuidos:</b> {system_stats['points_generated']} fragmentos de atención
• <b>Miembros del círculo exclusivo:</b> {system_stats['vip_subscriptions']} privilegiados
• <b>Tiempo en operación:</b> {system_stats['uptime']} de vigilancia continua

<b>🏛️ Sectores Bajo Su Jurisdicción:</b>
<i>Cada sección revela secretos que Diana permite compartir con usted...</i>

<b>👤 Su Estatus:</b> {self._format_permission_title(context.permission_level)}
<b>🕐 Sesión iniciada:</b> {context.session_start.strftime('%H:%M')} hrs"""

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
            InlineKeyboardButton(text="🏠 Inicio Usuario", callback_data="admin:back_to_user")
        ])
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    def _format_permission_title(self, permission_level: AdminPermissionLevel) -> str:
        """Format permission level with Lucien's elegant titles"""
        titles = {
            AdminPermissionLevel.SUPER_ADMIN: "🎩 Mayordomo Superior - Acceso Total a los Archivos de Diana",
            AdminPermissionLevel.ADMIN: "👤 Administrador de Confianza - Custodio de Secretos Selectos",
            AdminPermissionLevel.MODERATOR: "🎪 Moderador del Círculo - Guardian de las Conversaciones",
            AdminPermissionLevel.VIEWER: "👁️ Observador Discreto - Testigo Silencioso"
        }
        return titles.get(permission_level, "🤔 Visitante Desconocido")
    
    def _get_lucien_section_intro(self, section_key: str, section_title: str) -> str:
        """Get Lucien's personalized introduction for each section"""
        intros = {
            "vip": "Ah, los dominios exclusivos de Diana. Aquí residen los secretos más preciados y los privilegiados que han ganado su favor especial.",
            "free_channel": "El vestíbulo de ingreso, donde las almas curiosas toman sus primeros pasos hacia el mundo de Diana. Cada visitante es observado con atención.",
            "global_config": "Los engranajes silenciosos que mantienen el reino en funcionamiento. Diana confía en que estos mecanismos permanezcan precisos.",
            "gamification": "El sistema de recompensas que Diana ha diseñado con meticulosa elegancia. Cada punto otorgado tiene su propósito.",
            "auctions": "Los eventos especiales donde Diana permite que sus tesoros cambien de manos. Cada transacción está cuidadosamente orquestada.",
            "events": "Las celebraciones que Diana organiza para deliciar a sus seguidores. Momentos de revelación y sorpresa.",
            "trivia": "Los desafíos intelectuales que Diana usa para medir la perspicacia de sus visitantes."
        }
        return intros.get(section_key, f"Un sector especial del dominio de Diana: {section_title}")
    
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
        
        # Generate breadcrumb with Lucien's style
        breadcrumb = " → ".join(context.breadcrumb_path)
        
        # Lucien's section introduction
        section_intro = self._get_lucien_section_intro(section_key, section.title)
        
        text = f"""<b>🏛️ {breadcrumb}</b>

<b>{section.icon} {section.title.upper()}</b>

<i>{section_intro}</i>

<b>📋 Diana me ha confiado:</b> {section.description}

{await self._get_section_overview_lucien_style(section_key, section_stats)}

<b>🎯 Herramientas a su disposición:</b>
<i>Seleccione sabiamente, cada acción es observada...</i>"""
        
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
        
        text = f"""<b>🏛️ {breadcrumb}</b>

<b>{section.icon} {subsection_title}</b>

<i>"{content['lucien_quote']}"</i>

{content['description']}

<b>📊 Registro de Actividad:</b>
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
    
    async def _get_section_overview_lucien_style(self, section_key: str, stats: Dict[str, Any]) -> str:
        """Get overview text for a section with Lucien's elegant style"""
        
        if section_key == "vip":
            return f"""<b>💎 Informe del Círculo Exclusivo:</b>
• <b>Membresías disponibles:</b> {stats.get('total_tariffs', 0)} niveles de privilegio
• <b>Almas en el círculo:</b> {stats.get('active_subscriptions', 0)} selectos miembros
• <b>Tributos recaudados hoy:</b> ${stats.get('revenue_today', 0):.2f} en apreciación
• <b>Invitaciones en espera:</b> {stats.get('pending_invitations', 0)} llaves sin usar

<i>Diana observa con satisfacción el crecimiento de su círculo íntimo.</i>"""
            
        elif section_key == "gamification":
            return f"""<b>🎮 Estado del Sistema de Recompensas:</b>
• <b>Participantes registrados:</b> {stats.get('total_users', 0)} almas en el juego
• <b>Desafíos activos:</b> {stats.get('active_missions', 0)} pruebas disponibles
• <b>Besitos distribuidos hoy:</b> {stats.get('points_today', 0)} fragmentos de atención
• <b>Ascensos logrados:</b> {stats.get('level_ups_today', 0)} almas elevadas

<i>El sistema funciona con la precisión que Diana exige.</i>"""
            
        elif section_key == "free_channel":
            return f"""<b>🔓 Reporte del Vestíbulo Público:</b>
• <b>Visitantes suscritos:</b> {stats.get('total_subscribers', 0)} observadores
• <b>Interacciones registradas:</b> {stats.get('messages_today', 0)} mensajes hoy
• <b>Solicitudes pendientes:</b> {stats.get('pending_requests', 0)} en evaluación

<i>El primer filtro de Diana funciona eficientemente.</i>"""
            
        else:
            return f"""<b>📊 Métricas en Observación Continua</b>
<i>Los datos fluyen constantemente bajo la mirada atenta de Diana.</i>"""
    
    async def _get_subsection_content(self, section_key: str, subsection_key: str) -> Dict[str, Any]:
        """Get content for a specific subsection"""
        
        # VIP Section Content
        if section_key == "vip":
            if subsection_key == "config":
                return {
                    'lucien_quote': "Diana ha perfeccionado cada palabra, cada pausa, cada matiz de sus mensajes. Aquí yacen los textos que tocan el alma.",
                    'description': "<b>🛠 Configuración del Círculo Exclusivo</b>\nLas palabras que Diana susurra a sus elegidos, cuidadosamente seleccionadas para despertar deseo.",
                    'stats': "• <b>Mensajes de seducción:</b> 5 variaciones maestras\n• <b>Recordatorios susurrantes:</b> 3 secuencias activas\n• <b>Plantillas de intimidad:</b> 8 diseños disponibles",
                    'content': "<b>⚙️ Herramientas de Personalización:</b>\n• <b>Mensajes de Bienvenida VIP:</b> La primera caricia verbal\n• <b>Recordatorios de Renovación:</b> Susurros de permanencia\n• <b>Flujos de Suscripción:</b> El camino hacia la intimidad\n• <b>Mensajes de Despedida:</b> La elegante retirada",
                    'actions': [
                        {'text': '🏷️ Gestionar Tarifas', 'callback': 'admin:action:vip:manage_tariffs'},
                        {'text': '✏️ Editar Mensajes', 'callback': 'admin:action:vip:edit_messages'},
                        {'text': '⏰ Config Recordatorios', 'callback': 'admin:action:vip:config_reminders'},
                        {'text': '👋 Mensajes Despedida', 'callback': 'admin:action:vip:goodbye_messages'}
                    ]
                }
            elif subsection_key == "invite":
                return {
                    'lucien_quote': "Cada invitación es una llave dorada, forjada con precisión para abrir puertas que pocos pueden atravesar.",
                    'description': "<b>🏷 Forja de Invitaciones Exclusivas</b>\nLas llaves secretas que Diana otorga para acceso a sus dominios privados.",
                    'stats': "• <b>Llaves en circulación:</b> 12 invitaciones activas\n• <b>Accesos otorgados hoy:</b> 3 almas elevadas\n• <b>Llaves expiradas:</b> 2 oportunidades perdidas",
                    'content': "<b>🎫 Taller de Invitaciones Especiales:</b>\n• <b>Forjar nuevas llaves:</b> Crear tokens únicos\n• <b>Duración del encanto:</b> Configurar vigencia\n• <b>Asignación de privilegios:</b> Vincular a niveles VIP\n• <b>Vigilancia de uso:</b> Monitorear activaciones",
                    'actions': [
                        {'text': '🎫 Generar Token', 'callback': 'admin:action:vip:generate_token'},
                        {'text': '📋 Tokens Activos', 'callback': 'admin:action:vip:list_tokens'},
                        {'text': '⚙️ Configurar Tokens', 'callback': 'admin:action:vip:config_tokens'},
                        {'text': '📊 Registro de Uso', 'callback': 'admin:action:vip:token_stats'}
                    ]
                }
            elif subsection_key == "stats":
                return {
                    'lucien_quote': "Los números nunca mienten, pero en las manos de Diana, cada cifra cuenta una historia de seducción y conquista.",
                    'description': "<b>📊 Observatorio de Conquistas VIP</b>\nCada métrica revela el arte de Diana para cautivar corazones y abrir carteras.",
                    'stats': "• <b>Almas conquistadas hoy:</b> 5 nuevas conversiones\n• <b>Tributos acumulados:</b> $1,234.56 en devoción\n• <b>Efectividad de seducción:</b> 12.3% de éxito",
                    'content': "<b>📈 Análisis de la Influencia de Diana:</b>\n• <b>Patrones de conversión:</b> El arte de la persuasión\n• <b>Flujo de tributos:</b> La generosidad inspirada\n• <b>Lealtad de devotos:</b> La persistencia del encanto\n• <b>Evolución temporal:</b> El crecimiento del imperio",
                    'actions': [
                        {'text': '📈 Conquistas Detalladas', 'callback': 'admin:action:vip:conversion_stats'},
                        {'text': '💰 Flujo de Tributos', 'callback': 'admin:action:vip:revenue_analysis'},
                        {'text': '👥 Lealtad de Devotos', 'callback': 'admin:action:vip:retention_analysis'},
                        {'text': '📊 Exportar Inteligencia', 'callback': 'admin:action:vip:export_stats'}
                    ]
                }
                
        # Gamification Section Content
        elif section_key == "gamification":
            if subsection_key == "stats":
                return {
                    'lucien_quote': "Diana ha diseñado cada recompensa como un hilo invisible que une a sus seguidores con su mundo. Observo cómo responden con fascinación.",
                    'description': "<b>📊 Observatorio del Sistema de Recompensas</b>\nEl ingenioso mecanismo que Diana usa para medir el compromiso y otorgar favores.",
                    'stats': "• <b>Besitos en circulación:</b> 125,000 fragmentos de atención\n• <b>Participantes activos:</b> 456 almas comprometidas\n• <b>Desafíos completados:</b> 1,234 pruebas superadas",
                    'content': "<b>🎯 Análisis del Engagement:</b>\n• <b>Distribución de recompensas:</b> Quién merece la atención de Diana\n• <b>Progreso individual:</b> El crecimiento de cada alma\n• <b>Efectividad de desafíos:</b> Qué despierta más pasión\n• <b>Patrones de compromiso:</b> La devoción medida en datos",
                    'actions': [
                        {'text': '📈 Distribución de Besitos', 'callback': 'admin:action:gamification:points_distribution'},
                        {'text': '🎯 Desafíos Predilectos', 'callback': 'admin:action:gamification:mission_popularity'},
                        {'text': '📊 Análisis de Devoción', 'callback': 'admin:action:gamification:engagement_metrics'},
                        {'text': '📋 Informe Magistral', 'callback': 'admin:action:gamification:full_report'}
                    ]
                }
                
        # Global Configuration Section Content  
        elif section_key == "global_config":
            if subsection_key == "add_channels":
                return {
                    'lucien_quote': "Diana comprende que expandir su dominio requiere nuevos territorios. Cada canal es una nueva oportunidad para ejercer su influencia.",
                    'description': "<b>📺 Registro de Nuevos Dominios VIP</b>\nEl proceso sagrado de añadir nuevos canales al imperio de Diana.",
                    'stats': "• <b>Canales VIP activos:</b> 3 dominios establecidos\n• <b>Capacidad total:</b> Ilimitada expansión\n• <b>Último registro:</b> Hace 2 horas",
                    'content': "<b>🏛️ Gestión de Canales VIP:</b>\n• <b>Registro automático:</b> Creación instantánea con ID único\n• <b>Configuración inicial:</b> Preparación para gestión de tarifas\n• <b>Integración completa:</b> Listo para generar tokens\n• <b>Monitoreo activo:</b> Seguimiento de rendimiento",
                    'actions': [
                        {'text': '➕ Registrar Canal VIP', 'callback': 'admin:action:global_config:add_channels'},
                        {'text': '📋 Listar Canales', 'callback': 'admin:action:global_config:list_channels'},
                        {'text': '⚙️ Configurar Canal', 'callback': 'admin:action:global_config:config_channel'},
                        {'text': '📊 Estado de Canales', 'callback': 'admin:action:global_config:channel_stats'}
                    ]
                }
            elif subsection_key == "manage":
                return {
                    'lucien_quote': "Diana comprende que cada dominio debe ser vigilado y, cuando sea necesario, renovado. Aquí residen los territorios bajo su control.",
                    'description': "<b>🎚 Administración de Canales Registrados</b>\nControl total sobre los dominios establecidos de Diana.",
                    'stats': "• <b>Canales activos:</b> Bajo vigilancia constante\n• <b>Última verificación:</b> En tiempo real\n• <b>Estado del sistema:</b> Operacional",
                    'content': "<b>🏛️ Gestión de Dominios Existentes:</b>\n• <b>Visualización completa:</b> Lista de todos los canales registrados\n• <b>Control de acceso:</b> Eliminar canales cuando sea necesario\n• <b>Renovación de territorios:</b> Reemplazar canales obsoletos\n• <b>Monitoreo continuo:</b> Estado y rendimiento en tiempo real",
                    'actions': [
                        {'text': '📋 Ver Canales Registrados', 'callback': 'admin:action:global_config:list_registered_channels'},
                        {'text': '🔍 Verificar Estado', 'callback': 'admin:action:global_config:check_channels_status'},
                        {'text': '➕ Agregar Nuevo Canal', 'callback': 'admin:action:global_config:add_channels'}
                    ]
                }
                
        # Default fallback content with Lucien's touch
        return {
            'lucien_quote': "Ah, esta es un área que Diana aún está perfeccionando. La paciencia es una virtud, y las mejores cosas llegan a quienes saben esperar.",
            'description': f"<b>🔧 {subsection_key.replace('_', ' ').title()}</b>\nUn dominio que Diana está refinando con su característico detalle.",
            'stats': "• <b>Estado:</b> En proceso de perfeccionamiento\n• <b>Disponibilidad:</b> Cuando Diana lo considere digno de revelación",
            'content': "<b>⚙️ Mientras Diana completa su obra:</b>\n\nCada funcionalidad es meticulosamente diseñada para cumplir con sus elevados estándares.",
            'actions': [
                {'text': '📞 Reportar Urgencia', 'callback': f'admin:action:report_need:{section_key}:{subsection_key}'},
                {'text': '💡 Sugerir Refinamiento', 'callback': f'admin:action:suggest:{section_key}:{subsection_key}'}
            ]
        }
    
    # === UTILITY METHODS ===
    
    def _create_no_permission_interface(self) -> Tuple[str, InlineKeyboardMarkup]:
        """Create interface for users without admin permissions with Lucien's elegance"""
        text = """<b>🎩 Un Momento, Estimado Visitante</b>

<i>Lucien aquí, guardián de los secretos administrativos de Diana.</i>

Me temo que estos salones están reservados para aquellos que han ganado la confianza especial de Diana. Los dominios administrativos requieren... ciertos privilegios.

<b>🚪 Sus opciones:</b>
• Regresar al mundo que conoce
• Contactar con los guardianes apropiados

<i>Diana comprende la curiosidad, pero también valora los límites apropiados.</i>"""
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Regresar al Reino de Diana", callback_data="diana:refresh")]
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

# Command handlers
@admin_router.message(Command("admin"))
async def handle_admin_command(message: Message):
    """Handle /admin command"""
    if not diana_admin_master:
        await message.answer("🔧 Sistema administrativo no disponible")
        return
        
    user_id = message.from_user.id
    text, keyboard = await diana_admin_master.create_admin_main_interface(user_id)
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")

# Handle forwarded messages first (higher priority)
@admin_router.message(F.forward_from_chat & F.chat.type == "private")
async def handle_admin_forwarded_messages(message: Message):
    """Handle forwarded messages from channels"""
    if not diana_admin_master:
        return
        
    user_id = message.from_user.id
    
    try:
        # Check if user is in pending channel registration
        if hasattr(diana_admin_master.services_integration, '_pending_channel_registrations'):
            if user_id in diana_admin_master.services_integration._pending_channel_registrations:
                
                # Extract channel info from forwarded message
                forward_from_chat = message.forward_from_chat
                if forward_from_chat and (forward_from_chat.type == "channel" or forward_from_chat.type == "supergroup"):
                    
                    channel_id = str(forward_from_chat.id)
                    channel_name = forward_from_chat.title or f"Canal {channel_id[-6:]}"
                    
                    # Show confirmation message
                    confirmation_text = f"""<b>📺 Confirmar Registro de Canal</b>

<b>🔍 Información del mensaje reenviado:</b>
• <b>Telegram ID:</b> <code>{channel_id}</code>
• <b>Nombre:</b> {channel_name}
• <b>Tipo:</b> VIP

<b>¿Confirmas el registro de este canal?</b>"""

                    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                    
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [
                            InlineKeyboardButton(text="✅ Confirmar", 
                                               callback_data=f"admin:channel_confirm:{channel_id}"),
                            InlineKeyboardButton(text="❌ Cancelar", 
                                               callback_data="admin:channel_cancel")
                        ]
                    ])
                    
                    await message.answer(confirmation_text, reply_markup=keyboard, parse_mode="HTML")
                    
                    # Store channel info temporarily
                    if not hasattr(diana_admin_master.services_integration, '_temp_channel_data'):
                        diana_admin_master.services_integration._temp_channel_data = {}
                    diana_admin_master.services_integration._temp_channel_data[user_id] = {
                        "telegram_id": channel_id,
                        "name": channel_name,
                        "type": "vip"
                    }
                else:
                    await message.answer("❌ El mensaje debe ser reenviado desde un canal o supergrupo.")
                
                return
        
    except Exception as e:
        structlog.get_logger().error("Error handling admin forwarded message", error=str(e))

# Handle text messages (lower priority, after forwarded messages)
@admin_router.message(F.text & F.chat.type == "private")
async def handle_admin_text_messages(message: Message):
    """Handle text messages for interactive flows"""
    if not diana_admin_master:
        return
        
    user_id = message.from_user.id
    text = message.text.strip()
    
    # Skip if it's a command
    if text.startswith('/'):
        return
    
    try:
        # Check if user is in pending tariff creation
        if hasattr(diana_admin_master.services_integration, '_pending_tariff_creation'):
            if user_id in diana_admin_master.services_integration._pending_tariff_creation:
                await handle_tariff_creation_input(message, user_id, text)
                return
        
        # Check if user is in pending tariff field edit
        if hasattr(diana_admin_master.services_integration, '_pending_tariff_edits'):
            if user_id in diana_admin_master.services_integration._pending_tariff_edits:
                result = await diana_admin_master.services_integration.process_tariff_field_edit(user_id, text)
                if result.get('success'):
                    # Field updated successfully, interface already updated
                    pass
                else:
                    # Show error message
                    await message.answer(result.get('message', 'Error desconocido'))
                return
        
        # Check if user is in pending channel registration
        if hasattr(diana_admin_master.services_integration, '_pending_channel_registrations'):
            if user_id in diana_admin_master.services_integration._pending_channel_registrations:
                
                # Process the channel ID input
                result = await diana_admin_master.services_integration.process_channel_input(
                    user_id, text, "text"
                )
                
                if result.get("success") and result.get("show_confirmation"):
                    # Show confirmation message
                    channel_info = result["channel_info"]
                    confirmation_text = f"""<b>📺 Confirmar Registro de Canal</b>

<b>🔍 Información detectada:</b>
• <b>Telegram ID:</b> <code>{channel_info['telegram_id']}</code>
• <b>Nombre:</b> {channel_info['name']}
• <b>Tipo:</b> VIP

<b>¿Confirmas el registro de este canal?</b>"""

                    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                    
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [
                            InlineKeyboardButton(text="✅ Confirmar", 
                                               callback_data=f"admin:channel_confirm:{channel_info['telegram_id']}"),
                            InlineKeyboardButton(text="❌ Cancelar", 
                                               callback_data="admin:channel_cancel")
                        ]
                    ])
                    
                    await message.answer(confirmation_text, reply_markup=keyboard, parse_mode="HTML")
                    
                    # Store channel info temporarily
                    if not hasattr(diana_admin_master.services_integration, '_temp_channel_data'):
                        diana_admin_master.services_integration._temp_channel_data = {}
                    diana_admin_master.services_integration._temp_channel_data[user_id] = channel_info
                    
                else:
                    # Show error
                    error_msg = result.get("error", "Error desconocido")
                    await message.answer(f"❌ {error_msg}")
                
                return
        
    except Exception as e:
        structlog.get_logger().error("Error handling admin text message", error=str(e))

async def handle_tariff_creation_input(message: Message, user_id: int, text: str):
    """Handle input during tariff creation flow"""
    try:
        structlog.get_logger().info(f"📝 Procesando input de tarifa para usuario {user_id}: {text[:50]}...")
        
        if not hasattr(diana_admin_master.services_integration, '_pending_tariff_creation'):
            structlog.get_logger().error("❌ No hay _pending_tariff_creation")
            await message.answer("❌ No hay proceso de creación activo.")
            return
            
        if user_id not in diana_admin_master.services_integration._pending_tariff_creation:
            structlog.get_logger().error(f"❌ Usuario {user_id} no está en _pending_tariff_creation")
            await message.answer("❌ No hay proceso de creación activo para tu usuario.")
            return
            
        tariff_data = diana_admin_master.services_integration._pending_tariff_creation[user_id]
        current_step = tariff_data['step']
        
        structlog.get_logger().info(f"📝 Paso actual: {current_step}, datos: {tariff_data}")
        
        if current_step == 'price':
            # Validate price input
            try:
                price = float(text)
                if price < 0:
                    await message.answer("❌ El precio no puede ser negativo. Intenta de nuevo:")
                    return
                    
                # Store price and move to duration step
                tariff_data['data']['price'] = price
                tariff_data['step'] = 'duration'
                
                # Ask for duration with buttons
                from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(text="1 día", callback_data="admin:tariff_duration:1"),
                        InlineKeyboardButton(text="1 semana", callback_data="admin:tariff_duration:7")
                    ],
                    [
                        InlineKeyboardButton(text="2 semanas", callback_data="admin:tariff_duration:14"), 
                        InlineKeyboardButton(text="1 mes", callback_data="admin:tariff_duration:30")
                    ],
                    [InlineKeyboardButton(text="❌ Cancelar", callback_data="admin:action:vip:tariff_cancel")]
                ])
                
                await message.answer(
                    f"""<b>⏰ Paso 2 de 3: Duración</b>

<b>Precio configurado:</b> ${price:.2f}

Selecciona la <b>duración del acceso VIP</b> que tendrán los usuarios con esta tarifa:

<i>¿Cuánto tiempo durará el acceso?</i>""",
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
                
            except ValueError:
                await message.answer("❌ Precio inválido. Debe ser un número (ej: 29.99). Intenta de nuevo:")
                
        elif current_step == 'name':
            # Validate and store name
            name = text.strip()
            if len(name) < 3:
                await message.answer("❌ El nombre debe tener al menos 3 caracteres. Intenta de nuevo:")
                return
            if len(name) > 50:
                await message.answer("❌ El nombre no puede exceder 50 caracteres. Intenta de nuevo:")
                return
                
            tariff_data['data']['name'] = name
            
            structlog.get_logger().info(f"📝 Datos finales para crear tarifa: {tariff_data['data']}")
            
            # Create the tariff
            structlog.get_logger().info("📝 Llamando a create_tariff_from_flow_data...")
            result = await diana_admin_master.services_integration.create_tariff_from_flow_data(user_id, tariff_data['data'])
            structlog.get_logger().info(f"📝 Resultado de creación: {result}")
            
            if result and result.get('success'):
                tariff_info = result.get('tariff_info', {})
                success_text = f"""✅ <b>Tarifa creada exitosamente!</b>

<b>📋 Detalles de la Tarifa:</b>
• <b>ID:</b> {tariff_info.get('id')}
• <b>Nombre:</b> {tariff_info.get('name')}
• <b>Precio:</b> ${tariff_info.get('price', 0):.2f}
• <b>Duración:</b> {diana_admin_master.services_integration._format_duration_days(tariff_info.get('duration_days', 0))}

<i>Ya puedes usar esta tarifa para generar tokens VIP!</i>"""

                # Create navigation keyboard
                from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(text="🏷️ Ver Tarifas", callback_data="admin:action:vip:manage_tariffs"),
                        InlineKeyboardButton(text="🎫 Generar Token", callback_data="admin:subsection:vip:invite")
                    ],
                    [
                        InlineKeyboardButton(text="💎 Menú VIP", callback_data="admin:section:vip"),
                        InlineKeyboardButton(text="🏛️ Panel Admin", callback_data="admin:main")
                    ]
                ])
                
                await message.answer(success_text, reply_markup=keyboard, parse_mode="HTML")
            else:
                error_msg = result.get('error', 'Error desconocido') if result else 'Error al crear tarifa'
                await message.answer(f"❌ {error_msg}")
            
            # Cleanup
            del diana_admin_master.services_integration._pending_tariff_creation[user_id]
            
    except Exception as e:
        structlog.get_logger().error("Error handling tariff creation input", error=str(e))
        await message.answer("❌ Error procesando la información. Intenta de nuevo.")

@admin_router.callback_query(F.data.startswith("admin:tariff_"))
async def handle_tariff_flow_callbacks(callback: CallbackQuery):
    """Handle tariff creation flow callbacks"""
    if not diana_admin_master:
        await callback.answer("🔧 Sistema no disponible")
        return
        
    data = callback.data.replace("admin:tariff_", "")
    user_id = callback.from_user.id
    
    try:
        if data.startswith("duration:"):
            # Handle duration selection
            duration_days = int(data.replace("duration:", ""))
            
            if hasattr(diana_admin_master.services_integration, '_pending_tariff_creation'):
                if user_id in diana_admin_master.services_integration._pending_tariff_creation:
                    tariff_data = diana_admin_master.services_integration._pending_tariff_creation[user_id]
                    tariff_data['data']['duration_days'] = duration_days
                    tariff_data['step'] = 'name'
                    
                    duration_text = diana_admin_master.services_integration._format_duration_days(duration_days)
                    price = tariff_data['data']['price']
                    
                    await callback.message.edit_text(
                        f"""<b>📝 Paso 3 de 3: Nombre</b>

<b>Configuración actual:</b>
• <b>Precio:</b> ${price:.2f}
• <b>Duración:</b> {duration_text}

Envía el <b>nombre de la tarifa</b>.

<b>📝 Ejemplos:</b>
• <code>VIP Premium</code>
• <code>Acceso Mensual</code>
• <code>Plan Básico</code>

<i>¿Cómo se llamará esta tarifa?</i>""",
                        parse_mode="HTML"
                    )
                else:
                    await callback.answer("❌ Sesión expirada. Inicia el proceso de nuevo.")
            else:
                await callback.answer("❌ No hay proceso activo.")
                
    except Exception as e:
        structlog.get_logger().error("Error in tariff flow callback", error=str(e))
        await callback.answer("❌ Error procesando selección")
    
    await callback.answer()

@admin_router.callback_query(F.data.startswith("admin:channel_"))
async def handle_channel_confirmation_callbacks(callback: CallbackQuery):
    """Handle channel registration confirmation callbacks"""
    if not diana_admin_master:
        await callback.answer("🔧 Sistema no disponible")
        return
        
    data = callback.data.replace("admin:channel_", "")
    user_id = callback.from_user.id
    
    try:
        if data.startswith("confirm:"):
            # Confirm channel registration
            channel_id = data.replace("confirm:", "")
            
            # Get stored channel info
            if hasattr(diana_admin_master.services_integration, '_temp_channel_data'):
                channel_info = diana_admin_master.services_integration._temp_channel_data.get(user_id)
                if channel_info:
                    # Confirm registration
                    result = await diana_admin_master.services_integration.confirm_channel_registration(
                        user_id, channel_info, True
                    )
                    
                    if result.get("success"):
                        message = result.get("message", "Canal registrado exitosamente")
                        
                        # Check if navigation should be shown
                        if result.get("show_navigation"):
                            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                            
                            navigation_keyboard = InlineKeyboardMarkup(inline_keyboard=[
                                [
                                    InlineKeyboardButton(text="🏛️ Panel Admin", callback_data="admin:main"),
                                    InlineKeyboardButton(text="⚙ Configuración", callback_data="admin:section:global_config")
                                ],
                                [
                                    InlineKeyboardButton(text="💎 Configurar VIP", callback_data="admin:section:vip"),
                                    InlineKeyboardButton(text="🏷️ Crear Tarifas", callback_data="admin:subsection:vip:config")
                                ]
                            ])
                            
                            await callback.message.edit_text(message, reply_markup=navigation_keyboard, parse_mode="HTML")
                        else:
                            await callback.message.edit_text(message, parse_mode="HTML")
                    else:
                        error = result.get("message", "Error en el registro")
                        
                        # Check if navigation should be shown even for errors
                        if result.get("show_navigation"):
                            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                            
                            navigation_keyboard = InlineKeyboardMarkup(inline_keyboard=[
                                [
                                    InlineKeyboardButton(text="🏛️ Panel Admin", callback_data="admin:main"),
                                    InlineKeyboardButton(text="⚙ Configuración", callback_data="admin:section:global_config")
                                ],
                                [
                                    InlineKeyboardButton(text="💎 Configurar VIP", callback_data="admin:section:vip"),
                                    InlineKeyboardButton(text="🏷️ Crear Tarifas", callback_data="admin:subsection:vip:config")
                                ]
                            ])
                            
                            await callback.message.edit_text(error, reply_markup=navigation_keyboard, parse_mode="HTML")
                        else:
                            await callback.message.edit_text(f"❌ {error}", parse_mode="HTML")
                    
                    # Cleanup
                    del diana_admin_master.services_integration._temp_channel_data[user_id]
                    if hasattr(diana_admin_master.services_integration, '_pending_channel_registrations'):
                        diana_admin_master.services_integration._pending_channel_registrations.discard(user_id)
                else:
                    await callback.answer("❌ No se encontró información del canal.")
            else:
                await callback.answer("❌ No se encontró información del canal.")
                
        elif data == "cancel":
            # Cancel registration
            await callback.message.edit_text("❌ Registro de canal cancelado.")
            
            # Cleanup
            if hasattr(diana_admin_master.services_integration, '_temp_channel_data'):
                diana_admin_master.services_integration._temp_channel_data.pop(user_id, None)
            if hasattr(diana_admin_master.services_integration, '_pending_channel_registrations'):
                diana_admin_master.services_integration._pending_channel_registrations.discard(user_id)
        
    except Exception as e:
        structlog.get_logger().error("Error in channel confirmation callback", error=str(e))
        await callback.answer("❌ Error interno del sistema")
    
    await callback.answer()

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
                
        elif data == "back_to_user":
            # Route back to Diana User System via Diana Master System
            from .diana_user_master_system import diana_user_system
            
            if diana_user_system:
                text, keyboard = await diana_user_system.create_user_main_interface(user_id)
                await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
                return
            else:
                # Fallback message
                text = """<b>🎭 Regresando al Reino de Diana</b>
                
<i>Lucien te acompaña de vuelta al mundo de Diana...</i>

Usa /start para regresar al menú principal."""
                await callback.message.edit_text(text, parse_mode="HTML")
                return
                
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
                message = result.get('message', 'Acción ejecutada')
                show_alert = result.get('show_alert', False)
                await callback.answer(f"✅ {message}", show_alert=show_alert)
            else:
                error_msg = result.get('error', 'Error ejecutando acción')
                show_alert = result.get('show_alert', False)
                await callback.answer(f"❌ {error_msg}", show_alert=show_alert)
            return
            
        else:
            text, keyboard = await diana_admin_master.create_admin_main_interface(user_id)
        
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        
    except Exception as e:
        structlog.get_logger().error("Error in admin callback", error=str(e))
        await callback.answer("❌ Error interno del sistema")
    
    await callback.answer()

@admin_router.callback_query(F.data.startswith("admin:action:global_config:"))
async def handle_global_config_actions(callback: CallbackQuery):
    """Handle global config specific actions"""
    if not diana_admin_master:
        await callback.answer("🔧 Sistema no disponible")
        return
    
    data = callback.data.replace("admin:action:global_config:", "")
    user_id = callback.from_user.id
    
    try:
        if data == "list_registered_channels":
            # Get registered channels data and show interface
            channels_data = await diana_admin_master.services_integration.get_registered_channels_data()
            
            if not channels_data["success"]:
                error_text = f"❌ **Error al cargar canales**\n\n{channels_data['error']}\n\nIntenta de nuevo o contacta al administrador."
                
                from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="⬅️ Volver", callback_data="admin:section:global_config")]
                ])
                
                await callback.message.edit_text(error_text, reply_markup=keyboard, parse_mode="Markdown")
                return
            
            channels = channels_data["channels"]
            
            if not channels:
                no_channels_text = """📋 **Canales Registrados**

❌ No hay canales registrados actualmente.

Usa el menú de configuración para registrar canales."""
                
                from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="⬅️ Volver", callback_data="admin:section:global_config")]
                ])
                
                await callback.message.edit_text(no_channels_text, reply_markup=keyboard, parse_mode="Markdown")
                return
            
            # Construir mensaje con lista de canales
            message = "📋 **Canales Registrados**\n\n"
            buttons = []
            
            for channel in channels:
                channel_type_icon = "💎" if channel["type"] == "vip" else "🆓"
                message += f"{channel_type_icon} **{channel['name']}**\n"
                message += f"   • Tipo: {channel['type'].upper()}\n"
                message += f"   • ID: `{channel['telegram_id']}`\n"
                if channel["description"]:
                    message += f"   • {channel['description']}\n"
                message += "\n"
                
                # Agregar botón para eliminar cada canal
                buttons.append([{
                    "text": f"🗑️ Eliminar {channel['name']}",
                    "callback_data": f"admin:action:global_config:delete_channel:{channel['id']}"
                }])
            
            # Botones adicionales
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            
            additional_buttons = [
                [InlineKeyboardButton(text="🔄 Actualizar Lista", callback_data="admin:action:global_config:list_registered_channels")],
                [InlineKeyboardButton(text="📊 Estado de Canales", callback_data="admin:action:global_config:check_channels_status")],
                [InlineKeyboardButton(text="⬅️ Volver", callback_data="admin:section:global_config")]
            ]
            
            # Convertir buttons dict a InlineKeyboardButton
            inline_buttons = []
            for button_row in buttons:
                row = []
                for btn in button_row:
                    row.append(InlineKeyboardButton(text=btn["text"], callback_data=btn["callback_data"]))
                inline_buttons.append(row)
            
            # Agregar botones adicionales
            inline_buttons.extend(additional_buttons)
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=inline_buttons)
            await callback.message.edit_text(message, reply_markup=keyboard, parse_mode="Markdown")
            
        elif data == "check_channels_status":
            # Get channels status data and show interface
            status_data = await diana_admin_master.services_integration.get_channels_status_data()
            
            if not status_data["success"]:
                error_text = f"❌ **Error al verificar estado**\n\n{status_data['error']}\n\nIntenta de nuevo o contacta al administrador."
                
                from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="⬅️ Volver", callback_data="admin:section:global_config")]
                ])
                
                await callback.message.edit_text(error_text, reply_markup=keyboard, parse_mode="Markdown")
                return
            
            channels = status_data["channels"]
            
            if not channels:
                no_channels_text = """📊 **Estado de Canales**

❌ No hay canales registrados para mostrar estado."""
                
                from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="⬅️ Volver", callback_data="admin:section:global_config")]
                ])
                
                await callback.message.edit_text(no_channels_text, reply_markup=keyboard, parse_mode="Markdown")
                return
            
            message = "📊 **Estado de Canales**\n\n"
            
            for channel in channels:
                channel_type_icon = "💎" if channel["type"] == "vip" else "🆓"
                message += f"{channel_type_icon} **{channel['name']}** ({channel['type'].upper()})\n"
                message += f"   👥 Miembros: {channel['members_count']}\n"
                message += f"   💰 Tarifas activas: {channel['tariffs_count']}\n"
                message += f"   🆔 ID Telegram: `{channel['telegram_id']}`\n"
                message += f"   ✅ Estado: {'Activo' if channel['is_active'] else 'Inactivo'}\n"
                
                if channel["description"]:
                    message += f"   📝 {channel['description']}\n"
                
                message += "\n"
            
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔄 Actualizar Estado", callback_data="admin:action:global_config:check_channels_status")],
                [InlineKeyboardButton(text="📋 Ver Lista Canales", callback_data="admin:action:global_config:list_registered_channels")],
                [InlineKeyboardButton(text="⬅️ Volver", callback_data="admin:section:global_config")]
            ])
            
            await callback.message.edit_text(message, reply_markup=keyboard, parse_mode="Markdown")
            
        elif data.startswith("delete_channel:"):
            # Extract channel ID and delete channel
            channel_id_str = data.replace("delete_channel:", "")
            
            try:
                channel_id = int(channel_id_str)
                
                # Confirm deletion first
                from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                
                # Get channel info first
                channel_service = diana_admin_master.services_integration.services.get('channel')
                if not channel_service:
                    await callback.answer("❌ ChannelService no disponible")
                    return
                
                channel_info = await channel_service.get_channel(channel_id)
                if not channel_info:
                    await callback.answer("❌ Canal no encontrado")
                    return
                
                confirmation_text = f"""🗑️ **Confirmar Eliminación de Canal**

⚠️ **ATENCIÓN:** Esta acción eliminará permanentemente:

📺 **Canal:** {channel_info['name']}
🆔 **ID:** `{channel_info['telegram_id']}`
🏷️ **Tipo:** {channel_info['type'].upper()}
👥 **Miembros:** {channel_info.get('members_count', 0)}

**¿Estás seguro de que deseas continuar?**

*Esta acción no se puede deshacer.*"""

                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="✅ Sí, Eliminar", 
                            callback_data=f"admin:action:global_config:confirm_delete_channel:{channel_id}"
                        ),
                        InlineKeyboardButton(
                            text="❌ Cancelar", 
                            callback_data="admin:action:global_config:list_registered_channels"
                        )
                    ]
                ])
                
                await callback.message.edit_text(
                    confirmation_text, 
                    reply_markup=keyboard, 
                    parse_mode="Markdown"
                )
                
            except ValueError:
                await callback.answer("❌ ID de canal inválido")
                
        elif data.startswith("confirm_delete_channel:"):
            # Actually delete the channel
            channel_id_str = data.replace("confirm_delete_channel:", "")
            
            try:
                channel_id = int(channel_id_str)
                
                channel_service = diana_admin_master.services_integration.services.get('channel')
                if not channel_service:
                    await callback.answer("❌ ChannelService no disponible")
                    return
                
                # Get channel name before deletion for confirmation message
                channel_info = await channel_service.get_channel(channel_id)
                channel_name = channel_info['name'] if channel_info else f"Canal #{channel_id}"
                
                # Perform deletion (soft delete)
                success = await channel_service.delete_channel(channel_id)
                
                if success:
                    # Show success message and return to channel list
                    success_text = f"""✅ **Canal Eliminado Exitosamente**

🗑️ El canal **{channel_name}** ha sido eliminado del sistema.

• Los datos se han marcado como inactivos
• Las membresías han sido desactivadas
• El canal ya no aparecerá en las listas

**Regresando a la lista de canales...**"""

                    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                    
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(
                            text="📋 Ver Canales Restantes", 
                            callback_data="admin:action:global_config:list_registered_channels"
                        )],
                        [InlineKeyboardButton(
                            text="⬅️ Configuración", 
                            callback_data="admin:section:global_config"
                        )]
                    ])
                    
                    await callback.message.edit_text(
                        success_text, 
                        reply_markup=keyboard, 
                        parse_mode="Markdown"
                    )
                    
                    # Show brief success alert
                    await callback.answer(f"✅ Canal {channel_name} eliminado", show_alert=False)
                    
                else:
                    await callback.answer("❌ Error al eliminar canal")
                    await diana_admin_master.services_integration.show_registered_channels_interface(user_id)
                    
            except ValueError:
                await callback.answer("❌ ID de canal inválido")
        
        else:
            await callback.answer("❌ Acción desconocida")
            
    except Exception as e:
        structlog.get_logger().error(f"Error in global_config action: {e}")
        await callback.answer("❌ Error procesando acción")

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
