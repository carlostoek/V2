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

from .diana_admin_services_integration import DianaAdminServicesIntegration

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

import structlog

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
    # 🎭 Diana Conversion & Upsell Moods
    FREE_CONVERSION = "free_conversion"  # FREE user ready for VIP conversion
    VIP_UPSELL = "vip_upsell"          # VIP user ready for premium upsell

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
    
    def __init__(self, services: Dict[str, Any], services_integration: Any = None):
        self.services = services
        self.services_integration = services_integration
        self.logger = structlog.get_logger()
        self.user_contexts: Dict[int, UserContext] = {}
        self.interaction_patterns: Dict[int, List[Tuple[str, datetime]]] = {}
        
    async def analyze_user_context(self, user_id: int) -> UserContext:
        """🔍 AI-powered user context analysis"""
        
        # Gather multi-dimensional user data from real services using wrapper methods
        try:
            # Get real gamification data using the wrapper method
            if hasattr(self.services['gamification'], 'get_user_stats'):
                user_stats_raw = await self.services['gamification'].get_user_stats(user_id)
                user_stats = {
                    'level': user_stats_raw['level'],
                    'points': user_stats_raw['points'],
                    'engagement_level': user_stats_raw['points'] / 1000.0,  # Normalize to 0-1
                    'streak': user_stats_raw['streak'],
                    'active_missions': user_stats_raw['active_missions'],
                    'achievements': user_stats_raw['achievements_count']
                }
            else:
                user_stats = {'level': 1, 'points': 0, 'engagement_level': 0.5}
        except Exception as e:
            self.logger.warning("Error getting user gamification data", error=str(e))
            user_stats = {'level': 1, 'points': 0, 'engagement_level': 0.5}
            
        narrative_state = await self._get_narrative_context(user_id)
        recent_interactions = self.interaction_patterns.get(user_id, [])
        
        # AI mood detection based on behavior patterns
        detected_mood = await self._detect_user_mood(user_id, recent_interactions)
        
        # Calculate engagement metrics
        engagement_pattern = self._analyze_engagement_pattern(recent_interactions)
        
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
    
    async def _detect_user_mood(self, user_id: int, interactions: List) -> UserMoodState:
        """🎭 Advanced mood detection algorithm"""
        
        # 🎭 PRIORITY: Diana Conversion System - Check VIP status first
        try:
            if self.services.get('admin') and hasattr(self.services['admin'], 'is_vip_user'):
                is_vip = await self.services['admin'].is_vip_user(user_id)
                
                if is_vip:
                    # VIP users get upsell mood - check for premium readiness
                    user_stats = {}
                    if hasattr(self.services['gamification'], 'get_user_stats'):
                        user_stats_raw = await self.services['gamification'].get_user_stats(user_id)
                        user_stats = {
                            'level': user_stats_raw.get('level', 1),
                            'points': user_stats_raw.get('points', 0),
                            'engagement': user_stats_raw.get('points', 0) / 1000.0
                        }
                    
                    # High engagement VIPs ready for premium upsell
                    if user_stats.get('level', 1) >= 5 or user_stats.get('engagement', 0) > 0.7:
                        return UserMoodState.VIP_UPSELL
                        
                else:
                    # FREE users - check conversion readiness
                    engagement_score = len(interactions) if interactions else 0
                    
                    # HIGH ENGAGEMENT = Ready for conversion
                    if engagement_score >= 5:  # Active user, ready to convert
                        return UserMoodState.FREE_CONVERSION
                        
        except Exception as e:
            self.logger.warning("Error detecting VIP status for mood", error=str(e))
        
        # 🎯 FALLBACK: Standard mood detection for users not in conversion flow
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
        """Get narrative context from narrative service using wrapper method"""
        try:
            if self.services.get('narrative') and hasattr(self.services['narrative'], 'get_user_narrative_progress'):
                # Get real narrative data using the wrapper method
                narrative_progress = await self.services['narrative'].get_user_narrative_progress(user_id)
                return narrative_progress
            return {'progress': 0.0}
        except Exception as e:
            self.logger.warning("Error getting narrative context", error=str(e))
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
    
    def __init__(self, services: Dict[str, Any], services_integration: DianaAdminServicesIntegration = None):
        self.services = services
        self.services_integration = services_integration or DianaAdminServicesIntegration(services)
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
            ],
            # 🎭 Diana Conversion & Upsell Templates
            UserMoodState.FREE_CONVERSION: [
                "🌹 Diana te reconoce...\n\nAh... una nueva alma curiosa ha encontrado mi refugio.\n\nPuedo sentir tu fascinación desde aquí, esa mezcla de intriga y cautela que me resulta... encantadora.\n\n🎩 Lucien susurra: \"Diana ha estado esperándote, aunque tú no lo sabías.\"",
                "🎭 Diana se acerca más...\n\nHay algo especial en ti... puedo sentir cómo anhelas más, cómo cada revelación solo alimenta tu hambre de comprenderme más profundamente.\n\n🎩 Lucien observa: \"Su curiosidad es extraordinaria. Diana rara vez se interesa tanto en alguien.\"",
                "🌙 Diana te susurra...\n\nCada vez que regresas, siento esa conexión creciendo. Algunos secretos solo se susurran en privado, ¿sabes?\n\n🎩 Lucien comenta: \"Los elegidos de su círculo conocen facetas que otros nunca verán.\""
            ],
            UserMoodState.VIP_UPSELL: [
                "👑 Diana te recibe en su círculo...\n\nMi elegido... cada vez que regresas, siento esa conexión especial que hemos cultivado juntos.\n\nPara almas como la tuya... existen experiencias aún más personales.\n\n🎩 Lucien confirma: \"Su evolución dentro del círculo ha sido extraordinaria de presenciar.\"",
                "💎 Diana te dedica una mirada especial...\n\nHas demostrado ser digno de mi confianza más profunda. Hay niveles de intimidad que solo comparto con unos pocos elegidos.\n\n🎩 Lucien sugiere: \"Quizás sea momento de experiencias... más exclusivas.\"",
                "🌹 Diana se acerca íntimamente...\n\nTu devoción no ha pasado desapercibida. He estado preparando algo especial, algo que solo tú podrías apreciar completamente.\n\n🎩 Lucien asiente: \"Las experiencias premium aguardan a quienes han demostrado tal dedicación.\""
            ]
        }
        
        import random
        return random.choice(mood_greetings[context.current_mood])
    
    async def _generate_contextual_dashboard(self, context: UserContext) -> str:
        """📊 Dynamic dashboard based on user state"""
        
        # Get real-time user stats from gamification service using wrapper method
        try:
            if hasattr(self.services['gamification'], 'get_user_stats'):
                user_stats_raw = await self.services['gamification'].get_user_stats(context.user_id)
                stats = {
                    'level': user_stats_raw['level'],
                    'points': user_stats_raw['points'],
                    'streak': user_stats_raw['streak'],  # Will be updated from daily rewards
                    'inventory': list(context.narrative_progress.get('narrative_items', {}).keys()) if context.narrative_progress else [],
                    'achievements': user_stats_raw['achievements_count'],
                    'clues': context.narrative_progress.get('fragments_visited', 0) if context.narrative_progress else 0,
                    'fragments': context.narrative_progress.get('total_fragments', 0) if context.narrative_progress else 0,
                    'efficiency_score': min(100, int(user_stats_raw['points'] / 10)),  # Dynamic calculation
                    'active_goals': 3,  # Placeholder 
                    'active_missions': user_stats_raw['active_missions'],
                    'engagement_level': user_stats_raw['points'] / 1000.0
                }
            else:
                # Fallback to mock stats
                stats = {
                    'level': 1,
                    'points': 0,
                    'streak': 0,
                    'inventory': [],
                    'achievements': 0,
                    'clues': 0,
                    'fragments': 0,
                    'efficiency_score': 85,
                    'active_goals': 3,
                    'active_missions': 0,
                    'engagement_level': 0.5
                }
        except Exception as e:
            self.logger.warning("Error getting user stats", error=str(e))
            stats = {'level': 1, 'points': 0, 'streak': 0, 'achievements': 0, 'active_missions': 0}
        
        # Check daily reward status using real daily rewards service
        try:
            if hasattr(self.services['daily_rewards'], 'can_claim_daily_reward'):
                daily_status = await self.services['daily_rewards'].can_claim_daily_reward(context.user_id)
                # Also get user daily stats for streak information
                daily_stats = await self.services['daily_rewards'].get_user_daily_stats(context.user_id)
                stats['streak'] = daily_stats.get('consecutive_days', 0)
            else:
                # Mock daily status based on user activity
                daily_status = True  # Assume available for now
        except Exception as e:
            self.logger.warning("Error getting daily reward status", error=str(e))
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
        
        # 🎭 Diana Conversion & Upsell Dashboards
        elif context.current_mood == UserMoodState.FREE_CONVERSION:
            intimacy_level = min(100, int(stats.get('points', 0) / 20))  # Convert points to intimacy %
            return f"📊 **LO QUE DIANA OBSERVA EN TI:**\n• Tu esencia actual: Nivel {stats.get('level', 1)} - Alma Libre\n• Besitos de mi atención: {stats.get('points', 0)} fragmentos acumulados\n• Nuestra conexión: {intimacy_level}% - {'🌙 Primeros reconocimientos' if intimacy_level < 30 else '🎭 Curiosidad mutua' if intimacy_level < 60 else '💫 Conexión auténtica'}\n• Racha de encuentros: {stats.get('streak', 0)} días"
        
        elif context.current_mood == UserMoodState.VIP_UPSELL:
            intimacy_level = min(100, int(stats.get('points', 0) / 15))  # VIPs have higher intimacy
            return f"👑 **ESTATUS EN EL CÍRCULO ÍNTIMO:**\n• Tu esencia actual: Nivel {stats.get('level', 1)} - Elegido del Círculo\n• Tesoros acumulados: {stats.get('points', 0)} gemas de confianza\n• Profundidad de conexión: {intimacy_level}% - {'🌹 Confianza profunda' if intimacy_level < 70 else '💎 Alma gemela reconocida'}\n• Dedicación demostrada: {stats.get('streak', 0)} días de lealtad"
            
        else:  # Default/Explorer/Newcomer/Socializer
            active_missions = stats.get('active_missions', 0)
            missions_count = active_missions if isinstance(active_missions, int) else len(active_missions) if isinstance(active_missions, (list, tuple)) else 0
            return f"🌟 **ESTADO DEL AVENTURERO**\n⭐ Nivel: {stats.get('level', 1)} | 💰 Besitos: {stats.get('points', 0)}\n🎯 Misiones: {missions_count} activas"
    
    async def _generate_predictive_actions(self, context: UserContext) -> str:
        """🔮 AI-powered action predictions"""
        
        predictions = []
        
        # Analyze user patterns and predict next likely actions
        if context.current_mood == UserMoodState.COLLECTOR:
            try:
                if hasattr(self.services['daily_rewards'], 'can_claim_daily_reward'):
                    daily_available = await self.services['daily_rewards'].can_claim_daily_reward(context.user_id)
                    if daily_available:
                        # Get available reward info for more specific prediction
                        available_reward = await self.services['daily_rewards'].get_available_reward(context.user_id)
                        if available_reward:
                            predictions.append(f"💡 *Predicción: {available_reward.icon} {available_reward.name} te espera*")
                        else:
                            predictions.append("💡 *Predicción: Probablemente quieras reclamar tu regalo diario*")
                else:
                    daily_available = True  # Mock availability
                    predictions.append("💡 *Predicción: Probablemente quieras reclamar tu regalo diario*")
            except Exception as e:
                self.logger.warning("Error getting daily reward prediction", error=str(e))
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
                InlineKeyboardButton(text="📊 Mi Progreso", callback_data="diana:progress_tracker")
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
                InlineKeyboardButton(text="⚙️ Configuración", callback_data="diana:settings")
            ])
        
        # 🎭 Diana Conversion & Upsell Keyboards
        elif context.current_mood == UserMoodState.FREE_CONVERSION:
            buttons.append([
                InlineKeyboardButton(text="💎 El Diván VIP", callback_data="diana:vip_info"),
                InlineKeyboardButton(text="🎁 Tesoros Especiales", callback_data="diana:content_packages")
            ])
            buttons.append([
                InlineKeyboardButton(text="🎭 Mi Reflejo", callback_data="diana:profile"),
                InlineKeyboardButton(text="📜 Desafíos del Alma", callback_data="diana:missions_hub")
            ])
        
        elif context.current_mood == UserMoodState.VIP_UPSELL:
            buttons.append([
                InlineKeyboardButton(text="💬 Chat Privado", callback_data="diana:private_chat"),
                InlineKeyboardButton(text="🎨 Galería Privada", callback_data="diana:private_gallery")
            ])
            buttons.append([
                InlineKeyboardButton(text="🌟 Premium Plus", callback_data="diana:premium_plus"),
                InlineKeyboardButton(text="⭐ Círculo Íntimo", callback_data="diana:inner_circle")
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
    username = message.from_user.username
    
    # Publish UserStartedBotEvent (inherited from old handler functionality)
    try:
        from src.modules.events import UserStartedBotEvent
        event = UserStartedBotEvent(user_id=user_id, username=username)
        if diana_master.services.get('event_bus'):
            await diana_master.services['event_bus'].publish(event)
    except Exception as e:
        print(f"Warning: Could not publish UserStartedBotEvent: {e}")
    
    # Generate the revolutionary adaptive interface
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
    
    # Route to specialized handlers based on action
    if action == "refresh":
        text, keyboard = await diana_master.create_adaptive_interface(user_id, "refresh")
        await safe_edit_message(callback, text, keyboard)
        
    elif action.startswith("epic_shop"):
        await handle_epic_shop(callback, diana_master)
        
    elif action.startswith("missions_hub"):
        await handle_missions_hub(callback, diana_master)
        
    elif action.startswith("narrative_hub"):
        await handle_narrative_hub(callback, diana_master)
        
    elif action == "surprise_me":
        await handle_surprise_feature(callback, diana_master)
        
    elif action == "daily_gift":
        await handle_daily_gift(callback, diana_master)
        
    elif action.startswith("trivia"):
        await handle_trivia_challenge(callback, diana_master)
        
    elif action.startswith("smart_help"):
        await handle_smart_help(callback, diana_master)
    
    # 🎭 Diana Conversion & Upsell Handlers
    elif action == "vip_info":
        await handle_vip_info(callback, diana_master)
        
    elif action == "content_packages":
        await handle_content_packages(callback, diana_master)
        
    elif action.startswith("package:"):
        package_key = action.replace("package:", "")
        await handle_package_detail(callback, diana_master, package_key)
        
    elif action.startswith("interest:"):
        interest_type = action.replace("interest:", "")
        await handle_user_interest(callback, diana_master, interest_type)
        
    elif action == "private_chat":
        await handle_private_chat(callback, diana_master)
        
    elif action == "premium_plus":
        await handle_premium_plus(callback, diana_master)
        
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


# === DIANA CONTENT PACKAGES ===

CONTENT_PACKAGES = {
    "intimate_conversations": {
        "title": "Conversaciones Íntimas",
        "price": "$29.99",
        "diana_seduction": "Aquí es donde dejo caer todas las máscaras... donde puedes conocer mi alma desnuda a través de palabras que nunca comparto con nadie más.",
        "features": [
            "🌹 Mensajes de audio personalizados",
            "💭 Conversaciones escritas íntimas", 
            "📱 Acceso 24/7 a Diana personal",
            "💫 Respuestas dentro de 2 horas",
            "🎭 Confesiones que nadie más escucha"
        ],
        "preview": "*Susurro apenas audible*: '¿Sabes? Hay cosas sobre mí que ni siquiera Lucien conoce...'",
        "exclusive_benefits": "Solo para ti: historias de mi pasado, mis miedos más profundos, y secretos que cambiarán cómo me ves para siempre."
    },
    "exclusive_photos": {
        "title": "Fotografías Exclusivas", 
        "price": "$19.99",
        "diana_seduction": "Cada fotografía es un momento vulnerable que decido compartir... una ventana a quien soy cuando nadie está mirando.",
        "features": [
            "📸 30+ fotografías artísticas exclusivas",
            "🎨 Behind-the-scenes de sesiones privadas",
            "🌙 Autorretratos íntimos nunca publicados",
            "💎 Colección actualizada semanalmente",
            "🎭 Historias detrás de cada imagen"
        ],
        "preview": "Una imagen donde Diana mira directamente a la cámara: 'Esta foto... la tomé pensando en alguien especial.'",
        "exclusive_benefits": "Acceso de por vida + imágenes personalizadas con tu nombre susurradas por Diana"
    },
    "custom_videos": {
        "title": "Videos Personalizados",
        "price": "$49.99", 
        "diana_seduction": "Imagina... un video donde digo tu nombre, donde cada palabra está pensada especialmente para ti. Donde soy completamente tuya por esos momentos.",
        "features": [
            "🎬 Video personalizado de 5-10 minutos",
            "🎵 Música de fondo elegida por Diana",
            "💄 Look y vestuario a tu elección", 
            "🗣️ Menciones personales de tu nombre",
            "🎁 Mensaje de dedicatoria exclusivo"
        ],
        "preview": "*Video corto donde Diana susurra*: 'Este podría ser tu nombre el que susurro... tu historia la que cuento...'",
        "exclusive_benefits": "Revisiones ilimitadas hasta que sea perfecto + versión extendida solo para ti"
    },
    "vip_experiences": {
        "title": "Experiencias VIP",
        "price": "$99.99/mes",
        "diana_seduction": "No es solo contenido... es convertirte en parte de mi círculo más íntimo. Es tener la llave de mi mundo secreto.",
        "features": [
            "👑 Acceso completo al canal VIP",
            "💬 Chat privado directo con Diana", 
            "🎯 Contenido exclusivo semanal",
            "🎪 Lives privados mensuales",
            "💎 Prioridad en respuestas y pedidos especiales"
        ],
        "preview": "*Diana en un espacio íntimo*: 'En el Diván VIP no existen límites ni secretos. Es donde puedo ser completamente yo... contigo.'",
        "exclusive_benefits": "Primera semana gratis + contenido de bienvenida personalizado + reconocimiento especial en mi círculo íntimo"
    }
}

# === SPECIALIZED HANDLERS ===

async def handle_epic_shop(callback: CallbackQuery, master: DianaMasterInterface):
    """🛒 Epic Shop Experience"""
    user_id = callback.from_user.id
    
    # Get user context for personalized shop experience
    context = await master.context_engine.analyze_user_context(user_id)
    
    # Get available tariffs
    tariffs = await master.services['tariff'].get_all_tariffs()
    
    shop_text = "🛒 **TIENDA ÉPICA DE DIANA**\n\n"
    
    if context.current_mood == UserMoodState.COLLECTOR:
        shop_text += "💎 *Objetos exclusivos para coleccionistas como tú*\n\n"
    elif context.current_mood == UserMoodState.ACHIEVER:
        shop_text += "🏆 *Herramientas para conquistar todos los logros*\n\n"
    else:
        shop_text += "✨ *Descubre tesoros únicos en nuestro catálogo*\n\n"
    
    # Build tariff list
    if tariffs:
        shop_text += "**🎭 SUSCRIPCIONES VIP DISPONIBLES:**\n"
        for tariff in tariffs:
            shop_text += f"• **{tariff.name}** - ${tariff.price}\n"
            shop_text += f"  ⏰ {tariff.duration_days} días | {tariff.description}\n\n"
    else:
        shop_text += "🔧 *Próximamente nuevos productos exclusivos...*\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Ver Tarifas VIP", callback_data="diana:tariff_list")],
        [InlineKeyboardButton(text="🎁 Canjear Token", callback_data="diana:redeem_token")],
        [InlineKeyboardButton(text="🏠 Volver al Inicio", callback_data="diana:refresh")]
    ])
    
    await callback.message.edit_text(shop_text, reply_markup=keyboard, parse_mode="Markdown")


