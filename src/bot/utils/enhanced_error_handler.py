"""
🎭 ENHANCED ERROR HANDLER FOR DIANA BOT
======================================

Sophisticated error handling system that provides:
- User-friendly error messages with Diana's personality
- Automatic error recovery suggestions
- Graceful fallback options
- Error analytics and learning
- Context-aware error responses

This system transforms technical errors into opportunities for
better user engagement and experience improvement.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable, Tuple
from dataclasses import dataclass
from enum import Enum
import traceback

from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError, TelegramRetryAfter
import structlog

class ErrorCategory(Enum):
    """Categories of errors for different handling approaches"""
    TELEGRAM_API = "telegram_api"
    SERVICE_UNAVAILABLE = "service_unavailable"
    USER_INPUT = "user_input"
    PERMISSION_DENIED = "permission_denied"
    RATE_LIMIT = "rate_limit"
    NETWORK_ERROR = "network_error"
    UNKNOWN = "unknown"

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"          # Minor issues, user can continue normally
    MEDIUM = "medium"    # Moderate issues, user experience affected
    HIGH = "high"        # Significant issues, major features unavailable
    CRITICAL = "critical"  # Bot functionality severely impacted

@dataclass
class ErrorContext:
    """Context information about the error"""
    user_id: int
    error_category: ErrorCategory
    error_severity: ErrorSeverity
    original_error: Exception
    user_action: str  # What the user was trying to do
    timestamp: datetime
    recovery_attempts: int
    context_data: Dict[str, Any]

class DianaErrorHandler:
    """
    🌟 Advanced Error Handler with Diana's Personality
    
    Transforms errors into opportunities for better user experience
    by providing contextual, helpful responses that maintain Diana's
    elegant and supportive personality throughout error recovery.
    """
    
    def __init__(self, services: Dict[str, Any]):
        self.services = services
        self.logger = structlog.get_logger()
        
        # Error tracking and analytics
        self.error_history: Dict[int, List[ErrorContext]] = {}
        self.recovery_success_rate: Dict[str, float] = {}
        
        # Diana's error response patterns
        self.diana_error_responses = {
            ErrorCategory.SERVICE_UNAVAILABLE: {
                ErrorSeverity.LOW: {
                    "message": "🎭 <b>Diana suspira suavemente</b>\n\n<i>Parece que uno de mis servicios está descansando por un momento...</i>\n\n✨ <b>Lucien sugiere:</b> Intentemos de nuevo en unos segundos, mi querido.",
                    "recovery_options": ["🔄 Intentar de Nuevo", "🏠 Regresar al Inicio", "❓ Obtener Ayuda"]
                },
                ErrorSeverity.MEDIUM: {
                    "message": "🎭 <b>Diana frunce el ceño elegantemente</b>\n\n<i>Algo no está funcionando como debería en mi mundo digital...</i>\n\n🎩 <b>Lucien informa:</b> Estamos trabajando para resolver esto. Por favor, ten paciencia.",
                    "recovery_options": ["🏠 Ir al Menú Principal", "🔄 Reintentar", "📞 Contactar Soporte"]
                },
                ErrorSeverity.HIGH: {
                    "message": "🎭 <b>Diana se disculpa con gracia</b>\n\n<i>Me duele informarte que algunos de mis servicios principales no están respondiendo...</i>\n\n💫 <b>Diana promete:</b> Mis técnicos están trabajando para restaurar la magia. Regresa pronto.",
                    "recovery_options": ["🏠 Menú Básico", "📞 Soporte Inmediato", "⏰ Notificarme Cuando Esté Listo"]
                }
            },
            ErrorCategory.TELEGRAM_API: {
                ErrorSeverity.LOW: {
                    "message": "🎭 <b>Diana nota una pequeña interferencia</b>\n\n<i>Telegram parece estar procesando nuestras comunicaciones más lentamente...</i>\n\n✨ No te preocupes, esto es temporal.",
                    "recovery_options": ["🔄 Intentar Nuevamente", "⏳ Esperar un Momento"]
                },
                ErrorSeverity.MEDIUM: {
                    "message": "🎭 <b>Diana detecta complicaciones técnicas</b>\n\n<i>Telegram está experimentando algunas dificultades que afectan nuestras conversaciones...</i>\n\n🎩 <b>Lucien aconseja:</b> Tengamos paciencia mientras se resuelve.",
                    "recovery_options": ["🔄 Reintentar", "🏠 Menú Simplificado", "📞 Soporte"]
                }
            },
            ErrorCategory.USER_INPUT: {
                ErrorSeverity.LOW: {
                    "message": "🎭 <b>Diana sonríe comprensiva</b>\n\n<i>Creo que hubo un pequeño malentendido en lo que intentaste hacer...</i>\n\n💡 <b>Consejo amable:</b> Intentemos de nuevo con una aproximación diferente.",
                    "recovery_options": ["🔄 Intentar de Nuevo", "❓ Obtener Ayuda", "🏠 Menú Principal"]
                }
            },
            ErrorCategory.PERMISSION_DENIED: {
                ErrorSeverity.MEDIUM: {
                    "message": "🎭 <b>Diana explica con delicadeza</b>\n\n<i>Esta área está reservada para ciertos niveles de acceso...</i>\n\n💎 <b>Diana sugiere:</b> Quizás es momento de considerar un nivel de membresía diferente.",
                    "recovery_options": ["💎 Explorar VIP", "🏠 Regresar", "📞 Consultar Opciones"]
                }
            },
            ErrorCategory.RATE_LIMIT: {
                ErrorSeverity.MEDIUM: {
                    "message": "🎭 <b>Diana pide paciencia elegantemente</b>\n\n<i>Has sido muy activo explorando mi mundo... Necesitamos descansar un momento para que puedas continuar disfrutando.</i>\n\n⏰ <b>Tiempo de espera:</b> Solo unos minutos más.",
                    "recovery_options": ["⏳ Esperar", "🎭 Leer Sobre Diana", "📖 Ver Mi Historia"]
                }
            }
        }
        
    async def handle_error(self, 
                          error: Exception, 
                          user_id: int,
                          user_action: str,
                          context_data: Dict[str, Any] = None,
                          event = None) -> Tuple[str, InlineKeyboardMarkup]:
        """
        Main error handling entry point
        Returns user-friendly message and recovery keyboard
        """
        
        # Categorize and analyze the error
        error_category = self._categorize_error(error)
        error_severity = self._determine_severity(error, error_category)
        
        # Create error context
        error_context = ErrorContext(
            user_id=user_id,
            error_category=error_category,
            error_severity=error_severity,
            original_error=error,
            user_action=user_action,
            timestamp=datetime.now(),
            recovery_attempts=0,
            context_data=context_data or {}
        )
        
        # Track error for analytics
        await self._track_error(error_context)
        
        # Log error with context
        self.logger.error("Diana error handler processing error",
                         user_id=user_id,
                         error_category=error_category.value,
                         error_severity=error_severity.value,
                         user_action=user_action,
                         error_message=str(error))
        
        # Generate user-friendly response
        message, keyboard = await self._generate_error_response(error_context)
        
        return message, keyboard
    
    def _categorize_error(self, error: Exception) -> ErrorCategory:
        """Categorize error for appropriate handling"""
        
        if isinstance(error, (TelegramBadRequest, TelegramForbiddenError)):
            return ErrorCategory.TELEGRAM_API
        elif isinstance(error, TelegramRetryAfter):
            return ErrorCategory.RATE_LIMIT
        elif isinstance(error, (ConnectionError, TimeoutError)):
            return ErrorCategory.NETWORK_ERROR
        elif "service" in str(error).lower() and "unavailable" in str(error).lower():
            return ErrorCategory.SERVICE_UNAVAILABLE
        elif "permission" in str(error).lower() or "forbidden" in str(error).lower():
            return ErrorCategory.PERMISSION_DENIED
        elif "invalid" in str(error).lower() or "bad request" in str(error).lower():
            return ErrorCategory.USER_INPUT
        else:
            return ErrorCategory.UNKNOWN
    
    def _determine_severity(self, error: Exception, category: ErrorCategory) -> ErrorSeverity:
        """Determine error severity based on error type and impact"""
        
        # Critical errors that break core functionality
        if isinstance(error, (TelegramForbiddenError, ConnectionError)):
            return ErrorSeverity.CRITICAL
        
        # High severity for major service disruptions
        if category == ErrorCategory.SERVICE_UNAVAILABLE and "gamification" in str(error).lower():
            return ErrorSeverity.HIGH
        
        # Medium severity for user experience disruptions
        if category in [ErrorCategory.TELEGRAM_API, ErrorCategory.RATE_LIMIT, ErrorCategory.PERMISSION_DENIED]:
            return ErrorSeverity.MEDIUM
        
        # Low severity for minor issues
        return ErrorSeverity.LOW
    
    async def _generate_error_response(self, error_context: ErrorContext) -> Tuple[str, InlineKeyboardMarkup]:
        """Generate Diana-style error response with recovery options"""
        
        category = error_context.error_category
        severity = error_context.error_severity
        
        # Get Diana's response for this error type
        response_config = self.diana_error_responses.get(category, {}).get(severity)
        
        if not response_config:
            # Fallback to generic Diana error response
            response_config = {
                "message": "🎭 <b>Diana se disculpa sinceramente</b>\n\n<i>Ha ocurrido algo inesperado en nuestro encuentro...</i>\n\n💫 <b>Diana promete:</b> Haremos que esto funcione, mi querido.",
                "recovery_options": ["🔄 Intentar de Nuevo", "🏠 Regresar al Inicio", "📞 Obtener Ayuda"]
            }
        
        # Customize message based on user context
        message = await self._personalize_error_message(response_config["message"], error_context)
        
        # Create recovery keyboard
        keyboard = self._create_recovery_keyboard(response_config["recovery_options"], error_context)
        
        return message, keyboard
    
    async def _personalize_error_message(self, base_message: str, error_context: ErrorContext) -> str:
        """Personalize error message based on user context"""
        
        # Add specific error context if helpful
        personalized_message = base_message
        
        # Add retry information for rate limits
        if error_context.error_category == ErrorCategory.RATE_LIMIT:
            if isinstance(error_context.original_error, TelegramRetryAfter):
                retry_after = error_context.original_error.retry_after
                personalized_message += f"\n\n⏰ <b>Tiempo de espera:</b> {retry_after} segundos"
        
        # Add service-specific information
        if error_context.error_category == ErrorCategory.SERVICE_UNAVAILABLE:
            if error_context.context_data:
                service_name = error_context.context_data.get('service_name', 'servicio')
                personalized_message += f"\n\n🔧 <b>Servicio afectado:</b> {service_name}"
        
        # Add encouragement for frequent error users
        if await self._is_frequent_error_user(error_context.user_id):
            personalized_message += "\n\n🌟 <b>Diana nota:</b> <i>Has tenido varios inconvenientes. Por favor, contacta soporte para ayuda personalizada.</i>"
        
        return personalized_message
    
    def _create_recovery_keyboard(self, recovery_options: List[str], error_context: ErrorContext) -> InlineKeyboardMarkup:
        """Create recovery action keyboard"""
        
        buttons = []
        
        for option in recovery_options:
            if option == "🔄 Intentar de Nuevo" or option == "🔄 Reintentar":
                callback_data = f"diana_error:retry:{error_context.user_action}"
            elif option == "🏠 Regresar al Inicio" or option == "🏠 Menú Principal":
                callback_data = "diana_user:main"
            elif option == "❓ Obtener Ayuda":
                callback_data = "diana_user:help"
            elif option == "📞 Contactar Soporte" or option == "📞 Soporte":
                callback_data = "diana_error:contact_support"
            elif option == "💎 Explorar VIP":
                callback_data = "diana_user:section:vip_info"
            elif option == "⏳ Esperar":
                callback_data = "diana_error:wait"
            else:
                # Generic fallback
                callback_data = "diana_user:main"
            
            buttons.append([InlineKeyboardButton(text=option, callback_data=callback_data)])
        
        # Always add a direct way back to main menu
        if not any("🏠" in option for option in recovery_options):
            buttons.append([InlineKeyboardButton(text="🏠 Mi Mundo", callback_data="diana_user:main")])
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    async def _track_error(self, error_context: ErrorContext):
        """Track error for analytics and improvement"""
        
        user_id = error_context.user_id
        
        if user_id not in self.error_history:
            self.error_history[user_id] = []
        
        self.error_history[user_id].append(error_context)
        
        # Keep only last 50 errors per user
        if len(self.error_history[user_id]) > 50:
            self.error_history[user_id] = self.error_history[user_id][-50:]
        
        # Log aggregated error metrics
        await self._update_error_metrics(error_context)
    
    async def _update_error_metrics(self, error_context: ErrorContext):
        """Update error metrics for system health monitoring"""
        
        error_key = f"{error_context.error_category.value}_{error_context.error_severity.value}"
        
        # Simple metrics tracking - could be enhanced with proper analytics service
        self.logger.info("Error metrics update", 
                        error_key=error_key,
                        user_id=error_context.user_id,
                        timestamp=error_context.timestamp)
    
    async def _is_frequent_error_user(self, user_id: int) -> bool:
        """Check if user is experiencing frequent errors"""
        
        if user_id not in self.error_history:
            return False
        
        recent_errors = [
            error for error in self.error_history[user_id]
            if datetime.now() - error.timestamp < timedelta(hours=1)
        ]
        
        return len(recent_errors) >= 3
    
    # === RECOVERY HANDLERS ===
    
    async def handle_retry_action(self, callback: CallbackQuery, original_action: str):
        """Handle retry actions from error recovery"""
        
        user_id = callback.from_user.id
        
        try:
            # Increment recovery attempt count
            if user_id in self.error_history and self.error_history[user_id]:
                self.error_history[user_id][-1].recovery_attempts += 1
            
            # Log recovery attempt
            self.logger.info("Error recovery retry attempted",
                           user_id=user_id,
                           original_action=original_action)
            
            await callback.answer("🔄 Intentando de nuevo...")
            
            # The actual retry logic would be handled by the original handler
            # This is just for tracking and user feedback
            
        except Exception as e:
            self.logger.error("Error during recovery retry", error=str(e))
            await callback.answer("❌ Error durante recuperación")
    
    async def handle_support_contact(self, callback: CallbackQuery):
        """Handle support contact from error recovery"""
        
        support_message = """🎭 <b>Diana conecta con soporte</b>

