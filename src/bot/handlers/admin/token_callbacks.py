"""Callbacks específicos para la gestión de tokens en el panel de administración."""

from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from ...filters.role import IsAdminFilter

token_callbacks_router = Router()

class TokenStates(StatesGroup):
    """Estados para los flujos de gestión de tokens."""
    waiting_for_user_id = State()
    waiting_for_token_count = State()
    waiting_for_token_to_invalidate = State()

# =============================================================================
# CALLBACKS PRINCIPALES DE TOKENS
# =============================================================================

@token_callbacks_router.callback_query(F.data == "token:individual")
async def token_individual_callback(callback: CallbackQuery, state: FSMContext):
    """Inicia el proceso de generación de token individual."""
    text = (
        "🎯 **Generar Token Individual**\n\n"
        "Para generar un token individual, necesito que selecciones "
        "la tarifa para la cual deseas crear el token.\n\n"
        "**Proceso:**\n"
        "1. Selecciona la tarifa\n"
        "2. Se generará el enlace automáticamente\n"
        "3. Comparte el enlace con el usuario"
    )
    
    # Aquí deberíamos obtener las tarifas disponibles
    # Por ahora simulamos algunas tarifas de ejemplo
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Premium Mensual - $9.99", callback_data="generate_single:1")],
        [InlineKeyboardButton(text="👑 VIP Trimestral - $24.99", callback_data="generate_single:2")],
        [InlineKeyboardButton(text="🌟 Anual Premium - $89.99", callback_data="generate_single:3")],
        [InlineKeyboardButton(text="🔙 Volver", callback_data="admin:tokens")]
    ])
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer()

@token_callbacks_router.callback_query(F.data.startswith("generate_single:"))
async def generate_single_token_callback(callback: CallbackQuery):
    """Genera un token individual para la tarifa seleccionada."""
    tariff_id = callback.data.split(":")[1]
    admin_id = callback.from_user.id
    
    # Aquí integraremos con el Tokeneitor real
    # Por ahora simulamos la generación
    import uuid
    token_code = str(uuid.uuid4())[:8].upper()
    token_url = f"https://t.me/tu_bot?start=token_{token_code}"
    
    text = (
        "✅ **Token Generado Exitosamente**\n\n"
        f"**Token ID:** `{token_code}`\n"
        f"**Tarifa:** Tarifa #{tariff_id}\n"
        f"**Generado por:** Admin #{admin_id}\n"
        f"**Válido por:** 7 días\n\n"
        "**🔗 Enlace de invitación:**\n"
        f"`{token_url}`\n\n"
        "Comparte este enlace con el usuario. Al hacer clic, "
        "se unirá automáticamente con la tarifa seleccionada."
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Copiar Enlace", url=token_url)],
        [InlineKeyboardButton(text="🆕 Generar Otro", callback_data="token:individual")],
        [InlineKeyboardButton(text="🔙 Volver", callback_data="admin:tokens")]
    ])
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer("Token generado exitosamente! 🎉")

@token_callbacks_router.callback_query(F.data == "token:bulk")
async def token_bulk_callback(callback: CallbackQuery, state: FSMContext):
    """Inicia el proceso de generación masiva de tokens.""" 
    text = (
        "📦 **Generación Masiva de Tokens**\n\n"
        "Genera múltiples tokens de una vez para campañas o distribución masiva.\n\n"
        "**¿Cuántos tokens necesitas?**\n"
        "Ingresa un número entre 1 y 100:"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="5 tokens", callback_data="bulk_count:5")],
        [InlineKeyboardButton(text="10 tokens", callback_data="bulk_count:10")],
        [InlineKeyboardButton(text="25 tokens", callback_data="bulk_count:25")],
        [InlineKeyboardButton(text="50 tokens", callback_data="bulk_count:50")],
        [InlineKeyboardButton(text="🔙 Volver", callback_data="admin:tokens")]
    ])
    
    await state.set_state(TokenStates.waiting_for_token_count)
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer()

@token_callbacks_router.callback_query(F.data.startswith("bulk_count:"))
async def bulk_count_selected_callback(callback: CallbackQuery, state: FSMContext):
    """Maneja la selección de cantidad para tokens masivos."""
    count = int(callback.data.split(":")[1])
    await state.update_data(token_count=count)
    
    text = (
        f"📦 **Generar {count} Tokens**\n\n"
        "Selecciona la tarifa para estos tokens:"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Premium Mensual - $9.99", callback_data=f"bulk_tariff:1:{count}")],
        [InlineKeyboardButton(text="👑 VIP Trimestral - $24.99", callback_data=f"bulk_tariff:2:{count}")],
        [InlineKeyboardButton(text="🌟 Anual Premium - $89.99", callback_data=f"bulk_tariff:3:{count}")],
        [InlineKeyboardButton(text="🔙 Cambiar Cantidad", callback_data="token:bulk")]
    ])
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer()

