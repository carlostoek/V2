"""
🎯 DIANA ADMIN CALLBACKS SYSTEM
===============================

Silicon Valley-grade callback routing with type safety and validation.
Ultra-fast, elegant, and bulletproof callback handling.

Author: The Most Epic Silicon Valley Developer
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Literal, Callable
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import structlog

from pydantic import BaseModel, validator, Field
from aiogram.types import CallbackQuery

logger = structlog.get_logger()

# === TYPE-SAFE CALLBACK MODELS ===

class AdminAction(str, Enum):
    """All possible admin actions"""
    # Navigation
    MAIN = "main"
    SECTION = "section"
    SUBSECTION = "subsection"
    BACK = "back"
    
    # VIP Actions  
    VIP_CONFIG = "vip_config"
    VIP_GENERATE_TOKEN = "vip_generate_token"
    VIP_STATS = "vip_stats"
    VIP_SUBSCRIBERS = "vip_subscribers"
    VIP_POST = "vip_post"
    
    # Gamification Actions
    GAMIF_STATS = "gamif_stats"
    GAMIF_USERS = "gamif_users"
    GAMIF_MISSIONS = "gamif_missions"
    GAMIF_BADGES = "gamif_badges"
    GAMIF_LEVELS = "gamif_levels"
    GAMIF_REWARDS = "gamif_rewards"
    
    # Channel Actions
    CHANNEL_CONFIG = "channel_config"
    CHANNEL_STATS = "channel_stats"
    CHANNEL_REQUESTS = "channel_requests"
    CHANNEL_TEST = "channel_test"
    
    # System Actions
    SYSTEM_HEALTH = "system_health"
    SYSTEM_LOGS = "system_logs"
    SYSTEM_CONFIG = "system_config"
    
    # Utility Actions
    REFRESH = "refresh"
    SEARCH = "search"
    EXPORT = "export"
    HELP = "help"
    THEME = "theme"

class AdminCallbackData(BaseModel):
    """Type-safe callback data model"""
    action: AdminAction
    section: Optional[str] = None
    subsection: Optional[str] = None
    target: Optional[str] = None
    params: Dict[str, Any] = Field(default_factory=dict)
    user_id: Optional[int] = None
    
    class Config:
        use_enum_values = True
    
    def __post_init__(self):
        # Convert string to enum if needed
        if isinstance(self.action, str):
            self.action = AdminAction(self.action)
    
    @validator('params')
    def validate_params(cls, v):
        """Ensure params is valid dict"""
        if not isinstance(v, dict):
            return {}
        return v
    
    def to_callback_string(self) -> str:
        """Convert to callback string format"""
        parts = ["admin", self.action.value]
        
        if self.section:
            parts.append(self.section)
        if self.subsection:
            parts.append(self.subsection)
        if self.target:
            parts.append(self.target)
            
        # Add params as encoded string if present
        if self.params:
            import json
            import base64
            params_json = json.dumps(self.params)
            params_encoded = base64.b64encode(params_json.encode()).decode()
            parts.append(params_encoded)
        
        return ":".join(parts)
    
    @classmethod
    def from_callback_string(cls, callback_string: str) -> 'AdminCallbackData':
        """Parse callback string to model"""
        parts = callback_string.split(":")
        
        if len(parts) < 2 or parts[0] != "admin":
            raise ValueError(f"Invalid admin callback: {callback_string}")
        
        action = AdminAction(parts[1])
        section = parts[2] if len(parts) > 2 else None
        subsection = parts[3] if len(parts) > 3 else None
        target = parts[4] if len(parts) > 4 else None
        
        # Decode params if present
        params = {}
        if len(parts) > 5:
            try:
                import json
                import base64
                params_decoded = base64.b64decode(parts[5]).decode()
                params = json.loads(params_decoded)
            except Exception as e:
                logger.warning("Failed to decode callback params", error=str(e))
        
        return cls(
            action=action,
            section=section,
            subsection=subsection,
            target=target,
            params=params
        )

# === CALLBACK HANDLER SYSTEM ===

class CallbackHandler(ABC):
    """Abstract base class for callback handlers"""
    
    @abstractmethod
    async def handle(self, callback_query: CallbackQuery, data: AdminCallbackData) -> Any:
        """Handle the callback"""
        pass
    
    @abstractmethod
    def can_handle(self, data: AdminCallbackData) -> bool:
        """Check if this handler can process the callback"""
        pass

@dataclass
class CallbackRoute:
    """Defines a callback route"""
    pattern: AdminAction
    handler: CallbackHandler
    permission_required: Optional[str] = None
    rate_limit: Optional[int] = None  # requests per minute
    description: str = ""

class CallbackRouter:
    """Elite callback router with advanced features"""
    
    def __init__(self):
        self.routes: List[CallbackRoute] = []
        self.middleware: List[Callable] = []
        self.rate_limits: Dict[str, List[datetime]] = {}
        self.performance_stats: Dict[str, List[float]] = {}
    
    def add_route(self, pattern: AdminAction, handler: CallbackHandler, 
                 permission_required: str = None, rate_limit: int = None, 
                 description: str = ""):
        """Add a callback route"""
        route = CallbackRoute(
            pattern=pattern,
            handler=handler,
            permission_required=permission_required,
            rate_limit=rate_limit,
            description=description
        )
        self.routes.append(route)
        logger.info("Callback route registered", pattern=pattern.value, description=description)
    
    def add_middleware(self, middleware_func: Callable):
        """Add middleware function"""
        self.middleware.append(middleware_func)
    
    def _check_rate_limit(self, user_id: int, action: str, limit: int) -> bool:
        """Check if user is within rate limit"""
        key = f"{user_id}:{action}"
        now = datetime.now()
        
        # Clean old entries
        if key in self.rate_limits:
            self.rate_limits[key] = [
                timestamp for timestamp in self.rate_limits[key]
                if (now - timestamp).total_seconds() < 60  # Keep last minute
            ]
        else:
            self.rate_limits[key] = []
        
        # Check limit
        if len(self.rate_limits[key]) >= limit:
            return False
        
        # Add current request
        self.rate_limits[key].append(now)
        return True
    
    def _record_performance(self, action: str, duration: float):
        """Record performance metrics"""
        if action not in self.performance_stats:
            self.performance_stats[action] = []
        
        self.performance_stats[action].append(duration)
        
        # Keep only recent entries
        if len(self.performance_stats[action]) > 100:
            self.performance_stats[action] = self.performance_stats[action][-100:]
    
    async def route(self, callback_query: CallbackQuery) -> Any:
        """Route callback to appropriate handler"""
        start_time = datetime.now()
        
        try:
            # Parse callback data
            data = AdminCallbackData.from_callback_string(callback_query.data)
            data.user_id = callback_query.from_user.id
            
            # Find matching route
            route = None
            for r in self.routes:
                if r.pattern == data.action:
                    route = r
                    break
            
            if not route:
                logger.warning("No route found for callback", action=data.action.value)
                return await self._handle_unknown_callback(callback_query, data)
            
            # Check rate limit
            if route.rate_limit:
                if not self._check_rate_limit(data.user_id, data.action.value, route.rate_limit):
                    logger.warning("Rate limit exceeded", user_id=data.user_id, action=data.action.value)
                    return await self._handle_rate_limit_exceeded(callback_query, data)
            
            # Apply middleware
            for middleware in self.middleware:
                result = await middleware(callback_query, data)
                if result is False:  # Middleware can block execution
                    return None
            
            # Execute handler
            result = await route.handler.handle(callback_query, data)
            
            # Record performance
            duration = (datetime.now() - start_time).total_seconds()
            self._record_performance(data.action.value, duration)
            
            logger.info("Callback handled successfully", 
                       action=data.action.value, 
                       duration_ms=duration * 1000,
                       user_id=data.user_id)
            
            return result
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error("Callback handling failed", 
                        error=str(e), 
                        duration_ms=duration * 1000,
                        callback_data=callback_query.data)
            return await self._handle_error(callback_query, e)
    
    async def _handle_unknown_callback(self, callback_query: CallbackQuery, data: AdminCallbackData):
        """Handle unknown callback"""
        await callback_query.answer("❌ Acción desconocida")
        return None
    
    async def _handle_rate_limit_exceeded(self, callback_query: CallbackQuery, data: AdminCallbackData):
        """Handle rate limit exceeded"""
        await callback_query.answer("🚫 Demasiadas acciones. Espera un momento.")
        return None
    
    async def _handle_error(self, callback_query: CallbackQuery, error: Exception):
        """Handle callback error"""
        await callback_query.answer("⚠️ Error interno. Intenta de nuevo.")
        return None
    
    def get_performance_stats(self) -> Dict[str, Dict[str, float]]:
        """Get performance statistics"""
        stats = {}
        
        for action, durations in self.performance_stats.items():
            if durations:
                stats[action] = {
                    "avg_ms": (sum(durations) / len(durations)) * 1000,
                    "max_ms": max(durations) * 1000,
                    "min_ms": min(durations) * 1000,
                    "total_calls": len(durations)
                }
        
        return stats
    
    def get_routes_info(self) -> List[Dict[str, Any]]:
        """Get information about registered routes"""
        return [
            {
                "pattern": route.pattern.value,
                "permission": route.permission_required,
                "rate_limit": route.rate_limit,
                "description": route.description
            }
            for route in self.routes
        ]

# === QUICK CALLBACK BUILDERS ===

def create_navigation_callback(action: AdminAction, section: str = None, subsection: str = None) -> str:
    """Quick builder for navigation callbacks"""
    data = AdminCallbackData(
        action=action,
        section=section,
        subsection=subsection
    )
    return data.to_callback_string()

def create_action_callback(action: AdminAction, target: str = None, **params) -> str:
    """Quick builder for action callbacks"""
    data = AdminCallbackData(
        action=action,
        target=target,
        params=params
    )
    return data.to_callback_string()

def create_section_callback(section: str) -> str:
    """Create callback for section navigation"""
    return create_navigation_callback(AdminAction.SECTION, section=section)

def create_subsection_callback(section: str, subsection: str) -> str:
    """Create callback for subsection navigation"""
    return create_navigation_callback(AdminAction.SUBSECTION, section=section, subsection=subsection)

def create_back_callback(to_section: str = None) -> str:
    """Create back navigation callback"""
    return create_navigation_callback(AdminAction.BACK, section=to_section)

def create_refresh_callback(target: str = None) -> str:
    """Create refresh callback"""
    return create_action_callback(AdminAction.REFRESH, target=target)

# === SPECIALIZED HANDLERS ===

class NavigationHandler(CallbackHandler):
    """Handler for navigation actions"""
    
    def __init__(self, admin_system):
        self.admin_system = admin_system
    
    async def handle(self, callback_query: CallbackQuery, data: AdminCallbackData) -> Any:
        """Handle navigation callback"""
        user_id = callback_query.from_user.id
        
        if data.action == AdminAction.MAIN:
            text, keyboard = await self.admin_system.create_admin_main_interface(user_id)
            
        elif data.action == AdminAction.SECTION:
            text, keyboard = await self.admin_system.create_section_interface(user_id, data.section)
            
        elif data.action == AdminAction.SUBSECTION:
            text, keyboard = await self.admin_system.create_subsection_interface(
                user_id, data.section, data.subsection
            )
            
        elif data.action == AdminAction.BACK:
            # Smart back navigation
            context = await self.admin_system.get_admin_context(user_id)
            if context.current_subsection:
                # Back to section
                text, keyboard = await self.admin_system.create_section_interface(
                    user_id, context.current_section
                )
            elif context.current_section:
                # Back to main
                text, keyboard = await self.admin_system.create_admin_main_interface(user_id)
            else:
                # Already at main
                text, keyboard = await self.admin_system.create_admin_main_interface(user_id)
        
        else:
            raise ValueError(f"Unknown navigation action: {data.action}")
        
        # Update message
        await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
        await callback_query.answer()
        
        return True
    
    def can_handle(self, data: AdminCallbackData) -> bool:
        """Check if can handle navigation"""
        return data.action in [AdminAction.MAIN, AdminAction.SECTION, AdminAction.SUBSECTION, AdminAction.BACK]

class ActionHandler(CallbackHandler):
    """Handler for admin actions"""
    
    def __init__(self, admin_system):
        self.admin_system = admin_system
    
    async def handle(self, callback_query: CallbackQuery, data: AdminCallbackData) -> Any:
        """Handle action callback"""
        user_id = callback_query.from_user.id
        
        # Execute specific action based on type
        if data.action == AdminAction.REFRESH:
            # Refresh current view
            context = await self.admin_system.get_admin_context(user_id)
            
            if context.current_subsection:
                text, keyboard = await self.admin_system.create_subsection_interface(
                    user_id, context.current_section, context.current_subsection
                )
            elif context.current_section:
                text, keyboard = await self.admin_system.create_section_interface(
                    user_id, context.current_section
                )
            else:
                text, keyboard = await self.admin_system.create_admin_main_interface(user_id)
            
            await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
            await callback_query.answer("🔄 Actualizado")
            
        elif data.action == AdminAction.SYSTEM_HEALTH:
            # Show system health
            health_info = await self.admin_system.services_integration.get_system_overview()
            await callback_query.answer(f"🟢 Sistema: {health_info['overview']['status']}")
            
        else:
            # Other actions...
            await callback_query.answer(f"⚡ Acción: {data.action.value}")
        
        return True
    
    def can_handle(self, data: AdminCallbackData) -> bool:
        """Check if can handle action"""
        return data.action not in [AdminAction.MAIN, AdminAction.SECTION, AdminAction.SUBSECTION, AdminAction.BACK]

# === MIDDLEWARE FUNCTIONS ===

async def permission_middleware(callback_query: CallbackQuery, data: AdminCallbackData) -> bool:
    """Check user permissions"""
    # This would integrate with your permission system
    # For now, return True (allow all)
    return True

async def logging_middleware(callback_query: CallbackQuery, data: AdminCallbackData) -> bool:
    """Log all admin actions"""
    logger.info("Admin action", 
               user_id=data.user_id,
               action=data.action.value,
               section=data.section,
               subsection=data.subsection)
    return True

async def analytics_middleware(callback_query: CallbackQuery, data: AdminCallbackData) -> bool:
    """Track analytics for admin usage"""
    # Track admin panel usage for insights
    return True

# === GLOBAL ROUTER INSTANCE ===

# This will be initialized in the main admin system
elite_callback_router: Optional[CallbackRouter] = None

def get_callback_router() -> CallbackRouter:
    """Get the global callback router"""
    global elite_callback_router
    if elite_callback_router is None:
        elite_callback_router = CallbackRouter()
        
        # Add default middleware
        elite_callback_router.add_middleware(permission_middleware)
        elite_callback_router.add_middleware(logging_middleware)
        elite_callback_router.add_middleware(analytics_middleware)
    
    return elite_callback_router