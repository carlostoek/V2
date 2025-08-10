"""
Handler para el comando /regalo (Daily Rewards).
Permite a los usuarios reclamar recompensas diarias con sistema de racha.
"""

import logging
from datetime import datetime, timedelta
from aiogram import types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.modules.gamification.service import GamificationService
from src.bot.database.engine import get_session
from src.bot.database.models.gamification import UserPoints
from sqlalchemy import select

logger = logging.getLogger(__name__)

# Configuración de recompensas diarias
DAILY_REWARDS_CONFIG = {
    "base_reward": 20,  # Besitos base
    "streak_multipliers": {
        1: 1.0,   # Día 1: x1.0
        3: 1.2,   # Día 3: x1.2
        7: 1.5,   # Día 7: x1.5
        14: 1.8,  # Día 14: x1.8
        30: 2.0   # Día 30+: x2.0
    },
    "max_streak_reward": 100,  # Máximo besitos por día
    "streak_reset_hours": 48   # Horas para perder la racha
}

async def handle_daily_reward(message: types.Message, gamification_service: GamificationService):
    """
    Maneja el comando /regalo para recompensas diarias.
    
    Args:
        message: Mensaje que contiene el comando.
        gamification_service: Servicio que gestiona la gamificación.
    """
    user_id = message.from_user.id
    
    try:
        # Verificar si puede reclamar recompensa
        reward_info = await _check_daily_reward_availability(user_id)
        
        if not reward_info["can_claim"]:
            await _show_already_claimed_message(message, reward_info)
            return
        
        # Otorgar recompensa diaria
        reward_result = await _grant_daily_reward(user_id, gamification_service)
        
        # Mostrar mensaje de recompensa otorgada
        await _show_reward_granted_message(message, reward_result)
        
    except Exception as e:
        logger.error(f"Error en daily reward para usuario {user_id}: {e}")
        await message.answer(
            "❌ Ocurrió un error al procesar tu recompensa diaria. "
            "Inténtalo de nuevo más tarde."
        )

async def _check_daily_reward_availability(user_id: int) -> dict:
    """
    Verifica si el usuario puede reclamar la recompensa diaria.
    
    Args:
        user_id: ID del usuario.
        
    Returns:
        Dict con información sobre la disponibilidad de la recompensa.
    """
    async for session in get_session():
        # Obtener datos de puntos del usuario
        query = select(UserPoints).where(UserPoints.user_id == user_id)
        result = await session.execute(query)
        user_points = result.scalars().first()
        
        now = datetime.now()
        
        if not user_points:
            # Usuario nuevo, puede reclamar
            return {
                "can_claim": True,
                "is_first_time": True,
                "current_streak": 0,
                "next_claim_time": None
            }
        
        # Verificar última reclamación en el historial
        last_daily_reward = None
        for entry in reversed(user_points.points_history):
            if entry.get("source") == "DailyReward":
                last_daily_reward = datetime.fromisoformat(entry["timestamp"])
                break
        
        if not last_daily_reward:
            # Primera vez reclamando
            return {
                "can_claim": True,
                "is_first_time": True,
                "current_streak": 0,
                "next_claim_time": None
            }
        
        # Verificar si han pasado 24 horas
        time_since_last = now - last_daily_reward
        
        if time_since_last.total_seconds() < 86400:  # 24 horas en segundos
            # No puede reclamar aún
            next_claim = last_daily_reward + timedelta(hours=24)
            return {
                "can_claim": False,
                "is_first_time": False,
                "time_remaining": next_claim - now,
                "next_claim_time": next_claim
            }
        
        # Calcular racha actual
        current_streak = _calculate_current_streak(user_points.points_history)
        
        # Verificar si la racha se rompió
        if time_since_last.total_seconds() > (DAILY_REWARDS_CONFIG["streak_reset_hours"] * 3600):
            current_streak = 0
        
        return {
            "can_claim": True,
            "is_first_time": False,
            "current_streak": current_streak,
            "next_claim_time": None
        }

