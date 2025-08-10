"""Keyboards específicos para la gestión de tokens."""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict, Any

def get_token_generation_keyboard() -> InlineKeyboardMarkup:
    """Devuelve el teclado para generación de tokens."""
    buttons = [
        [
            InlineKeyboardButton(text="🎫 Token Individual", callback_data="token:generate_single"),
            InlineKeyboardButton(text="📦 Lote de Tokens", callback_data="token:bulk_generate")
        ],
        [
            InlineKeyboardButton(text="⚡ Generación Rápida", callback_data="token:quick_generate")
        ],
        [
            InlineKeyboardButton(text="⬅️ Volver", callback_data="admin:tokens")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_tariff_selection_keyboard(tariffs: List[Dict[str, Any]], bulk: bool = False) -> InlineKeyboardMarkup:
    """Devuelve el teclado para selección de tarifas."""
    buttons = []
    
    prefix = "bulk:tariff:" if bulk else "generate:tariff:"
    
    for tariff in tariffs:
        icon = "💎" if tariff["price"] >= 50 else "⭐" if tariff["price"] >= 20 else "💰"
        conversion_icon = "🔥" if tariff["conversion_rate"] >= 90 else "📈"
        
        button_text = f"{icon} {tariff['name']} - ${tariff['price']:.2f} {conversion_icon}"
        
        buttons.append([
            InlineKeyboardButton(
                text=button_text,
                callback_data=f"{prefix}{tariff['id']}"
            )
        ])
        
        # Mostrar info adicional en texto pequeño
        if not bulk:
            info_text = f"⏱️ {tariff['duration_days']}d | 📊 {tariff['conversion_rate']:.1f}%"
            buttons.append([
                InlineKeyboardButton(
                    text=info_text,
                    callback_data=f"tariff:info:{tariff['id']}"
                )
            ])
    
    # Botones de control
    control_buttons = [
        InlineKeyboardButton(text="🔄 Actualizar Tarifas", callback_data="tariff:refresh"),
        InlineKeyboardButton(text="➕ Nueva Tarifa", callback_data="tariff:create")
    ]
    buttons.append(control_buttons)
    
    buttons.append([
        InlineKeyboardButton(text="❌ Cancelar", callback_data="admin:tokens")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_token_list_keyboard(tokens: List[Dict[str, Any]], page: int = 0) -> InlineKeyboardMarkup:
    """Devuelve el teclado para la lista de tokens."""
    buttons = []
    
    # Filtros y ordenamiento
    filter_buttons = [
        InlineKeyboardButton(text="🟢 Activos", callback_data="token:filter:active"),
        InlineKeyboardButton(text="✅ Usados", callback_data="token:filter:used"),
        InlineKeyboardButton(text="❌ Expirados", callback_data="token:filter:expired")
    ]
    buttons.append(filter_buttons)
    
    # Tokens individuales (mostrar hasta 5 por página)
    start_idx = page * 5
    page_tokens = tokens[start_idx:start_idx + 5]
    
    for token in page_tokens:
        status_icon = "✅" if token["status"] == "Usado" else "🟡" if token["status"] == "Activo" else "❌"
        button_text = f"{status_icon} #{token['id']} - {token['tariff']} | ${token['price']:.2f}"
        
        buttons.append([
            InlineKeyboardButton(
                text=button_text,
                callback_data=f"token:detail:{token['id']}"
            )
        ])
    
    # Paginación
    pagination_buttons = []
    if page > 0:
        pagination_buttons.append(
            InlineKeyboardButton(text="⬅️ Anterior", callback_data=f"token:page:{page-1}")
        )
    if start_idx + 5 < len(tokens):
        pagination_buttons.append(
            InlineKeyboardButton(text="➡️ Siguiente", callback_data=f"token:page:{page+1}")
        )
    
    if pagination_buttons:
        buttons.append(pagination_buttons)
    
    # Acciones masivas
    bulk_actions = [
        InlineKeyboardButton(text="🔍 Buscar", callback_data="token:search"),
        InlineKeyboardButton(text="📤 Exportar", callback_data="token:export")
    ]
    buttons.append(bulk_actions)
    
    buttons.append([
        InlineKeyboardButton(text="⬅️ Panel Tokens", callback_data="admin:tokens")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_token_detail_keyboard(token_id: int, status: str) -> InlineKeyboardMarkup:
    """Devuelve el teclado para detalles de un token específico."""
    buttons = []
    
    if status == "Activo":
        # Token activo - opciones de gestión
        buttons.extend([
            [
                InlineKeyboardButton(text="📋 Copiar Enlace", callback_data=f"token:copy:{token_id}"),
                InlineKeyboardButton(text="📤 Enviar", callback_data=f"token:send:{token_id}")
            ],
            [
                InlineKeyboardButton(text="⏰ Extender Validez", callback_data=f"token:extend:{token_id}"),
                InlineKeyboardButton(text="❌ Invalidar", callback_data=f"token:invalidate:{token_id}")
            ]
        ])
    elif status == "Usado":
        # Token usado - opciones de análisis
        buttons.extend([
            [
                InlineKeyboardButton(text="👤 Ver Usuario", callback_data=f"user:view:from_token:{token_id}"),
                InlineKeyboardButton(text="📊 Estadísticas", callback_data=f"token:usage_stats:{token_id}")
            ],
            [
                InlineKeyboardButton(text="🔄 Renovar Suscripción", callback_data=f"user:renew:from_token:{token_id}")
            ]
        ])
    else:  # Expirado
        # Token expirado - opciones limitadas
        buttons.append([
            InlineKeyboardButton(text="🔄 Regenerar", callback_data=f"token:regenerate:{token_id}"),
            InlineKeyboardButton(text="📊 Análisis", callback_data=f"token:expiry_analysis:{token_id}")
        ])
    
    # Opciones comunes
    buttons.extend([
        [
            InlineKeyboardButton(text="📝 Agregar Nota", callback_data=f"token:add_note:{token_id}"),
            InlineKeyboardButton(text="🗑️ Eliminar", callback_data=f"token:delete:{token_id}")
        ],
        [
            InlineKeyboardButton(text="⬅️ Lista Tokens", callback_data="token:list")
        ]
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_token_search_keyboard() -> InlineKeyboardMarkup:
    """Devuelve el teclado para búsqueda de tokens."""
    buttons = [
        [
            InlineKeyboardButton(text="🔑 Por Token ID", callback_data="search:token_id"),
            InlineKeyboardButton(text="👤 Por Usuario", callback_data="search:user")
        ],
        [
            InlineKeyboardButton(text="🏷️ Por Tarifa", callback_data="search:tariff"),
            InlineKeyboardButton(text="📅 Por Fecha", callback_data="search:date")
        ],
        [
            InlineKeyboardButton(text="💰 Por Precio", callback_data="search:price"),
            InlineKeyboardButton(text="📊 Por Estado", callback_data="search:status")
        ],
        [
            InlineKeyboardButton(text="🔍 Búsqueda Avanzada", callback_data="search:advanced")
        ],
        [
            InlineKeyboardButton(text="⬅️ Volver", callback_data="admin:tokens")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_bulk_generation_keyboard() -> InlineKeyboardMarkup:
    """Devuelve el teclado para generación masiva."""
    buttons = [
        [
            InlineKeyboardButton(text="⚡ 10 tokens", callback_data="bulk:quantity:10"),
            InlineKeyboardButton(text="⚡ 25 tokens", callback_data="bulk:quantity:25")
        ],
        [
            InlineKeyboardButton(text="⚡ 50 tokens", callback_data="bulk:quantity:50"),
            InlineKeyboardButton(text="⚡ 100 tokens", callback_data="bulk:quantity:100")
        ],
        [
            InlineKeyboardButton(text="⚡ 250 tokens", callback_data="bulk:quantity:250"),
            InlineKeyboardButton(text="⚡ 500 tokens", callback_data="bulk:quantity:500")
        ],
        [
            InlineKeyboardButton(text="🎯 Cantidad Personalizada", callback_data="bulk:custom_quantity")
        ],
        [
            InlineKeyboardButton(text="❌ Cancelar", callback_data="admin:tokens")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_token_export_keyboard() -> InlineKeyboardMarkup:
    """Devuelve el teclado para opciones de exportación."""
    buttons = [
        [
            InlineKeyboardButton(text="📊 Excel (.xlsx)", callback_data="export:excel"),
            InlineKeyboardButton(text="📄 CSV", callback_data="export:csv")
        ],
        [
            InlineKeyboardButton(text="🔗 JSON (Enlaces)", callback_data="export:json_links"),
            InlineKeyboardButton(text="📋 Texto Plano", callback_data="export:txt")
        ],
        [
            InlineKeyboardButton(text="🎯 Solo Activos", callback_data="export:active_only"),
            InlineKeyboardButton(text="✅ Solo Usados", callback_data="export:used_only")
        ],
        [
            InlineKeyboardButton(text="📅 Por Período", callback_data="export:by_period")
        ],
        [
            InlineKeyboardButton(text="⬅️ Volver", callback_data="token:stats")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_token_analytics_keyboard() -> InlineKeyboardMarkup:
    """Devuelve el teclado para análisis de tokens."""
    buttons = [
        [
            InlineKeyboardButton(text="📈 Conversión por Hora", callback_data="analytics:hourly"),
            InlineKeyboardButton(text="📊 Conversión por Día", callback_data="analytics:daily")
        ],
        [
            InlineKeyboardButton(text="🏷️ Performance por Tarifa", callback_data="analytics:by_tariff"),
            InlineKeyboardButton(text="👥 Análisis de Usuarios", callback_data="analytics:users")
        ],
        [
            InlineKeyboardButton(text="💰 ROI y Revenue", callback_data="analytics:revenue"),
            InlineKeyboardButton(text="⏰ Tiempo de Canje", callback_data="analytics:redemption_time")
        ],
        [
            InlineKeyboardButton(text="🎯 Predicciones", callback_data="analytics:predictions"),
            InlineKeyboardButton(text="📋 Informe Completo", callback_data="analytics:full_report")
        ],
        [
            InlineKeyboardButton(text="⬅️ Estadísticas", callback_data="token:stats")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_token_management_actions_keyboard() -> InlineKeyboardMarkup:
    """Devuelve el teclado para acciones de gestión de tokens."""
    buttons = [
        [
            InlineKeyboardButton(text="⏰ Extender Expiración Masiva", callback_data="bulk:extend_expiry"),
            InlineKeyboardButton(text="❌ Invalidar Masivamente", callback_data="bulk:invalidate")
        ],
        [
            InlineKeyboardButton(text="🔄 Regenerar Expirados", callback_data="bulk:regenerate_expired"),
            InlineKeyboardButton(text="🧹 Limpiar Antiguos", callback_data="bulk:cleanup_old")
        ],
        [
            InlineKeyboardButton(text="📬 Notificar Usuarios", callback_data="bulk:notify_users"),
            InlineKeyboardButton(text="🏷️ Cambiar Tarifas", callback_data="bulk:change_tariffs")
        ],
        [
            InlineKeyboardButton(text="⬅️ Panel Tokens", callback_data="admin:tokens")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_quick_generation_keyboard() -> InlineKeyboardMarkup:
    """Devuelve el teclado para generación rápida de tokens."""
    buttons = [
        [
            InlineKeyboardButton(text="⚡ VIP Semana ($9.99)", callback_data="quick:generate:1"),
            InlineKeyboardButton(text="⚡ VIP Mes ($29.99)", callback_data="quick:generate:2")
        ],
        [
            InlineKeyboardButton(text="⚡ VIP Trimestre ($79.99)", callback_data="quick:generate:3")
        ],
        [
            InlineKeyboardButton(text="🎯 Más Opciones", callback_data="token:generate")
        ],
        [
            InlineKeyboardButton(text="⬅️ Panel Tokens", callback_data="admin:tokens")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)