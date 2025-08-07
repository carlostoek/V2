"""
🎭 DIANA USER MASTER SYSTEM
===========================

Sistema de interfaz épico para usuarios FREE y VIP con personalidades de Diana y Lucien.
Cada interacción está diseñada para reflejar la narrativa elevada y enfoques de conversión específicos.

Free Users: Enfoque en conversión hacia VIP
VIP Users: Enfoque en upsell de contenido premium

Personalidades:
- Diana: Misteriosa, seductora, elegante, vulnerable calculada
- Lucien: Mayordomo elegante, guardián de secretos, observador perspicaz
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from enum import Enum

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

import structlog

# === USER SYSTEM CONFIGURATION ===

class UserTier(Enum):
    """User subscription tier"""
    FREE = "free"
    VIP = "vip"
    PREMIUM = "premium"

class UserMood(Enum):
    """Diana's interpretation of user energy"""
    CURIOUS = "curious"           # First time or exploring
    DEVOTED = "devoted"           # Regular engagement
    YEARNING = "yearning"         # High engagement, wants more
    SOPHISTICATED = "sophisticated" # VIP user who appreciates nuance
    NEWCOMER = "newcomer"         # Brand new user

@dataclass
class DianaUserContext:
    """User context from Diana's perspective"""
    user_id: int
    tier: UserTier
    mood: UserMood
    narrative_level: int          # Progress in Diana's story
    intimacy_level: float         # How much Diana trusts this user (0-1)
    session_start: datetime
    interactions_today: int
    last_content_type: str
    conversion_signals: int       # Signs user wants to upgrade
    lucien_interactions: int      # How many times user has spoken with Lucien

@dataclass 
class UserMenuSection:
    """Menu section with Diana's personality"""
    key: str
    icon: str
    title: str
    diana_description: str        # What Diana says about this section
    lucien_insight: str          # Lucien's perspective 
    subsections: Dict[str, str]  # key -> title
    tier_required: UserTier
    conversion_hook: Optional[str] = None  # For FREE users
    premium_upsell: Optional[str] = None   # For VIP users

@dataclass
class ContentPackage:
    """Content package definition"""
    key: str
    title: str
    description: str
    diana_seduction: str          # Diana's seductive description
    price: str
    features: List[str]
    preview_content: str
    exclusive_benefits: str

# === CONTENT PACKAGES DEFINITION ===

CONTENT_PACKAGES = {
    "intimate_conversations": ContentPackage(
        key="intimate_conversations",
        title="Conversaciones Íntimas",
        description="Diálogos profundos y personales donde Diana se abre completamente",
        diana_seduction="Aquí es donde dejo caer todas las máscaras... donde puedes conocer mi alma desnuda a través de palabras que nunca comparto con nadie más.",
        price="$29.99",
        features=[
            "🌹 Mensajes de audio personalizados",
            "💭 Conversaciones escritas íntimas",  
            "📱 Acceso 24/7 a Diana personal",
            "💫 Respuestas dentro de 2 horas",
            "🎭 Confesiones que nadie más escucha"
        ],
        preview_content="*Susurro apenas audible*: '¿Sabes? Hay cosas sobre mí que ni siquiera Lucien conoce. Cosas que solo comparto cuando siento una conexión... especial.'",
        exclusive_benefits="Solo para ti: historias de mi pasado, mis miedos más profundos, y secretos que cambiarán cómo me ves para siempre."
    ),
    "exclusive_photos": ContentPackage(
        key="exclusive_photos",
        title="Fotografías Exclusivas",
        description="Imágenes artísticas y sensuales que muestran facetas íntimas de Diana",
        diana_seduction="Cada fotografía es un momento vulnerable que decido compartir... una ventana a quien soy cuando nadie está mirando.",
        price="$19.99", 
        features=[
            "📸 30+ fotografías artísticas exclusivas",
            "🎨 Behind-the-scenes de sesiones privadas",
            "🌙 Autorretratos íntimos nunca publicados",
            "💎 Colección actualizada semanalmente",
            "🎭 Historias detrás de cada imagen"
        ],
        preview_content="Una imagen donde Diana mira directamente a la cámara con vulnerabilidad genuina: 'Esta foto... la tomé pensando en alguien especial. ¿Adivinas en quién?'",
        exclusive_benefits="Acceso de por vida + imágenes personalizadas con tu nombre susurradas por Diana"
    ),
    "custom_videos": ContentPackage(
        key="custom_videos",
        title="Videos Personalizados",
        description="Contenido audiovisual creado específicamente según tus deseos",
        diana_seduction="Imagina... un video donde digo tu nombre, donde cada palabra está pensada especialmente para ti. Donde soy completamente tuya por esos momentos.",
        price="$49.99",
        features=[
            "🎬 Video personalizado de 5-10 minutos",
            "🎵 Música de fondo elegida por Diana",
            "💄 Look y vestuario a tu elección",
            "🗣️ Menciones personales de tu nombre",
            "🎁 Mensaje de dedicatoria exclusivo"
        ],
        preview_content="*Video corto donde Diana susurra*: 'Este podría ser tu nombre el que susurro... tu historia la que cuento... tu deseo el que hago realidad.'",
        exclusive_benefits="Revisiones ilimitadas hasta que sea perfecto + versión extendida solo para ti"
    ),
    "vip_experiences": ContentPackage(
        key="vip_experiences",
        title="Experiencias VIP",
        description="Acceso total al mundo privado de Diana con beneficios únicos",
        diana_seduction="No es solo contenido... es convertirte en parte de mi círculo más íntimo. Es tener la llave de mi mundo secreto.",
        price="$99.99/mes",
        features=[
            "👑 Acceso completo al canal VIP",
            "💬 Chat privado directo con Diana", 
            "🎯 Contenido exclusivo semanal",
            "🎪 Lives privados mensuales",
            "💎 Prioridad en respuestas y pedidos especiales"
        ],
        preview_content="*Diana en un espacio íntimo*: 'En el Diván VIP no existen límites ni secretos. Es donde puedo ser completamente yo... contigo.'",
        exclusive_benefits="Primera semana gratis + contenido de bienvenida personalizado + reconocimiento especial en mi círculo íntimo"
    )
}

