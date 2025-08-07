"""
🔗 DIANA ADMIN INTEGRATION
=========================

Integration module to connect Diana Admin Master System with the main bot.
This module handles registration, configuration, and lifecycle management.
"""

from typing import Dict, Any, Optional
import structlog

from .diana_admin_master import register_diana_admin_master, DianaAdminMaster
from .diana_admin_services_integration import DianaAdminServicesIntegration
from .diana_admin_security import DianaAdminSecurity

logger = structlog.get_logger()

class DianaAdminIntegration:
    """
    🔗 DIANA ADMIN INTEGRATION
    
    Manages the integration between Diana Admin Master System and the main bot.
    """
    
    def __init__(self):
        self.admin_system: Optional[DianaAdminMaster] = None
        self.is_initialized = False
        
    def integrate_with_bot(self, dp, services: Dict[str, Any]) -> DianaAdminMaster:
        """
        Integrate Diana Admin Master System with the bot.
        
        Args:
            dp: Aiogram Dispatcher
            services: Dictionary of available services
            
        Returns:
            Initialized DianaAdminMaster instance
        """
        try:
            logger.info("🎭 Initializing Diana Admin Master System...")
            
            # Validate required services
            self._validate_services(services)
            
            # Register admin system with dispatcher
            self.admin_system = register_diana_admin_master(dp, services)
            
            # Mark as initialized
            self.is_initialized = True
            
            logger.info(
                "✅ Diana Admin Master System integrated successfully",
                services_count=len(services),
                system_ready=True
            )
            
            return self.admin_system
            
        except Exception as e:
            logger.error(
                "❌ Failed to integrate Diana Admin Master System",
                error=str(e)
            )
            raise
    
    def _validate_services(self, services: Dict[str, Any]) -> None:
        """Validate that required services are available"""
        required_services = ['gamification', 'admin', 'daily_rewards']
        optional_services = ['narrative', 'shop', 'trivia', 'event_bus']
        
        missing_required = []
        for service in required_services:
            if service not in services:
                missing_required.append(service)
        
        if missing_required:
            logger.warning(
                "⚠️ Missing required services for admin system",
                missing=missing_required
            )
            # Don't fail, but log the issue
        
        available_services = [s for s in required_services + optional_services if s in services]
        logger.info(
            "🔧 Service validation complete",
            available_services=available_services,
            total_count=len(available_services)
        )
    
    def get_admin_system(self) -> Optional[DianaAdminMaster]:
        """Get the admin system instance"""
        return self.admin_system
    
    def is_ready(self) -> bool:
        """Check if admin system is ready"""
        return self.is_initialized and self.admin_system is not None
    
    async def shutdown(self):
        """Gracefully shutdown admin system"""
        if self.admin_system:
            logger.info("🔄 Shutting down Diana Admin Master System...")
            
            # Invalidate all active sessions
            for user_id in list(self.admin_system.security.active_sessions.keys()):
                await self.admin_system.security.invalidate_session(user_id)
            
            # Log shutdown
            await self.admin_system.security.log_admin_action(
                0, "system_shutdown", result="success", risk_level="low"
            )
            
            logger.info("✅ Diana Admin Master System shutdown complete")

# Global integration instance
_admin_integration: Optional[DianaAdminIntegration] = None

def get_admin_integration() -> DianaAdminIntegration:
    """Get the global admin integration instance"""
    global _admin_integration
    if _admin_integration is None:
        _admin_integration = DianaAdminIntegration()
    return _admin_integration

def initialize_admin_system(dp, services: Dict[str, Any]) -> DianaAdminMaster:
    """
    Initialize Diana Admin Master System.
    
    This is the main entry point for integrating the admin system.
    
    Args:
        dp: Aiogram Dispatcher
        services: Available bot services
        
    Returns:
        DianaAdminMaster instance
        
    Example:
        ```python
        from src.bot.core.diana_admin_integration import initialize_admin_system
        
        services = {
            'gamification': gamification_service,
            'admin': admin_service,
            'daily_rewards': daily_rewards_service,
            # ... other services
        }
        
        admin_system = initialize_admin_system(dp, services)
        ```
    """
    integration = get_admin_integration()
    return integration.integrate_with_bot(dp, services)

async def shutdown_admin_system():
    """Shutdown Diana Admin Master System"""
    integration = get_admin_integration()
    await integration.shutdown()