"""
Handler para el comando /tienda (Shop System).
Sistema completo de tienda con 4 categorías, navegación y compras.
"""

import logging
from datetime import datetime
from aiogram import types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.modules.gamification.service import GamificationService
from src.bot.handlers.gamification.shop_data import (
    SHOP_CATEGORIES, SHOP_ITEMS, get_item_by_id, get_items_by_category,
    calculate_final_price, format_item_description, RARITY_CONFIG
)
from src.bot.database.engine import get_session
from src.bot.database.models.user import User
from src.bot.database.models.gamification import UserPoints
from sqlalchemy import select, update

logger = logging.getLogger(__name__)

# Configuración de paginación
ITEMS_PER_PAGE = 5
MAX_PAGE_BUTTONS = 5

async def handle_shop_main(message: types.Message, gamification_service: GamificationService):
    """
    Maneja el comando /tienda - muestra el menú principal de la tienda.
    
    Args:
        message: Mensaje que contiene el comando.
        gamification_service: Servicio que gestiona la gamificación.
    """
    user_id = message.from_user.id
    
    try:
        # Obtener información del usuario
        user_info = await _get_user_info(user_id)
        if not user_info:
            await message.answer("❌ Error al cargar tu información. Inténtalo más tarde.")
            return
        
        await _show_shop_main_menu(message, user_info)
        
    except Exception as e:
        logger.error(f"Error en shop main para usuario {user_id}: {e}")
        await message.answer("❌ Error al cargar la tienda. Inténtalo más tarde.")

