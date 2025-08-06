"""
🎭 DIANA MASTER SYSTEM - Silicon Valley Edition
===============================================

The most advanced bot interface ever created.
Not just a menu - a living, breathing ecosystem.

Architecture: Adaptive Context Engine
Philosophy: Anticipate, Adapt, Amaze
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

import structlog

# Import services for real data integration
from src.modules.gamification.service import GamificationService
from src.modules.narrative.service import NarrativeService
from src.modules.admin.service import AdminService
from src.modules.user.service import UserService
from src.modules.shop.service import ShopService
from src.modules.daily_rewards.service import DailyRewardsService
from src.modules.trivia.service import TriviaService
from src.modules.tariff.service import TariffService

# === HELPER FUNCTIONS ===

async def safe_edit_message(callback: CallbackQuery, text: str, keyboard: InlineKeyboardMarkup = None, parse_mode: str = "Markdown"):
    """Safely edit message handling Telegram's 'message not modified' error"""
    try:
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode=parse_mode)
    except Exception as e:
        if "message is not modified" in str(e).lower():
            await callback.answer("🔄 Actualizado")
        else:
            await callback.answer(f"Error: {str(e)}")
            raise e

# === REVOLUTIONARY CONTEXT ENGINE ===

class UserMoodState(Enum):
    """AI-detected user mood states for adaptive UX"""
    EXPLORER = "explorer"          # Wants to discover new features
    ACHIEVER = "achiever"          # Focused on completing tasks
    COLLECTOR = "collector"        # Loves accumulating rewards/items
    STORYTELLER = "storyteller"    # Engaged with narrative
    SOCIALIZER = "socializer"      # Enjoys community features
    OPTIMIZER = "optimizer"        # Wants efficiency and stats
    NEWCOMER = "newcomer"          # Needs guidance and tutorials

@dataclass
class UserContext:
    """Complete user state for hyper-personalization"""
    user_id: int
    current_mood: UserMoodState
    engagement_pattern: str
    session_duration: int
    last_actions: List[str]
    preferred_features: List[str]
    notification_preferences: Dict[str, bool]
    personalization_score: float
    narrative_progress: float
    gamification_engagement: float


