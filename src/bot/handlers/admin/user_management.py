"""Handler para gestión completa de usuarios."""

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from datetime import datetime

from ...keyboards.admin.main_kb import get_user_management_keyboard
from ...filters.role import IsAdminFilter
from src.modules.admin.service import AdminService
from src.core.event_bus import EventBus

user_management_router = Router()

class UserManagementStates(StatesGroup):
    waiting_for_search = State()
    waiting_for_user_action = State()
    waiting_for_ban_reason = State()
    waiting_for_vip_duration = State()

@user_management_router.callback_query(F.data == "admin:users")
async def show_user_management(callback_query: CallbackQuery, session: AsyncSession):
    """Muestra el panel principal de gestión de usuarios."""
    try:
        event_bus = EventBus()
        admin_service = AdminService(event_bus)
        
        # Obtener estadísticas de usuarios
        user_stats = await admin_service.get_user_statistics()
        
        text = "👥 **GESTIÓN DE USUARIOS**\n\n"
        text += "📊 **Estadísticas Actuales:**\n"
        text += f"• Total de Usuarios: {user_stats['total_users']:,}\n"
        text += f"• Usuarios VIP: {user_stats['vip_users']:,}\n"
        text += f"• Usuarios Free: {user_stats['free_users']:,}\n"
        text += f"• Usuarios Activos (7 días): {user_stats['active_users']:,}\n"
        text += f"• Nuevos Hoy: {user_stats['today_new_users']:,}\n"
        text += f"• Usuarios Baneados: {user_stats['banned_users']:,}\n\n"
        
        text += "🔍 **Funciones Disponibles:**\n"
        text += "• Buscar usuarios por nombre/username\n"
        text += "• Ver detalles completos de cualquier usuario\n"
        text += "• Modificar status VIP (activar/desactivar)\n"
        text += "• Banear/desbanear usuarios problemáticos\n"
        text += "• Ver historial de suscripciones\n"
        text += "• Estadísticas de engagement por usuario\n\n"
        
        text += "📈 **Métricas de Engagement:**\n"
        text += f"• Tasa de Conversión VIP: {(user_stats['vip_users'] / max(user_stats['total_users'], 1) * 100):.1f}%\n"
        text += f"• Tasa de Actividad: {(user_stats['active_users'] / max(user_stats['total_users'], 1) * 100):.1f}%\n"
        text += f"• Crecimiento Hoy: +{user_stats['today_new_users']} usuarios\n"
        
        # Crear keyboard de gestión de usuarios
        keyboard = [
            [InlineKeyboardButton(text="🔍 Buscar Usuario", callback_data="user_mgmt:search")],
            [InlineKeyboardButton(text="👑 Lista VIP", callback_data="user_mgmt:list_vip"),
             InlineKeyboardButton(text="🚫 Lista Baneados", callback_data="user_mgmt:list_banned")],
            [InlineKeyboardButton(text="📊 Top Usuarios", callback_data="user_mgmt:top_users"),
             InlineKeyboardButton(text="📈 Métricas Detalladas", callback_data="user_mgmt:detailed_metrics")],
            [InlineKeyboardButton(text="⚡ Acciones Rápidas", callback_data="user_mgmt:quick_actions")],
            [InlineKeyboardButton(text="⬅️ Panel Admin", callback_data="admin:main")]
        ]
        
        await callback_query.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
        await callback_query.answer()
        
    except Exception as e:
        await callback_query.answer(f"Error al cargar gestión de usuarios: {str(e)}")

@user_management_router.callback_query(F.data == "user_mgmt:search")
async def start_user_search(callback_query: CallbackQuery, state: FSMContext):
    """Inicia el proceso de búsqueda de usuarios."""
    try:
        text = "🔍 **BÚSQUEDA DE USUARIOS**\n\n"
        text += "Ingresa el término de búsqueda:\n\n"
        text += "🎯 **Puedes buscar por:**\n"
        text += "• Nombre de usuario (@usuario o usuario)\n"
        text += "• Nombre completo\n"
        text += "• ID de usuario (número)\n"
        text += "• Parte del nombre\n\n"
        text += "💡 **Ejemplos:**\n"
        text += "• `@diana_user`\n"
        text += "• `María García`\n"
        text += "• `12345678`\n"
        text += "• `carlos`\n\n"
        text += "Escribe el término de búsqueda:"
        
        await state.set_state(UserManagementStates.waiting_for_search)
        
        keyboard = [
            [InlineKeyboardButton(text="❌ Cancelar", callback_data="admin:users")]
        ]
        
        await callback_query.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
        await callback_query.answer()
        
    except Exception as e:
        await callback_query.answer(f"Error al iniciar búsqueda: {str(e)}")

