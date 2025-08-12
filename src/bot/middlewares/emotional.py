"""Enhanced emotional middleware for Diana's personality system."""

from typing import Any, Awaitable, Callable, Dict
import structlog
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject

logger = structlog.get_logger()

class DianaEmotionalMiddleware(BaseMiddleware):
    """
    Advanced emotional middleware that processes Diana's emotional states
    and modifies responses based on her current mood and user interactions.
    """
    
    def __init__(self, emotional_service=None):
        """
        Initialize the emotional middleware.
        
        Args:
            emotional_service: Emotional service instance.
        """
        self.emotional_service = emotional_service
        self.response_cache: Dict[int, Dict[str, Any]] = {}  # Cache emotional contexts
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Execute the emotional processing middleware."""
        # Only process messages and callback queries
        if not isinstance(event, (Message, CallbackQuery)):
            return await handler(event, data)
        
        # Get user ID
        user_id = None
        message_text = None
        
        if isinstance(event, Message):
            user_id = event.from_user.id if event.from_user else None
            message_text = event.text or event.caption or ""
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id if event.from_user else None
            message_text = event.data or ""
        
        # Skip if no user ID or emotional service not available
        if not user_id or not self.emotional_service:
            return await handler(event, data)
        
        try:
            # Analyze user interaction for emotional context
            emotional_trigger = await self.emotional_service.analyze_user_interaction(
                user_id=user_id,
                message_text=message_text,
                context={
                    "message_type": "message" if isinstance(event, Message) else "callback",
                    "has_text": bool(message_text),
                    "is_command": message_text.startswith("/") if message_text else False
                }
            )
            
            # Get current emotional modifiers
            modifiers = await self.emotional_service.get_response_modifiers(user_id)
            
            # Create emotional context for handlers
            emotional_context = {
                "modifiers": modifiers,
                "trigger": emotional_trigger,
                "user_id": user_id,
                "message_text": message_text
            }
            
            # Add to handler data
            data["emotional_context"] = emotional_context
            data["emotional_service"] = self.emotional_service
            
            # Cache the context for response modification
            self.response_cache[user_id] = emotional_context
            
            # Trigger emotional state change if needed
            if emotional_trigger:
                await self.emotional_service.trigger_state_change(
                    user_id=user_id, 
                    trigger=emotional_trigger,
                    context={
                        "source": "middleware_analysis",
                        "message_type": "message" if isinstance(event, Message) else "callback"
                    }
                )
            
            logger.debug(f"Emotional context prepared for user {user_id}", 
                        current_modifiers=modifiers, 
                        trigger=emotional_trigger)
            
        except Exception as e:
            logger.error(f"Error in emotional middleware for user {user_id}: {e}")
            # Continue without emotional processing if there's an error
        
        # Execute the handler with emotional context
        return await handler(event, data)
    
    async def modify_outgoing_response(self, user_id: int, response_text: str, context: Dict[str, Any] = None) -> str:
        """
        Modify an outgoing response based on the user's emotional state.
        
        Args:
            user_id: User ID.
            response_text: Original response text.
            context: Additional context for modification.
            
        Returns:
            Modified response text.
        """
        if not self.emotional_service or user_id not in self.response_cache:
            return response_text
        
        try:
            # Use cached emotional context
            emotional_context = self.response_cache[user_id]
            
            # Apply emotional modifications
            modified_response = await self.emotional_service.modify_response(
                user_id=user_id,
                original_response=response_text,
                context={**emotional_context, **(context or {})}
            )
            
            logger.debug(f"Response modified for user {user_id}", 
                        original_length=len(response_text),
                        modified_length=len(modified_response))
            
            return modified_response
            
        except Exception as e:
            logger.error(f"Error modifying response for user {user_id}: {e}")
            return response_text
    
    def get_user_emotional_context(self, user_id: int) -> Dict[str, Any]:
        """
        Get the current emotional context for a user.
        
        Args:
            user_id: User ID.
            
        Returns:
            Emotional context dictionary.
        """
        return self.response_cache.get(user_id, {})
    
    def clear_user_cache(self, user_id: int) -> None:
        """
        Clear emotional cache for a specific user.
        
        Args:
            user_id: User ID.
        """
        if user_id in self.response_cache:
            del self.response_cache[user_id]


class EmotionalResponseInterceptor:
    """
    Helper class to intercept and modify outgoing messages
    with emotional context from Diana's personality system.
    """
    
    def __init__(self, middleware: DianaEmotionalMiddleware):
        """Initialize with emotional middleware reference."""
        self.middleware = middleware
    
    async def send_emotionally_aware_message(self, bot, chat_id: int, text: str, **kwargs) -> Any:
        """
        Send a message with emotional modifications applied.
        
        Args:
            bot: Bot instance.
            chat_id: Chat ID (user ID).
            text: Message text.
            **kwargs: Additional arguments for send_message.
            
        Returns:
            Message sending result.
        """
        # Apply emotional modifications
        modified_text = await self.middleware.modify_outgoing_response(
            user_id=chat_id,
            response_text=text,
            context={"outgoing_message": True}
        )
        
        # Send the emotionally-modified message
        return await bot.send_message(chat_id=chat_id, text=modified_text, **kwargs)
    
    async def edit_emotionally_aware_message(self, message, text: str, **kwargs) -> Any:
        """
        Edit a message with emotional modifications applied.
        
        Args:
            message: Message object to edit.
            text: New message text.
            **kwargs: Additional arguments for edit_text.
            
        Returns:
            Message editing result.
        """
        user_id = message.chat.id if message.chat else None
        
        if user_id:
            # Apply emotional modifications
            modified_text = await self.middleware.modify_outgoing_response(
                user_id=user_id,
                response_text=text,
                context={"outgoing_edit": True}
            )
            
            # Edit with emotionally-modified text
            return await message.edit_text(text=modified_text, **kwargs)
        else:
            # Fallback to original text if no user ID
            return await message.edit_text(text=text, **kwargs)