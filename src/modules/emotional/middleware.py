"""Middleware para integrar estados emocionales en las respuestas del bot."""

import logging
from typing import Dict, Any, Callable, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, Update

from src.modules.emotional.service import EmotionalService
from src.modules.emotional.diana_state import EmotionalTrigger


class EmotionalMiddleware(BaseMiddleware):
    """
    Middleware que integra el sistema emocional con las respuestas del bot.
    
    Intercepta mensajes de usuarios para:
    - Analizar el contenido emocional
    - Disparar transiciones de estado si es necesario
    - Modificar respuestas según el estado emocional actual
    """
    
    def __init__(self, emotional_service: EmotionalService):
        self.emotional_service = emotional_service
        self.logger = logging.getLogger(__name__)
        super().__init__()
    
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        """
        Procesa el evento antes y después del handler principal.
        
        Args:
            handler: Handler principal a ejecutar
            event: Evento/Update de Telegram
            data: Datos del contexto
            
        Returns:
            Resultado del handler principal
        """
        # Solo procesar mensajes de texto
        if not event.message or not event.message.text:
            return await handler(event, data)
        
        message = event.message
        user_id = message.from_user.id
        message_text = message.text
        
        # Analizar la interacción del usuario
        try:
            detected_trigger = await self.emotional_service.analyze_user_interaction(
                user_id=user_id,
                message_text=message_text,
                context={"message_type": "text", "chat_type": message.chat.type}
            )
            
            # Disparar cambio de estado si se detectó un trigger
            if detected_trigger:
                await self.emotional_service.trigger_state_change(
                    user_id=user_id,
                    trigger=detected_trigger,
                    context={"message": message_text}
                )
                
                self.logger.debug(f"Trigger {detected_trigger.value} procesado para usuario {user_id}")
        
        except Exception as e:
            self.logger.error(f"Error al analizar interacción emocional: {e}")
        
        # Añadir servicio emocional a los datos del contexto
        data["emotional_service"] = self.emotional_service
        data["user_emotional_state"] = await self.emotional_service.get_response_modifiers(user_id)
        
        # Ejecutar handler principal
        result = await handler(event, data)
        
        return result


class EmotionalResponseModifier:
    """
    Utilidad para modificar respuestas basándose en el estado emocional.
    
    Puede ser usada en handlers específicos para aplicar modificaciones
    emocionales a las respuestas antes de enviarlas.
    """
    
    def __init__(self, emotional_service: EmotionalService):
        self.emotional_service = emotional_service
        self.logger = logging.getLogger(__name__)
    
    async def modify_message(self, 
                           user_id: int, 
                           original_text: str,
                           context: Dict[str, Any] = None) -> str:
        """
        Modifica el texto de un mensaje según el estado emocional.
        
        Args:
            user_id: ID del usuario que recibirá el mensaje
            original_text: Texto original del mensaje
            context: Contexto adicional para la modificación
            
        Returns:
            Texto modificado según el estado emocional
        """
        try:
            modified_text = await self.emotional_service.modify_response(
                user_id=user_id,
                original_response=original_text,
                context=context
            )
            
            if modified_text != original_text:
                self.logger.debug(f"Respuesta modificada emocionalmente para usuario {user_id}")
            
            return modified_text
        
        except Exception as e:
            self.logger.error(f"Error al modificar respuesta emocional: {e}")
            return original_text
    
    async def get_emotional_context(self, user_id: int) -> Dict[str, Any]:
        """
        Obtiene el contexto emocional actual de un usuario.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Diccionario con información del estado emocional actual
        """
        try:
            stats = await self.emotional_service.get_user_emotional_stats(user_id)
            modifiers = await self.emotional_service.get_response_modifiers(user_id)
            
            return {
                "current_state": stats.get("current_state"),
                "state_duration_minutes": stats.get("state_duration_minutes"),
                "intensity_level": stats.get("intensity_level"),
                "modifiers": modifiers
            }
        
        except Exception as e:
            self.logger.error(f"Error al obtener contexto emocional: {e}")
            return {}


# Funciones de utilidad para usar en handlers

async def apply_emotional_tone(
    user_id: int, 
    message_text: str, 
    emotional_service: EmotionalService
) -> str:
    """
    Función de utilidad para aplicar tono emocional a un mensaje.
    
    Args:
        user_id: ID del usuario
        message_text: Texto del mensaje
        emotional_service: Servicio emocional
        
    Returns:
        Mensaje con tono emocional aplicado
    """
    modifier = EmotionalResponseModifier(emotional_service)
    return await modifier.modify_message(user_id, message_text)


async def trigger_emotional_response(
    user_id: int,
    trigger: EmotionalTrigger,
    emotional_service: EmotionalService,
    context: Dict[str, Any] = None
) -> bool:
    """
    Función de utilidad para disparar una respuesta emocional específica.
    
    Args:
        user_id: ID del usuario
        trigger: Trigger emocional a disparar
        emotional_service: Servicio emocional
        context: Contexto adicional
        
    Returns:
        True si el trigger fue procesado exitosamente
    """
    return await emotional_service.trigger_state_change(
        user_id=user_id,
        trigger=trigger,
        context=context
    )


async def get_emotional_greeting(
    user_id: int,
    emotional_service: EmotionalService
) -> str:
    """
    Genera un saludo basado en el estado emocional actual.
    
    Args:
        user_id: ID del usuario
        emotional_service: Servicio emocional
        
    Returns:
        Saludo personalizado según el estado emocional
    """
    try:
        stats = await emotional_service.get_user_emotional_stats(user_id)
        current_state = stats.get("current_state", "enigmatica")
        
        greetings = {
            "vulnerable": "Hola... ¿cómo te sientes hoy? 💙",
            "enigmatica": "Hola... hay algo intrigante en el aire hoy 🤔",
            "provocadora": "¡Hola, guapo! ¿Qué travesuras tienes planeadas? 😏",
            "analitica": "Hola. Espero que tengas un día productivo y reflexivo 🧠",
            "silenciosa": "Hola... *sonrisa silenciosa* ✨"
        }
        
        return greetings.get(current_state, "¡Hola! ¿Cómo estás?")
    
    except Exception as e:
        logging.getLogger(__name__).error(f"Error al generar saludo emocional: {e}")
        return "¡Hola! ¿Cómo estás?"