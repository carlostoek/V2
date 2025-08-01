"""
Diana Validation Integration Service

Este servicio integra el sistema de validación de Diana con el sistema de narrativa y gamificación.
Actúa como un adapter/bridge pattern entre los sistemas.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime

from src.core.interfaces.IEventBus import IEventBus
from src.core.interfaces.ICoreService import ICoreService
from src.modules.events import (
    NarrativeProgressionEvent,
    ReactionAddedEvent,
    DianaValidationCompletedEvent,
    DianaValidationFailedEvent,
    NarrativeValidationProgressEvent,
    MissionCompletedEvent
)

# Import Diana validation client
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../remp_narrativa'))

from diana_validation_client import DianaValidator, DianaValidatorForTransitions, ValidationResult


class DianaValidationIntegrationService(ICoreService):
    """
    Servicio de integración para validaciones de Diana.
    
    Responsabilidades:
    - Detectar eventos narrativos que requieren validación Diana
    - Ejecutar validaciones apropiadas usando DianaValidator
    - Traducir resultados a eventos de gamificación
    - Gestionar progreso de validaciones para misiones especiales
    """
    
    def __init__(self, event_bus: IEventBus, validation_service_url: str = "http://localhost:8000"):
        self._event_bus = event_bus
        self.validation_service_url = validation_service_url
        self.validator = None
        self.transitions_validator = None
        self.logger = logging.getLogger(__name__)
        
        # Cache para rastrear intentos de validación por usuario
        self.validation_attempts: Dict[int, Dict[str, List[Dict]]] = {}
        
        # Cache para datos de reacciones por usuario (para validación nivel 1→2)
        self.reaction_data_cache: Dict[int, List[Dict]] = {}
        
        # Cache para eventos de observación (para validación nivel 2→3)
        self.observation_events_cache: Dict[int, List[Dict]] = {}
        
    async def setup(self) -> None:
        """Inicializa el servicio y suscribe a eventos relevantes."""
        # Inicializar validador Diana
        self.validator = DianaValidator(self.validation_service_url)
        self.transitions_validator = DianaValidatorForTransitions(self.validator)
        
        # Suscribirse a eventos relevantes
        self._event_bus.subscribe(ReactionAddedEvent, self.handle_reaction_added)
        self._event_bus.subscribe(NarrativeProgressionEvent, self.handle_narrative_progression)
        self._event_bus.subscribe(MissionCompletedEvent, self.handle_mission_completed)
        
        self.logger.info("Diana Validation Integration Service inicializado")
    
    async def handle_reaction_added(self, event: ReactionAddedEvent) -> None:
        """
        Maneja reacciones para potencial validación de nivel 1 → 2.
        
        Args:
            event: Evento de reacción agregada
        """
        user_id = event.user_id
        
        # Registrar datos de reacción para validación posterior
        reaction_data = {
            'timestamp': datetime.now().timestamp(),
            'speed_seconds': 0,  # TODO: Calcular tiempo real desde el mensaje
            'message_id': event.message_id,
            'points_awarded': event.points_to_award
        }
        
        # Agregar a cache
        if user_id not in self.reaction_data_cache:
            self.reaction_data_cache[user_id] = []
        self.reaction_data_cache[user_id].append(reaction_data)
        
        # Limitar cache a últimas 10 reacciones
        if len(self.reaction_data_cache[user_id]) > 10:
            self.reaction_data_cache[user_id] = self.reaction_data_cache[user_id][-10:]
        
        # Trackear evento de forma asíncrona (no bloquea)
        if self.validator:
            await self.validator.track_user_event(user_id, "reaction", reaction_data)
        
        self.logger.debug(f"Datos de reacción registrados para usuario {user_id}")
    
    async def handle_narrative_progression(self, event: NarrativeProgressionEvent) -> None:
        """
        Maneja progresión narrativa para detectar validaciones necesarias.
        
        Args:
            event: Evento de progresión narrativa
        """
        user_id = event.user_id
        fragment_id = event.fragment_id
        
        # Registrar evento de observación/exploración
        observation_event = {
            'type': 'exploration',
            'timestamp': datetime.now().timestamp(),
            'fragment_id': fragment_id,
            'duration': 60,  # Duración estimada de exploración
            'interactions': 1
        }
        
        # Agregar a cache de observación
        if user_id not in self.observation_events_cache:
            self.observation_events_cache[user_id] = []
        self.observation_events_cache[user_id].append(observation_event)
        
        # Trackear evento
        if self.validator:
            await self.validator.track_user_event(user_id, "narrative_progression", {
                'fragment_id': fragment_id,
                'choices_made': event.choices_made
            })
        
        self.logger.debug(f"Progresión narrativa registrada para usuario {user_id} en fragmento {fragment_id}")
    
    async def handle_mission_completed(self, event: MissionCompletedEvent) -> None:
        """
        Maneja misiones completadas que pueden requerir validaciones Diana.
        
        Args:
            event: Evento de misión completada
        """
        user_id = event.user_id
        mission_id = event.mission_id
        
        # Verificar si es una misión de validación Diana
        if "diana_validation" in mission_id.lower():
            await self._trigger_diana_validation_mission(user_id, mission_id)
        
        self.logger.debug(f"Misión completada procesada para usuario {user_id}: {mission_id}")
    
    async def validate_level_progression(self, user_id: int, from_level: int, to_level: int, 
                                       context_data: Dict[str, Any] = None) -> bool:
        """
        Ejecuta validación Diana para progresión de nivel.
        
        Args:
            user_id: ID del usuario
            from_level: Nivel origen
            to_level: Nivel destino
            context_data: Datos adicionales para la validación
            
        Returns:
            True si la validación es exitosa, False en caso contrario
        """
        if not self.validator:
            self.logger.error("Diana validator no está inicializado")
            return False
        
        try:
            validation_result = None
            
            # Determinar tipo de validación basado en los niveles
            if from_level == 1 and to_level == 2:
                # Validación de reacción rápida
                reaction_data = self._get_recent_reaction_data(user_id)
                if reaction_data:
                    validation_result = await self.validator.can_advance_to_level_2(user_id, reaction_data)
                    
            elif from_level == 2 and to_level == 3:
                # Validación de observación
                observation_events = self.observation_events_cache.get(user_id, [])
                if observation_events:
                    validation_result = await self.validator.can_advance_to_level_3(user_id, observation_events)
                    
            elif from_level == 3 and to_level >= 4:  # VIP level
                # Validación de perfil de deseo
                desire_profile = context_data.get('desire_profile', {}) if context_data else {}
                if desire_profile:
                    validation_result = await self.validator.can_advance_to_vip(user_id, desire_profile)
                    
            elif from_level == 5 and to_level == 6:
                # Validación de empatía
                empathy_responses = context_data.get('empathy_responses', []) if context_data else []
                if empathy_responses:
                    validation_result = await self.validator.can_advance_to_level_6(user_id, empathy_responses)
            
            # Procesar resultado
            if validation_result:
                if validation_result.result == ValidationResult.PASSED:
                    # Emitir evento de validación exitosa
                    success_event = DianaValidationCompletedEvent(
                        user_id=user_id,
                        validation_type=f"level_{from_level}_to_{to_level}",
                        score=validation_result.score,
                        reward_data=validation_result.data
                    )
                    await self._event_bus.publish(success_event)
                    
                    self.logger.info(f"Validación Diana exitosa: usuario {user_id} nivel {from_level}→{to_level}")
                    return True
                else:
                    # Emitir evento de validación fallida  
                    failure_event = DianaValidationFailedEvent(
                        user_id=user_id,
                        validation_type=f"level_{from_level}_to_{to_level}",
                        score=validation_result.score,
                        retry_allowed=True
                    )
                    await self._event_bus.publish(failure_event)
                    
                    self.logger.info(f"Validación Diana fallida: usuario {user_id} nivel {from_level}→{to_level}")
                    return False
            
        except Exception as e:
            self.logger.error(f"Error en validación Diana: {e}")
            
        return False
    
    async def get_adaptive_content_for_user(self, user_id: int, content_type: str, 
                                          context: Dict = None) -> Dict[str, Any]:
        """
        Obtiene contenido adaptado usando el sistema Diana.
        
        Args:
            user_id: ID del usuario
            content_type: Tipo de contenido
            context: Contexto adicional
            
        Returns:
            Diccionario con contenido adaptado
        """
        if not self.validator:
            return {
                'text': f"Contenido por defecto para {content_type}",
                'buttons': [],
                'media': None,
                'archetype': 'unknown'
            }
        
        try:
            content = await self.validator.get_adaptive_content(user_id, content_type, context)
            return content
        except Exception as e:
            self.logger.error(f"Error obteniendo contenido adaptado: {e}")
            return {
                'text': f"Contenido por defecto para {content_type}",
                'buttons': [],
                'media': None,
                'archetype': 'unknown'
            }
    
    async def get_user_archetype(self, user_id: int) -> str:
        """
        Obtiene el arquetipo del usuario según Diana.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Arquetipo del usuario
        """
        if not self.validator:
            return 'unknown'
        
        try:
            archetype = await self.validator.get_user_archetype(user_id)
            return archetype
        except Exception as e:
            self.logger.error(f"Error obteniendo arquetipo de usuario: {e}")
            return 'unknown'
    
    def _get_recent_reaction_data(self, user_id: int) -> Optional[Dict]:
        """Obtiene datos de la reacción más reciente para validación."""
        reactions = self.reaction_data_cache.get(user_id, [])
        if reactions:
            return reactions[-1]  # Más reciente
        return None
    
    async def _trigger_diana_validation_mission(self, user_id: int, mission_id: str) -> None:
        """
        Activa una validación Diana específica basada en una misión.
        
        Args:
            user_id: ID del usuario
            mission_id: ID de la misión que activa la validación
        """
        try:
            # Determinar tipo de validación basado en mission_id
            if "level_1_to_2" in mission_id:
                reaction_data = self._get_recent_reaction_data(user_id)
                if reaction_data:
                    success = await self.validate_level_progression(user_id, 1, 2)
                    if success:
                        self.logger.info(f"Validación misión nivel 1→2 exitosa para usuario {user_id}")
                        
            elif "level_2_to_3" in mission_id:
                observation_events = self.observation_events_cache.get(user_id, [])
                if observation_events:
                    success = await self.validate_level_progression(user_id, 2, 3)
                    if success:
                        self.logger.info(f"Validación misión nivel 2→3 exitosa para usuario {user_id}")
            
            # Agregar más tipos de validación según sea necesario
            
        except Exception as e:
            self.logger.error(f"Error ejecutando validación de misión: {e}")
    
    async def cleanup(self) -> None:
        """Limpia recursos del servicio."""
        if self.validator and hasattr(self.validator, 'session') and self.validator.session:
            await self.validator.session.close()
        
        # Limpiar caches
        self.validation_attempts.clear()
        self.reaction_data_cache.clear()
        self.observation_events_cache.clear()
        
        self.logger.info("Diana Validation Integration Service limpiado")