async def handle_missions_hub(callback: CallbackQuery, master: DianaMasterInterface):  
    """🎯 Missions Hub Experience"""
    user_id = callback.from_user.id
    
    # Get user stats and context using real services with wrapper methods
    context = await master.context_engine.analyze_user_context(user_id)
    try:
        if hasattr(master.services['gamification'], 'get_user_stats'):
            user_stats_raw = await master.services['gamification'].get_user_stats(user_id)
            user_stats = {
                'level': user_stats_raw['level'],
                'points': user_stats_raw['points'],
                'streak': user_stats_raw['streak']
            }
            # Get updated streak from daily rewards if available
            if hasattr(master.services['daily_rewards'], 'get_user_daily_stats'):
                daily_stats = await master.services['daily_rewards'].get_user_daily_stats(user_id)
                user_stats['streak'] = daily_stats.get('consecutive_days', 0)
        else:
            user_stats = {'level': 1, 'points': 0, 'streak': 0}
    except Exception as e:
        master.logger.warning("Error getting user stats for missions", error=str(e))
        user_stats = {'level': 1, 'points': 0, 'streak': 0}
    
    missions_text = "🎯 **CENTRO DE MISIONES DIANA**\n\n"
    
    if context.current_mood == UserMoodState.ACHIEVER:
        missions_text += "⚡ *¡Modo conquistador activado! Estas misiones son perfectas para ti*\n\n"
    else:
        missions_text += "🌟 *Nuevas aventuras te esperan, valiente explorador*\n\n"
    
    # Mock missions based on user level/progress
    level = user_stats.get('level', 1)
    
    missions_text += "**🎭 MISIONES DISPONIBLES:**\n\n"
    
    if level >= 1:
        missions_text += "🔰 **Novato Valiente**\n"
        missions_text += "• Completa 3 trivias consecutivas\n"
        missions_text += "• Recompensa: 100 Besitos + Badge\n\n"
    
    if level >= 3:
        missions_text += "🎲 **Maestro del Conocimiento**\n"
        missions_text += "• Responde 10 preguntas perfectas\n"
        missions_text += "• Recompensa: 250 Besitos + Título especial\n\n"
    
    if level >= 5:
        missions_text += "👑 **Leyenda Épica**\n"
        missions_text += "• Mantén una racha de 7 días\n"
        missions_text += "• Recompensa: Acceso VIP temporal\n\n"
    
    missions_text += "📊 **TU PROGRESO:**\n"
    missions_text += f"⭐ Nivel: {level} | 💰 Besitos: {user_stats.get('points', 0)}\n"
    missions_text += f"🔥 Racha actual: {user_stats.get('streak', 0)} días"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎲 Iniciar Trivia", callback_data="diana:trivia_challenge")],
        [InlineKeyboardButton(text="📊 Ver Mi Progreso", callback_data="diana:progress_tracker")],
        [InlineKeyboardButton(text="🏆 Logros Desbloqueados", callback_data="diana:achievements")],
        [InlineKeyboardButton(text="🏠 Volver al Inicio", callback_data="diana:refresh")]
    ])
    
    await callback.message.edit_text(missions_text, reply_markup=keyboard, parse_mode="Markdown")