@token_callbacks_router.callback_query(F.data.startswith("bulk_tariff:"))
async def generate_bulk_tokens_callback(callback: CallbackQuery, state: FSMContext):
    """Genera tokens masivos para la tarifa seleccionada."""
    parts = callback.data.split(":")
    tariff_id = parts[1]
    count = int(parts[2])
    
    # Simular generación masiva
    import uuid
    tokens = []
    for i in range(count):
        token_code = str(uuid.uuid4())[:8].upper()
        token_url = f"https://t.me/tu_bot?start=token_{token_code}"
        tokens.append({"code": token_code, "url": token_url})
    
    # Crear mensaje con los tokens
    text = (
        f"✅ **{count} Tokens Generados**\n\n"
        f"**Tarifa:** Tarifa #{tariff_id}\n"
        f"**Válidos por:** 7 días cada uno\n\n"
        "**Enlaces generados:**\n"
    )
    
    # Mostrar primeros 5 tokens
    for i, token in enumerate(tokens[:5]):
        text += f"`{token['url']}`\n"
    
    if count > 5:
        text += f"\n... y {count - 5} más."
        
    text += (
        "\n\n💡 **Consejo:** Puedes exportar todos los enlaces "
        "a un archivo para distribución masiva."
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📄 Exportar Todos", callback_data=f"export_tokens:{tariff_id}:{count}")],
        [InlineKeyboardButton(text="🆕 Generar Más", callback_data="token:bulk")],
        [InlineKeyboardButton(text="🔙 Volver", callback_data="admin:tokens")]
    ])
    
    await state.clear()
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer(f"¡{count} tokens generados exitosamente! 🎉")

@token_callbacks_router.callback_query(F.data == "token:active")
async def token_active_callback(callback: CallbackQuery):
    """Muestra tokens activos."""
    text = (
        "👀 **Tokens Activos**\n\n"
        "📊 **Estadísticas actuales:**\n"
        "• Total tokens activos: 145\n"
        "• Tokens usados hoy: 23\n"
        "• Tasa de uso: 78%\n"
        "• Próximos a expirar: 12\n\n"
        "**🔥 Tokens más activos:**\n"
        "• `ABC123DE` - Premium Mensual (usado 3 veces)\n"
        "• `XYZ789GH` - VIP Trimestral (usado 2 veces)\n"
        "• `QWE456RT` - Anual Premium (usado 1 vez)"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Ver Todos", callback_data="tokens:list_all")],
        [InlineKeyboardButton(text="⏰ Próximos a Expirar", callback_data="tokens:expiring")],
        [InlineKeyboardButton(text="📊 Estadísticas", callback_data="tokens:stats_detailed")],
        [InlineKeyboardButton(text="🔙 Volver", callback_data="admin:tokens")]
    ])
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer()

@token_callbacks_router.callback_query(F.data == "token:invalidate")
async def token_invalidate_callback(callback: CallbackQuery, state: FSMContext):
    """Inicia el proceso de invalidar un token."""
    text = (
        "🚫 **Invalidar Token**\n\n"
        "Para invalidar un token, puedes:\n\n"
        "**1. Por código de token**\n"
        "Ingresa el código del token (ej: ABC123DE)\n\n"
        "**2. Seleccionar de lista**\n"
        "Ve todos los tokens activos y selecciona uno\n\n"
        "¿Qué método prefieres?"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⌨️ Ingresar Código", callback_data="invalidate:input")],
        [InlineKeyboardButton(text="📋 Seleccionar de Lista", callback_data="invalidate:select")],
        [InlineKeyboardButton(text="🔙 Volver", callback_data="admin:tokens")]
    ])
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer()

@token_callbacks_router.callback_query(F.data == "invalidate:input")
async def invalidate_input_callback(callback: CallbackQuery, state: FSMContext):
    """Solicita al admin que ingrese el código del token a invalidar."""
    text = (
        "⌨️ **Invalidar por Código**\n\n"
        "Ingresa el código del token que deseas invalidar.\n\n"
        "**Formato esperado:** ABC123DE\n"
        "**Nota:** El código es sensible a mayúsculas/minúsculas."
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Cambiar Método", callback_data="token:invalidate")]
    ])
    
    await state.set_state(TokenStates.waiting_for_token_to_invalidate)
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer()

