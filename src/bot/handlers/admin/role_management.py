"""Handlers para la gestión de roles de usuarios."""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ...filters.role import IsAdminFilter, PermissionFilter
from ...services.role import RoleService, RoleType
from ...keyboards.keyboard_factory import KeyboardFactory

# Crear router
router = Router()

# Estados para FSM
class RoleManagementStates(StatesGroup):
    waiting_for_user_id = State()
    waiting_for_vip_duration = State()
    confirming_role_change = State()

@router.message(Command("roles"), IsAdminFilter())
async def cmd_role_management(message: Message):
    """Muestra el panel de gestión de roles."""
    text = (
        "👑 **Gestión de Roles**\n\n"
        "Desde aquí puedes gestionar los roles de los usuarios:\n"
        "• **Administradores**: Acceso completo al sistema\n"
        "• **VIP**: Acceso a contenido premium y canales exclusivos\n"
        "• **Free**: Usuarios gratuitos con acceso básico\n\n"
        "Selecciona una opción:"
    )
    
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="👥 Ver Usuarios por Rol", callback_data="roles:view_by_role")
    keyboard.button(text="🔍 Buscar Usuario", callback_data="roles:search_user")
    keyboard.button(text="👑 Gestionar Administradores", callback_data="roles:manage_admins")
    keyboard.button(text="💎 Gestionar VIP", callback_data="roles:manage_vip")
    keyboard.button(text="📊 Estadísticas de Roles", callback_data="roles:statistics")
    keyboard.button(text="⬅️ Volver al Panel Admin", callback_data="admin:main_menu")
    keyboard.adjust(1)
    
    await message.answer(
        text,
        parse_mode="Markdown",
        reply_markup=keyboard.as_markup()
    )

@router.callback_query(F.data == "roles:view_by_role")
async def cb_view_by_role(callback: CallbackQuery):
    """Muestra menú para ver usuarios por rol."""
    text = (
        "👥 **Ver Usuarios por Rol**\n\n"
        "Selecciona el tipo de rol que deseas consultar:"
    )
    
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="👑 Administradores", callback_data="roles:list_admins")
    keyboard.button(text="💎 Usuarios VIP", callback_data="roles:list_vip")
    keyboard.button(text="🆓 Usuarios Gratuitos", callback_data="roles:list_free")
    keyboard.button(text="⬅️ Volver", callback_data="roles:main_menu")
    keyboard.adjust(1)
    
    await callback.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboard.as_markup()
    )
    await callback.answer()

@router.callback_query(F.data.startswith("roles:list_"))
async def cb_list_users_by_role(callback: CallbackQuery):
    """Lista usuarios por rol específico."""
    role_type = callback.data.split("_")[1]
    
    # Mapear tipos
    role_map = {
        "admins": RoleType.ADMIN,
        "vip": RoleType.VIP,
        "free": RoleType.FREE
    }
    
    role = role_map.get(role_type, RoleType.FREE)
    role_service = callback.bot.role_service if hasattr(callback.bot, 'role_service') else RoleService()
    
    # Obtener sesión del contexto
    session = callback.bot.session if hasattr(callback.bot, 'session') else None
    
    if not session:
        await callback.answer("Error: No se pudo acceder a la base de datos", show_alert=True)
        return
    
    try:
        users = await role_service.get_users_by_role(session, role)
        
        if not users:
            text = f"📋 **Usuarios {role.title()}**\n\nNo hay usuarios con este rol."
        else:
            text = f"📋 **Usuarios {role.title()}** ({len(users)})\n\n"
            
            for i, user in enumerate(users[:10], 1):  # Limitar a 10 para no hacer el mensaje muy largo
                username = user.get("username", "Sin username")
                first_name = user.get("first_name", "Sin nombre")
                
                text += f"{i}. **{first_name}** (@{username})\n"
                text += f"   ID: `{user['id']}`\n"
                
                if role == RoleType.VIP and user.get("expires_at"):
                    text += f"   Expira: {user['expires_at'][:10]}\n"
                elif role == RoleType.ADMIN and user.get("source"):
                    text += f"   Fuente: {user['source']}\n"
                
                text += "\n"
            
            if len(users) > 10:
                text += f"... y {len(users) - 10} usuarios más.\n"
        
        keyboard = InlineKeyboardBuilder()
        keyboard.button(text="⬅️ Volver", callback_data="roles:view_by_role")
        
        await callback.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=keyboard.as_markup()
        )
        
    except Exception as e:
        logger.error(f"Error al listar usuarios por rol: {e}")
        await callback.answer("Error al obtener la lista de usuarios", show_alert=True)
    
    await callback.answer()

