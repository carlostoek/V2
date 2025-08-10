"""
Middleware Diana Context

Middleware que intercepta todos los mensajes y proporciona contexto emocional
y respuestas personalizadas basadas en la personalidad de Diana.
"""

import logging
from typing import Dict, Any, Callable, Awaitable
from datetime import datetime, timedelta
from aiogram import BaseMiddleware
from aiogram.types import Message, Update, CallbackQuery

from src.modules.emotional.service import EmotionalService
from src.modules.narrative.service import NarrativeService
from src.bot.handlers.narrative.contextual_responses import DianaContextualResponseSystem
from src.core.interfaces.IEventBus import IEventBus

logger = logging.getLogger(__name__)


class DianaContextMiddleware(BaseMiddleware):
    """
    Middleware que proporciona contexto emocional y narrativo a todos los mensajes,
    permitiendo que Diana tenga personalidad real y consciente.
    
    Responsabilidades:
    - Interceptar todos los mensajes del usuario
    - Proporcionar contexto emocional actual
    - Generar respuestas contextuales cuando sea apropiado
    - Mantener memoria de interacciones del usuario
    - Detectar patrones de comportamiento
    """
    
    def __init__(self, 
                 event_bus: IEventBus,
                 emotional_service: EmotionalService,
                 narrative_service: NarrativeService):
        self.event_bus = event_bus
        self.emotional_service = emotional_service
        self.narrative_service = narrative_service
        
        # Inicializar sistema de respuestas contextuales
        self.diana_system = DianaContextualResponseSystem(
            event_bus=event_bus,
            emotional_service=emotional_service,
            narrative_service=narrative_service
        )
        
        # Cache de contexto por usuario
        self.user_context_cache: Dict[int, Dict[str, Any]] = {}
        
        # Rastreo de comandos recientes
        self.recent_commands: Dict[int, str] = {}
        
        super().__init__()
    
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        """
        Procesa el evento proporcionando contexto de Diana.
        
        Args:
            handler: Handler principal a ejecutar
            event: Update de Telegram
            data: Datos del contexto
            
        Returns:
            Resultado del handler principal
        """
        user_id = None
        
        # Extraer información del usuario según el tipo de evento
        if event.message:
            user_id = event.message.from_user.id
            await self._process_message_context(event.message, data)
        elif event.callback_query:
            user_id = event.callback_query.from_user.id
            await self._process_callback_context(event.callback_query, data)
        
        # Si tenemos user_id, proporcionar contexto Diana
        if user_id:
            diana_context = await self._get_diana_context(user_id)
            data['diana_context'] = diana_context
            data['diana_system'] = self.diana_system
        
        # Ejecutar handler principal
        result = await handler(event, data)
        
        # Post-procesamiento después del handler
        if user_id:
            await self._post_process_interaction(user_id, event, data)
        
        return result
    
    async def _process_message_context(self, message: Message, data: Dict[str, Any]):
        """Procesa el contexto de un mensaje."""
        user_id = message.from_user.id
        
        # Determinar tipo de interacción
        interaction_type = self._classify_interaction(message)
        
        # Actualizar caché de contexto
        await self._update_user_context(user_id, {
            'last_message_type': interaction_type,
            'last_message_text': message.text,
            'last_interaction_time': datetime.now(),
            'chat_type': message.chat.type
        })
        
        # Si es un comando, rastrearlo
        if message.text and message.text.startswith('/'):
            command = message.text.split()[0]
            self.recent_commands[user_id] = command
        
        logger.debug(f"Contexto de mensaje procesado para usuario {user_id}: {interaction_type}")
    
    async def _process_callback_context(self, callback: CallbackQuery, data: Dict[str, Any]):
        """Procesa el contexto de un callback."""
        user_id = callback.from_user.id
        
        # Determinar categoría del callback
        callback_category = self._classify_callback(callback.data)
        
        # Actualizar caché de contexto
        await self._update_user_context(user_id, {
            'last_callback_type': callback_category,
            'last_callback_data': callback.data,
            'last_interaction_time': datetime.now()
        })
        
        logger.debug(f"Contexto de callback procesado para usuario {user_id}: {callback_category}")
    
    async def _get_diana_context(self, user_id: int) -> Dict[str, Any]:
        """
        Obtiene el contexto completo de Diana para un usuario.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Diccionario con contexto completo de Diana
        """
        try:
            # Obtener estado emocional actual
            emotional_modifiers = await self.emotional_service.get_response_modifiers(user_id)
            emotional_stats = await self.emotional_service.get_user_emotional_stats(user_id)
            
            # Obtener progreso narrativo
            current_fragment = await self.narrative_service.get_user_fragment(user_id)
            lore_pieces = await self.narrative_service.get_user_lore_pieces(user_id)
            
            # Contexto de usuario desde caché
            user_context = self.user_context_cache.get(user_id, {})
            
            # Determinar personalidad actual
            personality_traits = self._determine_personality_traits(
                emotional_stats, 
                user_context, 
                len(lore_pieces)
            )
            
            # Determinar si debería enviar respuesta contextual automática
            should_respond = await self._should_send_contextual_response(user_id, user_context)
            
            return {
                'emotional_state': emotional_stats.get('current_state'),
                'emotional_intensity': emotional_stats.get('intensity_level', 0.5),
                'emotional_modifiers': emotional_modifiers,
                'narrative_progress': {
                    'current_fragment': current_fragment,
                    'lore_pieces_count': len(lore_pieces),
                    'fragments_visited': current_fragment.get('visited_fragments', []) if current_fragment else []
                },
                'personality_traits': personality_traits,
                'interaction_history': user_context,
                'should_respond_contextually': should_respond,
                'recent_command': self.recent_commands.get(user_id),
                'time_of_day': self.diana_system._get_time_context(),
                'interaction_frequency': self.diana_system._get_interaction_frequency(user_id)
            }
        
        except Exception as e:
            logger.error(f"Error obteniendo contexto Diana para usuario {user_id}: {e}")
            return {
                'emotional_state': 'enigmatica',
                'emotional_intensity': 0.5,
                'personality_traits': ['mysterious', 'gentle'],
                'should_respond_contextually': False
            }
    
    async def _update_user_context(self, user_id: int, context_update: Dict[str, Any]):
        """Actualiza el contexto del usuario en el caché."""
        if user_id not in self.user_context_cache:
            self.user_context_cache[user_id] = {}
        
        self.user_context_cache[user_id].update(context_update)
        
        # Limpiar contexto antiguo (mantener solo últimas 24 horas de datos)
        await self._cleanup_old_context(user_id)
    
    async def _cleanup_old_context(self, user_id: int):
        """Limpia contexto antiguo del caché."""
        context = self.user_context_cache.get(user_id, {})
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        # Mantener solo interacciones recientes
        if 'last_interaction_time' in context:
            if context['last_interaction_time'] < cutoff_time:
                # Mantener solo información esencial
                essential_context = {
                    'total_interactions': context.get('total_interactions', 0),
                    'favorite_features': context.get('favorite_features', []),
                    'personality_preferences': context.get('personality_preferences', {})
                }
                self.user_context_cache[user_id] = essential_context
    
    def _classify_interaction(self, message: Message) -> str:
        """Clasifica el tipo de interacción basándose en el mensaje."""
        if not message.text:
            return 'non_text'
        
        text = message.text.lower()
        
        # Comandos
        if text.startswith('/'):
            return 'command'
        
        # Saludos
        greeting_words = ['hola', 'hello', 'hi', 'buenos días', 'buenas tardes', 'buenas noches']
        if any(greeting in text for greeting in greeting_words):
            return 'greeting'
        
        # Preguntas
        if '?' in text or text.startswith(('qué', 'cómo', 'cuándo', 'dónde', 'por qué', 'quién')):
            return 'question'
        
        # Expresiones emocionales
        emotional_words = ['me gusta', 'amo', 'odio', 'me encanta', 'genial', 'increíble']
        if any(emotion in text for emotion in emotional_words):
            return 'emotional_expression'
        
        # Respuestas a opciones narrativas
        if any(word in text for word in ['sí', 'no', 'tal vez', 'acepto', 'rechazo']):
            return 'narrative_response'
        
        return 'casual_message'
    
    def _classify_callback(self, callback_data: str) -> str:
        """Clasifica el tipo de callback basándose en los datos."""
        if callback_data.startswith('diana:'):
            return 'diana_action'
        elif callback_data.startswith('narrative:'):
            return 'narrative_navigation'
        elif callback_data.startswith('choice:'):
            return 'narrative_choice'
        elif callback_data.startswith('mochila:'):
            return 'lore_exploration'
        elif callback_data.startswith('shop:'):
            return 'commerce'
        elif callback_data.startswith('mission:'):
            return 'gamification'
        else:
            return 'general_navigation'
    
    def _determine_personality_traits(self, emotional_stats: Dict, 
                                   user_context: Dict, 
                                   lore_count: int) -> List[str]:
        """Determina los rasgos de personalidad actuales de Diana."""
        traits = []
        
        # Basado en estado emocional
        current_state = emotional_stats.get('current_state', 'enigmatica')
        
        state_traits = {
            'vulnerable': ['gentle', 'caring', 'empathetic'],
            'enigmatica': ['mysterious', 'intriguing', 'thoughtful'],
            'provocadora': ['playful', 'flirty', 'confident'],
            'analitica': ['intellectual', 'analytical', 'logical'],
            'silenciosa': ['quiet', 'mysterious', 'contemplative']
        }
        
        traits.extend(state_traits.get(current_state, ['mysterious']))
        
        # Basado en progreso narrativo
        if lore_count > 5:
            traits.append('knowledgeable')
        elif lore_count > 2:
            traits.append('experienced')
        else:
            traits.append('discovering')
        
        # Basado en frecuencia de interacción
        recent_interactions = user_context.get('total_interactions', 0)
        if recent_interactions > 20:
            traits.extend(['familiar', 'comfortable'])
        elif recent_interactions > 5:
            traits.extend(['friendly', 'welcoming'])
        else:
            traits.extend(['curious', 'cautious'])
        
        return list(set(traits))  # Remover duplicados
    
    async def _should_send_contextual_response(self, user_id: int, 
                                             user_context: Dict) -> bool:
        """Determina si debería enviar una respuesta contextual automática."""
        
        # No responder si la última interacción fue muy reciente (menos de 30 segundos)
        last_interaction = user_context.get('last_interaction_time')
        if last_interaction:
            time_diff = datetime.now() - last_interaction
            if time_diff.total_seconds() < 30:
                return False
        
        # Responder en ciertos casos específicos
        last_message_type = user_context.get('last_message_type')
        
        # Siempre responder a saludos
        if last_message_type == 'greeting':
            return True
        
        # Responder ocasionalmente a mensajes casuales (30% de probabilidad)
        if last_message_type == 'casual_message':
            import random
            return random.random() < 0.3
        
        # Responder a expresiones emocionales
        if last_message_type == 'emotional_expression':
            return True
        
        return False
    
    async def _post_process_interaction(self, user_id: int, event: Update, data: Dict[str, Any]):
        """Procesa la interacción después del handler principal."""
        
        # Actualizar estadísticas de interacción
        context = self.user_context_cache.get(user_id, {})
        context['total_interactions'] = context.get('total_interactions', 0) + 1
        context['last_processed_time'] = datetime.now()
        
        # Si debería enviar respuesta contextual, prepararla
        diana_context = data.get('diana_context', {})
        if diana_context.get('should_respond_contextually', False):
            await self._prepare_contextual_response(user_id, event, diana_context)
        
        self.user_context_cache[user_id] = context
    
    async def _prepare_contextual_response(self, user_id: int, 
                                         event: Update, 
                                         diana_context: Dict[str, Any]):
        """Prepara y programa una respuesta contextual."""
        try:
            # Determinar tipo de respuesta basado en el contexto
            if event.message:
                message_type = diana_context['interaction_history'].get('last_message_type')
                
                if message_type == 'greeting':
                    context_type = 'greeting'
                elif message_type == 'emotional_expression':
                    context_type = 'emotional_response'
                else:
                    context_type = 'casual_response'
                
                # Generar respuesta contextual
                response = await self.diana_system.generate_contextual_response(
                    user_id=user_id,
                    context_type=context_type,
                    context_data={
                        'emotional_state': diana_context['emotional_state'],
                        'time_of_day': diana_context['time_of_day'],
                        'interaction_frequency': diana_context['interaction_frequency']
                    }
                )
                
                # En una implementación real, aquí enviaríamos el mensaje
                # Por ahora, solo lo registramos para referencia
                logger.info(f"Respuesta contextual preparada para usuario {user_id}: {response}")
                
                # Almacenar la respuesta para que pueda ser utilizada por otros componentes
                data['diana_contextual_response'] = response
        
        except Exception as e:
            logger.error(f"Error preparando respuesta contextual: {e}")
    
    def cleanup_user_cache(self, user_id: int):
        """Limpia el caché de un usuario específico."""
        if user_id in self.user_context_cache:
            del self.user_context_cache[user_id]
        
        if user_id in self.recent_commands:
            del self.recent_commands[user_id]
    
    async def get_user_interaction_summary(self, user_id: int) -> Dict[str, Any]:
        """Obtiene un resumen de las interacciones del usuario."""
        context = self.user_context_cache.get(user_id, {})
        diana_context = await self._get_diana_context(user_id)
        
        return {
            'total_interactions': context.get('total_interactions', 0),
            'last_interaction': context.get('last_interaction_time'),
            'favorite_interaction_type': context.get('favorite_interaction_type'),
            'current_emotional_state': diana_context['emotional_state'],
            'personality_traits': diana_context['personality_traits'],
            'narrative_progress': diana_context['narrative_progress']
        }