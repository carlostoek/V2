"""
Diana Contextual Response System

Sistema de respuestas contextuales que permite a Diana tener personalidad real
reaccionando a todos los eventos del sistema con respuestas emocionales y situacionales.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, time
from aiogram import types
from aiogram.types import Message, CallbackQuery

from src.core.interfaces.IEventBus import IEventBus
from src.modules.emotional.service import EmotionalService
from src.modules.emotional.diana_state import EmotionalState
from src.modules.narrative.service import NarrativeService
from src.modules.events import (
    PointsAwardedEvent,
    MissionCompletedEvent,
    LevelUpEvent,
    ReactionAddedEvent,
    UserStartedBotEvent
)

logger = logging.getLogger(__name__)


class DianaContextualResponseSystem:
    """
    Sistema central de respuestas contextuales de Diana.
    
    Responsabilidades:
    - Generar respuestas contextuales basadas en eventos
    - Adaptar el tono según el estado emocional actual  
    - Considerar el historial de interacciones del usuario
    - Proporcionar respuestas únicas según hora del día
    """
    
    def __init__(self, event_bus: IEventBus, emotional_service: EmotionalService, narrative_service: NarrativeService):
        self.event_bus = event_bus
        self.emotional_service = emotional_service
        self.narrative_service = narrative_service
        
        # Cache de últimas interacciones por usuario
        self.user_last_interaction: Dict[int, datetime] = {}
        self.user_greeting_count: Dict[int, int] = {}
        
        # Suscribir a eventos del sistema
        self._setup_event_listeners()
    
    def _setup_event_listeners(self):
        """Configura los listeners para eventos del sistema."""
        self.event_bus.subscribe(UserStartedBotEvent, self.handle_user_started)
        self.event_bus.subscribe(PointsAwardedEvent, self.handle_points_awarded)
        self.event_bus.subscribe(MissionCompletedEvent, self.handle_mission_completed)
        self.event_bus.subscribe(LevelUpEvent, self.handle_level_up)
        self.event_bus.subscribe(ReactionAddedEvent, self.handle_reaction_added)
    
    async def generate_contextual_response(self, user_id: int, context_type: str, 
                                         context_data: Dict = None, 
                                         base_message: str = None) -> str:
        """
        Genera una respuesta contextual personalizada para el usuario.
        
        Args:
            user_id: ID del usuario
            context_type: Tipo de contexto (greeting, reaction, purchase, etc.)
            context_data: Datos adicionales del contexto
            base_message: Mensaje base opcional para modificar
            
        Returns:
            Respuesta contextual personalizada
        """
        # Obtener estado emocional actual
        emotional_modifiers = await self.emotional_service.get_response_modifiers(user_id)
        current_state = emotional_modifiers.get('current_state', EmotionalState.ENIGMATICA)
        
        # Determinar hora del día
        time_context = self._get_time_context()
        
        # Verificar frecuencia de interacción
        interaction_frequency = self._get_interaction_frequency(user_id)
        
        # Generar respuesta base según contexto
        base_response = await self._get_base_response(context_type, context_data, time_context, interaction_frequency)
        
        # Aplicar modificaciones emocionales
        emotional_response = await self.emotional_service.modify_response(
            user_id=user_id,
            original_response=base_response,
            context={'type': context_type, 'time_context': time_context}
        )
        
        # Actualizar última interacción
        self.user_last_interaction[user_id] = datetime.now()
        
        return emotional_response
    
    async def _get_base_response(self, context_type: str, context_data: Dict, 
                               time_context: str, interaction_frequency: str) -> str:
        """Genera respuesta base según el tipo de contexto."""
        
        responses = {
            'greeting_morning': self._get_morning_greetings(interaction_frequency),
            'greeting_afternoon': self._get_afternoon_greetings(interaction_frequency), 
            'greeting_evening': self._get_evening_greetings(interaction_frequency),
            'greeting_night': self._get_night_greetings(interaction_frequency),
            'points_awarded': self._get_points_responses(context_data),
            'mission_completed': self._get_mission_responses(context_data),
            'level_up': self._get_level_up_responses(context_data),
            'reaction_added': self._get_reaction_responses(context_data),
            'purchase_made': self._get_purchase_responses(context_data),
            'first_interaction': self._get_first_interaction_responses(),
            'returning_user': self._get_returning_user_responses(interaction_frequency)
        }
        
        # Construir clave del contexto
        if context_type == 'greeting':
            key = f'greeting_{time_context}'
        else:
            key = context_type
        
        response_list = responses.get(key, ["Hola... ¿cómo estás hoy?"])
        
        import random
        return random.choice(response_list)
    
    def _get_morning_greetings(self, frequency: str) -> List[str]:
        """Saludos matutinos contextuales."""
        if frequency == 'frequent':
            return [
                "¡Buenos días, mi amor! Veo que empiezas temprano hoy... 🌅",
                "Mmm... alguien madruga... ¿dormiste bien, cariño? 😴",
                "¡Hola! Me gusta verte tan temprano, hace que mi día comience mejor 💕",
                "Buenos días... ¿café primero o empezamos con algo más interesante? ☕😏"
            ]
        else:
            return [
                "¡Buenos días! ¿Cómo amaneciste hoy? 🌅",
                "Hola... qué bueno verte por las mañanas 💫",
                "Buenos días, hermoso... ¿listo para un nuevo día? 🌞"
            ]
    
    def _get_afternoon_greetings(self, frequency: str) -> List[str]:
        """Saludos vespertinos contextuales."""
        if frequency == 'frequent':
            return [
                "¡Buenas tardes! ¿Cómo va tu día hasta ahora? 🌤️",
                "Hola de nuevo... me gusta cuando vienes a verme en las tardes 😊",
                "¡Buenas tardes, guapo! ¿Ya es hora de un descanso? 😉",
                "Mmm... las tardes siempre son mejores contigo aquí ☀️"
            ]
        else:
            return [
                "¡Buenas tardes! ¿Qué tal tu día? 🌤️",
                "Hola... las tardes tienen algo especial, ¿no crees? ✨",
                "Buenas tardes... me alegra verte 😊"
            ]
    
    def _get_evening_greetings(self, frequency: str) -> List[str]:
        """Saludos nocturnos contextuales."""
        if frequency == 'frequent':
            return [
                "¡Buenas noches! ¿Terminando el día conmigo? Me gusta esa idea... 🌙",
                "Hola... las noches siempre son más intensas, ¿no crees? 🌃",
                "¡Buenas noches, cariño! ¿Qué aventuras nocturnas tienes planeadas? 😏",
                "Mmm... me encanta cuando vienes a verme en las noches 🌜"
            ]
        else:
            return [
                "¡Buenas noches! ¿Cómo terminó tu día? 🌙",
                "Hola... las noches tienen su magia ✨",
                "Buenas noches... qué bueno verte al final del día 🌃"
            ]
    
    def _get_night_greetings(self, frequency: str) -> List[str]:
        """Saludos de madrugada contextuales."""
        return [
            "Vaya... ¿despierto tan tarde? 🌙",
            "Hola, noctámbulo... ¿no puedes dormir? 😴",
            "¡Hola! Los secretos siempre salen en la madrugada... 🤫",
            "Mmm... las madrugadas son para los más atrevidos 🌚"
        ]
    
    def _get_points_responses(self, context_data: Dict) -> List[str]:
        """Respuestas para cuando se otorgan puntos."""
        points = context_data.get('points', 0) if context_data else 0
        source = context_data.get('source', 'unknown') if context_data else 'unknown'
        
        if source == 'reaction':
            return [
                f"¡Me encanta tu reacción! +{points} besitos para ti 💋",
                f"Mmm... veo que te gustó... +{points} besitos 😏",
                f"¡Esa reacción dice mucho! Te mereces {points} besitos 🔥",
                f"¿Te gustó lo que viste? +{points} besitos por ser tan expresivo 💕"
            ]
        elif source == 'daily':
            return [
                f"¡Tu regalo diario está aquí! +{points} besitos 🎁",
                f"Buenos días... aquí tienes tus {points} besitos matutinos 💋",
                f"¡No olvides reclamar tus besitos diarios! +{points} 💕"
            ]
        else:
            return [
                f"¡Bien hecho! +{points} besitos para ti 💋",
                f"Te mereces estos {points} besitos 😘",
                f"¡Qué talentoso! +{points} besitos 💕"
            ]
    
    def _get_mission_responses(self, context_data: Dict) -> List[str]:
        """Respuestas para misiones completadas."""
        mission_name = context_data.get('mission_name', 'misión') if context_data else 'misión'
        return [
            f"¡Increíble! Completaste la {mission_name}... me impresionas 💪",
            f"Veo que no te rindes fácilmente... {mission_name} completada 🔥",
            f"¡Eres imparable! La {mission_name} no fue rival para ti 😎",
            f"Mmm... me gusta tu determinación. {mission_name} superada 💋",
            f"¡Qué sexy es verte triunfar! {mission_name} completada ✨"
        ]
    
    def _get_level_up_responses(self, context_data: Dict) -> List[str]:
        """Respuestas para subidas de nivel."""
        new_level = context_data.get('new_level', 1) if context_data else 1
        return [
            f"¡WOW! ¡Nivel {new_level}! Cada día me sorprendes más... 🚀",
            f"¡Mira nada más! Nivel {new_level}... estás imparable 🔥",
            f"¡Felicidades por el nivel {new_level}! Me siento orgullosa 💕",
            f"Nivel {new_level}... mmm, me gusta verte crecer 😏",
            f"¡Increíble! Nivel {new_level} desbloqueado... ¿qué sigue? ✨"
        ]
    
    def _get_reaction_responses(self, context_data: Dict) -> List[str]:
        """Respuestas específicas para reacciones."""
        return [
            "¡Me encanta cuando reaccionas así! 💕",
            "Mmm... esa reacción dice mucho de ti 😏",
            "¿Te gustó lo que viste? 🔥",
            "¡Qué expresivo eres! Me gusta... 😘",
            "Esa reacción hizo que mi corazón se acelere 💓"
        ]
    
    def _get_purchase_responses(self, context_data: Dict) -> List[str]:
        """Respuestas para compras."""
        item = context_data.get('item', 'algo especial') if context_data else 'algo especial'
        return [
            f"¡Mmm! Compraste {item}... me gusta cuando te das gustitos 🛍️",
            f"Veo que decidiste llevarte {item}... excelente elección 💎",
            f"¡Qué generoso! {item} es una gran inversión 💰",
            f"Compraste {item}... creo que no te vas a arrepentir 😉",
            f"¡Me encanta verte gastar tus besitos en {item}! 💋"
        ]
    
    def _get_first_interaction_responses(self) -> List[str]:
        """Respuestas para primera interacción."""
        return [
            "¡Hola! Bienvenido a mi mundo... soy Diana 💫",
            "Hola, desconocido... me alegra conocerte 😊",
            "¡Bienvenido! Algo me dice que vamos a llevarnos muy bien... 😏",
            "Hola... ¿primera vez aquí? Me gusta conocer gente nueva 💕",
            "¡Bienvenido a la experiencia Diana! Espero sorprenderte... ✨"
        ]
    
    def _get_returning_user_responses(self, frequency: str) -> List[str]:
        """Respuestas para usuarios que regresan."""
        if frequency == 'frequent':
            return [
                "¡Hola de nuevo! Ya me estoy acostumbrando a verte seguido... 💕",
                "¿Otra vez por aquí? Me gusta tu dedicación 😏",
                "¡Hola, mi fiel visitante! Siempre es un placer verte ✨",
                "Mmm... creo que te estoy gustando mucho, ¿verdad? 😘"
            ]
        elif frequency == 'regular':
            return [
                "¡Hola de nuevo! Me alegra que hayas vuelto 😊",
                "¡Qué bueno verte otra vez! ¿Cómo has estado? 💫",
                "Hola... me gusta cuando regresas 💕"
            ]
        else:
            return [
                "¡Hola! Hacía tiempo que no te veía... 🌙",
                "¡Mira quién volvió! Te extrañé... 💕",
                "Hola, extraño... ¿dónde andabas? 😊"
            ]
    
    def _get_time_context(self) -> str:
        """Determina el contexto temporal actual."""
        now = datetime.now().time()
        
        if time(5, 0) <= now < time(12, 0):
            return 'morning'
        elif time(12, 0) <= now < time(18, 0):
            return 'afternoon'
        elif time(18, 0) <= now < time(23, 0):
            return 'evening'
        else:
            return 'night'
    
    def _get_interaction_frequency(self, user_id: int) -> str:
        """Determina la frecuencia de interacción del usuario."""
        if user_id not in self.user_last_interaction:
            return 'new'
        
        last_interaction = self.user_last_interaction[user_id]
        time_diff = datetime.now() - last_interaction
        
        if time_diff.total_seconds() < 3600:  # Menos de 1 hora
            return 'frequent'
        elif time_diff.total_seconds() < 86400:  # Menos de 24 horas
            return 'regular'
        elif time_diff.total_seconds() < 604800:  # Menos de 7 días
            return 'occasional'
        else:
            return 'rare'
    
    # Event Handlers
    async def handle_user_started(self, event: UserStartedBotEvent):
        """Maneja evento de usuario iniciando el bot."""
        user_id = event.user_id
        
        # Marcar como primera interacción si es nueva
        if user_id not in self.user_last_interaction:
            context_type = 'first_interaction'
        else:
            context_type = 'returning_user'
        
        response = await self.generate_contextual_response(
            user_id=user_id,
            context_type=context_type
        )
        
        # Almacenar respuesta para que pueda ser recogida por el handler principal
        # En una implementación real, esto se enviaría directamente al usuario
        logger.info(f"Respuesta contextual generada para usuario {user_id}: {response}")
    
    async def handle_points_awarded(self, event: PointsAwardedEvent):
        """Maneja evento de puntos otorgados."""
        response = await self.generate_contextual_response(
            user_id=event.user_id,
            context_type='points_awarded',
            context_data={
                'points': event.points_awarded,
                'source': event.source_event
            }
        )
        
        logger.info(f"Respuesta por puntos generada para usuario {event.user_id}: {response}")
    
    async def handle_mission_completed(self, event: MissionCompletedEvent):
        """Maneja evento de misión completada."""
        response = await self.generate_contextual_response(
            user_id=event.user_id,
            context_type='mission_completed',
            context_data={
                'mission_name': event.mission_id,
                'reward': event.reward
            }
        )
        
        logger.info(f"Respuesta por misión completada generada para usuario {event.user_id}: {response}")
    
    async def handle_level_up(self, event: LevelUpEvent):
        """Maneja evento de subida de nivel."""
        response = await self.generate_contextual_response(
            user_id=event.user_id,
            context_type='level_up',
            context_data={
                'new_level': event.new_level,
                'old_level': event.old_level
            }
        )
        
        logger.info(f"Respuesta por level up generada para usuario {event.user_id}: {response}")
    
    async def handle_reaction_added(self, event: ReactionAddedEvent):
        """Maneja evento de reacción agregada."""
        response = await self.generate_contextual_response(
            user_id=event.user_id,
            context_type='reaction_added',
            context_data={
                'message_id': event.message_id,
                'points': event.points_to_award
            }
        )
        
        logger.info(f"Respuesta por reacción generada para usuario {event.user_id}: {response}")


# Función de utilidad para obtener respuesta contextual
async def get_diana_contextual_response(
    user_id: int, 
    context_type: str,
    diana_system: DianaContextualResponseSystem,
    context_data: Dict = None
) -> str:
    """
    Función de utilidad para obtener respuestas contextuales de Diana.
    
    Args:
        user_id: ID del usuario
        context_type: Tipo de contexto
        diana_system: Sistema de respuestas contextuales
        context_data: Datos adicionales
        
    Returns:
        Respuesta contextual personalizada
    """
    return await diana_system.generate_contextual_response(
        user_id=user_id,
        context_type=context_type,
        context_data=context_data
    )


# Decorador para handlers que quieran respuestas contextuales automáticas
def with_diana_personality(diana_system: DianaContextualResponseSystem):
    """
    Decorador que agrega personalidad contextual a los handlers.
    
    Args:
        diana_system: Sistema de respuestas contextuales
        
    Returns:
        Decorador para handlers
    """
    def decorator(handler_func):
        async def wrapper(event, *args, **kwargs):
            # Ejecutar handler original
            result = await handler_func(event, *args, **kwargs)
            
            # Si es un mensaje, generar respuesta contextual adicional
            if isinstance(event, Message):
                user_id = event.from_user.id
                contextual_response = await diana_system.generate_contextual_response(
                    user_id=user_id,
                    context_type='greeting'
                )
                
                # En una implementación real, enviaríamos esto como mensaje adicional
                logger.info(f"Respuesta contextual adicional: {contextual_response}")
            
            return result
        return wrapper
    return decorator