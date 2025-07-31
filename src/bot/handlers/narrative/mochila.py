"""
Handler para el comando /mochila, que muestra las pistas narrativas
desbloqueadas por el usuario.
"""

from aiogram import types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.modules.narrative.service import NarrativeService
from src.bot.keyboards.keyboard_factory import KeyboardFactory

async def handle_mochila(
    message: types.Message, 
    narrative_service: NarrativeService
):
    """
    Maneja el comando /mochila que muestra las pistas narrativas desbloqueadas.
    
    Args:
        message: Mensaje que contiene el comando.
        narrative_service: Servicio que gestiona la narrativa.
    """
    user_id = message.from_user.id
    
    # Obtener pistas desbloqueadas del usuario
    lore_pieces = await narrative_service.get_user_lore_pieces(user_id)
    
    if not lore_pieces:
        await message.answer(
            "🎒 *Tu mochila está vacía*\n\n"
            "No has encontrado ninguna pista aún. Interactúa con el bot, "
            "reacciona a publicaciones y completa misiones para desbloquear pistas sobre la historia.",
            parse_mode="Markdown",
            reply_markup=KeyboardFactory.back_button("main_menu:inventory")
        )
        return
    
    # Construir mensaje con las pistas
    header = "🎒 *Tu Mochila*\n\n" \
        "Estas son las pistas que has recolectado hasta ahora.\n" \
        "Cada pista te revela un fragmento del mundo de Diana.\n\n"
    
    pieces_text = []
    for piece in lore_pieces:
        pieces_text.append(
            f"🔹 *{piece['title']}*\n"
            f"_{piece['description']}_\n"
            f"_Desbloqueado por: {get_source_text(piece['source'])}_\n"
        )
    
    # Crear teclado para la mochila
    keyboard = InlineKeyboardBuilder()
    
    # Añadir botón para combinar pistas si tiene más de una
    if len(lore_pieces) > 1:
        keyboard.button(text="🔄 Combinar Pistas", callback_data="mochila:combine")
    
    # Añadir botón para volver
    keyboard.button(text="⬅️ Volver", callback_data="main_menu:inventory")
    
    # Dividir los botones en filas
    keyboard.adjust(1)
    
    await message.answer(
        header + "\n".join(pieces_text),
        parse_mode="Markdown",
        reply_markup=keyboard.as_markup()
    )

def get_source_text(source: str) -> str:
    """Convierte el código de fuente en texto legible."""
    sources = {
        "reaction": "Reacción en canal",
        "mission": "Misión completada",
        "daily": "Regalo diario",
        "trivia": "Respuesta correcta en trivia",
        "purchase": "Compra en tienda"
    }
    return sources.get(source, source.capitalize())

async def handle_mochila_callback(
    callback_query: types.CallbackQuery,
    narrative_service: NarrativeService
):
    """
    Maneja los callbacks relacionados con la mochila.
    
    Args:
        callback_query: Query del callback.
        narrative_service: Servicio que gestiona la narrativa.
    """
    user_id = callback_query.from_user.id
    action = callback_query.data.split(":")[1]
    
    if action == "combine":
        # Obtener pistas para combinar
        lore_pieces = await narrative_service.get_user_lore_pieces(user_id)
        
        if len(lore_pieces) < 2:
            await callback_query.answer("Necesitas al menos 2 pistas para combinar", show_alert=True)
            return
        
        # Crear teclado para seleccionar pistas a combinar
        keyboard = InlineKeyboardBuilder()
        
        for piece in lore_pieces:
            keyboard.button(
                text=piece['title'], 
                callback_data=f"combine:{piece['key']}"
            )
        
        keyboard.button(
            text="⬅️ Volver a la Mochila", 
            callback_data="mochila:back"
        )
        
        keyboard.adjust(1)  # Un botón por fila
        
        await callback_query.message.edit_text(
            "🔄 *Combinar Pistas*\n\n"
            "Selecciona la primera pista que quieres combinar:",
            parse_mode="Markdown",
            reply_markup=keyboard.as_markup()
        )
        
        await callback_query.answer()
    
    elif action == "back":
        # Volver a mostrar la mochila
        await handle_mochila(callback_query.message, narrative_service)
        await callback_query.answer()

def register_mochila_handler(dp, narrative_service):
    """Registra el handler del comando /mochila en el dispatcher."""
    dp.message.register(
        lambda message: handle_mochila(message, narrative_service),
        Command("mochila")
    )
    
    dp.callback_query.register(
        lambda callback_query: handle_mochila_callback(callback_query, narrative_service),
        lambda callback: callback.data.startswith("mochila:")
    )