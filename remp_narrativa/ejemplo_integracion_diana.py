# ejemplo_integracion_diana.py
"""
EJEMPLO COMPLETO DE INTEGRACIÓN
Bot Diana con Transitions + Sistema de Validaciones
¡Copiar y pegar directamente!
"""

from transitions.extensions.asyncio import AsyncMachine
from diana_validation_client import DianaValidator, DianaValidatorForTransitions, ValidationResult
import asyncio
import time
from typing import Dict, List

class DianaBot:
    """
    Bot Diana con integración completa del sistema de validaciones
    ¡Plug & Play!
    """
    
    # Estados del bot
    states = [
        'level_1_intro',
        'level_1_challenge', 
        'level_2_observation',
        'level_2_searching_clues',
        'level_3_desire_profile',
        'level_4_vip_intro',
        'level_5_empathy_test',
        'level_6_synthesis',
        'inner_circle'
    ]
    
    def __init__(self, user_id: int, validation_service_url: str = "http://localhost:8000"):
        self.user_id = user_id
        
        # ============================================
        # CONFIGURACIÓN SÚPER SIMPLE - 3 LÍNEAS
        # ============================================
        self.validator = DianaValidator(validation_service_url)
        self.transitions_validator = DianaValidatorForTransitions(self.validator)
        
        # Data storage para validaciones
        self.reaction_data = {}
        self.observation_events = []
        self.desire_responses = {}
        self.empathy_responses = []
        
        # Configurar máquina de estados
        self.setup_state_machine()
    
    def setup_state_machine(self):
        """Configuración de transitions con validaciones integradas"""
        
        transitions = [
            # Nivel 1 → Nivel 2
            {
                'trigger': 'user_reacted_to_post',
                'source': 'level_1_challenge',
                'dest': 'level_2_observation',
                'conditions': 'validate_level_1_reaction',  # ← Validación automática
                'after': 'deliver_level_1_rewards'
            },
            
            # Nivel 2 → Nivel 3
            {
                'trigger': 'observation_completed',
                'source': ['level_2_observation', 'level_2_searching_clues'],
                'dest': 'level_3_desire_profile',
                'conditions': 'validate_observation_skills',  # ← Validación automática
                'after': 'deliver_observation_rewards'
            },
            
            # Nivel 3 → VIP
            {
                'trigger': 'profile_completed',
                'source': 'level_3_desire_profile',
                'dest': 'level_4_vip_intro',
                'conditions': 'validate_desire_understanding',  # ← Validación automática
                'after': 'unlock_vip_access'
            },
            
            # Nivel 5 → Nivel 6
            {
                'trigger': 'empathy_completed',
                'source': 'level_5_empathy_test',
                'dest': 'level_6_synthesis',
                'conditions': 'validate_emotional_maturity',  # ← Validación automática
                'after': 'unlock_inner_circle'
            },
            
            # Transiciones adicionales para manejo de fallos
            {
                'trigger': 'validation_failed',
                'source': '*',
                'dest': '=',  # Mantiene estado actual
                'after': 'handle_validation_failure'
            }
        ]
        
        # Inicializar máquina de estados
        self.machine = AsyncMachine(
            model=self,
            states=self.states,
            transitions=transitions,
            initial='level_1_intro',
            auto_transitions=False
        )
    
    # ============================================
    # MÉTODOS DE VALIDACIÓN - PLUG & PLAY
    # ============================================
    
    async def validate_level_1_reaction(self) -> bool:
        """Validación para Nivel 1 → Nivel 2"""
        try:
            # ¡Una sola línea para validar!
            result = await self.validator.can_advance_to_level_2(self.user_id, self.reaction_data)
            
            if result.result == ValidationResult.PASSED:
                # Guardar datos para personalización posterior
                self.last_validation = result
                return True
            else:
                # Manejar fallo automáticamente
                await self.handle_validation_failure_with_guidance(result)
                return False
                
        except Exception as e:
            print(f"Error en validación nivel 1: {e}")
            return False
    
    async def validate_observation_skills(self) -> bool:
        """Validación para Nivel 2 → Nivel 3"""
        try:
            result = await self.validator.can_advance_to_level_3(self.user_id, self.observation_events)
            
            if result.result == ValidationResult.PASSED:
                self.last_validation = result
                return True
            else:
                await self.handle_validation_failure_with_guidance(result)
                return False
                
        except Exception as e:
            print(f"Error en validación nivel 2: {e}")
            return False
    
    async def validate_desire_understanding(self) -> bool:
        """Validación para Nivel 3 → VIP"""
        try:
            result = await self.validator.can_advance_to_vip(self.user_id, self.desire_responses)
            
            if result.result == ValidationResult.PASSED:
                self.last_validation = result
                return True
            else:
                await self.handle_validation_failure_with_guidance(result)
                return False
                
        except Exception as e:
            print(f"Error en validación nivel 3: {e}")
            return False
    
    async def validate_emotional_maturity(self) -> bool:
        """Validación para Nivel 5 → Nivel 6"""
        try:
            result = await self.validator.can_advance_to_level_6(self.user_id, self.empathy_responses)
            
            if result.result == ValidationResult.PASSED:
                self.last_validation = result
                return True
            else:
                await self.handle_validation_failure_with_guidance(result)
                return False
                
        except Exception as e:
            print(f"Error en validación nivel 5: {e}")
            return False
    
    # ============================================
    # HANDLERS DE EVENTOS DEL BOT
    # ============================================
    
    async def handle_user_reaction(self, message_id: str, reaction_emoji: str, timestamp: float):
        """
        Handler cuando usuario reacciona a un mensaje en el canal
        ¡Llamar desde tu bot cuando detectes reacción!
        """
        # Calcular velocidad de reacción
        reaction_speed = time.time() - timestamp
        
        # Guardar datos para validación
        self.reaction_data = {
            'message_id': message_id,
            'reaction_emoji': reaction_emoji,
            'timestamp': timestamp,
            'speed_seconds': reaction_speed
        }
        
        # Track automático del evento
        await self.validator.track_user_event(
            self.user_id, 
            'reaction', 
            self.reaction_data
        )
        
        # Intentar transición si está en estado correcto
        if self.state == 'level_1_challenge':
            try:
                await self.user_reacted_to_post()
            except Exception as e:
                print(f"Transición fallida: {e}")
    
    async def handle_user_message(self, message_text: str, timestamp: float):
        """
        Handler para mensajes de texto del usuario
        ¡Llamar desde tu bot para cada mensaje!
        """
        # Track automático
        await self.validator.track_user_event(
            self.user_id,
            'message',
            {'text': message_text, 'timestamp': timestamp}
        )
        
        # Procesar según estado actual
        if self.state == 'level_3_desire_profile':
            await self.process_desire_response(message_text)
        elif self.state == 'level_5_empathy_test':
            await self.process_empathy_response(message_text)
        
    async def handle_clue_found(self, clue_id: str, time_to_find: int):
        """
        Handler cuando usuario encuentra una pista
        ¡Llamar cuando detectes que encontró una pista!
        """
        clue_event = {
            'type': 'clue_found',
            'clue_id': clue_id,
            'timestamp': time.time(),
            'time_to_find': time_to_find
        }
        
        self.observation_events.append(clue_event)
        
        # Track automático
        await self.validator.track_user_event(
            self.user_id,
            'clue_found',
            clue_event
        )
        
        # Verificar si puede avanzar
        if len(self.observation_events) >= 3:  # Ejemplo: necesita 3 pistas
            try:
                await self.observation_completed()
            except Exception as e:
                print(f"No puede avanzar aún: {e}")
    
    # ============================================
    # CALLBACKS DE ESTADOS CON PERSONALIZACIÓN
    # ============================================
    
    async def deliver_level_1_rewards(self):
        """Callback al completar Nivel 1 - Personalizado automáticamente"""
        # Obtener contenido personalizado basado en la validación
        validation_data = self.last_validation.data
        
        content = await self.validator.get_adaptive_content(
            self.user_id,
            'level_1_reward',
            {
                'reaction_type': validation_data.get('reaction_type'),
                'state': self.state
            }
        )
        
        # Enviar mensaje personalizado
        await self.send_message_to_user(content['text'])
        
        # Entregar recompensas específicas
        await self.add_to_inventory('mochila_viajero')
        await self.add_to_inventory('pista_1')
        
        print(f"✅ Nivel 1 completado - Tipo: {validation_data.get('reaction_type')}")
    
    async def deliver_observation_rewards(self):
        """Callback al completar Nivel 2 - Personalizado por arquetipo"""
        validation_data = self.last_validation.data
        
        content = await self.validator.get_adaptive_content(
            self.user_id,
            'level_2_reward',
            {
                'observation_type': validation_data.get('observation_type'),
                'archetype': validation_data.get('user_archetype', 'unknown')
            }
        )
        
        await self.send_message_to_user(content['text'])
        
        # Recompensas específicas por arquetipo
        rewards = validation_data.get('reward_items', ['pista_2'])
        for reward in rewards:
            await self.add_to_inventory(reward)
        
        print(f"✅ Nivel 2 completado - Arquetipo: {validation_data.get('observation_type')}")
    
    async def unlock_vip_access(self):
        """Callback al desbloquear VIP - Con descuento personalizado"""
        validation_data = self.last_validation.data
        
        # Descuento personalizado basado en comprensión
        discount = validation_data.get('personalized_discount', 10)
        archetype = validation_data.get('user_archetype', 'unknown')
        
        content = await self.validator.get_adaptive_content(
            self.user_id,
            'vip_unlock',
            {
                'archetype': archetype,
                'discount': discount,
                'diana_impression': validation_data.get('diana_impression')
            }
        )
        
        await self.send_message_to_user(content['text'])
        await self.send_vip_payment_link(discount_percentage=discount)
        
        print(f"✅ VIP desbloqueado - Arquetipo: {archetype}, Descuento: {discount}%")
    
    async def unlock_inner_circle(self):
        """Callback al acceder al círculo íntimo"""
        validation_data = self.last_validation.data
        
        if validation_data.get('inner_circle_access', False):
            content = await self.validator.get_adaptive_content(
                self.user_id,
                'inner_circle_welcome',
                {
                    'emotional_maturity': validation_data.get('emotional_maturity'),
                    'empathy_type': validation_data.get('empathy_type')
                }
            )
            
            await self.send_message_to_user(content['text'])
            await self.grant_inner_circle_access()
            
            print(f"✅ Círculo íntimo desbloqueado - Madurez: {validation_data.get('emotional_maturity')}")
    
    # ============================================
    # MANEJO DE FALLOS CON GUÍA AUTOMÁTICA
    # ============================================
    
    async def handle_validation_failure_with_guidance(self, validation_result: 'ValidationResponse'):
        """Manejo inteligente de fallos con guía personalizada"""
        
        # Obtener contenido de guía personalizado
        content = await self.validator.get_adaptive_content(
            self.user_id,
            'validation_guidance',
            {
                'failure_reason': validation_result.message,
                'current_state': self.state,
                'score': validation_result.score,
                'next_action': validation_result.next_action
            }
        )
        
        await self.send_message_to_user(content['text'])
        
        print(f"❌ Validación fallida: {validation_result.message}")
        print(f"📋 Siguiente acción: {validation_result.next_action}")
    
    async def handle_validation_failure(self):
        """Callback genérico para fallos"""
        await self.send_message_to_user("Diana nota que necesitas más tiempo para comprender...")
    
    # ============================================
    # MÉTODOS DE PROCESAMIENTO ESPECÍFICOS
    # ============================================
    
    async def process_desire_response(self, text: str):
        """Procesa respuesta del perfil de deseo"""
        current_question = f"question_{len(self.desire_responses) + 1}"
        
        self.desire_responses[current_question] = text
        
        # Si completó todas las preguntas (ejemplo: 5)
        if len(self.desire_responses) >= 5:
            try:
                await self.profile_completed()
            except Exception as e:
                print(f"No puede avanzar a VIP: {e}")
        else:
            await self.ask_next_desire_question()
    
    async def process_empathy_response(self, text: str):
        """Procesa respuesta empática"""
        empathy_data = {
            'diana_vulnerability': self.current_vulnerability_text,
            'user_response': text,
            'response_time': time.time() - self.vulnerability_timestamp,
            'timestamp': time.time()
        }
        
        self.empathy_responses.append(empathy_data)
        
        # Si completó todas las evaluaciones empáticas
        if len(self.empathy_responses) >= 3:
            try:
                await self.empathy_completed()
            except Exception as e:
                print(f"No puede avanzar al nivel 6: {e}")
        else:
            await self.present_next_vulnerability()
    
    # ============================================
    # MÉTODOS AUXILIARES (IMPLEMENTAR SEGÚN TU BOT)
    # ============================================
    
    async def send_message_to_user(self, text: str):
        """Enviar mensaje al usuario - Implementar según tu bot"""
        print(f"🤖 Bot: {text}")
        # TODO: Integrar con tu sistema de mensajes
    
    async def add_to_inventory(self, item: str):
        """Agregar item al inventario - Implementar según tu sistema"""
        print(f"📦 Inventario +: {item}")
        # TODO: Integrar con tu sistema de inventario
    
    async def send_vip_payment_link(self, discount_percentage: int):
        """Enviar link de pago VIP - Implementar según tu sistema"""
        print(f"💳 Enviando link VIP con {discount_percentage}% descuento")
        # TODO: Integrar con tu sistema de pagos
    
    async def grant_inner_circle_access(self):
        """Otorgar acceso al círculo íntimo - Implementar según tu sistema"""
        print("👑 Acceso al círculo íntimo otorgado")
        # TODO: Integrar con tu sistema de accesos
    
    async def ask_next_desire_question(self):
        """Hacer siguiente pregunta del perfil de deseo"""
        question_num = len(self.desire_responses) + 1
        content = await self.validator.get_adaptive_content(
            self.user_id,
            f'desire_question_{question_num}',
            {'current_progress': len(self.desire_responses)}
        )
        await self.send_message_to_user(content['text'])
    
    async def present_next_vulnerability(self):
        """Presentar siguiente vulnerabilidad de Diana"""
        vulnerability_num = len(self.empathy_responses) + 1
        content = await self.validator.get_adaptive_content(
            self.user_id,
            f'diana_vulnerability_{vulnerability_num}',
            {'empathy_progress': len(self.empathy_responses)}
        )
        
        self.current_vulnerability_text = content['text']
        self.vulnerability_timestamp = time.time()
        
        await self.send_message_to_user(content['text'])


