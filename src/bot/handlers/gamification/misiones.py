"""
Handler para el comando /misiones, que muestra las misiones 
disponibles, en progreso y completadas por el usuario.
"""

from datetime import datetime
from aiogram import types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.modules.gamification.service import GamificationService
from src.bot.keyboards.keyboard_factory import KeyboardFactory

async def handle_misiones(
    message: types.Message, 
    gamification_service: GamificationService
):
    """
    Maneja el comando /misiones que muestra las misiones disponibles.
    
    Args:
        message: Mensaje que contiene el comando.
        gamification_service: Servicio que gestiona la gamificación.
    """
    user_id = message.from_user.id
    
    # Obtener misiones del usuario
    missions = await gamification_service.get_user_missions(user_id)
    
    # Mostrar menú principal de misiones
    await _show_missions_menu(message, missions)

async def _show_missions_menu(message: types.Message, missions: dict):
    """
    Muestra el menú principal de misiones.
    
    Args:
        message: Mensaje original.
        missions: Diccionario con misiones agrupadas por estado.
    """
    # Preparar contador de misiones
    available_count = len(missions["available"])
    in_progress_count = len(missions["in_progress"])
    completed_count = len(missions["completed"])
    total_count = available_count + in_progress_count + completed_count
    
    if total_count == 0:
        # No hay misiones disponibles
        text = (
            "🎯 *Misiones*\n\n"
            "No tienes misiones disponibles en este momento.\n\n"
            "Interactúa con el bot y explora la narrativa para desbloquear misiones."
        )
        await message.answer(
            text,
            parse_mode="Markdown",
            reply_markup=KeyboardFactory.back_button("main_menu:missions")
        )
        return
    
    # Crear texto para el menú principal
    text = (
        "🎯 *Misiones*\n\n"
        f"Tienes {total_count} misiones en total:\n"
        f"▫️ {available_count} misiones disponibles\n"
        f"▫️ {in_progress_count} misiones en progreso\n"
        f"▫️ {completed_count} misiones completadas\n\n"
        "Selecciona una categoría para ver detalles:"
    )
    
    # Crear teclado para el menú de misiones
    keyboard = KeyboardFactory.missions_menu()
    
    await message.answer(
        text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )

async def handle_missions_callback(
    query: types.CallbackQuery, 
    gamification_service: GamificationService
):
    """
    Maneja los callbacks del menú de misiones.
    
    Args:
        query: Query del callback.
        gamification_service: Servicio que gestiona la gamificación.
    """
    user_id = query.from_user.id
    callback_data = query.data
    action = callback_data.split(":")[1]
    
    # Obtener misiones del usuario
    missions = await gamification_service.get_user_missions(user_id)
    
    if action == "active":
        # Mostrar misiones disponibles y en progreso
        await _show_active_missions(query, missions)
    elif action == "completed":
        # Mostrar misiones completadas
        await _show_completed_missions(query, missions)
    elif action == "find":
        # Buscar nuevas misiones
        await _find_new_missions(query, gamification_service)
    elif action == "back_to_main":
        # Volver al menú principal
        await query.message.edit_text(
            "¡Bienvenido a Diana V2! ¿Qué te gustaría hacer hoy?",
            reply_markup=KeyboardFactory.main_menu()
        )
    elif action.startswith("view_"):
        # Ver detalles de una misión específica
        mission_id = int(action.split("_")[1])
        await _show_mission_details(query, missions, mission_id)
    
    await query.answer()

async def _show_active_missions(query: types.CallbackQuery, missions: dict):
    """
    Muestra las misiones disponibles y en progreso.
    
    Args:
        query: Query del callback.
        missions: Diccionario con misiones agrupadas por estado.
    """
    available = missions["available"]
    in_progress = missions["in_progress"]
    
    if not available and not in_progress:
        text = (
            "🎯 *Misiones Activas*\n\n"
            "No tienes misiones activas en este momento.\n\n"
            "Puedes buscar nuevas misiones o interactuar con el bot para desbloquear más."
        )
        await query.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=KeyboardFactory.back_button("missions:back_to_menu")
        )
        return
    
    # Crear texto para el menú
    text = "🎯 *Misiones Activas*\n\n"
    
    # Agregar misiones en progreso
    if in_progress:
        text += "*En Progreso:*\n"
        for mission in in_progress:
            progress_bar = _generate_progress_bar(mission["progress_percentage"])
            text += (
                f"▫️ *{mission['title']}*\n"
                f"  {progress_bar} {mission['progress_percentage']:.0f}%\n"
                f"  _{mission['description']}_\n\n"
            )
    
    # Agregar misiones disponibles
    if available:
        text += "*Disponibles:*\n"
        for mission in available:
            text += (
                f"▫️ *{mission['title']}*\n"
                f"  _{mission['description']}_\n\n"
            )
    
    # Crear teclado con las misiones
    keyboard = InlineKeyboardBuilder()
    
    # Añadir botones para cada misión
    for mission in in_progress + available:
        keyboard.button(
            text=f"{mission['title']} ({mission['progress_percentage']:.0f}%)",
            callback_data=f"missions:view_{mission['id']}"
        )
    
    # Añadir botón para volver
    keyboard.button(
        text="⬅️ Volver",
        callback_data="missions:back_to_menu"
    )
    
    keyboard.adjust(1)  # Un botón por fila
    
    await query.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboard.as_markup()
    )

