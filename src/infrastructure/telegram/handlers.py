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