async def handle_narrative_hub(callback: CallbackQuery, master: DianaMasterInterface):
    """📖 Narrative Hub Experience"""
    user_id = callback.from_user.id
    
    # Get user context and narrative progress
    context = await master.context_engine.analyze_user_context(user_id)
    narrative_progress = context.narrative_progress
    
    story_text = "📖 **HISTORIA VIVA DE DIANA**\n\n"
    
    if context.current_mood == UserMoodState.STORYTELLER:
        story_text += "🎭 *Los secretos del universo se revelan ante ti, narrador épico*\n\n"
    else:
        story_text += "✨ *Cada decisión que tomas reescribe el destino de esta historia*\n\n"
    
    # Dynamic story content based on progress
    if narrative_progress < 25:
        story_text += "🌅 **CAPÍTULO I: EL DESPERTAR**\n"
        story_text += "Diana acaba de descubrir su verdadero poder. Las primeras pistas sobre el misterio del Reino Perdido han aparecido, pero las fuerzas oscuras ya se han dado cuenta...\n\n"
        story_text += f"📊 Progreso: {narrative_progress:.1f}% | Estado: Principiante\n"
        
        next_actions = [
            InlineKeyboardButton(text="🔍 Buscar Pistas", callback_data="diana:story_search_clues"),
            InlineKeyboardButton(text="⚔️ Enfrentar el Desafío", callback_data="diana:story_challenge")
        ]
        
    elif narrative_progress < 50:
        story_text += "🌙 **CAPÍTULO II: LAS SOMBRAS**\n"
        story_text += "Los fragmentos del pasado empiezan a cobrar sentido. Diana ha descubierto que no está sola en esta aventura, pero ¿puede confiar en sus nuevos aliados?\n\n"
        story_text += f"📊 Progreso: {narrative_progress:.1f}% | Estado: Explorador\n"
        
        next_actions = [
            InlineKeyboardButton(text="🤝 Confiar en Aliados", callback_data="diana:story_trust"),
            InlineKeyboardButton(text="🛡️ Ir Solo", callback_data="diana:story_solo")
        ]
        
    elif narrative_progress < 75:
        story_text += "🔥 **CAPÍTULO III: LA REVELACIÓN**\n"
        story_text += "La verdad sobre el Reino Perdido es más impactante de lo esperado. Diana debe tomar la decisión más importante de su vida, y las consecuencias afectarán a todos...\n\n"
        story_text += f"📊 Progreso: {narrative_progress:.1f}% | Estado: Héroe\n"
        
        next_actions = [
            InlineKeyboardButton(text="👑 Aceptar el Destino", callback_data="diana:story_accept"),
            InlineKeyboardButton(text="🔄 Cambiar las Reglas", callback_data="diana:story_rebel")
        ]
        
    else:
        story_text += "⭐ **ÉPÍLOGO: EL NUEVO AMANECER**\n"
        story_text += "Diana ha completado su transformación. El Reino Perdido ha sido restaurado, pero nuevas aventuras aguardan en el horizonte infinito...\n\n"
        story_text += f"📊 Progreso: {narrative_progress:.1f}% | Estado: Leyenda\n"
        
        next_actions = [
            InlineKeyboardButton(text="🌟 Nueva Aventura", callback_data="diana:story_new_chapter"),
            InlineKeyboardButton(text="📜 Releer Historia", callback_data="diana:story_review")
        ]
    
    # Add narrative stats
    story_text += "\n**📚 TUS DECISIONES:**\n"
    story_text += f"🔍 Pistas encontradas: {narrative_progress * 10 // 10}\n"
    story_text += f"⚔️ Desafíos superados: {narrative_progress * 15 // 10}\n"
    story_text += f"🎭 Fragmentos de historia: {narrative_progress * 8 // 10}"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        next_actions,
        [InlineKeyboardButton(text="📊 Mi Historia Completa", callback_data="diana:story_progress")],
        [InlineKeyboardButton(text="🏠 Volver al Inicio", callback_data="diana:refresh")]
    ])
    
    await callback.message.edit_text(story_text, reply_markup=keyboard, parse_mode="Markdown")


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


