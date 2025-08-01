"""Handlers para trivias diarias."""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from datetime import datetime

from src.modules.trivia.service import TriviaService, TriviaQuestion

trivia_router = Router()

@trivia_router.message(Command("trivia"))
async def cmd_trivia(message: Message, trivia_service: TriviaService):
    """Comando principal de trivia diaria."""
    user_id = message.from_user.id
    
    # Verificar si puede responder la trivia diaria
    can_answer = await trivia_service.can_answer_daily(user_id)
    
    if not can_answer:
        # Ya completó la trivia de hoy
        stats = await trivia_service.get_user_trivia_stats(user_id)
        
        text = (
            "🧠 **Trivia Diaria Completada**\n\n"
            "Ya has completado la trivia de hoy. "
            "¡Vuelve mañana para una nueva pregunta!\n\n"
            f"📊 **Tus estadísticas:**\n"
            f"• Respondidas: {stats['total_answered']}\n"
            f"• Precisión: {stats['accuracy_rate']:.1f}%\n"
            f"• Puntos ganados: {stats['total_points_earned']}\n"
            f"• Racha actual: {stats['daily_streak']} días"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📊 Ver Ranking", callback_data="trivia:leaderboard")],
            [InlineKeyboardButton(text="📈 Mis Estadísticas", callback_data="trivia:my_stats")],
            [InlineKeyboardButton(text="🔙 Volver", callback_data="main_menu")]
        ])
        
    else:
        # Puede hacer la trivia
        text = (
            "🧠 **Trivia Diaria**\n\n"
            "¡Bienvenido a la trivia diaria! Responde correctamente "
            "para ganar besitos y mejorar tu ranking.\n\n"
            "**💡 Consejos:**\n"
            "• Responde rápido para obtener bonificación\n"
            "• Preguntas más difíciles dan más puntos\n"
            "• Los usuarios VIP tienen preguntas exclusivas\n\n"
            "¿Estás listo para el desafío de hoy?"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎯 Empezar Trivia", callback_data="trivia:start")],
            [InlineKeyboardButton(text="📊 Ver Ranking", callback_data="trivia:leaderboard")],
            [InlineKeyboardButton(text="📈 Mis Estadísticas", callback_data="trivia:my_stats")],
            [InlineKeyboardButton(text="🔙 Volver", callback_data="main_menu")]
        ])
    
    await message.answer(text, parse_mode="Markdown", reply_markup=keyboard)

@trivia_router.callback_query(F.data == "trivia:start")
async def trivia_start_callback(callback: CallbackQuery, trivia_service: TriviaService):
    """Inicia una nueva trivia."""
    user_id = callback.from_user.id
    
    # Verificar que puede hacer trivia
    can_answer = await trivia_service.can_answer_daily(user_id)
    if not can_answer:
        await callback.answer("Ya completaste la trivia de hoy", show_alert=True)
        return
    
    # Obtener pregunta diaria
    question = await trivia_service.get_daily_question(user_id)
    if not question:
        await callback.answer("No hay preguntas disponibles", show_alert=True)
        return
    
    # Iniciar sesión
    session = await trivia_service.start_trivia_session(user_id, question.id)
    
    # Mostrar pregunta
    await show_trivia_question(callback, question, trivia_service)