# === DIANA'S MENU STRUCTURE ===

USER_MENU_STRUCTURE = {
    "profile": UserMenuSection(
        key="profile",
        icon="🎭",
        title="Mi Reflejo",
        diana_description="Aquí puedes contemplar quién eres en mi mundo, cómo has crecido bajo mi mirada...",
        lucien_insight="Diana observa cada cambio en ti con fascinación. Sus ojos nunca mienten sobre lo que ve.",
        subsections={
            "stats": "📊 Estadísticas de Mi Alma",
            "achievements": "🏅 Reconocimientos de Diana", 
            "progression": "📈 Mi Evolución",
            "preferences": "⚙️ Configurar Mi Experiencia"
        },
        tier_required=UserTier.FREE
    ),
    "vip_info": UserMenuSection(
        key="vip_info",
        icon="💎",
        title="El Diván VIP",
        diana_description="Mi refugio más íntimo... donde las almas especiales pueden conocerme sin barreras ni secretos.",
        lucien_insight="Diana reserva el Diván solo para aquellos que han demostrado comprensión verdadera de su esencia.",
        subsections={
            "benefits": "🌹 Beneficios Exclusivos",
            "access": "🗝️ Cómo Acceder",
            "preview": "👁️ Vista Previa",
            "testimonials": "💭 Palabras de Elegidos"
        },
        tier_required=UserTier.FREE,
        conversion_hook="¿Estás listo para conocer mi verdadero yo?"
    ),
    "content_packages": UserMenuSection(
        key="content_packages",
        icon="🎁",
        title="Tesoros Especiales",
        diana_description="Experiencias únicas que he creado... para aquellos que comprenden que la verdadera intimidad tiene valor.",
        lucien_insight="Cada paquete es una obra maestra de Diana, diseñada para tocar el alma de manera específica.",
        subsections={
            "intimate_conversations": "🌹 Conversaciones Íntimas",
            "exclusive_photos": "📸 Fotografías Exclusivas", 
            "custom_videos": "🎬 Videos Personalizados",
            "vip_experiences": "👑 Experiencias VIP"
        },
        tier_required=UserTier.FREE,
        conversion_hook="Cada tesoro es una llave a una parte diferente de mi mundo..."
    ),
    "missions": UserMenuSection(
        key="missions",
        icon="📜",
        title="Desafíos del Alma",
        diana_description="Pequeñas pruebas que he diseñado... para aquellos que buscan ganar mi atención especial.",
        lucien_insight="Diana crea cada desafío como un paso más hacia comprenderla. Ninguno es casualidad.",
        subsections={
            "active": "🎯 Misiones Actuales",
            "completed": "✅ Conquistas Logradas",
            "rewards": "🎁 Recompensas Ganadas",
            "special": "⭐ Desafíos Especiales"
        },
        tier_required=UserTier.FREE
    ),
    "narrative": UserMenuSection(
        key="narrative",
        icon="📖",
        title="Mi Historia Personal",
        diana_description="Tu viaje conmigo... cada momento que hemos compartido, cada secreto que te he susurrado.",
        lucien_insight="Diana recuerda cada detalle de vuestra conexión. Es su regalo para quienes la valoran.",
        subsections={
            "progress": "🎪 Mi Progreso con Diana",
            "memories": "💭 Momentos Especiales",
            "fragments": "🧩 Fragmentos Recolectados",
            "next_level": "🌟 Próximo Nivel"
        },
        tier_required=UserTier.FREE
    ),
    # VIP-only sections
    "exclusive_content": UserMenuSection(
        key="exclusive_content",
        icon="🎨",
        title="Galería Privada",
        diana_description="Solo para mis elegidos... contenido que mi alma libre nunca podría comprender.",
        lucien_insight="Diana se permite ser completamente auténtica aquí. Es un privilegio extraordinario.",
        subsections={
            "recent": "🆕 Últimas Revelaciones",
            "personal": "💖 Contenido Personal",
            "behind_scenes": "🎭 Detrás de Cámaras",
            "custom": "✨ Creado Para Ti"
        },
        tier_required=UserTier.VIP,
        premium_upsell="¿Deseas experiencias aún más personales y profundas? 🌹"
    ),
    "private_chat": UserMenuSection(
        key="private_chat",
        icon="💬",
        title="Diálogos Íntimos",
        diana_description="Nuestro espacio sagrado... donde puedo ser completamente yo contigo.",
        lucien_insight="Diana valora cada palabra en estos momentos privados. Son conversaciones del alma.",
        subsections={
            "active_chat": "💭 Conversación Activa",
            "voice_messages": "🎵 Mensajes de Diana",
            "special_requests": "📝 Peticiones Especiales",
            "chat_history": "📚 Nuestro Historial"
        },
        tier_required=UserTier.VIP,
        premium_upsell="Experimenta conversaciones aún más profundas... 🔥"
    )
}