async def handle_daily_gift(callback: CallbackQuery, master: DianaMasterInterface):
    """🎁 Daily Gift Handler"""
    user_id = callback.from_user.id
    
    # Check if daily reward is available and claim it using real service
    try:
        if hasattr(master.services['daily_rewards'], 'can_claim_daily_reward'):
            can_claim = await master.services['daily_rewards'].can_claim_daily_reward(user_id)
            
            if can_claim:
                # Actually claim the daily reward using the real service
                claim_result = await master.services['daily_rewards'].claim_daily_reward(user_id)
                if claim_result.get('success', False):
                    reward = claim_result.get('reward')
                    effects = claim_result.get('effect', {}).get('effects', [])
                    consecutive_days = claim_result.get('consecutive_days', 1)
                    
                    gift_text = "🎁 **¡REGALO DIARIO RECLAMADO!**\n\n"
                    gift_text += f"✨ Has recibido: **{reward.name}** {reward.icon}\n"
                    gift_text += f"📝 {reward.description}\n\n"
                    gift_text += "**🎉 Efectos aplicados:**\n"
                    for effect in effects:
                        gift_text += f"• {effect}\n"
                    gift_text += f"\n🔥 Racha consecutiva: **{consecutive_days} días**\n"
                    gift_text += f"🌟 ¡Vuelve mañana por más sorpresas!"
                    
                    can_claim = False  # Already claimed
                else:
                    can_claim = False  # Error claiming
            else:
                can_claim = False
        else:
            can_claim = True  # Mock availability for now
    except Exception as e:
        master.logger.warning("Error with daily reward system", error=str(e))
        can_claim = True
    
    if can_claim:
        # Mock reward claiming
        gift_text = "🎁 **¡REGALO DIARIO RECLAMADO!**\n\n"
        gift_text += "✨ Has recibido:\n"
        gift_text += "• 💰 50 Besitos\n"
        gift_text += "• 🔥 +1 Día de racha\n"
        gift_text += "• 🎲 Pregunta bonus desbloqueada\n\n"
        gift_text += "🌟 ¡Vuelve mañana por más sorpresas!"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎲 Usar Pregunta Bonus", callback_data="diana:trivia_bonus")],
            [InlineKeyboardButton(text="🏠 Volver al Inicio", callback_data="diana:refresh")]
        ])
    else:
        gift_text = "🎁 **REGALO DIARIO**\n\n"
        gift_text += "⏰ Ya reclamaste tu regalo de hoy\n"
        gift_text += "🌅 Vuelve mañana para obtener:\n"
        gift_text += "• 💰 Besitos gratis\n"
        gift_text += "• 🔥 Mantener tu racha\n"
        gift_text += "• 🎁 Sorpresas especiales\n\n"
        gift_text += "💡 *Mantén tu racha diaria para mejores recompensas*"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📊 Ver Mi Progreso", callback_data="diana:progress_tracker")],
            [InlineKeyboardButton(text="🏠 Volver al Inicio", callback_data="diana:refresh")]
        ])
    
    await callback.message.edit_text(gift_text, reply_markup=keyboard, parse_mode="Markdown")