async def _get_user_info(user_id: int) -> dict:
    """
    Obtiene información básica del usuario necesaria para la tienda.
    
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
        
        return {
            "user_id": user_id,
            "level": user.level,
            "role": user.role,
            "current_points": current_points,
            "username": user.username or f"Usuario {user_id}"
        }

async def _show_shop_main_menu(message: types.Message, user_info: dict):
    """
    Muestra el menú principal de la tienda.
    
    Args:
        message: Mensaje donde mostrar el menú.
        user_info: Información del usuario.
    """
    current_points = user_info["current_points"]
    level = user_info["level"]
    username = user_info["username"]
    
    text = (
        f"🛍️ **Tienda de Diana** 🛍️\n\n"
        f"👤 {username} (Nivel {level})\n"
        f"💰 **{current_points:.0f} besitos** disponibles\n\n"
        "Selecciona una categoría para explorar:\n"
    )
    
    # Crear keyboard con categorías
    keyboard = InlineKeyboardBuilder()
    
    # Ordenar categorías por orden
    sorted_categories = sorted(
        SHOP_CATEGORIES.items(),
        key=lambda x: x[1]["order"]
    )
    
    for category_key, category_info in sorted_categories:
        # Contar items disponibles para el usuario
        available_items = get_items_by_category(category_key, level)
        item_count = len(available_items)
        
        button_text = f"{category_info['emoji']} {category_info['name'].split(' ', 1)[1]} ({item_count})"
        keyboard.button(
            text=button_text,
            callback_data=f"shop:category:{category_key}:0"
        )
    
    # Botones adicionales
    keyboard.button(text="🏆 Mi Perfil", callback_data="main_menu:profile")
    keyboard.button(text="🎯 Misiones", callback_data="main_menu:missions")
    keyboard.button(text="⬅️ Menú Principal", callback_data="main_menu")
    
    keyboard.adjust(1, 1, 1, 1, 2, 1)  # 1 botón por categoría, luego 2 botones, luego 1
    
    await message.answer(
        text,
        parse_mode="Markdown",
        reply_markup=keyboard.as_markup()
    )

async def handle_shop_callback(query: types.CallbackQuery, gamification_service: GamificationService):
    """
    Maneja todos los callbacks relacionados con la tienda.
    
    Args:
        query: Query del callback.
        gamification_service: Servicio que gestiona la gamificación.
    """
    user_id = query.from_user.id
    callback_data = query.data
    
    try:
        parts = callback_data.split(":")
        action = parts[1]
        
        # Obtener información del usuario
        user_info = await _get_user_info(user_id)
        if not user_info:
            await query.answer("❌ Error al cargar tu información.")
            return
        
        if action == "main":
            await _show_shop_main_menu(query.message, user_info)
        
        elif action == "category":
            category = parts[2]
            page = int(parts[3])
            await _show_category_items(query, user_info, category, page)
        
        elif action == "item":
            item_id = parts[2]
            await _show_item_details(query, user_info, item_id)
        
        elif action == "buy":
            item_id = parts[2]
            await _process_purchase(query, user_info, item_id, gamification_service)
        
        elif action == "confirm":
            item_id = parts[2]
            await _confirm_purchase(query, user_info, item_id, gamification_service)
        
        elif action == "back_to_category":
            category = parts[2]
            page = int(parts[3])
            await _show_category_items(query, user_info, category, page)
        
        await query.answer()
        
    except Exception as e:
        logger.error(f"Error en shop callback para usuario {user_id}: {e}")
        await query.answer("❌ Error al procesar la solicitud.")

async def _show_category_items(query: types.CallbackQuery, user_info: dict, category: str, page: int):
    """
    Muestra los items de una categoría específica.
    
    Args:
        query: Query del callback.
        user_info: Información del usuario.
        category: Categoría a mostrar.
        page: Página actual.
    """
    if category not in SHOP_CATEGORIES:
        await query.answer("❌ Categoría no encontrada.")
        return
    
    category_info = SHOP_CATEGORIES[category]
    available_items = get_items_by_category(category, user_info["level"])
    
    # Calcular paginación
    total_items = len(available_items)
    total_pages = (total_items + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    
    if page >= total_pages:
        page = 0
    
    start_idx = page * ITEMS_PER_PAGE
    end_idx = min(start_idx + ITEMS_PER_PAGE, total_items)
    page_items = available_items[start_idx:end_idx]
    
    # Crear texto del mensaje
    text = f"{category_info['emoji']} **{category_info['name']}**\n\n"
    text += f"_{category_info['description']}_\n\n"
    text += f"💰 Tienes **{user_info['current_points']:.0f} besitos**\n"
    text += f"📦 Items disponibles: {total_items}\n\n"
    
    if not page_items:
        text += "😔 No hay items disponibles para tu nivel actual.\n"
        text += "¡Sube de nivel para desbloquear más contenido!"
    else:
        text += "**Items disponibles:**\n\n"
        
        for i, item in enumerate(page_items, 1):
            rarity_info = RARITY_CONFIG.get(item["rarity"], RARITY_CONFIG["common"])
            price = calculate_final_price(item)
            
            text += f"{i}. {rarity_info['emoji']} **{item['name']}**\n"
            text += f"   💰 {price} besitos"
            
            if item.get("discount", 0) > 0:
                text += f" (-{item['discount']}%)"
            
            text += f" | 🎯 Nivel {item.get('level_required', 1)}\n"
            text += f"   _{item['description'][:50]}{'...' if len(item['description']) > 50 else ''}_\n\n"
    
    # Agregar información de paginación
    if total_pages > 1:
        text += f"📄 Página {page + 1} de {total_pages}"
    
    # Crear keyboard
    keyboard = InlineKeyboardBuilder()
    
    # Botones de items
    for item in page_items:
        price = calculate_final_price(item)
        rarity_emoji = RARITY_CONFIG.get(item["rarity"], RARITY_CONFIG["common"])["emoji"]
        button_text = f"{rarity_emoji} {item['name']} ({price} 💰)"
        keyboard.button(
            text=button_text,
            callback_data=f"shop:item:{item['id']}"
        )
    
    # Botones de navegación
    nav_row = []
    if total_pages > 1:
        if page > 0:
            nav_row.append({
                "text": "⬅️ Anterior",
                "callback_data": f"shop:category:{category}:{page-1}"
            })
        
        if page < total_pages - 1:
            nav_row.append({
                "text": "Siguiente ➡️",
                "callback_data": f"shop:category:{category}:{page+1}"
            })
    
    # Botón para volver
    keyboard.button(text="⬅️ Volver a Categorías", callback_data="shop:main")
    
    # Ajustar layout del keyboard
    keyboard.adjust(1)  # Un botón por fila para items
    if nav_row:
        for nav_button in nav_row:
            keyboard.button(text=nav_button["text"], callback_data=nav_button["callback_data"])
        keyboard.adjust(*([1] * len(page_items) + [len(nav_row)] + [1]))
    else:
        keyboard.adjust(*([1] * len(page_items) + [1]))
    
    await query.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboard.as_markup()
    )

async def _show_item_details(query: types.CallbackQuery, user_info: dict, item_id: str):
    """
    Muestra los detalles completos de un item.
    
    Args:
        query: Query del callback.
        user_info: Información del usuario.
        item_id: ID del item a mostrar.
    """
    item = get_item_by_id(item_id)
    if not item:
        await query.answer("❌ Item no encontrado.")
        return
    
    # Verificar si el usuario puede acceder al item
    if item.get("level_required", 1) > user_info["level"]:
        await query.answer(f"❌ Necesitas nivel {item['level_required']} para este item.")
        return
    
    # Formatear descripción completa
    text = format_item_description(item)
    text += f"\n💰 Tienes **{user_info['current_points']:.0f} besitos**\n"
    
    price = calculate_final_price(item)
    can_afford = user_info["current_points"] >= price
    
    if not can_afford:
        needed = price - user_info["current_points"]
        text += f"❌ Te faltan **{needed:.0f} besitos** para comprarlo\n"
    
    # Crear keyboard
    keyboard = InlineKeyboardBuilder()
    
    if can_afford:
        keyboard.button(
            text=f"💳 Comprar por {price} besitos",
            callback_data=f"shop:buy:{item_id}"
        )
    else:
        keyboard.button(
            text="💔 No tienes suficientes besitos",
            callback_data=f"shop:insufficient:{item_id}"
        )
    
    # Botones adicionales
    keyboard.button(text="🎁 Obtener más besitos", callback_data="main_menu:daily_reward")
    keyboard.button(text="🎯 Ver Misiones", callback_data="main_menu:missions")
    
    # Botón para volver
    keyboard.button(
        text="⬅️ Volver a Categoría",
        callback_data=f"shop:category:{item['category']}:0"
    )
    
    keyboard.adjust(1, 2, 1)
    
    await query.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboard.as_markup()
    )

async def _process_purchase(query: types.CallbackQuery, user_info: dict, item_id: str, gamification_service: GamificationService):
    """
    Procesa la compra de un item (confirmación).
    
    Args:
        query: Query del callback.
        user_info: Información del usuario.
        item_id: ID del item a comprar.
        gamification_service: Servicio de gamificación.
    """
    item = get_item_by_id(item_id)
    if not item:
        await query.answer("❌ Item no encontrado.")
        return
    
    price = calculate_final_price(item)
    
    # Verificar fondos nuevamente
    current_user_info = await _get_user_info(user_info["user_id"])
    if current_user_info["current_points"] < price:
        await query.answer("❌ No tienes suficientes besitos.")
        return
    
    # Mostrar confirmación
    rarity_info = RARITY_CONFIG.get(item["rarity"], RARITY_CONFIG["common"])
    
    text = (
        f"🛒 **Confirmar Compra**\n\n"
        f"{rarity_info['emoji']} **{item['name']}**\n"
        f"💰 Precio: **{price} besitos**\n\n"
        f"Tu saldo actual: **{current_user_info['current_points']:.0f} besitos**\n"
        f"Saldo después de compra: **{current_user_info['current_points'] - price:.0f} besitos**\n\n"
        "⚠️ **¿Estás seguro de que quieres comprar este item?**"
    )
    
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="✅ Confirmar Compra", callback_data=f"shop:confirm:{item_id}")
    keyboard.button(text="❌ Cancelar", callback_data=f"shop:item:{item_id}")
    keyboard.adjust(1, 1)
    
    await query.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboard.as_markup()
    )

async def _confirm_purchase(query: types.CallbackQuery, user_info: dict, item_id: str, gamification_service: GamificationService):
    """
    Confirma y ejecuta la compra de un item.
    
    Args:
        query: Query del callback.
        user_info: Información del usuario.
        item_id: ID del item a comprar.
        gamification_service: Servicio de gamificación.
    """
    item = get_item_by_id(item_id)
    if not item:
        await query.answer("❌ Item no encontrado.")
        return
    
    price = calculate_final_price(item)
    user_id = user_info["user_id"]
    
    try:
        async for session in get_session():
            # Verificar fondos una vez más
            points_query = select(UserPoints).where(UserPoints.user_id == user_id)
            points_result = await session.execute(points_query)
            user_points = points_result.scalars().first()
            
            if not user_points or user_points.current_points < price:
                await query.answer("❌ No tienes suficientes besitos.")
                return
            
            # Realizar la compra
            user_points.current_points -= price
            user_points.total_spent += price
            
            # Agregar al historial
            purchase_entry = {
                "timestamp": datetime.now().isoformat(),
                "amount": -price,
                "source": f"ShopPurchase_{item['type']}",
                "item_id": item_id,
                "item_name": item["name"],
                "balance": user_points.current_points
            }
            user_points.points_history.append(purchase_entry)
            
            await session.commit()
            
            # Mostrar mensaje de éxito
            await _show_purchase_success(query, item, price, user_points.current_points)
            
    except Exception as e:
        logger.error(f"Error al confirmar compra para usuario {user_id}: {e}")
        await query.answer("❌ Error al procesar la compra.")

async def _show_purchase_success(query: types.CallbackQuery, item: dict, price: int, remaining_points: float):
    """
    Muestra mensaje de compra exitosa.
    
    Args:
        query: Query del callback.
        item: Item comprado.
        price: Precio pagado.
        remaining_points: Puntos restantes.
    """
    rarity_info = RARITY_CONFIG.get(item["rarity"], RARITY_CONFIG["common"])
    
    text = (
        f"🎉 **¡Compra Exitosa!** 🎉\n\n"
        f"{rarity_info['emoji']} **{item['name']}** adquirido\n\n"
        f"💸 Gastaste: **{price} besitos**\n"
        f"💰 Saldo restante: **{remaining_points:.0f} besitos**\n\n"
    )
    
    # Mensaje especial según el tipo de item
    if item["type"] == "media":
        text += "📸 **Tu contenido exclusivo estará disponible en tu perfil**\n"
    elif item["type"] == "badge":
        text += "🏅 **Tu nuevo badge aparecerá en tu perfil**\n"
    elif item["type"] == "title":
        text += "👑 **Tu nuevo título ya está activo**\n"
    elif item["type"] == "multiplier":
        text += f"⚡ **Tu multiplicador x{item.get('multiplier', 2)} ya está activo**\n"
    elif item["type"] == "narrative_fragment":
        text += "📖 **El fragmento narrativo se ha desbloqueado**\n"
    
    text += "\n¡Gracias por tu compra! ¿Qué te gustaría hacer ahora?"
    
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="🛍️ Seguir Comprando", callback_data="shop:main")
    keyboard.button(text="🏆 Ver Mi Perfil", callback_data="main_menu:profile")
    keyboard.button(text="🎁 Obtener Más Besitos", callback_data="main_menu:daily_reward")
    keyboard.button(text="⬅️ Menú Principal", callback_data="main_menu")
    keyboard.adjust(1, 2, 1)
    
    await query.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboard.as_markup()
    )

def register_shop_handler(dp, gamification_service):
    """Registra los handlers de la tienda en el dispatcher."""
    # Comando /tienda
    dp.message.register(
        lambda message: handle_shop_main(message, gamification_service),
        Command("tienda")
    )
    
    # Callbacks de la tienda
    dp.callback_query.register(
        lambda query: handle_shop_callback(query, gamification_service),
        lambda c: c.data.startswith("shop:")
    )