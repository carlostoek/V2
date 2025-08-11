from aiogram import types, F, Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from typing import Optional
import logging

from src.core.interfaces.IEventBus import IEventBus
from src.modules.events import UserStartedBotEvent
from src.modules.gamification.service import GamificationService
from src.modules.admin.service import AdminService
from src.modules.emotional.service import EmotionalService
from src.modules.narrative.service import NarrativeService
from src.modules.channel.service import ChannelService
from src.modules.user.service import UserService
from src.modules.token.tokeneitor import Tokeneitor
from src.infrastructure.telegram.keyboards import (
    get_main_menu_keyboard, get_admin_menu_keyboard, get_free_channel_admin_kb, 
    get_wait_time_selection_kb, get_post_confirmation_kb, get_vip_admin_menu_kb,
    get_tariff_view_kb
)
# Importar handlers narrativos
from src.bot.handlers.narrative.story_navigation import StoryNavigationSystem
from src.bot.handlers.narrative.enhanced_mochila import EnhancedMochilaSystem
from src.bot.handlers.narrative.contextual_responses import DianaContextualResponseSystem

logger = logging.getLogger(__name__)

class AdminStates(StatesGroup):
    waiting_for_channel_id = State()
    waiting_for_post_text = State()
    waiting_for_media = State()
    confirming_post = State()
    waiting_for_tariff_name = State()
    waiting_for_tariff_price = State()
    waiting_for_tariff_duration = State()