class AdaptiveContextEngine:
    """
    🧠 THE BRAIN OF THE SYSTEM
    
    This engine doesn't just show menus - it crafts experiences.
    Each interaction is analyzed, predicted, and optimized.
    """
    
    def __init__(self, services: Dict[str, Any]):
        self.services = services
        self.logger = structlog.get_logger()
        
        # Initialize service instances for real data access
        self._gamification_service = services.get('gamification')
        self._narrative_service = services.get('narrative')
        self._admin_service = services.get('admin')
        self._user_service = services.get('user')
        self._shop_service = services.get('shop')
        self._daily_rewards_service = services.get('daily_rewards')
        self._trivia_service = services.get('trivia')
        self._tariff_service = services.get('tariff')
        self.user_contexts: Dict[int, UserContext] = {}
        self.interaction_patterns: Dict[int, List[Tuple[str, datetime]]] = {}
        
    async def analyze_user_context(self, user_id: int) -> UserContext:
        """🔍 AI-powered user context analysis"""
        
        # Gather multi-dimensional user data
        try:
            if hasattr(self.services['gamification'], 'get_user_points'):
                user_stats = await self.services['gamification'].get_user_points(user_id)
            else:
            # Get real user data from services
            user_points = 0
            user_level = 1
            narrative_progress = 0.0
            gamification_engagement = 0.0
            
            # Get gamification data
            if self._gamification_service:
                try:
                    points_data = await self._gamification_service.get_user_points(user_id)
                    user_points = points_data.get('current_points', 0)
                    user_level = self._calculate_level_from_points(user_points)
                    
                    # Calculate engagement based on missions and achievements
                    missions = await self._gamification_service.get_user_missions(user_id)
                    achievements = await self._gamification_service.get_user_achievements(user_id)
                    
                    total_missions = len(missions.get('available', [])) + len(missions.get('in_progress', [])) + len(missions.get('completed', []))
                    completed_missions = len(missions.get('completed', []))
                    completed_achievements = len([a for a in achievements if a.get('is_completed', False)])
                    
                    gamification_engagement = min(1.0, (completed_missions + completed_achievements) / max(1, total_missions + 10))
                except Exception as e:
                    self.logger.warning(f"Error getting gamification data: {e}")
            
            # Get narrative progress
            if self._narrative_service:
                try:
                    lore_pieces = await self._narrative_service.get_user_lore_pieces(user_id)
                    narrative_progress = min(1.0, len(lore_pieces) / 10.0)  # Assume 10 total pieces
                except Exception as e:
                    self.logger.warning(f"Error getting narrative data: {e}")
            
            # Detect user mood based on real data
            current_mood = await self._detect_user_mood(user_id, [])
            
            # Calculate engagement pattern
            engagement_pattern = self._analyze_engagement_pattern([])
            
            # Calculate personalization score
            personalization_score = min(1.0, (gamification_engagement + narrative_progress) / 2.0)
            
                user_stats = {'level': 1, 'points': 0, 'engagement_level': 0.5}
        except:
                current_mood=current_mood,
                engagement_pattern=engagement_pattern,
        recent_interactions = self.interaction_patterns.get(user_id, [])
        
        # AI mood detection based on behavior patterns
        detected_mood = await self._detect_user_mood(user_id, recent_interactions)
                personalization_score=personalization_score,
                narrative_progress=narrative_progress,
                gamification_engagement=gamification_engagement
        
        context = UserContext(
            user_id=user_id,
            current_mood=detected_mood,
            engagement_pattern=engagement_pattern,
            session_duration=self._calculate_session_duration(user_id),
            last_actions=self._get_recent_actions(user_id),
            preferred_features=await self._identify_preferred_features(user_id),
            notification_preferences=await self._get_notification_prefs(user_id),
            personalization_score=await self._calculate_personalization_score(user_id),
            narrative_progress=narrative_state.get('progress', 0),
            gamification_engagement=user_stats.get('engagement_level', 0)
        )
        
        self.user_contexts[user_id] = context
        return context
    
    def _calculate_level_from_points(self, points: int) -> int:
        """Calculate user level from points using standard progression."""
        if points < 100:
            return 1
        elif points < 400:
            return 2
        elif points < 900:
            return 3
        elif points < 1600:
            return 4
        elif points < 2500:
            return 5
        else:
            return min(10, 5 + (points - 2500) // 1000)
    
    async def _detect_user_mood(self, user_id: int, interactions: List) -> UserMoodState:
        """🎭 Advanced mood detection algorithm"""
        try:
            # Get real user data to determine mood
            if self._gamification_service:
                points_data = await self._gamification_service.get_user_points(user_id)
                missions = await self._gamification_service.get_user_missions(user_id)
                achievements = await self._gamification_service.get_user_achievements(user_id)
                
                # Analyze patterns
                total_points = points_data.get('current_points', 0)
                completed_missions = len(missions.get('completed', []))
                completed_achievements = len([a for a in achievements if a.get('is_completed', False)])
                
                # Determine mood based on activity patterns
                if total_points > 1000 and completed_achievements > 5:
                    return UserMoodState.ACHIEVER
                elif len(achievements) > completed_achievements * 2:  # Many incomplete achievements
                    return UserMoodState.COLLECTOR
                elif completed_missions > 10:
                    return UserMoodState.OPTIMIZER
                elif total_points > 500:
                    return UserMoodState.EXPLORER
                else:
                    return UserMoodState.NEWCOMER
        except Exception as e:
            self.logger.warning(f"Error detecting mood from real data: {e}")
        
        
        if not interactions:
            return UserMoodState.NEWCOMER
            
        recent_actions = [action for action, _ in interactions[-10:]]
        
        # Pattern analysis
        if 'shop' in ' '.join(recent_actions).lower():
            if 'narrative' in ' '.join(recent_actions).lower():
                return UserMoodState.COLLECTOR
        
        if 'trivia' in ' '.join(recent_actions).lower():
            return UserMoodState.ACHIEVER
            
        if 'story' in ' '.join(recent_actions).lower():
            return UserMoodState.STORYTELLER
            
        if len(recent_actions) > 8:  # High activity
            return UserMoodState.EXPLORER
            
        return UserMoodState.OPTIMIZER
    
    async def _get_narrative_context(self, user_id: int) -> Dict:
        """Get narrative context from narrative service"""
        try:
            if self.services.get('narrative'):
                # This would call actual narrative service methods
                return {'progress': 25.0}  # Mock for now
            return {'progress': 0.0}
        except:
            return {'progress': 0.0}
    
    def _calculate_session_duration(self, user_id: int) -> int:
        """Calculate current session duration in minutes"""
        # Mock implementation - in real system would track session start
        return 15
    
    def _get_recent_actions(self, user_id: int) -> List[str]:
        """Get user's recent actions"""
        interactions = self.interaction_patterns.get(user_id, [])
        return [action for action, _ in interactions[-5:]]
    
    async def _identify_preferred_features(self, user_id: int) -> List[str]:
        """Identify user's preferred features based on usage"""
        # Mock implementation - analyze user behavior patterns
        return ["trivia", "shop", "story"]
    
    async def _get_notification_prefs(self, user_id: int) -> Dict[str, bool]:
        """Get user notification preferences"""
        return {
            "daily_rewards": True,
            "mission_updates": True,
            "story_updates": False
        }
    
    async def _calculate_personalization_score(self, user_id: int) -> float:
        """Calculate how well we understand this user (0-1)"""
        interactions = len(self.interaction_patterns.get(user_id, []))
        return min(interactions / 50.0, 1.0)  # Max score after 50 interactions
    
    def _analyze_engagement_pattern(self, interactions: List) -> str:
        """📊 Engagement pattern recognition"""
        if not interactions:
            return "new_user"
            
        # Time-based analysis
        now = datetime.now()
        recent = [ts for _, ts in interactions if (now - ts).days < 7]
        
        if len(recent) > 20:
            return "power_user"
        elif len(recent) > 10:
            return "regular_user" 
        elif len(recent) > 3:
            return "casual_user"
        else:
            return "returning_user"


class DianaMasterInterface:
    """
    🏛️ THE MASTER INTERFACE
    
    This isn't just a menu system - it's a conversation with the ecosystem.
    Every button, every text, every flow is intelligently crafted.
    """
    
    def __init__(self, services: Dict[str, Any]):
        self.services = services
        self.context_engine = AdaptiveContextEngine(services)
        self.logger = structlog.get_logger()
        
        # Revolutionary features
        self.smart_predictions: Dict[int, List[str]] = {}
        self.contextual_shortcuts: Dict[int, Dict[str, Any]] = {}
        self.dynamic_layouts: Dict[int, str] = {}
        
    async def create_adaptive_interface(self, user_id: int, trigger: str = "main") -> Tuple[str, InlineKeyboardMarkup]:
        """
        🎨 ADAPTIVE INTERFACE GENERATION
        
        Creates a completely personalized interface based on:
        - User behavior patterns
        - Current context 
        - Predictive analytics
        - Emotional state
        - System state
        """
        
        # Analyze user context
        context = await self.context_engine.analyze_user_context(user_id)
        
        # Get real-time system state
        system_state = await self._get_system_state()
        
        # Generate personalized content
        interface_data = await self._generate_interface(context, system_state, trigger)
        
        return interface_data['text'], interface_data['keyboard']
    
    async def _get_system_state(self) -> Dict:
        """Get current system state for contextual decisions"""
        try:
            # Get real-time system information
            tariff_stats = await self.services['tariff'].get_tariff_stats()
            
            return {
                'active_tariffs': tariff_stats.get('active_tariffs', 0),
                'system_load': 'normal',  # Mock
                'maintenance_mode': False,
                'special_events': [],  # Mock - would contain active events
                'timestamp': datetime.now()
            }
        except Exception as e:
            self.logger.error("Error getting system state", error=str(e))
            return {
                'active_tariffs': 0,
                'system_load': 'unknown',
                'maintenance_mode': False,
                'special_events': [],
                'timestamp': datetime.now()
            }
    
    async def _generate_interface(self, context: UserContext, system_state: Dict, trigger: str) -> Dict:
        """🚀 The magic happens here - dynamic interface generation"""
        
        # === PERSONALIZED GREETING ===
        greeting = await self._generate_smart_greeting(context)
        
        # === CONTEXTUAL DASHBOARD ===
        dashboard = await self._generate_contextual_dashboard(context)
        
        # === PREDICTIVE ACTIONS ===
        predicted_actions = await self._generate_predictive_actions(context)
        
        # === SMART SHORTCUTS ===
        smart_shortcuts = await self._generate_smart_shortcuts(context)
        
        # === DYNAMIC KEYBOARD ===
        keyboard = await self._generate_adaptive_keyboard(context, predicted_actions, smart_shortcuts)
        
        # Combine everything into a cohesive experience
        text = f"{greeting}\n\n{dashboard}\n\n{predicted_actions}"
        
        return {
            'text': text,
            'keyboard': keyboard,
            'context_hash': hash(str(context))  # For caching
        }
    
    async def _generate_smart_greeting(self, context: UserContext) -> str:
        """👋 AI-powered personalized greetings"""
        
        mood_greetings = {
            UserMoodState.EXPLORER: [
                "🔮 ¡Hay secretos esperándote, explorador!",
                "🌟 Diana ha preparado algo especial para ti...",
                "🗺️ Nuevos territorios por descubrir te aguardan"
            ],
            UserMoodState.ACHIEVER: [
                "🎯 ¡Es hora de conquistar nuevos logros!",
                "🏆 Tu próxima victoria está a un clic de distancia",
                "⚡ El poder de completar misiones te llama"
            ],
            UserMoodState.COLLECTOR: [
                "💎 Los tesoros más raros te están esperando",
                "🎁 Tu colección puede crecer aún más...",
                "✨ Nuevos objetos han aparecido en el horizonte"
            ],
            UserMoodState.STORYTELLER: [
                "📖 La historia continúa escribiéndose...",
                "🎭 Diana tiene más secretos que revelar",
                "📜 Nuevos capítulos de tu aventura te aguardan"
            ],
            UserMoodState.SOCIALIZER: [
                "👥 La comunidad te está esperando",
                "🌐 Conecta con otros aventureros como tú",
                "💬 Nuevas conversaciones y desafíos sociales"
            ],
            UserMoodState.OPTIMIZER: [
                "📊 Aquí tienes tu resumen optimizado",
                "⚙️ Eficiencia máxima en cada acción",
                "🎛️ Control total de tu progreso"
            ],
            UserMoodState.NEWCOMER: [
                "🌅 ¡Bienvenido al mundo de Diana!",
                "🗝️ Te voy a mostrar los secretos de este lugar",
                "👑 Tu aventura épica comienza ahora"
            ]
        }
        
        import random
        return random.choice(mood_greetings[context.current_mood])
    
    async def _generate_contextual_dashboard(self, context: UserContext) -> str:
        """📊 Dynamic dashboard based on user state"""
        try:
            # Get real user statistics
            dashboard_text = ""
            
            if self._gamification_service:
                points_data = await self._gamification_service.get_user_points(context.user_id)
                missions = await self._gamification_service.get_user_missions(context.user_id)
                
                current_points = points_data.get('current_points', 0)
                active_missions = len(missions.get('in_progress', []))
                completed_today = len([m for m in missions.get('completed', []) 
                                     if m.get('completed_at') and 
                                     (datetime.now() - datetime.fromisoformat(m['completed_at'])).days < 1])
                
                if context.current_mood == UserMoodState.ACHIEVER:
                    dashboard_text = f"🎯 **MODO CONQUISTA ACTIVADO**\n"
                    dashboard_text += f"⭐ Nivel: {self._calculate_level_from_points(current_points)}\n"
                    dashboard_text += f"🔥 Misiones completadas hoy: {completed_today}\n"
                    dashboard_text += f"🎯 Misiones activas: {active_missions}\n"
                elif context.current_mood == UserMoodState.COLLECTOR:
                    achievements = await self._gamification_service.get_user_achievements(context.user_id)
                    completed_achievements = len([a for a in achievements if a.get('is_completed', False)])
                    dashboard_text = f"💎 **COLECCIÓN ACTIVA**\n"
                    dashboard_text += f"💰 Besitos: {current_points:,}\n"
                    dashboard_text += f"🏆 Logros: {completed_achievements}\n"
                    dashboard_text += f"📦 Inventario: {len(achievements)} items\n"
                elif context.current_mood == UserMoodState.STORYTELLER:
                    if self._narrative_service:
                        lore_pieces = await self._narrative_service.get_user_lore_pieces(context.user_id)
                        dashboard_text = f"📖 **NARRATIVA EN PROGRESO**\n"
                        dashboard_text += f"📚 Historia: {context.narrative_progress * 100:.1f}% completada\n"
                        dashboard_text += f"🔍 Pistas: {len(lore_pieces)}\n"
                        dashboard_text += f"💫 Progreso narrativo: Activo\n"
                elif context.current_mood == UserMoodState.OPTIMIZER:
                    dashboard_text = f"📊 **PANEL DE CONTROL**\n"
                    dashboard_text += f"⚙️ Eficiencia: {context.gamification_engagement * 100:.1f}%\n"
                    dashboard_text += f"📈 Rendimiento: Óptimo\n"
                    dashboard_text += f"🎯 Objetivos: {active_missions} activos\n"
                else:  # NEWCOMER or EXPLORER
                    dashboard_text = f"🌟 **BIENVENIDO AL UNIVERSO DIANA**\n"
                    dashboard_text += f"💰 Besitos: {current_points}\n"
                    dashboard_text += f"⭐ Nivel: {self._calculate_level_from_points(current_points)}\n"
                    dashboard_text += f"🎯 Misiones disponibles: {len(missions.get('available', []))}\n"
            
            return dashboard_text
            
        except Exception as e:
            self.logger.error(f"Error generating contextual dashboard: {e}")
            # Fallback to mock data
        
        # Get real-time user stats (with fallback)
        try:
            if hasattr(self.services['gamification'], 'get_user_points'):
                stats = await self.services['gamification'].get_user_points(context.user_id)
            else:
                # Fallback to mock stats for now
                stats = {
                    'level': 1,
                    'points': 0,
                    'streak': 0,
                    'inventory': [],
                    'achievements': [],
                    'clues': 0,
                    'fragments': 0,
                    'efficiency_score': 85,
                    'active_goals': 3,
                    'active_missions': [],
                    'engagement_level': 0.5
                }
        except Exception as e:
            self.logger.warning("Error getting user stats", error=str(e))
            stats = {'level': 1, 'points': 0, 'streak': 0}
        
        # Check daily reward status (fallback to mock if method doesn't exist)
        try:
            if hasattr(self.services['daily_rewards'], 'can_claim_daily_reward'):
                daily_status = await self.services['daily_rewards'].can_claim_daily_reward(context.user_id)
            else:
                # Mock daily status based on user activity
                daily_status = True  # Assume available for now
        except:
            daily_status = True
        
        # Smart stat selection based on user mood
        if context.current_mood == UserMoodState.ACHIEVER:
            return f"🎯 **MODO CONQUISTA ACTIVADO**\n⚡ Nivel: {stats.get('level', 1)} | 💰 Besitos: {stats.get('points', 0)}\n🔥 Racha: {stats.get('streak', 0)} días | 🎁 Regalo: {'✅ Disponible' if daily_status else '⏰ Próximamente'}"
        
        elif context.current_mood == UserMoodState.COLLECTOR:
            items_count = len(stats.get('inventory', []))
            return f"💎 **COLECCIÓN ACTIVA**\n🎒 Objetos: {items_count} | 💰 Besitos: {stats.get('points', 0)}\n🏆 Logros: {len(stats.get('achievements', []))} | ⭐ Progreso: {context.narrative_progress:.1f}%"
        
        elif context.current_mood == UserMoodState.STORYTELLER:
            return f"📖 **NARRATIVA EN PROGRESO**\n📜 Historia: {context.narrative_progress:.1f}% completa\n🔍 Pistas: {stats.get('clues', 0)} | 🎭 Fragmentos: {stats.get('fragments', 0)}"
        
        elif context.current_mood == UserMoodState.OPTIMIZER:
            efficiency = stats.get('efficiency_score', 85)
            return f"📊 **PANEL DE CONTROL**\n⚙️ Eficiencia: {efficiency}% | 📈 Tendencia: {'📈 Subiendo' if efficiency > 80 else '📊 Estable'}\n🎯 Objetivos: {stats.get('active_goals', 3)} activos"
            
        else:  # Default/Explorer/Newcomer/Socializer
            return f"🌟 **ESTADO DEL AVENTURERO**\n⭐ Nivel: {stats.get('level', 1)} | 💰 Besitos: {stats.get('points', 0)}\n🎯 Misiones: {len(stats.get('active_missions', []))} activas"
    
    async def _generate_predictive_actions(self, context: UserContext) -> str:
        """🔮 AI-powered action predictions"""
        try:
            predictions = []
            
            # Check daily rewards
            if self._daily_rewards_service:
                can_claim = await self._daily_rewards_service.can_claim_daily_reward(context.user_id)
                if can_claim:
                    predictions.append("💡 *Predicción: Tu regalo diario está esperándote*")
            
            # Check trivia availability
            if self._trivia_service:
                can_answer = await self._trivia_service.can_answer_daily(context.user_id)
                if can_answer:
                    predictions.append("🧠 *Sugerencia: Nueva trivia disponible para ti*")
            
            # Check missions
            if self._gamification_service:
                missions = await self._gamification_service.get_user_missions(context.user_id)
                active_missions = len(missions.get('in_progress', []))
                if active_missions > 0:
                    predictions.append(f"🎯 *Recordatorio: {active_missions} misiones en progreso*")
                
                available_missions = len(missions.get('available', []))
                if available_missions > 0:
                    predictions.append(f"🚀 *Oportunidad: {available_missions} nuevas misiones disponibles*")
            
            # Check narrative progress
            if self._narrative_service and context.narrative_progress < 0.8:
                predictions.append("📖 *Recomendación: Tu historia está esperando continuar...*")
            
            # Return random prediction or default
            if predictions:
                return random.choice(predictions)
            else:
                return "✨ *Todo está en orden - ¡explora nuevas aventuras!*"
                
        except Exception as e:
            self.logger.error(f"Error generating predictions: {e}")
        
        # Fallback predictions
        
        predictions = []
        
        # Analyze user patterns and predict next likely actions
        if context.current_mood == UserMoodState.COLLECTOR:
            try:
                if hasattr(self.services['daily_rewards'], 'can_claim_daily_reward'):
                    daily_available = await self.services['daily_rewards'].can_claim_daily_reward(context.user_id)
                else:
                    daily_available = True  # Mock availability
            except:
                daily_available = True
                
            if daily_available:
                predictions.append("💡 *Predicción: Probablemente quieras reclamar tu regalo diario*")
        
        if context.engagement_pattern == "power_user":
            predictions.append("🚀 *Sugerencia: Nuevas misiones épicas disponibles*")
        
        if context.narrative_progress > 70:
            predictions.append("📖 *Recomendación: El final de tu historia se acerca...*")
            
        return "\n".join(predictions) if predictions else "✨ *El sistema está analizando tus próximas oportunidades...*"
    
    async def _generate_smart_shortcuts(self, context: UserContext) -> List[Dict[str, str]]:
        """⚡ Intelligent shortcut generation"""
        
        shortcuts = []
        
        # Mood-based shortcuts
        if context.current_mood == UserMoodState.ACHIEVER:
            shortcuts.extend([
                {"text": "🎯 Misiones Rápidas", "callback_data": "smart:quick_missions"},
                {"text": "🏆 Ver Logros", "callback_data": "smart:achievements"}
            ])
        
        elif context.current_mood == UserMoodState.COLLECTOR:
            shortcuts.extend([
                {"text": "🛒 Tienda Premium", "callback_data": "smart:premium_shop"},
                {"text": "🎁 Recompensas", "callback_data": "smart:rewards"}
            ])
        
        elif context.current_mood == UserMoodState.STORYTELLER:
            shortcuts.extend([
                {"text": "📖 Continuar Historia", "callback_data": "smart:story_continue"},
                {"text": "🔍 Buscar Pistas", "callback_data": "smart:find_clues"}
            ])
        
        # Always available smart actions
        shortcuts.append({"text": "⚡ Acción Rápida", "callback_data": "smart:quick_action"})
        
        return shortcuts
    
    async def _generate_adaptive_keyboard(self, context: UserContext, predictions: str, shortcuts: List[Dict]) -> InlineKeyboardMarkup:
        """⌨️ Dynamic keyboard generation based on context"""
        
        buttons = []
        
        # === ROW 1: SMART SHORTCUTS (Always visible) ===
        if shortcuts:
            shortcut_row = [InlineKeyboardButton(text=s["text"], callback_data=s["callback_data"]) for s in shortcuts[:2]]
            buttons.append(shortcut_row)
        
        # === ROW 2: MOOD-SPECIFIC PRIMARY ACTIONS ===
        if context.current_mood == UserMoodState.ACHIEVER:
            buttons.append([
                InlineKeyboardButton(text="🎯 Centro de Misiones", callback_data="diana:missions_hub"),
                InlineKeyboardButton(text="🏆 Motor de Logros", callback_data="diana:achievement_engine")
            ])
            # Add leaderboard for competitive achievers
            buttons.append([
                InlineKeyboardButton(text="📊 Mi Progreso", callback_data="diana:progress_tracker"),
                InlineKeyboardButton(text="🏆 Rankings", callback_data="diana:leaderboard_system")
            ])
        
        elif context.current_mood == UserMoodState.COLLECTOR:
            buttons.append([
                InlineKeyboardButton(text="🛒 Tienda Épica", callback_data="diana:epic_shop"),
                InlineKeyboardButton(text="🎒 Mi Colección", callback_data="diana:collection")
            ])
        
        elif context.current_mood == UserMoodState.STORYTELLER:
            buttons.append([
                InlineKeyboardButton(text="📖 Historia Viva", callback_data="diana:narrative_hub"),
                InlineKeyboardButton(text="🎭 Decisiones", callback_data="diana:story_choices")
            ])
        
        elif context.current_mood == UserMoodState.EXPLORER:
            buttons.append([
                InlineKeyboardButton(text="🗺️ Explorar Todo", callback_data="diana:explore_mode"),
                InlineKeyboardButton(text="🔮 Sorpréndeme", callback_data="diana:surprise_me")
            ])
        
        elif context.current_mood == UserMoodState.OPTIMIZER:
            buttons.append([
                InlineKeyboardButton(text="📊 Dashboard Pro", callback_data="diana:pro_dashboard"),
                InlineKeyboardButton(text="⚙️ Config Gamificación", callback_data="diana:gamification_settings")
            ])
            # Add advanced gamification row for optimizers
            buttons.append([
                InlineKeyboardButton(text="💰 Calculadora Rewards", callback_data="diana:reward_calculator"),
                InlineKeyboardButton(text="🏆 Rankings", callback_data="diana:leaderboard_system")
            ])
        
        else:  # Newcomer/Socializer/Default
            buttons.append([
                InlineKeyboardButton(text="🌟 Comenzar Aventura", callback_data="diana:start_journey"),
                InlineKeyboardButton(text="💫 Tour Guiado", callback_data="diana:guided_tour")
            ])
        
        # === ROW 3: CORE FEATURES (Always available) ===
        buttons.append([
            InlineKeyboardButton(text="🎁 Regalo Diario", callback_data="diana:daily_gift"),
            InlineKeyboardButton(text="🧠 Trivia", callback_data="diana:trivia_challenge")
        ])
        
        # === ROW 4: ADMIN ACCESS (If applicable) ===
        # TODO: Check if user is admin
        # if await self._is_admin(context.user_id):
        #     buttons.append([InlineKeyboardButton(text="👑 Centro de Comando", callback_data="diana:admin_center")])
        
        # === ROW 5: NAVIGATION ===
        buttons.append([
            InlineKeyboardButton(text="🔄 Actualizar", callback_data="diana:refresh"),
            InlineKeyboardButton(text="❓ Ayuda Inteligente", callback_data="diana:smart_help")
        ])
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)


