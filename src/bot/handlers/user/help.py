from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from src.bot.keyboards.keyboard_factory import KeyboardFactory

async def handle_help(message: types.Message):
    """
    Maneja el comando /help del bot.
    
    Muestra información de ayuda sobre los comandos disponibles
    y cómo utilizar el bot.
    """
    help_text = (
        "**🤖 Ayuda de Diana V2 🤖**\n\n"
        "Estos son los comandos disponibles:\n\n"
        "📜 *Comandos básicos:*\n"
        "/start - Inicia el bot y muestra el menú principal\n"
        "/help - Muestra este mensaje de ayuda\n"
        "/profile - Muestra tu perfil y estadísticas\n\n"
        
        "📚 *Navegación por menús:*\n"
        "• Historia: Accede a la narrativa principal\n"
        "• Perfil: Revisa tus puntos y logros\n"
        "• Misiones: Consulta tus misiones activas\n"
        "• Mochila: Gestiona tus objetos\n\n"
        
        "💡 *Consejos:*\n"
        "• Reacciona a las publicaciones del canal para ganar puntos\n"
        "• Completa misiones para desbloquear contenido especial\n"
        "• Explora diferentes ramas de la historia para descubrir todos los secretos\n\n"
        
        "Si necesitas más ayuda, selecciona una opción a continuación:"
    )
    
    await message.answer(
        help_text,
        parse_mode="Markdown",
        reply_markup=KeyboardFactory.help_menu()
    )

async def handle_help_callback(query: types.CallbackQuery):
    """Maneja los callbacks del menú de ayuda."""
    callback_data = query.data
    
    if callback_data == "help:how_to_play":
        text = (
            "**📖 Cómo Jugar 📖**\n\n"
            "Diana V2 es un bot narrativo interactivo:\n\n"
            "1. **Sigue la historia**: Interactúa con el bot para avanzar en la narrativa\n"
            "2. **Toma decisiones**: Tus elecciones afectan el desarrollo de la historia\n"
            "3. **Gana puntos**: Recibe puntos por participar en el canal y completar misiones\n"
            "4. **Desbloquea contenido**: Utiliza tus puntos para acceder a contenido exclusivo\n"
            "5. **Explora ramas**: Descubre diferentes caminos en la historia\n\n"
            "Comienza pulsando el botón 'Historia' en el menú principal."
        )
        await query.message.edit_text(text, parse_mode="Markdown", reply_markup=KeyboardFactory.back_button("help:back_to_help"))
    
    elif callback_data == "help:commands":
        text = (
            "**⌨️ Comandos Disponibles ⌨️**\n\n"
            "/start - Inicia el bot y muestra el menú principal\n"
            "/help - Muestra el menú de ayuda\n"
            "/profile - Muestra tu perfil y estadísticas\n"
            "/daily - Reclama tu recompensa diaria\n"
            "/missions - Muestra tus misiones activas\n"
            "/inventory - Muestra tu inventario\n"
            "/settings - Configura tus preferencias\n\n"
            "Los comandos también están disponibles a través de los menús interactivos."
        )
        await query.message.edit_text(text, parse_mode="Markdown", reply_markup=KeyboardFactory.back_button("help:back_to_help"))
    
    elif callback_data == "help:faq":
        text = (
            "**❓ Preguntas Frecuentes ❓**\n\n"
            "**¿Cómo gano puntos?**\n"
            "Puedes ganar puntos reaccionando a publicaciones del canal, completando misiones, y avanzando en la historia.\n\n"
            
            "**¿Para qué sirven los puntos?**\n"
            "Los puntos te permiten desbloquear nuevas ramas de la historia, obtener objetos especiales y acceder a contenido exclusivo.\n\n"
            
            "**¿Puedo reiniciar mi progreso?**\n"
            "Sí, puedes reiniciar tu progreso en el menú de configuración, pero perderás todos tus avances actuales.\n\n"
            
            "**¿Hay contenido VIP?**\n"
            "Sí, puedes acceder a contenido exclusivo mediante suscripciones premium."
        )
        await query.message.edit_text(text, parse_mode="Markdown", reply_markup=KeyboardFactory.back_button("help:back_to_help"))
    
    elif callback_data == "help:back_to_help":
        await handle_help(query.message)
    
    elif callback_data == "help:back_to_main":
        await query.message.edit_text(
            "¡Bienvenido a Diana V2! ¿Qué te gustaría hacer hoy?",
            reply_markup=KeyboardFactory.main_menu()
        )
    
    await query.answer()

def register_help_handler(dp):
    """Registra los handlers de ayuda en el dispatcher."""
    # Comando /help
    dp.message.register(handle_help, Command("help"))
    
    # Callbacks del menú de ayuda
    dp.callback_query.register(handle_help_callback, lambda c: c.data.startswith("help:"))