# src/bot/handlers/diana/core_handlers.py

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from src.bot.core.diana_master_system import DianaMasterInterface
from src.utils.sexy_logger import logger

core_diana_router = Router(name="core_diana_handlers")

@core_diana_router.callback_query(F.data == "diana:refresh")
async def handle_diana_refresh(callback_query: CallbackQuery, state: FSMContext, diana_interface: DianaMasterInterface):
    """
    Maneja el callback 'diana:refresh', actualizando la interfaz adaptativa.
    """
    logger.info(f"User {callback_query.from_user.id} triggered diana:refresh")
    await callback_query.answer("🔄 Refrescando...")
    
    # Llama a la interfaz de Diana para obtener el menú actualizado
    await diana_interface.show_adaptive_menu(callback_query.from_user.id, state)

@core_diana_router.callback_query(F.data == "diana:smart_help")
async def handle_diana_smart_help(callback_query: CallbackQuery, state: FSMContext, diana_interface: DianaMasterInterface):
    """
    Maneja el callback 'diana:smart_help', proporcionando ayuda contextual.
    """
    user_id = callback_query.from_user.id
    logger.info(f"User {user_id} triggered diana:smart_help")
    
    # Aquí iría la lógica para determinar la ayuda contextual.
    # Por ahora, un mensaje genérico.
    help_text = await diana_interface.context_engine.get_contextual_help(user_id, state)
    
    await callback_query.answer()
    await callback_query.message.answer(help_text, parse_mode="Markdown")

@core_diana_router.callback_query(F.data == "diana:surprise_me")
async def handle_diana_surprise_me(callback_query: CallbackQuery, state: FSMContext, diana_interface: DianaMasterInterface):
    """
    Maneja el callback 'diana:surprise_me', ofreciendo una función sorpresa.
    """
    user_id = callback_query.from_user.id
    logger.info(f"User {user_id} triggered diana:surprise_me")
    
    # Lógica para la función sorpresa.
    surprise_text = await diana_interface.context_engine.get_surprise_feature(user_id, state)
    
    await callback_query.answer("🎲 ¡Sorpresa!")
    await callback_query.message.answer(surprise_text, parse_mode="Markdown")

def register_core_diana_handlers(router: Router):
    """Registra los handlers del core de Diana en el router principal."""
    router.include_router(core_diana_router)
    logger.info("Core Diana Handlers registered.")