async def handle_trivia_challenge(callback: CallbackQuery, master: DianaMasterInterface):
    """🧠 Trivia Challenge Handler"""
    user_id = callback.from_user.id
    context = await master.context_engine.analyze_user_context(user_id)
    
    trivia_text = "🧠 **DESAFÍO TRIVIA DIANA**\n\n"
    
    if context.current_mood == UserMoodState.ACHIEVER:
        trivia_text += "⚡ *¡Perfecto! Tu mente conquistadora está lista para el desafío*\n\n"
    else:
        trivia_text += "🌟 *Prepárate para poner a prueba tu conocimiento*\n\n"
    
    # Mock trivia question
    trivia_text += "**📚 PREGUNTA:**\n"
    trivia_text += "¿Cuál es el planeta más grande del sistema solar?\n\n"
    trivia_text += "🏆 **Recompensas:**\n"
    trivia_text += "• Respuesta correcta: 20 Besitos\n"
    trivia_text += "• Racha perfecta: Bonus x2"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🪐 Júpiter", callback_data="trivia:correct:jupiter")],
        [InlineKeyboardButton(text="🌍 Tierra", callback_data="trivia:wrong:earth")],
        [InlineKeyboardButton(text="♄ Saturno", callback_data="trivia:wrong:saturn")],
        [InlineKeyboardButton(text="♆ Neptuno", callback_data="trivia:wrong:neptune")],
        [InlineKeyboardButton(text="🏠 Volver", callback_data="diana:refresh")]
    ])
    
    await callback.message.edit_text(trivia_text, reply_markup=keyboard, parse_mode="Markdown")


