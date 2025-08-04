from aiogram import types, F, Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from src.core.interfaces.IEventBus import IEventBus
from src.modules.events import UserStartedBotEvent
from src.modules.gamification.service import GamificationService
from src.modules.admin.service import AdminService
from src.infrastructure.telegram.keyboards import (
    get_main_menu_keyboard, get_admin_menu_keyboard, get_free_channel_admin_kb, 
    get_wait_time_selection_kb, get_post_confirmation_kb, get_vip_admin_menu_kb,
    get_tariff_view_kb
)

class AdminStates(StatesGroup):
    waiting_for_channel_id = State()
    waiting_for_post_text = State()
    waiting_for_media = State()
    confirming_post = State()
    waiting_for_tariff_name = State()
    waiting_for_tariff_price = State()
    waiting_for_tariff_duration = State()

class Handlers:
    def __init__(self, event_bus: IEventBus, gamification_service: GamificationService, admin_service: AdminService):
        self._event_bus = event_bus
        self._gamification_service = gamification_service
        self._admin_service = admin_service

    async def handle_start(self, message: types.Message, command: types.BotCommand):
        token = command.args
        user_id = message.from_user.id

        if token:
            validated_token = await self._admin_service.validate_token(token, user_id)
            if validated_token:
                tariff = await self._admin_service.get_tariff(validated_token.tariff_id)
                await message.answer(f"¡Felicidades! Has canjeado un token para la tarifa '{tariff.name}'.\nDisfruta de tu acceso VIP por {tariff.duration_days} días.")
            else:
                await message.answer("El token que has usado no es válido o ya ha sido canjeado.")
        else:
            event = UserStartedBotEvent(user_id=user_id, username=message.from_user.username)
            await self._event_bus.publish(event)
            await message.answer(
                "¡Bienvenido a Diana V2! ¿Qué te gustaría hacer hoy?",
                reply_markup=get_main_menu_keyboard()
            )

    async def handle_admin_command(self, message: types.Message):
        """Handler para el comando /admin - TEMPORAL."""
        user_id = message.from_user.id
        print(f"🎯 ADMIN HANDLER: Comando /admin recibido de user_id: {user_id}")
        
        # Verificar si es admin (hardcodeado temporalmente)
        if user_id != 1280444712:
            print(f"🚫 ADMIN: Usuario {user_id} no es administrador")
            await message.answer("❌ No tienes permisos de administrador.")
            return
            
        print(f"✅ ADMIN: Usuario admin autenticado: {user_id}")
        # Importar el keyboard moderno
        from src.bot.keyboards.admin.main_kb import get_admin_main_keyboard
        
        welcome_text = "🛠️ **Panel de Administración Moderno**\n\n"
        welcome_text += "• Gestión completa de usuarios y roles\n"
        welcome_text += "• Administración de canales VIP y gratuitos\n"
        welcome_text += "• Gestión de tarifas y tokens\n"
        welcome_text += "• Acceso a estadísticas y analíticas\n"
        welcome_text += "\n🆕 **SISTEMA MODERNO ACTIVO**\n"
        welcome_text += "Selecciona una opción del menú:"
        
        await message.answer(
            welcome_text,
            parse_mode="Markdown",
            reply_markup=get_admin_main_keyboard()
        )

    # Callbacks del menú moderno
    async def handle_admin_tariffs_callback(self, query: types.CallbackQuery):
        """Callback para gestión de tarifas."""
        text = (
            "🏷️ **Gestión de Tarifas**\n\n"
            "Desde aquí puedes crear nuevas tarifas, generar enlaces de invitación "
            "y ver estadísticas de uso.\n\n"
            "**Funciones disponibles:**\n"
            "• Crear nuevas tarifas VIP\n"
            "• Generar enlaces de invitación\n"
            "• Ver estadísticas de tokens\n"
            "• Administrar tarifas existentes"
        )
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🆕 Nueva Tarifa", callback_data="tariff:new")],
            [InlineKeyboardButton(text="🔗 Generar Token", callback_data="tariff:generate")],
            [InlineKeyboardButton(text="📊 Estadísticas", callback_data="tariff:stats")],
            [InlineKeyboardButton(text="📋 Ver Tarifas", callback_data="tariff:list")],
            [InlineKeyboardButton(text="🔙 Volver", callback_data="admin:main")]
        ])
        
        await query.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
        await query.answer()

    async def handle_admin_tokens_callback(self, query: types.CallbackQuery):
        """Callback para generación de tokens."""
        text = (
            "🔑 **Generación de Tokens**\n\n"
            "Genera tokens de acceso para usuarios VIP.\n\n"
            "**Opciones disponibles:**\n"
            "• Generar token individual\n"
            "• Generar tokens masivos\n"
            "• Ver tokens activos\n"
            "• Invalidar tokens"
        )
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎯 Token Individual", callback_data="token:individual")],
            [InlineKeyboardButton(text="📦 Tokens Masivos", callback_data="token:bulk")],
            [InlineKeyboardButton(text="👀 Ver Activos", callback_data="token:active")],
            [InlineKeyboardButton(text="🚫 Invalidar Token", callback_data="token:invalidate")],
            [InlineKeyboardButton(text="🔙 Volver", callback_data="admin:main")]
        ])
        
        await query.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
        await query.answer()

    async def handle_admin_roles_callback(self, query: types.CallbackQuery):
        """Callback para gestión de roles."""
        text = (
            "👑 **Gestión de Roles**\n\n"
            "Administra usuarios, roles y permisos del sistema.\n\n"
            "**Funciones disponibles:**\n"
            "• Buscar y modificar usuarios\n"
            "• Otorgar/revocar roles VIP\n"
            "• Gestionar administradores\n"
            "• Ver estadísticas de roles\n"
            "• Mantenimiento automático"
        )
        
        from src.bot.keyboards.admin.main_kb import get_admin_roles_keyboard
        await query.message.edit_text(text, parse_mode="Markdown", reply_markup=get_admin_roles_keyboard())
        await query.answer()

    async def handle_admin_stats_callback(self, query: types.CallbackQuery):
        """Callback para estadísticas del sistema."""
        text = (
            "📊 **Estadísticas del Sistema**\n\n"
            "Analíticas completas de tu bot y usuarios.\n\n"
            "**Estadísticas disponibles:**\n"
            "• Usuarios activos\n"
            "• Conversiones VIP\n"
            "• Engagement narrativo\n"
            "• Performance de gamificación"
        )
        
        from src.bot.keyboards.admin.main_kb import get_admin_stats_keyboard
        await query.message.edit_text(text, parse_mode="Markdown", reply_markup=get_admin_stats_keyboard())
        await query.answer()

    async def handle_admin_settings_callback(self, query: types.CallbackQuery):
        """Callback para configuración del sistema."""
        text = (
            "⚙️ **Configuración del Sistema**\n\n"
            "Ajustes generales del bot y funcionalidades.\n\n"
            "**Configuraciones disponibles:**\n"
            "• Mensajes automáticos\n"
            "• Timeouts y eliminación\n"
            "• Configuración de canales\n"
            "• Ajustes de gamificación"
        )
        
        from src.bot.keyboards.admin.main_kb import get_admin_settings_keyboard
        await query.message.edit_text(text, parse_mode="Markdown", reply_markup=get_admin_settings_keyboard())
        await query.answer()

    async def handle_admin_main_callback(self, query: types.CallbackQuery):
        """Callback para volver al menú principal del admin."""
        from src.bot.keyboards.admin.main_kb import get_admin_main_keyboard
        
        welcome_text = "🛠️ **Panel de Administración Moderno**\n\n"
        welcome_text += "• Gestión completa de usuarios y roles\n"
        welcome_text += "• Administración de canales VIP y gratuitos\n"
        welcome_text += "• Gestión de tarifas y tokens\n"
        welcome_text += "• Acceso a estadísticas y analíticas\n"
        welcome_text += "\n🆕 **SISTEMA MODERNO ACTIVO**\n"
        welcome_text += "Selecciona una opción del menú:"
        
        await query.message.edit_text(welcome_text, parse_mode="Markdown", reply_markup=get_admin_main_keyboard())
        await query.answer()

    # ===== CALLBACKS DE ACCIONES DE TARIFAS =====
    async def handle_tariff_new_callback(self, query: types.CallbackQuery):
        """Callback para crear nueva tarifa."""
        text = (
            "🆕 **Crear Nueva Tarifa**\n\n"
            "Para crear una nueva tarifa, necesitarás proporcionar:\n"
            "• Nombre de la tarifa\n"
            "• Precio (en USD)\n"
            "• Duración en días\n\n"
            "¿Deseas continuar con el proceso de creación?"
        )
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Crear Tarifa", callback_data="admin:create_tariff")],
            [InlineKeyboardButton(text="🔙 Volver", callback_data="admin:tariffs")]
        ])
        
        await query.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
        await query.answer()

    async def handle_tariff_generate_callback(self, query: types.CallbackQuery):
        """Callback para generar token de tarifa."""
        tariffs = await self._admin_service.get_all_tariffs()
        
        if not tariffs:
            text = "❌ **No hay tarifas disponibles**\n\nPrimero debes crear al menos una tarifa para poder generar tokens."
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🆕 Crear Tarifa", callback_data="tariff:new")],
                [InlineKeyboardButton(text="🔙 Volver", callback_data="admin:tariffs")]
            ])
        else:
            text = "🔗 **Generar Token de Tarifa**\n\nSelecciona la tarifa para la cual deseas generar un token:"
            
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            buttons = []
            for tariff in tariffs:
                buttons.append([InlineKeyboardButton(
                    text=f"💎 {tariff.name} (${tariff.price})", 
                    callback_data=f"admin:generate_token_{tariff.id}"
                )])
            buttons.append([InlineKeyboardButton(text="🔙 Volver", callback_data="admin:tariffs")])
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        
        await query.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
        await query.answer()

    async def handle_tariff_stats_callback(self, query: types.CallbackQuery):
        """Callback para estadísticas de tarifas."""
        tariffs = await self._admin_service.get_all_tariffs()
        
        text = "📊 **Estadísticas de Tarifas**\n\n"
        
        if not tariffs:
            text += "❌ No hay tarifas registradas en el sistema."
        else:
            text += f"📈 **Total de tarifas:** {len(tariffs)}\n\n"
            
            for tariff in tariffs:
                # Aquí podrías agregar más estadísticas como tokens generados, usuarios activos, etc.
                text += f"💎 **{tariff.name}**\n"
                text += f"   • Precio: ${tariff.price}\n"
                text += f"   • Duración: {tariff.duration_days} días\n"
                text += f"   • Estado: ✅ Activa\n\n"
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Actualizar", callback_data="tariff:stats")],
            [InlineKeyboardButton(text="🔙 Volver", callback_data="admin:tariffs")]
        ])
        
        await query.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
        await query.answer()

    async def handle_tariff_list_callback(self, query: types.CallbackQuery):
        """Callback para listar todas las tarifas."""
        tariffs = await self._admin_service.get_all_tariffs()
        
        text = "📋 **Lista de Tarifas**\n\n"
        
        if not tariffs:
            text += "❌ No hay tarifas registradas en el sistema.\n\n¿Deseas crear una nueva tarifa?"
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🆕 Crear Tarifa", callback_data="tariff:new")],
                [InlineKeyboardButton(text="🔙 Volver", callback_data="admin:tariffs")]
            ])
        else:
            for i, tariff in enumerate(tariffs, 1):
                text += f"**{i}. {tariff.name}**\n"
                text += f"   💰 Precio: ${tariff.price}\n"
                text += f"   ⏱️ Duración: {tariff.duration_days} días\n"
                text += f"   🆔 ID: {tariff.id}\n\n"
            
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            buttons = []
            for tariff in tariffs:
                buttons.append([InlineKeyboardButton(
                    text=f"👁️ Ver {tariff.name}", 
                    callback_data=f"admin:view_tariff_{tariff.id}"
                )])
            buttons.append([InlineKeyboardButton(text="🔙 Volver", callback_data="admin:tariffs")])
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        
        await query.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
        await query.answer()

    # ===== CALLBACKS DE ACCIONES DE TOKENS =====
    async def handle_token_individual_callback(self, query: types.CallbackQuery):
        """Callback para generar token individual."""
        text = (
            "🎯 **Generar Token Individual**\n\n"
            "Esta función te permite generar un token único para un usuario específico.\n\n"
            "**Características:**\n"
            "• Token de uso único\n"
            "• Válido por tiempo limitado\n"
            "• Asociado a una tarifa específica\n\n"
            "Para continuar, primero selecciona una tarifa:"
        )
        
        # Reutilizar la lógica de generación de tokens
        await query.answer()
        await self.handle_tariff_generate_callback(query)

    async def handle_token_bulk_callback(self, query: types.CallbackQuery):
        """Callback para generar tokens masivos."""
        text = (
            "📦 **Generación Masiva de Tokens**\n\n"
            "⚠️ **Función en desarrollo**\n\n"
            "Esta funcionalidad permitirá generar múltiples tokens de una vez para:\n"
            "• Campañas promocionales\n"
            "• Distribución masiva\n"
            "• Eventos especiales\n\n"
            "🔧 **Estado:** En implementación"
        )
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Volver", callback_data="admin:tokens")]
        ])
        
        await query.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
        await query.answer()

    async def handle_token_active_callback(self, query: types.CallbackQuery):
        """Callback para ver tokens activos."""
        text = (
            "👀 **Tokens Activos**\n\n"
            "⚠️ **Función en desarrollo**\n\n"
            "Esta sección mostrará:\n"
            "• Lista de tokens no canjeados\n"
            "• Fecha de creación\n"
            "• Tarifa asociada\n"
            "• Estado de validez\n\n"
            "🔧 **Estado:** En implementación"
        )
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Actualizar", callback_data="token:active")],
            [InlineKeyboardButton(text="🔙 Volver", callback_data="admin:tokens")]
        ])
        
        await query.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
        await query.answer()

    async def handle_token_invalidate_callback(self, query: types.CallbackQuery):
        """Callback para invalidar tokens."""
        text = (
            "🚫 **Invalidar Token**\n\n"
            "⚠️ **Función en desarrollo**\n\n"
            "Esta funcionalidad permitirá:\n"
            "• Invalidar tokens específicos\n"
            "• Cancelar tokens masivamente\n"
            "• Gestionar tokens comprometidos\n\n"
            "🔧 **Estado:** En implementación"
        )
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Volver", callback_data="admin:tokens")]
        ])
        
        await query.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
        await query.answer()

    # ===== CALLBACKS DE ESTADÍSTICAS =====
    async def handle_stats_users_callback(self, query: types.CallbackQuery):
        """Callback para estadísticas de usuarios."""
        text = (
            "👥 **Estadísticas de Usuarios**\n\n"
            "⚠️ **Función en desarrollo**\n\n"
            "Esta sección mostrará:\n"
            "• Total de usuarios registrados\n"
            "• Usuarios activos (última semana)\n"
            "• Nuevos registros (último mes)\n"
            "• Distribución por tipo de usuario\n\n"
            "🔧 **Estado:** En implementación"
        )
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Actualizar", callback_data="stats:users")],
            [InlineKeyboardButton(text="🔙 Volver", callback_data="admin:stats")]
        ])
        
        await query.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
        await query.answer()

    async def handle_stats_conversions_callback(self, query: types.CallbackQuery):
        """Callback para estadísticas de conversiones VIP."""
        text = (
            "💎 **Conversiones VIP**\n\n"
            "⚠️ **Función en desarrollo**\n\n"
            "Esta sección mostrará:\n"
            "• Tasa de conversión gratuito → VIP\n"
            "• Tokens canjeados vs generados\n"
            "• Ingresos por tarifa\n"
            "• Retención de usuarios VIP\n\n"
            "🔧 **Estado:** En implementación"
        )
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Actualizar", callback_data="stats:conversions")],
            [InlineKeyboardButton(text="🔙 Volver", callback_data="admin:stats")]
        ])
        
        await query.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
        await query.answer()

    async def handle_stats_narrative_callback(self, query: types.CallbackQuery):
        """Callback para estadísticas narrativas."""
        text = (
            "📖 **Engagement Narrativo**\n\n"
            "⚠️ **Función en desarrollo**\n\n"
            "Esta sección mostrará:\n"
            "• Interacciones con Diana\n"
            "• Sesiones de conversación promedio\n"
            "• Temas más populares\n"
            "• Tiempo de engagement\n\n"
            "🔧 **Estado:** En implementación"
        )
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Actualizar", callback_data="stats:narrative")],
            [InlineKeyboardButton(text="🔙 Volver", callback_data="admin:stats")]
        ])
        
        await query.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
        await query.answer()

    async def handle_stats_gamification_callback(self, query: types.CallbackQuery):
        """Callback para estadísticas de gamificación."""
        text = (
            "🎮 **Performance de Gamificación**\n\n"
            "⚠️ **Función en desarrollo**\n\n"
            "Esta sección mostrará:\n"
            "• Puntos distribuidos\n"
            "• Misiones completadas\n"
            "• Rankings de usuarios\n"
            "• Efectividad de recompensas\n\n"
            "🔧 **Estado:** En implementación"
        )
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Actualizar", callback_data="stats:gamification")],
            [InlineKeyboardButton(text="🔙 Volver", callback_data="admin:stats")]
        ])
        
        await query.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
        await query.answer()

    async def handle_stats_general_callback(self, query: types.CallbackQuery):
        """Callback para resumen general de estadísticas."""
        tariffs = await self._admin_service.get_all_tariffs()
        
        text = "🔄 **Resumen General del Sistema**\n\n"
        text += f"📊 **Dashboard Principal**\n\n"
        text += f"💎 **Tarifas registradas:** {len(tariffs)}\n"
        text += f"🤖 **Estado del bot:** ✅ Operativo\n"
        text += f"📅 **Última actualización:** Ahora\n\n"
        
        text += "**Módulos disponibles:**\n"
        text += "✅ Sistema de tarifas\n"
        text += "✅ Generación de tokens\n"
        text += "✅ Panel de administración\n"
        text += "🔧 Estadísticas detalladas (en desarrollo)\n"
        text += "🔧 Gamificación avanzada (en desarrollo)\n"
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Actualizar", callback_data="stats:general")],
            [InlineKeyboardButton(text="🔙 Volver", callback_data="admin:stats")]
        ])
        
        await query.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
        await query.answer()

    # ===== CALLBACKS DE CONFIGURACIÓN =====
    async def handle_settings_auto_messages_callback(self, query: types.CallbackQuery):
        """Callback para configurar mensajes automáticos."""
        text = (
            "💬 **Mensajes Automáticos**\n\n"
            "⚠️ **Función en desarrollo**\n\n"
            "Esta sección permitirá configurar:\n"
            "• Mensajes de bienvenida personalizados\n"
            "• Respuestas automáticas\n"
            "• Notificaciones programadas\n"
            "• Templates de mensajes\n\n"
            "🔧 **Estado:** En implementación"
        )
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Volver", callback_data="admin:settings")]
        ])
        
        await query.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
        await query.answer()

    async def handle_settings_timeouts_callback(self, query: types.CallbackQuery):
        """Callback para configurar timeouts."""
        current_wait_time = self._admin_service.get_wait_time()
        
        text = (
            f"⏰ **Configuración de Timeouts**\n\n"
            f"**Configuración actual:**\n"
            f"• Tiempo de espera: {current_wait_time} minutos\n\n"
            f"**Timeouts configurables:**\n"
            f"• Tiempo entre mensajes gratuitos\n"
            f"• Timeout de sesiones inactivas\n"
            f"• Expiración de tokens\n"
            f"• Cooldown de comandos\n"
        )
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⏱️ Cambiar Tiempo de Espera", callback_data="admin:set_wait_time")],
            [InlineKeyboardButton(text="🔙 Volver", callback_data="admin:settings")]
        ])
        
        await query.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
        await query.answer()

    async def handle_settings_channels_callback(self, query: types.CallbackQuery):
        """Callback para configurar canales."""
        free_channel_id = self._admin_service.get_free_channel_id()
        
        text = "📺 **Configuración de Canales**\n\n"
        
        if free_channel_id:
            text += f"✅ **Canal gratuito configurado**\n"
            text += f"🆔 ID: {free_channel_id}\n\n"
        else:
            text += "❌ **Canal gratuito no configurado**\n\n"
        
        text += "**Canales disponibles:**\n"
        text += "• Canal gratuito (contenido público)\n"
        text += "• Canales VIP (por tarifa)\n"
        text += "• Canal de administradores\n"
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🆓 Configurar Canal Gratuito", callback_data="admin:free_channel_menu")],
            [InlineKeyboardButton(text="💎 Gestionar Canales VIP", callback_data="admin:vip_channel_menu")],
            [InlineKeyboardButton(text="🔙 Volver", callback_data="admin:settings")]
        ])
        
        await query.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
        await query.answer()

    async def handle_settings_gamification_callback(self, query: types.CallbackQuery):
        """Callback para configurar gamificación."""
        text = (
            "🎯 **Configuración de Gamificación**\n\n"
            "⚠️ **Función en desarrollo**\n\n"
            "Esta sección permitirá configurar:\n"
            "• Sistema de puntos y recompensas\n"
            "• Misiones y desafíos\n"
            "• Niveles de usuario\n"
            "• Badges y logros\n\n"
            "🔧 **Estado:** En implementación"
        )
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Volver", callback_data="admin:settings")]
        ])
        
        await query.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
        await query.answer()

    async def handle_settings_system_callback(self, query: types.CallbackQuery):
        """Callback para configuración del sistema."""
        text = (
            "🔧 **Configuración del Sistema**\n\n"
            "**Estado actual del sistema:**\n"
            "✅ Bot operativo\n"
            "✅ Base de datos conectada\n"
            "✅ Handlers registrados\n"
            "✅ Admin panel activo\n\n"
            "**Configuraciones del sistema:**\n"
            "• Logs y debugging\n"
            "• Límites de rate limiting\n"
            "• Configuración de base de datos\n"
            "• Mantenimiento programado\n"
        )
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📊 Ver Estado Sistema", callback_data="stats:general")],
            [InlineKeyboardButton(text="🔙 Volver", callback_data="admin:settings")]
        ])
        
        await query.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
        await query.answer()

    # ===== CALLBACKS DE ROLES =====
    async def handle_roles_search_callback(self, query: types.CallbackQuery):
        """Callback para buscar usuarios."""
        text = (
            "👤 **Buscar Usuario**\n\n"
            "⚠️ **Función en desarrollo**\n\n"
            "Esta funcionalidad permitirá:\n"
            "• Buscar usuarios por ID o username\n"
            "• Ver perfil completo del usuario\n"
            "• Modificar roles y permisos\n"
            "• Historial de actividad\n\n"
            "🔧 **Estado:** En implementación"
        )
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Volver", callback_data="admin:roles")]
        ])
        
        await query.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
        await query.answer()

    async def handle_roles_list_admins_callback(self, query: types.CallbackQuery):
        """Callback para listar administradores."""
        text = (
            "👑 **Lista de Administradores**\n\n"
            "**Administradores activos:**\n"
            "👤 ID: 1280444712 (Tú)\n"
            "   • Estado: ✅ Activo\n"
            "   • Permisos: 🌟 Súper Admin\n"
            "   • Último acceso: Ahora\n\n"
            "**Total de administradores:** 1\n\n"
            "⚠️ **Gestión de admins en desarrollo**"
        )
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Actualizar", callback_data="roles:list_admins")],
            [InlineKeyboardButton(text="🔙 Volver", callback_data="admin:roles")]
        ])
        
        await query.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
        await query.answer()

    async def handle_roles_list_vips_callback(self, query: types.CallbackQuery):
        """Callback para listar usuarios VIP."""
        text = (
            "💎 **Lista de Usuarios VIP**\n\n"
            "⚠️ **Función en desarrollo**\n\n"
            "Esta sección mostrará:\n"
            "• Lista completa de usuarios VIP\n"
            "• Tarifa asociada a cada usuario\n"
            "• Fecha de vencimiento\n"
            "• Estado de la suscripción\n\n"
            "🔧 **Estado:** En implementación"
        )
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Actualizar", callback_data="roles:list_vips")],
            [InlineKeyboardButton(text="🔙 Volver", callback_data="admin:roles")]
        ])
        
        await query.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
        await query.answer()

    async def handle_roles_stats_callback(self, query: types.CallbackQuery):
        """Callback para estadísticas de roles."""
        text = (
            "📊 **Estadísticas de Roles**\n\n"
            "**Distribución actual:**\n"
            "👑 **Administradores:** 1\n"
            "💎 **Usuarios VIP:** 0 (en desarrollo)\n"
            "👤 **Usuarios gratuitos:** 0 (en desarrollo)\n\n"
            "**Métricas adicionales:**\n"
            "• Total de usuarios: En desarrollo\n"
            "• Conversiones recientes: En desarrollo\n"
            "• Retención por rol: En desarrollo\n"
        )
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Actualizar", callback_data="roles:stats")],
            [InlineKeyboardButton(text="🔙 Volver", callback_data="admin:roles")]
        ])
        
        await query.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
        await query.answer()

    async def handle_roles_maintenance_callback(self, query: types.CallbackQuery):
        """Callback para mantenimiento de roles."""
        text = (
            "🔧 **Mantenimiento de Roles**\n\n"
            "⚠️ **Función en desarrollo**\n\n"
            "Esta funcionalidad incluirá:\n"
            "• Limpieza de roles expirados\n"
            "• Verificación de integridad\n"
            "• Migración de datos\n"
            "• Auditoría de permisos\n\n"
            "🔧 **Estado:** En implementación"
        )
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Volver", callback_data="admin:roles")]
        ])
        
        await query.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
        await query.answer()

    async def handle_free_channel_menu_callback(self, query: types.CallbackQuery):
        is_configured = self._admin_service.get_free_channel_id() is not None
        await query.message.edit_text(
            "🆓 **Administración Canal Gratuito**",
            reply_markup=get_free_channel_admin_kb(is_configured)
        )
        await query.answer()

    async def handle_setup_free_channel_callback(self, query: types.CallbackQuery, state: FSMContext):
        await query.message.edit_text("Por favor, reenvía un mensaje del canal gratuito para configurarlo.")
        await state.set_state(AdminStates.waiting_for_channel_id)
        await query.answer()

    async def handle_channel_forward(self, message: types.Message, state: FSMContext):
        if message.forward_from_chat:
            channel_id = message.forward_from_chat.id
            self._admin_service.set_free_channel_id(channel_id)
            await message.answer(f"Canal gratuito configurado con ID: {channel_id}")
            await state.clear()
            # Volver al menú de admin del canal gratuito
            is_configured = self._admin_service.get_free_channel_id() is not None
            await message.answer("🆓 **Administración Canal Gratuito**", reply_markup=get_free_channel_admin_kb(is_configured))
        else:
            await message.answer("Por favor, reenvía un mensaje de un canal.")

    async def handle_set_wait_time_callback(self, query: types.CallbackQuery):
        current_wait_time = self._admin_service.get_wait_time()
        await query.message.edit_text(
            f"⏰ **Configurar Tiempo de Espera**\n\nEl tiempo de espera actual es de {current_wait_time} minutos.",
            reply_markup=get_wait_time_selection_kb()
        )
        await query.answer()

    async def handle_set_wait_time_value_callback(self, query: types.CallbackQuery):
        minutes = int(query.data.split("_")[-1])
        self._admin_service.set_wait_time(minutes)
        await query.answer(f"Tiempo de espera configurado a {minutes} minutos.")
        # Volver al menú de admin del canal gratuito
        is_configured = self._admin_service.get_free_channel_id() is not None
        await query.message.edit_text(
            "🆓 **Administración Canal Gratuito**",
            reply_markup=get_free_channel_admin_kb(is_configured)
        )

    async def handle_send_to_free_channel_callback(self, query: types.CallbackQuery, state: FSMContext):
        await query.message.edit_text("Por favor, envía el texto del post.")
        await state.set_state(AdminStates.waiting_for_post_text)
        await query.answer()

    async def handle_post_text(self, message: types.Message, state: FSMContext):
        await state.update_data(post_text=message.text)
        await message.answer("Texto del post guardado. Ahora puedes enviar los archivos multimedia (o pulsar 'Enviar Post').", reply_markup=get_post_confirmation_kb())
        await state.set_state(AdminStates.confirming_post)

    async def handle_confirm_post_callback(self, query: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        text = data.get("post_text", "")
        media = data.get("media")
        self._admin_service.send_message_to_channel(text, media)
        await query.message.edit_text("Post enviado al canal.")
        await state.clear()
        await query.answer()

    async def handle_profile_callback(self, query: types.CallbackQuery):
        user_id = query.from_user.id
        points = self._gamification_service.get_points(user_id)
        await query.message.edit_text(f"Este es tu perfil:\n\nPuntos: {points}")
        await query.answer()

    async def handle_not_implemented_callback(self, query: types.CallbackQuery):
        await query.answer("Funcionalidad no implementada todavía.")

    def register(self, dp: Dispatcher):
        dp.message.register(self.handle_start, CommandStart())
        dp.message.register(self.handle_admin_command, Command("admin"))  # Reactivado con menú moderno
        dp.callback_query.register(self.handle_free_channel_menu_callback, F.data == "admin:free_channel_menu")
        dp.callback_query.register(self.handle_setup_free_channel_callback, F.data == "admin:setup_free_channel")
        dp.callback_query.register(self.handle_set_wait_time_callback, F.data == "admin:set_wait_time")
        dp.callback_query.register(self.handle_set_wait_time_value_callback, F.data.startswith("admin:set_wait_time_"))
        dp.callback_query.register(self.handle_send_to_free_channel_callback, F.data == "admin:send_to_free_channel")
        dp.message.register(self.handle_post_text, AdminStates.waiting_for_post_text)
        dp.callback_query.register(self.handle_confirm_post_callback, F.data == "admin:confirm_post")
        dp.message.register(self.handle_channel_forward, AdminStates.waiting_for_channel_id, F.forward_from_chat)
        dp.callback_query.register(self.handle_profile_callback, F.data == "main_menu:profile")
        dp.callback_query.register(self.handle_not_implemented_callback, F.data.startswith("main_menu:"))

        # Admin VIP
        dp.callback_query.register(self.handle_vip_channel_menu_callback, F.data == "admin:vip_channel_menu")
        dp.callback_query.register(self.handle_create_tariff_callback, F.data == "admin:create_tariff")
        dp.message.register(self.handle_tariff_name, AdminStates.waiting_for_tariff_name)
        dp.message.register(self.handle_tariff_price, AdminStates.waiting_for_tariff_price)
        dp.message.register(self.handle_tariff_duration, AdminStates.waiting_for_tariff_duration)
        dp.callback_query.register(self.handle_view_tariff_callback, F.data.startswith("admin:view_tariff_"))
        dp.callback_query.register(self.handle_delete_tariff_callback, F.data.startswith("admin:delete_tariff_"))
        dp.callback_query.register(self.handle_generate_token_callback, F.data.startswith("admin:generate_token_"))
        
        # Callbacks del menú moderno
        dp.callback_query.register(self.handle_admin_tariffs_callback, F.data == "admin:tariffs")
        dp.callback_query.register(self.handle_admin_tokens_callback, F.data == "admin:tokens")
        dp.callback_query.register(self.handle_admin_roles_callback, F.data == "admin:roles")
        dp.callback_query.register(self.handle_admin_stats_callback, F.data == "admin:stats")
        dp.callback_query.register(self.handle_admin_settings_callback, F.data == "admin:settings")
        dp.callback_query.register(self.handle_admin_main_callback, F.data == "admin:main")
        
        # Callbacks de acciones de tarifas
        dp.callback_query.register(self.handle_tariff_new_callback, F.data == "tariff:new")
        dp.callback_query.register(self.handle_tariff_generate_callback, F.data == "tariff:generate")
        dp.callback_query.register(self.handle_tariff_stats_callback, F.data == "tariff:stats")
        dp.callback_query.register(self.handle_tariff_list_callback, F.data == "tariff:list")
        
        # Callbacks de acciones de tokens
        dp.callback_query.register(self.handle_token_individual_callback, F.data == "token:individual")
        dp.callback_query.register(self.handle_token_bulk_callback, F.data == "token:bulk")
        dp.callback_query.register(self.handle_token_active_callback, F.data == "token:active")
        dp.callback_query.register(self.handle_token_invalidate_callback, F.data == "token:invalidate")
        
        # Callbacks de estadísticas
        dp.callback_query.register(self.handle_stats_users_callback, F.data == "stats:users")
        dp.callback_query.register(self.handle_stats_conversions_callback, F.data == "stats:conversions")
        dp.callback_query.register(self.handle_stats_narrative_callback, F.data == "stats:narrative")
        dp.callback_query.register(self.handle_stats_gamification_callback, F.data == "stats:gamification")
        dp.callback_query.register(self.handle_stats_general_callback, F.data == "stats:general")
        
        # Callbacks de configuración
        dp.callback_query.register(self.handle_settings_auto_messages_callback, F.data == "settings:auto_messages")
        dp.callback_query.register(self.handle_settings_timeouts_callback, F.data == "settings:timeouts")
        dp.callback_query.register(self.handle_settings_channels_callback, F.data == "settings:channels")
        dp.callback_query.register(self.handle_settings_gamification_callback, F.data == "settings:gamification")
        dp.callback_query.register(self.handle_settings_system_callback, F.data == "settings:system")
        
        # Callbacks de roles
        dp.callback_query.register(self.handle_roles_search_callback, F.data == "roles:search")
        dp.callback_query.register(self.handle_roles_list_admins_callback, F.data == "roles:list_admins")
        dp.callback_query.register(self.handle_roles_list_vips_callback, F.data == "roles:list_vips")
        dp.callback_query.register(self.handle_roles_stats_callback, F.data == "roles:stats")
        dp.callback_query.register(self.handle_roles_maintenance_callback, F.data == "roles:maintenance")

    # Flujo de Admin VIP
    async def handle_vip_channel_menu_callback(self, query: types.CallbackQuery):
        tariffs = await self._admin_service.get_all_tariffs()
        await query.message.edit_text(
            "💎 **Administración Canal VIP**\n\nSelecciona una tarifa para ver sus detalles o crea una nueva.",
            reply_markup=get_vip_admin_menu_kb(tariffs)
        )
        await query.answer()

    async def handle_create_tariff_callback(self, query: types.CallbackQuery, state: FSMContext):
        await query.message.edit_text("Por favor, introduce el nombre de la nueva tarifa.")
        await state.set_state(AdminStates.waiting_for_tariff_name)
        await query.answer()

    async def handle_tariff_name(self, message: types.Message, state: FSMContext):
        await state.update_data(tariff_name=message.text)
        await message.answer("Nombre guardado. Ahora, introduce el precio (ej: 10.99).")
        await state.set_state(AdminStates.waiting_for_tariff_price)

    async def handle_tariff_price(self, message: types.Message, state: FSMContext):
        try:
            price = float(message.text)
            await state.update_data(tariff_price=price)
            await message.answer("Precio guardado. Ahora, introduce la duración en días (ej: 30).")
            await state.set_state(AdminStates.waiting_for_tariff_duration)
        except ValueError:
            await message.answer("Precio inválido. Por favor, introduce un número.")

    async def handle_tariff_duration(self, message: types.Message, state: FSMContext):
        try:
            duration = int(message.text)
            data = await state.get_data()
            await self._admin_service.create_tariff(data['tariff_name'], data['tariff_price'], duration)
            await message.answer("¡Tarifa creada con éxito!")
            await state.clear()
            # Volver al menú de admin VIP
            tariffs = await self._admin_service.get_all_tariffs()
            await message.answer("💎 **Administración Canal VIP**", reply_markup=get_vip_admin_menu_kb(tariffs))
        except ValueError:
            await message.answer("Duración inválida. Por favor, introduce un número entero.")

    async def handle_view_tariff_callback(self, query: types.CallbackQuery):
        tariff_id = int(query.data.split("_")[-1])
        tariff = await self._admin_service.get_tariff(tariff_id)
        if tariff:
            text = f"**Tarifa: {tariff.name}**\n\n"
            text += f"**Precio:** ${tariff.price}\n"
            text += f"**Duración:** {tariff.duration_days} días"
            await query.message.edit_text(text, reply_markup=get_tariff_view_kb(tariff_id))
        else:
            await query.answer("Tarifa no encontrada.", show_alert=True)

    async def handle_delete_tariff_callback(self, query: types.CallbackQuery):
        tariff_id = int(query.data.split("_")[-1])
        await self._admin_service.delete_tariff(tariff_id)
        await query.answer("Tarifa eliminada con éxito.", show_alert=True)
        # Volver al menú de admin VIP
        tariffs = await self._admin_service.get_all_tariffs()
        await query.message.edit_text(
            "💎 **Administración Canal VIP**",
            reply_markup=get_vip_admin_menu_kb(tariffs)
        )

    async def handle_generate_token_callback(self, query: types.CallbackQuery):
        tariff_id = int(query.data.split("_")[-1])
        token = await self._admin_service.generate_subscription_token(tariff_id)
        if token:
            bot_username = (await query.bot.get_me()).username
            await query.message.edit_text(f"Token generado: `t.me/{bot_username}?start={token.token}`")
        else:
            await query.answer("Tarifa no encontrada.", show_alert=True)

def setup_handlers(dp: Dispatcher, event_bus: IEventBus, gamification_service: GamificationService, admin_service: AdminService):
    """Configura todos los handlers de la aplicación.""" 
    handler_instance = Handlers(event_bus, gamification_service, admin_service)
    handler_instance.register(dp)