# === GLOBAL ROUTER REGISTRATION ===

master_router = Router()

# Initialize the system when imported
diana_master: Optional[DianaMasterInterface] = None

def initialize_diana_master(services: Dict[str, Any]):
    """🚀 Initialize the Diana Master System"""
    global diana_master
    diana_master = DianaMasterInterface(services)
    return diana_master


# === COMMAND HANDLERS ===

@master_router.message(Command("start"))
async def cmd_start(message: Message):
    """🌟 The entry point to the Diana universe"""
    if not diana_master:
        await message.reply("🔧 Sistema inicializándose...")
        return
    
    user_id = message.from_user.id
    text, keyboard = await diana_master.create_adaptive_interface(user_id, "start")
    
    await message.reply(text, reply_markup=keyboard, parse_mode="Markdown")


@master_router.message(Command("admin"))
async def cmd_admin(message: Message):
    """👑 Admin access point"""
    if not diana_master:
        await message.reply("🔧 Sistema inicializándose...")
        return
    
    # TODO: Check admin permissions
    user_id = message.from_user.id
    text, keyboard = await diana_master.create_adaptive_interface(user_id, "admin")
    
    await message.reply(text, reply_markup=keyboard, parse_mode="Markdown")


@master_router.callback_query(F.data.startswith("diana:"))
async def handle_diana_callbacks(callback: CallbackQuery):
    """🎭 Handle all Diana Master System callbacks"""
    if not diana_master:
        await callback.answer("🔧 Sistema no disponible")
        return
    
    action = callback.data.replace("diana:", "")
    user_id = callback.from_user.id
    
    # Import existing handlers for integration
    try:
        from src.bot.handlers.gamification.misiones import handle_missions_callback
        from src.bot.handlers.user.shop import shop_main_callback
        from src.bot.handlers.narrative.navigation import show_current_fragment
        from src.bot.handlers.user.trivia import trivia_start_callback
        from src.bot.handlers.user.daily_rewards import daily_main_callback
    except ImportError as e:
        diana_master.logger.warning(f"Could not import existing handlers: {e}")
    
    # Import FASE 2 core handlers
    try:
        from src.bot.handlers.diana.core_handlers import (
            handle_progress_tracker,
            handle_pro_dashboard,
            handle_explore_mode,
            handle_start_journey,
            handle_guided_tour,
            handle_collection,
            handle_story_choices
        )
    except ImportError:
        diana_master.logger.warning("FASE 2 core handlers not yet implemented")
    
    # Import FASE 2.3 advanced gamification handlers
    try:
        from src.bot.handlers.diana.advanced_gamification_handlers import (
            handle_achievement_engine,
            handle_reward_calculator,
            handle_leaderboard_system,
            handle_gamification_settings
        )
    except ImportError:
        diana_master.logger.warning("FASE 2.3 advanced gamification handlers not yet implemented")
    
    # Route to specialized handlers based on action
    if action == "refresh":
        text, keyboard = await diana_master.create_adaptive_interface(user_id, "refresh")
        await safe_edit_message(callback, text, keyboard)
        
    # === EXISTING HANDLERS INTEGRATION (FASE 2.2) ===
    elif action.startswith("missions_hub"):
        await handle_diana_missions_integration(callback, diana_master)
        
    elif action.startswith("epic_shop"):
        await handle_diana_shop_integration(callback, diana_master)
        
    elif action.startswith("narrative_hub"):
        await handle_diana_narrative_integration(callback, diana_master)
        
    elif action.startswith("trivia_challenge"):
        await handle_diana_trivia_integration(callback, diana_master)
        
    elif action == "daily_gift":
        await handle_diana_daily_rewards_integration(callback, diana_master)
    
    # === DIANA MASTER SPECIFIC HANDLERS ===
    elif action == "surprise_me":
        await handle_surprise_feature(callback, diana_master)
        
    elif action.startswith("smart_help"):
        await handle_smart_help(callback, diana_master)
    
    # === FASE 2 CORE HANDLERS - NEW IMPLEMENTATIONS ===
    elif action == "progress_tracker":
        try:
            await handle_progress_tracker(callback, diana_master)
        except NameError:
            await handle_progress_tracker_fallback(callback, diana_master)
        
    elif action == "pro_dashboard":  
        try:
            await handle_pro_dashboard(callback, diana_master)
        except NameError:
            await handle_pro_dashboard_fallback(callback, diana_master)
        
    elif action == "explore_mode":
        try:
            await handle_explore_mode(callback, diana_master)
        except NameError:
            await handle_explore_mode_fallback(callback, diana_master)
        
    elif action == "start_journey":
        try:
            await handle_start_journey(callback, diana_master)
        except NameError:
            await handle_start_journey_fallback(callback, diana_master)
        
    elif action == "guided_tour":
        try:
            await handle_guided_tour(callback, diana_master)
        except NameError:
            await handle_guided_tour_fallback(callback, diana_master)
        
    elif action == "collection":
        try:
            await handle_collection(callback, diana_master)
        except NameError:
            await handle_collection_fallback(callback, diana_master)
        
    elif action == "story_choices":
        try:
            await handle_story_choices(callback, diana_master)
        except NameError:
            await handle_story_choices_fallback(callback, diana_master)
    
    # === FASE 2.3 ADVANCED GAMIFICATION HANDLERS ===
    elif action == "achievement_engine":
        try:
            await handle_achievement_engine(callback, diana_master)
        except NameError:
            await handle_achievement_engine_fallback(callback, diana_master)
        
    elif action == "reward_calculator":
        try:
            await handle_reward_calculator(callback, diana_master)
        except NameError:
            await handle_reward_calculator_fallback(callback, diana_master)
        
    elif action == "leaderboard_system":
        try:
            await handle_leaderboard_system(callback, diana_master)
        except NameError:
            await handle_leaderboard_system_fallback(callback, diana_master)
        
    elif action == "gamification_settings":
        try:
            await handle_gamification_settings(callback, diana_master)
        except NameError:
            await handle_gamification_settings_fallback(callback, diana_master)
        
    else:
        # Unknown action - show main menu
        text, keyboard = await diana_master.create_adaptive_interface(user_id, "refresh")
        await safe_edit_message(callback, text, keyboard)
    
    await callback.answer()


