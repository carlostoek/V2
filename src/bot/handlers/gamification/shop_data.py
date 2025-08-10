"""
Datos de ejemplo para el sistema de tienda de gamificación.
Incluye las 4 categorías obligatorias con items variados.
"""

# Configuración de la tienda con 4 categorías obligatorias
SHOP_CATEGORIES = {
    "especial": {
        "name": "💋 Contenido Especial",
        "description": "Fotos y videos exclusivos de Diana",
        "emoji": "💋",
        "order": 1
    },
    "recompensas": {
        "name": "🎁 Recompensas Virtuales",
        "description": "Badges, títulos y reconocimientos",
        "emoji": "🎁",
        "order": 2
    },
    "narrativa": {
        "name": "🔓 Desbloqueos Narrativos",
        "description": "Fragmentos VIP y pistas exclusivas",
        "emoji": "🔓",
        "order": 3
    },
    "beneficios": {
        "name": "⭐ Beneficios Temporales",
        "description": "Multiplicadores y ventajas especiales",
        "emoji": "⭐",
        "order": 4
    }
}

# Items disponibles por categoría
SHOP_ITEMS = {
    "especial": [
        {
            "id": "foto_exclusiva_1",
            "name": "Foto Exclusiva #1",
            "description": "Una foto sensual y misteriosa de Diana en ambiente íntimo",
            "price": 50,
            "type": "media",
            "rarity": "rare",
            "preview": "📸 Vista previa disponible",
            "level_required": 1
        },
        {
            "id": "video_personal_1",
            "name": "Video Personal de Diana",
            "description": "Un video personal donde Diana comparte pensamientos íntimos",
            "price": 120,
            "type": "media",
            "rarity": "epic",
            "preview": "🎥 30 segundos de contenido premium",
            "level_required": 3
        },
        {
            "id": "foto_exclusiva_2",
            "name": "Sesión Fotográfica Privada",
            "description": "Colección de 5 fotos de una sesión privada de Diana",
            "price": 200,
            "type": "media_bundle",
            "rarity": "legendary",
            "preview": "📷 5 fotos en alta calidad",
            "level_required": 5
        },
        {
            "id": "audio_susurro",
            "name": "Susurros de Diana",
            "description": "Audio íntimo con la voz seductora de Diana",
            "price": 80,
            "type": "audio",
            "rarity": "rare",
            "preview": "🔊 Audio de 2 minutos",
            "level_required": 2
        },
        {
            "id": "coleccion_completa",
            "name": "Colección Completa Premium",
            "description": "Todo el contenido especial disponible hasta la fecha",
            "price": 500,
            "type": "bundle",
            "rarity": "mythic",
            "preview": "🎊 +20 items premium",
            "level_required": 10,
            "discount": 30  # 30% descuento
        }
    ],
    
    "recompensas": [
        {
            "id": "badge_vip",
            "name": "Badge VIP Dorado",
            "description": "Un distintivo dorado que muestra tu estatus VIP",
            "price": 30,
            "type": "badge",
            "rarity": "common",
            "effect": "Título visible en el perfil",
            "level_required": 1
        },
        {
            "id": "titulo_conquistador",
            "name": "Título: Conquistador",
            "description": "Título especial que aparece junto a tu nombre",
            "price": 45,
            "type": "title",
            "rarity": "rare",
            "effect": "Aparece como 'Conquistador [Nombre]'",
            "level_required": 2
        },
        {
            "id": "marco_perfil_diamante",
            "name": "Marco de Perfil Diamante",
            "description": "Marco brillante para destacar tu perfil",
            "price": 75,
            "type": "cosmetic",
            "rarity": "epic",
            "effect": "Marco visual en tu perfil",
            "level_required": 4
        },
        {
            "id": "titulo_leyenda",
            "name": "Título: Leyenda de Diana",
            "description": "El título más prestigioso disponible",
            "price": 150,
            "type": "title",
            "rarity": "legendary",
            "effect": "Título especial con efectos visuales",
            "level_required": 7
        },
        {
            "id": "coleccion_badges",
            "name": "Colección de Badges Temáticos",
            "description": "Set de 10 badges con diferentes temas",
            "price": 100,
            "type": "badge_bundle",
            "rarity": "epic",
            "effect": "10 badges únicos para coleccionar",
            "level_required": 5
        }
    ],
    
    "narrativa": [
        {
            "id": "fragmento_vip_1",
            "name": "Fragmento VIP: 'El Encuentro'",
            "description": "Escena exclusiva entre Diana y el protagonista",
            "price": 60,
            "type": "narrative_fragment",
            "rarity": "rare",
            "content": "Fragmento narrativo de 500+ palabras",
            "level_required": 3
        },
        {
            "id": "pista_misteriosa_1",
            "name": "Pista Misteriosa: 'La Llave'",
            "description": "Una pista crucial para entender el misterio de Diana",
            "price": 40,
            "type": "clue",
            "rarity": "common",
            "content": "Pista que desbloquea nueva rama narrativa",
            "level_required": 2
        },
        {
            "id": "final_alternativo",
            "name": "Final Alternativo Secreto",
            "description": "Un final completamente diferente para la historia",
            "price": 250,
            "type": "narrative_ending",
            "rarity": "mythic",
            "content": "Final exclusivo de 1000+ palabras",
            "level_required": 8
        },
        {
            "id": "backstory_diana",
            "name": "Historia Personal de Diana",
            "description": "Los secretos del pasado de Diana revelados",
            "price": 90,
            "type": "backstory",
            "rarity": "epic",
            "content": "Capítulo especial sobre Diana",
            "level_required": 4
        },
        {
            "id": "dialogo_intimo",
            "name": "Diálogos Íntimos Exclusivos",
            "description": "Conversaciones profundas y personales con Diana",
            "price": 70,
            "type": "dialogue",
            "rarity": "rare",
            "content": "5 diálogos únicos no disponibles en la historia principal",
            "level_required": 3
        }
    ],
    
    "beneficios": [
        {
            "id": "multiplicador_2x_24h",
            "name": "Multiplicador x2 (24h)",
            "description": "Duplica todos los besitos ganados durante 24 horas",
            "price": 80,
            "type": "multiplier",
            "rarity": "rare",
            "duration_hours": 24,
            "multiplier": 2.0,
            "level_required": 2
        },
        {
            "id": "mision_extra",
            "name": "Misión Bonus Diaria",
            "description": "Una misión adicional por día durante una semana",
            "price": 100,
            "type": "mission_bonus",
            "rarity": "epic",
            "duration_days": 7,
            "effect": "Misión adicional cada día",
            "level_required": 3
        },
        {
            "id": "regalo_doble",
            "name": "Recompensa Diaria x2",
            "description": "Duplica la recompensa diaria por una semana",
            "price": 120,
            "type": "daily_bonus",
            "rarity": "epic",
            "duration_days": 7,
            "multiplier": 2.0,
            "level_required": 3
        },
        {
            "id": "acceso_vip_temp",
            "name": "Acceso VIP Temporal (3 días)",
            "description": "Acceso completo a contenido VIP por 3 días",
            "price": 150,
            "type": "vip_access",
            "rarity": "legendary",
            "duration_days": 3,
            "effect": "Acceso completo VIP",
            "level_required": 5
        },
        {
            "id": "multiplicador_mega",
            "name": "Mega Multiplicador x5 (2h)",
            "description": "Multiplica besitos por 5 durante 2 horas intensas",
            "price": 200,
            "type": "mega_multiplier",
            "rarity": "legendary",
            "duration_hours": 2,
            "multiplier": 5.0,
            "level_required": 6
        },
        {
            "id": "pack_beneficios",
            "name": "Pack de Beneficios Premium",
            "description": "Combinación de varios multiplicadores y bonuses",
            "price": 300,
            "type": "benefit_bundle",
            "rarity": "mythic",
            "contents": ["multiplicador_2x_24h", "regalo_doble", "mision_extra"],
            "discount": 25,  # 25% descuento
            "level_required": 7
        }
    ]
}