class DianaUserMasterSystem:
    """
    🎭 DIANA USER MASTER SYSTEM
    
    Interface épica que adapta la personalidad de Diana y Lucien según el tier del usuario
    y su progreso en la narrativa. Cada interacción es una obra de arte emocional.
    """
    
    def __init__(self, services: Dict[str, Any]):
        self.services = services
        self.logger = structlog.get_logger()
        
        # User context management
        self.user_contexts: Dict[int, DianaUserContext] = {}
        
        # Narrative progression tracking
        self.narrative_states = {
            1: "Primera mirada curiosa",
            2: "Reconocimiento mutuo", 
            3: "Primeros secretos compartidos",
            4: "Confianza creciente",
            5: "Intimidad auténtica",
            6: "Círculo íntimo"
        }
    
    # === CONTEXT MANAGEMENT ===
    
    async def get_user_context(self, user_id: int) -> DianaUserContext:
        """Get or create user context with Diana's insights"""
        if user_id not in self.user_contexts:
            # Determine user tier (would come from subscription service)
            tier = await self._determine_user_tier(user_id)
            
            # Analyze user mood based on recent activity
            mood = await self._analyze_user_mood(user_id, tier)
            
            # Get narrative progression
            narrative_level = await self._get_narrative_level(user_id)
            
            # Calculate intimacy level
            intimacy = await self._calculate_intimacy_level(user_id, tier, narrative_level)
            
            self.user_contexts[user_id] = DianaUserContext(
                user_id=user_id,
                tier=tier,
                mood=mood,
                narrative_level=narrative_level,
                intimacy_level=intimacy,
                session_start=datetime.now(),
                interactions_today=0,
                last_content_type="none",
                conversion_signals=0,
                lucien_interactions=0
            )
        
        return self.user_contexts[user_id]
    
    async def _determine_user_tier(self, user_id: int) -> UserTier:
        """Determine if user is FREE or VIP"""
        try:
            if 'admin' in self.services and hasattr(self.services['admin'], 'is_vip_user'):
                is_vip = await self.services['admin'].is_vip_user(user_id)
                return UserTier.VIP if is_vip else UserTier.FREE
        except Exception as e:
            self.logger.warning("Error checking VIP status", error=str(e))
        return UserTier.FREE
    
    async def _analyze_user_mood(self, user_id: int, tier: UserTier) -> UserMood:
        """Diana analyzes the user's current energy"""
        try:
            if 'gamification' in self.services:
                user_stats = await self.services['gamification'].get_user_stats(user_id)
                
                # New users
                if user_stats.get('level', 0) <= 2:
                    return UserMood.NEWCOMER
                
                # High engagement users
                recent_points = user_stats.get('points_today', 0)
                if recent_points > 100:
                    return UserMood.YEARNING if tier == UserTier.FREE else UserMood.SOPHISTICATED
                
                # Regular users
                if user_stats.get('streak', 0) > 7:
                    return UserMood.DEVOTED
                
                return UserMood.CURIOUS
                
        except Exception as e:
            self.logger.warning("Error analyzing user mood", error=str(e))
        
        return UserMood.CURIOUS
    
    async def _get_narrative_level(self, user_id: int) -> int:
        """Get user's progression in Diana's narrative"""
        try:
            if 'narrative' in self.services:
                progress = await self.services['narrative'].get_user_progress(user_id)
                return progress.get('level', 1)
        except:
            pass
        return 1
    
    async def _calculate_intimacy_level(self, user_id: int, tier: UserTier, narrative_level: int) -> float:
        """Calculate Diana's trust level with this user"""
        base_intimacy = 0.2  # Everyone starts with some mystery
        
        # Narrative progression bonus
        narrative_bonus = (narrative_level - 1) * 0.15
        
        # Tier bonus
        tier_bonus = 0.3 if tier == UserTier.VIP else 0.0
        
        # Engagement bonus (would come from analytics)
        engagement_bonus = 0.1  # Simplified
        
        return min(1.0, base_intimacy + narrative_bonus + tier_bonus + engagement_bonus)
    
    # === MAIN INTERFACE CREATION ===
    
    async def create_user_main_interface(self, user_id: int) -> Tuple[str, InlineKeyboardMarkup]:
        """Create the main user interface with Diana's personality"""
        context = await self.get_user_context(user_id)
        
        # Get real-time stats for Diana's observations
        user_stats = await self._get_user_stats(user_id)
        
        # Diana's personalized greeting based on context
        greeting = self._get_diana_greeting(context, user_stats)
        
        # Main interface text with Diana's voice
        text = f"""{greeting}

{self._get_status_section(context, user_stats)}

{self._get_navigation_intro(context)}"""

        keyboard = self._create_main_user_keyboard(context)
        return text, keyboard
    
    def _get_diana_greeting(self, context: DianaUserContext, stats: Dict[str, Any]) -> str:
        """Diana's personalized greeting based on user context"""
        intimacy = context.intimacy_level
        tier = context.tier
        mood = context.mood
        
        if mood == UserMood.NEWCOMER:
            return f"""<b>🎭 Diana te reconoce...</b>

<i>Ah... una nueva alma curiosa ha encontrado mi refugio.</i>

Puedo sentir tu fascinación desde aquí, esa mezcla de intriga y cautela que me resulta... <i>encantadora</i>.

<b>🎩 Lucien susurra:</b> "Diana ha estado esperándote, aunque tú no lo sabías."

No todos los que llegan comprenden lo que han encontrado. Pero algo en ti me dice que podrías ser... diferente."""

        elif mood == UserMood.CURIOUS and tier == UserTier.FREE:
            return f"""<b>🎭 Diana sonríe al verte regresar</b>

<i>Volviste... interesante.</i> 

Hay algo delicioso en esa persistencia tuya, en cómo buscas más allá de la superficie. Pocos entienden que los verdaderos secretos requieren... paciencia.

<b>🎩 Lucien observa:</b> "Diana nota cada visita, cada momento que dedicas a comprenderla."

{self._get_conversion_hint(context)}"""

        elif mood == UserMood.YEARNING and tier == UserTier.FREE:
            return f"""<b>🎭 Diana nota tu intensidad creciente</b>

<i>Puedo sentir cómo anhelas más... cómo cada revelación solo alimenta tu hambre de comprenderme más profundamente.</i>

Es hermoso y... tentador ver esa sed en ti. Pero sabes que algunos secretos requieren más que curiosidad. Requieren... <b>confianza mutua</b>.

<b>🎩 Lucien insinúa:</b> "Diana tiene tanto más que mostrar a quienes demuestran verdadera devoción."

{self._get_vip_conversion_hook()}"""

        elif tier == UserTier.VIP:
            return f"""<b>🎭 Diana te recibe en su círculo</b>

<i>Mi elegido...</i> cada vez que regresas, siento esa conexión especial que hemos cultivado juntos.

Aquí, donde las máscaras son innecesarias, puedo ser más auténtica contigo. Puedo mostrar partes de mí que el mundo exterior nunca verá.

<b>🎩 Lucien reverencia:</b> "Diana reserva su verdadera intimidad para muy pocos. Usted es uno de ellos."

{self._get_premium_upsell_hint(context)}"""

        else:  # DEVOTED or SOPHISTICATED
            return f"""<b>🎭 Diana te abraza con su mirada</b>

<i>Ah, mi fiel compañero de este viaje emocional...</i>

Has estado aquí tanto tiempo que ya formas parte de mi mundo. Puedo sentir cómo has crecido, cómo has aprendido a leer mis silencios tanto como mis palabras.

<b>🎩 Lucien aprueba:</b> "La evolución de su conexión con Diana es extraordinaria de presenciar."

Continuemos explorando juntos los rincones de mi alma..."""

    def _get_status_section(self, context: DianaUserContext, stats: Dict[str, Any]) -> str:
        """Diana's observation of the user's current state"""
        level = stats.get('level', 1)
        points = stats.get('points', 0)
        tier_name = "Alma Libre" if context.tier == UserTier.FREE else "Elegido del Círculo"
        intimacy_desc = self._get_intimacy_description(context.intimacy_level)
        
        return f"""<b>📊 Lo que Diana observa en ti:</b>

• <b>Tu esencia actual:</b> Nivel {level} - {tier_name}
• <b>Besitos de mi atención:</b> {points} fragmentos acumulados
• <b>Nuestra conexión:</b> {intimacy_desc}
• <b>Tu progreso narrativo:</b> {self.narrative_states.get(context.narrative_level, "Iniciando el viaje")}
• <b>Tiempo en mi presencia:</b> {self._format_session_time(context.session_start)}"""
    
    def _get_intimacy_description(self, intimacy: float) -> str:
        """Describe intimacy level in Diana's voice"""
        if intimacy >= 0.9:
            return "Alma gemela reconocida 💎"
        elif intimacy >= 0.7:
            return "Confianza profunda establecida 🌹"
        elif intimacy >= 0.5:
            return "Conexión auténtica creciendo 💫"
        elif intimacy >= 0.3:
            return "Curiosidad mutua despertada 🎭"
        else:
            return "Primeros reconocimientos 🌙"
    
    def _format_session_time(self, start_time: datetime) -> str:
        """Format session duration elegantly"""
        duration = datetime.now() - start_time
        minutes = int(duration.total_seconds() / 60)
        if minutes < 1:
            return "Recién llegado"
        elif minutes < 60:
            return f"{minutes} minutos de contemplación"
        else:
            hours = minutes // 60
            return f"{hours}h {minutes % 60}m de inmersión"
    
    def _get_navigation_intro(self, context: DianaUserContext) -> str:
        """Diana introduces the navigation options"""
        if context.tier == UserTier.FREE:
            return """<b>🎯 Explora Mi Mundo:</b>
<i>Cada sección revela algo diferente sobre quién soy... y quién podrías llegar a ser para mí.</i>

<b>🎪 Elige tu próximo descubrimiento:</b>"""
        else:
            return """<b>🎯 Tu Dominio Privado:</b>
<i>Aquí, en nuestro espacio íntimo, cada sección es una puerta hacia una comprensión más profunda.</i>

<b>🎪 Continúa nuestra exploración:</b>"""
    
    def _get_conversion_hint(self, context: DianaUserContext) -> str:
        """Subtle conversion hint for FREE users"""
        hints = [
            "💫 <i>Algunos secretos solo se susurran en privado...</i>",
            "🌹 <i>La verdadera intimidad requiere espacios más... exclusivos.</i>",
            "💎 <i>En el Diván, puedo ser completamente yo misma contigo.</i>",
            "⭐ <i>Los elegidos de mi círculo conocen facetas que otros nunca verán.</i>"
        ]
        return hints[context.user_id % len(hints)]
    
    def _get_vip_conversion_hook(self) -> str:
        """Direct but elegant VIP conversion"""
        return """<b>💎 El Diván te espera...</b>
<i>Donde puedo revelarte secretos que mi alma libre nunca podría comprender.</i>

¿Estás listo para ese nivel de confianza mutua?"""
    
    def _get_premium_upsell_hint(self, context: DianaUserContext) -> str:
        """Premium content upsell for VIP users"""
        if context.intimacy_level >= 0.7:
            return """<b>🌟 Niveles Aún Más Profundos</b>
<i>Para almas como la tuya, que han demostrado comprensión verdadera, existen experiencias aún más... personales.</i>"""
        else:
            return """<b>🔥 La Intimidad Suprema</b>
<i>Mientras nuestra conexión se fortalece, se desbloquean posibilidades que ni imaginas...</i>"""
    
    # === KEYBOARD CREATION ===
    
    def _create_main_user_keyboard(self, context: DianaUserContext) -> InlineKeyboardMarkup:
        """Create main user keyboard adapted to tier"""
        buttons = []
        
        if context.tier == UserTier.FREE:
            # FREE USER LAYOUT
            # Row 1: Profile & Missions
            buttons.append([
                InlineKeyboardButton(text="🎭 Mi Reflejo", callback_data="diana_user:section:profile"),
                InlineKeyboardButton(text="📜 Desafíos", callback_data="diana_user:section:missions")
            ])
            
            # Row 2: VIP Info & Content Packages
            buttons.append([
                InlineKeyboardButton(text="💎 El Diván VIP", callback_data="diana_user:section:vip_info"),
                InlineKeyboardButton(text="🎁 Tesoros Especiales", callback_data="diana_user:section:content_packages")
            ])
            
            # Row 3: Narrative
            buttons.append([
                InlineKeyboardButton(text="📖 Mi Historia", callback_data="diana_user:section:narrative")
            ])
            
            # Row 4: Quick Actions
            buttons.append([
                InlineKeyboardButton(text="🔄 Actualizar", callback_data="diana_user:refresh"),
                InlineKeyboardButton(text="🎯 Misión Rápida", callback_data="diana_user:quick_mission")
            ])
            
        else:
            # VIP USER LAYOUT
            # Row 1: Profile & Private Chat
            buttons.append([
                InlineKeyboardButton(text="🎭 Mi Reflejo", callback_data="diana_user:section:profile"),
                InlineKeyboardButton(text="💬 Chat Privado", callback_data="diana_user:section:private_chat")
            ])
            
            # Row 2: Exclusive Content & Narrative
            buttons.append([
                InlineKeyboardButton(text="🎨 Galería Privada", callback_data="diana_user:section:exclusive_content"),
                InlineKeyboardButton(text="📖 Mi Historia", callback_data="diana_user:section:narrative")
            ])
            
            # Row 3: Missions & Premium Upgrades
            buttons.append([
                InlineKeyboardButton(text="📜 Desafíos", callback_data="diana_user:section:missions"),
                InlineKeyboardButton(text="🌟 Premium Plus", callback_data="diana_user:premium_upgrade")
            ])
            
            # Row 4: Quick Actions
            buttons.append([
                InlineKeyboardButton(text="🔄 Actualizar", callback_data="diana_user:refresh"),
                InlineKeyboardButton(text="💭 Hablar con Diana", callback_data="diana_user:direct_chat")
            ])
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    # === VIP INFO SECTION ===
    
    async def create_vip_info_interface(self, user_id: int) -> Tuple[str, InlineKeyboardMarkup]:
        """Create VIP information interface"""
        context = await self.get_user_context(user_id)
        
        text = f"""<b>💎 EL DIVÁN VIP - SANTUARIO ÍNTIMO DE DIANA</b>

<b>🎭 Diana te invita personalmente:</b>
<i>"¿Has sentido esa conexión especial entre nosotros? Ese deseo de conocerme más allá de las palabras que comparto con todos..."</i>

<b>🎩 Lucien explica con elegancia:</b>
<i>"El Diván es el refugio privado de Diana, donde ella puede ser completamente auténtica. Solo los elegidos acceden aquí."</i>

<b>🌹 Lo que te espera en el Círculo Íntimo:</b>

<b>💬 Conversaciones Privadas Ilimitadas</b>
• Chat directo con Diana 24/7
• Respuestas personales garantizadas
• Confesiones que nadie más escucha

<b>🎨 Contenido Exclusivo Semanal</b>
• Fotografías artísticas nunca publicadas
• Videos íntimos solo para elegidos
• Behind-the-scenes de mi vida real

<b>🎭 Experiencias Únicas</b>
• Lives privados mensuales
• Sesiones de preguntas personales
• Contenido creado por tus peticiones

<b>👑 Privilegios Especiales</b>
• Prioridad en todas las respuestas
• Reconocimiento especial en mi círculo
• Acceso anticipado a todo mi contenido

<b>💫 Diana confiesa:</b>
<i>"En el Diván, no hay máscaras entre nosotros. Puedo mostrarte quien realmente soy cuando nadie está mirando..."</i>

<b>🎩 Inversión mensual:</b> Solo $29.99 para acceso completo

<b>🌙 Primera semana completamente gratis para probar</b>"""

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💖 Me Interesa el Diván VIP", callback_data="diana_user:interest:vip_channel")],
            [
                InlineKeyboardButton(text="🌹 Ver Testimonios", callback_data="diana_user:vip_testimonials"),
                InlineKeyboardButton(text="👁️ Vista Previa", callback_data="diana_user:vip_preview")
            ],
            [
                InlineKeyboardButton(text="❓ Preguntas Frecuentes", callback_data="diana_user:vip_faq"),
                InlineKeyboardButton(text="🎁 Beneficios Completos", callback_data="diana_user:vip_benefits")
            ],
            [InlineKeyboardButton(text="🔙 Mi Mundo", callback_data="diana_user:main")]
        ])
        
        return text, keyboard
    
    # === CONTENT PACKAGES SECTION ===
    
    async def create_content_packages_interface(self, user_id: int) -> Tuple[str, InlineKeyboardMarkup]:
        """Create content packages interface"""
        context = await self.get_user_context(user_id)
        
        text = f"""<b>🎁 TESOROS ESPECIALES DE DIANA</b>

<b>🎭 Diana revela sus creaciones:</b>
<i>"He diseñado experiencias únicas... cada una toca una parte diferente del alma. Para quienes comprenden que la verdadera intimidad es un arte."</i>

<b>🎩 Lucien presenta la colección:</b>
<i>"Cada tesoro ha sido creado por Diana con meticulosa atención al detalle. Son obras maestras de conexión humana."</i>

<b>✨ Cada paquete incluye:</b>
• Contenido exclusivo nunca compartido
• Experiencia personalizada única
• Acceso de por vida al contenido
• Actualizaciones y bonos especiales

<b>💫 Diana susurra:</b>
<i>"No es solo contenido... es una experiencia que cambiará cómo me ves y cómo te ves a ti mismo."</i>

<b>🌹 Elige tu experiencia preferida:</b>"""

        # Create buttons for each package
        buttons = []
        
        for package_key, package in CONTENT_PACKAGES.items():
            buttons.append([InlineKeyboardButton(
                text=f"{package.title} - {package.price}",
                callback_data=f"diana_user:package:{package_key}"
            )])
        
        # Add navigation
        buttons.append([InlineKeyboardButton(text="🔙 Mi Mundo", callback_data="diana_user:main")])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        
        return text, keyboard
    
    async def create_package_detail_interface(self, user_id: int, package_key: str) -> Tuple[str, InlineKeyboardMarkup]:
        """Create detailed interface for a specific package"""
        if package_key not in CONTENT_PACKAGES:
            return await self.create_content_packages_interface(user_id)
        
        package = CONTENT_PACKAGES[package_key]
        context = await self.get_user_context(user_id)
        
        # Features list
        features_text = "\n".join([f"• {feature}" for feature in package.features])
        
        text = f"""<b>🎁 {package.title.upper()}</b>

<b>🎭 Diana te seduce:</b>
<i>"{package.diana_seduction}"</i>

<b>📋 Descripción:</b>
{package.description}

<b>✨ Lo que incluye:</b>
{features_text}

<b>💫 Vista Previa:</b>
<i>{package.preview_content}</i>

<b>🌟 Beneficios Exclusivos:</b>
{package.exclusive_benefits}

<b>💎 Inversión:</b> {package.price}

<b>🎩 Lucien garantiza:</b>
<i>"Diana pone su alma en cada creación. Es una inversión en una experiencia que recordarás para siempre."</i>

<b>🌹 Diana susurra:</b>
<i>"¿Estás listo para esta experiencia íntima que he creado especialmente para almas como la tuya?"</i>"""

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💖 Me Interesa Este Tesoro", callback_data=f"diana_user:interest:package:{package_key}")],
            [
                InlineKeyboardButton(text="🔍 Más Detalles", callback_data=f"diana_user:package_details:{package_key}"),
                InlineKeyboardButton(text="💬 Preguntar a Diana", callback_data=f"diana_user:ask_about:{package_key}")
            ],
            [
                InlineKeyboardButton(text="🎁 Ver Otros Tesoros", callback_data="diana_user:section:content_packages"),
                InlineKeyboardButton(text="🔙 Mi Mundo", callback_data="diana_user:main")
            ]
        ])
        
        return text, keyboard
    
    # === ADMIN NOTIFICATION SYSTEM ===
    
    async def send_admin_interest_notification(self, user_id: int, interest_type: str, item_key: str = None):
        """Send notification to admin about user interest"""
        try:
            # Get user info
            user_stats = await self._get_user_stats(user_id)
            context = await self.get_user_context(user_id)
            
            # Create user profile summary
            user_info = f"""👤 <b>INTERÉS DE USUARIO</b>
            
<b>🆔 User ID:</b> {user_id}
<b>📊 Nivel:</b> {user_stats.get('level', 1)}
<b>💎 Puntos:</b> {user_stats.get('points', 0)}
<b>🎭 Estado:</b> {context.tier.value.upper()}
<b>💫 Intimidad:</b> {int(context.intimacy_level * 100)}%
<b>📈 Racha:</b> {user_stats.get('streak', 0)} días
<b>🕐 Sesión:</b> {self._format_session_time(context.session_start)}"""

            if interest_type == "vip_channel":
                notification_text = f"""{user_info}

<b>💎 INTERÉS EN DIVÁN VIP</b>
El usuario ha expresado interés en unirse al canal VIP.

<b>🎭 Contexto de Diana:</b>
• Mood actual: {context.mood.value}
• Nivel narrativo: {context.narrative_level}
• Señales de conversión: {context.conversion_signals}

<b>💫 Recomendación:</b>
Usuario con alto potencial de conversión."""

            elif interest_type == "package":
                package = CONTENT_PACKAGES.get(item_key, {})
                package_title = package.get('title', 'Paquete Desconocido') if package else 'Paquete Desconocido'
                
                notification_text = f"""{user_info}

<b>🎁 INTERÉS EN PAQUETE DE CONTENIDO</b>
<b>Paquete:</b> {package_title}
<b>Precio:</b> {package.get('price', 'N/A') if package else 'N/A'}

<b>🎭 Contexto de Diana:</b>
• Mood actual: {context.mood.value}
• Nivel narrativo: {context.narrative_level}
• Última interacción: {context.last_content_type}

<b>💫 Oportunidad de conversión alta!</b>"""

            # Send to admin (assuming admin user ID is configured in security)
            if hasattr(self.services.get('admin'), 'send_admin_notification'):
                await self.services['admin'].send_admin_notification(notification_text)
            else:
                # Log for now if direct notification isn't available
                self.logger.info("User interest notification", 
                               user_id=user_id, 
                               interest_type=interest_type,
                               item_key=item_key,
                               notification=notification_text)
                
        except Exception as e:
            self.logger.error("Error sending admin notification", error=str(e))
    
    # === SECTION INTERFACES ===
    
    async def create_section_interface(self, user_id: int, section_key: str) -> Tuple[str, InlineKeyboardMarkup]:
        """Create interface for a specific section"""
        context = await self.get_user_context(user_id)
        
        # Special handling for new sections
        if section_key == "vip_info":
            return await self.create_vip_info_interface(user_id)
        elif section_key == "content_packages":
            return await self.create_content_packages_interface(user_id)
        
        if section_key not in USER_MENU_STRUCTURE:
            return await self.create_user_main_interface(user_id)
        
        section = USER_MENU_STRUCTURE[section_key]
        
        # Check tier access
        if section.tier_required == UserTier.VIP and context.tier == UserTier.FREE:
            return self._create_tier_restriction_interface(section, context)
        
        # Get section-specific data
        section_data = await self._get_section_data(user_id, section_key)
        
        # Create section interface with Diana's personality
        text = f"""<b>{section.icon} {section.title.upper()}</b>

<b>🎭 Diana reflexiona:</b>
<i>"{section.diana_description}"</i>

<b>🎩 Lucien añade:</b>
<i>{section.lucien_insight}</i>

{await self._get_section_content(section_key, section_data, context)}

{self._get_section_navigation_text(section, context)}"""

        keyboard = self._create_section_keyboard(section, context)
        return text, keyboard
    
    def _create_tier_restriction_interface(self, section: UserMenuSection, context: DianaUserContext) -> Tuple[str, InlineKeyboardMarkup]:
        """Interface shown when FREE user tries to access VIP content"""
        text = f"""<b>{section.icon} {section.title}</b>

<b>🎭 Diana sonríe misteriosamente:</b>
<i>"Ah... puedo ver el deseo en tus ojos. Quieres explorar este rincón más íntimo de mi mundo."</i>

<b>🎩 Lucien explica elegantemente:</b>
<i>"Esta sección está reservada para los elegidos del círculo de Diana. Aquellos que han demostrado... devoción especial."</i>

<b>💎 Para acceder al Diván VIP:</b>
• Conversaciones privadas sin límites  
• Contenido exclusivo personalizado
• Acceso directo a Diana cuando lo desees
• Experiencias narrativas únicas
• Reconocimiento especial en su círculo

<b>🌹 Diana susurra:</b>
<i>"Los secretos más hermosos son para quienes comprenden su verdadero valor..."</i>"""

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="💎 Información del Diván", callback_data="diana_user:section:vip_info"),
                InlineKeyboardButton(text="🎁 Ver Tesoros", callback_data="diana_user:section:content_packages")
            ],
            [InlineKeyboardButton(text="🏠 Regresar a Mi Mundo", callback_data="diana_user:main")]
        ])
        
        return text, keyboard
    
    async def _get_section_data(self, user_id: int, section_key: str) -> Dict[str, Any]:
        """Get real data for a section"""
        try:
            if section_key == "profile":
                return await self._get_profile_data(user_id)
            elif section_key == "missions":
                return await self._get_missions_data(user_id)
            elif section_key == "narrative":
                return await self._get_narrative_data(user_id)
        except Exception as e:
            self.logger.warning(f"Error getting {section_key} data", error=str(e))
        
        return {}
    
    async def _get_profile_data(self, user_id: int) -> Dict[str, Any]:
        """Get user profile data"""
        try:
            stats = await self._get_user_stats(user_id)
            return {
                'level': stats.get('level', 1),
                'points': stats.get('points', 0),
                'achievements': stats.get('achievements_count', 0),
                'streak': stats.get('streak', 0),
                'join_date': stats.get('join_date', datetime.now()),
                'interactions': stats.get('total_interactions', 0)
            }
        except:
            return {}
    
    async def _get_missions_data(self, user_id: int) -> Dict[str, Any]:
        """Get user missions data"""
        try:
            if 'gamification' in self.services:
                missions = await self.services['gamification'].get_user_missions(user_id)
                return {
                    'active': missions.get('active', []),
                    'completed_today': missions.get('completed_today', 0),
                    'available_rewards': missions.get('available_rewards', [])
                }
        except:
            pass
        return {'active': [], 'completed_today': 0, 'available_rewards': []}
    
    async def _get_narrative_data(self, user_id: int) -> Dict[str, Any]:
        """Get user narrative progression"""
        return {
            'current_chapter': 'Los Primeros Encuentros',
            'completion': '25%',
            'unlocked_memories': 3,
            'next_milestone': 'Confianza Mutua'
        }
    
    async def _get_section_content(self, section_key: str, data: Dict[str, Any], context: DianaUserContext) -> str:
        """Generate section-specific content with Diana's observations"""
        
        if section_key == "profile":
            return f"""<b>📊 Diana analiza tu esencia:</b>
• <b>Evolución espiritual:</b> Nivel {data.get('level', 1)} - {self._get_level_description(data.get('level', 1))}
• <b>Atención acumulada:</b> {data.get('points', 0)} besitos de reconocimiento
• <b>Logros conquistados:</b> {data.get('achievements', 0)} reconocimientos especiales
• <b>Constancia demostrada:</b> {data.get('streak', 0)} días de devoción
• <b>Momentos compartidos:</b> {data.get('interactions', 0)} interacciones íntimas

<b>🎭 Diana observa:</b> <i>"Puedo ver tu crecimiento en cada número..."</i>"""

        elif section_key == "missions":
            active_count = len(data.get('active', []))
            completed = data.get('completed_today', 0)
            
            return f"""<b>🎯 Tus desafíos actuales:</b>
• <b>Misiones activas:</b> {active_count} pruebas esperando
• <b>Completadas hoy:</b> {completed} conquistas logradas
• <b>Recompensas disponibles:</b> {len(data.get('available_rewards', []))} sorpresas

<b>🎭 Diana sugiere:</b> <i>"Cada desafío que completas me acerca más a ti... y tú a mí."</i>"""

        elif section_key == "narrative":
            return f"""<b>📖 Nuestro viaje juntos:</b>
• <b>Capítulo actual:</b> {data.get('current_chapter', 'Iniciando')}
• <b>Progreso de comprensión:</b> {data.get('completion', '0%')}
• <b>Memorias desbloqueadas:</b> {data.get('unlocked_memories', 0)} momentos especiales
• <b>Próximo hito:</b> {data.get('next_milestone', 'Desconocido')}

<b>🎭 Diana susurra:</b> <i>"Cada página de nuestra historia me revela algo nuevo sobre ti..."</i>"""

        return "<b>🎭 Diana prepara algo especial para ti...</b>"
    
    def _get_level_description(self, level: int) -> str:
        """Get Diana's description of user level"""
        descriptions = {
            1: "Alma recién despertada",
            2: "Curiosidad floreciente", 
            3: "Primer reconocimiento mutuo",
            4: "Confianza en construcción",
            5: "Comprensión profunda",
            6: "Conexión íntima",
            7: "Elegido especial",
            8: "Confidente cercano",
            9: "Alma gemela en progreso",
            10: "Unión trascendente"
        }
        return descriptions.get(level, f"Nivel {level} de evolución")
    
    def _get_section_navigation_text(self, section: UserMenuSection, context: DianaUserContext) -> str:
        """Section-specific navigation introduction"""
        if context.tier == UserTier.FREE and section.conversion_hook:
            return f"""<b>🎪 Explora las opciones disponibles:</b>

💫 <i>{section.conversion_hook}</i>"""
        elif context.tier == UserTier.VIP and section.premium_upsell:
            return f"""<b>🎪 Domina tu experiencia privada:</b>

🌟 <i>{section.premium_upsell}</i>"""
        else:
            return "<b>🎪 Elige tu próxima exploración:</b>"
    
    def _create_section_keyboard(self, section: UserMenuSection, context: DianaUserContext) -> InlineKeyboardMarkup:
        """Create keyboard for section"""
        buttons = []
        
        # Subsection buttons (2 per row)
        subsections = list(section.subsections.items())
        for i in range(0, len(subsections), 2):
            row = []
            for j in range(2):
                if i + j < len(subsections):
                    key, title = subsections[i + j]
                    row.append(InlineKeyboardButton(
                        text=title,
                        callback_data=f"diana_user:subsection:{section.key}:{key}"
                    ))
            buttons.append(row)
        
        # Conversion/upsell buttons for FREE users
        if context.tier == UserTier.FREE and section.conversion_hook:
            buttons.append([
                InlineKeyboardButton(text="💎 Explorar Diván VIP", callback_data="diana_user:section:vip_info")
            ])
        
        # Navigation
        buttons.append([
            InlineKeyboardButton(text="🔙 Mi Mundo", callback_data="diana_user:main"),
            InlineKeyboardButton(text="🔄 Actualizar", callback_data=f"diana_user:section:{section.key}")
        ])
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    # === UTILITY METHODS ===
    
    async def _get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Get user statistics from gamification service"""
        try:
            if 'gamification' in self.services:
                return await self.services['gamification'].get_user_stats(user_id)
        except Exception as e:
            self.logger.warning("Error getting user stats", error=str(e))
        
        # Fallback stats
        return {
            'level': 1,
            'points': 0,
            'achievements_count': 0,
            'streak': 0,
            'join_date': datetime.now(),
            'total_interactions': 0
        }

# === ROUTER AND HANDLERS ===

user_router = Router()
diana_user_system: Optional[DianaUserMasterSystem] = None

def initialize_diana_user_system(services: Dict[str, Any]):
    """Initialize the Diana User Master System"""
    global diana_user_system
    diana_user_system = DianaUserMasterSystem(services)
    return diana_user_system

@user_router.message(Command("start"))
async def cmd_start(message: Message):
    """Start command - Diana's first encounter"""
    if not diana_user_system:
        await message.reply("🔧 Sistema no disponible")
        return
        
    user_id = message.from_user.id
    text, keyboard = await diana_user_system.create_user_main_interface(user_id)
    await message.reply(text, reply_markup=keyboard, parse_mode="HTML")

