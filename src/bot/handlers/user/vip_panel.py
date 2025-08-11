"""Handler para el panel VIP de usuarios."""

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from datetime import datetime, timedelta

from src.modules.admin.service import AdminService
from src.modules.user.service import UserService
from src.modules.gamification.service import GamificationService
from src.modules.narrative.service import NarrativeService
from src.core.event_bus import EventBus

vip_panel_router = Router()

@vip_panel_router.message(Command("vip"))
async def show_vip_panel(message: Message, session: AsyncSession):
    """Muestra el panel principal VIP para usuarios."""
    try:
        user_id = message.from_user.id
        username = message.from_user.username or message.from_user.first_name
        
        event_bus = EventBus()
        user_service = UserService(event_bus)
        admin_service = AdminService(event_bus)
        gamification_service = GamificationService(event_bus)
        
        # Verificar si el usuario es VIP
        user_result = await admin_service.get_user_details(user_id)
        if not user_result["success"]:
            await message.answer(
                "❌ **Error al acceder al panel VIP**\n\n"
                "No se pudo obtener tu información de usuario.\n"
                "Por favor contacta al soporte."
            )
            return
        
        user_data = user_result["data"]
        
        if not user_data["is_vip"]:
            # Usuario no es VIP - mostrar panel de información
            await show_non_vip_panel(message, user_data, session)
            return
        
        # Usuario es VIP - mostrar panel completo
        await show_vip_dashboard(message, user_data, session)
        
    except Exception as e:
        await message.answer(f"Error al mostrar panel VIP: {str(e)}")

