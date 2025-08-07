"""
🚀 DIANA ADMIN LIVE INTEGRATION
===============================

The final integration layer that brings everything together.
Live bot integration with all Silicon Valley features activated.

Author: The Most Epic Silicon Valley Developer
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import structlog

from aiogram import Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

# Import all our elite components
from .diana_admin_elite import DianaAdminElite, register_diana_admin_elite
from .diana_admin_elite_ui import theme_manager, ui_cache
from .diana_admin_callbacks import get_callback_router, AdminCallbackData, AdminAction
from .diana_admin_analytics import get_analytics_engine, get_real_time_updater
from .diana_admin_power_features import (
    command_palette, guided_tours, shortcuts_manager, contextual_help,
    build_command_palette_interface, build_guided_tour_interface, build_contextual_help_interface
)

logger = structlog.get_logger()

# === LIVE INTEGRATION SYSTEM ===

class DianaAdminLiveSystem:
    """Complete live integration system"""
    
    def __init__(self, dp: Dispatcher, services: Dict[str, Any]):
        self.dp = dp
        self.services = services
        
        # Initialize elite admin system
        self.admin_system = register_diana_admin_elite(dp, services)
        
        # Get components
        self.analytics = get_analytics_engine()
        self.real_time_updater = get_real_time_updater()
        self.callback_router = get_callback_router()
        
        # Enhanced features
        self.command_palette = command_palette
        self.guided_tours = guided_tours
        self.shortcuts_manager = shortcuts_manager
        self.contextual_help = contextual_help
        
        # Performance tracking
        self.performance_metrics = {}
        
        # Initialize live features
        self._initialize_live_features()
        
        logger.info("🎭 Diana Admin Live System initialized with all elite features")
    
    def _initialize_live_features(self):
        """Initialize all live features"""
        
        # Enhanced callback routing with power features
        self._setup_power_user_handlers()
        
        # Real-time analytics
        self._setup_analytics_tracking()
        
        # Performance monitoring
        self._setup_performance_monitoring()
        
        logger.info("All live features initialized successfully")
    
    def _setup_power_user_handlers(self):
        """Setup handlers for power user features"""
        
        # Command palette handlers
        @self.dp.message(Command("palette"))
        @self.dp.message(F.text.startswith("/cmd "))
        async def command_palette_handler(message: Message):
            """Handle command palette access"""
            user_id = message.from_user.id
            
            # Check admin permission
            if not await self.admin_system.check_admin_permission(user_id):
                await message.answer("🚫 Sin permisos de administrador")
                return
            
            # Extract query if using /cmd
            query = ""
            if message.text.startswith("/cmd "):
                query = message.text[5:].strip()
            
            # Search commands
            commands = self.command_palette.search_commands(query, user_id)
            
            # Build interface
            text, keyboard = build_command_palette_interface(commands, query)
            
            await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")
            
            # Track usage
            self.analytics.increment_metric("command_palette_opens")
            self.analytics.track_event("command_palette_used", {"query": query, "user_id": user_id})
        
        # Guided tour handlers
        @self.dp.message(Command("tour"))
        async def guided_tour_handler(message: Message):
            """Handle guided tour start"""
            user_id = message.from_user.id
            
            if not await self.admin_system.check_admin_permission(user_id):
                await message.answer("🚫 Sin permisos de administrador")
                return
            
            # Start basic tour
            first_step = self.guided_tours.start_tour(user_id, "basic_admin")
            if first_step:
                text, keyboard = build_guided_tour_interface(first_step, 1, len(self.guided_tours.tours["basic_admin"]))
                await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")
                
                self.analytics.increment_metric("guided_tours_started")
                self.analytics.track_event("tour_started", {"tour": "basic_admin", "user_id": user_id})
        
        # Shortcuts handler
        @self.dp.message(F.text.startswith("/"))
        async def shortcut_handler(message: Message):
            """Handle admin shortcuts"""
            user_id = message.from_user.id
            command = message.text[1:].strip().lower()
            
            if not await self.admin_system.check_admin_permission(user_id):
                return  # Don't respond to non-admin shortcuts
            
            shortcuts = self.shortcuts_manager.get_shortcuts_for_user(user_id)
            
            if command in shortcuts:
                # Execute shortcut
                callback_data = shortcuts[command]
                
                # Create a mock callback query for processing
                mock_callback = type('MockCallback', (), {
                    'data': callback_data,
                    'from_user': message.from_user,
                    'message': message,
                    'bot': message.bot,
                    'answer': lambda text="": asyncio.create_task(message.answer(f"⚡ {text}"))
                })()
                
                try:
                    await self.admin_system.handle_elite_callback(mock_callback)
                    self.analytics.increment_metric("shortcuts_used")
                    self.shortcuts_manager.track_usage(command)
                except Exception as e:
                    logger.error("Shortcut execution failed", shortcut=command, error=str(e))
    
    def _setup_analytics_tracking(self):
        """Setup comprehensive analytics tracking"""
        
        # Track all admin actions automatically
        original_handle_callback = self.admin_system.handle_elite_callback
        
        async def tracked_handle_callback(callback_query: CallbackQuery):
            """Wrapper to track all callback analytics"""
            start_time = datetime.now()
            user_id = callback_query.from_user.id
            
            try:
                # Parse callback data for analytics
                data = AdminCallbackData.from_callback_string(callback_query.data)
                
                # Track action
                self.analytics.increment_metric("admin_actions_total")
                self.analytics.track_event("admin_action", {
                    "action": data.action.value,
                    "section": data.section,
                    "subsection": data.subsection,
                    "user_id": user_id
                })
                
                # Execute original handler
                result = await original_handle_callback(callback_query)
                
                # Track performance
                duration_ms = (datetime.now() - start_time).total_seconds() * 1000
                self.analytics.record_histogram("admin_response_time", duration_ms)
                
                # Update performance metrics
                self._update_performance_metrics(data.action.value, duration_ms)
                
                return result
                
            except Exception as e:
                # Track errors
                self.analytics.increment_metric("admin_errors_total")
                self.analytics.track_event("admin_error", {
                    "error": str(e),
                    "callback_data": callback_query.data,
                    "user_id": user_id
                })
                
                logger.error("Admin callback failed", error=str(e), callback_data=callback_query.data)
                await callback_query.answer("❌ Error interno")
        
        # Replace the handler
        self.admin_system.handle_elite_callback = tracked_handle_callback
    
    def _setup_performance_monitoring(self):
        """Setup performance monitoring"""
        
        # Monitor cache performance
        original_cache_get = ui_cache.get
        original_cache_set = ui_cache.set
        
        cache_hits = 0
        cache_misses = 0
        
        def tracked_cache_get(key: str):
            nonlocal cache_hits, cache_misses
            result = original_cache_get(key)
            if result:
                cache_hits += 1
            else:
                cache_misses += 1
            
            # Update metrics periodically
            total = cache_hits + cache_misses
            if total > 0 and total % 10 == 0:
                hit_rate = (cache_hits / total) * 100
                self.analytics.set_gauge("cache_hit_rate", hit_rate)
            
            return result
        
        def tracked_cache_set(key: str, value: Any, ttl: int = None):
            self.analytics.increment_metric("cache_sets")
            return original_cache_set(key, value, ttl)
        
        ui_cache.get = tracked_cache_get
        ui_cache.set = tracked_cache_set
    
    def _update_performance_metrics(self, action: str, duration_ms: float):
        """Update performance metrics"""
        if action not in self.performance_metrics:
            self.performance_metrics[action] = []
        
        self.performance_metrics[action].append(duration_ms)
        
        # Keep only last 100 measurements
        if len(self.performance_metrics[action]) > 100:
            self.performance_metrics[action] = self.performance_metrics[action][-100:]
        
        # Calculate and update average
        avg_ms = sum(self.performance_metrics[action]) / len(self.performance_metrics[action])
        self.analytics.set_gauge(f"avg_response_time_{action}", avg_ms)
    
    async def start_real_time_features(self):
        """Start real-time features"""
        try:
            # Start analytics real-time updates
            asyncio.create_task(self.real_time_updater.start_updates())
            
            # Start system health monitoring
            asyncio.create_task(self._system_health_monitor())
            
            logger.info("Real-time features started successfully")
            
        except Exception as e:
            logger.error("Failed to start real-time features", error=str(e))
    
    async def _system_health_monitor(self):
        """Monitor system health continuously"""
        while True:
            try:
                # Get system overview
                overview = await self.admin_system.services_integration.get_system_overview()
                
                if overview and "overview" in overview:
                    # Update health metrics
                    status = overview["overview"].get("status", "unknown")
                    health_score = 100 if status == "healthy" else 50 if status == "degraded" else 0
                    
                    self.analytics.set_gauge("system_health_score", health_score)
                    self.analytics.set_gauge("services_healthy", overview["overview"].get("healthy_services", 0))
                    
                    # Update active sessions
                    active_sessions = len(self.admin_system.admin_contexts)
                    self.analytics.set_gauge("admin_sessions_active", active_sessions)
                
                # Wait 30 seconds before next check
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error("Health monitoring failed", error=str(e))
                await asyncio.sleep(60)  # Wait longer on error
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        return {
            "active_sessions": len(self.admin_system.admin_contexts),
            "total_commands": len(self.command_palette.commands),
            "cache_size": len(ui_cache.cache),
            "performance_metrics": self.performance_metrics,
            "analytics": self.analytics.get_all_metrics(),
            "callback_performance": self.callback_router.get_performance_stats(),
            "uptime": datetime.now().isoformat()
        }

# === ENHANCED CALLBACK HANDLERS ===

class LiveAdminRouter:
    """Enhanced router with all live features"""
    
    def __init__(self, live_system: DianaAdminLiveSystem):
        self.live_system = live_system
        self.router = Router()
        self._setup_enhanced_handlers()
    
    def _setup_enhanced_handlers(self):
        """Setup all enhanced handlers"""
        
        @self.router.message(Command("admin"))
        async def enhanced_admin_command(message: Message):
            """Enhanced /admin command with analytics and features"""
            user_id = message.from_user.id
            
            # Check permissions
            if not await self.live_system.admin_system.check_admin_permission(user_id):
                await message.answer("🚫 Sin permisos de administrador")
                return
            
            # Track admin session start
            self.live_system.analytics.increment_metric("admin_sessions_started")
            self.live_system.analytics.track_event("admin_session_start", {"user_id": user_id})
            
            # Create main interface with all enhancements
            text, keyboard = await self.live_system.admin_system.create_admin_main_interface(user_id)
            
            sent_message = await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")
            
            # Show welcome tip for new users (could be based on user history)
            await asyncio.sleep(1)
            await message.answer(
                "💡 **Tips Rápidos:**\n"
                "• Usa `/palette` para la paleta de comandos\n"
                "• Usa `/tour` para un tour guiado\n"
                "• Usa `/vip`, `/gamif` como shortcuts\n"
                "• Todas las estadísticas se actualizan en tiempo real",
                parse_mode="Markdown"
            )
        
        @self.router.callback_query(F.data.startswith("admin:"))
        async def enhanced_callback_handler(callback: CallbackQuery):
            """Enhanced callback handler with all features"""
            try:
                # Parse callback data
                data = AdminCallbackData.from_callback_string(callback.data)
                
                # Handle special power user actions
                if data.action == AdminAction.HELP:
                    await self._handle_help_actions(callback, data)
                    return
                
                if data.action == AdminAction.THEME:
                    await self._handle_theme_actions(callback, data)
                    return
                
                # Route through main system
                await self.live_system.admin_system.handle_elite_callback(callback)
                
            except Exception as e:
                logger.error("Enhanced callback failed", error=str(e))
                await callback.answer("❌ Error interno")
        
        @self.router.message(Command("admin_stats"))
        async def admin_stats_command(message: Message):
            """Show admin system statistics"""
            user_id = message.from_user.id
            
            if not await self.live_system.admin_system.check_admin_permission(user_id):
                await message.answer("🚫 Sin permisos de administrador")
                return
            
            stats = self.live_system.get_system_stats()
            
            stats_text = f"""
