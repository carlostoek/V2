from src.bot.handlers.narrative.mochila import register_mochila_handler
from src.bot.handlers.narrative.navigation import register_narrative_navigation_handlers

def register_narrative_handlers(dp, event_bus, narrative_service):
    """Registra todos los handlers relacionados con narrativa."""
    register_mochila_handler(dp, narrative_service)
    register_narrative_navigation_handlers(dp, narrative_service)