async def show_non_vip_panel(message: Message, user_data: Dict[str, Any], session: AsyncSession):
    """Muestra panel informativo para usuarios no VIP."""
    try:
        text = "🆓 **PANEL USUARIO FREE**\n\n"
        text += f"👋 Hola **{user_data['first_name']}**!\n\n"
        text += "🌟 **¿Por qué upgrade a VIP?**\n"
        text += "✨ Acceso a contenido premium exclusivo\n"
        text += "🎯 Misiones especiales con recompensas mayores\n"
        text += "💎 Multiplicador de besitos x2\n"
        text += "🏆 Logros y títulos exclusivos\n"
        text += "📖 Historias narrativas completas\n"
        text += "🎮 Minijuegos premium\n"
        text += "👑 Badge VIP en el perfil\n"
        text += "⚡ Soporte prioritario\n\n"
        
        # Estadísticas actuales del usuario
        text += "📊 **Tu Estado Actual:**\n"
        text += f"• Nivel: {user_data['level']}\n"
        text += f"• Experiencia: {user_data['experience_points']} XP\n"
        if user_data.get('points'):
            text += f"• Besitos: {user_data['points']['current']:.1f}\n"
        text += f"• Logros: {user_data['achievements_count']}\n"
        text += f"• Misiones completadas: {user_data['missions_completed']}\n\n"
        
        text += "🎫 **¿Tienes un token VIP?**\n"
        text += "Usa el comando `/token` seguido de tu código\n"
        text += "Ejemplo: `/token ABC123DEF456`\n\n"
        
        text += "💬 **¿Quieres ser VIP?**\n"
        text += "Contacta a los administradores para obtener acceso premium!"
        
        keyboard = [
            [InlineKeyboardButton(text="🎫 Canjear Token", callback_data="vip_panel:redeem_token")],
            [InlineKeyboardButton(text="📊 Ver Mi Perfil", callback_data="vip_panel:profile")],
            [InlineKeyboardButton(text="🎮 Ir a Juegos", callback_data="vip_panel:games")],
            [InlineKeyboardButton(text="📖 Ver Historias", callback_data="vip_panel:stories")]
        ]
        
        await message.answer(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
        
    except Exception as e:
        await message.answer(f"Error: {str(e)}")

async def show_vip_dashboard(message: Message, user_data: Dict[str, Any], session: AsyncSession):
    """Muestra el dashboard completo para usuarios VIP."""
    try:
        # Calcular días restantes de VIP
        vip_expires_at = user_data.get("vip_expires_at")
        days_remaining = None
        if vip_expires_at:
            if isinstance(vip_expires_at, str):
                expires_date = datetime.fromisoformat(vip_expires_at.replace('Z', '+00:00'))
            else:
                expires_date = vip_expires_at
            
            if expires_date > datetime.now():
                days_remaining = (expires_date - datetime.now()).days
        
        text = "👑 **PANEL VIP PREMIUM**\n\n"
        text += f"🎉 ¡Bienvenido **{user_data['first_name']}**!\n"
        text += f"✨ Status: **USUARIO VIP** 👑\n\n"
        
        # Estado de la suscripción
        text += "📅 **Tu Suscripción VIP:**\n"
        if days_remaining is not None:
            if days_remaining > 7:
                status_icon = "🟢"
                status_text = "Activa"
            elif days_remaining > 0:
                status_icon = "🟡"
                status_text = f"Expira pronto ({days_remaining} días)"
            else:
                status_icon = "🔴"
                status_text = "Expirada"
            
            text += f"{status_icon} Estado: {status_text}\n"
            if days_remaining > 0:
                text += f"⏰ Expira en: {days_remaining} días\n"
            if isinstance(vip_expires_at, str):
                date_str = vip_expires_at[:10]
            else:
                date_str = expires_date.strftime('%d/%m/%Y')
            text += f"📆 Fecha de expiración: {date_str}\n"
        else:
            text += "🟢 Estado: VIP Permanente\n"
        
        text += "\n"
        
        # Beneficios activos
        text += "🎯 **Beneficios Activos:**\n"
        text += "✅ Contenido premium desbloqueado\n"
        text += "✅ Multiplicador de besitos x2\n"
        text += "✅ Acceso a canales VIP\n"
        text += "✅ Misiones exclusivas\n"
        text += "✅ Historias completas\n"
        text += "✅ Soporte prioritario\n\n"
        
        # Estadísticas VIP
        text += "📊 **Tus Estadísticas VIP:**\n"
        text += f"👑 Nivel: {user_data['level']}\n"
        text += f"⭐ Experiencia: {user_data['experience_points']} XP\n"
        if user_data.get('points'):
            text += f"💎 Besitos: {user_data['points']['current']:.1f}\n"
            text += f"🏆 Total ganados: {user_data['points']['total_earned']:.1f}\n"
        text += f"🎖️ Logros: {user_data['achievements_count']}\n"
        text += f"✅ Misiones completadas: {user_data['missions_completed']}\n"
        
        # Historial de suscripciones
        if user_data.get('subscription_history'):
            text += f"\n💰 **Historial de Suscripciones:**\n"
            text += f"• Total de renovaciones: {len(user_data['subscription_history'])}\n"
            total_spent = sum(sub["price"] for sub in user_data["subscription_history"])
            text += f"• Total invertido: ${total_spent:.2f}\n"
            
            # Mostrar última suscripción
            last_sub = user_data["subscription_history"][-1]
            last_date = last_sub["used_at"]
            if isinstance(last_date, str):
                date_str = last_date[:10]
            else:
                date_str = last_date.strftime('%d/%m/%Y')
            text += f"• Última renovación: {last_sub['tariff_name']} ({date_str})\n"
        
        text += "\n🎮 **¡Disfruta de tu experiencia VIP!**"
        
        # Keyboard con opciones VIP
        keyboard = []
        
        # Primera fila - Acceso exclusivo
        keyboard.append([
            InlineKeyboardButton(text="👑 Canal VIP", callback_data="vip_panel:vip_channel"),
            InlineKeyboardButton(text="🎯 Misiones VIP", callback_data="vip_panel:vip_missions")
        ])
        
        # Segunda fila - Contenido premium
        keyboard.append([
            InlineKeyboardButton(text="📖 Historias Premium", callback_data="vip_panel:premium_stories"),
            InlineKeyboardButton(text="🎮 Juegos VIP", callback_data="vip_panel:vip_games")
        ])
        
        # Tercera fila - Gestión de cuenta
        keyboard.append([
            InlineKeyboardButton(text="📊 Mi Perfil VIP", callback_data="vip_panel:vip_profile"),
            InlineKeyboardButton(text="💎 Mi Inventario", callback_data="vip_panel:inventory")
        ])
        
        # Cuarta fila - Soporte y renovación
        if days_remaining is not None and days_remaining <= 7:
            keyboard.append([
                InlineKeyboardButton(text="🔄 Renovar VIP", callback_data="vip_panel:renew"),
                InlineKeyboardButton(text="💬 Soporte VIP", callback_data="vip_panel:support")
            ])
        else:
            keyboard.append([
                InlineKeyboardButton(text="💬 Soporte VIP", callback_data="vip_panel:support"),
                InlineKeyboardButton(text="🎫 Canjear Token", callback_data="vip_panel:redeem_token")
            ])
        
        # Quinta fila - Configuración
        keyboard.append([
            InlineKeyboardButton(text="⚙️ Configuración VIP", callback_data="vip_panel:settings"),
            InlineKeyboardButton(text="📈 Mis Estadísticas", callback_data="vip_panel:detailed_stats")
        ])
        
        await message.answer(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
        
    except Exception as e:
        await message.answer(f"Error: {str(e)}")

@vip_panel_router.callback_query(F.data.startswith("vip_panel:"))
async def handle_vip_panel_actions(callback_query: CallbackQuery, session: AsyncSession):
    """Maneja las acciones del panel VIP."""
    try:
        action = callback_query.data.split(":")[-1]
        user_id = callback_query.from_user.id
        
        if action == "redeem_token":
            await show_token_redemption_info(callback_query)
        elif action == "profile":
            await show_user_profile(callback_query, session)
        elif action == "vip_profile":
            await show_vip_profile(callback_query, session)
        elif action == "games":
            await callback_query.answer("🎮 Redirigiendo a juegos...")
            await callback_query.message.answer(
                "🎮 **JUEGOS DISPONIBLES**\n\n"
                "Usa estos comandos para jugar:\n"
                "🎁 `/regalo` - Recompensa diaria\n"
                "🛍️ `/tienda` - Tienda de items\n"
                "❓ `/trivia` - Juego de trivia\n\n"
                "¡Los usuarios VIP obtienen recompensas dobles! 👑"
            )
        elif action == "vip_games":
            await callback_query.answer("🎮 Juegos VIP - Funcionalidad en desarrollo")
        elif action == "stories":
            await callback_query.answer("📖 Redirigiendo a historias...")
            await callback_query.message.answer(
                "📖 **HISTORIAS DISPONIBLES**\n\n"
                "Usa estos comandos:\n"
                "📚 `/historia` - Navegar historias\n"
                "🎒 `/mochila` - Ver tu inventario\n\n"
                "¡Los usuarios VIP tienen acceso a historias exclusivas! 👑"
            )
        elif action == "premium_stories":
            await callback_query.answer("📖 Historias Premium - Funcionalidad en desarrollo")
        elif action == "vip_channel":
            await show_vip_channel_info(callback_query)
        elif action == "vip_missions":
            await show_vip_missions(callback_query, session)
        elif action == "inventory":
            await show_vip_inventory(callback_query, session)
        elif action == "renew":
            await show_renewal_options(callback_query)
        elif action == "support":
            await show_vip_support(callback_query)
        elif action == "settings":
            await show_vip_settings(callback_query, session)
        elif action == "detailed_stats":
            await show_detailed_stats(callback_query, session)
        else:
            await callback_query.answer("🔄 Funcionalidad en desarrollo...")
            
    except Exception as e:
        await callback_query.answer(f"Error: {str(e)}")

async def show_token_redemption_info(callback_query: CallbackQuery):
    """Muestra información sobre cómo canjear tokens."""
    text = "🎫 **CANJEAR TOKEN VIP**\n\n"
    text += "Para canjear tu token VIP:\n\n"
    text += "1️⃣ **Método 1 - Comando directo:**\n"
    text += "   `/token ABC123DEF456`\n"
    text += "   (Reemplaza ABC123DEF456 por tu token)\n\n"
    text += "2️⃣ **Método 2 - Enlace de Telegram:**\n"
    text += "   Si tienes un enlace, simplemente haz clic\n\n"
    text += "📝 **Formato del token:**\n"
    text += "• 32-64 caracteres alfanuméricos\n"
    text += "• Puede contener guiones y guiones bajos\n"
    text += "• Es sensible a mayúsculas y minúsculas\n\n"
    text += "⚠️ **Importante:**\n"
    text += "• Cada token solo se puede usar una vez\n"
    text += "• Los tokens tienen fecha de expiración\n"
    text += "• Tu VIP se activará inmediatamente\n\n"
    text += "💡 **¿No tienes token?**\n"
    text += "Contacta a los administradores para obtener uno."
    
    keyboard = [
        [InlineKeyboardButton(text="⬅️ Volver al Panel", callback_data="vip_panel:main")]
    ]
    
    await callback_query.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )
    await callback_query.answer()

async def show_user_profile(callback_query: CallbackQuery, session: AsyncSession):
    """Muestra el perfil del usuario."""
    try:
        user_id = callback_query.from_user.id
        
        event_bus = EventBus()
        admin_service = AdminService(event_bus)
        
        result = await admin_service.get_user_details(user_id)
        
        if not result["success"]:
            await callback_query.answer(f"❌ {result['error']}")
            return
        
        user = result["data"]
        
        text = f"👤 **MI PERFIL**\n\n"
        text += f"📝 **Información Básica:**\n"
        text += f"• Nombre: {user['first_name']}"
        if user.get("last_name"):
            text += f" {user['last_name']}"
        text += "\n"
        
        if user.get("username"):
            text += f"• Username: @{user['username']}\n"
        
        text += f"• ID: `{user['id']}`\n"
        
        if user.get("language_code"):
            text += f"• Idioma: {user['language_code'].upper()}\n"
        
        # Estado
        text += f"\n🏷️ **Estado:**\n"
        if user["is_vip"]:
            text += "👑 Usuario VIP\n"
        else:
            text += "🆓 Usuario Free\n"
        
        # Progreso
        text += f"\n📈 **Progreso:**\n"
        text += f"• Nivel: {user['level']}\n"
        text += f"• Experiencia: {user['experience_points']} XP\n"
        text += f"• Mensajes enviados: {user['messages_count']}\n"
        text += f"• Reacciones dadas: {user['reactions_count']}\n"
        
        # Besitos
        if user.get('points'):
            text += f"\n💎 **Besitos:**\n"
            text += f"• Actuales: {user['points']['current']:.1f}\n"
            text += f"• Total ganados: {user['points']['total_earned']:.1f}\n"
            text += f"• Total gastados: {user['points']['total_spent']:.1f}\n"
        
        # Logros
        text += f"\n🏆 **Gamificación:**\n"
        text += f"• Logros: {user['achievements_count']}\n"
        text += f"• Misiones completadas: {user['missions_completed']}\n"
        text += f"• Canales unidos: {user['channels_count']}\n"
        
        # Registro
        created_date = user["created_at"]
        if isinstance(created_date, str):
            date_str = created_date[:10]
        else:
            date_str = created_date.strftime('%d/%m/%Y')
        text += f"\n📅 **Fecha de registro:** {date_str}\n"
        
        keyboard = [
            [InlineKeyboardButton(text="⬅️ Volver", callback_data="vip_panel:main")]
        ]
        
        await callback_query.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
        await callback_query.answer()
        
    except Exception as e:
        await callback_query.answer(f"Error: {str(e)}")

async def show_vip_profile(callback_query: CallbackQuery, session: AsyncSession):
    """Muestra el perfil VIP detallado."""
    # Implementación similar a show_user_profile pero con énfasis en beneficios VIP
    await show_user_profile(callback_query, session)

async def show_vip_channel_info(callback_query: CallbackQuery):
    """Muestra información sobre el canal VIP."""
    text = "👑 **CANAL VIP EXCLUSIVO**\n\n"
    text += "🎉 ¡Como usuario VIP tienes acceso a nuestro canal premium!\n\n"
    text += "✨ **En el canal VIP encontrarás:**\n"
    text += "• Contenido exclusivo diario\n"
    text += "• Adelantos de nuevas funciones\n"
    text += "• Eventos especiales solo para VIP\n"
    text += "• Interacción directa con administradores\n"
    text += "• Sorteos y promociones exclusivas\n"
    text += "• Feedback y sugerencias prioritarias\n\n"
    text += "🔗 **¿Cómo unirme?**\n"
    text += "Tu acceso al canal se activó automáticamente al convertirte en VIP.\n"
    text += "Si tienes problemas, contacta al soporte.\n\n"
    text += "⚠️ **Importante:**\n"
    text += "• El acceso es válido mientras tu VIP esté activo\n"
    text += "• Respeta las reglas del canal\n"
    text += "• El contenido es confidencial y exclusivo"
    
    keyboard = [
        [InlineKeyboardButton(text="💬 Soporte VIP", callback_data="vip_panel:support")],
        [InlineKeyboardButton(text="⬅️ Volver", callback_data="vip_panel:main")]
    ]
    
    await callback_query.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )
    await callback_query.answer()

