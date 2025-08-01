"""Handlers para la administración de tarifas y tokens."""

from aiogram import types
from aiogram.filters import Command
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from src.modules.token.tokeneitor import Tokeneitor
from src.bot.keyboards.admin_keyboards import AdminKeyboardFactory


class TariffStates(StatesGroup):
    """Estados para el flujo de creación de tarifas."""
    waiting_for_name = State()
    waiting_for_duration = State()
    waiting_for_price = State()
    waiting_for_token_validity = State()
    waiting_for_description = State()


async def cmd_tariffs(message: types.Message, tokeneitor: Tokeneitor):
    """
    Maneja el comando /tarifas o botón de gestión de tarifas.
    Muestra el menú principal de gestión de tarifas.
    """
    # Obtener el canal administrado por este usuario
    # En una implementación completa, esto vendría de un servicio de administración
    # Por ahora usamos un valor de ejemplo
    channel_id = 1  # Canal por defecto para ejemplo
    
    # Obtener tarifas existentes
    tariffs = await tokeneitor.get_channel_tariffs(channel_id)
    
    # Construir mensaje
    if tariffs:
        tariff_list = "\n".join([
            f"🏷️ <b>{t['name']}</b>: {t['duration_days']} días - ${t['price']}" 
            for t in tariffs
        ])
        text = (
            "🏷️ <b>Tarifas configuradas:</b>\n\n"
            f"{tariff_list}\n\n"
            "Selecciona una opción:"
        )
    else:
        text = (
            "🏷️ <b>Gestión de Tarifas</b>\n\n"
            "No tienes tarifas configuradas todavía.\n\n"
            "Selecciona una opción:"
        )
    
    # Mostrar teclado con opciones
    await message.answer(
        text, 
        reply_markup=AdminKeyboardFactory.tariff_management(),
        parse_mode="HTML"
    )


async def cmd_new_tariff(message: types.Message, state: FSMContext):
    """
    Inicia el proceso de creación de una nueva tarifa.
    """
    await state.set_state(TariffStates.waiting_for_name)
    await message.answer(
        "🆕 <b>Nueva Tarifa</b>\n\n"
        "Por favor, ingresa el nombre de la tarifa.\n"
        "Ejemplo: \"Premium Mensual\", \"VIP Trimestral\", etc.",
        parse_mode="HTML",
        reply_markup=types.ReplyKeyboardRemove()
    )


async def process_tariff_name(message: types.Message, state: FSMContext):
    """
    Procesa el nombre de la tarifa y solicita la duración.
    """
    # Guardar nombre
    await state.update_data(name=message.text)
    
    # Solicitar duración
    await state.set_state(TariffStates.waiting_for_duration)
    await message.answer(
        "⏱️ <b>Duración de la Suscripción</b>\n\n"
        "¿Cuántos días durará esta suscripción?\n"
        "Ingresa un número entero. Por ejemplo: 30, 90, 365, etc.",
        parse_mode="HTML"
    )


async def process_tariff_duration(message: types.Message, state: FSMContext):
    """
    Procesa la duración de la tarifa y solicita el precio.
    """
    try:
        duration = int(message.text)
        if duration <= 0:
            raise ValueError("La duración debe ser un número positivo")
        
        # Guardar duración
        await state.update_data(duration_days=duration)
        
        # Solicitar precio
        await state.set_state(TariffStates.waiting_for_price)
        await message.answer(
            "💲 <b>Precio de la Tarifa</b>\n\n"
            "¿Cuál es el precio de esta tarifa?\n"
            "Ingresa un número (puede incluir decimales). Por ejemplo: 9.99, 29.90, etc.",
            parse_mode="HTML"
        )
    except ValueError:
        await message.answer(
            "⚠️ <b>Error</b>: Por favor, ingresa un número entero positivo para la duración.\n"
            "Ejemplo: 30, 90, 365, etc.",
            parse_mode="HTML"
        )


async def process_tariff_price(message: types.Message, state: FSMContext):
    """
    Procesa el precio de la tarifa y solicita la validez del token.
    """
    try:
        price = float(message.text.replace(",", "."))
        if price <= 0:
            raise ValueError("El precio debe ser un número positivo")
        
        # Guardar precio
        await state.update_data(price=price)
        
        # Solicitar validez del token
        await state.set_state(TariffStates.waiting_for_token_validity)
        await message.answer(
            "🔑 <b>Validez del Token</b>\n\n"
            "¿Cuántos días serán válidos los tokens generados para esta tarifa?\n"
            "Ingresa un número entero. Por defecto: 7 días.\n"
            "Este es el tiempo que tiene el usuario para canjear el token después de generado.",
            parse_mode="HTML",
            reply_markup=AdminKeyboardFactory.default_options(["7 días (por defecto)"])
        )
    except ValueError:
        await message.answer(
            "⚠️ <b>Error</b>: Por favor, ingresa un número válido para el precio.\n"
            "Ejemplo: 9.99, 29.90, etc.",
            parse_mode="HTML"
        )