🎭 **ESTADÍSTICAS DEL SISTEMA ADMIN**

**Sesiones Activas:** {stats['active_sessions']}
**Comandos Disponibles:** {stats['total_commands']}
**Cache Hits:** {len(stats.get('cache_size', 0))} entradas

**Rendimiento Promedio:**
"""
            
            for action, durations in stats.get('performance_metrics', {}).items():
                if durations:
                    avg = sum(durations) / len(durations)
                    stats_text += f"• {action}: {avg:.1f}ms\n"
            
            await message.answer(stats_text, parse_mode="Markdown")
    
    async def _handle_help_actions(self, callback: CallbackQuery, data: AdminCallbackData):
        """Handle help-related actions"""
        user_id = callback.from_user.id
        
        if data.target == "tour_basic":
            # Start basic tour
            first_step = self.live_system.guided_tours.start_tour(user_id, "basic_admin")
            if first_step:
                text, keyboard = build_guided_tour_interface(
                    first_step, 1, len(self.live_system.guided_tours.tours["basic_admin"])
                )
                await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
                await callback.answer("🎯 Tour iniciado")
        
        elif data.target == "command_palette":
            # Show command palette
            commands = self.live_system.command_palette.search_commands("", user_id)
            text, keyboard = build_command_palette_interface(commands)
            await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
            await callback.answer("⚡ Paleta abierta")
        
        else:
            # Show contextual help
            context = data.target or "main"
            text, keyboard = build_contextual_help_interface(context)
            await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
            await callback.answer("❓ Ayuda mostrada")
    
    async def _handle_theme_actions(self, callback: CallbackQuery, data: AdminCallbackData):
        """Handle theme switching"""
        user_id = callback.from_user.id
        
        # Show theme selector
        theme_options = theme_manager.get_theme_options()
        
        from .diana_admin_elite_ui import EliteUIBuilder
        builder = EliteUIBuilder()
        
        builder.header("🎨 SELECTOR DE TEMAS", "Personaliza tu experiencia visual", level=1)
        builder.alert("Selecciona tu tema preferido para el panel de administración", "info")
        
        builder.actions(theme_options, columns=2)
        builder.actions([
            {"text": "← Volver", "callback": "admin:main"}
        ], columns=1)
        
        text, keyboard = builder.build()
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
        await callback.answer("🎨 Selector de temas")

# === MAIN REGISTRATION FUNCTION ===

def initialize_diana_admin_live(dp: Dispatcher, services: Dict[str, Any]) -> DianaAdminLiveSystem:
    """Initialize the complete Diana Admin Live System"""
    
    logger.info("🚀 Initializing Diana Admin Live System...")
    
    # Create live system
    live_system = DianaAdminLiveSystem(dp, services)
    
    # Create enhanced router
    live_router = LiveAdminRouter(live_system)
    
    # Include the enhanced router
    dp.include_router(live_router.router)
    
    # Start real-time features
    asyncio.create_task(live_system.start_real_time_features())
    
    logger.info("🎭 Diana Admin Live System fully initialized and ready!")
    logger.info("✨ All Silicon Valley features are now active!")
    
    return live_system