async def show_vip_missions(callback_query: CallbackQuery, session: AsyncSession):
    """Muestra las misiones VIP disponibles."""
    text = "🎯 **MISIONES VIP EXCLUSIVAS**\n\n"
    text += "👑 ¡Misiones especiales para usuarios VIP!\n\n"
    text += "🔄 **Esta funcionalidad está en desarrollo**\n\n"
    text += "Próximamente incluirá:\n"
    text += "• Misiones con recompensas dobles\n"
    text += "• Desafíos exclusivos para VIP\n"
    text += "• Misiones cooperativas entre VIPs\n"
    text += "• Recompensas premium únicas\n"
    text += "• Eventos temporales especiales\n\n"
    text += "💡 **Mientras tanto:**\n"
    text += "Usa `/misiones` para ver las misiones regulares\n"
    text += "Como VIP obtienes bonificaciones en todas!"
    
    keyboard = [
        [InlineKeyboardButton(text="🎮 Ver Misiones Regulares", callback_data="vip_panel:games")],
        [InlineKeyboardButton(text="⬅️ Volver", callback_data="vip_panel:main")]
    ]
    
    await callback_query.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )
    await callback_query.answer()

async def show_vip_inventory(callback_query: CallbackQuery, session: AsyncSession):
    """Muestra el inventario VIP del usuario."""
    text = "🎒 **MI INVENTARIO VIP**\n\n"
    text += "✨ ¡Tu colección de items exclusivos!\n\n"
    text += "🔄 **Esta funcionalidad está en desarrollo**\n\n"
    text += "Tu inventario VIP incluirá:\n"
    text += "• Items exclusivos de VIP\n"
    text += "• Multiplicadores especiales\n"
    text += "• Insignias y títulos únicos\n"
    text += "• Cosméticos premium\n"
    text += "• Tokens de eventos especiales\n\n"
    text += "💡 **Mientras tanto:**\n"
    text += "Usa `/mochila` para ver tu inventario regular\n"
    text += "¡Los items VIP aparecen con una corona! 👑"
    
    keyboard = [
        [InlineKeyboardButton(text="🎒 Ver Mochila Regular", callback_data="vip_panel:stories")],
        [InlineKeyboardButton(text="⬅️ Volver", callback_data="vip_panel:main")]
    ]
    
    await callback_query.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )
    await callback_query.answer()