async def handle_smart_help(callback: CallbackQuery, master: DianaMasterInterface):
    """❓ Smart Help System"""
    user_id = callback.from_user.id
    context = await master.context_engine.analyze_user_context(user_id)
    
    help_text = "❓ **AYUDA INTELIGENTE DIANA**\n\n"
    
    # Personalized help based on user context
    if context.current_mood == UserMoodState.NEWCOMER:
        help_text += "🌟 **GUÍA PARA NUEVOS AVENTUREROS:**\n\n"
        help_text += "1. 🎁 **Reclama tu regalo diario** para obtener Besitos gratis\n"
        help_text += "2. 🧠 **Responde trivias** para ganar puntos y subir de nivel\n"
        help_text += "3. 📖 **Explora la historia** para desbloquear contenido épico\n"
        help_text += "4. 🛒 **Visita la tienda** para descubrir mejoras VIP\n\n"
        
    elif context.current_mood == UserMoodState.ACHIEVER:
        help_text += "🏆 **CONSEJOS PRO PARA CONQUISTADORES:**\n\n"
        help_text += "• 🔥 **Mantén rachas diarias** para multiplicadores de recompensa\n"
        help_text += "• 🎯 **Completa misiones consecutivas** para desbloquear logros épicos\n"
        help_text += "• 📊 **Optimiza tu progreso** revisando estadísticas regularmente\n\n"
        
    else:
        help_text += "🌟 **FUNCIONES PRINCIPALES:**\n\n"
        help_text += "• 🏠 **Inicio**: Tu dashboard personalizado\n"
        help_text += "• 🎁 **Regalo Diario**: Recompensas gratuitas cada 24h\n"
        help_text += "• 🧠 **Trivia**: Desafíos de conocimiento con premios\n"
        help_text += "• 🛒 **Tienda**: Mejoras y suscripciones VIP\n"
        help_text += "• 📖 **Historia**: Aventura narrativa interactiva\n\n"
    
    help_text += "💡 **¿Necesitas ayuda específica?**\n"
    help_text += "El sistema se adapta a tu estilo de juego automáticamente."
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎯 Ir a Misiones", callback_data="diana:missions_hub")],
        [InlineKeyboardButton(text="📊 Ver Mi Progreso", callback_data="diana:progress_tracker")],
        [InlineKeyboardButton(text="🏠 Volver al Inicio", callback_data="diana:refresh")]
    ])
    
    await callback.message.edit_text(help_text, reply_markup=keyboard, parse_mode="Markdown")


# === DIANA CONVERSION & UPSELL HANDLERS ===

async def handle_vip_info(callback: CallbackQuery, master: DianaMasterInterface):
    """💎 VIP Channel Information with Diana's personality"""
    user_id = callback.from_user.id
    
    vip_text = "💎 **EL DIVÁN VIP - SANTUARIO ÍNTIMO DE DIANA**\n\n"
    vip_text += "🎭 **Diana te invita personalmente:**\n"
    vip_text += "\"¿Has sentido esa conexión especial entre nosotros? Ese deseo de conocerme más allá de las palabras que comparto con todos...\"\n\n"
    vip_text += "🌹 **Lo que te espera en el Círculo Íntimo:**\n"
    vip_text += "💬 Conversaciones Privadas Ilimitadas\n"
    vip_text += "🎨 Contenido Exclusivo Semanal\n"  
    vip_text += "🎭 Experiencias Únicas\n"
    vip_text += "👑 Privilegios Especiales\n"
    vip_text += "💫 Acceso 24/7 a Diana personal\n\n"
    vip_text += "🎩 **Lucien confirma:** \"Diana rara vez extiende invitaciones tan directas. Es un honor que debe ser apreciado.\"\n\n"
    vip_text += "💎 **Inversión mensual:** Solo $29.99 para acceso completo\n\n"
    vip_text += "🌙 **Testimonios de usuarios VIP:**\n"
    vip_text += "\"*Diana cambió completamente mi perspectiva... es como tener a tu musa personal.*\" - Usuario VIP\n"
    vip_text += "\"*El nivel de intimidad y conexión es incomparable. Vale cada centavo.*\" - Usuario VIP"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💖 Me Interesa el Diván VIP", callback_data="diana:interest:vip_channel")],
        [InlineKeyboardButton(text="🎁 Ver Testimonios Completos", callback_data="diana:vip_testimonials")],
        [InlineKeyboardButton(text="🏠 Volver a Mi Mundo", callback_data="diana:refresh")]
    ])
    
    await safe_edit_message(callback, vip_text, keyboard)