class Handlers:
    def __init__(
        self, 
        event_bus: IEventBus, 
        gamification_service: GamificationService, 
        admin_service: AdminService,
        emotional_service: Optional[EmotionalService] = None,
        narrative_service: Optional[NarrativeService] = None,
        channel_service: Optional[ChannelService] = None,
        user_service: Optional[UserService] = None,
        token_service: Optional[Tokeneitor] = None
    ):
        self._event_bus = event_bus
        self._gamification_service = gamification_service
        self._admin_service = admin_service
        self._emotional_service = emotional_service
        self._narrative_service = narrative_service
        self._channel_service = channel_service
        self._user_service = user_service
        self._token_service = token_service
        
        # Inicializar sistemas narrativos si los servicios están disponibles
        self._story_system = None
        self._mochila_system = None
        self._diana_system = None
        
        if self._emotional_service and self._narrative_service:
            self._diana_system = DianaContextualResponseSystem(
                event_bus=self._event_bus,
                emotional_service=self._emotional_service,
                narrative_service=self._narrative_service
            )
            self._story_system = StoryNavigationSystem(
                narrative_service=self._narrative_service,
                emotional_service=self._emotional_service,
                diana_system=self._diana_system
            )
            self._mochila_system = EnhancedMochilaSystem(
                narrative_service=self._narrative_service,
                emotional_service=self._emotional_service,
                diana_system=self._diana_system
            )

    async def handle_start(self, message: types.Message, command: types.BotCommand):
        token = command.args
        user_id = message.from_user.id
        username = message.from_user.username

        if token:
            # Token redemption flow with Diana Master System integration
            if self._token_service:
                validated_token = await self._token_service.redeem_token(token, user_id)
                if validated_token:
                    await message.answer(f"¡Felicidades! Has canjeado un token exitosamente.\nDisfruta de tu nuevo acceso.")
                else:
                    await message.answer("El token que has usado no es válido o ya ha been canjeado.")
            else:
                # Fallback to admin service
                validated_token = self._admin_service.validate_token(token, user_id)
                if validated_token:
                    tariff = self._admin_service.get_tariff(validated_token['tariff_id'])
                    await message.answer(f"¡Felicidades! Has canjeado un token para la tarifa '{tariff['name']}'.\nDisfruta de tu acceso VIP por {tariff['duration_days']} días.")
                else:
                    await message.answer("El token que has usado no es válido o ya ha sido canjeado.")
        else:
            # Standard welcome flow with Diana Master System integration
            # Publish user started event
            event = UserStartedBotEvent(user_id=user_id, username=username)
            await self._event_bus.publish(event)
            
            # Initialize emotional state and generate contextual greeting
            if self._emotional_service and self._diana_system:
                await self._emotional_service.get_or_create_state_machine(user_id)
                # Generate contextual greeting using Diana system
                greeting = await self._diana_system.generate_contextual_response(
                    user_id=user_id,
                    context_type='greeting',
                    context_data={
                        'username': username,
                        'is_first_time': True
                    }
                )
            elif self._emotional_service:
                # Fallback to basic emotional greeting
                await self._emotional_service.get_or_create_state_machine(user_id)
                response_modifiers = await self._emotional_service.get_response_modifiers(user_id)
                greeting = self._generate_emotional_greeting(username, response_modifiers)
            else:
                # Basic greeting
                greeting = f"¡Bienvenido a Diana V2, {username or 'usuario'}! ¿Qué te gustaría hacer hoy?"
            
            await message.answer(greeting, reply_markup=get_main_menu_keyboard())
    
    def _generate_emotional_greeting(self, username: str, modifiers: dict) -> str:
        """Generate a personalized greeting based on emotional state modifiers."""
        tone = modifiers.get('tone', 'neutral')
        use_emojis = modifiers.get('use_emojis', True)
        keywords = modifiers.get('keywords', [])
        
        name = username or 'usuario'
        
        if tone == 'mysterious':
            base = f"Hola {name}... me pregunto qué aventuras nos esperan hoy"
            if use_emojis:
                base += " 🌙✨"
        elif tone == 'playful':
            base = f"¡Hola {name}! Lista para algo divertido"
            if use_emojis:
                base += " 😏"
        elif tone == 'gentle':
            base = f"Hola {name}, es un placer verte. ¿Cómo te sientes hoy?"
            if use_emojis:
                base += " 💙"
        elif tone == 'analytical':
            base = f"Saludos {name}. Analicemos qué podemos hacer juntos hoy"
        else:
            base = f"¡Hola {name}! ¿Qué te gustaría explorar?"
        
        return base

    async def handle_admin_command(self, message: types.Message):
        # Aquí iría la lógica para verificar si el usuario es admin
        await message.answer("Menú de Administración", reply_markup=get_admin_menu_keyboard())

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
    
    async def handle_main_menu_callback(self, query: types.CallbackQuery):
        """Handler para callbacks del menú principal."""
        action = query.data.replace("main_menu:", "")
        
        if action == "historia":
            if self._story_system:
                await self._story_system.show_story_hub(query.message)
                await query.answer()
            else:
                await query.answer("Sistema narrativo no disponible", show_alert=True)
                
        elif action == "mochila":
            if self._mochila_system:
                await self._mochila_system.show_mochila_hub(query.message)
                await query.answer()
            else:
                await query.answer("Sistema de mochila no disponible", show_alert=True)
                
        elif action == "profile":
            await self.handle_profile_callback(query)
            
        else:
            await query.answer("Funcionalidad no implementada todavía.")
    
    # Handlers Narrativos
    async def handle_historia_command(self, message: types.Message):
        """Handler para el comando /historia."""
        if self._story_system:
            await self._story_system.show_story_hub(message)
        else:
            await message.answer("El sistema narrativo no está disponible en este momento.")
    
    async def handle_mochila_command(self, message: types.Message):
        """Handler para el comando /mochila."""
        if self._mochila_system:
            await self._mochila_system.show_mochila_hub(message)
        else:
            await message.answer("El sistema de mochila no está disponible en este momento.")
    
    async def handle_diana_callback(self, query: types.CallbackQuery):
        """Handler para todos los callbacks que empiezan con diana:."""
        if not self._story_system:
            await query.answer("Sistema narrativo no disponible", show_alert=True)
            return
            
        action = query.data.replace("diana:", "")
        
        try:
            if action == "continue_story":
                await self._story_system.continue_story(query)
            elif action == "back_to_story_hub":
                # Recrear el hub de historia
                await self._story_system.show_story_hub(query.message)
                await query.answer()
            elif action.startswith("make_choice:"):
                choice_id = int(action.split(":")[1])
                await self._story_system.make_narrative_choice(query, choice_id)
            elif action.startswith("deep_explore:"):
                fragment_key = action.split(":", 1)[1]
                await self._story_system.deep_explore(query, fragment_key)
            elif action.startswith("reflect:"):
                fragment_key = action.split(":", 1)[1]
                await self._story_system.reflect_on_fragment(query, fragment_key)
            elif action == "back_to_main":
                await query.message.edit_text(
                    "¡Hola! ¿Qué te gustaría hacer?", 
                    reply_markup=get_main_menu_keyboard()
                )
                await query.answer()
            else:
                await query.answer("Función en desarrollo...", show_alert=True)
        except Exception as e:
            logger.error(f"Error manejando callback diana: {e}")
            await query.answer("Error procesando acción", show_alert=True)
    
    async def handle_mochila_callback(self, query: types.CallbackQuery):
        """Handler para todos los callbacks que empiezan con mochila:."""
        if not self._mochila_system:
            await query.answer("Sistema de mochila no disponible", show_alert=True)
            return
        
        action_parts = query.data.split(":")
        action = action_parts[1] if len(action_parts) > 1 else ""
        
        try:
            if action == "category" and len(action_parts) > 2:
                category_key = action_parts[2]
                await self._mochila_system.show_category_view(query, category_key)
            elif action == "piece" and len(action_parts) > 2:
                piece_key = action_parts[2]
                await self._mochila_system.show_piece_detail(query, piece_key)
            elif action == "find_connections":
                await self._mochila_system.find_connections(query)
            elif action == "back_to_hub":
                # Recrear el hub de mochila
                await self._mochila_system.show_mochila_hub(query.message)
                await query.answer()
            else:
                await query.answer("Función en desarrollo...", show_alert=True)
        except Exception as e:
            logger.error(f"Error manejando callback mochila: {e}")
            await query.answer("Error procesando acción", show_alert=True)

    def register(self, dp: Dispatcher):
        # Comandos básicos
        dp.message.register(self.handle_start, CommandStart())
        dp.message.register(self.handle_admin_command, Command("admin"))
        
        # Comandos narrativos
        if self._story_system:
            dp.message.register(self.handle_historia_command, Command("historia"))
        if self._mochila_system:
            dp.message.register(self.handle_mochila_command, Command("mochila"))
        
        # Callbacks narrativos
        if self._story_system:
            dp.callback_query.register(self.handle_diana_callback, F.data.startswith("diana:"))
        if self._mochila_system:
            dp.callback_query.register(self.handle_mochila_callback, F.data.startswith("mochila:"))
        
        # Admin callbacks
        dp.callback_query.register(self.handle_free_channel_menu_callback, F.data == "admin:free_channel_menu")
        dp.callback_query.register(self.handle_setup_free_channel_callback, F.data == "admin:setup_free_channel")
        dp.callback_query.register(self.handle_set_wait_time_callback, F.data == "admin:set_wait_time")
        dp.callback_query.register(self.handle_set_wait_time_value_callback, F.data.startswith("admin:set_wait_time_"))
        dp.callback_query.register(self.handle_send_to_free_channel_callback, F.data == "admin:send_to_free_channel")
        dp.message.register(self.handle_post_text, AdminStates.waiting_for_post_text)
        dp.callback_query.register(self.handle_confirm_post_callback, F.data == "admin:confirm_post")
        dp.message.register(self.handle_channel_forward, AdminStates.waiting_for_channel_id, F.forward_from_chat)
        
        # User interface - Main menu callbacks
        dp.callback_query.register(self.handle_main_menu_callback, F.data.startswith("main_menu:"))

        # Admin VIP
        dp.callback_query.register(self.handle_vip_channel_menu_callback, F.data == "admin:vip_channel_menu")
        dp.callback_query.register(self.handle_create_tariff_callback, F.data == "admin:create_tariff")
        dp.message.register(self.handle_tariff_name, AdminStates.waiting_for_tariff_name)
        dp.message.register(self.handle_tariff_price, AdminStates.waiting_for_tariff_price)
        dp.message.register(self.handle_tariff_duration, AdminStates.waiting_for_tariff_duration)
        dp.callback_query.register(self.handle_view_tariff_callback, F.data.startswith("admin:view_tariff_"))
        dp.callback_query.register(self.handle_delete_tariff_callback, F.data.startswith("admin:delete_tariff_"))
        dp.callback_query.register(self.handle_generate_token_callback, F.data.startswith("admin:generate_token_"))

    # Flujo de Admin VIP
    async def handle_vip_channel_menu_callback(self, query: types.CallbackQuery):
        tariffs = self._admin_service.get_all_tariffs()
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
            self._admin_service.create_tariff(data['tariff_name'], data['tariff_price'], duration)
            await message.answer("¡Tarifa creada con éxito!")
            await state.clear()
            # Volver al menú de admin VIP
            tariffs = self._admin_service.get_all_tariffs()
            await message.answer("💎 **Administración Canal VIP**", reply_markup=get_vip_admin_menu_kb(tariffs))
        except ValueError:
            await message.answer("Duración inválida. Por favor, introduce un número entero.")

    async def handle_view_tariff_callback(self, query: types.CallbackQuery):
        tariff_id = int(query.data.split("_")[-1])
        tariff = self._admin_service.get_tariff(tariff_id)
        if tariff:
            text = f"**Tarifa: {tariff['name']}**\n\n"
            text += f"**Precio:** ${tariff['price']}\n"
            text += f"**Duración:** {tariff['duration_days']} días"
            await query.message.edit_text(text, reply_markup=get_tariff_view_kb(tariff_id))
        else:
            await query.answer("Tarifa no encontrada.", show_alert=True)

    async def handle_delete_tariff_callback(self, query: types.CallbackQuery):
        tariff_id = int(query.data.split("_")[-1])
        self._admin_service.delete_tariff(tariff_id)
        await query.answer("Tarifa eliminada con éxito.", show_alert=True)
        # Volver al menú de admin VIP
        tariffs = self._admin_service.get_all_tariffs()
        await query.message.edit_text(
            "💎 **Administración Canal VIP**",
            reply_markup=get_vip_admin_menu_kb(tariffs)
        )

    async def handle_generate_token_callback(self, query: types.CallbackQuery):
        tariff_id = int(query.data.split("_")[-1])
        token = self._admin_service.generate_subscription_token(tariff_id)
        if token:
            bot_username = (await query.bot.get_me()).username
            await query.message.edit_text(f"Token generado: `t.me/{bot_username}?start={token['token']}`")
        else:
            await query.answer("Tarifa no encontrada.", show_alert=True)

def setup_handlers(
    dp: Dispatcher, 
    event_bus: IEventBus, 
    gamification_service: GamificationService, 
    admin_service: AdminService,
    emotional_service: Optional[EmotionalService] = None,
    narrative_service: Optional[NarrativeService] = None,
    channel_service: Optional[ChannelService] = None,
    user_service: Optional[UserService] = None,
    token_service: Optional[Tokeneitor] = None
):
    """Configura todos los handlers de la aplicación."""
    handler_instance = Handlers(
        event_bus, 
        gamification_service, 
        admin_service,
        emotional_service,
        narrative_service,
        channel_service,
        user_service,
        token_service
    )
    handler_instance.register(dp)