@master_router.callback_query(F.data.startswith("trivia:"))
async def handle_trivia_callbacks(callback: CallbackQuery):
    """🧠 Handle trivia answer callbacks"""
    if not diana_master:
        await callback.answer("🔧 Sistema no disponible")
        return
    
    trivia_data = callback.data.replace("trivia:", "")
    user_id = callback.from_user.id
    
    # Parse trivia answer: "correct:jupiter" or "wrong:earth"
    if trivia_data.startswith("correct:"):
        answer = trivia_data.replace("correct:", "")
        result_text = "🎉 **¡RESPUESTA CORRECTA!**\n\n"
        result_text += f"✅ ¡Bien hecho! {answer.capitalize()} es efectivamente el planeta más grande del sistema solar.\n\n"
        result_text += "🏆 **Recompensas obtenidas:**\n"
        result_text += "• 💰 20 Besitos\n"
        result_text += "• 🎯 +1 Pregunta correcta\n"
        result_text += "• ⭐ Experiencia en trivia\n\n"
        result_text += "🚀 ¡Sigue así y conviértete en un maestro del conocimiento!"
        
    elif trivia_data.startswith("wrong:"):
        answer = trivia_data.replace("wrong:", "")
        result_text = "😅 **Respuesta Incorrecta**\n\n"
        result_text += f"❌ {answer.capitalize()} no es correcto, pero ¡no te desanimes!\n\n"
        result_text += "💡 **Respuesta correcta:** Júpiter es el planeta más grande de nuestro sistema solar.\n\n"
        result_text += "🎁 **Consolación:**\n"
        result_text += "• 💰 5 Besitos por intentarlo\n"
        result_text += "• 🧠 Conocimiento adquirido\n\n"
        result_text += "📚 ¡Cada error es una oportunidad de aprender!"
    
    else:
        result_text = "🤔 Respuesta no reconocida. ¡Inténtalo de nuevo!"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎲 Nueva Pregunta", callback_data="diana:trivia_challenge")],
        [InlineKeyboardButton(text="🏠 Volver al Inicio", callback_data="diana:refresh")]
    ])
    
    await safe_edit_message(callback, result_text, keyboard)
    await callback.answer()


# === SPECIALIZED HANDLERS ===

# === FASE 2.2 INTEGRATION HANDLERS ===

async def handle_diana_missions_integration(callback: CallbackQuery, master: DianaMasterInterface):
    """🎯 Diana Master Missions Hub Integration"""
    user_id = callback.from_user.id
    
    # Get Diana Master context
    context = await master.context_engine.analyze_user_context(user_id)
    
    # Get missions data from gamification service
    try:
        if master.services.get('gamification'):
            missions = await master.services['gamification'].get_user_missions(user_id)
        else:
            # Fallback mock data
            missions = {
                "available": [],
                "in_progress": [],
                "completed": []
            }
    except Exception as e:
        master.logger.warning(f"Error getting missions: {e}")
        missions = {"available": [], "in_progress": [], "completed": []}
    
    # Create Diana Master style missions interface
    missions_text = "🎯 **CENTRO DE MISIONES DIANA**\n\n"
    
    if context.current_mood == UserMoodState.ACHIEVER:
        missions_text += "⚡ *¡Modo conquistador activado! Estas misiones son perfectas para ti*\n\n"
    else:
        missions_text += "🌟 *Nuevas aventuras te esperan, valiente explorador*\n\n"
    
    # Mission statistics
    available_count = len(missions["available"])
    in_progress_count = len(missions["in_progress"])
    completed_count = len(missions["completed"])
    total_count = available_count + in_progress_count + completed_count
    
    if total_count > 0:
        missions_text += f"📊 **ESTADO DE MISIONES:**\n"
        missions_text += f"• {available_count} misiones disponibles\n"
        missions_text += f"• {in_progress_count} misiones en progreso\n"
        missions_text += f"• {completed_count} misiones completadas\n\n"
        
        # Show some missions preview
        if missions["in_progress"]:
            missions_text += "**🔥 MISIONES EN PROGRESO:**\n"
            for mission in missions["in_progress"][:2]:  # Show max 2
                progress = mission.get('progress_percentage', 0)
                missions_text += f"• {mission['title']} ({progress:.0f}%)\n"
            missions_text += "\n"
        
        if missions["available"]:
            missions_text += "**✨ NUEVAS MISIONES:**\n"
            for mission in missions["available"][:2]:  # Show max 2
                missions_text += f"• {mission['title']}\n"
            missions_text += "\n"
    else:
        missions_text += "🌟 **PREPARÁNDOTE NUEVAS AVENTURAS**\n\n"
        missions_text += "Interactúa con Diana y explora la narrativa para desbloquear misiones épicas.\n\n"
    
    # Get user stats for display
    try:
    user_id = callback.from_user.id
        narrative_text += f"📊 **Progreso narrativo:** {context.narrative_progress * 100:.1f}%\n"
        narrative_text += "🎭 Cada decisión cambia tu destino"
        shop_text += "🏆 *Herramientas para conquistar todos los logros*\n\n"
    else:
        shop_text += "✨ *Descubre tesoros únicos en nuestro catálogo*\n\n"
    
    # Get user stats
    try:
        if master.services.get('shop'):
            user_stats = await master.services['shop'].gamification_service.get_user_stats(user_id)
            user_points = user_stats.get('total_points', 0)
            user_level = user_stats.get('level', 0)
        else:
            user_points = 0
            user_level = 1
    except:
        user_points = 0
        user_level = 1
    
    shop_text += f"💋 **Tus besitos:** {user_points}\n"
    shop_text += f"⭐ **Nivel:** {user_level}\n\n"
    
    # Get available categories
    try:
        if master.services.get('shop'):
            categories = await master.services['shop'].get_categories()
        else:
            categories = ["narrativa", "gamificacion", "especiales"]
    except:
        categories = ["narrativa", "gamificacion", "especiales"]
    
    shop_text += "**📦 CATEGORÍAS DISPONIBLES:**\n"
    category_icons = {
        "narrativa": "📖",
        "gamificacion": "🎮", 
        "vip": "👑",
        "especiales": "✨"
    }
    
    for category in categories[:3]:  # Show first 3 categories
        icon = category_icons.get(category, "📦")
        shop_text += f"• {icon} {category.title()}\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍️ Explorar Tienda", callback_data="shop:main")],
        [InlineKeyboardButton(text="👑 Artículos VIP", callback_data="shop:vip_only")],
        [InlineKeyboardButton(text="📊 Mis Compras", callback_data="shop:history")],
        [InlineKeyboardButton(text="🏠 Volver al Inicio", callback_data="diana:refresh")]
    ])
    
    await safe_edit_message(callback, shop_text, keyboard)


