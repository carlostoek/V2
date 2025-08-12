"""
🎭 DIANA USER UX ENHANCER
========================

Advanced UX enhancement layer that works with Diana User Master System
to provide exceptional user experiences through:

- Optimized keyboard layouts based on user behavior
- Contextual navigation patterns
- Smart button organization and flow
- Enhanced error handling and recovery
- Personality-driven interaction improvements

This enhancer works as a layer on top of the existing Diana User Master System,
providing UX optimizations without disrupting the core functionality.
"""

from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import structlog

class NavigationPattern(Enum):
    """Navigation patterns for different user types"""
    EXPLORER = "explorer"        # Wants to see all options clearly
    FOCUSED = "focused"          # Prefers fewer, prioritized options
    VISUAL = "visual"            # Responds well to icons and visual cues
    TEXT_HEAVY = "text_heavy"    # Prefers descriptive text
    MOBILE_OPTIMIZED = "mobile"  # Needs mobile-friendly layouts

class ConversionStage(Enum):
    """User conversion stages for UX adaptation"""
    DISCOVERY = "discovery"      # Just exploring, don't overwhelm
    INTEREST = "interest"        # Showing interest, guide carefully  
    CONSIDERATION = "consideration"  # Comparing options, provide clarity
    DECISION = "decision"        # Ready to convert, make it easy
    RETENTION = "retention"      # Existing customer, focus on value

@dataclass
class UXPreferences:
    """User UX preferences based on behavior analysis"""
    preferred_navigation: NavigationPattern
    conversion_stage: ConversionStage
    attention_span: str  # "short", "medium", "long"
    interaction_style: str  # "quick", "detailed", "exploratory"
    help_preference: str  # "minimal", "contextual", "comprehensive"

