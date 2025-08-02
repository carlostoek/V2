"""
Teclados para usuarios Free (nuevos usuarios)
Adaptado del módulo de menús con edición de mensajes y auto-eliminación
"""

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_free_main_menu_kb() -> InlineKeyboardMarkup:
    """Return the main menu keyboard for free users."""
    builder = InlineKeyboardBuilder()
    
    # Primera fila - Información sobre la creadora
    builder.button(text="🎀 Miss Packs", callback_data="free_miss_packs")
    builder.button(text="👑 Canal Premium", callback_data="free_canal_premium")
    
    # Segunda fila - Contenido y servicios
    builder.button(text="💌 Contenido Custom", callback_data="free_contenido_custom")
    builder.button(text="🎁 Desbloquear Regalo", callback_data="free_gift")
    
    # Tercera fila - Entretenimiento
    builder.button(text="🎮 Juego Kinky", callback_data="free_game")
    builder.button(text="🌐 Sígueme", callback_data="free_follow")
    
    # Configurar disposición: 2, 2, 2
    builder.adjust(2, 2, 2)
    return builder.as_markup()

def get_miss_packs_info_kb() -> InlineKeyboardMarkup:
    """Keyboard for Miss Packs information section."""
    builder = InlineKeyboardBuilder()
    
    # Botón principal de interés
    builder.button(text="💖 Me Interesa", callback_data="interest_miss_packs")
    
    # Botones de información extendida
    builder.button(text="📸 Ver Galería", callback_data="miss_packs_gallery")
    builder.button(text="🎬 Videos Preview", callback_data="miss_packs_videos")
    
    # Botón de regreso
    builder.button(text="↩️ Regresar", callback_data="free_main_menu")
    
    # Disposición: 1, 2, 1
    builder.adjust(1, 2, 1)
    return builder.as_markup()

def get_canal_premium_info_kb() -> InlineKeyboardMarkup:
    """Keyboard for Canal Premium information section."""
    builder = InlineKeyboardBuilder()
    
    # Botón principal de interés
    builder.button(text="👑 Me Interesa", callback_data="interest_canal_premium")
    
    # Botones de información extendida
    builder.button(text="💎 Beneficios VIP", callback_data="premium_benefits")
    builder.button(text="💰 Precios", callback_data="premium_prices")
    
    # Botón de regreso
    builder.button(text="↩️ Regresar", callback_data="free_main_menu")
    
    # Disposición: 1, 2, 1
    builder.adjust(1, 2, 1)
    return builder.as_markup()

def get_contenido_custom_info_kb() -> InlineKeyboardMarkup:
    """Keyboard for Contenido Custom information section."""
    builder = InlineKeyboardBuilder()
    
    # Botón principal de interés
    builder.button(text="🔥 Me Interesa", callback_data="interest_contenido_custom")
    
    # Botones de información extendida
    builder.button(text="🎨 Tipos de Contenido", callback_data="custom_types")
    builder.button(text="⏰ Tiempos de Entrega", callback_data="custom_delivery")
    
    # Botón de regreso
    builder.button(text="↩️ Regresar", callback_data="free_main_menu")
    
    # Disposición: 1, 2, 1
    builder.adjust(1, 2, 1)
    return builder.as_markup()

def get_free_game_kb() -> InlineKeyboardMarkup:
    """Keyboard shown in the free mini game section."""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="🎮 Jugar", callback_data="free_game_play")
    builder.button(text="🏆 Puntuación", callback_data="free_game_score")
    builder.button(text="↩️ Menú Principal", callback_data="free_main_menu")
    
    builder.adjust(2, 1)
    return builder.as_markup()

def get_free_gift_kb() -> InlineKeyboardMarkup:
    """Keyboard for free gift section."""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="🎁 Reclamar Regalo", callback_data="claim_free_gift")
    builder.button(text="📅 Próximo Regalo", callback_data="next_gift_info")
    builder.button(text="↩️ Menú Principal", callback_data="free_main_menu")
    
    builder.adjust(2, 1)
    return builder.as_markup()

def get_follow_me_kb() -> InlineKeyboardMarkup:
    """Keyboard for social media follow section."""
    builder = InlineKeyboardBuilder()
    
    # Enlaces a redes sociales (usar URLs reales cuando estén disponibles)
    builder.button(text="📸 Instagram", url="https://instagram.com/miss_packs")
    builder.button(text="🐦 Twitter", url="https://twitter.com/miss_packs")
    builder.button(text="💋 OnlyFans", url="https://onlyfans.com/miss_packs")
    
    builder.button(text="↩️ Menú Principal", callback_data="free_main_menu")
    
    builder.adjust(1, 1, 1, 1)
    return builder.as_markup()

# Teclado para notificaciones al administrador
def get_admin_notification_kb(user_id: int, interest_type: str) -> InlineKeyboardMarkup:
    """Keyboard for admin notifications when user shows interest."""
    builder = InlineKeyboardBuilder()
    
    # Botón para enviar mensaje directo al usuario
    builder.button(
        text="💬 Enviar Mensaje", 
        callback_data=f"admin_message_user_{user_id}_{interest_type}"
    )
    
    # Botón para cerrar la notificación
    builder.button(text="✅ Cerrar", callback_data="admin_close_notification")
    
    builder.adjust(1, 1)
    return builder.as_markup()

# Keyboard para backward compatibility
def get_subscription_kb() -> InlineKeyboardMarkup:
    """Alias for backward compatibility."""
    return get_free_main_menu_kb()