async def handle_diana_narrative_integration(callback: CallbackQuery, master: DianaMasterInterface):
    """📖 Diana Master Narrative Hub Integration"""
    user_id = callback.from_user.id
    
    # Get user context and narrative progress
    context = await master.context_engine.analyze_user_context(user_id)
    narrative_progress = context.narrative_progress
    
    story_text = "📖 **HISTORIA VIVA DE DIANA**\n\n"
    # Get real daily rewards data
    gift_text = "🎁 **REGALO DIARIO ÉPICO**\n\n"
    
    try:
        if master.context_engine._daily_rewards_service:
            can_claim = await master.context_engine._daily_rewards_service.can_claim_daily_reward(user_id)
            stats = await master.context_engine._daily_rewards_service.get_user_daily_stats(user_id)
            
            consecutive_days = stats.get('consecutive_days', 0)
            total_claimed = stats.get('total_claimed', 0)
            
            if can_claim:
                reward = await master.context_engine._daily_rewards_service.get_available_reward(user_id)
                if reward:
                    gift_text += f"{reward.icon} **{reward.name}**\n"
                    gift_text += f"✨ *{reward.rarity.title()}*\n\n"
                    gift_text += f"{reward.description}\n\n"
                    gift_text += f"🔥 **Racha actual:** {consecutive_days} días\n"
                    gift_text += f"📦 **Total reclamados:** {total_claimed}\n\n"
                    
                    # Streak bonuses
                    if consecutive_days >= 7:
                        gift_text += "🎊 **¡Bonus por racha semanal!**\n"
                    if consecutive_days >= 30:
                        gift_text += "👑 **¡Bonus legendario por mes completo!**\n"
                    
                    gift_text += "¡Reclama tu regalo para mantener tu racha!"
                else:
                    gift_text += "⏰ **No hay regalos disponibles en este momento**\n"
                    gift_text += "Intenta más tarde o contacta soporte."
            else:
                next_claim = stats.get('next_claim_time')
                if next_claim:
                    hours_remaining = (next_claim - datetime.now()).total_seconds() / 3600
                    gift_text += f"⏰ **Próximo regalo en:** {hours_remaining:.1f} horas\n\n"
                
                gift_text += f"🔥 **Racha actual:** {consecutive_days} días\n"
                gift_text += f"📦 **Total reclamados:** {total_claimed}\n\n"
                gift_text += "¡Ya reclamaste tu regalo de hoy! Vuelve mañana."
        
    except Exception as e:
        master.logger.error(f"Error getting daily gift data: {e}")
        gift_text += "✨ *Sistema de recompensas diarias*\n\n"
    
    
        gift_text += "💎 *Especialmente seleccionado para coleccionistas*\n"
        fragment = None
        gift_text += "🌟 *Tu recompensa diaria te está esperando*\n"
        if fragment.get('choices'):
            for i, choice in enumerate(fragment['choices'][:2], 1):
                story_text += f"{i}. {choice['text'][:50]}...\n"
        else:
    # Check if can claim
    try:
        if master.context_engine._daily_rewards_service:
            can_claim = await master.context_engine._daily_rewards_service.can_claim_daily_reward(user_id)
            if can_claim:
                keyboard_buttons.append([
                    InlineKeyboardButton(text="🎁 Reclamar Regalo", callback_data="daily:claim")
                ])
            else:
                keyboard_buttons.append([
                    InlineKeyboardButton(text="⏰ Ya Reclamado Hoy", callback_data="daily:stats")
                ])
    except:
        keyboard_buttons.append([
            InlineKeyboardButton(text="🎁 Reclamar Regalo", callback_data="daily:claim")
        ])
        story_text += "Interactúa con el bot y completa misiones para desbloquear contenido narrativo.\n\n"
        story_text += f"📊 Progreso general: {narrative_progress:.1f}%"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📖 Continuar Historia", callback_data="narrative:continue")],
        [InlineKeyboardButton(text="🌿 Explorar Ramas", callback_data="narrative:explore")],
        [InlineKeyboardButton(text="📜 Fragmentos Desbloqueados", callback_data="narrative:fragments")],
        [InlineKeyboardButton(text="🏠 Volver al Inicio", callback_data="diana:refresh")]
    ])
    
    await safe_edit_message(callback, story_text, keyboard)


async def handle_diana_trivia_integration(callback: CallbackQuery, master: DianaMasterInterface):
    """🧠 Diana Master Trivia Integration"""
    user_id = callback.from_user.id
    context = await master.context_engine.analyze_user_context(user_id)
    
    trivia_text = "🧠 **DESAFÍO TRIVIA DIANA**\n\n"
    
    if context.current_mood == UserMoodState.ACHIEVER:
        trivia_text += "⚡ *¡Perfecto! Tu mente conquistadora está lista para el desafío*\n\n"
    else:
    # Get real trivia data
        trivia_text += "🌟 *Prepárate para poner a prueba tu conocimiento*\n\n"
    
    try:
        if master.context_engine._trivia_service:
            can_answer = await master.context_engine._trivia_service.can_answer_daily(user_id)
            stats = await master.context_engine._trivia_service.get_user_trivia_stats(user_id)
            
            total_answered = stats.get('total_answered', 0)
            accuracy_rate = stats.get('accuracy_rate', 0)
            daily_streak = stats.get('daily_streak', 0)
            total_points = stats.get('total_points_earned', 0)
            
            trivia_text += f"📊 **Tus estadísticas:**\n"
            trivia_text += f"🎯 Respondidas: {total_answered}\n"
            trivia_text += f"✅ Precisión: {accuracy_rate:.1f}%\n"
            trivia_text += f"🔥 Racha: {daily_streak} días\n"
            trivia_text += f"💰 Puntos ganados: {total_points}\n\n"
            
            if can_answer:
                question = await master.context_engine._trivia_service.get_daily_question(user_id)
                if question:
                    trivia_text += f"**🎯 PREGUNTA DEL DÍA:**\n"
                    trivia_text += f"📂 Categoría: {question.category}\n"
                    trivia_text += f"⚡ Dificultad: {question.difficulty.value.title()}\n"
                    trivia_text += f"💰 Recompensa: {question.points_reward} besitos\n\n"
                    trivia_text += "¿Estás listo para el desafío?"
                else:
                    trivia_text += "⏰ **No hay preguntas disponibles**\n"
                    trivia_text += "Intenta más tarde."
            else:
                trivia_text += "✅ **¡Trivia completada hoy!**\n"
                trivia_text += "Vuelve mañana para una nueva pregunta."
        
    except Exception as e:
        master.logger.error(f"Error getting trivia data: {e}")
        trivia_text += "🎯 *Desafía tu conocimiento*\n\n"
    
    # Check if can answer daily trivia
    try:
        trivia_text += "💡 *Optimiza tu rendimiento*\n"
    
        trivia_text += "🎯 ¿Estás listo para el desafío?"
        trivia_text += "¿Estás listo para el desafío de hoy?"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎯 Empezar Trivia", callback_data="trivia:start")],
    # Check if can start trivia
    try:
        if master.context_engine._trivia_service:
            can_answer = await master.context_engine._trivia_service.can_answer_daily(user_id)
            if can_answer:
                keyboard_buttons.append([
                    InlineKeyboardButton(text="🎯 Empezar Trivia", callback_data="trivia:start")
                ])
            else:
                keyboard_buttons.append([
                    InlineKeyboardButton(text="✅ Completada Hoy", callback_data="trivia:my_stats")
                ])
    except:
        keyboard_buttons.append([
            InlineKeyboardButton(text="🎯 Empezar Trivia", callback_data="trivia:start")
        ])
    else:
        trivia_text += "✅ **TRIVIA DIARIA COMPLETADA**\n\n"
        trivia_text += "Ya has completado la trivia de hoy. ¡Vuelve mañana para una nueva pregunta!\n\n"
        trivia_text += f"📊 **Tus estadísticas:**\n"
        trivia_text += f"• Respondidas: {stats['total_answered']}\n"
        trivia_text += f"• Precisión: {stats['accuracy_rate']:.1f}%\n"
        trivia_text += f"• Puntos ganados: {stats['total_points_earned']}\n"
        trivia_text += f"• Racha actual: {stats['daily_streak']} días"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📊 Ver Ranking", callback_data="trivia:leaderboard")],
            [InlineKeyboardButton(text="📈 Mis Estadísticas", callback_data="trivia:my_stats")],
            [InlineKeyboardButton(text="🏠 Volver al Inicio", callback_data="diana:refresh")]
        ])
    
    await safe_edit_message(callback, trivia_text, keyboard)


