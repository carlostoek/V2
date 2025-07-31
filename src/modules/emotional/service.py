"""Servicio para gestionar estados emocionales de Diana."""

import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from sqlalchemy import select, update, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.interfaces.IEventBus import IEvent, IEventBus
from src.core.interfaces.ICoreService import ICoreService
from src.bot.database.engine import get_session
from src.bot.database.models.user import User
from src.modules.emotional.diana_state import (
    DianaStateMachine, 
    EmotionalState, 
    EmotionalTrigger,
    DianaStateData
)
from src.modules.emotional.events import (
    EmotionalStateChangedEvent,
    UserInteractionAnalyzedEvent,
    EmotionalIntensityChangedEvent,
    EmotionalResetEvent,
    ResponseModifiedEvent
)
from src.modules.events import UserStartedBotEvent


class EmotionalService(ICoreService):
    """
    Servicio para gestionar los estados emocionales de Diana.
    
    Responsabilidades:
    - Mantener máquinas de estado por usuario
    - Analizar interacciones y disparar transiciones
    - Proporcionar modificadores para respuestas
    - Persistir estados emocionales en base de datos
    """
    
    def __init__(self, event_bus: IEventBus):
        self._event_bus = event_bus
        self.state_machines: Dict[int, DianaStateMachine] = {}
        self.logger = logging.getLogger(__name__)
        
        # Cache para evitar crear múltiples máquinas para el mismo usuario
        self._initialization_cache = set()
    
    async def setup(self) -> None:
        """Suscribe el servicio a los eventos relevantes."""
        # Suscribirse a eventos de usuarios nuevos
        self._event_bus.subscribe(UserStartedBotEvent, self.handle_user_started)
        
        self.logger.info("Servicio emocional inicializado")
    
    async def handle_user_started(self, event: UserStartedBotEvent) -> None:
        """Maneja el evento de inicio de usuario creando su máquina de estados."""
        await self.get_or_create_state_machine(event.user_id)
        self.logger.info(f"Máquina de estados emocionales creada para usuario {event.user_id}")
    
    async def get_or_create_state_machine(self, user_id: int) -> DianaStateMachine:
        """
        Obtiene o crea una máquina de estados para un usuario.
        
        Args:
            user_id: ID del usuario.
            
        Returns:
            Máquina de estados del usuario.
        """
        if user_id not in self.state_machines:
            # Cargar estado persistido desde base de datos
            state_data = await self._load_user_emotional_state(user_id)
            
            # Crear nueva máquina de estados
            machine = DianaStateMachine(user_id)
            
            if state_data:
                # Restaurar estado desde base de datos
                machine.state_data = DianaStateData.from_dict(state_data)
                machine.state = machine.state_data.current_state.value
                self.logger.info(f"Estado emocional restaurado para usuario {user_id}: {machine.state_data.current_state.value}")
            
            self.state_machines[user_id] = machine
        
        return self.state_machines[user_id]
    
    async def _load_user_emotional_state(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Carga el estado emocional persistido de un usuario."""
        try:
            async for session in get_session():
                # Buscar usuario
                user_query = select(User).where(User.id == user_id)
                user_result = await session.execute(user_query)
                user = user_result.scalars().first()
                
                if user and hasattr(user, 'emotional_state') and user.emotional_state:
                    return json.loads(user.emotional_state)
                
                return None
        
        except Exception as e:
            self.logger.error(f"Error al cargar estado emocional para usuario {user_id}: {e}")
            return None
    
    async def _save_user_emotional_state(self, user_id: int, state_data: DianaStateData) -> None:
        """Guarda el estado emocional de un usuario en base de datos."""
        try:
            async for session in get_session():
                # Buscar usuario
                user_query = select(User).where(User.id == user_id)
                user_result = await session.execute(user_query)
                user = user_result.scalars().first()
                
                if user:
                    # Guardar estado como JSON
                    if not hasattr(user, 'emotional_state'):
                        # Si el modelo User no tiene el campo, lo agregamos dinámicamente
                        # En una implementación real, se agregaría a la migración de base de datos
                        pass
                    
                    # Por ahora, guardamos en un campo de metadatos si existe
                    if hasattr(user, 'metadata'):
                        if user.metadata is None:
                            user.metadata = {}
                        user.metadata['emotional_state'] = state_data.to_dict()
                        await session.commit()
                    
                    self.logger.debug(f"Estado emocional guardado para usuario {user_id}")
        
        except Exception as e:
            self.logger.error(f"Error al guardar estado emocional para usuario {user_id}: {e}")
    
    async def analyze_user_interaction(self, 
                                     user_id: int, 
                                     message_text: str,
                                     context: Dict[str, Any] = None) -> Optional[EmotionalTrigger]:
        """
        Analiza una interacción del usuario y determina si debe cambiar el estado emocional.
        
        Args:
            user_id: ID del usuario.
            message_text: Texto del mensaje.
            context: Contexto adicional (sentimiento, etc.).
            
        Returns:
            Trigger detectado o None si no se detecta ninguno.
        """
        machine = await self.get_or_create_state_machine(user_id)
        
        # Analizar el texto para detectar triggers
        detected_trigger = machine.analyze_user_input(message_text, context)
        
        # Verificar si necesita transición automática por tiempo
        auto_trigger = machine.should_auto_transition()
        if auto_trigger and not detected_trigger:
            detected_trigger = auto_trigger
        
        # Publicar evento de análisis
        analysis_event = UserInteractionAnalyzedEvent(
            user_id=user_id,
            message_text=message_text,
            detected_trigger=detected_trigger,
            sentiment_score=context.get('sentiment', 0.0) if context else 0.0,
            context=context
        )
        await self._event_bus.publish(analysis_event)
        
        return detected_trigger
    
    async def trigger_state_change(self, 
                                 user_id: int, 
                                 trigger: EmotionalTrigger,
                                 context: Dict[str, Any] = None) -> bool:
        """
        Dispara un cambio de estado emocional.
        
        Args:
            user_id: ID del usuario.
            trigger: Trigger que causa el cambio.
            context: Contexto adicional.
            
        Returns:
            True si el cambio fue exitoso, False en caso contrario.
        """
        machine = await self.get_or_create_state_machine(user_id)
        previous_state = machine.get_current_state()
        
        # Intentar transición
        success = machine.trigger_transition(trigger, context)
        
        if success:
            new_state = machine.get_current_state()
            
            # Guardar estado actualizado
            await self._save_user_emotional_state(user_id, machine.state_data)
            
            # Publicar evento de cambio de estado
            state_change_event = EmotionalStateChangedEvent(
                user_id=user_id,
                previous_state=previous_state,
                new_state=new_state,
                trigger=trigger,
                context=context
            )
            await self._event_bus.publish(state_change_event)
            
            self.logger.info(f"Usuario {user_id}: Estado cambiado de {previous_state.value} a {new_state.value}")
        
        return success
    
    async def get_response_modifiers(self, user_id: int) -> Dict[str, Any]:
        """
        Obtiene modificadores para respuestas basados en el estado emocional actual.
        
        Args:
            user_id: ID del usuario.
            
        Returns:
            Diccionario con modificadores de tono, estilo, etc.
        """
        machine = await self.get_or_create_state_machine(user_id)
        return machine.get_response_modifiers()
    
    async def modify_response(self, 
                            user_id: int, 
                            original_response: str,
                            context: Dict[str, Any] = None) -> str:
        """
        Modifica una respuesta basándose en el estado emocional actual.
        
        Args:
            user_id: ID del usuario.
            original_response: Respuesta original.
            context: Contexto adicional.
            
        Returns:
            Respuesta modificada según el estado emocional.
        """
        machine = await self.get_or_create_state_machine(user_id)
        modifiers = machine.get_response_modifiers()
        
        # Aplicar modificaciones básicas basadas en el estado
        modified_response = original_response
        
        # Modificar según el tono
        if modifiers.get("tone") == "gentle":
            modified_response = self._apply_gentle_tone(modified_response)
        elif modifiers.get("tone") == "playful":
            modified_response = self._apply_playful_tone(modified_response)
        elif modifiers.get("tone") == "analytical":
            modified_response = self._apply_analytical_tone(modified_response)
        elif modifiers.get("tone") == "mysterious":
            modified_response = self._apply_mysterious_tone(modified_response)
        elif modifiers.get("tone") == "quiet":
            modified_response = self._apply_quiet_tone(modified_response)
        
        # Ajustar longitud si es necesario
        if modifiers.get("response_length") == "short" and len(modified_response) > 100:
            modified_response = self._shorten_response(modified_response)
        elif modifiers.get("response_length") == "long" and len(modified_response) < 50:
            modified_response = self._expand_response(modified_response, modifiers)
        
        # Publicar evento de modificación
        if modified_response != original_response:
            modification_event = ResponseModifiedEvent(
                user_id=user_id,
                original_response=original_response,
                modified_response=modified_response,
                emotional_state=machine.get_current_state(),
                modifiers_applied=modifiers
            )
            await self._event_bus.publish(modification_event)
        
        return modified_response
    
    def _apply_gentle_tone(self, response: str) -> str:
        """Aplica un tono gentil y comprensivo."""
        gentle_prefixes = [
            "Entiendo lo que sientes... ",
            "Comprendo tu situación... ",
            "Me parece que... ",
            "Desde mi corazón, "
        ]
        
        # Agregar prefijo gentil si la respuesta no es muy personal ya
        if not any(word in response.lower() for word in ["entiendo", "comprendo", "siento"]):
            import random
            response = random.choice(gentle_prefixes) + response.lower()
        
        # Suavizar el lenguaje
        response = response.replace("no puedes", "tal vez podrías intentar")
        response = response.replace("debes", "podrías considerar")
        response = response.replace("tienes que", "sería bueno si")
        
        return response
    
    def _apply_playful_tone(self, response: str) -> str:
        """Aplica un tono juguetón y coqueto."""
        playful_additions = [" 😏", " jeje", " 😉", " *guiño*"]
        
        # Agregar elementos juguetones
        if not any(emoji in response for emoji in ["😏", "😉", "jeje", "jaja"]):
            import random
            response += random.choice(playful_additions)
        
        # Hacer el lenguaje más informal
        response = response.replace("Por favor", "Anda")
        response = response.replace("Muchas gracias", "Gracias, linda")
        response = response.replace("¿Cómo estás?", "¿Qué tal, guapo?")
        
        return response
    
    def _apply_analytical_tone(self, response: str) -> str:
        """Aplica un tono analítico y reflexivo."""
        analytical_prefixes = [
            "Analizando la situación, ",
            "Desde una perspectiva objetiva, ",
            "Considerando los factores relevantes, ",
            "Evaluando las opciones disponibles, "
        ]
        
        if not any(word in response.lower() for word in ["analiz", "consider", "evalú", "perspectiv"]):
            import random
            response = random.choice(analytical_prefixes) + response.lower()
        
        return response
    
    def _apply_mysterious_tone(self, response: str) -> str:
        """Aplica un tono misterioso e intrigante."""
        mysterious_additions = ["...", " 🤔", " *sonrisa enigmática*"]
        mysterious_prefixes = [
            "Interesante pregunta... ",
            "Hmm, eso me hace pensar... ",
            "Qué curioso que preguntes eso... "
        ]
        
        if len(response) < 50:
            import random
            response = random.choice(mysterious_prefixes) + response.lower()
        
        if not response.endswith(("...", ".", "!", "?")):
            import random
            response += random.choice(mysterious_additions)
        
        return response
    
    def _apply_quiet_tone(self, response: str) -> str:
        """Aplica un tono silencioso y reservado."""
        if len(response) > 50:
            # Acortar respuesta para estado silencioso
            sentences = response.split('. ')
            response = sentences[0] + ("." if not sentences[0].endswith('.') else "")
        
        # Agregar elementos de silencio
        quiet_additions = ["...", " *asiente en silencio*", " *pausa reflexiva*"]
        
        import random
        if random.random() < 0.3:  # 30% de chance de agregar elemento silencioso
            response += random.choice(quiet_additions)
        
        return response
    
    def _shorten_response(self, response: str) -> str:
        """Acorta una respuesta manteniendo el sentido principal."""
        sentences = response.split('. ')
        if len(sentences) > 1:
            return sentences[0] + "."
        return response[:80] + "..." if len(response) > 80 else response
    
    def _expand_response(self, response: str, modifiers: Dict[str, Any]) -> str:
        """Expande una respuesta corta."""
        keywords = modifiers.get("keywords", [])
        if keywords:
            import random
            addition = f" {random.choice(keywords)}"
            response += addition
        
        return response
    
    async def get_user_emotional_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Obtiene estadísticas emocionales de un usuario.
        
        Args:
            user_id: ID del usuario.
            
        Returns:
            Estadísticas del estado emocional.
        """
        machine = await self.get_or_create_state_machine(user_id)
        return machine.get_state_statistics()
    
    async def reset_emotional_state(self, user_id: int, reason: str = "manual_reset") -> bool:
        """
        Resetea el estado emocional de un usuario al estado inicial.
        
        Args:
            user_id: ID del usuario.
            reason: Razón del reset.
            
        Returns:
            True si el reset fue exitoso.
        """
        success = await self.trigger_state_change(user_id, EmotionalTrigger.MOOD_RESET)
        
        if success:
            # Publicar evento de reset
            reset_event = EmotionalResetEvent(user_id=user_id, reason=reason)
            await self._event_bus.publish(reset_event)
        
        return success
    
    async def cleanup_inactive_machines(self, max_age_hours: int = 24) -> int:
        """
        Limpia máquinas de estado de usuarios inactivos para liberar memoria.
        
        Args:
            max_age_hours: Máximo de horas de inactividad antes de limpiar.
            
        Returns:
            Número de máquinas limpiadas.
        """
        cleanup_count = 0
        current_time = datetime.now()
        users_to_remove = []
        
        for user_id, machine in self.state_machines.items():
            # Verificar si la máquina ha estado inactiva por mucho tiempo
            if machine.get_state_duration() > timedelta(hours=max_age_hours):
                users_to_remove.append(user_id)
        
        # Guardar estados antes de limpiar
        for user_id in users_to_remove:
            machine = self.state_machines[user_id]
            await self._save_user_emotional_state(user_id, machine.state_data)
            del self.state_machines[user_id]
            cleanup_count += 1
        
        if cleanup_count > 0:
            self.logger.info(f"Limpiadas {cleanup_count} máquinas de estado inactivas")
        
        return cleanup_count