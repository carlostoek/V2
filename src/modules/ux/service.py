"""
Servicio de Experiencia de Usuario (UX)
Maneja onboarding, personalización, y mejoras de experiencia de usuario.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.interfaces.IEventBus import IEventBus
from src.bot.database.engine import get_session
from src.bot.database.models.user import User
from src.bot.database.models.gamification import UserPoints, UserMission, UserAchievement
from src.bot.database.models.narrative import UserNarrativeState

logger = logging.getLogger(__name__)

class UXService:
    """
    Servicio para manejar la experiencia de usuario, onboarding y personalización.
    """

    def __init__(self, event_bus: IEventBus):
        self.event_bus = event_bus
        self.logger = logging.getLogger(__name__)

    async def setup(self):
        """Configura el servicio UX."""
        self.logger.info("UXService configurado exitosamente")

    async def get_user_context(self, user_id: int) -> Dict[str, Any]:
        """
        Obtiene el contexto completo del usuario para personalización.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Diccionario con contexto completo del usuario
        """
        async with get_session() as session:
            try:
                # Obtener información básica del usuario
                user_stmt = select(User).where(User.id == user_id)
                user_result = await session.execute(user_stmt)
                user = user_result.scalar_one_or_none()

                if not user:
                    return self._create_default_context(user_id)

                # Obtener puntos del usuario
                points_stmt = select(UserPoints).where(UserPoints.user_id == user_id)
                points_result = await session.execute(points_stmt)
                points = points_result.scalar_one_or_none()

                # Obtener progreso narrativo
                narrative_stmt = select(UserNarrativeState).where(UserNarrativeState.user_id == user_id)
                narrative_result = await session.execute(narrative_stmt)
                narrative_states = narrative_result.scalars().all()

                # Obtener misiones activas
                missions_stmt = select(UserMission).where(
                    and_(UserMission.user_id == user_id, UserMission.status == 'active')
                )
                missions_result = await session.execute(missions_stmt)
                active_missions = missions_result.scalars().all()

                # Obtener logros
                achievements_stmt = select(UserAchievement).where(UserAchievement.user_id == user_id)
                achievements_result = await session.execute(achievements_stmt)
                achievements = achievements_result.scalars().all()

                # Determinar si es usuario nuevo
                is_new_user = self._is_new_user(user)
                
                # Determinar el nivel de experiencia
                experience_level = self._calculate_experience_level(user, points, achievements)

                return {
                    'user_id': user_id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'is_new_user': is_new_user,
                    'is_returning_user': not is_new_user,
                    'is_vip': user.is_vip,
                    'is_admin': user.is_admin,
                    'level': user.level,
                    'experience_points': user.experience_points,
                    'experience_level': experience_level,
                    'points': points.points if points else 0,
                    'active_missions_count': len(active_missions),
                    'achievements_count': len(achievements),
                    'narrative_progress_count': len(narrative_states),
                    'last_activity': user.last_activity_at,
                    'settings': user.user_settings or {},
                    'created_at': user.created_at
                }

            except Exception as e:
                self.logger.error(f"Error obteniendo contexto de usuario {user_id}: {e}")
                return self._create_default_context(user_id)

    def _create_default_context(self, user_id: int) -> Dict[str, Any]:
        """Crea un contexto por defecto para usuarios no encontrados."""
        return {
            'user_id': user_id,
            'username': None,
            'first_name': 'Usuario',
            'is_new_user': True,
            'is_returning_user': False,
            'is_vip': False,
            'is_admin': False,
            'level': 1,
            'experience_points': 0,
            'experience_level': 'beginner',
            'points': 0,
            'active_missions_count': 0,
            'achievements_count': 0,
            'narrative_progress_count': 0,
            'last_activity': None,
            'settings': {},
            'created_at': datetime.utcnow()
        }

    def _is_new_user(self, user: User) -> bool:
        """Determina si un usuario es nuevo basado en su actividad."""
        if not user.last_activity_at:
            return True
        
        # Usuario nuevo si se creó hace menos de 24 horas Y tiene poca actividad
        time_threshold = datetime.utcnow() - timedelta(hours=24)
        is_recently_created = user.created_at > time_threshold
        has_low_activity = user.messages_count < 5
        
        return is_recently_created and has_low_activity

    def _calculate_experience_level(self, user: User, points: Optional[UserPoints], achievements: List) -> str:
        """Calcula el nivel de experiencia del usuario."""
        total_score = 0
        
        # Puntos de experiencia del usuario
        if user.experience_points:
            total_score += user.experience_points
            
        # Puntos del sistema de gamificación
        if points:
            total_score += points.points // 10  # Convertir puntos a experiencia
            
        # Logros
        total_score += len(achievements) * 50
        
        # Nivel de la cuenta
        total_score += (user.level - 1) * 100

        if total_score < 100:
            return 'beginner'
        elif total_score < 500:
            return 'intermediate'
        elif total_score < 1500:
            return 'advanced'
        else:
            return 'expert'

    async def create_onboarding_flow(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea un flujo de onboarding personalizado basado en el contexto del usuario.
        
        Args:
            user_context: Contexto del usuario obtenido de get_user_context
            
        Returns:
            Flujo de onboarding con pasos y mensajes personalizados
        """
        is_new = user_context['is_new_user']
        is_vip = user_context['is_vip']
        experience_level = user_context['experience_level']
        first_name = user_context['first_name']

        if is_new:
            return self._create_new_user_onboarding(first_name, is_vip)
        else:
            return self._create_returning_user_welcome(user_context)

    def _create_new_user_onboarding(self, first_name: str, is_vip: bool) -> Dict[str, Any]:
        """Crea onboarding para usuarios completamente nuevos."""
        steps = [
            {
                'step': 1,
                'type': 'welcome',
                'title': f'¡Bienvenida {first_name}! 🌟',
                'message': (
                    f'¡Hola {first_name}! Soy Diana, tu compañera en esta aventura interactiva. '
                    'Estoy aquí para guiarte através de un mundo de historias, juegos y '
                    'experiencias únicas. 💖\n\n'
                    '¿Lista para comenzar esta aventura juntas?'
                ),
                'has_tutorial': True,
                'callback_data': 'onboarding:step_1'
            },
            {
                'step': 2,
                'type': 'features_intro',
                'title': '🎮 ¿Qué puedes hacer aquí?',
                'message': (
                    '✨ **Historias Interactivas**: Vive aventuras donde tus decisiones importan\n'
                    '🎯 **Sistema de Gamificación**: Gana puntos, completa misiones y desbloquea recompensas\n'
                    '🎁 **Regalos Diarios**: Recibe recompensas especiales cada día\n'
                    '🛍️ **Tienda Virtual**: Canjea tus puntos por contenido exclusivo\n'
                    '🎒 **Sistema de Mochila**: Colecciona pistas y objetos especiales\n'
                ),
                'callback_data': 'onboarding:step_2'
            },
            {
                'step': 3,
                'type': 'gamification_intro',
                'title': '🏆 Tu Sistema de Progreso',
                'message': (
                    'En Diana Bot, cada acción cuenta para tu progreso:\n\n'
                    '💎 **Puntos (Besitos)**: Los ganas interactuando y completando actividades\n'
                    '🎯 **Misiones**: Desafíos especiales que te dan grandes recompensas\n'
                    '🏅 **Niveles**: Tu experiencia te hace subir de nivel\n'
                    '🎪 **Logros**: Marcas especiales por tus aventuras\n\n'
                    '¡Empezarás con algunos puntos de bienvenida!'
                ),
                'callback_data': 'onboarding:step_3'
            },
            {
                'step': 4,
                'type': 'navigation_tutorial',
                'title': '🧭 Navegando en Diana',
                'message': (
                    'Navegar es súper fácil:\n\n'
                    '📜 **Historia**: Comienza tu aventura narrativa\n'
                    '🏆 **Perfil**: Ve tu progreso y estadísticas\n'
                    '🎮 **Gamificación**: Accede a minijuegos y actividades\n'
                    '🎁 **Regalo Diario**: ¡No olvides reclamarlo cada día!\n'
                    '❓ **Ayuda**: Siempre disponible si te pierdes\n\n'
                    '¡Usa los botones y yo te guiaré!'
                ),
                'callback_data': 'onboarding:step_4'
            },
            {
                'step': 5,
                'type': 'first_reward',
                'title': '🎁 ¡Tu Regalo de Bienvenida!',
                'message': (
                    f'¡{first_name}, es momento de tu primer regalo! 🎉\n\n'
                    'Como nueva aventurera, te doy:\n'
                    '🎊 **100 puntos de bienvenida**\n'
                    '🎯 **Tu primera misión especial**\n'
                    '🔮 **Un objeto mágico para tu mochila**\n\n'
                    '¿Lista para recibir tus regalos?'
                ),
                'callback_data': 'onboarding:claim_welcome_reward'
            }
        ]

        if is_vip:
            steps.insert(4, {
                'step': 4.5,
                'type': 'vip_perks',
                'title': '👑 ¡Eres Usuario VIP!',
                'message': (
                    f'¡Increíble {first_name}! Tienes acceso VIP, lo que significa:\n\n'
                    '💎 **Contenido Exclusivo**: Ramas de historia solo para VIP\n'
                    '🚀 **Recompensas Mejoradas**: Más puntos en todas las actividades\n'
                    '⚡ **Acceso Prioritario**: A nuevas funciones antes que nadie\n'
                    '🎁 **Regalos Especiales**: Recompensas VIP exclusivas\n'
                    '💬 **Soporte Premium**: Atención personalizada\n\n'
                    '¡Disfruta tu experiencia premium!'
                ),
                'callback_data': 'onboarding:vip_intro'
            })

        return {
            'type': 'new_user_onboarding',
            'total_steps': len(steps),
            'current_step': 0,
            'steps': steps,
            'estimated_time': '3-5 minutos',
            'can_skip': False,
            'welcome_reward': {
                'points': 100,
                'special_mission': True,
                'welcome_item': 'crystal_of_beginnings'
            }
        }

    def _create_returning_user_welcome(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Crea bienvenida personalizada para usuarios que regresan."""
        first_name = user_context['first_name']
        level = user_context['level']
        points = user_context['points']
        active_missions = user_context['active_missions_count']
        last_activity = user_context['last_activity']
        is_vip = user_context['is_vip']
        
        # Determinar tiempo desde última actividad
        time_away = self._calculate_time_away(last_activity) if last_activity else None
        
        # Mensaje personalizado basado en progreso
        if user_context['experience_level'] == 'beginner':
            progress_message = '¡Sigues en el inicio de tu aventura! Hay mucho por descubrir.'
        elif user_context['experience_level'] == 'intermediate':
            progress_message = 'Ya tienes experiencia navegando por mis mundos. ¡Impresionante!'
        elif user_context['experience_level'] == 'advanced':
            progress_message = 'Eres toda una veterana en mis aventuras. ¡Me encanta tu dedicación!'
        else:
            progress_message = '¡Eres una experta absoluta! Conoces todos mis secretos.'

        welcome_message = f'¡{first_name}! Me alegra tenerte de vuelta 💖\n\n'
        
        if time_away:
            welcome_message += f'Han pasado {time_away} desde tu última visita. '
        
        welcome_message += f'{progress_message}\n\n'
        
        welcome_message += f'📊 **Tu Estado Actual:**\n'
        welcome_message += f'🏆 Nivel: {level}\n'
        welcome_message += f'💎 Puntos: {points:,}\n'
        
        if active_missions > 0:
            welcome_message += f'🎯 Misiones activas: {active_missions}\n'
            
        if is_vip:
            welcome_message += '👑 Estado: VIP Premium\n'
            
        welcome_message += '\n¿Qué aventura te espera hoy?'

        return {
            'type': 'returning_user_welcome',
            'message': welcome_message,
            'time_away': time_away,
            'has_daily_reward': True,
            'has_notifications': active_missions > 0,
            'quick_actions': self._get_personalized_quick_actions(user_context),
            'recommended_action': self._get_recommended_action(user_context)
        }

    def _calculate_time_away(self, last_activity: datetime) -> str:
        """Calcula tiempo transcurrido desde última actividad en formato amigable."""
        if not last_activity:
            return "mucho tiempo"
            
        now = datetime.utcnow()
        # Asegurar que ambas fechas estén en UTC para la comparación
        if last_activity.tzinfo is not None:
            now = now.replace(tzinfo=last_activity.tzinfo)
            
        delta = now - last_activity
        
        if delta.days > 30:
            months = delta.days // 30
            return f"{months} mes{'es' if months > 1 else ''}"
        elif delta.days > 0:
            return f"{delta.days} día{'s' if delta.days > 1 else ''}"
        elif delta.seconds > 3600:
            hours = delta.seconds // 3600
            return f"{hours} hora{'s' if hours > 1 else ''}"
        else:
            return "unas horas"

    def _get_personalized_quick_actions(self, user_context: Dict[str, Any]) -> List[Dict[str, str]]:
        """Genera acciones rápidas personalizadas basadas en el contexto del usuario."""
        actions = []
        
        # Siempre incluir historia si hay progreso narrativo
        if user_context['narrative_progress_count'] > 0:
            actions.append({
                'text': '📜 Continuar Historia',
                'callback_data': 'main_menu:narrative'
            })
        else:
            actions.append({
                'text': '📜 Comenzar Historia',
                'callback_data': 'main_menu:narrative'
            })
            
        # Regalo diario siempre disponible
        actions.append({
            'text': '🎁 Regalo Diario',
            'callback_data': 'gamification:daily_reward'
        })
        
        # Misiones si hay activas
        if user_context['active_missions_count'] > 0:
            actions.append({
                'text': f'🎯 Misiones ({user_context["active_missions_count"]})',
                'callback_data': 'main_menu:missions'
            })
            
        # Tienda si tiene puntos
        if user_context['points'] >= 50:
            actions.append({
                'text': '🛍️ Tienda',
                'callback_data': 'shop:main'
            })
            
        return actions

    def _get_recommended_action(self, user_context: Dict[str, Any]) -> Dict[str, str]:
        """Determina la acción recomendada basada en el contexto del usuario."""
        # Prioritario: misiones activas
        if user_context['active_missions_count'] > 0:
            return {
                'text': 'Completar misiones pendientes',
                'callback_data': 'main_menu:missions',
                'reason': 'Tienes misiones activas que te darán grandes recompensas'
            }
            
        # Si es usuario intermedio+ sin progreso reciente en historia
        if user_context['experience_level'] in ['intermediate', 'advanced', 'expert']:
            return {
                'text': 'Explorar nuevas ramas de historia',
                'callback_data': 'main_menu:narrative',
                'reason': 'Hay nuevas aventuras esperándote'
            }
            
        # Para principiantes: gamificación
        if user_context['experience_level'] == 'beginner':
            return {
                'text': 'Explorar el sistema de gamificación',
                'callback_data': 'gamification:main',
                'reason': 'Aprende a ganar puntos y desbloquear contenido'
            }
            
        # Default: historia
        return {
            'text': 'Continuar tu historia',
            'callback_data': 'main_menu:narrative',
            'reason': 'Tu aventura personal te está esperando'
        }

    async def track_user_interaction(self, user_id: int, interaction_type: str, context: Dict[str, Any] = None):
        """
        Rastrea las interacciones del usuario para personalización futura.
        
        Args:
            user_id: ID del usuario
            interaction_type: Tipo de interacción (menu_click, command_use, etc.)
            context: Contexto adicional de la interacción
        """
        try:
            async with get_session() as session:
                # Actualizar última actividad
                update_stmt = select(User).where(User.id == user_id)
                result = await session.execute(update_stmt)
                user = result.scalar_one_or_none()
                
                if user:
                    user.last_activity_at = datetime.utcnow()
                    user.messages_count += 1
                    
                    # Actualizar configuraciones del usuario si es necesario
                    if context and 'update_settings' in context:
                        if not user.user_settings:
                            user.user_settings = {}
                        user.user_settings.update(context['update_settings'])
                    
                    await session.commit()
                    
        except Exception as e:
            self.logger.error(f"Error tracking user interaction {user_id}: {e}")

    async def update_user_preferences(self, user_id: int, preferences: Dict[str, Any]) -> bool:
        """
        Actualiza las preferencias del usuario.
        
        Args:
            user_id: ID del usuario
            preferences: Diccionario con nuevas preferencias
            
        Returns:
            True si se actualizó exitosamente
        """
        try:
            async with get_session() as session:
                stmt = select(User).where(User.id == user_id)
                result = await session.execute(stmt)
                user = result.scalar_one_or_none()
                
                if user:
                    if not user.user_settings:
                        user.user_settings = {}
                    
                    user.user_settings.update(preferences)
                    await session.commit()
                    return True
                    
                return False
                
        except Exception as e:
            self.logger.error(f"Error updating user preferences {user_id}: {e}")
            return False

    def create_error_recovery_message(self, error_type: str, user_context: Dict[str, Any] = None) -> str:
        """
        Crea mensajes de error amigables y útiles.
        
        Args:
            error_type: Tipo de error ocurrido
            user_context: Contexto del usuario (opcional)
            
        Returns:
            Mensaje de error amigable con opción de recovery
        """
        user_name = user_context.get('first_name', 'usuario') if user_context else 'usuario'
        
        error_messages = {
            'network_error': (
                f'Ups {user_name}, parece que tengo problemas de conexión. '
                'Dame un momento y vuelve a intentarlo. 💫'
            ),
            'database_error': (
                f'Disculpa {user_name}, estoy organizando algunas cosas en mi mente. '
                'Intenta nuevamente en unos segundos. ⚡'
            ),
            'permission_error': (
                f'{user_name}, no tienes permisos para realizar esta acción. '
                'Si crees que es un error, contacta al administrador. 🔐'
            ),
            'validation_error': (
                f'Oops {user_name}, algo en la información no está bien. '
                'Revisa los datos e inténtalo nuevamente. 📝'
            ),
            'service_unavailable': (
                f'{user_name}, esta función está temporalmente fuera de servicio. '
                'Puedes probar otras aventuras mientras tanto. 🛠️'
            ),
            'generic_error': (
                f'Lo siento {user_name}, algo inesperado ocurrió. '
                'Pero no te preocupes, puedes volver al menú principal y continuar. ✨'
            )
        }
        
        return error_messages.get(error_type, error_messages['generic_error'])