@user_management_router.message(UserManagementStates.waiting_for_search)
async def process_user_search(message: Message, state: FSMContext, session: AsyncSession):
    """Procesa la búsqueda de usuarios."""
    try:
        search_term = message.text.strip()
        
        event_bus = EventBus()
        admin_service = AdminService(event_bus)
        
        # Buscar usuarios
        users = await admin_service.search_users(search_term, limit=20)
        
        if not users:
            await message.answer(
                f"🚫 **No se encontraron usuarios**\n\n"
                f"No hay usuarios que coincidan con: `{search_term}`\n\n"
                f"💡 **Sugerencias:**\n"
                f"• Verifica la ortografía\n"
                f"• Prueba con menos caracteres\n"
                f"• Usa solo el nombre o username\n\n"
                f"Intenta con otro término:",
                parse_mode="Markdown"
            )
            return
        
        # Mostrar resultados
        text = f"🔍 **RESULTADOS DE BÚSQUEDA**\n\n"
        text += f"Encontrados {len(users)} usuario(s) para: `{search_term}`\n\n"
        
        keyboard = []
        for user in users:
            status_icons = []
            if user["is_vip"]:
                status_icons.append("👑")
            if user["is_admin"]:
                status_icons.append("⚡")
            if user["is_banned"]:
                status_icons.append("🚫")
            
            status_text = "".join(status_icons) if status_icons else "👤"
            
            user_display = f"{user['first_name']}"
            if user.get("last_name"):
                user_display += f" {user['last_name']}"
            if user.get("username"):
                user_display += f" (@{user['username']})"
            
            text += f"{status_text} **{user_display}**\n"
            text += f"   ID: `{user['id']}`\n"
            
            # Última actividad
            if user.get("last_activity_at"):
                last_activity = user["last_activity_at"]
                if isinstance(last_activity, str):
                    text += f"   Última actividad: {last_activity[:10]}\n"
                else:
                    text += f"   Última actividad: {last_activity.strftime('%d/%m/%Y')}\n"
            
            text += "\n"
            
            # Agregar botón para ver detalles
            keyboard.append([
                InlineKeyboardButton(
                    text=f"{status_text} {user_display[:30]}...",
                    callback_data=f"user_mgmt:details:{user['id']}"
                )
            ])
        
        # Limitar a 10 botones para evitar problemas
        keyboard = keyboard[:10]
        
        keyboard.append([InlineKeyboardButton(text="🔍 Nueva Búsqueda", callback_data="user_mgmt:search")])
        keyboard.append([InlineKeyboardButton(text="⬅️ Volver", callback_data="admin:users")])
        
        await state.clear()
        await message.answer(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
        
    except Exception as e:
        await message.answer(f"Error en búsqueda: {str(e)}")
        await state.clear()

@user_management_router.callback_query(F.data.startswith("user_mgmt:details:"))
async def show_user_details(callback_query: CallbackQuery, session: AsyncSession):
    """Muestra detalles completos de un usuario."""
    try:
        user_id = int(callback_query.data.split(":")[-1])
        
        event_bus = EventBus()
        admin_service = AdminService(event_bus)
        
        # Obtener detalles del usuario
        result = await admin_service.get_user_details(user_id)
        
        if not result["success"]:
            await callback_query.answer(f"❌ {result['error']}")
            return
        
        user = result["data"]
        
        # Construir mensaje de detalles
        text = f"👤 **DETALLES DE USUARIO**\n\n"
        
        # Información básica
        text += f"🆔 **ID:** `{user['id']}`\n"
        text += f"📝 **Nombre:** {user['first_name']}"
        if user.get("last_name"):
            text += f" {user['last_name']}"
        text += "\n"
        
        if user.get("username"):
            text += f"👤 **Username:** @{user['username']}\n"
        
        if user.get("language_code"):
            text += f"🌐 **Idioma:** {user['language_code'].upper()}\n"
        
        # Status
        text += f"\n🏷️ **Estado:**\n"
        if user["is_admin"]:
            text += "⚡ Administrador\n"
        if user["is_vip"]:
            text += "👑 Usuario VIP"
            if user.get("vip_expires_at"):
                expires = user["vip_expires_at"]
                if isinstance(expires, str):
                    text += f" (expira: {expires[:10]})"
                else:
                    text += f" (expira: {expires.strftime('%d/%m/%Y')})"
            text += "\n"
        else:
            text += "🆓 Usuario Free\n"
        
        if user["is_banned"]:
            text += "🚫 Usuario Baneado\n"
        elif user["is_active"]:
            text += "✅ Usuario Activo\n"
        else:
            text += "😴 Usuario Inactivo\n"
        
        # Estadísticas
        text += f"\n📊 **Estadísticas:**\n"
        text += f"• Nivel: {user['level']}\n"
        text += f"• Experiencia: {user['experience_points']} XP\n"
        text += f"• Mensajes: {user['messages_count']}\n"
        text += f"• Reacciones: {user['reactions_count']}\n"
        
        # Puntos (Besitos)
        if user.get("points"):
            text += f"• Besitos Actuales: {user['points']['current']:.1f}\n"
            text += f"• Besitos Ganados: {user['points']['total_earned']:.1f}\n"
            text += f"• Besitos Gastados: {user['points']['total_spent']:.1f}\n"
        
        # Gamificación
        text += f"\n🎮 **Gamificación:**\n"
        text += f"• Logros: {user['achievements_count']}\n"
        text += f"• Misiones Completadas: {user['missions_completed']}\n"
        text += f"• Canales: {user['channels_count']}\n"
        
        # Suscripciones
        if user['tokens_used'] > 0:
            text += f"\n💎 **Historial de Suscripciones:**\n"
            text += f"• Tokens Canjeados: {user['tokens_used']}\n"
            
            # Mostrar últimas suscripciones
            if user.get("subscription_history"):
                text += "• Últimas suscripciones:\n"
                for sub in user["subscription_history"][-3:]:  # Últimas 3
                    used_date = sub["used_at"]
                    if isinstance(used_date, str):
                        date_str = used_date[:10]
                    else:
                        date_str = used_date.strftime('%d/%m/%Y')
                    text += f"  - {sub['tariff_name']} (${sub['price']:.2f}) - {date_str}\n"
        
        # Fechas
        text += f"\n📅 **Fechas:**\n"
        created_date = user["created_at"]
        if isinstance(created_date, str):
            text += f"• Registro: {created_date[:10]}\n"
        else:
            text += f"• Registro: {created_date.strftime('%d/%m/%Y')}\n"
        
        if user.get("last_activity_at"):
            last_activity = user["last_activity_at"]
            if isinstance(last_activity, str):
                text += f"• Última actividad: {last_activity[:10]}\n"
            else:
                text += f"• Última actividad: {last_activity.strftime('%d/%m/%Y %H:%M')}\n"
        
        # Crear keyboard de acciones
        keyboard = []
        
        # Primera fila - Estado VIP
        if user["is_vip"]:
            keyboard.append([InlineKeyboardButton(text="👑➡️🆓 Quitar VIP", callback_data=f"user_action:remove_vip:{user_id}")])
        else:
            keyboard.append([InlineKeyboardButton(text="🆓➡️👑 Hacer VIP", callback_data=f"user_action:make_vip:{user_id}")])
        
        # Segunda fila - Ban/Unban
        if user["is_banned"]:
            keyboard.append([InlineKeyboardButton(text="🚫➡️✅ Desbanear", callback_data=f"user_action:unban:{user_id}")])
        else:
            keyboard.append([InlineKeyboardButton(text="✅➡️🚫 Banear", callback_data=f"user_action:ban:{user_id}")])
        
        # Tercera fila - Acciones adicionales
        keyboard.append([
            InlineKeyboardButton(text="📊 Ver Actividad", callback_data=f"user_action:activity:{user_id}"),
            InlineKeyboardButton(text="💰 Historial Pagos", callback_data=f"user_action:payments:{user_id}")
        ])
        
        # Cuarta fila - Navegación
        keyboard.append([
            InlineKeyboardButton(text="🔄 Actualizar", callback_data=f"user_mgmt:details:{user_id}"),
            InlineKeyboardButton(text="⬅️ Volver", callback_data="admin:users")
        ])
        
        await callback_query.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
        await callback_query.answer()
        
    except Exception as e:
        await callback_query.answer(f"Error al mostrar detalles: {str(e)}")

@user_management_router.callback_query(F.data.startswith("user_action:"))
async def handle_user_actions(callback_query: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Maneja las acciones sobre usuarios."""
    try:
        data_parts = callback_query.data.split(":")
        action = data_parts[1]
        user_id = int(data_parts[2])
        
        event_bus = EventBus()
        admin_service = AdminService(event_bus)
        admin_id = callback_query.from_user.id
        
        if action == "remove_vip":
            # Quitar VIP
            result = await admin_service.set_user_vip_status(
                user_id=user_id,
                is_vip=False,
                admin_id=admin_id
            )
            
            if result["success"]:
                await callback_query.answer("✅ Status VIP removido exitosamente")
                # Actualizar vista
                await show_user_details(callback_query, session)
            else:
                await callback_query.answer(f"❌ Error: {result['error']}")
                
        elif action == "make_vip":
            # Hacer VIP - pedir duración
            text = f"👑 **ACTIVAR VIP**\n\n"
            text += f"Usuario ID: `{user_id}`\n\n"
            text += f"Ingresa la duración en días para el acceso VIP:\n\n"
            text += f"💡 **Opciones comunes:**\n"
            text += f"• 7 días (1 semana)\n"
            text += f"• 30 días (1 mes)\n"
            text += f"• 90 días (3 meses)\n"
            text += f"• 365 días (1 año)\n\n"
            text += f"Escribe el número de días:"
            
            await state.update_data(action="make_vip", user_id=user_id)
            await state.set_state(UserManagementStates.waiting_for_vip_duration)
            
            keyboard = [
                [InlineKeyboardButton(text="7 días", callback_data="vip_duration:7"),
                 InlineKeyboardButton(text="30 días", callback_data="vip_duration:30")],
                [InlineKeyboardButton(text="90 días", callback_data="vip_duration:90"),
                 InlineKeyboardButton(text="365 días", callback_data="vip_duration:365")],
                [InlineKeyboardButton(text="❌ Cancelar", callback_data=f"user_mgmt:details:{user_id}")]
            ]
            
            await callback_query.message.edit_text(
                text,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
            )
            await callback_query.answer()
            
        elif action == "ban":
            # Banear - pedir razón
            text = f"🚫 **BANEAR USUARIO**\n\n"
            text += f"Usuario ID: `{user_id}`\n\n"
            text += f"Ingresa la razón del ban (opcional):\n\n"
            text += f"💡 **Razones comunes:**\n"
            text += f"• Spam\n"
            text += f"• Contenido inapropiado\n"
            text += f"• Violación de términos\n"
            text += f"• Comportamiento abusivo\n\n"
            text += f"Escribe la razón o /skip para continuar sin razón:"
            
            await state.update_data(action="ban", user_id=user_id)
            await state.set_state(UserManagementStates.waiting_for_ban_reason)
            
            keyboard = [
                [InlineKeyboardButton(text="Spam", callback_data="ban_reason:Spam"),
                 InlineKeyboardButton(text="Contenido inapropiado", callback_data="ban_reason:Contenido inapropiado")],
                [InlineKeyboardButton(text="Violación términos", callback_data="ban_reason:Violación de términos"),
                 InlineKeyboardButton(text="Sin razón", callback_data="ban_reason:")],
                [InlineKeyboardButton(text="❌ Cancelar", callback_data=f"user_mgmt:details:{user_id}")]
            ]
            
            await callback_query.message.edit_text(
                text,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
            )
            await callback_query.answer()
            
        elif action == "unban":
            # Desbanear
            result = await admin_service.unban_user(
                user_id=user_id,
                admin_id=admin_id
            )
            
            if result["success"]:
                await callback_query.answer("✅ Usuario desbaneado exitosamente")
                # Actualizar vista
                await show_user_details(callback_query, session)
            else:
                await callback_query.answer(f"❌ Error: {result['error']}")
                
        elif action == "activity":
            # Ver actividad del usuario
            await show_user_activity(callback_query, user_id, session)
            
        elif action == "payments":
            # Ver historial de pagos
            await show_user_payment_history(callback_query, user_id, session)
            
    except Exception as e:
        await callback_query.answer(f"Error en acción: {str(e)}")

@user_management_router.callback_query(F.data.startswith("vip_duration:"))
async def handle_vip_duration(callback_query: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Maneja la selección de duración VIP."""
    try:
        duration_days = int(callback_query.data.split(":")[-1])
        data = await state.get_data()
        user_id = data["user_id"]
        admin_id = callback_query.from_user.id
        
        event_bus = EventBus()
        admin_service = AdminService(event_bus)
        
        result = await admin_service.set_user_vip_status(
            user_id=user_id,
            is_vip=True,
            duration_days=duration_days,
            admin_id=admin_id
        )
        
        await state.clear()
        
        if result["success"]:
            await callback_query.answer(f"✅ Usuario VIP por {duration_days} días")
            # Actualizar vista
            await show_user_details(callback_query, session)
        else:
            await callback_query.answer(f"❌ Error: {result['error']}")
            
    except Exception as e:
        await callback_query.answer(f"Error al activar VIP: {str(e)}")

@user_management_router.callback_query(F.data.startswith("ban_reason:"))
async def handle_ban_reason(callback_query: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Maneja la selección de razón de ban."""
    try:
        reason = callback_query.data.split(":", 1)[-1]  # Puede contener ":"
        data = await state.get_data()
        user_id = data["user_id"]
        admin_id = callback_query.from_user.id
        
        event_bus = EventBus()
        admin_service = AdminService(event_bus)
        
        result = await admin_service.ban_user(
            user_id=user_id,
            admin_id=admin_id,
            reason=reason if reason else None
        )
        
        await state.clear()
        
        if result["success"]:
            reason_text = f" (Razón: {reason})" if reason else ""
            await callback_query.answer(f"✅ Usuario baneado{reason_text}")
            # Actualizar vista
            await show_user_details(callback_query, session)
        else:
            await callback_query.answer(f"❌ Error: {result['error']}")
            
    except Exception as e:
        await callback_query.answer(f"Error al banear: {str(e)}")

@user_management_router.message(UserManagementStates.waiting_for_vip_duration)
async def process_vip_duration_text(message: Message, state: FSMContext, session: AsyncSession):
    """Procesa la duración VIP ingresada por texto."""
    try:
        duration_str = message.text.strip()
        
        try:
            duration_days = int(duration_str)
            if duration_days <= 0:
                raise ValueError("Duración debe ser mayor que 0")
        except ValueError:
            await message.answer(
                "❌ **Duración inválida**\n\n"
                "Por favor ingresa un número entero mayor que 0.\n"
                "Ejemplo: 30"
            )
            return
        
        data = await state.get_data()
        user_id = data["user_id"]
        admin_id = message.from_user.id
        
        event_bus = EventBus()
        admin_service = AdminService(event_bus)
        
        result = await admin_service.set_user_vip_status(
            user_id=user_id,
            is_vip=True,
            duration_days=duration_days,
            admin_id=admin_id
        )
        
        await state.clear()
        
        if result["success"]:
            await message.answer(f"✅ **Usuario VIP activado**\n\nDuración: {duration_days} días")
        else:
            await message.answer(f"❌ **Error:** {result['error']}")
            
    except Exception as e:
        await message.answer(f"Error: {str(e)}")
        await state.clear()

@user_management_router.message(UserManagementStates.waiting_for_ban_reason)
async def process_ban_reason_text(message: Message, state: FSMContext, session: AsyncSession):
    """Procesa la razón de ban ingresada por texto."""
    try:
        reason = message.text.strip() if message.text.strip().lower() != "/skip" else None
        
        data = await state.get_data()
        user_id = data["user_id"]
        admin_id = message.from_user.id
        
        event_bus = EventBus()
        admin_service = AdminService(event_bus)
        
        result = await admin_service.ban_user(
            user_id=user_id,
            admin_id=admin_id,
            reason=reason
        )
        
        await state.clear()
        
        if result["success"]:
            reason_text = f"\nRazón: {reason}" if reason else ""
            await message.answer(f"✅ **Usuario baneado**{reason_text}")
        else:
            await message.answer(f"❌ **Error:** {result['error']}")
            
    except Exception as e:
        await message.answer(f"Error: {str(e)}")
        await state.clear()

async def show_user_activity(callback_query: CallbackQuery, user_id: int, session: AsyncSession):
    """Muestra la actividad de un usuario."""
    try:
        text = f"📊 **ACTIVIDAD DEL USUARIO**\n\n"
        text += f"Usuario ID: `{user_id}`\n\n"
        text += f"🔄 **Esta funcionalidad está en desarrollo**\n\n"
        text += f"Próximamente incluirá:\n"
        text += f"• Historial de mensajes por fecha\n"
        text += f"• Interacciones en canales\n"
        text += f"• Uso de comandos\n"
        text += f"• Participación en gamificación\n"
        text += f"• Estadísticas de engagement\n"
        
        keyboard = [
            [InlineKeyboardButton(text="⬅️ Volver", callback_data=f"user_mgmt:details:{user_id}")]
        ]
        
        await callback_query.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
        await callback_query.answer()
        
    except Exception as e:
        await callback_query.answer(f"Error: {str(e)}")

async def show_user_payment_history(callback_query: CallbackQuery, user_id: int, session: AsyncSession):
    """Muestra el historial de pagos de un usuario."""
    try:
        event_bus = EventBus()
        admin_service = AdminService(event_bus)
        
        # Obtener detalles del usuario con historial de suscripciones
        result = await admin_service.get_user_details(user_id)
        
        if not result["success"]:
            await callback_query.answer(f"❌ {result['error']}")
            return
        
        user = result["data"]
        
        text = f"💰 **HISTORIAL DE PAGOS**\n\n"
        text += f"👤 Usuario: {user['first_name']}"
        if user.get("last_name"):
            text += f" {user['last_name']}"
        text += f" (`{user_id}`)\n\n"
        
        if not user["subscription_history"]:
            text += "📭 **Sin historial de pagos**\n\n"
            text += "Este usuario no ha canjeado ningún token de suscripción."
        else:
            text += f"📈 **Total de tokens canjeados:** {len(user['subscription_history'])}\n\n"
            
            total_spent = sum(sub["price"] for sub in user["subscription_history"])
            text += f"💵 **Total gastado:** ${total_spent:.2f}\n\n"
            
            text += "🧾 **Historial de suscripciones:**\n"
            for i, sub in enumerate(reversed(user["subscription_history"][-10:]), 1):  # Últimas 10
                used_date = sub["used_at"]
                if isinstance(used_date, str):
                    date_str = used_date[:10]
                else:
                    date_str = used_date.strftime('%d/%m/%Y')
                
                text += f"{i}. **{sub['tariff_name']}**\n"
                text += f"   💰 ${sub['price']:.2f} - {date_str}\n"
                text += f"   Token ID: `{sub['token_id']}`\n\n"
        
        keyboard = [
            [InlineKeyboardButton(text="📊 Ver Actividad", callback_data=f"user_action:activity:{user_id}")],
            [InlineKeyboardButton(text="⬅️ Volver", callback_data=f"user_mgmt:details:{user_id}")]
        ]
        
        await callback_query.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
        await callback_query.answer()
        
    except Exception as e:
        await callback_query.answer(f"Error: {str(e)}")

@user_management_router.callback_query(F.data == "user_mgmt:list_vip")
async def show_vip_users_list(callback_query: CallbackQuery, session: AsyncSession):
    """Muestra lista de usuarios VIP."""
    try:
        event_bus = EventBus()
        admin_service = AdminService(event_bus)
        
        # Buscar usuarios VIP (usando búsqueda vacía con filtro interno)
        # Por simplicidad, usaremos datos simulados aquí
        text = f"👑 **USUARIOS VIP ACTIVOS**\n\n"
        text += f"🔄 **Esta funcionalidad está en desarrollo**\n\n"
        text += f"Próximamente mostrará:\n"
        text += f"• Lista completa de usuarios VIP\n"
        text += f"• Fechas de expiración\n"
        text += f"• Acciones rápidas por usuario\n"
        text += f"• Filtros por fecha de expiración\n"
        
        keyboard = [
            [InlineKeyboardButton(text="⬅️ Volver", callback_data="admin:users")]
        ]
        
        await callback_query.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
        await callback_query.answer()
        
    except Exception as e:
        await callback_query.answer(f"Error: {str(e)}")