async def process_tariff_token_validity(message: types.Message, state: FSMContext):
    """
    Procesa la validez del token y solicita una descripción opcional.
    """
    try:
        # Manejar el caso del botón de valor por defecto
        if message.text == "7 días (por defecto)":
            token_validity = 7
        else:
            token_validity = int(message.text)
            if token_validity <= 0:
                raise ValueError("La validez debe ser un número positivo")
        
        # Guardar validez del token
        await state.update_data(token_validity_days=token_validity)
        
        # Solicitar descripción opcional
        await state.set_state(TariffStates.waiting_for_description)
        await message.answer(
            "📝 <b>Descripción (Opcional)</b>\n\n"
            "Puedes añadir una descripción para esta tarifa.\n"
            "Esta descripción será visible cuando se muestre información detallada de la tarifa.\n\n"
            "Si no deseas añadir una descripción, simplemente envía 'Omitir'.",
            parse_mode="HTML",
            reply_markup=AdminKeyboardFactory.default_options(["Omitir"])
        )
    except ValueError:
        await message.answer(
            "⚠️ <b>Error</b>: Por favor, ingresa un número entero positivo para la validez del token.\n"
            "Ejemplo: 7, 14, 30, etc.",
            parse_mode="HTML"
        )


async def process_tariff_description(message: types.Message, state: FSMContext, tokeneitor: Tokeneitor):
    """
    Procesa la descripción y crea la tarifa.
    """
    # Obtener datos almacenados
    data = await state.get_data()
    
    # Procesar descripción
    if message.text != "Omitir":
        data["description"] = message.text
    else:
        data["description"] = None
    
    # Obtener canal administrado por este usuario
    # En una implementación completa, esto vendría de un servicio de administración
    channel_id = 1  # Canal por defecto para ejemplo
    admin_id = message.from_user.id
    
    # Crear tarifa
    tariff_id = await tokeneitor.create_tariff(
        channel_id=channel_id,
        name=data["name"],
        duration_days=data["duration_days"],
        price=data["price"],
        admin_id=admin_id,
        token_validity_days=data["token_validity_days"],
        description=data["description"]
    )
    
    # Mostrar resultado
    if tariff_id:
        await message.answer(
            "✅ <b>¡Tarifa Creada Exitosamente!</b>\n\n"
            f"Se ha creado la tarifa <b>{data['name']}</b>.\n\n"
            "Ya puedes generar enlaces de invitación para esta tarifa.",
            parse_mode="HTML",
            reply_markup=AdminKeyboardFactory.tariff_management()
        )
    else:
        await message.answer(
            "❌ <b>Error al Crear Tarifa</b>\n\n"
            "Ocurrió un error al intentar crear la tarifa. Por favor, intenta nuevamente.",
            parse_mode="HTML",
            reply_markup=AdminKeyboardFactory.tariff_management()
        )
    
    # Limpiar estado
    await state.clear()


async def cmd_generate_link(message: types.Message, tokeneitor: Tokeneitor):
    """
    Muestra las tarifas disponibles para generar un enlace.
    """
    # Obtener canal administrado por este usuario
    channel_id = 1  # Canal por defecto para ejemplo
    
    # Obtener tarifas existentes
    tariffs = await tokeneitor.get_channel_tariffs(channel_id)
    
    if not tariffs:
        await message.answer(
            "⚠️ <b>No hay tarifas disponibles</b>\n\n"
            "Para generar enlaces de invitación, primero debes crear al menos una tarifa.",
            parse_mode="HTML",
            reply_markup=AdminKeyboardFactory.tariff_management()
        )
        return
    
    # Crear teclado con las tarifas
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(
            text=f"{t['name']} - {t['duration_days']} días - ${t['price']}",
            callback_data=f"generate_token:{t['id']}"
        )] for t in tariffs
    ])
    
    await message.answer(
        "🔗 <b>Generar Enlace de Invitación</b>\n\n"
        "Selecciona la tarifa para la cual deseas generar un enlace:",
        parse_mode="HTML",
        reply_markup=keyboard
    )


