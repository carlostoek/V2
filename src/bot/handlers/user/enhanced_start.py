"""
Handler mejorado para el comando /start con onboarding personalizado.
Parte del sistema UX final de Diana Bot V2.
"""

import logging
from aiogram import types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from typing import Optional, Dict, Any

from src.core.interfaces.IEventBus import IEventBus
from src.modules.events import UserStartedBotEvent
from src.modules.ux.service import UXService
from src.modules.admin.service import AdminService
from src.modules.gamification.service import GamificationService
from src.modules.emotional.service import EmotionalService
from src.modules.token.tokeneitor import Tokeneitor
from src.infrastructure.telegram.keyboards import get_main_menu_keyboard

logger = logging.getLogger(__name__)

class OnboardingStates(StatesGroup):
    """Estados para el flujo de onboarding."""
    onboarding_step = State()
    welcome_reward_claim = State()

class EnhancedStartHandler:
    """Handler mejorado para /start con onboarding personalizado y manejo de tokens."""

    def __init__(
        self,
        event_bus: IEventBus,
        ux_service: UXService,
        admin_service: AdminService,
        gamification_service: Optional[GamificationService] = None,
        emotional_service: Optional[EmotionalService] = None,
        token_service: Optional[Tokeneitor] = None
    ):
        self.event_bus = event_bus
        self.ux_service = ux_service
        self.admin_service = admin_service
        self.gamification_service = gamification_service
        self.emotional_service = emotional_service
        self.token_service = token_service
        self.logger = logging.getLogger(__name__)

    async def handle_start_command(
        self, 
        message: types.Message, 
        command: types.BotCommand, 
        state: FSMContext
    ):
        """
        Maneja el comando /start con onboarding personalizado y validación de tokens.
        
        Args:
            message: Mensaje de Telegram
            command: Comando parseado
            state: Estado FSM del usuario
        """
        try:
            token = command.args
            user_id = message.from_user.id
            username = message.from_user.username
            
            # Clear any existing state
            await state.clear()
            
            # Rastrear interacción del usuario
            await self.ux_service.track_user_interaction(
                user_id, 
                'start_command', 
                {'has_token': bool(token)}
            )

            if token:
                # Flujo de canje de token
                await self._handle_token_redemption(message, token, user_id)
            else:
                # Flujo de onboarding personalizado
                await self._handle_personalized_onboarding(message, state, user_id, username)
                
        except Exception as e:
            self.logger.error(f"Error en handle_start_command para usuario {message.from_user.id}: {e}")
            await self._send_error_recovery_message(message, 'generic_error')

    async def _handle_token_redemption(self, message: types.Message, token: str, user_id: int):
        """Maneja el flujo de canje de tokens."""
        try:
            # Intentar con token service primero
            if self.token_service:
                validated_token = await self.token_service.redeem_token(token, user_id)
                if validated_token:
                    # Token válido - mensaje de éxito personalizado
                    success_message = (
                        "🎉 ¡Increíble! Tu token ha sido canjeado exitosamente.\n\n"
                        "✨ **Ahora tienes acceso premium** con beneficios exclusivos.\n"
                        "👑 Disfruta de contenido VIP, recompensas especiales y mucho más.\n\n"
                        "¡Bienvenida al club premium de Diana!"
                    )
                    
                    keyboard = self._create_vip_welcome_keyboard()
                    await message.answer(success_message, reply_markup=keyboard)
                    return
                    
            # Fallback al admin service
            validated_token = self.admin_service.validate_token(token, user_id)
            if validated_token:
                tariff = self.admin_service.get_tariff(validated_token['tariff_id'])
                if tariff:
                    success_message = (
                        f"🎊 ¡Felicidades! Token canjeado exitosamente.\n\n"
                        f"📋 **Tarifa:** {tariff['name']}\n"
                        f"⏰ **Duración:** {tariff['duration_days']} días\n"
                        f"💎 **Estado:** VIP Premium Activado\n\n"
                        "¡Tu aventura premium comienza ahora!"
                    )
                    keyboard = self._create_vip_welcome_keyboard()
                    await message.answer(success_message, reply_markup=keyboard)
                    return
                    
            # Token inválido
            await self._handle_invalid_token(message, user_id)
            
        except Exception as e:
            self.logger.error(f"Error en _handle_token_redemption: {e}")
            await self._send_error_recovery_message(message, 'validation_error')

    async def _handle_invalid_token(self, message: types.Message, user_id: int):
        """Maneja tokens inválidos con mensaje amigable."""
        user_context = await self.ux_service.get_user_context(user_id)
        user_name = user_context.get('first_name', 'usuario')
        
        error_message = (
            f"Oops {user_name}, ese token no parece funcionar. 😔\n\n"
            "**Posibles causas:**\n"
            "• El token ya fue usado anteriormente\n"
            "• Ha expirado o no es válido\n"
            "• Hay un error de escritura\n\n"
            "💡 **¿Necesitas ayuda?** Contacta al administrador o "
            "comienza tu aventura gratuita mientras tanto."
        )
        
        keyboard = self._create_token_error_keyboard()
        await message.answer(error_message, reply_markup=keyboard)

    async def _handle_personalized_onboarding(
        self, 
        message: types.Message, 
        state: FSMContext, 
        user_id: int, 
        username: str
    ):
        """Maneja el onboarding personalizado basado en el contexto del usuario."""
        try:
            # Publicar evento de inicio de usuario
            event = UserStartedBotEvent(user_id=user_id, username=username)
            await self.event_bus.publish(event)
            
            # Obtener contexto completo del usuario
            user_context = await self.ux_service.get_user_context(user_id)
            
            # Crear flujo de onboarding personalizado
            onboarding_flow = await self.ux_service.create_onboarding_flow(user_context)
            
            if onboarding_flow['type'] == 'new_user_onboarding':
                await self._start_new_user_onboarding(message, state, onboarding_flow, user_context)
            else:
                await self._welcome_returning_user(message, onboarding_flow, user_context)
                
        except Exception as e:
            self.logger.error(f"Error en _handle_personalized_onboarding: {e}")
            await self._fallback_welcome(message, user_id)

    async def _start_new_user_onboarding(
        self, 
        message: types.Message, 
        state: FSMContext,
        onboarding_flow: Dict[str, Any],
        user_context: Dict[str, Any]
    ):
        """Inicia el flujo de onboarding para usuarios nuevos."""
        # Guardar el flujo en el estado
        await state.update_data(
            onboarding_flow=onboarding_flow,
            user_context=user_context,
            current_step=0
        )
        await state.set_state(OnboardingStates.onboarding_step)
        
        # Mostrar primer paso
        first_step = onboarding_flow['steps'][0]
        keyboard = self._create_onboarding_keyboard(first_step, 0, len(onboarding_flow['steps']))
        
        await message.answer(
            first_step['message'],
            reply_markup=keyboard
        )

    async def _welcome_returning_user(
        self, 
        message: types.Message, 
        welcome_flow: Dict[str, Any],
        user_context: Dict[str, Any]
    ):
        """Da la bienvenida a usuarios que regresan con información personalizada."""
        keyboard = self._create_returning_user_keyboard(welcome_flow, user_context)
        
        await message.answer(
            welcome_flow['message'],
            reply_markup=keyboard
        )

    def _create_onboarding_keyboard(self, step: Dict[str, Any], current_step: int, total_steps: int):
        """Crea el teclado para el paso actual del onboarding."""
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        
        builder = InlineKeyboardBuilder()
        
        # Botón principal del paso
        if step.get('has_tutorial'):
            builder.button(text="✨ ¡Comenzar!", callback_data=step['callback_data'])
        else:
            builder.button(text="📖 Continuar", callback_data=step['callback_data'])
        
        # Botones de navegación
        if current_step < total_steps - 1:
            builder.button(text="⏭️ Siguiente", callback_data=f"onboarding:next_{current_step}")
            
        # Botón para saltar (solo después del primer paso)
        if current_step > 0:
            builder.button(text="🚀 Ir al menú", callback_data="onboarding:skip_to_menu")
        
        # Progreso
        builder.button(
            text=f"📍 Paso {current_step + 1} de {total_steps}", 
            callback_data="onboarding:progress"
        )
        
        builder.adjust(1, 2, 1)
        return builder.as_markup()

    def _create_returning_user_keyboard(self, welcome_flow: Dict[str, Any], user_context: Dict[str, Any]):
        """Crea teclado personalizado para usuarios que regresan."""
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        
        builder = InlineKeyboardBuilder()
        
        # Acciones rápidas personalizadas
        quick_actions = welcome_flow.get('quick_actions', [])
        for action in quick_actions[:4]:  # Máximo 4 acciones rápidas
            builder.button(text=action['text'], callback_data=action['callback_data'])
        
        # Acción recomendada destacada
        recommended = welcome_flow.get('recommended_action')
        if recommended:
            builder.button(
                text=f"⭐ {recommended['text']}", 
                callback_data=recommended['callback_data']
            )
        
        # Regalo diario si está disponible
        if welcome_flow.get('has_daily_reward'):
            builder.button(text="🎁 Reclamar Regalo Diario", callback_data="gamification:daily_reward")
        
        # Menú principal
        builder.button(text="🏠 Menú Principal", callback_data="main_menu:show")
        
        # Ajustar layout
        if len(quick_actions) <= 2:
            builder.adjust(len(quick_actions), 1, 1, 1)
        else:
            builder.adjust(2, 2, 1, 1, 1)
        
        return builder.as_markup()

    def _create_vip_welcome_keyboard(self):
        """Crea teclado especial para usuarios VIP después de canje de token."""
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        
        builder = InlineKeyboardBuilder()
        builder.button(text="👑 Panel VIP", callback_data="vip:dashboard")
        builder.button(text="💎 Contenido Exclusivo", callback_data="vip:exclusive_content")
        builder.button(text="🎁 Regalos VIP", callback_data="vip:special_rewards")
        builder.button(text="🏠 Menú Principal", callback_data="main_menu:show")
        builder.adjust(1, 2, 1)
        return builder.as_markup()

    def _create_token_error_keyboard(self):
        """Crea teclado para el caso de token inválido."""
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        
        builder = InlineKeyboardBuilder()
        builder.button(text="🆓 Comenzar Aventura Gratuita", callback_data="start:free_mode")
        builder.button(text="❓ Ayuda con Tokens", callback_data="help:tokens")
        builder.button(text="📞 Contactar Admin", callback_data="help:contact_admin")
        builder.adjust(1, 2)
        return builder.as_markup()

    async def handle_onboarding_callback(self, query: types.CallbackQuery, state: FSMContext):
        """Maneja los callbacks del proceso de onboarding."""
        try:
            action = query.data.replace("onboarding:", "")
            state_data = await state.get_data()
            
            if not state_data or 'onboarding_flow' not in state_data:
                await query.answer("El proceso de onboarding ha expirado. Usa /start para comenzar de nuevo.")
                return
            
            onboarding_flow = state_data['onboarding_flow']
            current_step = state_data.get('current_step', 0)
            
            if action.startswith('step_'):
                step_num = int(action.split('_')[1]) - 1
                await self._handle_onboarding_step(query, state, step_num, onboarding_flow)
                
            elif action.startswith('next_'):
                next_step = int(action.split('_')[1]) + 1
                await self._handle_onboarding_step(query, state, next_step, onboarding_flow)
                
            elif action == 'claim_welcome_reward':
                await self._handle_welcome_reward_claim(query, state, onboarding_flow)
                
            elif action == 'skip_to_menu':
                await self._complete_onboarding(query, state, skip=True)
                
            elif action == 'progress':
                total_steps = len(onboarding_flow['steps'])
                await query.answer(f"Progreso: {current_step + 1}/{total_steps} pasos completados")
                
        except Exception as e:
            self.logger.error(f"Error en handle_onboarding_callback: {e}")
            await query.answer("Ocurrió un error. Intenta nuevamente.")

    async def _handle_onboarding_step(
        self, 
        query: types.CallbackQuery, 
        state: FSMContext, 
        step_index: int,
        onboarding_flow: Dict[str, Any]
    ):
        """Maneja un paso específico del onboarding."""
        steps = onboarding_flow['steps']
        
        if step_index >= len(steps):
            await self._complete_onboarding(query, state)
            return
        
        # Actualizar estado
        await state.update_data(current_step=step_index)
        
        step = steps[step_index]
        keyboard = self._create_onboarding_keyboard(step, step_index, len(steps))
        
        try:
            await query.message.edit_text(
                step['message'],
                reply_markup=keyboard
            )
        except Exception:
            # Si falla la edición, enviar nuevo mensaje
            await query.message.answer(
                step['message'],
                reply_markup=keyboard
            )
        
        await query.answer()

    async def _handle_welcome_reward_claim(
        self, 
        query: types.CallbackQuery, 
        state: FSMContext,
        onboarding_flow: Dict[str, Any]
    ):
        """Maneja la reclamación del regalo de bienvenida."""
        user_id = query.from_user.id
        reward = onboarding_flow.get('welcome_reward', {})
        
        try:
            # Dar recompensa a través del servicio de gamificación
            if self.gamification_service and reward.get('points'):
                points_result = await self.gamification_service.add_points(
                    user_id, 
                    reward['points'], 
                    "welcome_bonus"
                )
                
            reward_message = (
                "🎉 ¡Regalo de bienvenida entregado!\n\n"
                f"🎊 **{reward.get('points', 0)} puntos** añadidos a tu cuenta\n"
                "🎯 **Misión especial** desbloqueada\n"
                "🔮 **Objeto mágico** añadido a tu mochila\n\n"
                "¡Ya puedes comenzar tu aventura con Diana!"
            )
            
            keyboard = self._create_post_reward_keyboard()
            
            await query.message.edit_text(reward_message, reply_markup=keyboard)
            await query.answer("¡Recompensa reclamada!")
            
            # Completar onboarding
            await state.update_data(onboarding_completed=True)
            
        except Exception as e:
            self.logger.error(f"Error claiming welcome reward: {e}")
            await query.answer("Error al entregar el regalo. Contacta al administrador.")

    def _create_post_reward_keyboard(self):
        """Crea teclado después de reclamar el regalo de bienvenida."""
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        
        builder = InlineKeyboardBuilder()
        builder.button(text="📜 Comenzar Historia", callback_data="main_menu:narrative")
        builder.button(text="🎮 Explorar Gamificación", callback_data="gamification:main")
        builder.button(text="🎒 Ver Mi Mochila", callback_data="main_menu:inventory")
        builder.button(text="🏠 Menú Principal", callback_data="main_menu:show")
        builder.adjust(1, 2, 1)
        return builder.as_markup()

    async def _complete_onboarding(self, query: types.CallbackQuery, state: FSMContext, skip: bool = False):
        """Completa el proceso de onboarding."""
        await state.clear()
        
        if skip:
            message = (
                "¡Perfecto! Has saltado el tutorial.\n\n"
                "🎯 Recuerda que siempre puedes usar /ayuda para obtener información.\n"
                "¡Que disfrutes tu aventura con Diana!"
            )
        else:
            message = (
                "🎊 ¡Onboarding completado exitosamente!\n\n"
                "Ya conoces todo lo básico para disfrutar tu aventura. "
                "Recuerda que siempre estaré aquí para ayudarte.\n\n"
                "¿Lista para tu primera gran aventura?"
            )
        
        keyboard = get_main_menu_keyboard()
        
        try:
            await query.message.edit_text(message, reply_markup=keyboard)
        except Exception:
            await query.message.answer(message, reply_markup=keyboard)
        
        await query.answer("¡Bienvenida a Diana!")

    async def _fallback_welcome(self, message: types.Message, user_id: int):
        """Mensaje de bienvenida de emergencia si falla el onboarding."""
        try:
            user_context = await self.ux_service.get_user_context(user_id)
            user_name = user_context.get('first_name', 'usuario')
            
            fallback_message = (
                f"¡Hola {user_name}! 👋\n\n"
                "Bienvenida a Diana Bot V2. Soy tu compañera en esta aventura interactiva "
                "llena de historias, juegos y experiencias únicas.\n\n"
                "🌟 Usa los botones de abajo para comenzar tu aventura."
            )
            
            await message.answer(fallback_message, reply_markup=get_main_menu_keyboard())
            
        except Exception as e:
            self.logger.error(f"Error en _fallback_welcome: {e}")
            await message.answer(
                "¡Bienvenida a Diana Bot V2! ¿Qué te gustaría hacer hoy?",
                reply_markup=get_main_menu_keyboard()
            )

    async def _send_error_recovery_message(self, message: types.Message, error_type: str):
        """Envía un mensaje de error amigable con opciones de recuperación."""
        try:
            user_context = await self.ux_service.get_user_context(message.from_user.id)
            error_message = self.ux_service.create_error_recovery_message(error_type, user_context)
            
            keyboard = self._create_error_recovery_keyboard()
            await message.answer(error_message, reply_markup=keyboard)
            
        except Exception:
            await message.answer(
                "Ups, algo salió mal. Pero no te preocupes, puedes continuar con tu aventura.",
                reply_markup=get_main_menu_keyboard()
            )

    def _create_error_recovery_keyboard(self):
        """Crea teclado para recuperación de errores."""
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        
        builder = InlineKeyboardBuilder()
        builder.button(text="🔄 Intentar de nuevo", callback_data="start:retry")
        builder.button(text="🏠 Menú Principal", callback_data="main_menu:show")
        builder.button(text="❓ Obtener Ayuda", callback_data="help:main")
        builder.adjust(1, 2)
        return builder.as_markup()

    def register_handlers(self, dp, router):
        """Registra todos los handlers del sistema de start mejorado."""
        # Comando /start principal
        dp.message.register(
            self.handle_start_command, 
            CommandStart()
        )
        
        # Callbacks de onboarding
        dp.callback_query.register(
            self.handle_onboarding_callback,
            F.data.startswith("onboarding:")
        )
        
        # Callbacks de start específicos
        dp.callback_query.register(
            self._handle_start_callbacks,
            F.data.startswith("start:")
        )

    async def _handle_start_callbacks(self, query: types.CallbackQuery):
        """Maneja callbacks específicos del sistema de start."""
        action = query.data.replace("start:", "")
        
        if action == "free_mode":
            await self._handle_personalized_onboarding(
                query.message, 
                None, 
                query.from_user.id, 
                query.from_user.username
            )
        elif action == "retry":
            # Simular comando /start sin argumentos
            fake_command = types.BotCommand(command="start", description="")
            await self.handle_start_command(query.message, fake_command, None)
        
        await query.answer()