"""Keyboards específicos para la gestión de tarifas."""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict, Any

def get_tariff_list_keyboard(tariffs: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    """Devuelve el teclado con la lista de tarifas."""
    buttons = []
    
    # Mostrar hasta 5 tarifas por página
    for i, tariff in enumerate(tariffs[:5]):
        status_icon = "✅" if tariff.get("is_active", True) else "❌"
        button_text = f"{status_icon} {tariff['name']} - ${tariff['price']:.2f}"
        buttons.append([
            InlineKeyboardButton(
                text=button_text, 
                callback_data=f"tariff:detail:{tariff['id']}"
            )
        ])
    
    # Botones de acción
    action_buttons = [
        [
            InlineKeyboardButton(text="➕ Nueva Tarifa", callback_data="tariff:create"),
            InlineKeyboardButton(text="🔄 Actualizar", callback_data="tariff:list")
        ]
    ]
    
    # Si hay más de 5 tarifas, agregar paginación
    if len(tariffs) > 5:
        action_buttons.append([
            InlineKeyboardButton(text="⬅️ Anterior", callback_data="tariff:page:prev"),
            InlineKeyboardButton(text="➡️ Siguiente", callback_data="tariff:page:next")
        ])
    
    action_buttons.append([
        InlineKeyboardButton(text="⬅️ Volver", callback_data="admin:tariffs")
    ])
    
    buttons.extend(action_buttons)
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_tariff_detail_keyboard(tariff_id: int, is_active: bool = True) -> InlineKeyboardMarkup:
    """Devuelve el teclado para detalles de una tarifa específica."""
    buttons = [
        [
            InlineKeyboardButton(text="✏️ Editar", callback_data=f"tariff:edit:{tariff_id}"),
            InlineKeyboardButton(text="🎫 Generar Token", callback_data=f"token:generate:{tariff_id}")
        ],
        [
            InlineKeyboardButton(text="📊 Estadísticas", callback_data=f"tariff:stats:{tariff_id}"),
            InlineKeyboardButton(text="📋 Ver Tokens", callback_data=f"token:list:{tariff_id}")
        ]
    ]
    
    # Botón de activar/desactivar según el estado
    if is_active:
        buttons.append([
            InlineKeyboardButton(text="❌ Desactivar", callback_data=f"tariff:deactivate:{tariff_id}")
        ])
    else:
        buttons.append([
            InlineKeyboardButton(text="✅ Activar", callback_data=f"tariff:activate:{tariff_id}")
        ])
    
    buttons.extend([
        [InlineKeyboardButton(text="🗑️ Eliminar", callback_data=f"tariff:delete:{tariff_id}")],
        [InlineKeyboardButton(text="⬅️ Lista Tarifas", callback_data="tariff:list")]
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_tariff_creation_keyboard(step: str) -> InlineKeyboardMarkup:
    """Devuelve el teclado para el proceso de creación de tarifas."""
    buttons = []
    
    if step == "name":
        # Sugerencias de nombres
        suggestions = [
            ("VIP 1 Semana", "tariff:suggest_name:VIP 1 Semana"),
            ("VIP 1 Mes", "tariff:suggest_name:VIP 1 Mes"),
            ("VIP 3 Meses", "tariff:suggest_name:VIP 3 Meses")
        ]
        for name, callback_data in suggestions:
            buttons.append([InlineKeyboardButton(text=f"💡 {name}", callback_data=callback_data)])
    
    elif step == "price":
        # Sugerencias de precios
        suggestions = [
            ("$9.99", "tariff:suggest_price:9.99"),
            ("$29.99", "tariff:suggest_price:29.99"),
            ("$79.99", "tariff:suggest_price:79.99")
        ]
        for price, callback_data in suggestions:
            buttons.append([InlineKeyboardButton(text=f"💰 {price}", callback_data=callback_data)])
    
    elif step == "duration":
        # Sugerencias de duración
        suggestions = [
            ("7 días", "tariff:suggest_duration:7"),
            ("30 días", "tariff:suggest_duration:30"),
            ("90 días", "tariff:suggest_duration:90")
        ]
        for duration, callback_data in suggestions:
            buttons.append([InlineKeyboardButton(text=f"⏰ {duration}", callback_data=callback_data)])
    
    elif step == "description":
        # Sugerencias de descripción
        suggestions = [
            ("Omitir", "tariff:skip_description"),
            ("Usar plantilla", "tariff:suggest_description")
        ]
        for text, callback_data in suggestions:
            buttons.append([InlineKeyboardButton(text=f"📝 {text}", callback_data=callback_data)])
    
    # Botón para cancelar
    buttons.append([InlineKeyboardButton(text="❌ Cancelar", callback_data="admin:tariffs")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_tariff_edit_keyboard(tariff_id: int) -> InlineKeyboardMarkup:
    """Devuelve el teclado para editar una tarifa."""
    buttons = [
        [
            InlineKeyboardButton(text="📝 Cambiar Nombre", callback_data=f"tariff:edit_name:{tariff_id}"),
            InlineKeyboardButton(text="💰 Cambiar Precio", callback_data=f"tariff:edit_price:{tariff_id}")
        ],
        [
            InlineKeyboardButton(text="⏰ Cambiar Duración", callback_data=f"tariff:edit_duration:{tariff_id}"),
            InlineKeyboardButton(text="📄 Cambiar Descripción", callback_data=f"tariff:edit_description:{tariff_id}")
        ],
        [
            InlineKeyboardButton(text="🔧 Configuración Avanzada", callback_data=f"tariff:edit_advanced:{tariff_id}")
        ],
        [
            InlineKeyboardButton(text="✅ Guardar Cambios", callback_data=f"tariff:save_changes:{tariff_id}"),
            InlineKeyboardButton(text="❌ Cancelar", callback_data=f"tariff:detail:{tariff_id}")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_channel_selection_keyboard(channels: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    """Devuelve el teclado para selección de canal."""
    buttons = []
    
    for channel in channels:
        icon = "👑" if channel["type"] == "vip" else "🆓"
        button_text = f"{icon} {channel['name']}"
        buttons.append([
            InlineKeyboardButton(
                text=button_text,
                callback_data=f"channel:select:{channel['id']}"
            )
        ])
    
    buttons.append([
        InlineKeyboardButton(text="➕ Crear Nuevo Canal", callback_data="channel:create_new")
    ])
    buttons.append([
        InlineKeyboardButton(text="❌ Cancelar", callback_data="admin:tariffs")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_tariff_confirmation_keyboard(action: str, tariff_id: int) -> InlineKeyboardMarkup:
    """Devuelve el teclado de confirmación para acciones de tarifa."""
    buttons = []
    
    if action == "delete":
        buttons = [
            [
                InlineKeyboardButton(text="🗑️ Sí, Eliminar", callback_data=f"tariff:confirm_delete:{tariff_id}"),
                InlineKeyboardButton(text="❌ Cancelar", callback_data=f"tariff:detail:{tariff_id}")
            ]
        ]
    elif action == "deactivate":
        buttons = [
            [
                InlineKeyboardButton(text="❌ Sí, Desactivar", callback_data=f"tariff:confirm_deactivate:{tariff_id}"),
                InlineKeyboardButton(text="⬅️ Cancelar", callback_data=f"tariff:detail:{tariff_id}")
            ]
        ]
    elif action == "activate":
        buttons = [
            [
                InlineKeyboardButton(text="✅ Sí, Activar", callback_data=f"tariff:confirm_activate:{tariff_id}"),
                InlineKeyboardButton(text="⬅️ Cancelar", callback_data=f"tariff:detail:{tariff_id}")
            ]
        ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_pricing_strategy_keyboard() -> InlineKeyboardMarkup:
    """Devuelve el teclado para estrategias de precios."""
    buttons = [
        [
            InlineKeyboardButton(text="💎 Premium ($50+)", callback_data="pricing:premium"),
            InlineKeyboardButton(text="⭐ Estándar ($20-49)", callback_data="pricing:standard")
        ],
        [
            InlineKeyboardButton(text="💰 Económico ($5-19)", callback_data="pricing:budget"),
            InlineKeyboardButton(text="🎁 Promocional (<$5)", callback_data="pricing:promo")
        ],
        [
            InlineKeyboardButton(text="📊 Analizar Competencia", callback_data="pricing:analyze")
        ],
        [
            InlineKeyboardButton(text="⬅️ Volver", callback_data="admin:tariffs")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_bulk_operations_keyboard() -> InlineKeyboardMarkup:
    """Devuelve el teclado para operaciones masivas en tarifas."""
    buttons = [
        [
            InlineKeyboardButton(text="✅ Activar Todas", callback_data="tariff:bulk_activate"),
            InlineKeyboardButton(text="❌ Desactivar Todas", callback_data="tariff:bulk_deactivate")
        ],
        [
            InlineKeyboardButton(text="💰 Ajustar Precios", callback_data="tariff:bulk_price_adjust"),
            InlineKeyboardButton(text="📤 Exportar Datos", callback_data="tariff:export_all")
        ],
        [
            InlineKeyboardButton(text="🎫 Generar Tokens Masivos", callback_data="tariff:bulk_token_generation")
        ],
        [
            InlineKeyboardButton(text="⬅️ Volver", callback_data="admin:tariffs")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)