async def show_renewal_options(callback_query: CallbackQuery):
    """Muestra opciones de renovación VIP."""
    text = "🔄 **RENOVAR SUSCRIPCIÓN VIP**\n\n"
    text += "⚠️ **Tu VIP expira pronto!**\n\n"
    text += "💎 **Opciones de renovación:**\n"
    text += "• Adquiere un nuevo token VIP\n"
    text += "• Contacta a los administradores\n"
    text += "• Participa en eventos especiales\n\n"
    text += "🎁 **Beneficios de renovar:**\n"
    text += "• Mantienes todos tus beneficios\n"
    text += "• No pierdes tu progreso VIP\n"
    text += "• Acceso continuo a contenido exclusivo\n"
    text += "• Descuentos por fidelidad (consultar)\n\n"
    text += "📞 **¿Necesitas ayuda?**\n"
    text += "Nuestro soporte VIP te puede ayudar con opciones de renovación."
    
    keyboard = [
        [InlineKeyboardButton(text="🎫 Canjear Token", callback_data="vip_panel:redeem_token")],
        [InlineKeyboardButton(text="💬 Contactar Admin", callback_data="vip_panel:support")],
        [InlineKeyboardButton(text="⬅️ Volver", callback_data="vip_panel:main")]
    ]
    
    await callback_query.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )
    await callback_query.answer()

