# DIANA MASTER SYSTEM REVOLUTION - START HANDLER ELIMINATED
# The start handler has been completely replaced by Diana Master System
# from src.bot.handlers.user.start import register_start_handler  # ← ELIMINATED
from src.bot.handlers.user.help import register_help_handler
from src.bot.handlers.user.profile import register_profile_handlers

def register_user_handlers(dp, event_bus, gamification_service, admin_service):
    """Registra todos los handlers relacionados con usuarios."""
    # register_start_handler(dp, event_bus, admin_service)  # ← ELIMINATED - Diana Master System handles /start
    register_help_handler(dp)
    register_profile_handlers(dp, gamification_service)