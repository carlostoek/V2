# diana_validation_client.py
"""
Cliente Diana Validation - Plug & Play
Integración súper simple para el bot Diana con transitions
"""

import aiohttp
import asyncio
import json
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

class ValidationResult(Enum):
    PASSED = "passed"
    FAILED = "failed"
    PENDING = "pending"

@dataclass
class ValidationResponse:
    result: ValidationResult
    score: float
    data: Dict[str, Any]
    message: str = ""
    next_action: str = ""

class DianaValidator:
    """
    Cliente súper simple para validaciones Diana
    
    Uso básico:
    validator = DianaValidator()
    result = await validator.can_advance_to_level_2(user_id, reaction_data)
    if result.result == ValidationResult.PASSED:
        # Permitir transición
    """
    
    def __init__(self, service_url: str = "http://localhost:8000"):
        self.service_url = service_url
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    # ============================================
    # MÉTODOS PLUG & PLAY PARA TRANSITIONS
    # ============================================
    
    async def can_advance_to_level_2(self, user_id: int, reaction_data: Dict) -> ValidationResponse:
        """
        Valida si usuario puede avanzar de Nivel 1 → Nivel 2
        
        Args:
            user_id: ID del usuario
            reaction_data: {
                'timestamp': timestamp de la reacción,
                'speed_seconds': segundos desde el mensaje hasta la reacción,
                'message_id': ID del mensaje reaccionado
            }
        
        Returns:
            ValidationResponse con resultado y datos
        """
        try:
            async with self.session.post(
                f"{self.service_url}/api/v1/validate/level-1-to-2",
                json={
                    "user_id": user_id,
                    "reaction_speed": reaction_data.get('speed_seconds', 0),
                    "timestamp": reaction_data.get('timestamp', time.time()),
                    "message_id": reaction_data.get('message_id')
                }
            ) as response:
                data = await response.json()
                
                return ValidationResponse(
                    result=ValidationResult.PASSED if data['passed'] else ValidationResult.FAILED,
                    score=data.get('engagement_score', 0.0),
                    data={
                        'reaction_type': data.get('reaction_type'),  # 'immediate' o 'thoughtful'
                        'diana_response_variant': data.get('diana_response'),
                        'reward_type': data.get('reward_type')
                    },
                    message=data.get('message', ''),
                    next_action=data.get('next_action', '')
                )
                
        except Exception as e:
            return ValidationResponse(
                result=ValidationResult.FAILED,
                score=0.0,
                data={},
                message=f"Error de validación: {str(e)}"
            )
    
    async def can_advance_to_level_3(self, user_id: int, observation_events: List[Dict]) -> ValidationResponse:
        """
        Valida si usuario puede avanzar de Nivel 2 → Nivel 3
        
        Args:
            user_id: ID del usuario
            observation_events: Lista de eventos de observación:
            [
                {
                    'type': 'clue_found',
                    'timestamp': timestamp,
                    'clue_id': 'pista_1',
                    'time_to_find': 120  # segundos
                },
                {
                    'type': 'exploration',
                    'duration': 300,  # segundos explorando
                    'interactions': 5
                }
            ]
        """
        try:
            clues_found = len([e for e in observation_events if e['type'] == 'clue_found'])
            total_exploration_time = sum(e.get('duration', 0) for e in observation_events if e['type'] == 'exploration')
            
            async with self.session.post(
                f"{self.service_url}/api/v1/validate/level-2-to-3",
                json={
                    "user_id": user_id,
                    "observation_events": observation_events,
                    "clues_found": clues_found,
                    "total_exploration_time": total_exploration_time,
                    "observation_pattern": self._analyze_observation_pattern(observation_events)
                }
            ) as response:
                data = await response.json()
                
                return ValidationResponse(
                    result=ValidationResult.PASSED if data['passed'] else ValidationResult.FAILED,
                    score=data.get('observation_score', 0.0),
                    data={
                        'observation_type': data.get('observation_type'),  # 'explorer', 'methodical', etc.
                        'diana_recognition': data.get('diana_recognition'),
                        'reward_items': data.get('rewards', [])
                    },
                    message=data.get('message', ''),
                    next_action=data.get('next_action', '')
                )
                
        except Exception as e:
            return ValidationResponse(
                result=ValidationResult.FAILED,
                score=0.0,
                data={},
                message=f"Error de validación: {str(e)}"
            )
    
    async def can_advance_to_vip(self, user_id: int, desire_profile: Dict[str, str]) -> ValidationResponse:
        """
        Valida si usuario puede avanzar de Nivel 3 → VIP (Diván)
        
        Args:
            user_id: ID del usuario  
            desire_profile: Respuestas del perfil de deseo:
            {
                'question_1': 'respuesta del usuario...',
                'question_2': 'respuesta del usuario...',
                # ... más respuestas
            }
        """
        try:
            async with self.session.post(
                f"{self.service_url}/api/v1/validate/level-3-to-vip",
                json={
                    "user_id": user_id,
                    "desire_profile": desire_profile,
                    "response_analysis": self._analyze_responses(desire_profile)
                }
            ) as response:
                data = await response.json()
                
                return ValidationResponse(
                    result=ValidationResult.PASSED if data['passed'] else ValidationResult.FAILED,
                    score=data.get('understanding_score', 0.0),
                    data={
                        'user_archetype': data.get('archetype'),  # 'explorer', 'romantic', etc.
                        'diana_impression': data.get('diana_impression'),
                        'vip_access_type': data.get('vip_access_type'),
                        'personalized_discount': data.get('discount_percentage')
                    },
                    message=data.get('message', ''),
                    next_action=data.get('next_action', '')
                )
                
        except Exception as e:
            return ValidationResponse(
                result=ValidationResult.FAILED,
                score=0.0,
                data={},
                message=f"Error de validación: {str(e)}"
            )
    
    async def can_advance_to_level_6(self, user_id: int, empathy_responses: List[Dict]) -> ValidationResponse:
        """
        Valida si usuario puede avanzar de Nivel 5 → Nivel 6
        
        Args:
            user_id: ID del usuario
            empathy_responses: Lista de respuestas empáticas:
            [
                {
                    'diana_vulnerability': 'Texto de vulnerabilidad de Diana',
                    'user_response': 'Respuesta del usuario',
                    'response_time': 180,  # segundos para responder
                    'timestamp': timestamp
                }
            ]
        """
        try:
            async with self.session.post(
                f"{self.service_url}/api/v1/validate/level-5-to-6",
                json={
                    "user_id": user_id,
                    "empathy_responses": empathy_responses,
                    "emotional_evolution": self._calculate_emotional_evolution(user_id, empathy_responses)
                }
            ) as response:
                data = await response.json()
                
                return ValidationResponse(
                    result=ValidationResult.PASSED if data['passed'] else ValidationResult.FAILED,
                    score=data.get('empathy_score', 0.0),
                    data={
                        'emotional_maturity': data.get('maturity_level'),
                        'empathy_type': data.get('empathy_classification'),  # 'genuine', 'possessive', etc.
                        'diana_final_assessment': data.get('diana_assessment'),
                        'inner_circle_access': data.get('inner_circle', False)
                    },
                    message=data.get('message', ''),
                    next_action=data.get('next_action', '')
                )
                
        except Exception as e:
            return ValidationResponse(
                result=ValidationResult.FAILED,
                score=0.0,
                data={},
                message=f"Error de validación: {str(e)}"
            )
    
    # ============================================
    # MÉTODOS AUXILIARES PARA TRACKING
    # ============================================
    
    async def track_user_event(self, user_id: int, event_type: str, event_data: Dict) -> None:
        """
        Tracking asíncrono de eventos (no bloquea el bot)
        
        Args:
            user_id: ID del usuario
            event_type: Tipo de evento ('message', 'reaction', 'exploration', etc.)
            event_data: Datos del evento
        """
        try:
            asyncio.create_task(self._async_track_event(user_id, event_type, event_data))
        except Exception:
            pass  # No fallar nunca por tracking
    
    async def _async_track_event(self, user_id: int, event_type: str, event_data: Dict) -> None:
        """Tracking interno asíncrono"""
        try:
            async with self.session.post(
                f"{self.service_url}/api/v1/track/event",
                json={
                    "user_id": user_id,
                    "event_type": event_type,
                    "event_data": event_data,
                    "timestamp": time.time()
                }
            ) as response:
                pass  # Solo trackear, no procesar respuesta
        except Exception:
            pass  # No fallar nunca
    
    async def get_adaptive_content(self, user_id: int, content_type: str, context: Dict = None) -> Dict:
        """
        Obtiene contenido adaptado al arquetipo del usuario
        
        Args:
            user_id: ID del usuario
            content_type: Tipo de contenido ('diana_welcome', 'lucien_challenge', etc.)
            context: Contexto adicional
            
        Returns:
            {
                'text': 'Texto personalizado para el usuario',
                'buttons': [{'text': 'Botón', 'callback': 'callback'}],
                'media': 'URL de imagen/video opcional',
                'archetype': 'Arquetipo detectado'
            }
        """
        try:
            async with self.session.get(
                f"{self.service_url}/api/v1/content/{user_id}/{content_type}",
                params=context or {}
            ) as response:
                return await response.json()
        except Exception:
            # Fallback a contenido por defecto
            return {
                'text': f"Contenido por defecto para {content_type}",
                'buttons': [],
                'media': None,
                'archetype': 'unknown'
            }
    
    async def get_user_archetype(self, user_id: int) -> str:
        """
        Obtiene el arquetipo actual del usuario
        
        Returns:
            'explorer', 'direct', 'romantic', 'analytical', 'persistent', 'patient', o 'unknown'
        """
        try:
            async with self.session.get(f"{self.service_url}/api/v1/user/{user_id}/archetype") as response:
                data = await response.json()
                return data.get('archetype', 'unknown')
        except Exception:
            return 'unknown'
    
    # ============================================
    # MÉTODOS PRIVADOS AUXILIARES
    # ============================================
    
    def _analyze_observation_pattern(self, events: List[Dict]) -> str:
        """Analiza patrón de observación básico"""
        if len(events) > 10:
            return 'exhaustive'
        elif len(events) > 5:
            return 'methodical'
        else:
            return 'focused'
    
    def _analyze_responses(self, responses: Dict[str, str]) -> Dict:
        """Análisis básico de respuestas"""
        total_length = sum(len(r) for r in responses.values())
        avg_length = total_length / len(responses) if responses else 0
        
        return {
            'total_responses': len(responses),
            'average_length': avg_length,
            'depth_indicator': 'deep' if avg_length > 100 else 'surface'
        }
    
    def _calculate_emotional_evolution(self, user_id: int, responses: List[Dict]) -> Dict:
        """Calcula evolución emocional básica"""
        if len(responses) < 2:
            return {'evolution': 'insufficient_data'}
        
        first_response_length = len(responses[0].get('user_response', ''))
        last_response_length = len(responses[-1].get('user_response', ''))
        
        return {
            'evolution': 'positive' if last_response_length > first_response_length else 'stable',
            'response_count': len(responses),
            'growth_indicator': last_response_length / first_response_length if first_response_length > 0 else 1.0
        }