# Configuración de rareza y colores
RARITY_CONFIG = {
    "common": {
        "name": "Común",
        "color": "⚪",
        "emoji": "⚪"
    },
    "rare": {
        "name": "Raro",
        "color": "🔵",
        "emoji": "💎"
    },
    "epic": {
        "name": "Épico",
        "color": "🟣",
        "emoji": "✨"
    },
    "legendary": {
        "name": "Legendario",
        "color": "🟡",
        "emoji": "👑"
    },
    "mythic": {
        "name": "Mítico",
        "color": "🔴",
        "emoji": "⭐"
    }
}

def get_item_by_id(item_id: str) -> dict:
    """
    Busca un item por su ID en todas las categorías.
    
    Args:
        item_id: ID del item a buscar.
        
    Returns:
        Dict con el item encontrado o None si no existe.
    """
    for category, items in SHOP_ITEMS.items():
        for item in items:
            if item["id"] == item_id:
                item["category"] = category
                return item
    return None

def get_items_by_category(category: str, user_level: int = 1) -> list:
    """
    Obtiene items de una categoría filtrados por nivel del usuario.
    
    Args:
        category: Categoría de items.
        user_level: Nivel del usuario.
        
    Returns:
        Lista de items disponibles para el usuario.
    """
    if category not in SHOP_ITEMS:
        return []
    
    available_items = []
    for item in SHOP_ITEMS[category]:
        if item.get("level_required", 1) <= user_level:
            available_items.append(item)
    
    return available_items

