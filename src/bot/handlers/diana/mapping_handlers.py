from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable

from src.modules.gamification.service import GamificationService
from src.modules.shop.service import ShopService
from src.modules.narrative.service import NarrativeService
from src.modules.trivia.service import TriviaService
from src.modules.daily_rewards.service import DailyRewardsService
from src.bot.handlers.gamification.misiones import handle_misiones as show_missions_hub
from src.bot.handlers.user.shop import cmd_shop as show_epic_shop
from src.bot.handlers.narrative.navigation import show_current_fragment as show_narrative_hub
from src.bot.handlers.user.trivia import cmd_trivia as show_trivia_challenge
from src.bot.handlers.user.daily_rewards import cmd_daily_reward as show_daily_gift

# --- Middleware para Inyección de Dependencias ---

class ServiceInjectorMiddleware(BaseMiddleware):
    """
    Middleware para inyectar instancias de servicios en los handlers.
    """
    def __init__(self, services: Dict[str, Any]):
        super().__init__()
        self.services = services

    async def __call__(
        self,
        handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        # Inyecta los servicios requeridos por el handler en el diccionario de datos.
        # El handler los recibirá como argumentos.
        data.update(self.services)
        return await handler(event, data)

# --- Router de Mapeo ---

# Este router conectará los callbacks de Diana con handlers existentes.
diana_mapping_router = Router(name="diana_mapping_handlers")


@diana_mapping_router.callback_query(F.data == "diana:missions_hub")
async def handle_diana_missions_hub(callback_query: CallbackQuery, gamification_service: GamificationService):
    """
    Mapea el callback 'diana:missions_hub' al handler de misiones existente.
    """
    await show_missions_hub(callback_query.message, gamification_service)
    await callback_query.answer()

@diana_mapping_router.callback_query(F.data == "diana:epic_shop")
async def handle_diana_epic_shop(callback_query: CallbackQuery, shop_service: ShopService):
    """
    Mapea el callback 'diana:epic_shop' al handler de la tienda existente.
    """
    await show_epic_shop(callback_query.message, shop_service)
    await callback_query.answer()

@diana_mapping_router.callback_query(F.data == "diana:narrative_hub")
async def handle_diana_narrative_hub(callback_query: CallbackQuery, narrative_service: NarrativeService):
    """
    Mapea el callback 'diana:narrative_hub' al hub de narrativa.
    """
    await show_narrative_hub(callback_query, narrative_service)
    await callback_query.answer()

@diana_mapping_router.callback_query(F.data == "diana:trivia_challenge")
async def handle_diana_trivia_challenge(callback_query: CallbackQuery, trivia_service: TriviaService):
    """
    Mapea el callback 'diana:trivia_challenge' al handler de trivia.
    """
    await show_trivia_challenge(callback_query.message, trivia_service)
    await callback_query.answer()

@diana_mapping_router.callback_query(F.data == "diana:daily_gift")
async def handle_diana_daily_gift(callback_query: CallbackQuery, daily_rewards_service: DailyRewardsService):
    """
    Mapea el callback 'diana:daily_gift' al handler de regalos diarios.
    """
    await show_daily_gift(callback_query.message, daily_rewards_service)
    await callback_query.answer()

# Aquí se añadirán más mapeos...

def register_diana_mapping_handlers(router: Router, services: dict):
    """
    Registra los handlers de mapeo en el router principal de Diana
    e inyecta las dependencias de servicio necesarias.
    """
    # Inyectar dependencias a los handlers de este router
    diana_mapping_router.callback_query.middleware(
        ServiceInjectorMiddleware(services)
    )
    
    router.include_router(diana_mapping_router)