async def show_trivia_question(
    callback: CallbackQuery, 
    question: TriviaQuestion,
    trivia_service: TriviaService
):
    """Muestra una pregunta de trivia."""
    
    # Iconos por dificultad
    difficulty_icons = {
        "easy": "🟢",
        "medium": "🟡", 
        "hard": "🔴",
        "expert": "⚫"
    }
    
    difficulty_icon = difficulty_icons.get(question.difficulty.value, "❓")
    vip_badge = " 👑" if question.vip_only else ""
    
    text = (
        f"🧠 **Trivia Diaria**{vip_badge}\n\n"
        f"{difficulty_icon} **Dificultad:** {question.difficulty.value.title()}\n"
        f"📂 **Categoría:** {question.category}\n"
        f"💋 **Recompensa:** {question.points_reward} besitos\n\n"
        f"**Pregunta:**\n{question.question}\n\n"
        "**Opciones:**"
    )
    
    # Crear botones para las opciones
    keyboard_buttons = []
    for i, option in enumerate(question.options):
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=f"{chr(65 + i)}) {option}",
                callback_data=f"trivia:answer:{i}"
            )
        ])
    
    # Botón para abandonar
    keyboard_buttons.append([
        InlineKeyboardButton(text="❌ Abandonar", callback_data="trivia:abandon")
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer()

@trivia_router.callback_query(F.data.startswith("trivia:answer:"))
async def trivia_answer_callback(callback: CallbackQuery, trivia_service: TriviaService):
    """Procesa la respuesta del usuario."""
    user_id = callback.from_user.id
    selected_answer = int(callback.data.split(":")[2])
    
    # Procesar respuesta
    result = await trivia_service.submit_answer(user_id, selected_answer)
    
    if not result["success"]:
        await callback.answer(f"Error: {result['reason']}", show_alert=True)
        return
    
    # Obtener información de la pregunta
    session = await trivia_service.get_active_session(user_id)
    if session:
        question = await trivia_service.get_question_by_id(session.question_id)
    else:
        # La sesión ya se cerró, usar datos del resultado
        question = None
    
    # Crear mensaje de resultado
    if result["is_correct"]:
        status_icon = "✅"
        status_text = "¡Correcto!"
        points_text = f"Has ganado **{result['points_earned']} besitos**"
        
        # Bonificación por velocidad
        if result["response_time"] < 30:
            points_text += " (incluye bonificación por velocidad ⚡)"
    else:
        status_icon = "❌"
        status_text = "Incorrecto"
        points_text = "No has ganado puntos esta vez"
    
    # Mostrar respuesta correcta
    correct_option = chr(65 + result["correct_answer"])  # A, B, C, D
    
    text = (
        f"{status_icon} **{status_text}**\n\n"
        f"**Respuesta correcta:** {correct_option}\n\n"
        f"**Explicación:**\n{result['explanation']}\n\n"
        f"💋 {points_text}\n\n"
        f"⏱️ **Tiempo de respuesta:** {result['response_time']:.1f} segundos"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Ver Ranking", callback_data="trivia:leaderboard")],
        [InlineKeyboardButton(text="📈 Mis Estadísticas", callback_data="trivia:my_stats")],
        [InlineKeyboardButton(text="🏠 Menú Principal", callback_data="main_menu")]
    ])
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    
    # Respuesta de confirmación
    if result["is_correct"]:
        await callback.answer("¡Respuesta correcta! 🎉", show_alert=True)
    else:
        await callback.answer("Respuesta incorrecta 😔")

@trivia_router.callback_query(F.data == "trivia:abandon")
async def trivia_abandon_callback(callback: CallbackQuery, trivia_service: TriviaService):
    """Abandona la trivia actual."""
    user_id = callback.from_user.id
    
    # Limpiar sesión activa si existe
    session = await trivia_service.get_active_session(user_id)
    if session and user_id in trivia_service._active_sessions:
        del trivia_service._active_sessions[user_id]
    
    text = (
        "❌ **Trivia Abandonada**\n\n"
        "Has abandonado la trivia actual. "
        "Podrás intentarlo de nuevo mañana.\n\n"
        "¡No te rindas! La práctica hace al maestro."
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Ver Ranking", callback_data="trivia:leaderboard")],
        [InlineKeyboardButton(text="🏠 Menú Principal", callback_data="main_menu")]
    ])
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer("Trivia abandonada")

@trivia_router.callback_query(F.data == "trivia:leaderboard")
async def trivia_leaderboard_callback(callback: CallbackQuery, trivia_service: TriviaService):
    """Muestra el ranking de trivias."""
    leaderboard = await trivia_service.get_leaderboard(limit=10)
    
    if not leaderboard:
        text = (
            "📊 **Ranking de Trivias**\n\n"
            "Aún no hay estadísticas disponibles.\n"
            "¡Sé el primero en aparecer en el ranking!"
        )
    else:
        text = "📊 **Ranking de Trivias**\n\n"
        
        for i, entry in enumerate(leaderboard, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            text += (
                f"{medal} Usuario {entry['user_id']}\n"
                f"   💋 {entry['total_points']} puntos | "
                f"🎯 {entry['accuracy']:.1f}% precisión\n\n"
            )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📈 Mis Estadísticas", callback_data="trivia:my_stats")],
        [InlineKeyboardButton(text="🔙 Volver", callback_data="trivia:main")]
    ])
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer()

