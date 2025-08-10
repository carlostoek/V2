"""
Handler para el menú principal de gamificación.
Centraliza el acceso a todas las funcionalidades de gamificación.
"""

import logging
from aiogram import types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.modules.gamification.service import GamificationService
from src.bot.keyboards.gamification.main_kb import GamificationKeyboard
from src.bot.database.engine import get_session
from src.bot.database.models.user import User
from src.bot.database.models.gamification import UserPoints
from sqlalchemy import select

logger = logging.getLogger(__name__)

async def handle_gamification_main(query: types.CallbackQuery, gamification_service: GamificationService):
    """
    Maneja el menú principal de gamificación.
    
    Args:
        query: Query del callback.
        gamification_service: Servicio que gestiona la gamificación.
    """
    user_id = query.from_user.id
    
    try:
        # Obtener información del usuario
        user_info = await _get_user_gamification_info(user_id)
        if not user_info:
            await query.answer("❌ Error al cargar información de gamificación.")
            return
        
        await _show_gamification_main_menu(query, user_info)
        
    except Exception as e:
        logger.error(f"Error en gamification main para usuario {user_id}: {e}")
        await query.answer("❌ Error al cargar el menú de gamificación.")

async def _get_user_gamification_info(user_id: int) -> dict:
    """
    Obtiene información completa del usuario para gamificación.
    
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
        
        # Verificar si puede reclamar regalo diario
        can_claim_daily = await _check_daily_reward_availability(user_points)
        
        return {
            "user_id": user_id,
            "level": user.level,
            "role": user.role,
            "current_points": current_points,
            "username": user.username or f"Usuario {user_id}",
            "can_claim_daily": can_claim_daily,
            "show_premium": user.role == "VIP" or user.level >= 5
        }

async def _check_daily_reward_availability(user_points) -> bool:
    """
    Verifica si el usuario puede reclamar recompensa diaria.
    
    Args:
        user_points: Objeto UserPoints del usuario.
        
    Returns:
        True si puede reclamar, False si no.
    """
    if not user_points or not user_points.points_history:
        return True
    
    from datetime import datetime, timedelta
    
    # Buscar última recompensa diaria
    for entry in reversed(user_points.points_history):
        if entry.get("source") == "DailyReward":
            try:
                last_claim = datetime.fromisoformat(entry["timestamp"])
                time_since = datetime.now() - last_claim
                return time_since.total_seconds() >= 86400  # 24 horas
            except:
                continue
    
    return True

async def _show_gamification_main_menu(query: types.CallbackQuery, user_info: dict):
    """
    Muestra el menú principal de gamificación.
    
    Args:
        query: Query del callback.
        user_info: Información del usuario.
    """
    username = user_info["username"]
    level = user_info["level"]
    current_points = user_info["current_points"]
    can_claim_daily = user_info["can_claim_daily"]
    show_premium = user_info["show_premium"]
    
    # Crear mensaje principal
    text = (
        f"🎮 **Centro de Gamificación** 🎮\n\n"
        f"👤 {username} (Nivel {level})\n"
        f"💰 **{current_points:.0f} besitos** disponibles\n\n"
        "🎯 **¿Qué te gustaría hacer hoy?**\n\n"
    )
    
    # Agregar información contextual
    if can_claim_daily:
        text += "🎁 **¡Tienes un regalo diario disponible!**\n"
    
    if level >= 5:
        text += "⭐ **Acceso VIP desbloqueado**\n"
    
    text += "\nSelecciona una opción del menú:"
    
    # Crear keyboard usando la clase especializada
    keyboard = GamificationKeyboard.main_menu(
        user_points=current_points,
        user_level=level,
        show_premium=show_premium
    )
    
    await query.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )

async def handle_gamification_callback(query: types.CallbackQuery, gamification_service: GamificationService):
    """
    Maneja todos los callbacks del sistema de gamificación.
    
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
            await handle_gamification_main(query, gamification_service)
        
        elif action == "daily_reward":
            # Redirigir al handler de daily rewards
            from src.bot.handlers.gamification.daily_rewards import handle_daily_reward
            await handle_daily_reward(query.message, gamification_service)
        
        elif action == "progress":
            await _show_progress_menu(query, gamification_service)
        
        elif action == "achievements":
            await _show_achievements_menu(query, gamification_service)
        
        elif action == "vip_zone":
            await _show_vip_zone(query, gamification_service)
        
        elif action == "settings":
            await _show_settings_menu(query)
        
        elif action.startswith("stats"):
            await _handle_stats_callback(query, parts, gamification_service)
        
        await query.answer()
        
    except Exception as e:
        logger.error(f"Error en gamification callback para usuario {user_id}: {e}")
        await query.answer("❌ Error al procesar la solicitud.")