async def show_vip_support(callback_query: CallbackQuery):
    """Muestra información de soporte VIP."""
    text = "💬 **SOPORTE VIP EXCLUSIVO**\n\n"
    text += "👑 ¡Soporte prioritario para usuarios VIP!\n\n"
    text += "🚀 **Ventajas del soporte VIP:**\n"
    text += "• Respuesta prioritaria (< 2 horas)\n"
    text += "• Acceso directo a administradores\n"
    text += "• Resolución especializada\n"
    text += "• Asistencia personalizada\n\n"
    text += "📞 **¿Cómo contactarnos?**\n"
    text += "• Menciona que eres usuario VIP\n"
    text += "• Describe tu consulta detalladamente\n"
    text += "• Incluye tu ID de usuario si es técnico\n\n"
    text += "🆔 **Tu ID:** `" + str(callback_query.from_user.id) + "`\n\n"
    text += "⚡ **Para soporte inmediato:**\n"
    text += "Contacta a cualquier administrador del bot\n"
    text += "mencionando tu status VIP."
    
    keyboard = [
        [InlineKeyboardButton(text="⬅️ Volver al Panel", callback_data="vip_panel:main")]
    ]
    
    await callback_query.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )
    await callback_query.answer()

async def show_vip_settings(callback_query: CallbackQuery, session: AsyncSession):
    """Muestra configuraciones VIP."""
    text = "⚙️ **CONFIGURACIÓN VIP**\n\n"
    text += "👑 Personaliza tu experiencia VIP\n\n"
    text += "🔄 **Esta funcionalidad está en desarrollo**\n\n"
    text += "Próximas configuraciones VIP:\n"
    text += "• Notificaciones premium\n"
    text += "• Preferencias de contenido\n"
    text += "• Configuración de privacidad VIP\n"
    text += "• Personalización de dashboard\n"
    text += "• Configuración de multiplicadores\n"
    text += "• Alertas de expiración\n\n"
    text += "💡 **Configuración actual:**\n"
    text += "• Status VIP: Activo ✅\n"
    text += "• Soporte prioritario: Habilitado ✅\n"
    text += "• Notificaciones: Estándar\n"
    
    keyboard = [
        [InlineKeyboardButton(text="⬅️ Volver", callback_data="vip_panel:main")]
    ]
    
    await callback_query.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )
    await callback_query.answer()

