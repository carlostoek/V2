"""
Handler para el comando /trivia (Trivia System).
Sistema de preguntas con 4 niveles de dificultad, timer y recompensas.
"""

import logging
import asyncio
from datetime import datetime, timedelta
from aiogram import types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.modules.gamification.service import GamificationService
from src.bot.handlers.gamification.trivia_data import (
    TRIVIA_LEVELS, get_random_question, get_level_info, get_available_levels,
    calculate_trivia_bonus, format_trivia_stats
)
from src.bot.database.engine import get_session
from src.bot.database.models.user import User
from src.bot.database.models.gamification import UserPoints
from sqlalchemy import select

logger = logging.getLogger(__name__)

# Cache para sesiones de trivia activas
active_trivia_sessions = {}

# Configuración de trivia
TRIVIA_CONFIG = {
    "max_daily_questions": 20,  # Máximo de preguntas por día
    "streak_bonus_multiplier": 0.1,  # 10% extra por cada respuesta correcta consecutiva
    "max_streak_bonus": 2.0,  # Máximo multiplicador por racha
    "cooldown_seconds": 5,  # Tiempo entre preguntas
    "session_timeout_minutes": 10  # Timeout de sesión inactiva
}

async def handle_trivia_main(message: types.Message, gamification_service: GamificationService):
    """
    Maneja el comando /trivia - muestra el menú principal de trivia.
    
    Args:
        message: Mensaje que contiene el comando.
        gamification_service: Servicio que gestiona la gamificación.
    """
    user_id = message.from_user.id
    
    try:
        # Verificar si hay sesión activa
        if user_id in active_trivia_sessions:
            await _show_active_session_warning(message)
            return
        
        # Obtener información del usuario
        user_info = await _get_user_info(user_id)
        if not user_info:
            await message.answer("❌ Error al cargar tu información. Inténtalo más tarde.")
            return
        
        await _show_trivia_main_menu(message, user_info)
        
    except Exception as e:
        logger.error(f"Error en trivia main para usuario {user_id}: {e}")
        await message.answer("❌ Error al cargar la trivia. Inténtalo más tarde.")

async def _get_user_info(user_id: int) -> dict:
    """
    Obtiene información del usuario necesaria para trivia.
    
    Args:
        user_id: ID del usuario.
        
    Returns:
        Dict con información del usuario.
    """
    async for session in get_session():
        # Obtener usuario
        user_query = select(User).where(User.id == user_id)
        user_result = await session.execute(user_query)
        user = user_result.scalars().first()
        
        if not user:
            return None
        
        # Obtener puntos
        points_query = select(UserPoints).where(UserPoints.user_id == user_id)
        points_result = await session.execute(points_query)
        user_points = points_result.scalars().first()
        
        current_points = user_points.current_points if user_points else 0
        
        # Obtener estadísticas de trivia del historial de puntos
        trivia_stats = {}
        if user_points and user_points.points_history:
            trivia_stats = _extract_trivia_stats(user_points.points_history)
        
        return {
            "user_id": user_id,
            "level": user.level,
            "current_points": current_points,
            "username": user.username or f"Usuario {user_id}",
            "trivia_stats": trivia_stats
        }

def _extract_trivia_stats(points_history: list) -> dict:
    """
    Extrae estadísticas de trivia del historial de puntos.
    
    Args:
        points_history: Historial de puntos del usuario.
        
    Returns:
        Dict con estadísticas por nivel.
    """
    stats = {}
    today = datetime.now().date()
    
    for entry in points_history:
        if not entry.get("source", "").startswith("Trivia_"):
            continue
        
        try:
            timestamp = datetime.fromisoformat(entry["timestamp"])
            if timestamp.date() != today:
                continue  # Solo contar preguntas de hoy
            
            # Extraer información de la fuente
            source_parts = entry["source"].split("_")
            if len(source_parts) >= 3:
                level = source_parts[1]
                result = source_parts[2]  # "correct" or "incorrect"
                
                if level not in stats:
                    stats[level] = {"answered": 0, "correct": 0}
                
                stats[level]["answered"] += 1
                if result == "correct":
                    stats[level]["correct"] += 1
        
        except (ValueError, KeyError, IndexError):
            continue
    
    return stats