async def _show_progress_menu(query: types.CallbackQuery, gamification_service: GamificationService):
    """
    Muestra el menú de progreso del usuario.
    
    Args:
        query: Query del callback.
        gamification_service: Servicio de gamificación.
    """
    user_id = query.from_user.id
    
    # Obtener información de progreso
    user_info = await _get_user_gamification_info(user_id)
    missions = await gamification_service.get_user_missions(user_id)
    achievements = await gamification_service.get_user_achievements(user_id)
    
    # Calcular estadísticas
    total_missions = sum(len(missions[key]) for key in missions)
    completed_missions = len(missions["completed"])
    total_achievements = len(achievements["completed"]) + len(achievements["in_progress"])
    completed_achievements = len(achievements["completed"])
    
    text = (
        f"📊 **Tu Progreso en Diana** 📊\n\n"
        f"🎯 **Nivel:** {user_info['level']}\n"
        f"💰 **Besitos:** {user_info['current_points']:.0f}\n\n"
        f"**Misiones:**\n"
        f"✅ Completadas: {completed_missions}\n"
        f"🔄 En progreso: {len(missions['in_progress'])}\n"
        f"📋 Disponibles: {len(missions['available'])}\n\n"
        f"**Logros:**\n"
        f"🏆 Conseguidos: {completed_achievements}/{total_achievements}\n\n"
        "Selecciona qué quieres ver en detalle:"
    )
    
    keyboard = GamificationKeyboard.progress_menu()
    
    await query.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )

async def _show_achievements_menu(query: types.CallbackQuery, gamification_service: GamificationService):
    """
    Muestra el menú de logros.
    
    Args:
        query: Query del callback.
        gamification_service: Servicio de gamificación.
    """
    user_id = query.from_user.id
    
    achievements = await gamification_service.get_user_achievements(user_id)
    
    completed_count = len(achievements["completed"])
    progress_count = len(achievements["in_progress"])
    
    text = (
        f"🏆 **Tus Logros** 🏆\n\n"
        f"✅ **Completados:** {completed_count}\n"
        f"🔄 **En progreso:** {progress_count}\n\n"
        "Los logros te dan puntos extra y reconocimiento.\n"
        "¡Sigue jugando para desbloquear más!\n\n"
        "¿Qué logros quieres ver?"
    )
    
    keyboard = GamificationKeyboard.achievements_menu()
    
    await query.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )

async def _show_vip_zone(query: types.CallbackQuery, gamification_service: GamificationService):
    """
    Muestra la zona VIP.
    
    Args:
        query: Query del callback.
        gamification_service: Servicio de gamificación.
    """
    text = (
        f"⭐ **Zona VIP** ⭐\n\n"
        f"¡Bienvenido al área exclusiva!\n\n"
        f"Aquí encontrarás:\n"
        f"💎 Contenido exclusivo premium\n"
        f"⚡ Multiplicadores especiales\n"
        f"👑 Trivia de nivel experto\n"
        f"🎁 Recompensas VIP únicas\n"
        f"📈 Estadísticas avanzadas\n\n"
        f"Selecciona lo que te interese:"
    )
    
    keyboard = GamificationKeyboard.vip_zone_menu()
    
    await query.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )

async def _show_settings_menu(query: types.CallbackQuery):
    """
    Muestra el menú de configuraciones.
    
    Args:
        query: Query del callback.
    """
    text = (
        f"⚙️ **Configuración de Gamificación** ⚙️\n\n"
        f"Personaliza tu experiencia de juego:\n\n"
        f"🔔 **Notificaciones** - Alertas de recompensas y logros\n"
        f"🎯 **Dificultad** - Nivel de desafío en trivia\n"
        f"📊 **Privacidad** - Control de estadísticas públicas\n"
        f"🎨 **Tema Visual** - Personalización de interfaz\n"
        f"🔄 **Reset** - Reiniciar progreso (¡cuidado!)\n\n"
        f"¿Qué quieres configurar?"
    )
    
    keyboard = GamificationKeyboard.settings_menu()
    
    await query.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )

async def _handle_stats_callback(query: types.CallbackQuery, parts: list, gamification_service: GamificationService):
    """
    Maneja callbacks relacionados con estadísticas.
    
    Args:
        query: Query del callback.
        parts: Partes del callback data.
        gamification_service: Servicio de gamificación.
    """
    if len(parts) < 3:
        return
    
    stats_type = parts[2]
    user_id = query.from_user.id
    
    if stats_type == "general":
        user_points = await gamification_service.get_user_points(user_id)
        
        text = (
            f"📊 **Estadísticas Generales** 📊\n\n"
            f"💰 **Besitos actuales:** {user_points['current_points']:.0f}\n"
            f"📈 **Total ganado:** {user_points['total_earned']:.0f}\n"
            f"💸 **Total gastado:** {user_points['total_spent']:.0f}\n"
            f"🎯 **Nivel:** {user_points['level']}\n"
            f"📊 **Progreso nivel:** {user_points['progress_to_next_level']:.1f}%\n\n"
            f"**Distribución de puntos:**\n"
        )
        
        stats = user_points['stats']
        for category, points in stats.items():
            if points > 0:
                category_name = category.replace('from_', '').replace('_', ' ').title()
                text += f"▫️ {category_name}: {points:.0f}\n"
        
        keyboard = GamificationKeyboard.back_to_gamification()
        
        await query.message.edit_text(
            text,
            parse_mode="Markdown", 
            reply_markup=keyboard
        )

def register_gamification_main_handler(dp, gamification_service):
    """Registra el handler del menú principal de gamificación en el dispatcher."""
    # Callbacks de gamificación
    dp.callback_query.register(
        lambda query: handle_gamification_callback(query, gamification_service),
        lambda c: c.data.startswith("gamification:")
    )