def _calculate_current_streak(points_history: list) -> int:
    """
    Calcula la racha actual de recompensas diarias.
    
    Args:
        points_history: Historial de puntos del usuario.
        
    Returns:
        Número de días consecutivos de recompensas.
    """
    if not points_history:
        return 0
    
    streak = 0
    current_date = datetime.now().date()
    
    # Buscar recompensas diarias en orden inverso
    for entry in reversed(points_history):
        if entry.get("source") != "DailyReward":
            continue
        
        try:
            reward_date = datetime.fromisoformat(entry["timestamp"]).date()
            expected_date = current_date - timedelta(days=streak)
            
            if reward_date == expected_date:
                streak += 1
            elif reward_date == expected_date - timedelta(days=1):
                # Recompensa de ayer, continúa la racha
                streak += 1
                current_date = reward_date
            else:
                # Se rompió la racha
                break
        except (ValueError, KeyError):
            continue
    
    return streak

async def _grant_daily_reward(user_id: int, gamification_service: GamificationService) -> dict:
    """
    Otorga la recompensa diaria al usuario.
    
    Args:
        user_id: ID del usuario.
        gamification_service: Servicio de gamificación.
        
    Returns:
        Dict con información sobre la recompensa otorgada.
    """
    # Verificar disponibilidad nuevamente (por seguridad)
    reward_info = await _check_daily_reward_availability(user_id)
    
    if not reward_info["can_claim"]:
        return {"success": False, "error": "No se puede reclamar en este momento"}
    
    # Calcular recompensa basada en la racha
    base_reward = DAILY_REWARDS_CONFIG["base_reward"]
    current_streak = reward_info["current_streak"] + 1  # +1 porque será el nuevo día
    
    # Obtener multiplicador de racha
    multiplier = 1.0
    for streak_milestone in sorted(DAILY_REWARDS_CONFIG["streak_multipliers"].keys(), reverse=True):
        if current_streak >= streak_milestone:
            multiplier = DAILY_REWARDS_CONFIG["streak_multipliers"][streak_milestone]
            break
    
    # Calcular recompensa final
    reward_points = min(
        int(base_reward * multiplier),
        DAILY_REWARDS_CONFIG["max_streak_reward"]
    )
    
    # Simular evento de recompensa diaria para el sistema de gamificación
    class DailyRewardEvent:
        def __init__(self, user_id):
            self.user_id = user_id
    
    # Otorgar puntos a través del servicio
    await gamification_service._award_points(user_id, reward_points, DailyRewardEvent(user_id))
    
    # Calcular bonus por racha
    streak_bonus = 0
    if current_streak >= 7:
        streak_bonus = min(current_streak * 2, 50)  # Máximo 50 bonus
    
    if streak_bonus > 0:
        await gamification_service._award_points(user_id, streak_bonus, DailyRewardEvent(user_id))
    
    return {
        "success": True,
        "points_awarded": reward_points + streak_bonus,
        "base_points": reward_points,
        "streak_bonus": streak_bonus,
        "current_streak": current_streak,
        "multiplier": multiplier,
        "next_milestone": _get_next_streak_milestone(current_streak)
    }

def _get_next_streak_milestone(current_streak: int) -> dict:
    """
    Obtiene información sobre el próximo hito de racha.
    
    Args:
        current_streak: Racha actual.
        
    Returns:
        Dict con información del próximo hito.
    """
    milestones = sorted(DAILY_REWARDS_CONFIG["streak_multipliers"].keys())
    
    for milestone in milestones:
        if current_streak < milestone:
            return {
                "days": milestone,
                "multiplier": DAILY_REWARDS_CONFIG["streak_multipliers"][milestone],
                "days_remaining": milestone - current_streak
            }
    
    # Ya alcanzó el máximo
    return {
        "days": max(milestones),
        "multiplier": DAILY_REWARDS_CONFIG["streak_multipliers"][max(milestones)],
        "days_remaining": 0,
        "is_max": True
    }

