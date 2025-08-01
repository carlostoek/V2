"""Handlers para la tienda de besitos."""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from typing import List

from ...keyboards.keyboard_factory import KeyboardFactory
from src.modules.shop.service import ShopService, ShopItem

shop_router = Router()

@shop_router.message(Command("tienda"))
async def cmd_shop(message: Message, shop_service: ShopService):
    """Comando principal de la tienda."""
    user_id = message.from_user.id
    
    # Obtener estadísticas del usuario
    user_stats = await shop_service.gamification_service.get_user_stats(user_id)
    user_points = user_stats.get('total_points', 0)
    user_level = user_stats.get('level', 0)
    
    # Obtener categorías disponibles
    categories = await shop_service.get_categories()
    
    text = (
        "🛍️ **Tienda de Besitos**\n\n"
        f"💋 **Tus besitos:** {user_points}\n"
        f"⭐ **Nivel:** {user_level}\n\n"
        "Intercambia tus besitos por artículos especiales, "
        "pistas narrativas, potenciadores y mucho más.\n\n"
        "**Categorías disponibles:**"
    )
    
    await message.answer(
        text,
        parse_mode="Markdown",
        reply_markup=get_shop_main_keyboard(categories)
    )

@shop_router.callback_query(F.data == "shop:main")
async def shop_main_callback(callback: CallbackQuery, shop_service: ShopService):
    """Volver al menú principal de la tienda."""
    user_id = callback.from_user.id
    
    # Obtener estadísticas del usuario
    user_stats = await shop_service.gamification_service.get_user_stats(user_id)
    user_points = user_stats.get('total_points', 0)
    user_level = user_stats.get('level', 0)
    
    # Obtener categorías disponibles
    categories = await shop_service.get_categories()
    
    text = (
        "🛍️ **Tienda de Besitos**\n\n"
        f"💋 **Tus besitos:** {user_points}\n"
        f"⭐ **Nivel:** {user_level}\n\n"
        "Intercambia tus besitos por artículos especiales, "
        "pistas narrativas, potenciadores y mucho más.\n\n"
        "**Categorías disponibles:**"
    )
    
    await callback.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=get_shop_main_keyboard(categories)
    )
    await callback.answer()

@shop_router.callback_query(F.data.startswith("shop:category:"))
async def shop_category_callback(callback: CallbackQuery, shop_service: ShopService):
    """Mostrar artículos de una categoría específica."""
    category = callback.data.split(":")[2]
    user_id = callback.from_user.id
    
    # Obtener artículos de la categoría
    items = await shop_service.get_shop_items(user_id, category=category)
    
    if not items:
        text = (
            f"🛍️ **Categoría: {category.title()}**\n\n"
            "No hay artículos disponibles en esta categoría en este momento.\n"
            "¡Vuelve pronto para ver nuevos productos!"
        )
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Volver", callback_data="shop:main")]
        ])
    else:
        text = f"🛍️ **Categoría: {category.title()}**\n\n"
        
        # Agregar información de usuario
        user_stats = await shop_service.gamification_service.get_user_stats(user_id)
        user_points = user_stats.get('total_points', 0)
        text += f"💋 **Tus besitos:** {user_points}\n\n"
        
        keyboard = get_category_items_keyboard(items, category)
    
    await callback.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    await callback.answer()

@shop_router.callback_query(F.data.startswith("shop:item:"))
async def shop_item_callback(callback: CallbackQuery, shop_service: ShopService):
    """Mostrar detalles de un artículo específico."""
    item_id = callback.data.split(":")[2]
    user_id = callback.from_user.id
    
    # Obtener el artículo
    item = await shop_service.get_item_by_id(item_id)
    if not item:
        await callback.answer("Artículo no encontrado", show_alert=True)
        return
    
    # Verificar si puede comprar
    validation = await shop_service.can_purchase(user_id, item_id)
    
    # Obtener stats del usuario
    user_stats = await shop_service.gamification_service.get_user_stats(user_id)
    user_points = user_stats.get('total_points', 0)
    user_level = user_stats.get('level', 0)
    is_vip = user_stats.get('is_vip', False)
    
    text = (
        f"{item.icon} **{item.name}**\n\n"
        f"{item.description}\n\n"
        f"💰 **Precio:** {item.price} besitos\n"
        f"📂 **Categoría:** {item.category.title()}\n"
    )
    
    # Agregar requisitos si los hay
    if item.level_required > 0:
        status_icon = "✅" if user_level >= item.level_required else "❌"
        text += f"⭐ **Nivel requerido:** {item.level_required} {status_icon}\n"
    
    if item.vip_only:
        status_icon = "✅" if is_vip else "❌"
        text += f"👑 **Solo VIP:** Sí {status_icon}\n"
    
    if item.stock is not None:
        text += f"📦 **Stock:** {item.stock} unidades\n"
    
    if item.purchase_limit:
        text += f"🔄 **Límite:** {item.purchase_limit} por día\n"
    
    text += f"\n💋 **Tus besitos:** {user_points}"
    
    # Crear teclado según disponibilidad
    keyboard_buttons = []
    
    if validation["can_purchase"]:
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=f"💳 Comprar por {item.price} besitos",
                callback_data=f"shop:buy:{item_id}"
            )
        ])
    else:
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=f"❌ {validation['reason']}",
                callback_data="shop:cannot_buy"
            )
        ])
    
    keyboard_buttons.extend([
        [InlineKeyboardButton(text="🔙 Volver a Categoría", callback_data=f"shop:category:{item.category}")],
        [InlineKeyboardButton(text="🏠 Menú Principal", callback_data="shop:main")]
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await callback.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    await callback.answer()

@shop_router.callback_query(F.data.startswith("shop:buy:"))
async def shop_buy_callback(callback: CallbackQuery, shop_service: ShopService):
    """Procesar la compra de un artículo."""
    item_id = callback.data.split(":")[2]
    user_id = callback.from_user.id
    
    # Realizar la compra
    result = await shop_service.purchase_item(user_id, item_id)
    
    if result["success"]:
        item = result["item"]
        effects = result["effect"]["effects"]
        remaining_points = result["remaining_points"]
        
        text = (
            "✅ **¡Compra Exitosa!**\n\n"
            f"{item.icon} **{item.name}** adquirido\n\n"
            "**Efectos recibidos:**\n"
        )
        
        for effect in effects:
            text += f"• {effect}\n"
        
        text += f"\n💋 **Besitos restantes:** {remaining_points}"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛍️ Seguir Comprando", callback_data="shop:main")],
            [InlineKeyboardButton(text="📊 Ver Perfil", callback_data="profile:main")]
        ])
        
        await callback.answer("¡Compra realizada! 🎉", show_alert=True)
        
    else:
        text = (
            "❌ **Error en la Compra**\n\n"
            f"No se pudo completar la compra:\n{result['reason']}\n\n"
            "Intenta nuevamente o contacta soporte."
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Intentar de Nuevo", callback_data=f"shop:item:{item_id}")],
            [InlineKeyboardButton(text="🏠 Volver al Menú", callback_data="shop:main")]
        ])
        
        await callback.answer(f"Error: {result['reason']}", show_alert=True)
    
    await callback.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )

@shop_router.callback_query(F.data == "shop:cannot_buy")
async def shop_cannot_buy_callback(callback: CallbackQuery):
    """Callback para cuando no se puede comprar."""
    await callback.answer("No puedes comprar este artículo en este momento", show_alert=True)

@shop_router.callback_query(F.data == "shop:vip_only")
async def shop_vip_only_callback(callback: CallbackQuery, shop_service: ShopService):
    """Mostrar solo artículos VIP."""
    user_id = callback.from_user.id
    
    # Obtener artículos VIP
    items = await shop_service.get_shop_items(user_id, vip_only=True)
    
    user_stats = await shop_service.gamification_service.get_user_stats(user_id)
    user_points = user_stats.get('total_points', 0)
    is_vip = user_stats.get('is_vip', False)
    
    text = (
        "👑 **Artículos VIP Exclusivos**\n\n"
        f"💋 **Tus besitos:** {user_points}\n\n"
    )
    
    if not is_vip:
        text += (
            "❌ **Necesitas acceso VIP**\n\n"
            "Para acceder a estos artículos exclusivos, "
            "necesitas ser usuario VIP.\n\n"
            "¡Hazte VIP y desbloquea contenido especial!"
        )
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👑 Información VIP", callback_data="vip:info")],
            [InlineKeyboardButton(text="🔙 Volver", callback_data="shop:main")]
        ])
    elif not items:
        text += "No hay artículos VIP disponibles en este momento."
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Volver", callback_data="shop:main")]
        ])
    else:
        text += "Artículos exclusivos para usuarios VIP:"
        keyboard = get_vip_items_keyboard(items)
    
    await callback.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    await callback.answer()

# =============================================================================
# FUNCIONES AUXILIARES PARA TECLADOS
# =============================================================================

def get_shop_main_keyboard(categories: List[str]) -> InlineKeyboardMarkup:
    """Crear teclado principal de la tienda."""
    buttons = []
    
    # Botones de categorías
    category_icons = {
        "narrativa": "📖",
        "gamificacion": "🎮", 
        "vip": "👑",
        "especiales": "✨"
    }
    
    for category in categories:
        icon = category_icons.get(category, "📦")
        buttons.append([
            InlineKeyboardButton(
                text=f"{icon} {category.title()}",
                callback_data=f"shop:category:{category}"
            )
        ])
    
    # Botones especiales
    buttons.extend([
        [InlineKeyboardButton(text="👑 Solo VIP", callback_data="shop:vip_only")],
        [InlineKeyboardButton(text="📊 Mis Compras", callback_data="shop:history")],
        [InlineKeyboardButton(text="🔙 Volver", callback_data="main_menu")]
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_category_items_keyboard(items: List[ShopItem], category: str) -> InlineKeyboardMarkup:
    """Crear teclado para artículos de una categoría."""
    buttons = []
    
    for item in items[:10]:  # Máximo 10 artículos por página
        price_text = f"💋{item.price}"
        if item.vip_only:
            price_text += " 👑"
        if item.stock is not None and item.stock <= 5:
            price_text += f" (Stock: {item.stock})"
            
        buttons.append([
            InlineKeyboardButton(
                text=f"{item.icon} {item.name} - {price_text}",
                callback_data=f"shop:item:{item.id}"
            )
        ])
    
    # Botones de navegación
    buttons.extend([
        [InlineKeyboardButton(text="🔙 Volver", callback_data="shop:main")]
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_vip_items_keyboard(items: List[ShopItem]) -> InlineKeyboardMarkup:
    """Crear teclado para artículos VIP."""
    buttons = []
    
    for item in items:
        buttons.append([
            InlineKeyboardButton(
                text=f"{item.icon} {item.name} - 💋{item.price}",
                callback_data=f"shop:item:{item.id}"
            )
        ])
    
    buttons.append([
        InlineKeyboardButton(text="🔙 Volver", callback_data="shop:main")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def register_shop_handlers(dp, shop_service: ShopService):
    """Registra los handlers de la tienda."""
    shop_router.message.register(
        lambda message: cmd_shop(message, shop_service),
        Command("tienda")
    )
    
    dp.include_router(shop_router)