async def handle_diana_daily_rewards_integration(callback: CallbackQuery, master: DianaMasterInterface):
    """🎁 Diana Master Daily Rewards Integration"""
    user_id = callback.from_user.id
    context = await master.context_engine.analyze_user_context(user_id)
    
    gift_text = "🎁 **REGALO DIARIO DIANA**\n\n"
    
    if context.current_mood == UserMoodState.COLLECTOR:
        gift_text += "💎 *Un tesoro especial te espera cada día, coleccionista épico*\n\n"
    else:
        gift_text += "✨ *Diana tiene una sorpresa especial preparada para ti*\n\n"
    
    # Check daily reward availability
    try:
        if master.services.get('daily_rewards'):
            stats = await master.services['daily_rewards'].get_user_daily_stats(user_id)
            can_claim = stats["can_claim_today"]
        else:
            can_claim = True
            stats = {"consecutive_days": 0, "total_claimed": 0, "best_streak": 0}
    except:
        can_claim = True
        stats = {"consecutive_days": 0, "total_claimed": 0, "best_streak": 0}
    
    if can_claim:
        # Can claim reward
        try:
            if master.services.get('daily_rewards'):
                reward = await master.services['daily_rewards'].get_available_reward(user_id)
            else:
                reward = None
        except:
            reward = None
        
        if reward:
            rarity_icons = {
                "common": "⚪",
                "rare": "🔵", 
                "epic": "🟣",
                "legendary": "🟡"
            }
            
            rarity_icon = rarity_icons.get(getattr(reward, 'rarity', 'common'), "⚪")
            
            gift_text += "🎯 **REGALO DISPONIBLE**\n\n"
            gift_text += f"{getattr(reward, 'icon', '🎁')} **{getattr(reward, 'name', 'Regalo Diario')}**\n"
            gift_text += f"{rarity_icon} *{getattr(reward, 'rarity', 'common').title()}*\n\n"
            gift_text += f"{getattr(reward, 'description', 'Un regalo especial para ti')}\n\n"
        else:
            gift_text += "🎁 **REGALO DIARIO DISPONIBLE**\n\n"
            gift_text += "Diana ha preparado una sorpresa especial para ti.\n\n"
        
        gift_text += f"🔥 **Racha consecutiva:** {stats['consecutive_days']} días\n\n"
        gift_text += "¡Reclama tu regalo para mantener tu racha!"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎁 Reclamar Regalo", callback_data="daily:claim")],
            [InlineKeyboardButton(text="📊 Ver Estadísticas", callback_data="daily:stats")],
            [InlineKeyboardButton(text="🏆 Ranking Rachas", callback_data="daily:leaderboard")],
            [InlineKeyboardButton(text="🏠 Volver al Inicio", callback_data="diana:refresh")]
        ])
    else:
        # Already claimed today
        gift_text += "✅ **REGALO YA RECLAMADO**\n\n"
        gift_text += "Ya has reclamado tu regalo diario de hoy. ¡Vuelve mañana para continuar tu racha!\n\n"
        gift_text += f"🔥 **Racha actual:** {stats['consecutive_days']} días\n"
        gift_text += f"📦 **Total reclamados:** {stats['total_claimed']} regalos\n"
        gift_text += f"🏆 **Mejor racha:** {stats['best_streak']} días"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📊 Ver Estadísticas", callback_data="daily:stats")],
            [InlineKeyboardButton(text="🏆 Ranking Rachas", callback_data="daily:leaderboard")],
            [InlineKeyboardButton(text="🎁 Ver Recompensas", callback_data="daily:rewards_info")],
            [InlineKeyboardButton(text="🏠 Volver al Inicio", callback_data="diana:refresh")]
        ])
    
    await safe_edit_message(callback, gift_text, keyboard)


# === FALLBACK HANDLERS FOR FASE 2 CORE FEATURES ===

async def handle_progress_tracker_fallback(callback: CallbackQuery, master: DianaMasterInterface):
    """📊 Progress Tracker Fallback Implementation"""
    user_id = callback.from_user.id
    context = await master.context_engine.analyze_user_context(user_id)
    
    text = "📊 **SEGUIMIENTO DE PROGRESO**\n\n"
    text += "🎯 **Tu Evolución Diana Master:**\n\n"
    text += f"⭐ Personalización: {context.personalization_score * 100:.0f}%\n"
    text += f"📖 Progreso Narrativo: {context.narrative_progress:.1f}%\n"
    text += f"🎮 Compromiso Gamificación: {context.gamification_engagement * 100:.0f}%\n\n"
    text += f"🎭 **Modo Actual:** {context.current_mood.value.title()}\n"
    text += f"⏱️ **Sesión:** {context.session_duration} minutos\n"
    text += f"🔥 **Patrón:** {context.engagement_pattern.replace('_', ' ').title()}"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎯 Ir a Misiones", callback_data="diana:missions_hub")],
        [InlineKeyboardButton(text="📈 Estadísticas Detalladas", callback_data="diana:detailed_stats")],
        [InlineKeyboardButton(text="🏠 Volver", callback_data="diana:refresh")]
    ])
    
    await safe_edit_message(callback, text, keyboard)


async def handle_pro_dashboard_fallback(callback: CallbackQuery, master: DianaMasterInterface):
    """📊 Pro Dashboard Fallback Implementation"""
    user_id = callback.from_user.id
    context = await master.context_engine.analyze_user_context(user_id)
    
    text = "📊 **DASHBOARD PROFESIONAL**\n\n"
    text += "⚙️ **Análisis Avanzado de Usuario**\n\n"
    text += f"🧠 **Patrón de Uso:** {context.engagement_pattern.replace('_', ' ').title()}\n"
    text += f"🎯 **Acciones Recientes:** {len(context.last_actions)} registradas\n"
    text += f"⭐ **Funciones Preferidas:** {', '.join(context.preferred_features[:3])}\n\n"
    text += f"📊 **Métricas Clave:**\n"
    text += f"• Tiempo de sesión: {context.session_duration}min\n"
    text += f"• Score personalización: {context.personalization_score:.2f}\n"
    text += f"• Mood detectado: {context.current_mood.value}\n\n"
    text += "🚀 **Estado del Sistema:** Operativo"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚙️ Configuración Avanzada", callback_data="diana:advanced_settings")],
        [InlineKeyboardButton(text="📈 Exportar Datos", callback_data="diana:export_data")],
        [InlineKeyboardButton(text="🏠 Volver", callback_data="diana:refresh")]
    ])
    
    await safe_edit_message(callback, text, keyboard)


async def handle_explore_mode_fallback(callback: CallbackQuery, master: DianaMasterInterface):
    """🗺️ Explore Mode Fallback Implementation"""
    text = "🗺️ **MODO EXPLORACIÓN**\n\n"
    text += "🌟 Descubre todo lo que Diana tiene para ofrecerte:\n\n"
    text += "🎯 **Misiones Épicas** - Completa desafíos únicos\n"
    text += "🛒 **Tienda Mágica** - Intercambia besitos por tesoros\n"
    text += "📖 **Historia Viva** - Vive aventuras interactivas\n"
    text += "🧠 **Desafíos Trivia** - Pon a prueba tu conocimiento\n"
    text += "🎁 **Regalos Diarios** - Sorpresas cada día\n\n"
    text += "✨ **¿Por dónde quieres empezar tu exploración?**"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎯 Explorar Misiones", callback_data="diana:missions_hub")],
        [InlineKeyboardButton(text="🛒 Explorar Tienda", callback_data="diana:epic_shop")],
        [InlineKeyboardButton(text="📖 Explorar Historia", callback_data="diana:narrative_hub")],
        [InlineKeyboardButton(text="🔄 Volver", callback_data="diana:refresh")]
    ])
    
    await safe_edit_message(callback, text, keyboard)


async def handle_start_journey_fallback(callback: CallbackQuery, master: DianaMasterInterface):
    """🌟 Start Journey Fallback Implementation"""
    text = "🌟 **¡COMIENZA TU AVENTURA!**\n\n"
    text += "Bienvenido al mundo de Diana, donde cada decisión cuenta y cada acción te acerca a descubrir secretos increíbles.\n\n"
    text += "🎯 **Para empezar te recomendamos:**\n\n"
    text += "1️⃣ **Reclama tu regalo diario** para obtener besitos\n"
    text += "2️⃣ **Responde una trivia** para ganar más puntos\n"
    text += "3️⃣ **Explora la historia** para desbloquear misterios\n"
    text += "4️⃣ **Completa misiones** para obtener recompensas épicas\n\n"
    text += "✨ **¿Estás listo para comenzar?**"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎁 Mi Primer Regalo", callback_data="diana:daily_gift")],
        [InlineKeyboardButton(text="🧠 Mi Primera Trivia", callback_data="diana:trivia_challenge")],
        [InlineKeyboardButton(text="📖 Mi Primera Historia", callback_data="diana:narrative_hub")],
        [InlineKeyboardButton(text="🏠 Volver al Inicio", callback_data="diana:refresh")]
    ])
    
    await safe_edit_message(callback, text, keyboard)


async def handle_guided_tour_fallback(callback: CallbackQuery, master: DianaMasterInterface):
    """💫 Guided Tour Fallback Implementation"""
    text = "💫 **TOUR GUIADO DIANA**\n\n"
    text += "Te voy a mostrar todas las funciones increíbles que tengo para ti:\n\n"
    text += "🎭 **Diana Master System**\n"
    text += "Una interfaz inteligente que se adapta a tu estilo de juego\n\n"
    text += "🎯 **Sistema de Misiones**\n"
    text += "Completa desafíos únicos y obtén recompensas épicas\n\n"
    text += "🛒 **Tienda de Besitos**\n"
    text += "Intercambia puntos por objetos especiales y mejoras VIP\n\n"
    text += "📖 **Historia Interactiva**\n"
    text += "Vive una aventura donde tus decisiones importan\n\n"
    text += "**¿Qué te gustaría explorar primero?**"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Ver Dashboard", callback_data="diana:pro_dashboard")],
        [InlineKeyboardButton(text="🗺️ Modo Exploración", callback_data="diana:explore_mode")],
        [InlineKeyboardButton(text="🎯 Comenzar Aventura", callback_data="diana:start_journey")],
        [InlineKeyboardButton(text="🏠 Volver", callback_data="diana:refresh")]
    ])
    
    await safe_edit_message(callback, text, keyboard)