# ============================================
# EJEMPLO DE USO COMPLETO
# ============================================

async def ejemplo_uso_completo():
    """
    Ejemplo de cómo usar el bot completo
    ¡Copiar este patrón!
    """
    
    # Inicializar bot para un usuario
    user_id = 12345
    bot = DianaBot(user_id, "http://validation-service:8000")
    
    print(f"🎭 Bot Diana iniciado para usuario {user_id}")
    print(f"📍 Estado inicial: {bot.state}")
    
    # Simular eventos del usuario
    
    # 1. Usuario reacciona a mensaje en canal
    await bot.handle_user_reaction(
        message_id="msg_123",
        reaction_emoji="❤️", 
        timestamp=time.time() - 30  # Reaccionó en 30 segundos
    )
    
    print(f"📍 Estado después de reacción: {bot.state}")
    
    # 2. Usuario encuentra pistas
    await bot.handle_clue_found("pista_oculta_1", time_to_find=120)
    await bot.handle_clue_found("pista_oculta_2", time_to_find=300) 
    await bot.handle_clue_found("pista_oculta_3", time_to_find=180)
    
    print(f"📍 Estado después de pistas: {bot.state}")
    
    # 3. Usuario responde perfil de deseo
    desire_responses = [
        "Busco conexión auténtica, no superficial",
        "Me atrae la complejidad emocional",
        "Valoro el misterio y la profundidad",
        "Prefiero calidad sobre cantidad",
        "El respeto mutuo es fundamental"
    ]
    
    for response in desire_responses:
        await bot.handle_user_message(response, time.time())
    
    print(f"📍 Estado después de perfil: {bot.state}")
    
    # Y así sucesivamente...


if __name__ == "__main__":
    # Ejecutar ejemplo
    asyncio.run(ejemplo_uso_completo())