async def process_generate_token(callback_query: types.CallbackQuery, tokeneitor: Tokeneitor):
    """
    Genera un token para la tarifa seleccionada y muestra el enlace.
    """
    # Obtener ID de la tarifa
    tariff_id = int(callback_query.data.split(":")[1])
    admin_id = callback_query.from_user.id
    
    # Generar token
    token_url = await tokeneitor.generate_token(tariff_id, admin_id)
    
    if token_url:
        # Crear mensaje con enlace clickeable
        await callback_query.message.answer(
            "✅ <b>Enlace Generado Exitosamente</b>\n\n"
            "Comparte este enlace con el usuario. Al hacer clic, se unirá al canal con la tarifa seleccionada.\n\n"
            f"🔗 <b>Enlace de Invitación:</b>\n{token_url}",
            parse_mode="HTML",
            reply_markup=AdminKeyboardFactory.tariff_management()
        )
    else:
        await callback_query.message.answer(
            "❌ <b>Error al Generar Enlace</b>\n\n"
            "Ocurrió un error al intentar generar el enlace. Por favor, intenta nuevamente.",
            parse_mode="HTML",
            reply_markup=AdminKeyboardFactory.tariff_management()
        )
    
    # Cerrar el callback
    await callback_query.answer()


async def cmd_token_stats(message: types.Message, tokeneitor: Tokeneitor):
    """
    Muestra estadísticas de tokens para el canal.
    """
    # Obtener canal administrado por este usuario
    channel_id = 1  # Canal por defecto para ejemplo
    
    # Obtener estadísticas
    stats = await tokeneitor.get_token_stats(channel_id)
    
    if stats["total_generated"] == 0:
        await message.answer(
            "📊 <b>Estadísticas de Tokens</b>\n\n"
            "No se han generado tokens todavía para este canal.",
            parse_mode="HTML",
            reply_markup=AdminKeyboardFactory.tariff_management()
        )
        return
    
    # Construir mensaje con estadísticas
    stats_text = (
        "📊 <b>Estadísticas de Tokens</b>\n\n"
        f"🔢 <b>Total generados:</b> {stats['total_generated']}\n"
        f"✅ <b>Canjeados:</b> {stats['total_redeemed']}\n"
        f"📈 <b>Tasa de conversión:</b> {stats['conversion_rate']}%\n\n"
        "<b>Por tarifa:</b>\n"
    )
    
    for tariff_name, tariff_stats in stats["by_tariff"].items():
        stats_text += (
            f"  • <b>{tariff_name}:</b> {tariff_stats['generated']} generados, "
            f"{tariff_stats['redeemed']} canjeados ({tariff_stats['conversion_rate']}%)\n"
        )
    
    if stats["recent_tokens"]:
        stats_text += "\n<b>Tokens recientes:</b>\n"
        for token in stats["recent_tokens"][:5]:  # Limitamos a 5 para no hacer el mensaje demasiado largo
            status = "✅ Canjeado" if token["is_used"] else "⏳ Pendiente"
            stats_text += f"  • {token['tariff']}: {status}\n"
    
    await message.answer(
        stats_text,
        parse_mode="HTML",
        reply_markup=AdminKeyboardFactory.tariff_management()
    )


def register_tariff_handlers(dp, tokeneitor):
    """Registra los handlers relacionados con tarifas en el dispatcher."""
    # Comandos principales
    dp.message.register(
        lambda message: cmd_tariffs(message, tokeneitor),
        Command("tarifas")
    )
    dp.message.register(
        lambda message: cmd_tariffs(message, tokeneitor),
        F.text == "🏷️ Gestionar Tarifas"
    )
    
    # Flujo de creación de tarifas
    dp.message.register(cmd_new_tariff, F.text == "🆕 Nueva Tarifa")
    dp.message.register(process_tariff_name, TariffStates.waiting_for_name)
    dp.message.register(process_tariff_duration, TariffStates.waiting_for_duration)
    dp.message.register(process_tariff_price, TariffStates.waiting_for_price)
    dp.message.register(process_tariff_token_validity, TariffStates.waiting_for_token_validity)
    dp.message.register(
        lambda message, state: process_tariff_description(message, state, tokeneitor),
        TariffStates.waiting_for_description
    )
    
    # Generación de enlaces
    dp.message.register(
        lambda message: cmd_generate_link(message, tokeneitor),
        F.text == "🔗 Generar Enlace"
    )
    dp.callback_query.register(
        lambda callback_query: process_generate_token(callback_query, tokeneitor),
        lambda callback_query: callback_query.data.startswith("generate_token:")
    )
    
    # Estadísticas
    dp.message.register(
        lambda message: cmd_token_stats(message, tokeneitor),
        F.text == "📊 Estadísticas"
    )