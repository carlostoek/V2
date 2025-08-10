"""Handler para gestión de tarifas VIP."""

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any

from ...keyboards.admin.main_kb import get_tariff_management_keyboard
from ...keyboards.admin.tariff_kb import (
    get_tariff_list_keyboard,
    get_tariff_detail_keyboard,
    get_tariff_creation_keyboard,
    get_tariff_edit_keyboard,
    get_channel_selection_keyboard
)
from ...filters.role import IsAdminFilter
from src.modules.admin.service import AdminService
from src.modules.token.tokeneitor import Tokeneitor
from src.modules.channel.service import ChannelService
from src.core.event_bus import EventBus

tariff_router = Router()

class TariffCreationStates(StatesGroup):
    waiting_for_channel = State()
    waiting_for_name = State()
    waiting_for_price = State()
    waiting_for_duration = State()
    waiting_for_description = State()

class TariffEditStates(StatesGroup):
    waiting_for_selection = State()
    waiting_for_field = State()
    waiting_for_value = State()

@tariff_router.callback_query(F.data == "admin:tariffs")
async def show_tariff_management(callback_query: CallbackQuery, session: AsyncSession):
    """Muestra el panel de gestión de tarifas."""
    try:
        event_bus = EventBus()
        tokeneitor = Tokeneitor(event_bus)
        
        # Obtener estadísticas de tarifas
        tariff_stats = await get_tariff_statistics(tokeneitor)
        
        text = "💰 **GESTIÓN DE TARIFAS**\n\n"
        text += "📊 **Resumen:**\n"
        text += f"• Tarifas Activas: {tariff_stats['active_count']}\n"
        text += f"• Tarifas Inactivas: {tariff_stats['inactive_count']}\n"
        text += f"• Total de Tokens Generados: {tariff_stats['total_tokens']}\n"
        text += f"• Tokens Canjeados: {tariff_stats['redeemed_tokens']}\n\n"
        
        text += "🎯 **Tarifas Más Populares:**\n"
        for tariff in tariff_stats['popular_tariffs']:
            text += f"• {tariff['name']}: ${tariff['price']:.2f} ({tariff['sales']} ventas)\n"
        
        text += "\n🛠️ **Opciones Disponibles:**\n"
        text += "• Crear nuevas tarifas con precios personalizados\n"
        text += "• Editar tarifas existentes\n"
        text += "• Activar/desactivar tarifas según demanda\n"
        text += "• Ver estadísticas detalladas de ventas\n"
        
        await callback_query.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=get_tariff_management_keyboard()
        )
        await callback_query.answer()
        
    except Exception as e:
        await callback_query.answer(f"Error al cargar gestión de tarifas: {str(e)}")

@tariff_router.callback_query(F.data == "tariff:list")
async def show_tariff_list(callback_query: CallbackQuery, session: AsyncSession):
    """Muestra la lista de todas las tarifas."""
    try:
        event_bus = EventBus()
        tokeneitor = Tokeneitor(event_bus)
        
        # Por ahora usamos datos simulados, después se conectará con el servicio real
        tariffs = [
            {
                "id": 1,
                "name": "VIP 1 Semana",
                "price": 9.99,
                "duration_days": 7,
                "is_active": True,
                "description": "Acceso VIP por 1 semana completa",
                "sales": 45
            },
            {
                "id": 2,
                "name": "VIP 1 Mes",
                "price": 29.99,
                "duration_days": 30,
                "is_active": True,
                "description": "Acceso VIP por 1 mes completo",
                "sales": 67
            },
            {
                "id": 3,
                "name": "VIP 3 Meses",
                "price": 79.99,
                "duration_days": 90,
                "is_active": True,
                "description": "Acceso VIP por 3 meses",
                "sales": 30
            }
        ]
        
        text = "📋 **LISTA DE TARIFAS**\n\n"
        
        for tariff in tariffs:
            status_icon = "✅" if tariff["is_active"] else "❌"
            text += f"{status_icon} **{tariff['name']}**\n"
            text += f"💰 Precio: ${tariff['price']:.2f}\n"
            text += f"⏰ Duración: {tariff['duration_days']} días\n"
            text += f"📊 Ventas: {tariff['sales']} tokens\n"
            text += f"📝 {tariff['description']}\n"
            text += "─────────────────\n"
        
        text += "\n💡 **Tip:** Haz clic en 'Editar' para modificar cualquier tarifa"
        
        await callback_query.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=get_tariff_list_keyboard(tariffs)
        )
        await callback_query.answer()
        
    except Exception as e:
        await callback_query.answer(f"Error al obtener lista de tarifas: {str(e)}")