async def handle_collection_fallback(callback: CallbackQuery, master: DianaMasterInterface):
    """🎒 Collection Fallback Implementation"""
    user_id = callback.from_user.id
    context = await master.context_engine.analyze_user_context(user_id)
    
    text = "🎒 **MI COLECCIÓN**\n\n"
    text += "Aquí están todos los tesoros que has conseguido en tu aventura:\n\n"
    text += "📊 **Estadísticas de Colección:**\n"
    text += f"⭐ Nivel de coleccionista: {int(context.personalization_score * 10)}\n"
    text += f"🎯 Progreso narrativo: {context.narrative_progress:.1f}%\n"
    text += f"🏆 Logros desbloqueados: {len(context.preferred_features)}\n\n"
    text += "🔮 **Elementos Únicos:**\n"
    text += "• 🎭 Fragmentos de historia coleccionados\n"
    text += "• 🏆 Logros y medallas obtenidas\n"
    text += "• 💎 Objetos especiales de la tienda\n"
    text += "• 🎁 Recompensas diarias acumuladas\n\n"
    text += "✨ *Continúa jugando para expandir tu colección*"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏆 Ver Logros", callback_data="diana:achievements")],
        [InlineKeyboardButton(text="🛒 Ir a Tienda", callback_data="diana:epic_shop")],
        [InlineKeyboardButton(text="📊 Mi Progreso", callback_data="diana:progress_tracker")],
        [InlineKeyboardButton(text="🏠 Volver", callback_data="diana:refresh")]
    ])
    
    await safe_edit_message(callback, text, keyboard)


async def handle_story_choices_fallback(callback: CallbackQuery, master: DianaMasterInterface):
    """🎭 Story Choices Fallback Implementation"""
    user_id = callback.from_user.id
    context = await master.context_engine.analyze_user_context(user_id)
    
    text = "🎭 **DECISIONES NARRATIVAS**\n\n"
    text += "Tus elecciones han moldeado la historia de Diana. Cada decisión cuenta.\n\n"
    text += f"📊 **Progreso Actual:** {context.narrative_progress:.1f}%\n\n"
    text += "🎯 **Decisiones Importantes Tomadas:**\n"
    text += "• Camino elegido en el Reino Perdido\n"
    text += "• Alianzas forjadas o rechazadas\n"
    text += "• Secretos descubiertos o ignorados\n\n"
    text += "🌟 **Próximas Decisiones:**\n"
    if context.narrative_progress < 50:
        text += "• Encontrar a los aliados perdidos\n"
        text += "• Descubrir el origen del poder de Diana\n"
    else:
        text += "• Confrontar el destino final\n"
        text += "• Determinar el futuro del reino\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📖 Continuar Historia", callback_data="diana:narrative_hub")],
        [InlineKeyboardButton(text="🔍 Revisar Decisiones", callback_data="diana:story_review")],
        [InlineKeyboardButton(text="🎭 Nueva Aventura", callback_data="diana:story_new_chapter")],
        [InlineKeyboardButton(text="🏠 Volver", callback_data="diana:refresh")]
    ])
    
    await safe_edit_message(callback, text, keyboard)


# === FASE 2.3 ADVANCED GAMIFICATION FALLBACK HANDLERS ===

async def handle_achievement_engine_fallback(callback: CallbackQuery, master: DianaMasterInterface):
    """🏆 Achievement Engine Fallback Implementation"""
    user_id = callback.from_user.id
    context = await master.context_engine.analyze_user_context(user_id)
    
    text = "🏆 **MOTOR DE LOGROS**\n\n"
    text += "🎯 *Tu sistema personalizado de logros y reconocimientos*\n\n"
    
    # Mock achievement data
    text += "**📊 RESUMEN DE LOGROS**\n"
    text += f"🏅 Logros desbloqueados: 8/25\n"
    text += f"⭐ Puntos de logros: 1,250\n"
    text += f"🎯 Próximo objetivo: 🧠 Maestro del Conocimiento\n"
    text += f"📈 Progreso: 23/50 trivias correctas\n\n"
    
    text += "**🔥 LOGROS RECIENTES**\n"
    text += "• 🔰 Primera Trivia - Completado\n"
    text += "• 🎯 Racha de 7 días - Completado\n"
    text += "• 📖 Explorador de Historia - En progreso\n\n"
    
    text += "**🎲 PRÓXIMOS DESAFÍOS**\n"
    text += "• 🧠 Responde 50 trivias correctamente\n"
    text += "• 💎 Colecciona 10 objetos únicos\n"
    text += "• 🏆 Alcanza el nivel 5"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏅 Ver Todos los Logros", callback_data="diana:all_achievements")],
        [InlineKeyboardButton(text="🎯 Logros en Progreso", callback_data="diana:progress_achievements")],
        [InlineKeyboardButton(text="🎲 Nuevos Desafíos", callback_data="diana:new_challenges")],
        [InlineKeyboardButton(text="🏠 Volver", callback_data="diana:refresh")]
    ])
    
    await safe_edit_message(callback, text, keyboard)


async def handle_reward_calculator_fallback(callback: CallbackQuery, master: DianaMasterInterface):
    """💰 Reward Calculator Fallback Implementation"""
    user_id = callback.from_user.id
    context = await master.context_engine.analyze_user_context(user_id)
    
    text = "💰 **CALCULADORA DE RECOMPENSAS**\n\n"
    text += "🔬 *Análisis avanzado de tus recompensas y bonificaciones*\n\n"
    
    # Mock calculation
    base_points = 100
    streak_bonus = 1.4 if hasattr(context, 'streak_days') else 1.0
    mood_bonus = 1.2 if context.current_mood == UserMoodState.ACHIEVER else 1.0
    total_multiplier = streak_bonus * mood_bonus
    final_points = int(base_points * total_multiplier)
    
    text += f"**⚡ CÁLCULO ACTUAL**\n"
    text += f"💎 Puntos base: {base_points}\n"
    text += f"🔥 Bonus por racha: {streak_bonus:.1f}x\n"
    text += f"🎭 Bonus por mood: {mood_bonus:.1f}x\n"
    text += f"📈 Multiplicador total: {total_multiplier:.2f}x\n"
    text += f"💰 **TOTAL: {final_points} besitos**\n\n"
    
    text += f"**📊 ANÁLISIS DE EFICIENCIA**\n"
    efficiency = (total_multiplier - 1.0) * 50 + 50
    text += f"⚙️ Eficiencia actual: {efficiency:.1f}%\n"
    text += f"📈 Estado: {'Excelente' if efficiency > 80 else 'Bueno' if efficiency > 60 else 'Mejorable'}\n\n"
    
    text += f"**💡 RECOMENDACIONES**\n"
    text += f"• 🔥 Mantén tu racha diaria para +40% bonus\n"
    text += f"• 🎯 Responde trivias en modo conquista\n"
    text += f"• ⏰ Juega en horas pico para bonus extra"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎲 Simular Trivia", callback_data="diana:simulate_reward")],
        [InlineKeyboardButton(text="📊 Análisis Detallado", callback_data="diana:detailed_calculation")],
        [InlineKeyboardButton(text="💡 Optimizar Recompensas", callback_data="diana:optimize_rewards")],
        [InlineKeyboardButton(text="🏠 Volver", callback_data="diana:refresh")]
    ])
    
    await safe_edit_message(callback, text, keyboard)


async def handle_leaderboard_system_fallback(callback: CallbackQuery, master: DianaMasterInterface):
    """🏆 Leaderboard System Fallback Implementation"""
    user_id = callback.from_user.id
    context = await master.context_engine.analyze_user_context(user_id)
    
    text = "🏆 **SISTEMA DE CLASIFICACIONES**\n\n"
    text += "🌟 *Compite con otros aventureros en múltiples categorías*\n\n"
    
    # Mock user ranking
    user_rank = 15
    user_score = 1250
    
    text += f"**👤 TU POSICIÓN**\n"
    text += f"🏅 Ranking general: #{user_rank}\n"
    text += f"⭐ Puntuación: {user_score:,} puntos\n"
    text += f"🎖️ Tier: 🥈 Plata\n"
    text += f"🔥 Racha: 7 días\n\n"
    
    text += f"**👑 TOP 5 LÍDERES**\n"
    text += f"🥇 Diana_Master: 5,000 pts\n"
    text += f"🥈 Trivia_King: 4,200 pts\n"
    text += f"🥉 Story_Teller: 3,800 pts\n"
    text += f"4️⃣ Quest_Hunter: 3,400 pts\n"
    text += f"5️⃣ Collector_Pro: 3,000 pts\n\n"
    
    text += f"**🏆 COMPETENCIA SEMANAL**\n"
    text += f"👥 Participantes: 156\n"
    text += f"⏰ Tiempo restante: 3 días\n"
    text += f"🎁 Premio: 5,000 besitos\n\n"
    
    text += f"**🎯 TU PROGRESO**\n"
    points_to_top10 = max(0, 2500 - user_score)
    if points_to_top10 > 0:
        text += f"📈 Para top 10: {points_to_top10} puntos más\n"
        text += f"⚡ Con tu racha actual, puedes lograrlo"
    else:
        text += f"🎉 ¡Ya estás en el top 10!\n"
        text += f"🚀 Sigue así para mantener tu posición"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏆 Ranking Completo", callback_data="diana:full_leaderboard")],
        [InlineKeyboardButton(text="📊 Mi Análisis", callback_data="diana:my_stats")],
        [InlineKeyboardButton(text="🎯 Competencias", callback_data="diana:competitions")],
        [InlineKeyboardButton(text="⚡ Ganar Puntos", callback_data="diana:earn_points")],
        [InlineKeyboardButton(text="🏠 Volver", callback_data="diana:refresh")]
    ])
    
    await safe_edit_message(callback, text, keyboard)