@router.callback_query(F.data == "roles:search_user")
async def cb_search_user(callback: CallbackQuery, state: FSMContext):
    """Inicia búsqueda de usuario para gestión de roles."""
    text = (
        "🔍 **Buscar Usuario**\n\n"
        "Envía el ID de Telegram del usuario que deseas gestionar.\n"
        "Ejemplo: `123456789`"
    )
    
    await callback.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=KeyboardFactory.back_button("roles:main_menu")
    )
    
    await state.set_state(RoleManagementStates.waiting_for_user_id)
    await callback.answer()

@router.message(RoleManagementStates.waiting_for_user_id)
async def process_user_search(message: Message, state: FSMContext):
    """Procesa la búsqueda de usuario."""
    try:
        target_user_id = int(message.text.strip())
    except ValueError:
        await message.answer(
            "❌ **Error**: Por favor, envía un ID de usuario válido (solo números).",
            parse_mode="Markdown"
        )
        return
    
    # Obtener información del usuario
    role_service = RoleService()
    session = message.bot.session if hasattr(message.bot, 'session') else None
    
    if not session:
        await message.answer("❌ Error: No se pudo acceder a la base de datos.")
        await state.clear()
        return
    
    try:
        # Obtener rol actual
        user_role = await role_service.get_user_role(session, target_user_id)
        permissions = await role_service.get_user_permissions(session, target_user_id)
        
        # Obtener datos del usuario si existe
        user = await role_service.get_by_id(session, target_user_id)
        
        if user:
            user_info = f"**{user.first_name}** (@{user.username or 'Sin username'})"
            if user.is_vip and user.vip_expires_at:
                user_info += f"\nVIP hasta: {user.vip_expires_at.strftime('%d/%m/%Y')}"
        else:
            user_info = f"Usuario ID: {target_user_id} (No registrado en el bot)"
        
        text = (
            f"👤 **Información del Usuario**\n\n"
            f"{user_info}\n"
            f"**Rol actual**: {user_role.upper()}\n\n"
            f"**Permisos principales**:\n"
            f"• Admin Panel: {'✅' if permissions.get('can_access_admin_panel') else '❌'}\n"
            f"• Canales VIP: {'✅' if permissions.get('can_access_vip_channels') else '❌'}\n"
            f"• Contenido VIP: {'✅' if permissions.get('can_access_vip_content') else '❌'}\n"
            f"• Gestionar Usuarios: {'✅' if permissions.get('can_manage_users') else '❌'}\n\n"
            f"¿Qué acción deseas realizar?"
        )
        
        # Crear teclado con opciones
        keyboard = InlineKeyboardBuilder()
        
        # Opciones según el rol actual
        if user_role != RoleType.ADMIN:
            keyboard.button(text="👑 Hacer Administrador", callback_data=f"roles:make_admin_{target_user_id}")
        else:
            keyboard.button(text="👤 Quitar Admin", callback_data=f"roles:remove_admin_{target_user_id}")
        
        if user_role != RoleType.VIP:
            keyboard.button(text="💎 Hacer VIP", callback_data=f"roles:make_vip_{target_user_id}")
        else:
            keyboard.button(text="🔄 Extender VIP", callback_data=f"roles:extend_vip_{target_user_id}")
            keyboard.button(text="❌ Quitar VIP", callback_data=f"roles:remove_vip_{target_user_id}")
        
        keyboard.button(text="🔍 Buscar Otro Usuario", callback_data="roles:search_user")
        keyboard.button(text="⬅️ Volver", callback_data="roles:main_menu")
        keyboard.adjust(1)
        
        await message.answer(
            text,
            parse_mode="Markdown",
            reply_markup=keyboard.as_markup()
        )
        
        # Guardar ID del usuario en el estado
        await state.update_data(target_user_id=target_user_id)
        await state.clear()
        
    except Exception as e:
        logger.error(f"Error al buscar usuario: {e}")
        await message.answer("❌ Error al buscar el usuario.")
        await state.clear()