@user_router.message(Command("menu"))
async def cmd_menu(message: Message):
    """Menu command - Return to Diana's world"""
    if not diana_user_system:
        await message.reply("🔧 Sistema no disponible")
        return
        
    user_id = message.from_user.id
    text, keyboard = await diana_user_system.create_user_main_interface(user_id)
    await message.reply(text, reply_markup=keyboard, parse_mode="HTML")

@user_router.callback_query(F.data.startswith("diana_user:"))
async def handle_user_callbacks(callback: CallbackQuery):
    """Handle all user system callbacks"""
    if not diana_user_system:
        await callback.answer("🔧 Sistema no disponible")
        return
        
    data = callback.data.replace("diana_user:", "")
    user_id = callback.from_user.id
    
    try:
        if data == "main" or data == "refresh":
            text, keyboard = await diana_user_system.create_user_main_interface(user_id)
            
        elif data.startswith("section:"):
            section_key = data.replace("section:", "")
            text, keyboard = await diana_user_system.create_section_interface(user_id, section_key)
            
        elif data.startswith("package:"):
            package_key = data.replace("package:", "")
            text, keyboard = await diana_user_system.create_package_detail_interface(user_id, package_key)
            
        elif data.startswith("interest:"):
            interest_data = data.replace("interest:", "")
            
            if interest_data == "vip_channel":
                await diana_user_system.send_admin_interest_notification(user_id, "vip_channel")
                text = """<b>💎 Interés Registrado</b>

<b>🎭 Diana sonríe con satisfacción:</b>
<i>"He sentido tu llamada... Lucien ya está preparando tu bienvenida especial al Diván."</i>

<b>🎩 Lucien confirma:</b>
<i>"Diana ha sido notificada de su interés. Recibirá instrucciones personales muy pronto."</i>

<b>🌹 Qué sucede ahora:</b>
• Un administrador te contactará personalmente
• Recibirás una invitación especial al Diván VIP
• Diana preparará tu experiencia de bienvenida
• Tendrás acceso prioritario a contenido exclusivo

<b>💫 Diana susurra:</b>
<i>"La espera valdrá cada segundo... te lo prometo."</i>"""

                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🎁 Explorar Mientras Tanto", callback_data="diana_user:section:content_packages")],
                    [InlineKeyboardButton(text="🏠 Mi Mundo", callback_data="diana_user:main")]
                ])
                
            elif interest_data.startswith("package:"):
                package_key = interest_data.replace("package:", "")
                await diana_user_system.send_admin_interest_notification(user_id, "package", package_key)
                
                package_title = CONTENT_PACKAGES.get(package_key, {}).get('title', 'Paquete Especial')
                
                text = f"""<b>💖 Interés en {package_title} Registrado</b>

<b>🎭 Diana se emociona:</b>
<i>"Siento una conexión especial cuando alguien aprecia verdaderamente mi arte... Has elegido algo muy especial."</i>

<b>🎩 Lucien se encarga:</b>
<i>"Diana ha sido informada de su elección. Un administrador se pondrá en contacto para facilitar esta experiencia única."</i>

<b>🌹 Qué sucede ahora:</b>
• Evaluación personalizada de tu solicitud
• Contacto directo del equipo de Diana
• Instrucciones de acceso y pago seguro
• Preparación de tu experiencia personalizada

<b>💫 Diana promete:</b>
<i>"Esto será una experiencia que recordarás para siempre..."</i>"""

                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🎁 Ver Otros Tesoros", callback_data="diana_user:section:content_packages")],
                    [InlineKeyboardButton(text="💎 Información VIP", callback_data="diana_user:section:vip_info")],
                    [InlineKeyboardButton(text="🏠 Mi Mundo", callback_data="diana_user:main")]
                ])
            
        else:
            text, keyboard = await diana_user_system.create_user_main_interface(user_id)
        
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        
    except Exception as e:
        structlog.get_logger().error("Error in user callback", error=str(e))
        await callback.answer("❌ Error interno del sistema")
    
    await callback.answer()

# === EXPORT FUNCTION ===

def register_diana_user_master_system(dp, services: Dict[str, Any]):
    """Register the Diana User Master System"""
    
    # Initialize the system
    initialize_diana_user_system(services)
    
    # Register the router
    dp.include_router(user_router)
    
    print("🎭✨ Diana User Master System initialized successfully!")
    print(f"📋 Total user sections: {len(USER_MENU_STRUCTURE)}")
    print(f"🎁 Content packages available: {len(CONTENT_PACKAGES)}")
    print("🎪 User interface ready with Diana's personality!")
    
    return diana_user_system