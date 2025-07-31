from aiogram import types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from src.modules.gamification.service import GamificationService
from src.bot.keyboards.keyboard_factory import KeyboardFactory

async def handle_profile_command(message: types.Message, gamification_service: GamificationService):
    """
    Maneja el comando /profile del bot.
    
    Muestra el perfil del usuario con sus puntos y estadísticas.
    """
    user_id = message.from_user.id
    points = gamification_service.get_points(user_id)
    
    profile_text = (
        "**🏆 Tu Perfil 🏆**\n\n"
        f"**Puntos:** {points}\n"
        "\n"
        "**Logros desbloqueados:** 0/10\n"
        "**Misiones completadas:** 0/5\n"
        "**Fragmentos de historia descubiertos:** 0/20\n"
        "\n"
        "Selecciona una opción para ver más detalles:"
    )
    
    await message.answer(
        profile_text,
        parse_mode="Markdown",
        reply_markup=KeyboardFactory.main_menu()
    )

async def handle_profile_callback(query: types.CallbackQuery, gamification_service: GamificationService):
    """
    Maneja el callback de perfil desde el menú principal.
    
    Muestra el perfil del usuario con sus puntos y estadísticas.
    """
    user_id = query.from_user.id
    points = gamification_service.get_points(user_id)
    
    profile_text = (
        "**🏆 Tu Perfil 🏆**\n\n"
        f"**Puntos:** {points}\n"
        "\n"
        "**Logros desbloqueados:** 0/10\n"
        "**Misiones completadas:** 0/5\n"
        "**Fragmentos de historia descubiertos:** 0/20\n"
        "\n"
        "Selecciona una opción para ver más detalles:"
    )
    
    # Crear un teclado inline para el perfil
    buttons = [
        [{"text": "🏅 Ver Logros", "callback_data": "profile:achievements"}],
        [{"text": "📊 Estadísticas", "callback_data": "profile:stats"}],
        [{"text": "⬅️ Volver al Menú Principal", "callback_data": "profile:back_to_main"}]
    ]
    keyboard = KeyboardFactory.create_inline(buttons)
    
    await query.message.edit_text(
        profile_text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    await query.answer()

async def handle_profile_achievements(query: types.CallbackQuery):
    """Maneja la visualización de logros del perfil."""
    text = (
        "**🏅 Tus Logros 🏅**\n\n"
        "No has desbloqueado ningún logro todavía.\n\n"
        "Completa misiones y avanza en la historia para desbloquear logros."
    )
    
    await query.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=KeyboardFactory.back_button("profile:back_to_profile")
    )
    await query.answer()

async def handle_profile_stats(query: types.CallbackQuery, gamification_service: GamificationService):
    """Maneja la visualización de estadísticas del perfil."""
    user_id = query.from_user.id
    points = gamification_service.get_points(user_id)
    
    text = (
        "**📊 Tus Estadísticas 📊**\n\n"
        f"**Puntos totales:** {points}\n"
        "**Interacciones:** 1\n"
        "**Tiempo en el bot:** 0 días\n"
        "**Nivel actual:** 1\n"
        "**Siguiente nivel:** 50 puntos"
    )
    
    await query.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=KeyboardFactory.back_button("profile:back_to_profile")
    )
    await query.answer()

async def handle_profile_back(query: types.CallbackQuery):
    """Maneja los callbacks de navegación del perfil."""
    callback_data = query.data
    
    if callback_data == "profile:back_to_profile":
        # Volver al perfil principal
        await handle_profile_callback(query, query.bot.gamification_service)
    
    elif callback_data == "profile:back_to_main":
        # Volver al menú principal
        await query.message.edit_text(
            "¡Bienvenido a Diana V2! ¿Qué te gustaría hacer hoy?",
            reply_markup=KeyboardFactory.main_menu()
        )
        await query.answer()

def register_profile_handlers(dp, gamification_service):
    """Registra los handlers de perfil en el dispatcher."""
    # Comando /profile
    dp.message.register(
        lambda message: handle_profile_command(message, gamification_service),
        Command("profile")
    )
    
    # Callback desde el menú principal
    dp.callback_query.register(
        lambda query: handle_profile_callback(query, gamification_service),
        F.data == "main_menu:profile"
    )
    
    # Callbacks de navegación del perfil
    dp.callback_query.register(
        handle_profile_achievements,
        F.data == "profile:achievements"
    )
    
    dp.callback_query.register(
        lambda query: handle_profile_stats(query, gamification_service),
        F.data == "profile:stats"
    )
    
    dp.callback_query.register(
        handle_profile_back,
        lambda c: c.data in ["profile:back_to_profile", "profile:back_to_main"]
    )