class DianaUserUXEnhancer:
    """
    🌟 Diana UX Enhancement Engine
    
    Provides intelligent UX improvements that adapt to user behavior,
    preferences, and conversion stage while maintaining Diana's personality.
    """
    
    def __init__(self, services: Dict[str, Any]):
        self.services = services
        self.logger = structlog.get_logger()
        
        # User preference tracking
        self.user_preferences: Dict[int, UXPreferences] = {}
        
        # UX optimization patterns
        self.conversion_ctas = {
            ConversionStage.DISCOVERY: {
                "primary": "✨ Descubrir Más",
                "secondary": "🎭 Ver Mi Mundo",
                "personality": "Diana te invita gentilmente a explorar..."
            },
            ConversionStage.INTEREST: {
                "primary": "💎 Explorar VIP", 
                "secondary": "🎁 Ver Tesoros",
                "personality": "Diana siente tu curiosidad creciente..."
            },
            ConversionStage.CONSIDERATION: {
                "primary": "🌹 Me Interesa",
                "secondary": "💭 Saber Más",
                "personality": "Diana espera tu decisión con paciencia..."
            },
            ConversionStage.DECISION: {
                "primary": "💖 ¡Quiero Acceder!",
                "secondary": "💬 Hablar con Diana",
                "personality": "Diana está lista para recibirte..."
            }
        }
    
    async def analyze_user_ux_preferences(self, user_id: int, interaction_history: List[Dict] = None) -> UXPreferences:
        """Analyze user behavior to determine UX preferences"""
        
        if user_id in self.user_preferences:
            return self.user_preferences[user_id]
        
        # Analyze user behavior patterns
        try:
            # Get user stats for behavior analysis
            user_stats = {}
            if 'gamification' in self.services:
                user_stats = await self.services['gamification'].get_user_stats(user_id)
            
            # Determine navigation preferences based on engagement patterns
            level = user_stats.get('level', 1)
            interactions = user_stats.get('total_interactions', 0)
            
            # Determine preferred navigation pattern
            if interactions > 50:
                nav_pattern = NavigationPattern.FOCUSED  # Experienced users want efficiency
            elif level > 5:
                nav_pattern = NavigationPattern.EXPLORER  # Engaged users want options
            else:
                nav_pattern = NavigationPattern.VISUAL  # New users need visual guidance
            
            # Determine conversion stage
            conversion_stage = await self._analyze_conversion_stage(user_id)
            
            # Determine interaction preferences
            attention_span = "long" if level > 7 else "medium" if level > 3 else "short"
            interaction_style = "detailed" if interactions > 30 else "exploratory" if interactions > 10 else "quick"
            help_preference = "minimal" if level > 10 else "contextual" if level > 5 else "comprehensive"
            
            preferences = UXPreferences(
                preferred_navigation=nav_pattern,
                conversion_stage=conversion_stage,
                attention_span=attention_span,
                interaction_style=interaction_style,
                help_preference=help_preference
            )
            
            self.user_preferences[user_id] = preferences
            return preferences
            
        except Exception as e:
            self.logger.warning("Error analyzing UX preferences", error=str(e))
            
            # Fallback to default preferences
            return UXPreferences(
                preferred_navigation=NavigationPattern.VISUAL,
                conversion_stage=ConversionStage.DISCOVERY,
                attention_span="short",
                interaction_style="quick",
                help_preference="contextual"
            )
    
    async def _analyze_conversion_stage(self, user_id: int) -> ConversionStage:
        """Analyze user's current conversion stage"""
        try:
            # Check VIP status
            is_vip = False
            if 'admin' in self.services and hasattr(self.services['admin'], 'is_vip_user'):
                is_vip = await self.services['admin'].is_vip_user(user_id)
            
            if is_vip:
                return ConversionStage.RETENTION
            
            # Analyze engagement level for conversion readiness
            user_stats = {}
            if 'gamification' in self.services:
                user_stats = await self.services['gamification'].get_user_stats(user_id)
            
            level = user_stats.get('level', 1)
            interactions = user_stats.get('total_interactions', 0)
            
            # Determine stage based on engagement
            if interactions > 20 and level > 5:
                return ConversionStage.DECISION
            elif interactions > 10 and level > 3:
                return ConversionStage.CONSIDERATION
            elif interactions > 5:
                return ConversionStage.INTEREST
            else:
                return ConversionStage.DISCOVERY
                
        except Exception as e:
            self.logger.warning("Error analyzing conversion stage", error=str(e))
            return ConversionStage.DISCOVERY
    
    def enhance_main_keyboard(self, 
                             original_keyboard: InlineKeyboardMarkup, 
                             user_id: int, 
                             tier: str,
                             ux_preferences: UXPreferences) -> InlineKeyboardMarkup:
        """Enhance the main keyboard based on user preferences"""
        
        if tier == "FREE":
            return self._enhance_free_user_keyboard(ux_preferences)
        else:
            return self._enhance_vip_user_keyboard(ux_preferences)
    
    def _enhance_free_user_keyboard(self, prefs: UXPreferences) -> InlineKeyboardMarkup:
        """Enhanced FREE user keyboard with UX optimizations"""
        
        if prefs.conversion_stage == ConversionStage.DISCOVERY:
            # Discovery stage - gentle exploration focus
            buttons = [
                [InlineKeyboardButton(text="🎭 Conocer a Diana", callback_data="diana_user:section:profile")],
                [
                    InlineKeyboardButton(text="📖 Mi Historia", callback_data="diana_user:section:narrative"),
                    InlineKeyboardButton(text="📜 Desafíos", callback_data="diana_user:section:missions")
                ],
                [InlineKeyboardButton(text="✨ Descubrir Más", callback_data="diana_user:section:vip_info")],
                [
                    InlineKeyboardButton(text="❓ Ayuda", callback_data="diana_user:help"),
                    InlineKeyboardButton(text="🔄 Actualizar", callback_data="diana_user:refresh")
                ]
            ]
            
        elif prefs.conversion_stage == ConversionStage.INTEREST:
            # Interest stage - highlight VIP benefits
            buttons = [
                [
                    InlineKeyboardButton(text="🎭 Mi Reflejo", callback_data="diana_user:section:profile"),
                    InlineKeyboardButton(text="📜 Desafíos", callback_data="diana_user:section:missions")
                ],
                [InlineKeyboardButton(text="💎 El Diván VIP ⭐", callback_data="diana_user:section:vip_info")],
                [
                    InlineKeyboardButton(text="🎁 Tesoros Especiales", callback_data="diana_user:section:content_packages"),
                    InlineKeyboardButton(text="📖 Mi Historia", callback_data="diana_user:section:narrative")
                ],
                [
                    InlineKeyboardButton(text="🔄 Actualizar", callback_data="diana_user:refresh"),
                    InlineKeyboardButton(text="🎯 Misión Rápida", callback_data="diana_user:quick_mission")
                ]
            ]
            
        elif prefs.conversion_stage in [ConversionStage.CONSIDERATION, ConversionStage.DECISION]:
            # Consideration/Decision stage - prioritize conversion paths
            buttons = [
                [InlineKeyboardButton(text="💎 El Diván VIP - ¡Promoción Especial! 🌟", callback_data="diana_user:section:vip_info")],
                [
                    InlineKeyboardButton(text="🎁 Tesoros Premium", callback_data="diana_user:section:content_packages"),
                    InlineKeyboardButton(text="🎭 Mi Perfil", callback_data="diana_user:section:profile")
                ],
                [
                    InlineKeyboardButton(text="📖 Mi Historia", callback_data="diana_user:section:narrative"),
                    InlineKeyboardButton(text="📜 Desafíos", callback_data="diana_user:section:missions")
                ],
                [
                    InlineKeyboardButton(text="💬 Hablar con Diana", callback_data="diana_user:contact_diana"),
                    InlineKeyboardButton(text="🔄 Actualizar", callback_data="diana_user:refresh")
                ]
            ]
        else:
            # Fallback to balanced layout
            buttons = [
                [
                    InlineKeyboardButton(text="🎭 Mi Reflejo", callback_data="diana_user:section:profile"),
                    InlineKeyboardButton(text="📜 Desafíos", callback_data="diana_user:section:missions")
                ],
                [
                    InlineKeyboardButton(text="💎 El Diván VIP", callback_data="diana_user:section:vip_info"),
                    InlineKeyboardButton(text="🎁 Tesoros Especiales", callback_data="diana_user:section:content_packages")
                ],
                [InlineKeyboardButton(text="📖 Mi Historia", callback_data="diana_user:section:narrative")],
                [
                    InlineKeyboardButton(text="🔄 Actualizar", callback_data="diana_user:refresh"),
                    InlineKeyboardButton(text="❓ Ayuda", callback_data="diana_user:help")
                ]
            ]
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    def _enhance_vip_user_keyboard(self, prefs: UXPreferences) -> InlineKeyboardMarkup:
        """Enhanced VIP user keyboard with retention focus"""
        
        # VIP users get premium-focused layout with upsell opportunities
        buttons = [
            [
                InlineKeyboardButton(text="💬 Chat Privado con Diana", callback_data="diana_user:section:private_chat"),
                InlineKeyboardButton(text="🎨 Galería Privada", callback_data="diana_user:section:exclusive_content")
            ],
            [
                InlineKeyboardButton(text="🎭 Mi Reflejo VIP", callback_data="diana_user:section:profile"),
                InlineKeyboardButton(text="📖 Mi Historia", callback_data="diana_user:section:narrative")
            ],
            [InlineKeyboardButton(text="🌟 Premium Plus - Experiencias Únicas", callback_data="diana_user:premium_upgrade")],
            [
                InlineKeyboardButton(text="📜 Desafíos Elite", callback_data="diana_user:section:missions"),
                InlineKeyboardButton(text="🎁 Creaciones Personalizadas", callback_data="diana_user:custom_content")
            ],
            [
                InlineKeyboardButton(text="💭 Hablar con Diana", callback_data="diana_user:direct_chat"),
                InlineKeyboardButton(text="🔄 Actualizar", callback_data="diana_user:refresh")
            ]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    def enhance_section_keyboard(self, 
                                section_key: str,
                                original_keyboard: InlineKeyboardMarkup,
                                ux_preferences: UXPreferences,
                                conversion_context: Dict[str, Any] = None) -> InlineKeyboardMarkup:
        """Enhance section keyboards with better navigation patterns"""
        
        if section_key == "vip_info":
            return self._enhance_vip_info_keyboard(ux_preferences, conversion_context)
        elif section_key == "content_packages":
            return self._enhance_packages_keyboard(ux_preferences, conversion_context)
        else:
            return self._enhance_generic_section_keyboard(section_key, original_keyboard, ux_preferences)
    
    def _enhance_vip_info_keyboard(self, prefs: UXPreferences, context: Dict = None) -> InlineKeyboardMarkup:
        """Enhanced VIP info keyboard with conversion optimization"""
        
        cta_config = self.conversion_ctas.get(prefs.conversion_stage, self.conversion_ctas[ConversionStage.INTEREST])
        
        if prefs.conversion_stage == ConversionStage.DECISION:
            # Decision stage - make conversion super easy
            buttons = [
                [InlineKeyboardButton(text="💖 ¡Quiero Acceder al Diván VIP!", callback_data="diana_user:interest:vip_channel")],
                [InlineKeyboardButton(text="🎁 Primera Semana GRATIS", callback_data="diana_user:vip_trial")],
                [
                    InlineKeyboardButton(text="🌹 Ver Testimonios", callback_data="diana_user:vip_testimonials"),
                    InlineKeyboardButton(text="💬 Preguntar a Diana", callback_data="diana_user:ask_diana_vip")
                ],
                [
                    InlineKeyboardButton(text="📋 Beneficios Completos", callback_data="diana_user:vip_benefits"),
                    InlineKeyboardButton(text="🎯 Comparar Paquetes", callback_data="diana_user:compare_packages")
                ],
                [InlineKeyboardButton(text="🔙 Mi Mundo", callback_data="diana_user:main")]
            ]
        else:
            # Standard enhanced layout
            buttons = [
                [InlineKeyboardButton(text=f"💖 {cta_config['primary']}", callback_data="diana_user:interest:vip_channel")],
                [
                    InlineKeyboardButton(text="🌹 Ver Testimonios", callback_data="diana_user:vip_testimonials"),
                    InlineKeyboardButton(text="👁️ Vista Previa", callback_data="diana_user:vip_preview")
                ],
                [
                    InlineKeyboardButton(text="📋 Beneficios Completos", callback_data="diana_user:vip_benefits"),
                    InlineKeyboardButton(text="❓ Preguntas Frecuentes", callback_data="diana_user:vip_faq")
                ],
                [
                    InlineKeyboardButton(text="🎁 Ver Otros Tesoros", callback_data="diana_user:section:content_packages"),
                    InlineKeyboardButton(text="🔙 Mi Mundo", callback_data="diana_user:main")
                ]
            ]
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    def _enhance_packages_keyboard(self, prefs: UXPreferences, context: Dict = None) -> InlineKeyboardMarkup:
        """Enhanced content packages keyboard"""
        
        # Always show packages clearly with enhanced CTAs
        buttons = [
            [InlineKeyboardButton(text="🌹 Conversaciones Íntimas - $29.99", callback_data="diana_user:package:intimate_conversations")],
            [InlineKeyboardButton(text="📸 Fotografías Exclusivas - $19.99", callback_data="diana_user:package:exclusive_photos")],
            [InlineKeyboardButton(text="🎬 Videos Personalizados - $49.99", callback_data="diana_user:package:custom_videos")],
            [InlineKeyboardButton(text="👑 Experiencias VIP - $99.99/mes", callback_data="diana_user:package:vip_experiences")],
            [
                InlineKeyboardButton(text="💎 Comparar con VIP", callback_data="diana_user:compare_vip"),
                InlineKeyboardButton(text="🎁 Ofertas Especiales", callback_data="diana_user:special_offers")
            ],
            [InlineKeyboardButton(text="🔙 Mi Mundo", callback_data="diana_user:main")]
        ]
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    def _enhance_generic_section_keyboard(self, 
                                        section_key: str, 
                                        original: InlineKeyboardMarkup, 
                                        prefs: UXPreferences) -> InlineKeyboardMarkup:
        """Enhance generic section keyboards with better navigation"""
        
        # For now, return original with potential navigation improvements
        # Could be enhanced further based on specific section needs
        return original
    
    def get_contextual_help_message(self, section_key: str, user_preferences: UXPreferences) -> Optional[str]:
        """Get contextual help message for current section"""
        
        help_messages = {
            "main": {
                "comprehensive": "🎯 <b>Guía Completa:</b> Usa los botones para navegar, 🎭 para tu perfil, 💎 para VIP, 🎁 para tesoros especiales. Diana te guiará en cada paso.",
                "contextual": "💡 <b>Consejo:</b> Explora las diferentes secciones para conocer mejor el mundo de Diana.",
                "minimal": "🔍 Usa los botones para explorar."
            },
            "vip_info": {
                "comprehensive": "💎 <b>Información VIP:</b> Aquí puedes conocer todos los beneficios del Diván VIP. Haz clic en 'Me Interesa' cuando estés listo para el siguiente nivel.",
                "contextual": "🌹 <b>Consejo de Diana:</b> El Diván VIP es donde puedo ser completamente auténtica contigo.",
                "minimal": "💡 Explora los beneficios VIP."
            },
            "content_packages": {
                "comprehensive": "🎁 <b>Tesoros Especiales:</b> Cada paquete ofrece una experiencia única creada por Diana. Haz clic en cualquiera para ver detalles completos.",
                "contextual": "✨ <b>Diana sugiere:</b> Cada tesoro ha sido diseñado para tocar el alma de manera especial.",
                "minimal": "🎨 Explora los tesoros disponibles."
            }
        }
        
        section_help = help_messages.get(section_key, {})
        return section_help.get(user_preferences.help_preference, None)
    
    def analyze_conversion_optimization_opportunities(self, user_id: int, current_section: str) -> Dict[str, Any]:
        """Analyze opportunities for conversion optimization"""
        
        preferences = self.user_preferences.get(user_id)
        if not preferences:
            return {}
        
        opportunities = {
            "current_stage": preferences.conversion_stage.value,
            "recommended_next_action": None,
            "optimization_suggestions": [],
            "urgency_level": "low"
        }
        
        if preferences.conversion_stage == ConversionStage.DECISION and current_section != "vip_info":
            opportunities.update({
                "recommended_next_action": "guide_to_vip_info",
                "optimization_suggestions": ["Add prominent VIP CTA", "Show limited-time offer"],
                "urgency_level": "high"
            })
        
        elif preferences.conversion_stage == ConversionStage.CONSIDERATION:
            opportunities.update({
                "recommended_next_action": "provide_social_proof",
                "optimization_suggestions": ["Show testimonials", "Highlight benefits", "Offer trial"],
                "urgency_level": "medium"
            })
        
        return opportunities

def create_diana_ux_enhancer(services: Dict[str, Any]) -> DianaUserUXEnhancer:
    """Factory function to create Diana UX Enhancer"""
    return DianaUserUXEnhancer(services)