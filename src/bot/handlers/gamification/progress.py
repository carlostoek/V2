"""
Manejador para el seguimiento y visualización del progreso de misiones.
Este módulo contiene las funciones para mostrar y actualizar el progreso de misiones.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.modules.gamification.service import GamificationService
from src.modules.events import MissionCompletedEvent, PointsAwardedEvent
from src.bot.keyboards.keyboard_factory import KeyboardFactory

# Constantes para visualización
PROGRESS_BAR_LENGTH = 10
MISSION_COMPLETED_ICON = "✅"
MISSION_IN_PROGRESS_ICON = "🔄"
MISSION_AVAILABLE_ICON = "⏳"

async def handle_mission_progress(
    message: types.Message,
    user_id: int,
    mission_id: int,
    gamification_service: GamificationService
):
    """
    Maneja la visualización detallada del progreso de una misión.
    
    Args:
        message: Mensaje original.
        user_id: ID del usuario.
        mission_id: ID de la misión.
        gamification_service: Servicio de gamificación.
    """
    # Obtener misiones del usuario
    missions = await gamification_service.get_user_missions(user_id)
    
    # Buscar la misión específica
    mission = find_mission_by_id(missions, mission_id)
    
    if not mission:
        await message.answer(
            "⚠️ No se encontró la misión solicitada.",
            reply_markup=KeyboardFactory.back_button("missions:back_to_menu")
        )
        return
    
    # Crear mensaje con detalles del progreso
    text = generate_mission_progress_text(mission)
    
    # Crear teclado con opciones
    keyboard = create_mission_progress_keyboard(mission)
    
    await message.answer(
        text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )

async def handle_mission_progress_callback(
    query: types.CallbackQuery,
    gamification_service: GamificationService
):
    """
    Maneja los callbacks relacionados con el progreso de misiones.
    
    Args:
        query: Query del callback.
        gamification_service: Servicio de gamificación.
    """
    user_id = query.from_user.id
    callback_data = query.data
    
    # Extraer ID de misión del callback
    action, mission_id = callback_data.split("_")
    mission_id = int(mission_id)
    
    # Obtener misiones del usuario
    missions = await gamification_service.get_user_missions(user_id)
    
    # Buscar la misión específica
    mission = find_mission_by_id(missions, mission_id)
    
    if not mission:
        await query.answer("Misión no encontrada", show_alert=True)
        return
    
    # Diferentes acciones según el callback
    if action == "progress":
        # Mostrar detalles del progreso
        text = generate_mission_progress_text(mission)
        keyboard = create_mission_progress_keyboard(mission)
        
        await query.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    
    elif action == "claim":
        # Reclamar recompensa
        # En una implementación real, esto llamaría al servicio para validar y entregar la recompensa
        text = (
            f"🎁 *¡Recompensa reclamada!*\n\n"
            f"Has recibido {mission['rewards']['points']} besitos por completar "
            f"la misión *{mission['title']}*.\n\n"
        )
        
        # Agregar detalles de objetos si hay
        if mission['rewards']['items'] and len(mission['rewards']['items']) > 0:
            text += "*Objetos recibidos:*\n"
            for item, qty in mission['rewards']['items'].items():
                text += f"▫️ {qty}x {item}\n"
        
        await query.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=KeyboardFactory.back_button("missions:back_to_menu")
        )
    
    await query.answer()

def find_mission_by_id(missions: Dict[str, List[Dict[str, Any]]], mission_id: int) -> Optional[Dict[str, Any]]:
    """
    Busca una misión por su ID en todas las categorías.
    
    Args:
        missions: Diccionario con misiones agrupadas por estado.
        mission_id: ID de la misión a buscar.
        
    Returns:
        La misión encontrada o None.
    """
    for category in ["available", "in_progress", "completed"]:
        for mission in missions[category]:
            if mission["id"] == mission_id:
                return mission
    return None

def generate_mission_progress_text(mission: Dict[str, Any]) -> str:
    """
    Genera el texto con los detalles del progreso de una misión.
    
    Args:
        mission: Datos de la misión.
        
    Returns:
        Texto formateado con Markdown.
    """
    # Determinar estado y ícono
    status = "disponible"
    icon = MISSION_AVAILABLE_ICON
    
    if mission.get("progress_percentage", 0) > 0:
        status = "en progreso"
        icon = MISSION_IN_PROGRESS_ICON
        
        if mission.get("progress_percentage", 0) >= 100:
            status = "completada"
            icon = MISSION_COMPLETED_ICON
    
    # Crear encabezado
    text = f"{icon} *Misión: {mission['title']}*\n\n"
    text += f"_{mission['description']}_\n\n"
    
    # Agregar estado y progreso
    text += f"*Estado:* {status.capitalize()}\n"
    text += f"*Progreso total:* {mission.get('progress_percentage', 0):.0f}%\n"
    
    # Crear barra de progreso
    progress_bar = generate_progress_bar(mission.get('progress_percentage', 0))
    text += f"{progress_bar}\n\n"
    
    # Agregar objetivos si tiene
    if mission.get("objectives"):
        text += "*Objetivos:*\n"
        for objective in mission["objectives"]:
            obj_id = objective["id"]
            current = mission["progress"].get(obj_id, 0)
            required = objective["required"]
            percentage = min(100, (current / required) * 100) if required > 0 else 0
            
            # Generar mini barra de progreso para el objetivo
            mini_bar = generate_progress_bar(percentage, 5)
            
            obj_desc = objective.get("description", "Objetivo")
            text += f"▫️ {obj_desc}: {current}/{required} {mini_bar}\n"
    
    # Agregar fechas importantes
    if mission.get("started_at"):
        try:
            dt = datetime.fromisoformat(mission["started_at"])
            text += f"\n*Iniciada:* {dt.strftime('%d/%m/%Y %H:%M')}\n"
        except:
            pass
    
    if mission.get("completed_at"):
        try:
            dt = datetime.fromisoformat(mission["completed_at"])
            text += f"*Completada:* {dt.strftime('%d/%m/%Y %H:%M')}\n"
        except:
            pass
    
    if mission.get("expires_at"):
        try:
            dt = datetime.fromisoformat(mission["expires_at"])
            text += f"*Expira:* {dt.strftime('%d/%m/%Y %H:%M')}\n"
        except:
            pass
    
    # Agregar recompensas
    text += "\n*Recompensas:*\n"
    text += f"▫️ {mission['rewards']['points']} besitos\n"
    
    if mission['rewards']['items'] and len(mission['rewards']['items']) > 0:
        for item, qty in mission['rewards']['items'].items():
            text += f"▫️ {qty}x {item}\n"
    
    return text

def create_mission_progress_keyboard(mission: Dict[str, Any]) -> types.InlineKeyboardMarkup:
    """
    Crea un teclado con opciones para la misión según su estado.
    
    Args:
        mission: Datos de la misión.
        
    Returns:
        Teclado inline.
    """
    keyboard = InlineKeyboardBuilder()
    
    # Botones según estado
    progress = mission.get("progress_percentage", 0)
    
    if progress >= 100 and not mission.get("reward_claimed", True):
        # Misión completada, mostrar botón para reclamar recompensa
        keyboard.button(
            text="🎁 Reclamar Recompensa",
            callback_data=f"claim_{mission['id']}"
        )
    elif 0 < progress < 100:
        # Misión en progreso, mostrar detalles
        keyboard.button(
            text="🔄 Actualizar Progreso",
            callback_data=f"refresh_{mission['id']}"
        )
    elif progress == 0:
        # Misión disponible, mostrar botón para iniciar
        keyboard.button(
            text="▶️ Iniciar Misión",
            callback_data=f"start_{mission['id']}"
        )
    
    # Botón para volver
    keyboard.button(
        text="⬅️ Volver a Misiones",
        callback_data="missions:back_to_menu"
    )
    
    keyboard.adjust(1)  # Un botón por fila
    return keyboard.as_markup()

def generate_progress_bar(percentage: float, length: int = PROGRESS_BAR_LENGTH) -> str:
    """
    Genera una barra de progreso de texto.
    
    Args:
        percentage: Porcentaje de progreso (0-100).
        length: Longitud de la barra.
        
    Returns:
        String con la barra de progreso.
    """
    filled = int((percentage / 100) * length)
    bar = "█" * filled + "▒" * (length - filled)
    return f"[{bar}] {percentage:.0f}%"

async def send_mission_update_notification(
    bot: Any, 
    user_id: int, 
    mission_id: int,
    progress: float,
    gamification_service: GamificationService
) -> None:
    """
    Envía una notificación al usuario sobre actualización de progreso en una misión.
    
    Args:
        bot: Instancia del bot para enviar mensajes.
        user_id: ID del usuario.
        mission_id: ID de la misión.
        progress: Nuevo porcentaje de progreso.
        gamification_service: Servicio de gamificación.
    """
    # Obtener misiones del usuario
    missions = await gamification_service.get_user_missions(user_id)
    
    # Buscar la misión específica
    mission = find_mission_by_id(missions, mission_id)
    
    if not mission:
        return
    
    # Crear mensaje de notificación
    progress_bar = generate_progress_bar(progress)
    
    text = (
        f"🔔 *Actualización de misión*\n\n"
        f"Tu misión *{mission['title']}* ha sido actualizada.\n"
        f"Progreso: {progress_bar}\n\n"
        f"Usa /misiones para ver los detalles."
    )
    
    # Crear teclado para ver detalles
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="🔍 Ver Detalles",
        callback_data=f"missions:view_{mission_id}"
    )
    keyboard.adjust(1)
    
    # Enviar notificación
    try:
        await bot.send_message(
            chat_id=user_id,
            text=text,
            parse_mode="Markdown",
            reply_markup=keyboard.as_markup()
        )
    except Exception as e:
        # Si falla el envío, solo loggear el error (no bloquear el flujo)
        print(f"Error al enviar notificación de misión: {e}")

async def send_mission_completed_notification(
    bot: Any, 
    event: MissionCompletedEvent,
    gamification_service: GamificationService
) -> None:
    """
    Envía una notificación al usuario sobre una misión completada.
    
    Args:
        bot: Instancia del bot para enviar mensajes.
        event: Evento de misión completada.
        gamification_service: Servicio de gamificación.
    """
    user_id = event.user_id
    mission_id = event.mission_id
    
    # Obtener misiones del usuario
    missions = await gamification_service.get_user_missions(user_id)
    
    # Encontrar la misión por clave
    mission = None
    for m in missions["completed"]:
        if m["key"] == mission_id:
            mission = m
            break
    
    if not mission:
        return
    
    # Crear mensaje de notificación
    text = (
        f"🎉 *¡Misión completada!*\n\n"
        f"Has completado la misión *{mission['title']}*.\n"
        f"Recompensa: {event.reward_points} besitos\n\n"
        f"Usa /misiones para reclamar tu recompensa."
    )
    
    # Crear teclado para reclamar recompensa
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="🎁 Reclamar Recompensa",
        callback_data=f"missions:claim_{mission['id']}"
    )
    keyboard.adjust(1)
    
    # Enviar notificación
    try:
        await bot.send_message(
            chat_id=user_id,
            text=text,
            parse_mode="Markdown",
            reply_markup=keyboard.as_markup()
        )
    except Exception as e:
        # Si falla el envío, solo loggear el error (no bloquear el flujo)
        print(f"Error al enviar notificación de misión completada: {e}")

def register_mission_progress_handlers(dp, gamification_service):
    """Registra los handlers de progreso de misiones en el dispatcher."""
    # Callbacks para progreso de misiones
    dp.callback_query.register(
        lambda query: handle_mission_progress_callback(query, gamification_service),
        lambda c: c.data.startswith(("progress_", "claim_", "refresh_", "start_"))
    )