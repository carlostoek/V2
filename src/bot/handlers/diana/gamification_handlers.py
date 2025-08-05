# src/bot/handlers/diana/gamification_handlers.py

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from src.bot.core.diana_master_system import DianaMasterInterface
from src.modules.gamification.service import GamificationService
from src.utils.sexy_logger import logger

gamification_diana_router = Router(name="gamification_diana_handlers")

@gamification_diana_router.callback_query(F.data == "diana:progress_tracker")
async def handle_progress_tracker(callback_query: CallbackQuery, gamification_service: GamificationService):
    """
    Muestra un dashboard de progreso avanzado al usuario.
    """
    user_id = callback_query.from_user.id
    logger.info(f"User {user_id} triggered diana:progress_tracker")
    
    stats = await gamification_service.get_user_stats(user_id)
    
    text = (
        "📊 **Dashboard de Progreso** 📊\n\n"
        f"Nivel: {stats.get('level', 1)}\n"
        f"Puntos de Experiencia (XP): {stats.get('xp', 0)} / {stats.get('next_level_xp', 100)}\n"
        f"Besitos (Moneda): {stats.get('points', 0)} 💋\n"
        f"Racha Diaria: {stats.get('streak', 0)} 🔥\n\n"
        "¡Sigue así para desbloquear más recompensas!"
    )
    
    await callback_query.message.edit_text(text, parse_mode="Markdown")
    await callback_query.answer()

@gamification_diana_router.callback_query(F.data == "diana:pro_dashboard")
async def handle_pro_dashboard(callback_query: CallbackQuery, gamification_service: GamificationService):
    """
    Muestra un panel de control optimizado para usuarios avanzados.
    """
    user_id = callback_query.from_user.id
    logger.info(f"User {user_id} triggered diana:pro_dashboard")

    # Aquí iría una lógica más compleja para un dashboard pro
    stats = await gamification_service.get_user_stats(user_id)
    
    text = (
        "🚀 **Dashboard PRO** 🚀\n\n"
        "**Estadísticas Clave:**\n"
        f"  - Eficiencia de Misiones: {stats.get('mission_efficiency', 'N/A')}%\n"
        f"  - Tasa de Éxito en Trivia: {stats.get('trivia_accuracy', 'N/A')}%\n"
        f"  - Ratio Gasto/Ganancia: {stats.get('economy_ratio', 'N/A')}\n\n"
        "**Análisis de Rendimiento:**\n"
        "📈 Tu rendimiento está por encima del promedio. ¡Excelente trabajo!"
    )
    
    await callback_query.message.edit_text(text, parse_mode="Markdown")
    await callback_query.answer()

@gamification_diana_router.callback_query(F.data == "diana:explore_mode")
async def handle_explore_mode(callback_query: CallbackQuery, diana_interface: DianaMasterInterface):
    """
    Activa un modo de exploración gamificado.
    """
    user_id = callback_query.from_user.id
    logger.info(f"User {user_id} triggered diana:explore_mode")

    # Lógica para el modo exploración
    text = (
        "🗺️ **Modo Exploración Activado** 🗺️\n\n"
        "Has encontrado un cofre del tesoro escondido. ¿Qué quieres hacer?\n\n"
        "A) Abrirlo con una llave (coste: 50 besitos)\n"
        "B) Intentar forzar la cerradura (riesgoso)\n"
        "C) Dejarlo y seguir explorando"
    )
    
    # Este es un ejemplo, podría tener su propio teclado y lógica de estado
    await callback_query.message.edit_text(text, parse_mode="Markdown")
    await callback_query.answer("¡La aventura te espera!")


def register_gamification_diana_handlers(router: Router):
    """Registra los handlers de gamificación de Diana en el router principal."""
    router.include_router(gamification_diana_router)
    logger.info("Gamification Diana Handlers registered.")