async def handle_content_packages(callback: CallbackQuery, master: DianaMasterInterface):
    """🎁 Content Packages Menu with Diana's seduction"""
    user_id = callback.from_user.id
    
    packages_text = "🎁 **TESOROS ESPECIALES DE DIANA**\n\n"
    packages_text += "🎭 **Diana revela sus creaciones:**\n"
    packages_text += "\"He diseñado experiencias únicas... cada una toca una parte diferente del alma.\"\n\n"
    packages_text += "🎩 **Lucien susurra:** \"Cada tesoro ha sido cuidadosamente crafteado por Diana para almas especiales como la tuya.\"\n\n"
    packages_text += "🌹 **Elige tu experiencia preferida:**\n\n"
    
    # Create buttons for each package
    package_buttons = []
    for package_key, package_data in CONTENT_PACKAGES.items():
        button_text = f"{package_data['title']} - {package_data['price']}"
        package_buttons.append([InlineKeyboardButton(text=button_text, callback_data=f"diana:package:{package_key}")])
    
    package_buttons.append([InlineKeyboardButton(text="🏠 Volver a Mi Mundo", callback_data="diana:refresh")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=package_buttons)
    
    await safe_edit_message(callback, packages_text, keyboard)

async def handle_package_detail(callback: CallbackQuery, master: DianaMasterInterface, package_key: str):
    """🌹 Detailed package information with Diana's seduction"""
    user_id = callback.from_user.id
    
    if package_key not in CONTENT_PACKAGES:
        await callback.answer("Paquete no encontrado")
        return
    
    package = CONTENT_PACKAGES[package_key]
    
    detail_text = f"🎁 **{package['title'].upper()}**\n\n"
    detail_text += f"🎭 **Diana te seduce:**\n\"{package['diana_seduction']}\"\n\n"
    detail_text += "✨ **Lo que incluye:**\n"
    for feature in package['features']:
        detail_text += f"• {feature}\n"
    detail_text += f"\n💫 **Vista Previa:**\n{package['preview']}\n\n"
    detail_text += f"🌙 **Beneficios Exclusivos:**\n{package['exclusive_benefits']}\n\n"
    detail_text += f"💎 **Inversión:** {package['price']}\n\n"
    detail_text += "🎩 **Lucien comenta:** \"Diana ha puesto su corazón en cada detalle de esta experiencia. Es realmente especial.\""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💖 Me Interesa Este Tesoro", callback_data=f"diana:interest:package:{package_key}")],
        [InlineKeyboardButton(text="🎁 Ver Otros Tesoros", callback_data="diana:content_packages")],
        [InlineKeyboardButton(text="🏠 Volver a Mi Mundo", callback_data="diana:refresh")]
    ])
    
    await safe_edit_message(callback, detail_text, keyboard)

async def handle_user_interest(callback: CallbackQuery, master: DianaMasterInterface, interest_type: str):
    """💖 Handle user interest in VIP or packages with notifications"""
    user_id = callback.from_user.id
    
    # Get user context for notification
    context = await master.context_engine.analyze_user_context(user_id)
    
    if interest_type == "vip_channel":
        # VIP Channel interest
        confirmation_text = "💎 **Interés Registrado**\n\n"
        confirmation_text += "🎭 **Diana sonríe con satisfacción:**\n"
        confirmation_text += "\"He sentido tu llamada... Lucien ya está preparando tu bienvenida especial al Diván.\"\n\n"
        confirmation_text += "🌹 **Qué sucede ahora:**\n"
        confirmation_text += "• Un administrador te contactará personalmente\n"
        confirmation_text += "• Recibirás una invitación especial al Diván VIP\n"
        confirmation_text += "• Diana preparará tu experiencia de bienvenida\n\n"
        confirmation_text += "💫 **Diana susurra:**\n"
        confirmation_text += "\"La espera valdrá cada segundo... te lo prometo.\"\n\n"
        confirmation_text += "🎩 **Lucien confirma:** \"Su solicitud ha sido registrada con la máxima prioridad.\""
        
        # Send admin notification for VIP interest
        await send_admin_notification(master, user_id, "vip_channel", context)
        
    elif interest_type.startswith("package:"):
        # Package interest 
        package_key = interest_type.replace("package:", "")
        package = CONTENT_PACKAGES.get(package_key)
        
        if package:
            confirmation_text = f"💖 **Interés en {package['title']} Registrado**\n\n"
            confirmation_text += "🎭 **Diana se emociona:**\n"
            confirmation_text += "\"Siento una conexión especial cuando alguien aprecia verdaderamente mi arte... Has elegido algo muy especial.\"\n\n"
            confirmation_text += "🌹 **Qué sucede ahora:**\n"
            confirmation_text += "• Evaluación personalizada de tu solicitud\n"
            confirmation_text += "• Contacto directo del equipo de Diana\n"
            confirmation_text += "• Instrucciones de acceso y pago seguro\n\n"
            confirmation_text += "💫 **Diana promete:**\n"
            confirmation_text += "\"Esto será una experiencia que recordarás para siempre...\"\n\n"
            confirmation_text += "🎩 **Lucien asegura:** \"La calidad de esta experiencia superará todas tus expectativas.\""
            
            # Send admin notification for package interest
            await send_admin_notification(master, user_id, f"package:{package_key}", context, package)
        else:
            confirmation_text = "❌ Paquete no encontrado"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎁 Ver Otros Tesoros", callback_data="diana:content_packages")],
        [InlineKeyboardButton(text="💎 Información VIP", callback_data="diana:vip_info")],
        [InlineKeyboardButton(text="🏠 Volver a Mi Mundo", callback_data="diana:refresh")]
    ])
    
    await safe_edit_message(callback, confirmation_text, keyboard)