async def _show_already_claimed_message(message: types.Message, reward_info: dict):
    """
    Muestra mensaje cuando ya se reclamó la recompensa.
    
    Args:
        message: Mensaje original.
        reward_info: Información sobre la recompensa.
    """
    time_remaining = reward_info.get("time_remaining")
    
    if time_remaining:
        hours = int(time_remaining.total_seconds() // 3600)
        minutes = int((time_remaining.total_seconds() % 3600) // 60)
        
        time_text = ""
        if hours > 0:
            time_text += f"{hours}h "
        if minutes > 0:
            time_text += f"{minutes}m"
        
        text = (
            "🎁 *Recompensa Diaria*\n\n"
            "Ya reclamaste tu recompensa diaria.\n\n"
            f"⏰ Próxima recompensa disponible en: **{time_text}**\n\n"
            "¡Vuelve mañana para mantener tu racha!"
        )
    else:
        text = (
            "🎁 *Recompensa Diaria*\n\n"
            "Ya reclamaste tu recompensa diaria.\n\n"
            "¡Vuelve mañana para más besitos!"
        )
    
    # Crear keyboard con opciones adicionales
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="🏆 Ver Mi Perfil", callback_data="main_menu:profile")
    keyboard.button(text="🎯 Ver Misiones", callback_data="main_menu:missions")
    keyboard.button(text="🛍️ Ir a la Tienda", callback_data="shop:main")
    keyboard.button(text="⬅️ Menú Principal", callback_data="main_menu")
    keyboard.adjust(2, 1, 1)
    
    await message.answer(
        text,
        parse_mode="Markdown",
        reply_markup=keyboard.as_markup()
    )

async def _show_reward_granted_message(message: types.Message, reward_result: dict):
    """
    Muestra mensaje de recompensa otorgada.
    
    Args:
        message: Mensaje original.
        reward_result: Resultado de otorgar la recompensa.
    """
    if not reward_result["success"]:
        await message.answer("❌ No se pudo otorgar la recompensa. Inténtalo más tarde.")
        return
    
    current_streak = reward_result["current_streak"]
    points_awarded = reward_result["points_awarded"]
    base_points = reward_result["base_points"]
    streak_bonus = reward_result["streak_bonus"]
    multiplier = reward_result["multiplier"]
    next_milestone = reward_result["next_milestone"]
    
    # Crear mensaje principal
    text = f"🎁 *¡Recompensa Diaria Reclamada!*\n\n"
    text += f"💰 **+{points_awarded} besitos** otorgados\n\n"
    
    # Información de la racha
    if current_streak > 1:
        text += f"🔥 **Racha de {current_streak} días**\n"
        text += f"📈 Multiplicador: x{multiplier}\n"
        
        if streak_bonus > 0:
            text += f"🎉 Bonus por racha: +{streak_bonus} besitos\n"
        
        text += "\n"
    else:
        text += "🌟 ¡Primera recompensa del día!\n\n"
    
    # Información del próximo hito
    if not next_milestone.get("is_max"):
        days_remaining = next_milestone["days_remaining"]
        next_multiplier = next_milestone["multiplier"]
        text += f"🎯 **Próximo hito:** {days_remaining} días más para x{next_multiplier}\n"
    else:
        text += "👑 **¡Has alcanzado el máximo multiplicador!**\n"
    
    text += "\n💡 *Vuelve mañana para mantener tu racha*"
    
    # Crear keyboard con opciones
    keyboard = InlineKeyboardBuilder()
    
    # Botones principales
    keyboard.button(text="🛍️ Ir a la Tienda", callback_data="shop:main")
    keyboard.button(text="🎯 Ver Misiones", callback_data="main_menu:missions")
    keyboard.button(text="🏆 Mi Perfil", callback_data="main_menu:profile")
    
    # Botón de juego adicional
    if current_streak >= 3:
        keyboard.button(text="🎮 Jugar Trivia", callback_data="trivia:main")
    
    keyboard.button(text="⬅️ Menú Principal", callback_data="main_menu")
    
    keyboard.adjust(2, 1, 1, 1)
    
    await message.answer(
        text,
        parse_mode="Markdown",
        reply_markup=keyboard.as_markup()
    )

def register_daily_rewards_handler(dp, gamification_service):
    """Registra el handler del comando /regalo en el dispatcher."""
    dp.message.register(
        lambda message: handle_daily_reward(message, gamification_service),
        Command("regalo")
    )
    
    # También registrar como callback desde el menú principal
    dp.callback_query.register(
        lambda query: handle_daily_reward(query.message, gamification_service),
        lambda c: c.data == "main_menu:daily_reward" or c.data == "gamification:daily_reward"
    )