def calculate_final_price(item: dict, user_data: dict = None) -> int:
    """
    Calcula el precio final de un item considerando descuentos.
    
    Args:
        item: Item del cual calcular el precio.
        user_data: Datos del usuario para descuentos especiales.
        
    Returns:
        Precio final del item.
    """
    base_price = item["price"]
    
    # Aplicar descuento del item si existe
    discount = item.get("discount", 0)
    if discount > 0:
        base_price = int(base_price * (1 - discount / 100))
    
    # Descuentos adicionales basados en el usuario podrían ir aquí
    # Por ejemplo: descuentos VIP, descuentos por nivel, etc.
    
    return base_price

def format_item_description(item: dict) -> str:
    """
    Formatea la descripción de un item para mostrar en el bot.
    
    Args:
        item: Item a formatear.
        
    Returns:
        Descripción formateada en markdown.
    """
    rarity_info = RARITY_CONFIG.get(item["rarity"], RARITY_CONFIG["common"])
    price = calculate_final_price(item)
    
    text = f"{rarity_info['emoji']} **{item['name']}**\n"
    text += f"_{item['description']}_\n\n"
    
    # Precio con descuento si aplica
    if item.get("discount", 0) > 0:
        original_price = item["price"]
        text += f"💰 ~~{original_price}~~ **{price} besitos** (-{item['discount']}%)\n"
    else:
        text += f"💰 **{price} besitos**\n"
    
    # Información adicional según el tipo
    if "preview" in item:
        text += f"👁️ {item['preview']}\n"
    
    if "effect" in item:
        text += f"⚡ {item['effect']}\n"
    
    if "duration_hours" in item:
        text += f"⏰ Duración: {item['duration_hours']} horas\n"
    
    if "duration_days" in item:
        text += f"📅 Duración: {item['duration_days']} días\n"
    
    if "level_required" in item and item["level_required"] > 1:
        text += f"🎯 Nivel requerido: {item['level_required']}\n"
    
    text += f"🏷️ Rareza: {rarity_info['name']}\n"
    
    return text