async def handle_gamification_settings_fallback(callback: CallbackQuery, master: DianaMasterInterface):
    """⚙️ Gamification Settings Fallback Implementation"""
    user_id = callback.from_user.id
    context = await master.context_engine.analyze_user_context(user_id)
    
    text = "⚙️ **CONFIGURACIÓN DE GAMIFICACIÓN**\n\n"
    text += "🎛️ *Personaliza tu experiencia de juego*\n\n"
    
    text += f"**🎯 CONFIGURACIÓN ACTUAL**\n"
    text += f"🎮 Dificultad: Adaptativa\n"
    text += f"🔔 Notificaciones: Inteligentes\n"
    text += f"💰 Recompensas: Equilibradas\n"
    text += f"🏆 Logros: Habilitados\n\n"
    
    text += f"**🤖 PERFIL DETECTADO**\n"
    if context.current_mood == UserMoodState.OPTIMIZER:
        text += f"⚙️ *Optimizador Avanzado*\n"
        text += f"• Métricas detalladas recomendadas\n"
        text += f"• Enfoque en eficiencia\n"
        text += f"• Dashboard profesional ideal\n\n"
    elif context.current_mood == UserMoodState.ACHIEVER:
        text += f"🏆 *Conquistador Épico*\n"
        text += f"• Desafíos más difíciles\n"
        text += f"• Notificaciones de logros prominentes\n"
        text += f"• Sistema competitivo ideal\n\n"
    else:
        text += f"🌟 *Aventurero Equilibrado*\n"
        text += f"• Configuración balanceada\n"
        text += f"• Experiencia adaptativa\n"
        text += f"• Ajustes automáticos\n\n"
    
    text += f"**🎛️ OPCIONES DISPONIBLES**\n"
    text += f"• 🎯 Ajustar dificultad de desafíos\n"
    text += f"• 🔔 Personalizar notificaciones\n"
    text += f"• 💎 Configurar tipos de recompensas\n"
    text += f"• 🎨 Personalizar interfaz\n"
    text += f"• 👥 Configuración social\n\n"
    
    text += f"**💡 RECOMENDACIÓN IA**\n"
    personalization = context.personalization_score * 100
    text += f"📊 Tu nivel de personalización: {personalization:.0f}%\n"
    if personalization < 50:
        text += f"🚀 Sugerencia: Activar más funciones automáticas"
    else:
        text += f"✅ Tu configuración está bien optimizada"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎯 Ajustar Dificultad", callback_data="diana:adjust_difficulty")],
        [InlineKeyboardButton(text="🔔 Notificaciones", callback_data="diana:notification_settings")],
        [InlineKeyboardButton(text="💎 Recompensas", callback_data="diana:reward_settings")],
        [InlineKeyboardButton(text="🎨 Interfaz", callback_data="diana:ui_settings")],
        [InlineKeyboardButton(text="🔄 Valores por Defecto", callback_data="diana:reset_settings")],
        [InlineKeyboardButton(text="💾 Guardar Cambios", callback_data="diana:save_settings")],
        [InlineKeyboardButton(text="🏠 Volver", callback_data="diana:refresh")]
    ])
    
    await safe_edit_message(callback, text, keyboard)


# === LEGACY HANDLERS (PRESERVED) ===

async def handle_epic_shop(callback: CallbackQuery, master: DianaMasterInterface):
    """🛒 Epic Shop Experience (Legacy - now calls integration)"""
    await handle_diana_shop_integration(callback, master)


    # Get real shop data
    shop_text = "🛒 **TIENDA ÉPICA DE DIANA**\n\n"
    
    try:
        # Get user points
        if master.context_engine._gamification_service:
            points_data = await master.context_engine._gamification_service.get_user_points(user_id)
            user_points = points_data.get('current_points', 0)
            shop_text += f"💰 **Tus besitos:** {user_points:,}\n\n"
        
        # Get available shop items
        if master.context_engine._shop_service:
            categories = await master.context_engine._shop_service.get_categories()
            shop_text += "**🏪 CATEGORÍAS DISPONIBLES:**\n"
            for category in categories:
                items = await master.context_engine._shop_service.get_shop_items(user_id, category=category)
                shop_text += f"• {category.title()}: {len(items)} artículos\n"
            shop_text += "\n"
        
        # Get VIP tariffs if available
        if master.context_engine._tariff_service:
            tariffs = await master.context_engine._tariff_service.get_all_tariffs()
            if tariffs:
                shop_text += "**👑 SUSCRIPCIONES VIP:**\n"
                for tariff in tariffs[:3]:  # Show top 3
                    shop_text += f"• {tariff.name}: ${tariff.price} ({tariff.duration_days} días)\n"
                shop_text += "\n"
        
    except Exception as e:
    
async def handle_missions_hub(callback: CallbackQuery, master: DianaMasterInterface):  
    """🎯 Missions Hub Experience (Legacy - now calls integration)"""
    await handle_diana_missions_integration(callback, master)


async def handle_narrative_hub(callback: CallbackQuery, master: DianaMasterInterface):






async def handle_surprise_feature(callback: CallbackQuery, master: DianaMasterInterface):
    """🔮 Surprise Feature - AI chooses what to show"""
    # TODO: Implement AI-powered surprise feature selection
    surprises = [
        "🎲 **DATO CURIOSO**: ¡Eres el usuario #42 más activo esta semana!",
        "✨ **REGALO SORPRESA**: ¡Has desbloqueado 50 besitos extra!",
        "🔮 **PREDICCIÓN**: Mañana será un gran día para completar misiones",
        "🌟 **SECRETO**: Diana está preparando algo especial para usuarios como tú..."
    ]
    
    import random
    surprise = random.choice(surprises)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Otra Sorpresa", callback_data="diana:surprise_me")],
        [InlineKeyboardButton(text="🏠 Volver", callback_data="diana:refresh")]
    ])
    
    await callback.message.edit_text(surprise, reply_markup=keyboard, parse_mode="Markdown")






async def handle_smart_help(callback: CallbackQuery, master: DianaMasterInterface):
    """❓ Smart Help System"""
    user_id = callback.from_user.id
    context = await master.context_engine.analyze_user_context(user_id)
    
    # Get real missions data
    help_text = "❓ **AYUDA INTELIGENTE DIANA**\n\n"
    
    # Personalized help based on user context
    if context.current_mood == UserMoodState.NEWCOMER:
        help_text += "🌟 **GUÍA PARA NUEVOS AVENTUREROS:**\n\n"
        help_text += "1. 🎁 **Reclama tu regalo diario** para obtener Besitos gratis\n"
    try:
        if master.context_engine._gamification_service:
            missions = await master.context_engine._gamification_service.get_user_missions(user_id)
            points_data = await master.context_engine._gamification_service.get_user_points(user_id)
            
            available_count = len(missions.get('available', []))
            in_progress_count = len(missions.get('in_progress', []))
            completed_count = len(missions.get('completed', []))
            current_points = points_data.get('current_points', 0)
            user_level = master.context_engine._calculate_level_from_points(current_points)
            
            missions_text += f"⭐ **Tu nivel:** {user_level}\n"
            missions_text += f"💰 **Besitos:** {current_points:,}\n\n"
            missions_text += f"**📋 ESTADO DE MISIONES:**\n"
            missions_text += f"🎯 Disponibles: {available_count}\n"
            missions_text += f"⏳ En progreso: {in_progress_count}\n"
            missions_text += f"✅ Completadas: {completed_count}\n\n"
            
            # Show active missions
            if in_progress_count > 0:
                missions_text += "**🔥 MISIONES ACTIVAS:**\n"
                for mission in missions.get('in_progress', [])[:3]:  # Show top 3
                    progress = mission.get('progress_percentage', 0)
                    missions_text += f"• {mission.get('title', 'Misión')}: {progress:.0f}%\n"
                missions_text += "\n"
            
            # Show available missions
            if available_count > 0:
                missions_text += "**⭐ NUEVAS OPORTUNIDADES:**\n"
                for mission in missions.get('available', [])[:2]:  # Show top 2
                    reward = mission.get('rewards', {}).get('points', 0)
                    missions_text += f"• {mission.get('title', 'Misión')}: +{reward} besitos\n"
                missions_text += "\n"
        
    except Exception as e:
        master.logger.error(f"Error getting missions data: {e}")
        missions_text += "✨ *Centro de misiones dinámico*\n\n"
    
        help_text += "2. 🧠 **Responde trivias** para ganar puntos y subir de nivel\n"
        missions_text += "🎮 ¡Aventuras esperándote!"
    
    help_text += "💡 **¿Necesitas ayuda específica?**\n"
    help_text += "El sistema se adapta a tu estilo de juego automáticamente."
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎯 Ir a Misiones", callback_data="diana:missions_hub")],
        [InlineKeyboardButton(text="📊 Ver Mi Progreso", callback_data="diana:progress_tracker")],
        [InlineKeyboardButton(text="🏠 Volver al Inicio", callback_data="diana:refresh")]
    ])
    
    await callback.message.edit_text(help_text, reply_markup=keyboard, parse_mode="Markdown")


# === EXPORT FOR REGISTRATION ===

def register_diana_master_system(dp, services: Dict[str, Any]):
    """🏛️ Register the complete Diana Master System"""
    
    # Get real narrative data
    # Initialize the system
    initialize_diana_master(services)
    try:
        if master.context_engine._narrative_service:
            lore_pieces = await master.context_engine._narrative_service.get_user_lore_pieces(user_id)
            current_fragment = await master.context_engine._narrative_service.get_user_fragment(user_id)
            
            narrative_text += f"🔍 **Pistas recolectadas:** {len(lore_pieces)}\n"
            
            if current_fragment:
                narrative_text += f"📍 **Ubicación actual:** {current_fragment.get('title', 'Fragmento Actual')}\n"
                narrative_text += f"🎭 **Personaje:** {current_fragment.get('character', 'Diana')}\n\n"
                
                # Show current fragment text (truncated)
                fragment_text = current_fragment.get('text', '')
                if len(fragment_text) > 100:
                    fragment_text = fragment_text[:100] + "..."
                narrative_text += f"*\"{fragment_text}\"*\n\n"
                
                # Show available choices
                choices = current_fragment.get('choices', [])
                if choices:
                    narrative_text += f"**🎭 DECISIONES DISPONIBLES:** {len(choices)}\n"
                    for i, choice in enumerate(choices[:2], 1):  # Show first 2
                        narrative_text += f"{i}. {choice.get('text', 'Opción')}\n"
                    if len(choices) > 2:
                        narrative_text += f"... y {len(choices) - 2} más\n"
                    narrative_text += "\n"
            else:
                narrative_text += "🌟 **Estado:** Listo para comenzar tu aventura\n\n"
        
    except Exception as e:
        master.logger.error(f"Error getting narrative data: {e}")
        narrative_text += "✨ *Tu historia personal se desarrolla aquí*\n\n"
    
    
    # Register the router