async def _show_completed_missions(query: types.CallbackQuery, missions: dict):
    """
    Muestra las misiones completadas.
    
    Args:
        query: Query del callback.
        missions: Diccionario con misiones agrupadas por estado.
    """
    completed = missions["completed"]
    
    if not completed:
        text = (
            "🎯 *Misiones Completadas*\n\n"
            "No has completado ninguna misión aún.\n\n"
            "Completa misiones para obtener recompensas y desbloquear logros."
        )
        await query.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=KeyboardFactory.back_button("missions:back_to_menu")
        )
        return
    
    # Crear texto para el menú
    text = (
        "🎯 *Misiones Completadas*\n\n"
        f"Has completado {len(completed)} misiones:\n\n"
    )
    
    # Agregar misiones completadas
    for mission in completed:
        # Formatear fecha de completado
        completed_date = None
        if mission["completed_at"]:
            try:
                dt = datetime.fromisoformat(mission["completed_at"])
                completed_date = dt.strftime("%d/%m/%Y")
            except:
                completed_date = "Fecha desconocida"
        
        text += (
            f"✅ *{mission['title']}*\n"
            f"  _Completada: {completed_date}_\n"
            f"  _Recompensa: {mission['rewards']['points']} besitos_\n\n"
        )
    
    # Crear teclado con las misiones
    keyboard = InlineKeyboardBuilder()
    
    # Añadir botones para cada misión
    for mission in completed:
        keyboard.button(
            text=f"{mission['title']} (Completada)",
            callback_data=f"missions:view_{mission['id']}"
        )
    
    # Añadir botón para volver
    keyboard.button(
        text="⬅️ Volver",
        callback_data="missions:back_to_menu"
    )
    
    keyboard.adjust(1)  # Un botón por fila
    
    await query.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboard.as_markup()
    )

async def _find_new_missions(query: types.CallbackQuery, gamification_service: GamificationService):
    """
    Busca nuevas misiones disponibles.
    
    Args:
        query: Query del callback.
        gamification_service: Servicio que gestiona la gamificación.
    """
    # En una implementación real, este método podría intentar buscar
    # nuevas misiones disponibles para el usuario, pero por ahora
    # solo mostramos un mensaje informativo
    
    text = (
        "🔍 *Buscar Nuevas Misiones*\n\n"
        "Las misiones se desbloquean automáticamente a medida que avanzas en la historia "
        "y completas diferentes acciones.\n\n"
        "Algunas misiones se desbloquean:\n"
        "▫️ Al subir de nivel\n"
        "▫️ Al completar misiones anteriores\n"
        "▫️ Después de ciertos eventos narrativos\n"
        "▫️ Al desbloquear pistas específicas\n\n"
        "Continúa interactuando con Diana para desbloquear más misiones."
    )
    
    await query.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=KeyboardFactory.back_button("missions:back_to_menu")
    )