# ============================================
# WRAPPER PARA USAR CON TRANSITIONS
# ============================================

class DianaValidatorForTransitions:
    """
    Wrapper específico para usar con transitions
    Hace que las validaciones sean super fáciles de usar como conditions
    """
    
    def __init__(self, validator: DianaValidator):
        self.validator = validator
        self.last_validation_result = None
    
    async def validate_level_1_completion(self, user_id: int, reaction_data: Dict) -> bool:
        """Para usar como condition en transitions"""
        result = await self.validator.can_advance_to_level_2(user_id, reaction_data)
        self.last_validation_result = result
        return result.result == ValidationResult.PASSED
    
    async def validate_level_2_completion(self, user_id: int, observation_events: List[Dict]) -> bool:
        """Para usar como condition en transitions"""
        result = await self.validator.can_advance_to_level_3(user_id, observation_events)
        self.last_validation_result = result
        return result.result == ValidationResult.PASSED
    
    async def validate_level_3_completion(self, user_id: int, desire_profile: Dict) -> bool:
        """Para usar como condition en transitions"""
        result = await self.validator.can_advance_to_vip(user_id, desire_profile)
        self.last_validation_result = result
        return result.result == ValidationResult.PASSED
    
    async def validate_level_5_completion(self, user_id: int, empathy_responses: List[Dict]) -> bool:
        """Para usar como condition en transitions"""
        result = await self.validator.can_advance_to_level_6(user_id, empathy_responses)
        self.last_validation_result = result
        return result.result == ValidationResult.PASSED
    
    def get_last_validation_data(self) -> Optional[ValidationResponse]:
        """Obtiene datos de la última validación para personalizar respuestas"""
        return self.last_validation_result


