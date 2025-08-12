"""
Listener for narrative and emotional system events.

This module handles narrative progression events and triggers appropriate
emotional state changes in Diana's personality system.
"""

import structlog
from typing import Dict, Any
from datetime import datetime

from aiogram import Bot
from src.core.interfaces.IEventBus import IEventBus
from src.modules.events import (
    UserStartedBotEvent,
    PointsAwardedEvent, 
    MissionCompletedEvent,
    LevelUpEvent,
    NarrativeProgressionEvent,
    PieceUnlockedEvent
)
from src.modules.narrative.service import NarrativeService
from src.modules.emotional.service import EmotionalService
from src.modules.emotional.diana_state import EmotionalTrigger

logger = structlog.get_logger()

class NarrativeEventListener:
    """
    Listener for narrative and emotional events.
    
    This listener subscribes to system events and triggers appropriate
    narrative responses and emotional state changes for Diana.
    """
    
    def __init__(self, bot: Bot, event_bus: IEventBus, narrative_service: NarrativeService, emotional_service: EmotionalService = None):
        """
        Initialize the narrative listener.
        
        Args:
            bot: Bot instance for sending messages.
            event_bus: Event bus.
            narrative_service: Narrative service.
            emotional_service: Emotional service (optional).
        """
        self.bot = bot
        self.event_bus = event_bus
        self.narrative_service = narrative_service
        self.emotional_service = emotional_service
        self.user_interaction_history: Dict[int, list] = {}  # Track user interactions
        
        # Register event handlers
        self._register_event_handlers()
        
        logger.info("NarrativeEventListener initialized")
    
    def _register_event_handlers(self) -> None:
        """Register event handlers."""
        self.event_bus.subscribe(UserStartedBotEvent, self.handle_user_started)
        self.event_bus.subscribe(PointsAwardedEvent, self.handle_points_awarded)
        self.event_bus.subscribe(MissionCompletedEvent, self.handle_mission_completed)
        self.event_bus.subscribe(LevelUpEvent, self.handle_level_up)
        self.event_bus.subscribe(NarrativeProgressionEvent, self.handle_narrative_progression)
        self.event_bus.subscribe(PieceUnlockedEvent, self.handle_piece_unlocked)
        
        logger.info("NarrativeEventListener: Events registered")
    
    async def handle_user_started(self, event: UserStartedBotEvent) -> None:
        """
        Handle user started event with emotional context.
        
        Args:
            event: User started event.
        """
        user_id = event.user_id
        logger.info(f"New user started: {user_id}")
        
        # Initialize user interaction history
        if user_id not in self.user_interaction_history:
            self.user_interaction_history[user_id] = []
        
        self.user_interaction_history[user_id].append({
            "event": "user_started",
            "timestamp": datetime.now().isoformat()
        })
        
        # Trigger initial emotional state (Neutral -> Happy for new users)
        if self.emotional_service:
            try:
                await self.emotional_service.trigger_state_change(
                    user_id=user_id,
                    trigger=EmotionalTrigger.POSITIVE_INTERACTION,
                    context={
                        "source": "user_started", 
                        "reason": "new_user_welcome",
                        "intensity": "medium"
                    }
                )
                logger.info(f"Emotional state set to HAPPY for new user {user_id}")
            except Exception as e:
                logger.error(f"Failed to set initial emotional state for user {user_id}: {e}")
        
        # Send narrative welcome (this is already handled in narrative service)
        # but we can add emotional context here if needed
        
        # Send emotionally-aware welcome message
        try:
            welcome_message = "🌸 *¡Bienvenido a mi mundo!*\n\n"
            welcome_message += "Soy Diana, y estoy emocionada de conocerte. "
            welcome_message += "Juntos vamos a vivir una historia única llena de secretos, emociones y aventuras.\n\n"
            welcome_message += "Tu historia personal ya está comenzando... 📖✨"
            
            # Apply emotional modification if service available
            if self.emotional_service:
                welcome_message = await self.emotional_service.modify_response(
                    user_id=user_id,
                    original_response=welcome_message,
                    context={"source": "user_started", "first_interaction": True}
                )
            
            await self.bot.send_message(
                chat_id=user_id,
                text=welcome_message,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Failed to send welcome message to user {user_id}: {e}")
    
    async def handle_points_awarded(self, event: PointsAwardedEvent) -> None:
        """
        Handle points awarded event with emotional and narrative context.
        
        Args:
            event: Points awarded event.
        """
        user_id = event.user_id
        points = event.points
        source = event.source_event
        
        logger.info(f"Points awarded to user {user_id}: {points} from {source}")
        
        # Update interaction history
        if user_id not in self.user_interaction_history:
            self.user_interaction_history[user_id] = []
        
        self.user_interaction_history[user_id].append({
            "event": "points_awarded",
            "points": points,
            "source": source,
            "timestamp": datetime.now().isoformat()
        })
        
        # Trigger emotional state changes based on points and frequency
        if self.emotional_service:
            try:
                # Determine emotional trigger based on point amount and frequency
                recent_interactions = [
                    interaction for interaction in self.user_interaction_history[user_id]
                    if (datetime.now() - datetime.fromisoformat(interaction["timestamp"])).total_seconds() < 300  # Last 5 minutes
                ]
                
                if len(recent_interactions) >= 3:
                    # User is very active - trigger PLAYFUL state
                    trigger = EmotionalTrigger.HIGH_ENGAGEMENT
                    context = {"source": "high_activity", "recent_interactions": len(recent_interactions)}
                elif points >= 50:
                    # Large point reward - trigger HAPPY state
                    trigger = EmotionalTrigger.ACHIEVEMENT_UNLOCKED  
                    context = {"source": "major_achievement", "points": points}
                elif source == "ReactionAddedEvent":
                    # User reacted to content - trigger HAPPY or PLAYFUL
                    trigger = EmotionalTrigger.POSITIVE_INTERACTION
                    context = {"source": "channel_interaction", "engagement_type": "reaction"}
                else:
                    # General positive interaction
                    trigger = EmotionalTrigger.POSITIVE_INTERACTION
                    context = {"source": source, "points": points}
                
                await self.emotional_service.trigger_state_change(
                    user_id=user_id,
                    trigger=trigger,
                    context=context
                )
                
            except Exception as e:
                logger.error(f"Failed to trigger emotional state change for points award: {e}")
        
        # Send contextual narrative response if fragment was queued
        if user_id in self.narrative_service.story_fragments_to_send:
            try:
                fragment_message = (
                    f"✨ *Diana sonríe al verte tan activo...*\n\n"
                    f"'Me encanta verte participando así. Cada acción tuya desbloquea "
                    f"nuevas partes de mi historia... y me permite conocerte mejor.'\n\n"
                    f"📜 Tienes un nuevo fragmento esperándote. Usa /fragmento para verlo."
                )
                
                # Apply emotional modification
                if self.emotional_service:
                    fragment_message = await self.emotional_service.modify_response(
                        user_id=user_id,
                        original_response=fragment_message,
                        context={"source": "points_awarded", "has_fragment": True}
                    )
                
                await self.bot.send_message(
                    chat_id=user_id,
                    text=fragment_message,
                    parse_mode="Markdown"
                )
                
            except Exception as e:
                logger.error(f"Failed to send fragment notification: {e}")
    
    async def handle_mission_completed(self, event: MissionCompletedEvent) -> None:
        """
        Handle mission completed event with emotional context.
        
        Args:
            event: Mission completed event.
        """
        user_id = event.user_id
        mission_id = event.mission_id
        
        logger.info(f"Mission completed by user {user_id}: {mission_id}")
        
        # Update interaction history
        if user_id not in self.user_interaction_history:
            self.user_interaction_history[user_id] = []
        
        self.user_interaction_history[user_id].append({
            "event": "mission_completed",
            "mission_id": mission_id,
            "timestamp": datetime.now().isoformat()
        })
        
        # Trigger strong positive emotional state
        if self.emotional_service:
            try:
                await self.emotional_service.trigger_state_change(
                    user_id=user_id,
                    trigger=EmotionalTrigger.ACHIEVEMENT_UNLOCKED,
                    context={
                        "source": "mission_completed",
                        "mission_id": mission_id,
                        "intensity": "high"
                    }
                )
                
            except Exception as e:
                logger.error(f"Failed to trigger emotional state for mission completion: {e}")
        
        # Send emotionally-aware congratulations message
        try:
            congrats_message = (
                f"🎉 *¡Increíble logro!*\n\n"
                f"Has completado una misión importante, y eso me hace muy feliz. "
                f"Tu dedicación no pasa desapercibida...\n\n"
                f"Como recompensa, podrías haber desbloqueado nuevas partes de mi historia. "
                f"¿Por qué no revisas si tienes fragmentos nuevos?"
            )
            
            # Apply emotional modification
            if self.emotional_service:
                congrats_message = await self.emotional_service.modify_response(
                    user_id=user_id,
                    original_response=congrats_message,
                    context={"source": "mission_completed", "celebration": True}
                )
            
            await self.bot.send_message(
                chat_id=user_id,
                text=congrats_message,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Failed to send mission completion message: {e}")
    
    async def handle_level_up(self, event: LevelUpEvent) -> None:
        """
        Handle level up event with emotional celebration.
        
        Args:
            event: Level up event.
        """
        user_id = event.user_id
        new_level = event.new_level
        
        logger.info(f"User {user_id} leveled up to level {new_level}")
        
        # Update interaction history
        if user_id not in self.user_interaction_history:
            self.user_interaction_history[user_id] = []
        
        self.user_interaction_history[user_id].append({
            "event": "level_up",
            "new_level": new_level,
            "timestamp": datetime.now().isoformat()
        })
        
        # Trigger very positive emotional state
        if self.emotional_service:
            try:
                await self.emotional_service.trigger_state_change(
                    user_id=user_id,
                    trigger=EmotionalTrigger.ACHIEVEMENT_UNLOCKED,
                    context={
                        "source": "level_up",
                        "new_level": new_level,
                        "intensity": "very_high"
                    }
                )
                
            except Exception as e:
                logger.error(f"Failed to trigger emotional state for level up: {e}")
        
        # Send special level up message with emotional context
        try:
            level_message = (
                f"🌟 *¡NIVEL {new_level} ALCANZADO!* 🌟\n\n"
                f"Estoy genuinamente impresionada por tu progreso. "
                f"Cada nivel que alcanzas demuestra tu dedicación a nuestra historia juntos.\n\n"
                f"Con este nuevo nivel, se han desbloqueado secretos más profundos sobre mí. "
                f"¿Estás listo para descubrir más?"
            )
            
            # Apply emotional modification
            if self.emotional_service:
                level_message = await self.emotional_service.modify_response(
                    user_id=user_id,
                    original_response=level_message,
                    context={"source": "level_up", "celebration": True, "level": new_level}
                )
            
            await self.bot.send_message(
                chat_id=user_id,
                text=level_message,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Failed to send level up message: {e}")
    
    async def handle_narrative_progression(self, event: NarrativeProgressionEvent) -> None:
        """
        Handle narrative progression with emotional context.
        
        Args:
            event: Narrative progression event.
        """
        user_id = event.user_id
        fragment_id = event.fragment_id
        
        logger.info(f"Narrative progression for user {user_id}: {fragment_id}")
        
        # Update interaction history
        if user_id not in self.user_interaction_history:
            self.user_interaction_history[user_id] = []
        
        self.user_interaction_history[user_id].append({
            "event": "narrative_progression",
            "fragment_id": fragment_id,
            "timestamp": datetime.now().isoformat()
        })
        
        # Trigger emotional state based on story progression
        if self.emotional_service:
            try:
                # Different fragments might trigger different emotional states
                if "mystery" in fragment_id.lower():
                    trigger = EmotionalTrigger.CURIOSITY_PIQUED
                elif "romance" in fragment_id.lower() or "intimate" in fragment_id.lower():
                    trigger = EmotionalTrigger.INTIMATE_MOMENT
                else:
                    trigger = EmotionalTrigger.STORY_ENGAGEMENT
                
                await self.emotional_service.trigger_state_change(
                    user_id=user_id,
                    trigger=trigger,
                    context={
                        "source": "narrative_progression",
                        "fragment_id": fragment_id
                    }
                )
                
            except Exception as e:
                logger.error(f"Failed to trigger emotional state for narrative progression: {e}")
    
    async def handle_piece_unlocked(self, event: PieceUnlockedEvent) -> None:
        """
        Handle lore piece unlocked with emotional context.
        
        Args:
            event: Piece unlocked event.
        """
        user_id = event.user_id
        piece_id = event.piece_id
        unlock_method = event.unlock_method
        
        logger.info(f"Lore piece unlocked for user {user_id}: {piece_id} via {unlock_method}")
        
        # Update interaction history
        if user_id not in self.user_interaction_history:
            self.user_interaction_history[user_id] = []
        
        self.user_interaction_history[user_id].append({
            "event": "piece_unlocked",
            "piece_id": piece_id,
            "unlock_method": unlock_method,
            "timestamp": datetime.now().isoformat()
        })
        
        # Trigger mysterious or analytical emotional state
        if self.emotional_service:
            try:
                await self.emotional_service.trigger_state_change(
                    user_id=user_id,
                    trigger=EmotionalTrigger.SECRET_REVEALED,
                    context={
                        "source": "piece_unlocked",
                        "piece_id": piece_id,
                        "unlock_method": unlock_method
                    }
                )
                
            except Exception as e:
                logger.error(f"Failed to trigger emotional state for piece unlock: {e}")
        
        # Send mysterious lore unlock message
        try:
            lore_message = (
                f"🗝️ *Un secreto se revela...*\n\n"
                f"Has desbloqueado una nueva pista sobre mi mundo. "
                f"Cada secreto que descubres nos conecta más profundamente.\n\n"
                f"Revisa tu mochila para ver qué has descubierto... "
                f"algunos secretos cambian todo lo que creías saber sobre mí."
            )
            
            # Apply emotional modification
            if self.emotional_service:
                lore_message = await self.emotional_service.modify_response(
                    user_id=user_id,
                    original_response=lore_message,
                    context={"source": "piece_unlocked", "mysterious": True}
                )
            
            await self.bot.send_message(
                chat_id=user_id,
                text=lore_message,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"Failed to send lore unlock message: {e}")
    
    async def get_user_interaction_summary(self, user_id: int) -> Dict[str, Any]:
        """Get summary of user interactions for emotional analysis."""
        if user_id not in self.user_interaction_history:
            return {"total_interactions": 0, "recent_activity": "low"}
        
        interactions = self.user_interaction_history[user_id]
        recent_interactions = [
            interaction for interaction in interactions
            if (datetime.now() - datetime.fromisoformat(interaction["timestamp"])).total_seconds() < 3600  # Last hour
        ]
        
        return {
            "total_interactions": len(interactions),
            "recent_interactions": len(recent_interactions),
            "recent_activity": "high" if len(recent_interactions) >= 5 else "medium" if len(recent_interactions) >= 2 else "low",
            "last_interaction_types": [interaction["event"] for interaction in interactions[-5:]]  # Last 5
        }


def setup_narrative_listener(bot: Bot, event_bus: IEventBus, narrative_service: NarrativeService, emotional_service: EmotionalService = None) -> NarrativeEventListener:
    """
    Setup the narrative event listener.
    
    Args:
        bot: Bot instance.
        event_bus: Event bus.
        narrative_service: Narrative service.
        emotional_service: Emotional service (optional).
        
    Returns:
        NarrativeEventListener instance.
    """
    listener = NarrativeEventListener(bot, event_bus, narrative_service, emotional_service)
    logger.info("NarrativeEventListener configured")
    return listener