async def _show_trivia_main_menu(message: types.Message, user_info: dict):
    """
    Muestra el menú principal de trivia.
    
    Args:
        message: Mensaje donde mostrar el menú.
        user_info: Información del usuario.
    """
    username = user_info["username"]
    level = user_info["level"]
    current_points = user_info["current_points"]
    trivia_stats = user_info["trivia_stats"]
    
    # Contar preguntas respondidas hoy
    daily_questions = sum(stats.get("answered", 0) for stats in trivia_stats.values())
    remaining_questions = max(0, TRIVIA_CONFIG["max_daily_questions"] - daily_questions)
    
    text = (
        f"🧠 **Trivia de Diana** 🧠\n\n"
        f"👤 {username} (Nivel {level})\n"
        f"💰 {current_points:.0f} besitos\n"
        f"❓ Preguntas hoy: {daily_questions}/{TRIVIA_CONFIG['max_daily_questions']}\n\n"
    )
    
    if remaining_questions == 0:
        text += "⏰ **Has alcanzado el límite diario de preguntas.**\n"
        text += "¡Vuelve mañana para más trivia!"
    else:
        text += "Selecciona un nivel de dificultad:\n"
    
    # Obtener niveles disponibles
    available_levels = get_available_levels(level)
    
    # Crear keyboard
    keyboard = InlineKeyboardBuilder()
    
    if remaining_questions > 0:
        for level_data in available_levels:
            level_key = level_data["key"]
            level_info = level_data["info"]
            question_count = level_data["question_count"]
            
            # Estadísticas del nivel si existen
            level_stats = trivia_stats.get(level_key, {})
            answered = level_stats.get("answered", 0)
            correct = level_stats.get("correct", 0)
            accuracy = f" ({correct}/{answered})" if answered > 0 else ""
            
            button_text = f"{level_info['emoji']} {level_info['name'].split(' ', 1)[1]} (+{level_info['reward']} 💰){accuracy}"
            keyboard.button(
                text=button_text,
                callback_data=f"trivia:level:{level_key}"
            )
    
    # Botones adicionales
    if trivia_stats:
        keyboard.button(text="📊 Ver Estadísticas", callback_data="trivia:stats")
    
    keyboard.button(text="🎁 Obtener Besitos", callback_data="main_menu:daily_reward")
    keyboard.button(text="⬅️ Menú Principal", callback_data="main_menu")
    
    # Ajustar layout
    if remaining_questions > 0:
        keyboard.adjust(*([1] * len(available_levels) + [1, 2]))
    else:
        keyboard.adjust(1, 2)
    
    await message.answer(
        text,
        parse_mode="Markdown",
        reply_markup=keyboard.as_markup()
    )

async def _show_active_session_warning(message: types.Message):
    """
    Muestra advertencia cuando hay una sesión activa.
    
    Args:
        message: Mensaje donde mostrar la advertencia.
    """
    text = (
        "⚠️ **Sesión de Trivia Activa**\n\n"
        "Ya tienes una pregunta en curso.\n"
        "Responde la pregunta actual o espera a que termine el tiempo."
    )
    
    await message.answer(
        text,
        parse_mode="Markdown"
    )

async def handle_trivia_callback(query: types.CallbackQuery, gamification_service: GamificationService):
    """
    Maneja todos los callbacks relacionados con trivia.
    
    Args:
        query: Query del callback.
        gamification_service: Servicio que gestiona la gamificación.
    """
    user_id = query.from_user.id
    callback_data = query.data
    
    try:
        parts = callback_data.split(":")
        action = parts[1]
        
        if action == "main":
            await handle_trivia_main(query.message, gamification_service)
        
        elif action == "level":
            level = parts[2]
            await _start_trivia_question(query, level, gamification_service)
        
        elif action == "answer":
            session_id = parts[2]
            answer_idx = int(parts[3])
            await _process_trivia_answer(query, session_id, answer_idx, gamification_service)
        
        elif action == "stats":
            await _show_trivia_stats(query)
        
        elif action == "next":
            level = parts[2]
            await _start_trivia_question(query, level, gamification_service)
        
        await query.answer()
        
    except Exception as e:
        logger.error(f"Error en trivia callback para usuario {user_id}: {e}")
        await query.answer("❌ Error al procesar la solicitud.")

