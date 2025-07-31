from src.bot.handlers.gamification.misiones import register_misiones_handler
from src.bot.handlers.gamification.progress import register_mission_progress_handlers

def register_gamification_handlers(dp, event_bus, gamification_service):
    """Registra todos los handlers relacionados con gamificación."""
    register_misiones_handler(dp, gamification_service)
    register_mission_progress_handlers(dp, gamification_service)