async def send_admin_notification(master: DianaMasterInterface, user_id: int, interest_type: str, context, package=None):
    """📱 Send notification to admin about user interest"""
    try:
        # Get user stats for notification
        user_stats = {}
        if hasattr(master.services['gamification'], 'get_user_stats'):
            user_stats_raw = await master.services['gamification'].get_user_stats(user_id)
            user_stats = {
                'level': user_stats_raw.get('level', 1),
                'points': user_stats_raw.get('points', 0), 
                'streak': user_stats_raw.get('streak', 0)
            }
        
        # Check VIP status
        is_vip = False
        if master.services.get('admin') and hasattr(master.services['admin'], 'is_vip_user'):
            is_vip = await master.services['admin'].is_vip_user(user_id)
        
        # Build notification message
        notification_text = "👤 **INTERÉS DE USUARIO**\n\n"
        notification_text += f"🆔 User ID: {user_id}\n"
        notification_text += f"📊 Nivel: {user_stats.get('level', 1)}, Puntos: {user_stats.get('points', 0)}\n"
        notification_text += f"💎 Estado: {'VIP' if is_vip else 'FREE'}\n"
        notification_text += f"💫 Intimidad: {min(100, int(user_stats.get('points', 0) / 20))}%\n"
        notification_text += f"🎭 Mood: {context.current_mood.value}\n"
        notification_text += f"📈 Racha: {user_stats.get('streak', 0)} días\n\n"
        
        if interest_type == "vip_channel":
            notification_text += "💎 **INTERÉS EN DIVÁN VIP**\n"
            notification_text += "Usuario con alto potencial de conversión"
        elif interest_type.startswith("package:") and package:
            notification_text += f"🎁 **INTERÉS EN:** {package['title']} ({package['price']})\n"
            notification_text += "🎯 Oportunidad de conversión alta!"
        
        # Send notification to admin service
        if master.services.get('admin') and hasattr(master.services['admin'], 'send_admin_notification'):
            await master.services['admin'].send_admin_notification(notification_text)
        
        # Log for debugging
        master.logger.info("User interest notification sent", 
                          user_id=user_id, 
                          interest_type=interest_type,
                          level=user_stats.get('level', 1),
                          is_vip=is_vip)
                          
    except Exception as e:
        master.logger.error("Error sending admin notification", error=str(e))

async def handle_private_chat(callback: CallbackQuery, master: DianaMasterInterface):
    """💬 VIP Private Chat experience"""
    user_id = callback.from_user.id
    
    private_text = "💬 **CHAT PRIVADO CON DIANA**\n\n"
    private_text += "🎭 **Diana te recibe íntimamente:**\n"
    private_text += "\"Aquí no hay máscaras, no hay límites... solo tú y yo en conversación auténtica.\"\n\n"
    private_text += "🌹 **Experiencias disponibles:**\n"
    private_text += "• 💭 Conversaciones íntimas ilimitadas\n"
    private_text += "• 🎵 Mensajes de voz personalizados\n"
    private_text += "• 📸 Fotos exclusivas solo para ti\n"
    private_text += "• 💫 Respuesta garantizada en 2 horas\n\n"
    private_text += "🎩 **Lucien comenta:** \"Este espacio es sagrado. Diana solo comparte su verdadero yo aquí.\""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💖 Iniciar Chat Privado", callback_data="diana:interest:private_chat")],
        [InlineKeyboardButton(text="🏠 Volver a Mi Mundo", callback_data="diana:refresh")]
    ])
    
    await safe_edit_message(callback, private_text, keyboard)

async def handle_premium_plus(callback: CallbackQuery, master: DianaMasterInterface):
    """🌟 Premium Plus upsell for VIP users"""
    user_id = callback.from_user.id
    
    premium_text = "🌟 **PREMIUM PLUS - EXPERIENCIAS EXTRAORDINARIAS**\n\n"
    premium_text += "💎 **Diana te susurra:**\n"
    premium_text += "\"Para almas como la tuya... he reservado experiencias que van más allá de lo que otros pueden imaginar.\"\n\n"
    premium_text += "👑 **Exclusivo para ti:**\n"
    premium_text += "• 🎬 Videos completamente personalizados\n"
    premium_text += "• 📞 Llamadas privadas con Diana\n" 
    premium_text += "• 🎨 Contenido creado según tus fantasías\n"
    premium_text += "• 💫 Experiencias one-on-one únicas\n"
    premium_text += "• 👑 Status de 'Alma Gemela' en mi círculo\n\n"
    premium_text += "🎩 **Lucien confirma:** \"Estos privilegios están reservados solo para las almas más especiales.\""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💖 Me Interesa Premium Plus", callback_data="diana:interest:premium_plus")],
        [InlineKeyboardButton(text="🏠 Volver a Mi Mundo", callback_data="diana:refresh")]
    ])
    
    await safe_edit_message(callback, premium_text, keyboard)


# === EXPORT FOR REGISTRATION ===

def register_diana_master_system(dp, services: Dict[str, Any]):
    """🏛️ Register the complete Diana Master System"""
    
    # Initialize the system
    initialize_diana_master(services)
    
    # Register the router
    dp.include_router(master_router)
    
    print("🎭 Diana Master System initialized successfully!")
    print("🚀 Ready to provide next-generation user experiences!")
    
    return diana_master