async def _start_trivia_question(query: types.CallbackQuery, level: str, gamification_service: GamificationService):
    """
    Inicia una nueva pregunta de trivia.
    
    Args:
        query: Query del callback.
        level: Nivel de dificultad.
        gamification_service: Servicio de gamificación.
    """
    user_id = query.from_user.id
    
    # Verificar si ya hay sesión activa
    if user_id in active_trivia_sessions:
        await query.answer("⚠️ Ya tienes una pregunta activa.")
        return
    
    # Obtener información del usuario
    user_info = await _get_user_info(user_id)
    if not user_info:
        await query.answer("❌ Error al cargar información.")
        return
    
    # Verificar límite diario
    trivia_stats = user_info["trivia_stats"]
    daily_questions = sum(stats.get("answered", 0) for stats in trivia_stats.values())
    
    if daily_questions >= TRIVIA_CONFIG["max_daily_questions"]:
        await query.answer("⏰ Has alcanzado el límite diario de preguntas.")
        return
    
    # Verificar nivel disponible
    level_info = get_level_info(level)
    if not level_info or level_info["level_required"] > user_info["level"]:
        await query.answer("❌ Nivel de trivia no disponible.")
        return
    
    # Obtener pregunta aleatoria
    # Evitar preguntas ya respondidas en esta sesión (podríamos implementar esto más adelante)
    question = get_random_question(level)
    if not question:
        await query.answer("❌ No hay preguntas disponibles en este nivel.")
        return
    
    # Crear sesión de trivia
    session_id = f"{user_id}_{datetime.now().timestamp()}"
    session_data = {
        "user_id": user_id,
        "level": level,
        "question": question,
        "start_time": datetime.now(),
        "timer_seconds": level_info["timer_seconds"],
        "current_streak": _get_current_streak(trivia_stats, level)
    }
    
    active_trivia_sessions[user_id] = session_data
    
    # Mostrar pregunta
    await _show_trivia_question(query, session_id, session_data)
    
    # Programar timeout
    asyncio.create_task(_schedule_trivia_timeout(session_id, level_info["timer_seconds"]))

def _get_current_streak(trivia_stats: dict, level: str) -> int:
    """
    Obtiene la racha actual de respuestas correctas para un nivel.
    
    Args:
        trivia_stats: Estadísticas de trivia.
        level: Nivel actual.
        
    Returns:
        Racha actual de respuestas correctas.
    """
    # Por ahora retornamos 0, pero se podría implementar un sistema más sofisticado
    # que trackee las últimas N respuestas consecutivas
    return 0

async def _show_trivia_question(query: types.CallbackQuery, session_id: str, session_data: dict):
    """
    Muestra la pregunta de trivia con timer.
    
    Args:
        query: Query del callback.
        session_id: ID de la sesión.
        session_data: Datos de la sesión.
    """
    question = session_data["question"]
    level = session_data["level"]
    timer_seconds = session_data["timer_seconds"]
    current_streak = session_data["current_streak"]
    
    level_info = get_level_info(level)
    
    text = f"🧠 **Pregunta {level_info['emoji']} {level_info['name']}**\n\n"
    text += f"❓ **{question['question']}**\n\n"
    text += f"⏰ Tiempo: {timer_seconds} segundos\n"
    text += f"💰 Recompensa: {level_info['reward']} besitos\n"
    
    if current_streak > 0:
        bonus_multiplier = min(1 + (current_streak * TRIVIA_CONFIG["streak_bonus_multiplier"]), TRIVIA_CONFIG["max_streak_bonus"])
        text += f"🔥 Racha x{current_streak}: Bonus x{bonus_multiplier:.1f}\n"
    
    text += "\nSelecciona tu respuesta:"
    
    # Crear keyboard con opciones
    keyboard = InlineKeyboardBuilder()
    
    for i, option in enumerate(question["options"]):
        keyboard.button(
            text=f"{chr(65 + i)}) {option}",
            callback_data=f"trivia:answer:{session_id}:{i}"
        )
    
    keyboard.adjust(1)  # Una opción por fila
    
    await query.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboard.as_markup()
    )

async def _schedule_trivia_timeout(session_id: str, timer_seconds: int):
    """
    Programa el timeout de una pregunta de trivia.
    
    Args:
        session_id: ID de la sesión.
        timer_seconds: Segundos de timeout.
    """
    await asyncio.sleep(timer_seconds)
    
    # Buscar sesión por session_id
    user_id = None
    for uid, session_data in active_trivia_sessions.items():
        if f"{uid}_{session_data['start_time'].timestamp()}" == session_id:
            user_id = uid
            break
    
    if user_id and user_id in active_trivia_sessions:
        session_data = active_trivia_sessions[user_id]
        
        # Solo procesar timeout si la sesión sigue activa
        if f"{user_id}_{session_data['start_time'].timestamp()}" == session_id:
            await _handle_trivia_timeout(user_id, session_data)

