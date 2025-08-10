"""
Sistema de Navegación de Historia Mejorado

Handler avanzado para el comando /historia que proporciona navegación narrativa
interactiva con decisiones que afectan la progresión y personalidad de Diana.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from aiogram import types, Router
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup

from src.modules.narrative.service import NarrativeService
from src.modules.emotional.service import EmotionalService
from src.modules.emotional.diana_state import EmotionalTrigger
from src.bot.handlers.narrative.contextual_responses import DianaContextualResponseSystem

logger = logging.getLogger(__name__)
router = Router()


class StoryNavigationSystem:
    """
    Sistema avanzado de navegación narrativa.
    
    Características:
    - Navegación por fragmentos con decisiones consecuentes
    - UI adaptativa según el progreso del usuario
    - Integración con sistema emocional
    - Memory system - Diana recuerda decisiones anteriores
    - Fragmentos dinámicos según estado emocional
    """
    
    def __init__(self, 
                 narrative_service: NarrativeService,
                 emotional_service: EmotionalService,
                 diana_system: DianaContextualResponseSystem):
        self.narrative_service = narrative_service
        self.emotional_service = emotional_service
        self.diana_system = diana_system
        
        # Cache de navegación por usuario
        self.navigation_history: Dict[int, List[str]] = {}
        self.user_decisions_impact: Dict[int, Dict[str, Any]] = {}
    
    async def show_story_hub(self, message: Message) -> None:
        """
        Muestra el hub principal de navegación narrativa.
        
        Args:
            message: Mensaje del comando /historia
        """
        user_id = message.from_user.id
        
        try:
            # Obtener contexto del usuario
            current_fragment = await self.narrative_service.get_user_fragment(user_id)
            lore_pieces = await self.narrative_service.get_user_lore_pieces(user_id)
            emotional_modifiers = await self.emotional_service.get_response_modifiers(user_id)
            
            # Generar respuesta contextual de Diana
            diana_response = await self.diana_system.generate_contextual_response(
                user_id=user_id,
                context_type='story_access',
                context_data={
                    'has_active_fragment': current_fragment is not None,
                    'lore_count': len(lore_pieces)
                }
            )
            
            # Construir mensaje principal
            title = "📖 **La Historia de Diana**\n\n"
            
            # Respuesta personalizada de Diana
            diana_section = f"*Diana susurra:* \"{diana_response}\"\n\n"
            
            # Estado actual
            if current_fragment:
                progress_section = (
                    f"📍 **Fragmento Actual:** {current_fragment['title']}\n"
                    f"🎭 **Personaje:** {current_fragment['character'].title()}\n"
                )
                
                if current_fragment.get('choices'):
                    progress_section += f"🔀 **Decisiones disponibles:** {len(current_fragment['choices'])}\n"
            else:
                progress_section = "📍 **Estado:** Esperando nueva aventura narrativa...\n"
            
            # Progreso general
            stats_section = (
                f"🗝️ **Pistas recolectadas:** {len(lore_pieces)}\n"
                f"😌 **Estado emocional:** {emotional_modifiers.get('current_state', 'Enigmática').title()}\n\n"
            )
            
            # Construir mensaje completo
            full_message = title + diana_section + progress_section + stats_section
            
            # Crear keyboard adaptativo
            keyboard = await self._create_story_hub_keyboard(user_id, current_fragment, lore_pieces)
            
            await message.answer(
                full_message,
                parse_mode="Markdown",
                reply_markup=keyboard
            )
        
        except Exception as e:
            logger.error(f"Error mostrando hub de historia para usuario {user_id}: {e}")
            await message.answer(
                "📖 *La Historia*\n\n"
                "Ups... parece que Diana está organizando sus recuerdos. "
                "Inténtalo de nuevo en un momento. 🌙",
                parse_mode="Markdown"
            )
    
    async def _create_story_hub_keyboard(self, 
                                       user_id: int, 
                                       current_fragment: Optional[Dict],
                                       lore_pieces: List[Dict]) -> InlineKeyboardMarkup:
        """Crea keyboard adaptativo para el hub de historia."""
        builder = InlineKeyboardBuilder()
        
        # Botón principal de continuar historia
        if current_fragment:
            builder.button(
                text="📖 Continuar Historia",
                callback_data="diana:continue_story"
            )
        else:
            builder.button(
                text="🌟 Comenzar Nueva Historia",
                callback_data="diana:start_new_story"
            )
        
        # Exploración de pistas (solo si tiene pistas)
        if lore_pieces:
            builder.button(
                text=f"🗝️ Examinar Pistas ({len(lore_pieces)})",
                callback_data="diana:explore_lore"
            )
        
        # Memoria de Diana (decisiones anteriores)
        if user_id in self.user_decisions_impact and self.user_decisions_impact[user_id]:
            builder.button(
                text="💭 Recordar Decisiones",
                callback_data="diana:recall_decisions"
            )
        
        # Explorar fragmentos desbloqueados
        builder.button(
            text="📜 Fragmentos Visitados",
            callback_data="diana:visited_fragments"
        )
        
        # Configuración narrativa personalizada
        builder.button(
            text="⚙️ Preferencias Narrativas",
            callback_data="diana:story_preferences"
        )
        
        # Botón de volver
        builder.button(
            text="⬅️ Menú Principal",
            callback_data="diana:back_to_main"
        )
        
        # Organizar botones en filas
        builder.adjust(1)  # Una opción por fila
        
        return builder.as_markup()
    
    async def continue_story(self, callback: CallbackQuery) -> None:
        """Continúa la historia actual del usuario."""
        user_id = callback.from_user.id
        
        try:
            # Obtener fragmento actual
            current_fragment = await self.narrative_service.get_user_fragment(user_id)
            
            if not current_fragment:
                await callback.answer(
                    "No hay historia activa. ¡Comienza una nueva aventura!",
                    show_alert=True
                )
                return
            
            # Generar respuesta contextual de Diana para la continuación
            diana_response = await self.diana_system.generate_contextual_response(
                user_id=user_id,
                context_type='story_continuation',
                context_data={
                    'fragment_title': current_fragment['title'],
                    'character': current_fragment['character']
                }
            )
            
            # Mostrar fragmento con contexto emocional
            await self._display_story_fragment(callback, current_fragment, diana_response)
            
            # Registrar en historial de navegación
            self._add_to_navigation_history(user_id, current_fragment['key'])
        
        except Exception as e:
            logger.error(f"Error continuando historia para usuario {user_id}: {e}")
            await callback.answer("Error al cargar la historia", show_alert=True)
    
    async def _display_story_fragment(self, 
                                    callback: CallbackQuery,
                                    fragment: Dict,
                                    diana_response: str = None) -> None:
        """Muestra un fragmento de historia con formato mejorado."""
        
        # Obtener emoji del personaje
        character_emoji = self._get_character_emoji(fragment['character'])
        
        # Construir mensaje del fragmento
        fragment_text = (
            f"{character_emoji} **{fragment['title']}**\n\n"
            f"*{fragment['character'].title()} dice:*\n"
            f"\"{fragment['text']}\"\n\n"
        )
        
        # Agregar respuesta contextual de Diana si existe
        if diana_response:
            fragment_text += f"💫 *Diana comenta: \"{diana_response}\"*\n\n"
        
        # Información adicional si es fragmento VIP
        if fragment.get('is_vip_only', False):
            fragment_text += "👑 *Contenido VIP* - Solo para miembros especiales\n\n"
        
        # Crear keyboard con decisiones
        keyboard = await self._create_story_choices_keyboard(fragment)
        
        await callback.message.edit_text(
            fragment_text,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        
        await callback.answer()
    
    async def _create_story_choices_keyboard(self, fragment: Dict) -> InlineKeyboardMarkup:
        """Crea keyboard con las opciones de decisión del fragmento."""
        builder = InlineKeyboardBuilder()
        
        # Agregar opciones de decisión si existen
        if fragment.get('choices'):
            for choice in fragment['choices']:
                # Verificar si la opción requiere items especiales
                choice_text = choice['text']
                
                if choice.get('required_items'):
                    choice_text += " 🔐"  # Indicar que requiere items
                
                builder.button(
                    text=choice_text,
                    callback_data=f"diana:make_choice:{choice['id']}"
                )
        
        # Opciones adicionales
        builder.row()  # Nueva fila
        
        # Botón de exploración profunda (usar pistas para más información)
        builder.button(
            text="🔍 Explorar Profundamente",
            callback_data=f"diana:deep_explore:{fragment['key']}"
        )
        
        # Botón para reflexionar (triggera respuesta emocional)
        builder.button(
            text="💭 Reflexionar",
            callback_data=f"diana:reflect:{fragment['key']}"
        )
        
        builder.row()  # Nueva fila
        
        # Navegación
        builder.button(
            text="⬅️ Volver al Hub",
            callback_data="diana:back_to_story_hub"
        )
        
        return builder.as_markup()
    
    async def make_narrative_choice(self, callback: CallbackQuery, choice_id: int) -> None:
        """Procesa una decisión narrativa del usuario."""
        user_id = callback.from_user.id
        
        try:
            # Procesar decisión en el servicio narrativo
            success = await self.narrative_service.make_narrative_choice(user_id, choice_id)
            
            if not success:
                await callback.answer("No se pudo procesar tu decisión", show_alert=True)
                return
            
            # Registrar impacto de la decisión
            await self._record_decision_impact(user_id, choice_id)
            
            # Generar respuesta contextual de Diana a la decisión
            diana_response = await self.diana_system.generate_contextual_response(
                user_id=user_id,
                context_type='decision_made',
                context_data={
                    'choice_id': choice_id,
                    'decision_count': len(self.user_decisions_impact.get(user_id, {}))
                }
            )
            
            # Mostrar resultado de la decisión con un mensaje intermedio
            await callback.message.edit_text(
                f"⚡ **Decisión Tomada**\n\n"
                f"💫 *Diana observa tu elección...*\n"
                f"\"{diana_response}\"\n\n"
                f"🌀 *La historia continúa...*",
                parse_mode="Markdown"
            )
            
            # Esperar un momento para crear suspense
            await asyncio.sleep(2)
            
            # Mostrar nuevo fragmento
            new_fragment = await self.narrative_service.get_user_fragment(user_id)
            if new_fragment:
                await self._display_story_fragment(callback, new_fragment)
            else:
                await callback.message.edit_text(
                    "📖 **Final del Capítulo**\n\n"
                    "Has llegado al final de este fragmento de la historia. "
                    "Nuevas aventuras te esperan pronto...\n\n"
                    "💫 *Diana sonríe misteriosamente*",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardBuilder().button(
                        text="⬅️ Volver al Hub",
                        callback_data="diana:back_to_story_hub"
                    ).as_markup()
                )
        
        except Exception as e:
            logger.error(f"Error procesando decisión narrativa para usuario {user_id}: {e}")
            await callback.answer("Error al procesar decisión", show_alert=True)
    
    async def deep_explore(self, callback: CallbackQuery, fragment_key: str) -> None:
        """Permite exploración profunda usando pistas narrativas."""
        user_id = callback.from_user.id
        
        try:
            # Obtener pistas del usuario
            lore_pieces = await self.narrative_service.get_user_lore_pieces(user_id)
            
            if not lore_pieces:
                await callback.answer(
                    "Necesitas pistas narrativas para explorar más profundamente",
                    show_alert=True
                )
                return
            
            # Generar información adicional basada en las pistas
            exploration_text = await self._generate_deep_exploration(fragment_key, lore_pieces)
            
            # Generar respuesta de Diana
            diana_response = await self.diana_system.generate_contextual_response(
                user_id=user_id,
                context_type='deep_exploration',
                context_data={
                    'fragment_key': fragment_key,
                    'lore_count': len(lore_pieces)
                }
            )
            
            await callback.message.edit_text(
                f"🔍 **Exploración Profunda**\n\n"
                f"{exploration_text}\n\n"
                f"💫 *Diana susurra:* \"{diana_response}\"\n\n"
                f"🗝️ *Has usado tus pistas para descubrir secretos ocultos*",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardBuilder().button(
                    text="⬅️ Volver al Fragmento",
                    callback_data="diana:continue_story"
                ).as_markup()
            )
            
            await callback.answer()
        
        except Exception as e:
            logger.error(f"Error en exploración profunda: {e}")
            await callback.answer("Error en la exploración", show_alert=True)
    
    async def reflect_on_fragment(self, callback: CallbackQuery, fragment_key: str) -> None:
        """Permite al usuario reflexionar sobre un fragmento."""
        user_id = callback.from_user.id
        
        try:
            # Trigger respuesta emocional reflexiva
            await self.emotional_service.trigger_state_change(
                user_id=user_id,
                trigger=EmotionalTrigger.INTROSPECTION
            )
            
            # Generar reflexión personalizada
            diana_response = await self.diana_system.generate_contextual_response(
                user_id=user_id,
                context_type='reflection',
                context_data={
                    'fragment_key': fragment_key
                }
            )
            
            # Mostrar mensaje reflexivo
            await callback.message.edit_text(
                f"💭 **Momento de Reflexión**\n\n"
                f"*Te tomas un momento para reflexionar sobre lo que has vivido...*\n\n"
                f"🌙 *Diana te acompaña en silencio y luego dice:*\n"
                f"\"{diana_response}\"\n\n"
                f"✨ *La reflexión a veces revela verdades ocultas*",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardBuilder().button(
                    text="⬅️ Continuar Historia",
                    callback_data="diana:continue_story"
                ).as_markup()
            )
            
            await callback.answer()
        
        except Exception as e:
            logger.error(f"Error en reflexión: {e}")
            await callback.answer("Error en la reflexión", show_alert=True)
    
    async def _record_decision_impact(self, user_id: int, choice_id: int) -> None:
        """Registra el impacto de una decisión para memoria futura."""
        if user_id not in self.user_decisions_impact:
            self.user_decisions_impact[user_id] = {}
        
        timestamp = datetime.now()
        
        self.user_decisions_impact[user_id][f"choice_{choice_id}"] = {
            'choice_id': choice_id,
            'timestamp': timestamp,
            'emotional_state_at_choice': await self.emotional_service.get_response_modifiers(user_id)
        }
    
    async def _generate_deep_exploration(self, fragment_key: str, lore_pieces: List[Dict]) -> str:
        """Genera texto de exploración profunda basado en pistas."""
        
        # Combinaciones de pistas que revelan información especial
        exploration_texts = {
            'historia_diana': "Al examinar más de cerca, notas detalles sobre el pasado de Diana...",
            'misterio_kinkys': "Tus pistas sobre Los Kinkys revelan conexiones ocultas...",
            'secreto_lucien': "Los fragmentos sobre Lucien cobran nuevo significado aquí...",
            'simbolo_mariposa': "El símbolo de la mariposa aparece sutilmente en este lugar...",
            'ritual_iniciacion': "Reconoces elementos del ritual de iniciación..."
        }
        
        # Buscar pistas relevantes
        relevant_lore = [piece for piece in lore_pieces 
                        if piece['key'] in exploration_texts]
        
        if relevant_lore:
            # Usar pista más relevante
            lore_key = relevant_lore[0]['key']
            return exploration_texts[lore_key]
        else:
            # Texto genérico basado en cantidad de pistas
            if len(lore_pieces) > 3:
                return "Tu experiencia narrativa te permite ver detalles que otros pasarían por alto..."
            else:
                return "Aunque no tienes muchas pistas aún, tu intuición te guía..."
    
    def _get_character_emoji(self, character: str) -> str:
        """Obtiene emoji apropiado para cada personaje."""
        emojis = {
            'diana': '🌸',
            'lucien': '🎭',
            'sistema': '🤖',
            'narrador': '📖',
            'desconocido': '❓'
        }
        return emojis.get(character.lower(), '👤')
    
    def _add_to_navigation_history(self, user_id: int, fragment_key: str) -> None:
        """Agrega fragmento al historial de navegación."""
        if user_id not in self.navigation_history:
            self.navigation_history[user_id] = []
        
        # Agregar al historial, manteniendo solo últimos 10
        history = self.navigation_history[user_id]
        if fragment_key not in history:  # Evitar duplicados consecutivos
            history.append(fragment_key)
            if len(history) > 10:
                history.pop(0)


# Registro de handlers
@router.message(Command("historia"))
async def handle_story_command(message: Message, 
                             narrative_service: NarrativeService,
                             emotional_service: EmotionalService,
                             diana_system: DianaContextualResponseSystem):
    """Handler principal para el comando /historia."""
    story_system = StoryNavigationSystem(narrative_service, emotional_service, diana_system)
    await story_system.show_story_hub(message)


@router.callback_query(lambda c: c.data.startswith("diana:"))
async def handle_diana_callbacks(callback: CallbackQuery,
                               narrative_service: NarrativeService,
                               emotional_service: EmotionalService,
                               diana_system: DianaContextualResponseSystem):
    """Handler para todos los callbacks de Diana."""
    
    story_system = StoryNavigationSystem(narrative_service, emotional_service, diana_system)
    
    action = callback.data.replace("diana:", "")
    
    if action == "continue_story":
        await story_system.continue_story(callback)
    
    elif action == "back_to_story_hub":
        # Recrear el hub de historia
        await story_system.show_story_hub(callback.message)
        await callback.answer()
    
    elif action.startswith("make_choice:"):
        choice_id = int(action.split(":")[1])
        await story_system.make_narrative_choice(callback, choice_id)
    
    elif action.startswith("deep_explore:"):
        fragment_key = action.split(":", 1)[1]
        await story_system.deep_explore(callback, fragment_key)
    
    elif action.startswith("reflect:"):
        fragment_key = action.split(":", 1)[1]
        await story_system.reflect_on_fragment(callback, fragment_key)
    
    else:
        await callback.answer("Función en desarrollo...", show_alert=True)


def register_story_navigation_handlers(dp, narrative_service, emotional_service, diana_system):
    """Registra los handlers de navegación narrativa."""
    dp.include_router(router)
    
    # Proporcionar dependencias a través del contexto
    # En una implementación real, esto se haría a través del sistema DI
    pass