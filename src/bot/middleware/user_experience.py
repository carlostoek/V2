"""
🎭 USER EXPERIENCE MIDDLEWARE
============================

Advanced UX middleware that enhances user interactions with:
- Smart onboarding flow detection
- Contextual help injection  
- User journey tracking
- Engagement optimization
- Error recovery assistance

This middleware works seamlessly with Diana's personality to create
exceptional user experiences.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
import structlog

class UserJourneyStage(Enum):
    """User journey stages for personalized experiences"""
    FIRST_VISIT = "first_visit"
    ONBOARDING = "onboarding" 
    EXPLORATION = "exploration"
    ENGAGEMENT = "engagement"
    CONVERSION_READY = "conversion_ready"
    ACTIVE_USER = "active_user"
    VIP_USER = "vip_user"

@dataclass
class UserExperienceState:
    """Complete user experience state tracking"""
    user_id: int
    journey_stage: UserJourneyStage
    onboarding_completed: bool
    help_tips_shown: List[str]
    last_error_time: Optional[datetime]
    session_start: datetime
    interaction_count: int
    needs_guidance: bool
    preferred_interaction_style: str
    conversion_signals: int

class UserExperienceMiddleware(BaseMiddleware):
    """
    🌟 Advanced UX Middleware
    
    Enhances every user interaction with:
    - Intelligent onboarding detection
    - Contextual help suggestions
    - Error prevention and recovery
    - User journey optimization
    - Diana personality consistency
    """
    
    def __init__(self, services: Dict[str, Any]):
        self.services = services
        self.logger = structlog.get_logger()
        
        # User experience state tracking
        self.user_states: Dict[int, UserExperienceState] = {}
        self.journey_analytics: Dict[int, List[Dict]] = {}
        
        # UX Configuration
        self.onboarding_tips = {
            "first_interaction": "💡 <i>Consejo de Diana: Explora las diferentes secciones para descubrir mis secretos...</i>",
            "vip_discovery": "✨ <i>Lucien sugiere: El Diván VIP ofrece experiencias más íntimas y personales.</i>",
            "gamification_intro": "🎮 <i>Diana observa: Completar desafíos te acerca más a mi círculo íntimo.</i>",
            "content_packages": "🎁 <i>Susurro de Diana: Cada tesoro ha sido creado pensando en almas especiales como la tuya.</i>"
        }
        
        self.contextual_help = {
            "navigation": "🧭 <b>Navegación:</b> Usa los botones para explorar, '🔙' para regresar, '🔄' para actualizar.",
            "vip_benefits": "💎 <b>VIP:</b> Acceso ilimitado a contenido exclusivo, chat directo, y experiencias personalizadas.",
            "points_system": "⭐ <b>Besitos:</b> Cada interacción y desafío completado te otorga puntos de atención de Diana.",
            "conversion": "🌹 <b>Próximo paso:</b> Cuando estés listo para una experiencia más íntima, el Diván VIP te espera."
        }
    
    async def __call__(
        self,
        handler,
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Process every user interaction for UX enhancement"""
        
        # Only process user messages and callbacks
        if not isinstance(event, (Message, CallbackQuery)):
            return await handler(event, data)
        
        user_id = event.from_user.id
        
        # Initialize or update user experience state
        await self._update_user_experience_state(user_id, event)
        
        # Pre-process: Add UX enhancements to data
        data['ux_state'] = self.user_states.get(user_id)
        data['ux_tips'] = await self._generate_contextual_tips(user_id, event)
        data['ux_middleware'] = self  # Allow handlers to access middleware
        
        try:
            # Execute the handler
            result = await handler(event, data)
            
            # Post-process: Track successful interaction
            await self._track_successful_interaction(user_id, event)
            
            return result
            
        except Exception as e:
            # Enhanced error handling with user-friendly recovery
            await self._handle_error_with_recovery(user_id, event, e)
            raise e
    
    async def _update_user_experience_state(self, user_id: int, event: TelegramObject):
        """Update or create user experience state"""
        
        now = datetime.now()
        
        if user_id not in self.user_states:
            # New user - initialize state
            journey_stage = await self._detect_initial_journey_stage(user_id)
            
            self.user_states[user_id] = UserExperienceState(
                user_id=user_id,
                journey_stage=journey_stage,
                onboarding_completed=False,
                help_tips_shown=[],
                last_error_time=None,
                session_start=now,
                interaction_count=1,
                needs_guidance=True,
                preferred_interaction_style="guided",
                conversion_signals=0
            )
            
            self.logger.info("New user experience state initialized", 
                           user_id=user_id, 
                           journey_stage=journey_stage.value)
        else:
            # Existing user - update state
            state = self.user_states[user_id]
            state.interaction_count += 1
            
            # Update journey stage based on activity
            new_stage = await self._analyze_journey_progression(user_id, event)
            if new_stage != state.journey_stage:
                self.logger.info("User journey stage updated", 
                               user_id=user_id,
                               old_stage=state.journey_stage.value,
                               new_stage=new_stage.value)
                state.journey_stage = new_stage
            
            # Detect if user needs guidance
            state.needs_guidance = await self._detect_guidance_need(user_id, event)
    
    async def _detect_initial_journey_stage(self, user_id: int) -> UserJourneyStage:
        """Detect initial journey stage for new users"""
        try:
            # Check if user has any existing data
            if 'gamification' in self.services:
                user_stats = await self.services['gamification'].get_user_stats(user_id)
                if user_stats.get('level', 0) > 1:
                    return UserJourneyStage.ACTIVE_USER
            
            # Check VIP status
            if 'admin' in self.services and hasattr(self.services['admin'], 'is_vip_user'):
                is_vip = await self.services['admin'].is_vip_user(user_id)
                if is_vip:
                    return UserJourneyStage.VIP_USER
            
        except Exception as e:
            self.logger.warning("Error detecting initial journey stage", error=str(e))
        
        return UserJourneyStage.FIRST_VISIT
    
    async def _analyze_journey_progression(self, user_id: int, event: TelegramObject) -> UserJourneyStage:
        """Analyze user journey progression based on activity"""
        state = self.user_states[user_id]
        
        try:
            # Check VIP status first
            if 'admin' in self.services and hasattr(self.services['admin'], 'is_vip_user'):
                is_vip = await self.services['admin'].is_vip_user(user_id)
                if is_vip:
                    return UserJourneyStage.VIP_USER
            
            # Analyze engagement patterns
            if isinstance(event, CallbackQuery):
                callback_data = event.data
                
                # VIP interest signals
                if 'vip' in callback_data.lower() or 'premium' in callback_data.lower():
                    state.conversion_signals += 1
                    if state.conversion_signals >= 3:
                        return UserJourneyStage.CONVERSION_READY
                
                # High engagement patterns
                if state.interaction_count > 10:
                    return UserJourneyStage.ENGAGEMENT
                elif state.interaction_count > 5:
                    return UserJourneyStage.EXPLORATION
                elif state.interaction_count > 2:
                    return UserJourneyStage.ONBOARDING
            
        except Exception as e:
            self.logger.warning("Error analyzing journey progression", error=str(e))
        
        return state.journey_stage
    
    async def _generate_contextual_tips(self, user_id: int, event: TelegramObject) -> List[str]:
        """Generate contextual tips based on user state and current action"""
        state = self.user_states.get(user_id)
        if not state:
            return []
        
        tips = []
        
        # Journey-stage specific tips
        if state.journey_stage == UserJourneyStage.FIRST_VISIT:
            if "first_interaction" not in state.help_tips_shown:
                tips.append(self.onboarding_tips["first_interaction"])
                state.help_tips_shown.append("first_interaction")
        
        elif state.journey_stage == UserJourneyStage.EXPLORATION:
            if isinstance(event, CallbackQuery) and "vip" in event.data.lower():
                if "vip_discovery" not in state.help_tips_shown:
                    tips.append(self.onboarding_tips["vip_discovery"])
                    state.help_tips_shown.append("vip_discovery")
        
        elif state.journey_stage == UserJourneyStage.CONVERSION_READY:
            tips.append("🌟 <i>Diana siente tu interés creciente... ¿Estás listo para el próximo nivel?</i>")
        
        # Context-specific tips
        if isinstance(event, CallbackQuery):
            callback_data = event.data.lower()
            
            if 'package' in callback_data and "content_packages" not in state.help_tips_shown:
                tips.append(self.onboarding_tips["content_packages"])
                state.help_tips_shown.append("content_packages")
            
            elif 'mission' in callback_data and "gamification_intro" not in state.help_tips_shown:
                tips.append(self.onboarding_tips["gamification_intro"])
                state.help_tips_shown.append("gamification_intro")
        
        return tips
    
    async def _detect_guidance_need(self, user_id: int, event: TelegramObject) -> bool:
        """Detect if user needs guidance based on behavior patterns"""
        state = self.user_states.get(user_id)
        if not state:
            return True
        
        # New users always need guidance
        if state.journey_stage in [UserJourneyStage.FIRST_VISIT, UserJourneyStage.ONBOARDING]:
            return True
        
        # Users with recent errors need guidance
        if state.last_error_time and (datetime.now() - state.last_error_time) < timedelta(minutes=5):
            return True
        
        # Users showing confusion patterns (rapid back/forth navigation)
        if isinstance(event, CallbackQuery):
            recent_actions = self._get_recent_actions(user_id)
            if len(recent_actions) > 3 and all('back' in action for action in recent_actions[-3:]):
                return True
        
        return False
    
    def _get_recent_actions(self, user_id: int) -> List[str]:
        """Get recent user actions for pattern analysis"""
        return self.journey_analytics.get(user_id, [])[-10:]  # Last 10 actions
    
    async def _track_successful_interaction(self, user_id: int, event: TelegramObject):
        """Track successful interactions for analytics"""
        if user_id not in self.journey_analytics:
            self.journey_analytics[user_id] = []
        
        interaction_data = {
            'timestamp': datetime.now(),
            'type': type(event).__name__,
            'success': True
        }
        
        if isinstance(event, CallbackQuery):
            interaction_data['callback_data'] = event.data
        elif isinstance(event, Message):
            interaction_data['message_type'] = 'command' if event.text and event.text.startswith('/') else 'text'
        
        self.journey_analytics[user_id].append(interaction_data)
        
        # Keep only last 50 interactions
        if len(self.journey_analytics[user_id]) > 50:
            self.journey_analytics[user_id] = self.journey_analytics[user_id][-50:]
    
    async def _handle_error_with_recovery(self, user_id: int, event: TelegramObject, error: Exception):
        """Enhanced error handling with user-friendly recovery suggestions"""
        state = self.user_states.get(user_id)
        if state:
            state.last_error_time = datetime.now()
        
        self.logger.error("User experience error with enhanced recovery", 
                         user_id=user_id, 
                         error=str(error),
                         event_type=type(event).__name__)
        
        # TODO: Could implement automatic error recovery messages here
        # For now, we let the error propagate but with enhanced context
    
    # === UX HELPER METHODS FOR HANDLERS ===
    
    def get_user_onboarding_status(self, user_id: int) -> Dict[str, Any]:
        """Get user onboarding status for handlers"""
        state = self.user_states.get(user_id)
        if not state:
            return {'needs_onboarding': True, 'stage': 'new_user'}
        
        return {
            'needs_onboarding': not state.onboarding_completed,
            'stage': state.journey_stage.value,
            'needs_guidance': state.needs_guidance,
            'interaction_count': state.interaction_count,
            'conversion_signals': state.conversion_signals
        }
    
    def mark_onboarding_completed(self, user_id: int):
        """Mark onboarding as completed for a user"""
        state = self.user_states.get(user_id)
        if state:
            state.onboarding_completed = True
            state.needs_guidance = False
            self.logger.info("User onboarding completed", user_id=user_id)
    
    def add_conversion_signal(self, user_id: int, signal_type: str):
        """Add conversion signal for analytics"""
        state = self.user_states.get(user_id)
        if state:
            state.conversion_signals += 1
            self.logger.info("Conversion signal added", 
                           user_id=user_id, 
                           signal_type=signal_type,
                           total_signals=state.conversion_signals)

def create_user_experience_middleware(services: Dict[str, Any]) -> UserExperienceMiddleware:
    """Factory function to create UX middleware"""
    return UserExperienceMiddleware(services)