async def show_detailed_stats(callback_query: CallbackQuery, session: AsyncSession):
    """Muestra estadísticas detalladas del usuario VIP."""
    try:
        user_id = callback_query.from_user.id
        
        event_bus = EventBus()
        admin_service = AdminService(event_bus)
        
        result = await admin_service.get_user_details(user_id)
        
        if not result["success"]:
            await callback_query.answer(f"❌ {result['error']}")
            return
        
        user = result["data"]
        
        text = f"📈 **MIS ESTADÍSTICAS DETALLADAS**\n\n"
        text += f"👑 **Status VIP Confirmado** ✅\n\n"
        
        # Estadísticas de engagement
        text += f"📊 **Engagement:**\n"
        text += f"• Mensajes totales: {user['messages_count']:,}\n"
        text += f"• Reacciones dadas: {user['reactions_count']:,}\n"
        
        # Calcular promedio diario (aproximado)
        created_date = user["created_at"]
        if isinstance(created_date, str):
            created = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
        else:
            created = created_date
        
        days_registered = max(1, (datetime.now() - created).days)
        avg_messages = user['messages_count'] / days_registered
        
        text += f"• Promedio mensajes/día: {avg_messages:.1f}\n"
        text += f"• Días registrado: {days_registered:,}\n\n"
        
        # Estadísticas de puntos
        if user.get('points'):
            points = user['points']
            text += f"💎 **Economía de Besitos:**\n"
            text += f"• Balance actual: {points['current']:,.1f}\n"
            text += f"• Total ganado histórico: {points['total_earned']:,.1f}\n"
            text += f"• Total gastado: {points['total_spent']:,.1f}\n"
            text += f"• Tasa de ahorro: {((points['current'] / max(points['total_earned'], 1)) * 100):.1f}%\n\n"
        
        # Estadísticas de gamificación
        text += f"🎮 **Gamificación:**\n"
        text += f"• Nivel actual: {user['level']}\n"
        text += f"• Experiencia: {user['experience_points']:,} XP\n"
        text += f"• Logros desbloqueados: {user['achievements_count']}\n"
        text += f"• Misiones completadas: {user['missions_completed']}\n"
        text += f"• Tasa de éxito: {((user['missions_completed'] / max(user['achievements_count'] + user['missions_completed'], 1)) * 100):.1f}%\n\n"
        
        # Estadísticas VIP
        if user.get('subscription_history'):
            subs = user['subscription_history']
            total_spent = sum(sub["price"] for sub in subs)
            text += f"💰 **Inversión VIP:**\n"
            text += f"• Renovaciones: {len(subs)}\n"
            text += f"• Gasto total: ${total_spent:.2f}\n"
            text += f"• Promedio por renovación: ${total_spent/len(subs):.2f}\n"
            text += f"• Cliente desde: {len(subs)} suscripción(es)\n\n"
        
        # Ranking aproximado (simulado)
        text += f"🏆 **Tu Ranking:**\n"
        text += f"• Top nivel: ~{max(1, 100 - user['level'] * 3)}% de usuarios\n"
        text += f"• Top XP: ~{max(1, 100 - user['experience_points'] // 100)}% de usuarios\n"
        if user.get('points'):
            text += f"• Top besitos: ~{max(1, 100 - int(user['points']['total_earned'] // 50))}% de usuarios\n"
        
        text += f"\n🌟 **¡Excelente progreso como usuario VIP!**"
        
        keyboard = [
            [InlineKeyboardButton(text="📊 Comparar con Promedio", callback_data="vip_panel:compare_stats")],
            [InlineKeyboardButton(text="⬅️ Volver", callback_data="vip_panel:main")]
        ]
        
        await callback_query.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
        await callback_query.answer()
        
    except Exception as e:
        await callback_query.answer(f"Error: {str(e)}")

@vip_panel_router.callback_query(F.data == "vip_panel:main")
async def return_to_vip_main(callback_query: CallbackQuery, session: AsyncSession):
    """Regresa al panel principal VIP."""
    # Simular un mensaje para reutilizar la lógica
    fake_message = callback_query.message
    fake_message.from_user = callback_query.from_user
    await show_vip_panel(fake_message, session)