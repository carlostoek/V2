"""
Keyboards específicos para el sistema de tienda.
Maneja la navegación por categorías, items y procesos de compra.
"""

from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Dict, Any

class ShopKeyboard:
    """
    Keyboards especializados para el sistema de tienda de gamificación.
    """
    
    @staticmethod
    def main_categories(categories: Dict[str, Dict], user_level: int = 1) -> types.InlineKeyboardMarkup:
        """
        Crea keyboard con las categorías principales de la tienda.
        
        Args:
            categories: Diccionario con información de categorías.
            user_level: Nivel del usuario para filtrar contenido.
            
        Returns:
            Keyboard con categorías disponibles.
        """
        keyboard = InlineKeyboardBuilder()
        
        # Ordenar categorías por orden
        sorted_categories = sorted(categories.items(), key=lambda x: x[1]["order"])
        
        for category_key, category_info in sorted_categories:
            # Agregar emoji y contador si está disponible
            button_text = f"{category_info['emoji']} {category_info['name'].split(' ', 1)[1]}"
            keyboard.button(
                text=button_text,
                callback_data=f"shop:category:{category_key}:0"
            )
        
        # Botones adicionales
        keyboard.button(text="🔥 Ofertas Especiales", callback_data="shop:deals")
        keyboard.button(text="📦 Mis Compras", callback_data="shop:purchases")
        keyboard.button(text="⬅️ Menú Principal", callback_data="main_menu")
        
        keyboard.adjust(1, 1, 1, 1, 1, 2)
        return keyboard.as_markup()
    
    @staticmethod
    def category_items(items: List[Dict], category: str, current_page: int = 0, total_pages: int = 1) -> types.InlineKeyboardMarkup:
        """
        Crea keyboard para items de una categoría específica.
        
        Args:
            items: Lista de items a mostrar.
            category: Categoría actual.
            current_page: Página actual.
            total_pages: Total de páginas.
            
        Returns:
            Keyboard con items y navegación.
        """
        keyboard = InlineKeyboardBuilder()
        
        # Botones de items
        for item in items:
            price = item.get("price", 0)
            rarity_emoji = ShopKeyboard._get_rarity_emoji(item.get("rarity", "common"))
            
            # Indicar si hay descuento
            discount_text = ""
            if item.get("discount", 0) > 0:
                discount_text = f" (-{item['discount']}%)"
            
            button_text = f"{rarity_emoji} {item['name']} ({price}💰{discount_text})"
            
            keyboard.button(
                text=button_text,
                callback_data=f"shop:item:{item['id']}"
            )
        
        # Navegación de páginas si es necesaria
        if total_pages > 1:
            nav_buttons = []
            
            if current_page > 0:
                nav_buttons.append({
                    "text": "⬅️ Anterior",
                    "callback_data": f"shop:category:{category}:{current_page-1}"
                })
            
            nav_buttons.append({
                "text": f"📄 {current_page+1}/{total_pages}",
                "callback_data": f"shop:page_info:{category}:{current_page}"
            })
            
            if current_page < total_pages - 1:
                nav_buttons.append({
                    "text": "Siguiente ➡️",
                    "callback_data": f"shop:category:{category}:{current_page+1}"
                })
            
            # Agregar botones de navegación
            for nav_button in nav_buttons:
                keyboard.button(
                    text=nav_button["text"],
                    callback_data=nav_button["callback_data"]
                )
        
        # Botón para volver
        keyboard.button(text="⬅️ Volver a Categorías", callback_data="shop:main")
        
        # Ajustar layout
        items_per_row = 1
        nav_buttons_count = len(nav_buttons) if total_pages > 1 else 0
        
        layout = [items_per_row] * len(items)
        if nav_buttons_count > 0:
            layout.extend([nav_buttons_count])
        layout.append(1)  # Botón volver
        
        keyboard.adjust(*layout)
        return keyboard.as_markup()
    
    @staticmethod
    def item_details(item: Dict[str, Any], user_points: float, can_afford: bool = True) -> types.InlineKeyboardMarkup:
        """
        Crea keyboard para detalles de un item específico.
        
        Args:
            item: Información del item.
            user_points: Puntos actuales del usuario.
            can_afford: Si el usuario puede permitirse el item.
            
        Returns:
            Keyboard con opciones para el item.
        """
        keyboard = InlineKeyboardBuilder()
        
        price = item.get("price", 0)
        
        # Botón principal de compra
        if can_afford:
            keyboard.button(
                text=f"💳 Comprar por {price} besitos",
                callback_data=f"shop:buy:{item['id']}"
            )
        else:
            needed = price - user_points
            keyboard.button(
                text=f"💔 Te faltan {needed:.0f} besitos",
                callback_data=f"shop:insufficient:{item['id']}"
            )
        
        # Opciones adicionales
        if not can_afford:
            keyboard.button(text="🎁 Obtener Besitos", callback_data="gamification:daily_reward")
            keyboard.button(text="🎯 Ver Misiones", callback_data="main_menu:missions")
        else:
            keyboard.button(text="❤️ Agregar a Favoritos", callback_data=f"shop:favorite:{item['id']}")
            keyboard.button(text="👀 Vista Previa", callback_data=f"shop:preview:{item['id']}")
        
        # Navegación
        keyboard.button(
            text="⬅️ Volver a Categoría",
            callback_data=f"shop:category:{item.get('category', 'especial')}:0"
        )
        
        # Ajustar layout
        if can_afford:
            keyboard.adjust(1, 2, 1)
        else:
            keyboard.adjust(1, 2, 1)
        
        return keyboard.as_markup()
    
    @staticmethod
    def purchase_confirmation(item: Dict[str, Any], final_price: int, user_points: float) -> types.InlineKeyboardMarkup:
        """
        Crea keyboard de confirmación de compra.
        
        Args:
            item: Item a comprar.
            final_price: Precio final con descuentos.
            user_points: Puntos actuales del usuario.
            
        Returns:
            Keyboard de confirmación.
        """
        keyboard = InlineKeyboardBuilder()
        
        keyboard.button(text="✅ Confirmar Compra", callback_data=f"shop:confirm:{item['id']}")
        keyboard.button(text="❌ Cancelar", callback_data=f"shop:item:{item['id']}")
        
        # Opciones adicionales si no está seguro
        keyboard.button(text="👀 Ver Detalles de Nuevo", callback_data=f"shop:item:{item['id']}")
        keyboard.button(text="🛍️ Seguir Viendo", callback_data=f"shop:category:{item.get('category', 'especial')}:0")
        
        keyboard.adjust(2, 2)
        return keyboard.as_markup()
    
    @staticmethod
    def purchase_success(item: Dict[str, Any], points_spent: int, remaining_points: float) -> types.InlineKeyboardMarkup:
        """
        Crea keyboard para después de una compra exitosa.
        
        Args:
            item: Item comprado.
            points_spent: Puntos gastados.
            remaining_points: Puntos restantes.
            
        Returns:
            Keyboard post-compra.
        """
        keyboard = InlineKeyboardBuilder()
        
        # Acciones principales
        keyboard.button(text="🛍️ Seguir Comprando", callback_data="shop:main")
        keyboard.button(text="🏆 Ver Mi Perfil", callback_data="main_menu:profile")
        
        # Sugerencias basadas en el tipo de item
        item_type = item.get("type", "")
        
        if item_type == "multiplier":
            keyboard.button(text="🎯 Usar en Misiones", callback_data="main_menu:missions")
            keyboard.button(text="🧠 Usar en Trivia", callback_data="trivia:main")
        elif item_type == "media":
            keyboard.button(text="📱 Ver Mi Colección", callback_data="shop:my_media")
        elif item_type == "badge":
            keyboard.button(text="🏅 Ver Mis Badges", callback_data="gamification:achievements")
        
        # Navegación
        keyboard.button(text="⬅️ Menú Principal", callback_data="main_menu")
        
        # Ajustar layout dinámicamente
        base_buttons = 2
        suggestion_buttons = 1 if item_type in ["multiplier"] else 1 if item_type in ["media", "badge"] else 0
        
        if suggestion_buttons == 1:
            keyboard.adjust(2, 1, 1)
        elif suggestion_buttons == 2:
            keyboard.adjust(2, 2, 1)
        else:
            keyboard.adjust(2, 1)
        
        return keyboard.as_markup()
    
    @staticmethod
    def deals_menu(deals: List[Dict[str, Any]]) -> types.InlineKeyboardMarkup:
        """
        Crea keyboard para ofertas especiales.
        
        Args:
            deals: Lista de ofertas disponibles.
            
        Returns:
            Keyboard con ofertas.
        """
        keyboard = InlineKeyboardBuilder()
        
        for deal in deals:
            discount_text = f"-{deal.get('discount', 0)}%"
            keyboard.button(
                text=f"🔥 {deal['name']} ({discount_text})",
                callback_data=f"shop:deal:{deal['id']}"
            )
        
        # Si no hay ofertas
        if not deals:
            keyboard.button(text="😔 No hay ofertas disponibles", callback_data="shop:no_deals")
        
        keyboard.button(text="🔄 Actualizar Ofertas", callback_data="shop:refresh_deals")
        keyboard.button(text="⬅️ Volver a Tienda", callback_data="shop:main")
        
        keyboard.adjust(1)
        return keyboard.as_markup()
    
    @staticmethod
    def my_purchases(purchases: List[Dict[str, Any]]) -> types.InlineKeyboardMarkup:
        """
        Crea keyboard para ver compras del usuario.
        
        Args:
            purchases: Lista de compras del usuario.
            
        Returns:
            Keyboard con historial de compras.
        """
        keyboard = InlineKeyboardBuilder()
        
        # Mostrar últimas compras
        for purchase in purchases[:10]:  # Máximo 10 más recientes
            purchase_date = purchase.get("date", "")
            keyboard.button(
                text=f"📦 {purchase['item_name']} ({purchase_date})",
                callback_data=f"shop:purchase_details:{purchase['id']}"
            )
        
        if not purchases:
            keyboard.button(text="🛒 ¡Haz tu primera compra!", callback_data="shop:main")
        
        # Opciones adicionales
        keyboard.button(text="📊 Estadísticas de Gastos", callback_data="shop:spending_stats")
        keyboard.button(text="⬅️ Volver a Tienda", callback_data="shop:main")
        
        keyboard.adjust(1)
        return keyboard.as_markup()
    
    @staticmethod
    def filter_options(category: str, current_filters: Dict[str, Any] = None) -> types.InlineKeyboardMarkup:
        """
        Crea keyboard para filtros de búsqueda en tienda.
        
        Args:
            category: Categoría actual.
            current_filters: Filtros activos.
            
        Returns:
            Keyboard con opciones de filtro.
        """
        keyboard = InlineKeyboardBuilder()
        current_filters = current_filters or {}
        
        # Filtros por rareza
        keyboard.button(text="⚪ Común", callback_data=f"shop:filter:{category}:rarity:common")
        keyboard.button(text="💎 Raro", callback_data=f"shop:filter:{category}:rarity:rare")
        keyboard.button(text="✨ Épico", callback_data=f"shop:filter:{category}:rarity:epic")
        keyboard.button(text="👑 Legendario", callback_data=f"shop:filter:{category}:rarity:legendary")
        
        # Filtros por precio
        keyboard.button(text="💰 Baratos (0-50)", callback_data=f"shop:filter:{category}:price:cheap")
        keyboard.button(text="💰 Medios (51-150)", callback_data=f"shop:filter:{category}:price:medium")
        keyboard.button(text="💰 Caros (151+)", callback_data=f"shop:filter:{category}:price:expensive")
        
        # Limpiar filtros y volver
        keyboard.button(text="🔄 Limpiar Filtros", callback_data=f"shop:clear_filters:{category}")
        keyboard.button(text="⬅️ Volver", callback_data=f"shop:category:{category}:0")
        
        keyboard.adjust(2, 2, 3, 2)
        return keyboard.as_markup()
    
    @staticmethod
    def _get_rarity_emoji(rarity: str) -> str:
        """
        Obtiene el emoji correspondiente a una rareza.
        
        Args:
            rarity: Nivel de rareza.
            
        Returns:
            Emoji representativo.
        """
        rarity_emojis = {
            "common": "⚪",
            "rare": "💎", 
            "epic": "✨",
            "legendary": "👑",
            "mythic": "⭐"
        }
        return rarity_emojis.get(rarity, "⚪")