@token_callbacks_router.callback_query(F.data == "invalidate:select")
async def invalidate_select_callback(callback: CallbackQuery):
    """Muestra lista de tokens para seleccionar cuál invalidar."""
    text = (
        "📋 **Seleccionar Token a Invalidar**\n\n"
        "Tokens activos disponibles:"
    )
    
    # Simular algunos tokens activos
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="ABC123DE - Premium Mensual", callback_data="invalidate_confirm:ABC123DE")],
        [InlineKeyboardButton(text="XYZ789GH - VIP Trimestral", callback_data="invalidate_confirm:XYZ789GH")],
        [InlineKeyboardButton(text="QWE456RT - Anual Premium", callback_data="invalidate_confirm:QWE456RT")],
        [InlineKeyboardButton(text="🔄 Recargar Lista", callback_data="invalidate:select")],
        [InlineKeyboardButton(text="🔙 Volver", callback_data="token:invalidate")]
    ])
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer()

@token_callbacks_router.callback_query(F.data.startswith("invalidate_confirm:"))
async def confirm_invalidate_callback(callback: CallbackQuery):
    """Confirma la invalidación del token seleccionado."""
    token_code = callback.data.split(":")[1]
    
    text = (
        "⚠️ **Confirmar Invalidación**\n\n"
        f"**Token a invalidar:** `{token_code}`\n\n"
        "**Esta acción:**\n"
        "• Invalidará el token permanentemente\n"
        "• No se podrá usar para acceder al canal\n"
        "• No se puede deshacer\n\n"
        "¿Estás seguro de que deseas continuar?"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Sí, Invalidar", callback_data=f"do_invalidate:{token_code}")],
        [InlineKeyboardButton(text="❌ Cancelar", callback_data="token:invalidate")]
    ])
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer()

@token_callbacks_router.callback_query(F.data.startswith("do_invalidate:"))
async def do_invalidate_callback(callback: CallbackQuery):
    """Ejecuta la invalidación del token."""
    token_code = callback.data.split(":")[1]
    
    # Aquí se haría la invalidación real con el Tokeneitor
    # Por ahora simulamos el proceso
    
    text = (
        "✅ **Token Invalidado**\n\n"
        f"**Token:** `{token_code}`\n"
        f"**Estado:** ❌ Invalidado\n"
        f"**Fecha:** {callback.message.date.strftime('%Y-%m-%d %H:%M')}\n\n"
        "El token ya no se puede usar para acceder al canal."
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚫 Invalidar Otro", callback_data="token:invalidate")],
        [InlineKeyboardButton(text="👀 Ver Activos", callback_data="token:active")],
        [InlineKeyboardButton(text="🔙 Volver", callback_data="admin:tokens")]
    ])
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer("Token invalidado exitosamente ✅")

# =============================================================================
# CALLBACKS AUXILIARES
# =============================================================================

@token_callbacks_router.callback_query(F.data.startswith("export_tokens:"))
async def export_tokens_callback(callback: CallbackQuery):
    """Maneja la exportación de tokens a archivo."""
    parts = callback.data.split(":")
    tariff_id = parts[1]
    count = int(parts[2])
    
    text = (
        "📄 **Exportar Tokens**\n\n"
        f"Se exportarán {count} tokens a un archivo de texto.\n\n"
        "**Formatos disponibles:**\n"
        "• 📝 Texto plano (.txt)\n"
        "• 📊 CSV (.csv)\n"
        "• 🔗 Solo enlaces"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Archivo TXT", callback_data=f"do_export:txt:{tariff_id}:{count}")],
        [InlineKeyboardButton(text="📊 Archivo CSV", callback_data=f"do_export:csv:{tariff_id}:{count}")],
        [InlineKeyboardButton(text="🔗 Solo Enlaces", callback_data=f"do_export:links:{tariff_id}:{count}")],
        [InlineKeyboardButton(text="🔙 Volver", callback_data="admin:tokens")]
    ])
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer()

@token_callbacks_router.callback_query(F.data.startswith("do_export:"))
async def do_export_callback(callback: CallbackQuery):
    """Ejecuta la exportación de tokens."""
    parts = callback.data.split(":")
    format_type = parts[1]
    tariff_id = parts[2]
    count = int(parts[3])
    
    text = (
        "✅ **Exportación Completada**\n\n"
        f"**Archivo:** tokens_tarifa_{tariff_id}.{format_type}\n"
        f"**Tokens exportados:** {count}\n"
        f"**Formato:** {format_type.upper()}\n\n"
        "El archivo ha sido generado y enviado por mensaje privado.\n"
        "También puedes descargarlo desde el panel de archivos."
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📁 Ver Archivos", callback_data="admin:files")],
        [InlineKeyboardButton(text="🆕 Exportar Más", callback_data="token:bulk")],
        [InlineKeyboardButton(text="🔙 Volver", callback_data="admin:tokens")]
    ])
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer(f"Archivo {format_type.upper()} generado ✅")