<i>Lucien está preparando una conexión directa con nuestro equipo de soporte técnico...</i>

📞 <b>Opciones de contacto:</b>
• Mensaje directo al equipo técnico
• Chat en vivo con especialista
• Email de soporte prioritario

💫 <b>Diana asegura:</b> <i>Recibirás ayuda personalizada muy pronto.</i>"""

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💬 Chat en Vivo", callback_data="diana_support:live_chat")],
            [InlineKeyboardButton(text="📧 Enviar Email", callback_data="diana_support:email")],
            [InlineKeyboardButton(text="🏠 Regresar", callback_data="diana_user:main")]
        ])
        
        await callback.message.edit_text(support_message, reply_markup=keyboard, parse_mode="HTML")
        await callback.answer()
    
    async def get_error_analytics(self, user_id: int = None) -> Dict[str, Any]:
        """Get error analytics for system monitoring"""
        
        if user_id:
            user_errors = self.error_history.get(user_id, [])
            is_frequent = await self._is_frequent_error_user(user_id)
            return {
                'total_errors': len(user_errors),
                'recent_errors': len([e for e in user_errors if datetime.now() - e.timestamp < timedelta(hours=24)]),
                'most_common_category': self._get_most_common_error_category(user_errors),
                'needs_attention': is_frequent
            }
        else:
            # Global analytics
            all_errors = []
            for errors in self.error_history.values():
                all_errors.extend(errors)
            
            return {
                'total_errors': len(all_errors),
                'affected_users': len(self.error_history),
                'most_common_category': self._get_most_common_error_category(all_errors),
                'critical_error_count': len([e for e in all_errors if e.error_severity == ErrorSeverity.CRITICAL])
            }
    
    def _get_most_common_error_category(self, errors: List[ErrorContext]) -> str:
        """Get most common error category from error list"""
        
        if not errors:
            return "none"
        
        category_counts = {}
        for error in errors:
            category = error.error_category.value
            category_counts[category] = category_counts.get(category, 0) + 1
        
        return max(category_counts, key=category_counts.get) if category_counts else "none"

def create_diana_error_handler(services: Dict[str, Any]) -> DianaErrorHandler:
    """Factory function to create Diana Error Handler"""
    return DianaErrorHandler(services)