async def _handle_trivia_timeout(user_id: int, session_data: dict):
    """
    Maneja el timeout de una pregunta de trivia.
    
    Args:
        user_id: ID del usuario.
        session_data: Datos de la sesión.
    """
    try:
        # Remover sesión
        if user_id in active_trivia_sessions:
            del active_trivia_sessions[user_id]
        
        # Aquí podríamos enviar un mensaje de timeout, pero requeriría
        # mantener referencia al bot/chat, lo cual complicaría la implementación
        logger.info(f"Trivia timeout para usuario {user_id}")
        
    except Exception as e:
        logger.error(f"Error en trivia timeout: {e}")

async def _process_trivia_answer(query: types.CallbackQuery, session_id: str, answer_idx: int, gamification_service: GamificationService):
    """
    Procesa la respuesta a una pregunta de trivia.
    
    Args:
        query: Query del callback.
        session_id: ID de la sesión.
        answer_idx: Índice de la respuesta seleccionada.
        gamification_service: Servicio de gamificación.
    """
    user_id = query.from_user.id
    
    # Verificar sesión activa
    if user_id not in active_trivia_sessions:
        await query.answer("❌ Sesión de trivia expirada.")
        return
    
    session_data = active_trivia_sessions[user_id]
    question = session_data["question"]
    level = session_data["level"]
    start_time = session_data["start_time"]
    current_streak = session_data["current_streak"]
    
    # Verificar que el session_id coincida
    expected_session_id = f"{user_id}_{start_time.timestamp()}"
    if session_id != expected_session_id:
        await query.answer("❌ Sesión inválida.")
        return
    
    # Calcular tiempo tomado
    time_taken = (datetime.now() - start_time).total_seconds()
    is_correct = answer_idx == question["correct"]
    
    # Remover sesión activa
    del active_trivia_sessions[user_id]
    
    # Calcular recompensa
    level_info = get_level_info(level)
    base_reward = level_info["reward"]
    
    if is_correct:
        # Calcular bonus por velocidad
        speed_bonus = calculate_trivia_bonus(level, int(time_taken), level_info["timer_seconds"])
        
        # Calcular bonus por racha
        streak_bonus = 0
        if current_streak > 0:
            streak_multiplier = min(1 + (current_streak * TRIVIA_CONFIG["streak_bonus_multiplier"]), TRIVIA_CONFIG["max_streak_bonus"])
            streak_bonus = int(base_reward * (streak_multiplier - 1))
        
        total_reward = base_reward + speed_bonus + streak_bonus
        
        # Otorgar puntos
        class TriviaEvent:
            def __init__(self, user_id, level, result):
                self.user_id = user_id
                self.level = level
                self.result = result
        
        await gamification_service._award_points(user_id, total_reward, TriviaEvent(user_id, level, "correct"))
        
        # Mostrar respuesta correcta
        await _show_correct_answer(query, question, total_reward, base_reward, speed_bonus, streak_bonus, time_taken, level)
    
    else:
        # Respuesta incorrecta - otorgar puntos de consolación
        consolation_points = max(1, base_reward // 4)  # 25% de la recompensa
        await gamification_service._award_points(user_id, consolation_points, TriviaEvent(user_id, level, "incorrect"))
        
        # Mostrar respuesta incorrecta
        await _show_incorrect_answer(query, question, consolation_points, time_taken, level)

async def _show_correct_answer(query: types.CallbackQuery, question: dict, total_reward: int, base_reward: int, speed_bonus: int, streak_bonus: int, time_taken: float, level: str):
    """
    Muestra mensaje para respuesta correcta.
    
    Args:
        query: Query del callback.
        question: Datos de la pregunta.
        total_reward: Recompensa total.
        base_reward: Recompensa base.
        speed_bonus: Bonus por velocidad.
        streak_bonus: Bonus por racha.
        time_taken: Tiempo tomado.
        level: Nivel de la pregunta.
    """
    level_info = get_level_info(level)
    
    text = f"✅ **¡Respuesta Correcta!** ✅\n\n"
    text += f"💰 **+{total_reward} besitos** ganados\n\n"
    
    # Desglose de recompensas
    text += f"🎯 Recompensa base: {base_reward}\n"
    if speed_bonus > 0:
        text += f"⚡ Bonus por velocidad: +{speed_bonus}\n"
    if streak_bonus > 0:
        text += f"🔥 Bonus por racha: +{streak_bonus}\n"
    
    text += f"\n⏱️ Respondiste en {time_taken:.1f} segundos\n\n"
    
    # Explicación si existe
    if "explanation" in question:
        text += f"💡 **Explicación:**\n_{question['explanation']}_\n\n"
    
    text += "¿Quieres responder otra pregunta?"
    
    # Crear keyboard
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text=f"🧠 Otra Pregunta {level_info['emoji']}", callback_data=f"trivia:next:{level}")
    keyboard.button(text="📊 Ver Estadísticas", callback_data="trivia:stats")
    keyboard.button(text="🔄 Cambiar Nivel", callback_data="trivia:main")
    keyboard.button(text="⬅️ Menú Principal", callback_data="main_menu")
    keyboard.adjust(1, 2, 1)
    
    await query.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboard.as_markup()
    )