@router.callback_query(F.data.startswith("roles:make_admin_"))
async def cb_make_admin(callback: CallbackQuery):
    """Otorga estado de administrador a un usuario."""
    target_user_id = int(callback.data.split("_")[2])
    admin_user_id = callback.from_user.id
    
    role_service = RoleService()
    session = callback.bot.session if hasattr(callback.bot, 'session') else None
    
    if not session:
        await callback.answer("Error: No se pudo acceder a la base de datos", show_alert=True)
        return
    
    try:
        success = await role_service.grant_admin_status(session, target_user_id, admin_user_id)
        
        if success:
            await callback.message.edit_text(
                f"✅ **Administrador Otorgado**\n\n"
                f"El usuario `{target_user_id}` ahora es administrador.\n"
                f"Tendrá acceso completo al panel de administración.",
                parse_mode="Markdown",
                reply_markup=KeyboardFactory.back_button("roles:main_menu")
            )
        else:
            await callback.answer("❌ No se pudo otorgar el estado de administrador", show_alert=True)
    
    except Exception as e:
        logger.error(f"Error al otorgar admin: {e}")
        await callback.answer("❌ Error al procesar la solicitud", show_alert=True)
    
    await callback.answer()

@router.callback_query(F.data.startswith("roles:make_vip_"))
async def cb_make_vip(callback: CallbackQuery, state: FSMContext):
    """Inicia proceso para otorgar estado VIP."""
    target_user_id = int(callback.data.split("_")[2])
    
    text = (
        f"💎 **Otorgar Estado VIP**\n\n"
        f"Usuario: `{target_user_id}`\n\n"
        f"¿Por cuántos días deseas otorgar el estado VIP?\n"
        f"Envía un número (ejemplo: 30, 90, 365) o 'permanente' para VIP sin expiración."
    )
    
    await callback.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=KeyboardFactory.back_button("roles:main_menu")
    )
    
    await state.update_data(target_user_id=target_user_id, action="grant_vip")
    await state.set_state(RoleManagementStates.waiting_for_vip_duration)
    await callback.answer()

@router.message(RoleManagementStates.waiting_for_vip_duration)
async def process_vip_duration(message: Message, state: FSMContext):
    """Procesa la duración del VIP."""
    data = await state.get_data()
    target_user_id = data.get("target_user_id")
    action = data.get("action")
    
    duration_days = None
    
    if message.text.lower() == "permanente":
        duration_days = None
        duration_text = "permanente"
    else:
        try:
            duration_days = int(message.text.strip())
            if duration_days <= 0:
                raise ValueError("Duración debe ser positiva")
            duration_text = f"{duration_days} días"
        except ValueError:
            await message.answer(
                "❌ **Error**: Por favor, envía un número válido de días o 'permanente'.",
                parse_mode="Markdown"
            )
            return
    
    # Confirmar acción
    text = (
        f"💎 **Confirmar Acción VIP**\n\n"
        f"Usuario: `{target_user_id}`\n"
        f"Acción: {'Otorgar' if action == 'grant_vip' else 'Extender'} VIP\n"
        f"Duración: {duration_text}\n\n"
        f"¿Confirmas esta acción?"
    )
    
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="✅ Confirmar", callback_data=f"roles:confirm_vip_{target_user_id}_{duration_days or 0}")
    keyboard.button(text="❌ Cancelar", callback_data="roles:main_menu")
    keyboard.adjust(1)
    
    await message.answer(
        text,
        parse_mode="Markdown",
        reply_markup=keyboard.as_markup()
    )
    
    await state.clear()

