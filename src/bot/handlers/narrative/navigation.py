"""
Sistema de navegación narrativa que permite a los usuarios
explorar fragmentos de historia y tomar decisiones.
"""

from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.modules.narrative.service import NarrativeService
from src.bot.keyboards.keyboard_factory import KeyboardFactory

async def handle_narrative_callback(
    callback_query: types.CallbackQuery,
    narrative_service: NarrativeService
):
    """
    Maneja los callbacks relacionados con la narrativa.
    
    Args:
        callback_query: Query del callback.
        narrative_service: Servicio que gestiona la narrativa.
    """
    user_id = callback_query.from_user.id
    action = callback_query.data.split(":")[1]
    
    if action == "continue":
        # Mostrar el fragmento actual de la historia
        await show_current_fragment(callback_query, narrative_service)
    
    elif action == "explore":
        # Mostrar ramas narrativas disponibles
        await show_narrative_branches(callback_query, narrative_service)
    
    elif action == "fragments":
        # Mostrar fragmentos desbloqueados
        await show_unlocked_fragments(callback_query, narrative_service)
    
    elif action == "back_to_main":
        # Volver al menú principal
        await callback_query.message.edit_text(
            "¡Bienvenido a Diana V2! ¿Qué te gustaría hacer hoy?",
            reply_markup=KeyboardFactory.main_menu()
        )
    
    # Confirmar la acción para cerrar el estado de espera en el cliente
    await callback_query.answer()

async def handle_choice_callback(
    callback_query: types.CallbackQuery,
    narrative_service: NarrativeService
):
    """
    Maneja los callbacks de elecciones narrativas.
    
    Args:
        callback_query: Query del callback.
        narrative_service: Servicio que gestiona la narrativa.
    """
    user_id = callback_query.from_user.id
    choice_id = int(callback_query.data.split(":")[1])
    
    # Procesar la elección
    success = await narrative_service.make_narrative_choice(user_id, choice_id)
    
    if success:
        # Mostrar el nuevo fragmento
        await show_current_fragment(callback_query, narrative_service)
    else:
        # Error al procesar la elección
        await callback_query.answer("No se pudo procesar tu elección", show_alert=True)

async def show_current_fragment(
    callback_query: types.CallbackQuery,
    narrative_service: NarrativeService
):
    """
    Muestra el fragmento actual de la historia al usuario.
    
    Args:
        callback_query: Query del callback.
        narrative_service: Servicio que gestiona la narrativa.
    """
    user_id = callback_query.from_user.id
    
    # Obtener fragmento actual
    fragment = await narrative_service.get_user_fragment(user_id)
    
    if not fragment:
        # El usuario no tiene un fragmento actual
        await callback_query.message.edit_text(
            "🌠 *La Historia*\n\n"
            "No hay ningún fragmento de historia disponible actualmente.\n"
            "Interactúa con el bot y completa misiones para desbloquear contenido narrativo.",
            parse_mode="Markdown",
            reply_markup=KeyboardFactory.back_button("main_menu:narrative")
        )
        return
    
    # Crear el mensaje del fragmento
    character_emoji = get_character_emoji(fragment['character'])
    message = (
        f"{character_emoji} *{fragment['title']}*\n\n"
        f"{fragment['text']}\n\n"
    )
    
    # Crear teclado con opciones
    keyboard = InlineKeyboardBuilder()
    
    if fragment['choices']:
        for choice in fragment['choices']:
            keyboard.button(
                text=choice['text'],
                callback_data=f"choice:{choice['id']}"
            )
    else:
        # Si no hay opciones, es un fragmento final o informativo
        keyboard.button(
            text="⬅️ Volver al Menú de Narrativa",
            callback_data="narrative:back_to_narrative"
        )
    
    keyboard.adjust(1)  # Una opción por fila
    
    await callback_query.message.edit_text(
        message,
        parse_mode="Markdown",
        reply_markup=keyboard.as_markup()
    )

async def show_narrative_branches(
    callback_query: types.CallbackQuery,
    narrative_service: NarrativeService
):
    """
    Muestra las ramas narrativas disponibles.
    
    Args:
        callback_query: Query del callback.
        narrative_service: Servicio que gestiona la narrativa.
    """
    # Esta función se puede ampliar para mostrar diferentes ramas
    # basadas en decisiones pasadas o nivel del usuario
    
    await callback_query.message.edit_text(
        "🌿 *Explorar Ramas*\n\n"
        "En esta sección podrás explorar diferentes ramas de la historia.\n"
        "Esta funcionalidad estará disponible próximamente.",
        parse_mode="Markdown",
        reply_markup=KeyboardFactory.back_button("narrative:back_to_narrative")
    )

async def show_unlocked_fragments(
    callback_query: types.CallbackQuery,
    narrative_service: NarrativeService
):
    """
    Muestra los fragmentos desbloqueados por el usuario.
    
    Args:
        callback_query: Query del callback.
        narrative_service: Servicio que gestiona la narrativa.
    """
    # Esta función se puede ampliar para mostrar un historial
    # de fragmentos desbloqueados
    
    await callback_query.message.edit_text(
        "📜 *Fragmentos Desbloqueados*\n\n"
        "Aquí podrás ver todos los fragmentos de historia que has desbloqueado.\n"
        "Esta funcionalidad estará disponible próximamente.",
        parse_mode="Markdown",
        reply_markup=KeyboardFactory.back_button("narrative:back_to_narrative")
    )

def get_character_emoji(character: str) -> str:
    """Obtiene el emoji correspondiente al personaje."""
    characters = {
        "diana": "🌸",
        "lucien": "🎭",
        "sistema": "🤖",
        "desconocido": "❓"
    }
    return characters.get(character.lower(), "👤")

def register_narrative_navigation_handlers(dp, narrative_service):
    """Registra los handlers de navegación narrativa en el dispatcher."""
    # Callbacks del menú de narrativa
    dp.callback_query.register(
        lambda callback_query: handle_narrative_callback(callback_query, narrative_service),
        lambda callback: callback.data.startswith("narrative:")
    )
    
    # Callbacks de elecciones narrativas
    dp.callback_query.register(
        lambda callback_query: handle_choice_callback(callback_query, narrative_service),
        lambda callback: callback.data.startswith("choice:")
    )