"""
Bot Orchestrator module.

This module implements the Facade pattern to coordinate interactions between 
different services in the bot.
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

from src.core.interfaces.IEventBus import IEventBus
from src.bot.core.containers import ApplicationContainer
from src.core.services.config import CentralConfig
from src.modules.narrative.service import NarrativeService
from src.modules.gamification.service import GamificationService
from src.modules.events import (
    UserMessageEvent,
    ReactionAddedEvent,
    UserStartedBotEvent,
    CommandExecutedEvent
)
from ..services.user import UserService
from ..services.admin import AdminService
from ..services.emotional import EmotionalService

logger = logging.getLogger(__name__)

class BotOrchestrator:
    """Facade that coordinates the different services of the bot."""

    def __init__(self, container: ApplicationContainer):
        # Core services
        self._event_bus = container.core.event_bus()
        self._config = container.core.central_config()
        
        # Application services
        self._narrative_service = container.services.narrative_service()
        self._gamification_service = container.services.gamification_service()
        self._user_service = container.services.user_service()
        self._admin_service = container.services.admin_service()
        self._emotional_service = container.services.emotional_service()
        
        logger.info("Bot Orchestrator initialized with all services")

    async def handle_user_message(self, user_id: int, message_text: str, username: str = None) -> Dict[str, Any]:
        """
        Processes a user message and coordinates actions across services.
        
        Args:
            user_id: The ID of the user sending the message.
            message_text: The text content of the message.
            username: Optional username of the user.
            
        Returns:
            A response object containing the response text and additional data.
        """
        logger.debug(f"Processing message from user {user_id}: {message_text[:20]}...")
        
        # 1. Get or create user profile
        user_profile = await self._user_service.get_or_create_user(user_id, username)
        
        # 2. Process message through emotional system
        emotional_context = await self._emotional_service.process_message(
            user_id, 
            message_text, 
            user_profile
        )
        
        # 3. Publish user message event
        await self._event_bus.publish(UserMessageEvent(
            user_id=user_id,
            message=message_text,
            timestamp=datetime.now().isoformat()
        ))
        
        # 4. Update engagement in gamification system
        await self._gamification_service.update_engagement(user_id)
        
        # 5. Record interaction in narrative system
        await self._narrative_service.record_interaction(user_id, message_text)
        
        # 6. Generate response based on emotional context and message
        response_text = await self._generate_response(
            user_id, 
            message_text, 
            user_profile,
            emotional_context
        )
        
        # 7. Prepare complete response object
        response = {
            "text": response_text,
            "user_id": user_id,
            "emotional_state": emotional_context.get("current_state", "Neutral"),
            "timestamp": datetime.now().isoformat(),
            "points": await self._gamification_service.get_points(user_id),
        }
        
        # 8. Check if narrative fragment should be sent
        if user_id in self._narrative_service.story_fragments_to_send:
            fragment_key = self._narrative_service.story_fragments_to_send[user_id]
            response["narrative_fragment"] = await self._narrative_service.get_user_fragment(user_id)
            # Remove from queue after sending
            self._narrative_service.story_fragments_to_send.pop(user_id, None)
            
        return response
        
    async def handle_command(self, user_id: int, command: str, args: List[str] = None) -> Dict[str, Any]:
        """
        Handles a bot command and coordinates appropriate services.
        
        Args:
            user_id: The ID of the user executing the command.
            command: The command name (without the / prefix).
            args: Optional list of command arguments.
            
        Returns:
            A response object containing the response text and additional data.
        """
        logger.debug(f"Processing command from user {user_id}: /{command}")
        args = args or []
        
        # 1. Get user profile
        user_profile = await self._user_service.get_or_create_user(user_id)
        
        # 2. Publish command event
        await self._event_bus.publish(CommandExecutedEvent(
            user_id=user_id,
            command=command,
            args=args,
            timestamp=datetime.now().isoformat()
        ))
        
        # 3. Handle specific commands
        response_data = {}
        
        if command == "start":
            # Handle start command
            await self._event_bus.publish(UserStartedBotEvent(
                user_id=user_id,
                username=user_profile.get("username", "unknown")
            ))
            response_text = "¡Bienvenido a Diana Bot! 🌙"
            
            # Send first narrative fragment
            response_data["narrative_fragment"] = await self._narrative_service.get_user_fragment(user_id)
            
        elif command == "profile":
            # Handle profile command
            points_data = await self._gamification_service.get_user_points(user_id)
            response_text = f"Perfil de usuario:\n" \
                           f"Nivel: {user_profile.get('level', 1)}\n" \
                           f"Besitos: {points_data.get('current_points', 0)}\n"
            response_data["profile_data"] = points_data
            
        elif command == "mochila":
            # Handle backpack command to show narrative items
            lore_pieces = await self._narrative_service.get_user_lore_pieces(user_id)
            response_text = f"Tu mochila contiene {len(lore_pieces)} pistas narrativas."
            response_data["lore_pieces"] = lore_pieces
            
        elif command == "misiones":
            # Handle missions command
            missions = await self._gamification_service.get_user_missions(user_id)
            response_text = f"Tienes {len(missions.get('in_progress', []))} misiones en progreso."
            response_data["missions"] = missions
            
        else:
            # Unknown command
            response_text = f"Comando desconocido: /{command}"
        
        # 4. Prepare response
        response = {
            "text": response_text,
            "user_id": user_id,
            "command": command,
            "timestamp": datetime.now().isoformat(),
            **response_data
        }
        
        return response
        
    async def handle_reaction(self, user_id: int, message_id: int, reaction_type: str) -> Dict[str, Any]:
        """
        Handles a user reaction to a message.
        
        Args:
            user_id: The ID of the user reacting.
            message_id: The ID of the message being reacted to.
            reaction_type: The type of reaction.
            
        Returns:
            A response object with the result of the reaction processing.
        """
        logger.debug(f"Processing reaction from user {user_id} to message {message_id}: {reaction_type}")
        
        # 1. Determine points to award based on reaction type
        points_map = {
            "like": 1,
            "love": 2,
            "wow": 3,
            "kiss": 5
        }
        
        points = points_map.get(reaction_type, 1)
        
        # 2. Publish reaction event
        await self._event_bus.publish(ReactionAddedEvent(
            user_id=user_id,
            message_id=message_id,
            points_to_award=points
        ))
        
        # 3. Get user profile
        user_profile = await self._user_service.get_or_create_user(user_id)
        
        # 4. Update emotional state based on reaction
        emotional_context = await self._emotional_service.process_reaction(
            user_id, 
            reaction_type, 
            user_profile
        )
        
        # 5. Prepare response
        response = {
            "success": True,
            "user_id": user_id,
            "message_id": message_id,
            "reaction": reaction_type,
            "points_awarded": points,
            "emotional_response": emotional_context.get("response", None),
            "timestamp": datetime.now().isoformat()
        }
        
        return response
        
    async def handle_narrative_choice(self, user_id: int, choice_id: int) -> Dict[str, Any]:
        """
        Handles a user's narrative choice.
        
        Args:
            user_id: The ID of the user making the choice.
            choice_id: The ID of the choice made.
            
        Returns:
            A response object with the next narrative fragment.
        """
        logger.debug(f"Processing narrative choice from user {user_id}: choice_id={choice_id}")
        
        # 1. Make the narrative choice
        success = await self._narrative_service.make_narrative_choice(user_id, choice_id)
        
        if not success:
            return {
                "success": False,
                "user_id": user_id,
                "error": "Invalid choice or narrative state"
            }
        
        # 2. Get the new narrative fragment
        fragment = await self._narrative_service.get_user_fragment(user_id)
        
        # 3. Update emotional state based on narrative progression
        await self._emotional_service.process_narrative_progression(user_id, fragment)
        
        # 4. Award points for progression
        points = self._config.get("narrative.progression_points", 2)
        await self._gamification_service.award_points_for_narrative(user_id, points)
        
        # 5. Prepare response
        response = {
            "success": True,
            "user_id": user_id,
            "narrative_fragment": fragment,
            "points_awarded": points,
            "timestamp": datetime.now().isoformat()
        }
        
        return response
    
    async def _generate_response(self, user_id: int, message: str, user_profile: Dict[str, Any], 
                               emotional_context: Dict[str, Any]) -> str:
        """
        Generates a response based on the user's message and context.
        
        In a full implementation, this would use an AI service or template system.
        For now, it returns a simple response based on emotional state.
        
        Args:
            user_id: The ID of the user.
            message: The user's message.
            user_profile: The user's profile data.
            emotional_context: The emotional context data.
            
        Returns:
            A response string.
        """
        # In a real implementation, this would call a response generation service
        # For now, use a simple response based on emotional state
        state = emotional_context.get("current_state", "Neutral")
        
        # Simple response templates based on emotional state
        templates = {
            "Enigmática": [
                "Hmm, interesante perspectiva...",
                "¿Y qué te hace pensar eso?",
                "Hay más de lo que parece en tus palabras."
            ],
            "Vulnerable": [
                "Me haces sentir extrañamente cómoda contigo.",
                "No suelo compartir esto con cualquiera...",
                "Hay algo en ti que me hace bajar la guardia."
            ],
            "Provocadora": [
                "¿Siempre eres así de directo?",
                "Me gusta cómo piensas...",
                "Eso es bastante atrevido, ¿no crees?"
            ],
            "Analítica": [
                "Analizando lo que dices, creo que...",
                "Desde una perspectiva lógica, consideraría que...",
                "Interesante punto de vista. He observado que..."
            ],
            "Silenciosa": [
                "...",
                "A veces el silencio dice más que las palabras.",
                "[Te mira en silencio, pensativa]"
            ],
            "Neutral": [
                "Entiendo lo que dices.",
                "Interesante punto de vista.",
                "Cuéntame más sobre eso."
            ]
        }
        
        import random
        responses = templates.get(state, templates["Neutral"])
        return random.choice(responses)
