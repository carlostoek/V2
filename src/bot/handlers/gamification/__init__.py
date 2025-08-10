from src.bot.handlers.gamification.misiones import register_misiones_handler
from src.bot.handlers.gamification.progress import register_mission_progress_handlers
from src.bot.handlers.gamification.daily_rewards import register_daily_rewards_handler
from src.bot.handlers.gamification.shop import register_shop_handler
from src.bot.handlers.gamification.trivia import register_trivia_handler
from src.bot.handlers.gamification.main_menu import register_gamification_main_handler

def register_gamification_handlers(dp, event_bus, gamification_service):
    """Registra todos los handlers relacionados con gamificación."""
    register_misiones_handler(dp, gamification_service)
    register_mission_progress_handlers(dp, gamification_service)
    register_daily_rewards_handler(dp, gamification_service)
    register_shop_handler(dp, gamification_service)
    register_trivia_handler(dp, gamification_service)
    register_gamification_main_handler(dp, gamification_service)