@trivia_router.callback_query(F.data == "trivia:my_stats")
async def trivia_my_stats_callback(callback: CallbackQuery, trivia_service: TriviaService):
    """Muestra las estadísticas personales del usuario."""
    user_id = callback.from_user.id
    stats = await trivia_service.get_user_trivia_stats(user_id)
    
    if stats["total_answered"] == 0:
        text = (
            "📈 **Mis Estadísticas**\n\n"
            "Aún no has participado en ninguna trivia.\n"
            "¡Comienza hoy y ve cómo mejoras día a día!"
        )
    else:
        text = (
            "📈 **Mis Estadísticas**\n\n"
            f"🎯 **Preguntas respondidas:** {stats['total_answered']}\n"
            f"✅ **Respuestas correctas:** {stats['correct_answers']}\n"
            f"📊 **Precisión:** {stats['accuracy_rate']:.1f}%\n"
            f"💋 **Puntos ganados:** {stats['total_points_earned']}\n"
            f"🔥 **Racha actual:** {stats['daily_streak']} días\n\n"
            "**Por dificultad:**\n"
        )
        
        # Estadísticas por dificultad
        for difficulty, data in stats["difficulty_breakdown"].items():
            if data["answered"] > 0:
                accuracy = (data["correct"] / data["answered"]) * 100
                text += f"• {difficulty.title()}: {data['correct']}/{data['answered']} ({accuracy:.1f}%)\n"
        
        # Agregar mejor categoría si existe
        if stats["best_category"]:
            text += f"\n🏆 **Mejor categoría:** {stats['best_category']}"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Ver Ranking", callback_data="trivia:leaderboard")],
        [InlineKeyboardButton(text="🔙 Volver", callback_data="trivia:main")]
    ])
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer()

@trivia_router.callback_query(F.data == "trivia:main")
async def trivia_main_callback(callback: CallbackQuery, trivia_service: TriviaService):
    """Vuelve al menú principal de trivia."""
    user_id = callback.from_user.id
    
    # Verificar si puede responder la trivia diaria
    can_answer = await trivia_service.can_answer_daily(user_id)
    
    if not can_answer:
        # Ya completó la trivia de hoy
        stats = await trivia_service.get_user_trivia_stats(user_id)
        
        text = (
            "🧠 **Trivia Diaria Completada**\n\n"
            "Ya has completado la trivia de hoy. "
            "¡Vuelve mañana para una nueva pregunta!\n\n"
            f"📊 **Tus estadísticas:**\n"
            f"• Respondidas: {stats['total_answered']}\n"
            f"• Precisión: {stats['accuracy_rate']:.1f}%\n"
            f"• Puntos ganados: {stats['total_points_earned']}\n"
            f"• Racha actual: {stats['daily_streak']} días"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📊 Ver Ranking", callback_data="trivia:leaderboard")],
            [InlineKeyboardButton(text="📈 Mis Estadísticas", callback_data="trivia:my_stats")],
            [InlineKeyboardButton(text="🔙 Volver", callback_data="main_menu")]
        ])
        
    else:
        # Puede hacer la trivia
        text = (
            "🧠 **Trivia Diaria**\n\n"
            "¡Bienvenido a la trivia diaria! Responde correctamente "
            "para ganar besitos y mejorar tu ranking.\n\n"
            "**💡 Consejos:**\n"
            "• Responde rápido para obtener bonificación\n"
            "• Preguntas más difíciles dan más puntos\n"
            "• Los usuarios VIP tienen preguntas exclusivas\n\n"
            "¿Estás listo para el desafío de hoy?"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎯 Empezar Trivia", callback_data="trivia:start")],
            [InlineKeyboardButton(text="📊 Ver Ranking", callback_data="trivia:leaderboard")],
            [InlineKeyboardButton(text="📈 Mis Estadísticas", callback_data="trivia:my_stats")],
            [InlineKeyboardButton(text="🔙 Volver", callback_data="main_menu")]
        ])
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer()

def register_trivia_handlers(dp, trivia_service: TriviaService):
    """Registra los handlers de trivia."""
    trivia_router.message.register(
        lambda message: cmd_trivia(message, trivia_service),
        Command("trivia")
    )
    
    dp.include_router(trivia_router)