@tariff_router.callback_query(F.data == "tariff:create")
async def start_tariff_creation(callback_query: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Inicia el proceso de creación de tarifa."""
    try:
        text = "➕ **CREAR NUEVA TARIFA**\n\n"
        text += "🎯 **Paso 1/5: Seleccionar Canal**\n\n"
        text += "Selecciona el canal para el cual crear la tarifa:\n"
        text += "• Canal VIP: Acceso premium con contenido exclusivo\n"
        text += "• Canal Free: Acceso gratuito con limitaciones\n\n"
        text += "💡 **Tip:** Las tarifas VIP generan más ingresos"
        
        # Simular canales disponibles
        channels = [
            {"id": 1, "name": "Canal VIP Principal", "type": "vip"},
            {"id": 2, "name": "Canal Free", "type": "free"}
        ]
        
        await state.set_state(TariffCreationStates.waiting_for_channel)
        await callback_query.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=get_channel_selection_keyboard(channels)
        )
        await callback_query.answer()
        
    except Exception as e:
        await callback_query.answer(f"Error al iniciar creación de tarifa: {str(e)}")

@tariff_router.callback_query(F.data.startswith("channel:select:"), TariffCreationStates.waiting_for_channel)
async def channel_selected(callback_query: CallbackQuery, state: FSMContext):
    """Maneja la selección de canal para la nueva tarifa."""
    try:
        channel_id = int(callback_query.data.split(":")[-1])
        await state.update_data(channel_id=channel_id)
        
        text = "➕ **CREAR NUEVA TARIFA**\n\n"
        text += "📝 **Paso 2/5: Nombre de la Tarifa**\n\n"
        text += "Ingresa un nombre descriptivo para la tarifa:\n\n"
        text += "🌟 **Ejemplos exitosos:**\n"
        text += "• VIP 1 Semana\n"
        text += "• VIP Premium 30 Días\n"
        text += "• VIP Trimestral\n"
        text += "• Acceso VIP Express\n\n"
        text += "💡 **Tip:** Nombres claros aumentan las conversiones\n\n"
        text += "Escribe el nombre de la tarifa:"
        
        await state.set_state(TariffCreationStates.waiting_for_name)
        await callback_query.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=get_tariff_creation_keyboard("name")
        )
        await callback_query.answer()
        
    except Exception as e:
        await callback_query.answer(f"Error al seleccionar canal: {str(e)}")

@tariff_router.message(TariffCreationStates.waiting_for_name)
async def tariff_name_received(message: Message, state: FSMContext):
    """Recibe el nombre de la tarifa."""
    try:
        await state.update_data(name=message.text.strip())
        
        text = "➕ **CREAR NUEVA TARIFA**\n\n"
        text += "💰 **Paso 3/5: Precio de la Tarifa**\n\n"
        text += f"📝 **Nombre:** {message.text.strip()}\n\n"
        text += "Ingresa el precio en USD (solo números):\n\n"
        text += "💲 **Precios Recomendados:**\n"
        text += "• 1 Semana: $5.99 - $14.99\n"
        text += "• 1 Mes: $19.99 - $39.99\n"
        text += "• 3 Meses: $49.99 - $99.99\n"
        text += "• 6 Meses: $89.99 - $149.99\n\n"
        text += "💡 **Tip:** Precios terminados en .99 convierten mejor\n\n"
        text += "Escribe el precio (ej: 29.99):"
        
        await state.set_state(TariffCreationStates.waiting_for_price)
        await message.answer(
            text,
            parse_mode="Markdown",
            reply_markup=get_tariff_creation_keyboard("price")
        )
        
    except Exception as e:
        await message.answer(f"Error al procesar nombre: {str(e)}")

@tariff_router.message(TariffCreationStates.waiting_for_price)
async def tariff_price_received(message: Message, state: FSMContext):
    """Recibe el precio de la tarifa."""
    try:
        try:
            price = float(message.text.strip())
            if price <= 0:
                raise ValueError("El precio debe ser mayor que 0")
        except ValueError:
            await message.answer(
                "❌ **Precio inválido**\n\n"
                "Por favor ingresa un número válido mayor que 0.\n"
                "Ejemplo: 29.99"
            )
            return
        
        await state.update_data(price=price)
        data = await state.get_data()
        
        text = "➕ **CREAR NUEVA TARIFA**\n\n"
        text += "⏰ **Paso 4/5: Duración de la Suscripción**\n\n"
        text += f"📝 **Nombre:** {data['name']}\n"
        text += f"💰 **Precio:** ${price:.2f}\n\n"
        text += "Ingresa la duración en días:\n\n"
        text += "📅 **Duraciones Populares:**\n"
        text += "• 7 días (1 semana)\n"
        text += "• 30 días (1 mes)\n"
        text += "• 90 días (3 meses)\n"
        text += "• 180 días (6 meses)\n"
        text += "• 365 días (1 año)\n\n"
        text += "Escribe el número de días:"
        
        await state.set_state(TariffCreationStates.waiting_for_duration)
        await message.answer(
            text,
            parse_mode="Markdown",
            reply_markup=get_tariff_creation_keyboard("duration")
        )
        
    except Exception as e:
        await message.answer(f"Error al procesar precio: {str(e)}")

@tariff_router.message(TariffCreationStates.waiting_for_duration)
async def tariff_duration_received(message: Message, state: FSMContext):
    """Recibe la duración de la tarifa."""
    try:
        try:
            duration = int(message.text.strip())
            if duration <= 0:
                raise ValueError("La duración debe ser mayor que 0")
        except ValueError:
            await message.answer(
                "❌ **Duración inválida**\n\n"
                "Por favor ingresa un número entero mayor que 0.\n"
                "Ejemplo: 30"
            )
            return
        
        await state.update_data(duration_days=duration)
        data = await state.get_data()
        
        text = "➕ **CREAR NUEVA TARIFA**\n\n"
        text += "📝 **Paso 5/5: Descripción (Opcional)**\n\n"
        text += f"📝 **Nombre:** {data['name']}\n"
        text += f"💰 **Precio:** ${data['price']:.2f}\n"
        text += f"⏰ **Duración:** {duration} días\n\n"
        text += "Ingresa una descripción atractiva (opcional):\n\n"
        text += "✨ **Ejemplos de Descripciones:**\n"
        text += "• \"Acceso completo al contenido premium\"\n"
        text += "• \"Incluye contenido exclusivo y sin anuncios\"\n"
        text += "• \"Acceso prioritario a nuevo contenido\"\n\n"
        text += "💡 Escribe la descripción o usa /skip para omitir:"
        
        await state.set_state(TariffCreationStates.waiting_for_description)
        await message.answer(
            text,
            parse_mode="Markdown",
            reply_markup=get_tariff_creation_keyboard("description")
        )
        
    except Exception as e:
        await message.answer(f"Error al procesar duración: {str(e)}")

@tariff_router.message(TariffCreationStates.waiting_for_description)
async def tariff_description_received(message: Message, state: FSMContext, session: AsyncSession):
    """Recibe la descripción y crea la tarifa."""
    try:
        description = None
        if message.text.strip().lower() != "/skip":
            description = message.text.strip()
        
        data = await state.get_data()
        
        # Crear la tarifa usando el servicio Tokeneitor
        event_bus = EventBus()
        tokeneitor = Tokeneitor(event_bus)
        
        # Por ahora simulamos la creación exitosa
        # En producción se usaría: 
        # tariff_id = await tokeneitor.create_tariff(
        #     channel_id=data['channel_id'],
        #     name=data['name'],
        #     price=data['price'],
        #     duration_days=data['duration_days'],
        #     admin_id=message.from_user.id,
        #     description=description
        # )
        
        tariff_id = 123  # Simulado
        
        if tariff_id:
            text = "✅ **TARIFA CREADA EXITOSAMENTE**\n\n"
            text += f"🆔 **ID:** {tariff_id}\n"
            text += f"📝 **Nombre:** {data['name']}\n"
            text += f"💰 **Precio:** ${data['price']:.2f}\n"
            text += f"⏰ **Duración:** {data['duration_days']} días\n"
            if description:
                text += f"📄 **Descripción:** {description}\n"
            text += f"🎯 **Estado:** Activa\n\n"
            text += "🚀 **¡La tarifa está lista para generar tokens!**\n"
            text += "Ahora puedes ir a 'Tokens VIP' para generar enlaces de venta."
            
            success_keyboard = [
                [{"text": "🎫 Generar Tokens", "data": "admin:tokens"}],
                [{"text": "📋 Ver Tarifas", "data": "tariff:list"}],
                [{"text": "⬅️ Panel Admin", "data": "admin:main"}]
            ]
        else:
            text = "❌ **Error al crear la tarifa**\n\n"
            text += "Ha ocurrido un problema al crear la tarifa.\n"
            text += "Por favor intenta nuevamente o contacta al soporte técnico."
            
            success_keyboard = [
                [{"text": "🔄 Intentar Nuevamente", "data": "tariff:create"}],
                [{"text": "⬅️ Volver", "data": "admin:tariffs"}]
            ]
        
        await state.clear()
        await message.answer(
            text,
            parse_mode="Markdown",
            reply_markup=create_keyboard_from_data(success_keyboard)
        )
        
    except Exception as e:
        await message.answer(f"Error al crear tarifa: {str(e)}")
        await state.clear()

@tariff_router.callback_query(F.data == "tariff:stats")
async def show_tariff_statistics(callback_query: CallbackQuery, session: AsyncSession):
    """Muestra estadísticas detalladas de tarifas."""
    try:
        text = "📊 **ESTADÍSTICAS DE TARIFAS**\n\n"
        
        # Estadísticas simuladas - en producción vendrían del servicio
        text += "💰 **Ingresos por Tarifa (Último Mes):**\n"
        text += "• VIP 1 Mes: $2,009.33 (67 ventas)\n"
        text += "• VIP 1 Semana: $449.55 (45 ventas)\n"
        text += "• VIP 3 Meses: $2,399.70 (30 ventas)\n"
        text += "─────────────────\n"
        text += "💎 **Total:** $4,858.58 (142 ventas)\n\n"
        
        text += "📈 **Rendimiento:**\n"
        text += "• Tasa de Conversión Promedio: 91.0%\n"
        text += "• Precio Promedio por Venta: $34.20\n"
        text += "• Duración Promedio: 38 días\n"
        text += "• Crecimiento vs Mes Anterior: +23.5%\n\n"
        
        text += "🏆 **Top Performers:**\n"
        text += "1. VIP 1 Mes (47.2% de ingresos)\n"
        text += "2. VIP 3 Meses (49.4% de ingresos)\n"
        text += "3. VIP 1 Semana (9.3% de ingresos)\n\n"
        
        text += "📅 **Tendencias:**\n"
        text += "• Lunes: Día con más ventas\n"
        text += "• 18:00-22:00: Horario pico de compras\n"
        text += "• Tokens .99: +15% conversión vs precios redondos"
        
        stats_keyboard = [
            [{"text": "📤 Exportar Datos", "data": "tariff:export"}],
            [{"text": "📈 Ver Gráficos", "data": "tariff:charts"}],
            [{"text": "⬅️ Volver", "data": "admin:tariffs"}]
        ]
        
        await callback_query.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=create_keyboard_from_data(stats_keyboard)
        )
        await callback_query.answer()
        
    except Exception as e:
        await callback_query.answer(f"Error al obtener estadísticas: {str(e)}")

# Funciones auxiliares

async def get_tariff_statistics(tokeneitor: Tokeneitor) -> Dict[str, Any]:
    """Obtiene estadísticas de tarifas."""
    # Por ahora devuelve datos simulados
    return {
        "active_count": 3,
        "inactive_count": 0,
        "total_tokens": 156,
        "redeemed_tokens": 142,
        "popular_tariffs": [
            {"name": "VIP 1 Mes", "price": 29.99, "sales": 67},
            {"name": "VIP 1 Semana", "price": 9.99, "sales": 45},
            {"name": "VIP 3 Meses", "price": 79.99, "sales": 30}
        ]
    }

def create_keyboard_from_data(keyboard_data: List[List[Dict[str, str]]]):
    """Crea un teclado a partir de datos estructurados."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    buttons = []
    for row in keyboard_data:
        button_row = []
        for button in row:
            button_row.append(InlineKeyboardButton(
                text=button["text"], 
                callback_data=button["data"]
            ))
        buttons.append(button_row)
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)