async def _show_incorrect_answer(query: types.CallbackQuery, question: dict, consolation_points: int, time_taken: float, level: str):
    """
    Muestra mensaje para respuesta incorrecta.
    
    Args:
        query: Query del callback.
        question: Datos de la pregunta.
        consolation_points: Puntos de consolación.
        time_taken: Tiempo tomado.
        level: Nivel de la pregunta.
    """
    level_info = get_level_info(level)
    correct_answer = question["options"][question["correct"]]
    
    text = f"❌ **Respuesta Incorrecta** ❌\n\n"
    text += f"✅ **Respuesta correcta:** {correct_answer}\n\n"
    text += f"💝 Puntos de consolación: **+{consolation_points} besitos**\n"
    text += f"⏱️ Respondiste en {time_taken:.1f} segundos\n\n"
    
    # Explicación si existe
    if "explanation" in question:
        text += f"💡 **Explicación:**\n_{question['explanation']}_\n\n"
    
    text += "¡No te desanimes! Cada error es una oportunidad de aprender."
    
    # Crear keyboard
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text=f"🧠 Intentar Otra {level_info['emoji']}", callback_data=f"trivia:next:{level}")
    keyboard.button(text="📊 Ver Estadísticas", callback_data="trivia:stats")
    keyboard.button(text="🔄 Cambiar Nivel", callback_data="trivia:main")
    keyboard.button(text="⬅️ Menú Principal", callback_data="main_menu")
    keyboard.adjust(1, 2, 1)
    
    await query.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboard.as_markup()
    )

async def _show_trivia_stats(query: types.CallbackQuery):
    """
    Muestra las estadísticas de trivia del usuario.
    
    Args:
        query: Query del callback.
    """
    user_id = query.from_user.id
    
    # Obtener información del usuario
    user_info = await _get_user_info(user_id)
    if not user_info:
        await query.answer("❌ Error al cargar estadísticas.")
        return
    
    trivia_stats = user_info["trivia_stats"]
    stats_text = format_trivia_stats(trivia_stats)
    
    # Agregar información adicional
    daily_questions = sum(stats.get("answered", 0) for stats in trivia_stats.values())
    remaining_questions = max(0, TRIVIA_CONFIG["max_daily_questions"] - daily_questions)
    
    stats_text += f"\n\n⏰ **Preguntas restantes hoy:** {remaining_questions}"
    
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="🧠 Responder Preguntas", callback_data="trivia:main")
    keyboard.button(text="⬅️ Volver", callback_data="trivia:main")
    keyboard.adjust(1, 1)
    
    await query.message.edit_text(
        stats_text,
        parse_mode="Markdown",
        reply_markup=keyboard.as_markup()
    )

def register_trivia_handler(dp, gamification_service):
    """Registra los handlers de trivia en el dispatcher."""
    # Comando /trivia
    dp.message.register(
        lambda message: handle_trivia_main(message, gamification_service),
        Command("trivia")
    )
    
    # Callbacks de trivia
    dp.callback_query.register(
        lambda query: handle_trivia_callback(query, gamification_service),
        lambda c: c.data.startswith("trivia:")
    )