@router.callback_query(F.data.startswith("roles:confirm_vip_"))
async def cb_confirm_vip(callback: CallbackQuery):
    """Confirma y ejecuta la acción VIP."""
    parts = callback.data.split("_")
    target_user_id = int(parts[2])
    duration_days = int(parts[3]) if parts[3] != "0" else None
    
    admin_user_id = callback.from_user.id
    role_service = RoleService()
    session = callback.bot.session if hasattr(callback.bot, 'session') else None
    
    if not session:
        await callback.answer("Error: No se pudo acceder a la base de datos", show_alert=True)
        return
    
    try:
        success = await role_service.grant_vip_status(
            session, target_user_id, duration_days, admin_user_id
        )
        
        if success:
            duration_text = f"{duration_days} días" if duration_days else "permanente"
            await callback.message.edit_text(
                f"✅ **VIP Otorgado**\n\n"
                f"El usuario `{target_user_id}` ahora es VIP por {duration_text}.\n"
                f"Tendrá acceso a contenido y canales exclusivos.",
                parse_mode="Markdown",
                reply_markup=KeyboardFactory.back_button("roles:main_menu")
            )
        else:
            await callback.answer("❌ No se pudo otorgar el estado VIP", show_alert=True)
    
    except Exception as e:
        logger.error(f"Error al otorgar VIP: {e}")
        await callback.answer("❌ Error al procesar la solicitud", show_alert=True)
    
    await callback.answer()

@router.callback_query(F.data.startswith("roles:remove_vip_"))
async def cb_remove_vip(callback: CallbackQuery):
    """Revoca estado VIP de un usuario."""
    target_user_id = int(callback.data.split("_")[2])
    admin_user_id = callback.from_user.id
    
    role_service = RoleService()
    session = callback.bot.session if hasattr(callback.bot, 'session') else None
    
    if not session:
        await callback.answer("Error: No se pudo acceder a la base de datos", show_alert=True)
        return
    
    try:
        success = await role_service.revoke_vip_status(session, target_user_id, admin_user_id)
        
        if success:
            await callback.message.edit_text(
                f"❌ **VIP Revocado**\n\n"
                f"El usuario `{target_user_id}` ya no es VIP.\n"
                f"Perderá acceso a contenido y canales exclusivos.",
                parse_mode="Markdown",
                reply_markup=KeyboardFactory.back_button("roles:main_menu")
            )
        else:
            await callback.answer("❌ No se pudo revocar el estado VIP", show_alert=True)
    
    except Exception as e:
        logger.error(f"Error al revocar VIP: {e}")
        await callback.answer("❌ Error al procesar la solicitud", show_alert=True)
    
    await callback.answer()

@router.callback_query(F.data == "roles:statistics")
async def cb_role_statistics(callback: CallbackQuery):
    """Muestra estadísticas de roles."""
    role_service = RoleService()
    session = callback.bot.session if hasattr(callback.bot, 'session') else None
    
    if not session:
        await callback.answer("Error: No se pudo acceder a la base de datos", show_alert=True)
        return
    
    try:
        stats = await role_service.get_role_statistics(session)
        
        text = (
            f"📊 **Estadísticas de Roles**\n\n"
            f"**Total de usuarios**: {stats['total_users']}\n\n"
            f"👑 **Administradores**: {stats['admins']} ({stats['admin_percentage']}%)\n"
            f"💎 **Usuarios VIP**: {stats['vip_users']} ({stats['vip_percentage']}%)\n"
            f"🆓 **Usuarios Gratuitos**: {stats['free_users']} ({stats['free_percentage']}%)\n\n"
            f"*Estadísticas actualizadas en tiempo real*"
        )
        
        await callback.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=KeyboardFactory.back_button("roles:main_menu")
        )
        
    except Exception as e:
        logger.error(f"Error al obtener estadísticas: {e}")
        await callback.answer("❌ Error al obtener estadísticas", show_alert=True)
    
    await callback.answer()

@router.callback_query(F.data == "roles:main_menu")
async def cb_back_to_roles_menu(callback: CallbackQuery):
    """Vuelve al menú principal de roles."""
    await cmd_role_management(callback.message)
    await callback.answer()

def register_role_management_handlers(dp):
    """Registra los handlers de gestión de roles."""
    dp.include_router(router)