# ============================================
# EJEMPLO DE USO PLUG & PLAY
# ============================================

"""
# En tu bot principal:

from diana_validation_client import DianaValidator, DianaValidatorForTransitions, ValidationResult

class DianaBot:
    def __init__(self):
        self.validator = DianaValidator("http://validation-service:8000")
        self.transitions_validator = DianaValidatorForTransitions(self.validator)
        self.setup_state_machine()
    
    async def setup_state_machine(self):
        # Configurar transitions con validaciones
        transitions = [
            {
                'trigger': 'user_reacted',
                'source': 'level_1_challenge',
                'dest': 'level_2_observation',
                'conditions': self.check_level_1,
                'after': 'deliver_level_1_rewards'
            }
        ]
    
    async def check_level_1(self):
        # ¡Una sola línea para validar!
        return await self.transitions_validator.validate_level_1_completion(
            self.user_id, 
            self.last_reaction_data
        )
    
    async def deliver_level_1_rewards(self):
        # Obtener datos de la validación para personalizar
        validation_data = self.transitions_validator.get_last_validation_data()
        
        # Contenido adaptado automáticamente
        content = await self.validator.get_adaptive_content(
            self.user_id, 
            'mochila_reward',
            {'reaction_type': validation_data.data['reaction_type']}
        )
        
        await self.send_message(content['text'])
"""