async def _show_mission_details(query: types.CallbackQuery, missions: dict, mission_id: int):
    """
    Muestra los detalles de una misión específica.
    
    Args:
        query: Query del callback.
        missions: Diccionario con misiones agrupadas por estado.
        mission_id: ID de la misión a mostrar.
    """
    # Buscar la misión en todas las categorías
    mission = None
    status = None
    
    for category in ["available", "in_progress", "completed"]:
        for m in missions[category]:
            if m["id"] == mission_id:
                mission = m
                status = category
                break
        if mission:
            break
    
    if not mission:
        await query.message.edit_text(
            "⚠️ Misión no encontrada",
            reply_markup=KeyboardFactory.back_button("missions:back_to_menu")
        )
        return
    
    # Crear texto con detalles de la misión
    text = f"🎯 *{mission['title']}*\n\n"
    text += f"_{mission['description']}_\n\n"
    
    # Detalles adicionales según el estado
    if status == "completed":
        text += "✅ *Misión completada*\n"
        if mission["completed_at"]:
            try:
                dt = datetime.fromisoformat(mission["completed_at"])
                text += f"Completada el: {dt.strftime('%d/%m/%Y')}\n"
            except:
                pass
    elif status == "in_progress":
        text += f"*Progreso: {mission['progress_percentage']:.0f}%*\n"
        progress_bar = _generate_progress_bar(mission['progress_percentage'])
        text += f"{progress_bar}\n\n"
        
        # Mostrar objetivos
        text += "*Objetivos:*\n"
        for objective in mission["objectives"]:
            obj_id = objective["id"]
            current = mission["progress"].get(obj_id, 0)
            required = objective["required"]
            percentage = min(100, (current / required) * 100) if required > 0 else 0
            
            obj_desc = objective.get("description", "Objetivo")
            text += f"▫️ {obj_desc}: {current}/{required} ({percentage:.0f}%)\n"
    else:  # available
        text += "*Misión disponible*\n"
        if mission["expires_at"]:
            try:
                dt = datetime.fromisoformat(mission["expires_at"])
                text += f"Disponible hasta: {dt.strftime('%d/%m/%Y')}\n"
            except:
                pass
    
    # Mostrar recompensas
    text += "\n*Recompensas:*\n"
    text += f"▫️ {mission['rewards']['points']} besitos\n"
    
    # Añadir recompensas de objetos si existen
    if mission["rewards"]["items"] and len(mission["rewards"]["items"]) > 0:
        for item, qty in mission["rewards"]["items"].items():
            text += f"▫️ {qty}x {item}\n"
    
    # Botones para acciones
    keyboard = InlineKeyboardBuilder()
    
    if status == "available":
        keyboard.button(
            text="▶️ Iniciar Misión",
            callback_data=f"missions:start_{mission_id}"
        )
    elif status == "in_progress":
        keyboard.button(
            text="📊 Ver Progreso",
            callback_data=f"missions:progress_{mission_id}"
        )
    elif status == "completed" and not mission.get("reward_claimed", True):
        keyboard.button(
            text="🎁 Reclamar Recompensa",
            callback_data=f"missions:claim_{mission_id}"
        )
    
    # Botón para volver
    if status == "completed":
        keyboard.button(
            text="⬅️ Volver a Completadas",
            callback_data="missions:completed"
        )
    else:
        keyboard.button(
            text="⬅️ Volver a Activas",
            callback_data="missions:active"
        )
    
    keyboard.adjust(1)  # Un botón por fila
    
    await query.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboard.as_markup()
    )

def _generate_progress_bar(percentage: float, length: int = 10) -> str:
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
    return f"[{bar}]"

async def handle_missions_back_to_menu(query: types.CallbackQuery):
    """
    Maneja el callback para volver al menú de misiones.
    
    Args:
        query: Query del callback.
    """
    # Obtener misiones del usuario
    missions = await query.bot.gamification_service.get_user_missions(query.from_user.id)
    
    # Preparar contador de misiones
    available_count = len(missions["available"])
    in_progress_count = len(missions["in_progress"])
    completed_count = len(missions["completed"])
    total_count = available_count + in_progress_count + completed_count
    
    # Crear texto para el menú principal
    text = (
        "🎯 *Misiones*\n\n"
        f"Tienes {total_count} misiones en total:\n"
        f"▫️ {available_count} misiones disponibles\n"
        f"▫️ {in_progress_count} misiones en progreso\n"
        f"▫️ {completed_count} misiones completadas\n\n"
        "Selecciona una categoría para ver detalles:"
    )
    
    # Crear teclado para el menú de misiones
    keyboard = KeyboardFactory.missions_menu()
    
    await query.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    await query.answer()

def register_misiones_handler(dp, gamification_service):
    """Registra el handler del comando /misiones en el dispatcher."""
    # Comando /misiones
    dp.message.register(
        lambda message: handle_misiones(message, gamification_service),
        Command("misiones")
    )
    
    # Callback desde el menú principal
    dp.callback_query.register(
        lambda query: handle_missions_callback(query, gamification_service),
        lambda c: c.data.startswith("missions:") and not c.data == "missions:back_to_menu"
    )
    
    # Callback para volver al menú de misiones
    dp.callback_query.register(
        handle_missions_back_to_menu,
        F.data == "missions:back_to_menu"
    )
    
    # Callback desde el menú principal
    dp.callback_query.register(
        lambda query: handle_misiones(query.message, gamification_service),
        F.data == "main_menu:missions"
    )