"""
🎭 DIANA MASTER SYSTEM - CORE HANDLERS FASE 2
===========================================

Advanced UI handlers for the Diana Master System.
These handlers provide sophisticated, adaptive interfaces for
the core Diana experience.

Author: UI Component Builder Agent
Version: 2.0.0 - FASE 2 Implementation
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import random

from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import structlog

# Import the helper function for safe message editing
from src.bot.core.diana_master_system import safe_edit_message, UserMoodState

logger = structlog.get_logger()


async def handle_progress_tracker(callback: CallbackQuery, diana_master):
    """📊 Advanced Progress Dashboard - FASE 2 Implementation"""
    user_id = callback.from_user.id
    
    # Get comprehensive user context
    context = await diana_master.context_engine.analyze_user_context(user_id)
    
    # Gather data from all services
    try:
        if hasattr(diana_master.services['gamification'], 'get_user_points'):
            gamification_data = await diana_master.services['gamification'].get_user_points(user_id)
        else:
            gamification_data = {
                'level': 3, 'points': 1250, 'streak': 7,
                'total_questions': 45, 'correct_answers': 38,
                'achievements': ['🔰 Novato', '🧠 Sabio', '🔥 Racha 7'],
                'efficiency_score': 84.4
            }
    except:
        gamification_data = {'level': 1, 'points': 0, 'streak': 0}
    
    # Build comprehensive progress dashboard
    progress_text = "📊 **DASHBOARD DE PROGRESO AVANZADO**\n\n"
    
    # Personalized greeting based on mood
    if context.current_mood == UserMoodState.OPTIMIZER:
        progress_text += "⚙️ *Análisis completo de tu rendimiento optimizado*\n\n"
    elif context.current_mood == UserMoodState.ACHIEVER:
        progress_text += "🏆 *Tu hoja de conquistas y logros épicos*\n\n"
    else:
        progress_text += "🌟 *Resumen completo de tu aventura en Diana*\n\n"
    
    # Core Stats Section
    progress_text += "**📈 ESTADÍSTICAS PRINCIPALES**\n"
    progress_text += f"⭐ Nivel: {gamification_data.get('level', 1)} | 💰 Besitos: {gamification_data.get('points', 0):,}\n"
    progress_text += f"🔥 Racha actual: {gamification_data.get('streak', 0)} días\n"
    progress_text += f"📚 Preguntas respondidas: {gamification_data.get('total_questions', 0)}\n"
    progress_text += f"✅ Precisión: {(gamification_data.get('correct_answers', 0) / max(gamification_data.get('total_questions', 1), 1) * 100):.1f}%\n\n"
    
    # Performance Analytics Section
    efficiency = gamification_data.get('efficiency_score', 75.0)
    progress_text += "**📊 ANÁLISIS DE RENDIMIENTO**\n"
    progress_text += f"⚙️ Puntuación de eficiencia: {efficiency:.1f}%\n"
    
    # Performance trend analysis
    if efficiency > 85:
        trend = "📈 Excelente - Rendimiento superior"
    elif efficiency > 70:
        trend = "📊 Bueno - Progreso constante"
    else:
        trend = "📉 Mejorable - Oportunidades de crecimiento"
    
    progress_text += f"📈 Tendencia: {trend}\n"
    progress_text += f"🎯 Objetivos completados: {len(gamification_data.get('achievements', []))}/10\n\n"
    
    # Achievements Section
    achievements = gamification_data.get('achievements', [])
    if achievements:
        progress_text += "**🏆 LOGROS DESBLOQUEADOS**\n"
        for achievement in achievements[:5]:  # Show top 5
            progress_text += f"• {achievement}\n"
        if len(achievements) > 5:
            progress_text += f"• ... y {len(achievements) - 5} más\n"
    else:
        progress_text += "**🏆 LOGROS**\n• 🎯 ¡Completa tu primera trivia para empezar!\n"
    
    progress_text += "\n"
    
    # Weekly Progress
    progress_text += "**📅 PROGRESO SEMANAL**\n"
    weekly_progress = min(gamification_data.get('streak', 0) * 14.3, 100)  # Mock weekly calculation
    progress_text += f"📊 Esta semana: {weekly_progress:.1f}% completado\n"
    progress_text += f"🎯 Meta semanal: {'✅ Alcanzada' if weekly_progress > 70 else '⏳ En progreso'}\n\n"
    
    # Next Level Preview
    current_level = gamification_data.get('level', 1)
    points_to_next = (current_level + 1) * 500 - gamification_data.get('points', 0)
    if points_to_next > 0:
        progress_text += "**🎯 PRÓXIMO NIVEL**\n"
        progress_text += f"🌟 Nivel {current_level + 1}: Faltan {points_to_next:,} besitos\n"
        progress_text += f"📊 Progreso: {min(85, (gamification_data.get('points', 0) / ((current_level + 1) * 500)) * 100):.1f}%"
    else:
        progress_text += "**👑 NIVEL MÁXIMO ALCANZADO**\n"
        progress_text += "🎉 ¡Eres una leyenda de Diana!"
    
    # Build adaptive keyboard
    keyboard_buttons = []
    
    # First row - Core actions
    keyboard_buttons.append([
        InlineKeyboardButton(text="🎯 Ver Misiones", callback_data="diana:missions_hub"),
        InlineKeyboardButton(text="🏆 Motor de Logros", callback_data="diana:achievement_engine")
    ])
    
    # Second row - Advanced Analytics (Enhanced with gamification)
    keyboard_buttons.append([
        InlineKeyboardButton(text="💰 Calculadora Rewards", callback_data="diana:reward_calculator"),
        InlineKeyboardButton(text="🏆 Rankings", callback_data="diana:leaderboard_system")
    ])
    
    # Third row - Mood-specific actions
    if context.current_mood == UserMoodState.OPTIMIZER:
        keyboard_buttons.append([
            InlineKeyboardButton(text="⚙️ Optimizar Rendimiento", callback_data="diana:optimize_performance"),
            InlineKeyboardButton(text="📊 Métricas Avanzadas", callback_data="diana:advanced_metrics")
        ])
    elif context.current_mood == UserMoodState.ACHIEVER:
        keyboard_buttons.append([
            InlineKeyboardButton(text="🏆 Nuevos Desafíos", callback_data="diana:new_challenges"),
            InlineKeyboardButton(text="⚡ Misión Rápida", callback_data="diana:quick_mission")
        ])
    else:
        keyboard_buttons.append([
            InlineKeyboardButton(text="🎲 Sorpréndeme", callback_data="diana:surprise_me"),
            InlineKeyboardButton(text="📖 Mi Historia", callback_data="diana:narrative_hub")
        ])
    
    # Navigation row
    keyboard_buttons.append([
        InlineKeyboardButton(text="🔄 Actualizar", callback_data="diana:progress_tracker"),
        InlineKeyboardButton(text="🏠 Volver al Inicio", callback_data="diana:refresh")
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await safe_edit_message(callback, progress_text, keyboard)


async def handle_pro_dashboard(callback: CallbackQuery, diana_master):
    """📊 Professional Control Panel - FASE 2 Implementation"""
    user_id = callback.from_user.id
    
    # Get user context and system state
    context = await diana_master.context_engine.analyze_user_context(user_id)
    system_state = await diana_master._get_system_state()
    
    # Advanced dashboard for power users
    dashboard_text = "📊 **CENTRO DE CONTROL PROFESIONAL**\n\n"
    dashboard_text += "⚙️ *Panel de control avanzado para usuarios expertos*\n\n"
    
    # System Overview
    dashboard_text += "**🖥️ ESTADO DEL SISTEMA**\n"
    dashboard_text += f"🟢 Estado: Operativo\n"
    dashboard_text += f"⚡ Carga del sistema: {system_state.get('system_load', 'Normal').title()}\n"
    dashboard_text += f"👥 Usuarios activos: {system_state.get('active_tariffs', 0)}\n"
    dashboard_text += f"🕐 Uptime: 99.9%\n\n"
    
    # User Analytics
    dashboard_text += "**📊 TUS MÉTRICAS AVANZADAS**\n"
    dashboard_text += f"🎯 Sesión actual: {context.session_duration} minutos\n"
    dashboard_text += f"📈 Patrón de uso: {context.engagement_pattern.replace('_', ' ').title()}\n"
    dashboard_text += f"🧠 Precisión personal: {context.personalization_score * 100:.1f}%\n"
    dashboard_text += f"🎭 Estado detectado: {context.current_mood.value.title()}\n\n"
    
    # Performance Insights
    dashboard_text += "**⚡ INSIGHTS DE RENDIMIENTO**\n"
    efficiency = 87.5  # Mock advanced efficiency calculation
    dashboard_text += f"📊 Eficiencia global: {efficiency}%\n"
    dashboard_text += f"🎲 Sesiones completadas: {len(context.last_actions)}/10\n"
    dashboard_text += f"🔥 Streak de rendimiento: {'Alto' if efficiency > 80 else 'Medio'}\n"
    dashboard_text += f"📱 Dispositivo optimizado: ✅ Android\n\n"
    
    # Advanced Features
    dashboard_text += "**🛠️ HERRAMIENTAS PROFESIONALES**\n"
    dashboard_text += "• 📈 Analytics en tiempo real\n"
    dashboard_text += "• ⚙️ Configuración avanzada\n"
    dashboard_text += "• 🎯 Objetivos personalizados\n"
    dashboard_text += "• 🔍 Análisis predictivo\n"
    dashboard_text += "• 📊 Exportar datos\n\n"
    
    # Recommendations
    dashboard_text += "**💡 RECOMENDACIONES IA**\n"
    if context.current_mood == UserMoodState.OPTIMIZER:
        dashboard_text += "• ⚡ Tu patrón de uso es óptimo\n"
        dashboard_text += "• 📊 Considera explorar métricas avanzadas\n"
        dashboard_text += "• 🎯 Perfecto momento para nuevos desafíos"
    else:
        dashboard_text += "• 🎲 Prueba funciones de automatización\n"
        dashboard_text += "• 📈 Revisa tus patrones de actividad\n"
        dashboard_text += "• ⚙️ Personaliza tu experiencia"
    
    # Build professional keyboard
    keyboard_buttons = []
    
    # Advanced Gamification Tools (FASE 2.3 Enhancement)
    keyboard_buttons.append([
        InlineKeyboardButton(text="🏆 Motor de Logros", callback_data="diana:achievement_engine"),
        InlineKeyboardButton(text="💰 Calculadora Rewards", callback_data="diana:reward_calculator")
    ])
    
    # Professional analytics and leaderboards
    keyboard_buttons.append([
        InlineKeyboardButton(text="🏆 Sistema Rankings", callback_data="diana:leaderboard_system"),
        InlineKeyboardButton(text="⚙️ Config Gamificación", callback_data="diana:gamification_settings")
    ])
    
    # Automation row
    keyboard_buttons.append([
        InlineKeyboardButton(text="🤖 Automatización", callback_data="diana:automation_center"),
        InlineKeyboardButton(text="🎯 Objetivos Custom", callback_data="diana:custom_goals")
    ])
    
    # Advanced features row
    keyboard_buttons.append([
        InlineKeyboardButton(text="🔍 Análisis Predictivo", callback_data="diana:predictive_analysis"),
        InlineKeyboardButton(text="🛠️ Herramientas Dev", callback_data="diana:dev_tools")
    ])
    
    # Navigation
    keyboard_buttons.append([
        InlineKeyboardButton(text="🔄 Actualizar Panel", callback_data="diana:pro_dashboard"),
        InlineKeyboardButton(text="🏠 Dashboard Normal", callback_data="diana:refresh")
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await safe_edit_message(callback, dashboard_text, keyboard)


async def handle_explore_mode(callback: CallbackQuery, diana_master):
    """🗺️ Discovery Interface - FASE 2 Implementation"""
    user_id = callback.from_user.id
    context = await diana_master.context_engine.analyze_user_context(user_id)
    
    explore_text = "🗺️ **MODO EXPLORACIÓN ACTIVADO**\n\n"
    explore_text += "🌟 *Descubre territorios inexplorados del universo Diana*\n\n"
    
    # Dynamic exploration content based on user level/progress
    user_level = 3  # Mock user level
    exploration_progress = context.narrative_progress
    
    # Available exploration zones
    explore_text += "**🌍 TERRITORIOS DISPONIBLES**\n\n"
    
    # Zone 1: Always available
    explore_text += "🌅 **ZONA NOVATO** - *Territorio Inicial*\n"
    explore_text += "• 🎲 Trivias básicas desbloqueadas\n"
    explore_text += "• 🎁 Recompensas diarias activas\n"
    explore_text += "• 📖 Capítulos 1-3 de la historia\n"
    explore_text += f"✅ Estado: Dominado {min(100, exploration_progress + 20):.0f}%\n\n"
    
    # Zone 2: Level 2+
    if user_level >= 2:
        explore_text += "🌙 **ZONA INTERMEDIA** - *Territorio Misterioso*\n"
        explore_text += "• 🧠 Trivias avanzadas disponibles\n"
        explore_text += "• 🏆 Sistema de logros épicos\n"
        explore_text += "• 🛒 Tienda VIP desbloqueada\n"
        explore_text += f"⏳ Estado: En progreso {min(75, exploration_progress):.0f}%\n\n"
    
    # Zone 3: Level 5+
    if user_level >= 5:
        explore_text += "⭐ **ZONA ÉPICA** - *Reino Legendario*\n"
        explore_text += "• 👑 Misiones épicas legendarias\n"
        explore_text += "• 🎭 Historia narrativa completa\n"
        explore_text += "• 💎 Objetos únicos exclusivos\n"
        explore_text += f"🔒 Estado: Bloqueado - Requiere nivel 5\n\n"
    
    # Secret areas
    if exploration_progress > 50:
        explore_text += "🔮 **ÁREA SECRETA DETECTADA**\n"
        explore_text += "• ❓ Contenido misterioso disponible\n"
        explore_text += "• 🗝️ Requiere clave especial\n"
        explore_text += "• 🏆 Recompensas únicas\n\n"
    
    # Exploration tools
    explore_text += "**🧭 HERRAMIENTAS DE EXPLORACIÓN**\n"
    explore_text += "• 🔍 Radar de oportunidades\n"
    explore_text += "• 🗺️ Mapa de progreso\n"
    explore_text += "• 🎯 Brújula de objetivos\n"
    explore_text += "• 💡 Detector de secretos\n\n"
    
    # Current exploration recommendation
    if context.current_mood == UserMoodState.EXPLORER:
        explore_text += "**🎯 RECOMENDACIÓN PERSONAL**\n"
        explore_text += "🌟 *Como explorador nato, te sugerimos:*\n"
        explore_text += "• 🔮 Buscar áreas secretas\n"
        explore_text += "• 🗝️ Coleccionar objetos raros\n"
        explore_text += "• 📚 Descubrir lore oculto"
    else:
        explore_text += "**🎯 MISIÓN DE EXPLORACIÓN**\n"
        explore_text += "🗺️ *Objetivo actual: Descubrir nueva zona*\n"
        explore_text += "• 🎲 Completa 3 trivias para desbloquear\n"
        explore_text += "• 📖 Avanza en la historia principal\n"
        explore_text += "• 🏆 Obtén 2 logros nuevos"
    
    # Build exploration keyboard
    keyboard_buttons = []
    
    # Gamification-enhanced exploration (FASE 2.3 Enhancement)
    keyboard_buttons.append([
        InlineKeyboardButton(text="🏆 Explorar Logros", callback_data="diana:achievement_engine"),
        InlineKeyboardButton(text="💰 Descubrir Rewards", callback_data="diana:reward_calculator")
    ])
    
    # Zone exploration with leaderboard integration
    keyboard_buttons.append([
        InlineKeyboardButton(text="🌅 Explorar Zona Inicial", callback_data="diana:explore_zone_1"),
        InlineKeyboardButton(text="🏆 Ver Rankings", callback_data="diana:leaderboard_system")
    ])
    
    # Advanced zones (if available)
    if user_level >= 5:
        keyboard_buttons.append([
            InlineKeyboardButton(text="⭐ Reino Épico", callback_data="diana:explore_zone_epic"),
            InlineKeyboardButton(text="🔮 Área Secreta", callback_data="diana:explore_secret")
        ])
    
    # Exploration tools
    keyboard_buttons.append([
        InlineKeyboardButton(text="🔍 Radar de Oportunidades", callback_data="diana:exploration_radar"),
        InlineKeyboardButton(text="🗺️ Mapa Completo", callback_data="diana:full_map")
    ])
    
    # Special actions
    keyboard_buttons.append([
        InlineKeyboardButton(text="🎲 Exploración Aleatoria", callback_data="diana:random_explore"),
        InlineKeyboardButton(text="🏆 Misiones de Exploración", callback_data="diana:exploration_missions")
    ])
    
    # Navigation
    keyboard_buttons.append([
        InlineKeyboardButton(text="🔄 Actualizar Mapa", callback_data="diana:explore_mode"),
        InlineKeyboardButton(text="🏠 Volver al Inicio", callback_data="diana:refresh")
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await safe_edit_message(callback, explore_text, keyboard)


async def handle_start_journey(callback: CallbackQuery, diana_master):
    """🌟 Onboarding Experience - FASE 2 Implementation"""
    user_id = callback.from_user.id
    context = await diana_master.context_engine.analyze_user_context(user_id)
    
    # Determine if user is truly new or returning
    is_new_user = context.engagement_pattern == "new_user"
    
    if is_new_user or context.current_mood == UserMoodState.NEWCOMER:
        journey_text = "🌟 **¡BIENVENIDO AL UNIVERSO DIANA!**\n\n"
        journey_text += "🎭 *Prepárate para una aventura épica llena de misterios, desafíos y recompensas increíbles*\n\n"
        
        journey_text += "**🗺️ TU AVENTURA COMIENZA AQUÍ**\n\n"
        journey_text += "Diana es más que un bot - es un universo completo donde:\n\n"
        
        journey_text += "🎯 **MISIONES & DESAFÍOS**\n"
        journey_text += "• Completa trivias épicas\n"
        journey_text += "• Desbloquea logros únicos\n"
        journey_text += "• Sube de nivel y obtén poder\n\n"
        
        journey_text += "📖 **HISTORIA NARRATIVA**\n"
        journey_text += "• Vive una aventura interactiva\n"
        journey_text += "• Toma decisiones que importan\n"
        journey_text += "• Descubre secretos ancestrales\n\n"
        
        journey_text += "💎 **RECOMPENSAS & COLECCIÓN**\n"
        journey_text += "• Gana besitos (nuestra moneda)\n"
        journey_text += "• Colecciona objetos únicos\n"
        journey_text += "• Accede a contenido VIP\n\n"
        
        journey_text += "**🎁 REGALO DE BIENVENIDA**\n"
        journey_text += "Para comenzar tu aventura, recibes:\n"
        journey_text += "• 💰 100 Besitos gratis\n"
        journey_text += "• 🏆 Logro 'Nuevo Aventurero'\n"
        journey_text += "• 🎯 Acceso a misiones especiales\n\n"
        
        journey_text += "**👑 ¿LISTO PARA COMENZAR?**\n"
        journey_text += "Elige tu primer paso en esta aventura épica:"
        
        # New user keyboard
        keyboard_buttons = [
            [InlineKeyboardButton(text="🎲 Mi Primera Trivia", callback_data="diana:first_trivia")],
            [InlineKeyboardButton(text="📖 Comenzar la Historia", callback_data="diana:story_intro")],
            [InlineKeyboardButton(text="🎁 Reclamar Regalo", callback_data="diana:welcome_gift")],
            [InlineKeyboardButton(text="💫 Tour Completo", callback_data="diana:guided_tour")],
            [InlineKeyboardButton(text="🏠 Ir al Dashboard", callback_data="diana:refresh")]
        ]
        
    else:
        # Returning user journey restart
        journey_text = "🌟 **¡REINICIA TU AVENTURA!**\n\n"
        journey_text += "🚀 *Es hora de comenzar un nuevo capítulo en tu historia épica*\n\n"
        
        # Show current achievements
        journey_text += "**🏆 TU LEGADO HASTA AHORA**\n"
        journey_text += f"⭐ Nivel alcanzado: {3}\n"  # Mock level
        journey_text += f"🏆 Logros desbloqueados: {len(['Novato', 'Sabio', 'Explorador'])}\n"
        journey_text += f"📖 Historia completada: {context.narrative_progress:.1f}%\n"
        journey_text += f"🎯 Misiones completadas: {15}\n\n"
        
        journey_text += "**🚀 NUEVO COMIENZO**\n"
        journey_text += "Puedes elegir:\n\n"
        
        journey_text += "🔄 **REINICIAR PROGRESO**\n"
        journey_text += "• Comenzar desde cero\n"
        journey_text += "• Mantener logros principales\n"
        journey_text += "• Nueva experiencia personalizada\n\n"
        
        journey_text += "⚡ **CONTINUAR AVENTURA**\n"
        journey_text += "• Seguir desde donde lo dejaste\n"
        journey_text += "• Nuevos desafíos disponibles\n"
        journey_text += "• Acceso a contenido avanzado\n\n"
        
        journey_text += "**🎯 ¿QUÉ PREFIERES HACER?**"
        
        # Returning user keyboard
        keyboard_buttons = [
            [InlineKeyboardButton(text="⚡ Continuar Aventura", callback_data="diana:continue_journey")],
            [InlineKeyboardButton(text="🔄 Nuevo Comienzo", callback_data="diana:restart_journey")],
            [InlineKeyboardButton(text="🎯 Ver Mi Progreso", callback_data="diana:progress_tracker")],
            [InlineKeyboardButton(text="📖 Continuar Historia", callback_data="diana:narrative_hub")],
            [InlineKeyboardButton(text="🏠 Dashboard Principal", callback_data="diana:refresh")]
        ]
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await safe_edit_message(callback, journey_text, keyboard)


async def handle_guided_tour(callback: CallbackQuery, diana_master):
    """💫 Tutorial System - FASE 2 Implementation"""
    user_id = callback.from_user.id
    context = await diana_master.context_engine.analyze_user_context(user_id)
    
    # Tutorial system with multiple steps
    tour_text = "💫 **TOUR GUIADO DE DIANA**\n\n"
    tour_text += "🎓 *Tu guía completa para dominar el universo Diana*\n\n"
    
    # Adaptive tutorial based on user experience
    if context.engagement_pattern == "new_user":
        tour_text += "**📚 GUÍA PARA PRINCIPIANTES**\n\n"
        
        tour_text += "**PASO 1: CONOCE TU DASHBOARD**\n"
        tour_text += "🏠 Tu dashboard se adapta a tu estilo de juego\n"
        tour_text += "📊 Siempre verás tu nivel, besitos y progreso\n"
        tour_text += "🎯 Las opciones cambian según tus preferencias\n\n"
        
        tour_text += "**PASO 2: SISTEMA DE RECOMPENSAS**\n"
        tour_text += "💰 Los *Besitos* son nuestra moneda\n"
        tour_text += "🎁 Regalo diario cada 24 horas\n"
        tour_text += "🔥 Mantén tu racha para bonificaciones\n\n"
        
        tour_text += "**PASO 3: TRIVIAS & MISIONES**\n"
        tour_text += "🧠 Responde preguntas para ganar puntos\n"
        tour_text += "🏆 Completa misiones para logros épicos\n"
        tour_text += "⭐ Sube de nivel para desbloquear contenido\n\n"
        
        tour_text += "**PASO 4: HISTORIA INTERACTIVA**\n"
        tour_text += "📖 Vive una aventura narrativa épica\n"
        tour_text += "🎭 Tus decisiones afectan la historia\n"
        tour_text += "🔍 Descubre secretos y misterios ocultos"
        
    else:
        tour_text += "**🚀 GUÍA AVANZADA**\n\n"
        
        tour_text += "**FUNCIONES AVANZADAS**\n"
        tour_text += "📊 Dashboard Pro para usuarios expertos\n"
        tour_text += "🗺️ Modo exploración para descubrir secretos\n"
        tour_text += "🎯 Sistema de objetivos personalizados\n\n"
        
        tour_text += "**OPTIMIZACIÓN DE EXPERIENCIA**\n"
        tour_text += "🤖 IA adaptativa que aprende tus gustos\n"
        tour_text += "⚡ Shortcuts inteligentes personalizados\n"
        tour_text += "📈 Analytics de tu rendimiento\n\n"
        
        tour_text += "**CARACTERÍSTICAS EXCLUSIVAS**\n"
        tour_text += "👑 Contenido VIP para suscriptores\n"
        tour_text += "🏆 Sistema de logros multinivel\n"
        tour_text += "🎭 Decisiones narrativas complejas"
    
    tour_text += "\n\n**🎯 TUTORIAL INTERACTIVO**\n"
    tour_text += "Puedes hacer un tour paso a paso o saltar a la función que más te interese:"
    
    # Build tutorial keyboard
    keyboard_buttons = []
    
    # Tutorial steps
    keyboard_buttons.append([
        InlineKeyboardButton(text="1️⃣ Tour Básico", callback_data="diana:tutorial_basic"),
        InlineKeyboardButton(text="2️⃣ Funciones Avanzadas", callback_data="diana:tutorial_advanced")
    ])
    
    # Specific tutorials
    keyboard_buttons.append([
        InlineKeyboardButton(text="🎲 Tutorial de Trivias", callback_data="diana:tutorial_trivia"),
        InlineKeyboardButton(text="📖 Tutorial de Historia", callback_data="diana:tutorial_story")
    ])
    
    keyboard_buttons.append([
        InlineKeyboardButton(text="💰 Tutorial de Recompensas", callback_data="diana:tutorial_rewards"),
        InlineKeyboardButton(text="🏆 Tutorial de Logros", callback_data="diana:tutorial_achievements")
    ])
    
    # Interactive demo
    keyboard_buttons.append([
        InlineKeyboardButton(text="🎮 Demo Interactivo", callback_data="diana:interactive_demo"),
        InlineKeyboardButton(text="📱 Consejos de Uso", callback_data="diana:usage_tips")
    ])
    
    # Quick start options
    keyboard_buttons.append([
        InlineKeyboardButton(text="⚡ Comenzar Ahora", callback_data="diana:quick_start"),
        InlineKeyboardButton(text="🏠 Ir al Dashboard", callback_data="diana:refresh")
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await safe_edit_message(callback, tour_text, keyboard)


async def handle_collection(callback: CallbackQuery, diana_master):
    """🎒 User Inventory/Collection Display - FASE 2 Implementation"""
    user_id = callback.from_user.id
    context = await diana_master.context_engine.analyze_user_context(user_id)
    
    # Mock user collection data
    user_inventory = {
        'badges': ['🔰 Novato', '🧠 Sabio', '🔥 Racha 7', '🎯 Precisión', '⭐ Explorador'],
        'artifacts': ['🗝️ Llave Ancestral', '💎 Gema de Sabiduría', '📜 Pergamino Místico'],
        'achievements': ['🏆 Primera Trivia', '🎓 Maestro del Conocimiento', '👑 Leyenda Épica'],
        'story_items': ['🔮 Cristal de Visión', '⚔️ Espada de Diana', '🛡️ Escudo Protector'],
        'special_tokens': ['🎟️ Token VIP', '🌟 Token Épico', '💫 Token Legendario']
    }
    
    collection_text = "🎒 **MI COLECCIÓN ÉPICA**\n\n"
    
    if context.current_mood == UserMoodState.COLLECTOR:
        collection_text += "💎 *¡Tu tesoro personal, coleccionista maestro!*\n\n"
    else:
        collection_text += "✨ *Todos los objetos y logros que has conseguido*\n\n"
    
    # Collection stats
    total_items = sum(len(items) for items in user_inventory.values())
    collection_text += f"**📊 ESTADÍSTICAS DE COLECCIÓN**\n"
    collection_text += f"🎒 Total de objetos: {total_items}\n"
    collection_text += f"📈 Valor estimado: {total_items * 50:,} besitos\n"
    collection_text += f"🏆 Rareza promedio: {'Épica' if total_items > 15 else 'Rara'}\n"
    collection_text += f"⭐ Completitud: {min(85, total_items * 5):.0f}%\n\n"
    
    # Badges section
    if user_inventory['badges']:
        collection_text += "**🏅 INSIGNIAS DESBLOQUEADAS**\n"
        for i, badge in enumerate(user_inventory['badges'][:4]):  # Show first 4
            rarity = ['Común', 'Rara', 'Épica', 'Legendaria'][min(i, 3)]
            collection_text += f"• {badge} - *{rarity}*\n"
        if len(user_inventory['badges']) > 4:
            collection_text += f"• ... y {len(user_inventory['badges']) - 4} más\n"
        collection_text += "\n"
    
    # Artifacts section
    if user_inventory['artifacts']:
        collection_text += "**🏺 ARTEFACTOS ANTIGUOS**\n"
        for artifact in user_inventory['artifacts']:
            collection_text += f"• {artifact}\n"
        collection_text += "\n"
    
    # Story items section
    if user_inventory['story_items']:
        collection_text += "**⚔️ OBJETOS DE HISTORIA**\n"
        for item in user_inventory['story_items']:
            collection_text += f"• {item}\n"
        collection_text += "\n"
    
    # Special tokens
    if user_inventory['special_tokens']:
        collection_text += "**🎟️ TOKENS ESPECIALES**\n"
        for token in user_inventory['special_tokens']:
            collection_text += f"• {token}\n"
        collection_text += "\n"
    
    # Collection goals
    collection_text += "**🎯 PRÓXIMOS OBJETIVOS**\n"
    collection_text += "• 🏆 Desbloquear insignia 'Maestro Coleccionista'\n"
    collection_text += "• 💎 Encontrar 3 gemas raras más\n"
    collection_text += "• 📜 Completar set de pergaminos antiguos\n"
    collection_text += "• ⭐ Alcanzar 95% de completitud"
    
    # Build collection keyboard
    keyboard_buttons = []
    
    # Category browsing
    keyboard_buttons.append([
        InlineKeyboardButton(text="🏅 Ver Todas las Insignias", callback_data="diana:view_badges"),
        InlineKeyboardButton(text="🏺 Explorar Artefactos", callback_data="diana:view_artifacts")
    ])
    
    keyboard_buttons.append([
        InlineKeyboardButton(text="⚔️ Objetos de Historia", callback_data="diana:view_story_items"),
        InlineKeyboardButton(text="🎟️ Tokens Especiales", callback_data="diana:view_tokens")
    ])
    
    # Collection management
    keyboard_buttons.append([
        InlineKeyboardButton(text="📊 Estadísticas Detalladas", callback_data="diana:collection_stats"),
        InlineKeyboardButton(text="🔍 Buscar Objetos", callback_data="diana:search_items")
    ])
    
    # Collection goals
    keyboard_buttons.append([
        InlineKeyboardButton(text="🎯 Objetivos de Colección", callback_data="diana:collection_goals"),
        InlineKeyboardButton(text="🏆 Logros Faltantes", callback_data="diana:missing_achievements")
    ])
    
    # Actions
    keyboard_buttons.append([
        InlineKeyboardButton(text="💎 Buscar Tesoros", callback_data="diana:treasure_hunt"),
        InlineKeyboardButton(text="🛒 Ir a la Tienda", callback_data="diana:epic_shop")
    ])
    
    # Navigation
    keyboard_buttons.append([
        InlineKeyboardButton(text="🔄 Actualizar Colección", callback_data="diana:collection"),
        InlineKeyboardButton(text="🏠 Volver al Inicio", callback_data="diana:refresh")
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await safe_edit_message(callback, collection_text, keyboard)


async def handle_story_choices(callback: CallbackQuery, diana_master):
    """🎭 Advanced Narrative Choices - FASE 2 Implementation"""
    user_id = callback.from_user.id
    context = await diana_master.context_engine.analyze_user_context(user_id)
    
    # Determine current story state
    story_progress = context.narrative_progress
    
    story_text = "🎭 **DECISIONES NARRATIVAS ÉPICAS**\n\n"
    
    if context.current_mood == UserMoodState.STORYTELLER:
        story_text += "📖 *El poder de cambiar el destino está en tus manos, maestro narrador*\n\n"
    else:
        story_text += "✨ *Cada elección que hagas reescribirá la historia para siempre*\n\n"
    
    # Dynamic story choice based on progress
    if story_progress < 25:
        # Early game choices
        story_text += "**📖 CAPÍTULO I: EL DESPERTAR**\n\n"
        story_text += "Diana acaba de descubrir un misterioso artefacto en las ruinas del Templo Olvidado. El objeto pulsa con una energía extraña y susurra secretos ancestrales.\n\n"
        story_text += "💫 *Una voz etérea emerge del artefacto:*\n"
        story_text += "\"*Joven elegida, el destino del Reino Perdido yace en tus decisiones. ¿Qué camino eliges?*\"\n\n"
        
        story_text += "**⚡ CONSECUENCIAS DE TUS ELECCIONES:**\n"
        story_text += "🔮 **Activar el Artefacto**: Poder inmediato, pero riesgo desconocido\n"
        story_text += "📚 **Estudiar los Símbolos**: Conocimiento seguro, progreso más lento\n"
        story_text += "🤝 **Buscar Consejo**: Sabiduría colectiva, dependencia de otros\n\n"
        
        story_text += "**🎯 ELECCIÓN CRÍTICA:**\n"
        story_text += "*Esta decisión afectará permanentemente tu relación con la magia ancestral*"
        
        # Early game choices keyboard
        choice_buttons = [
            [InlineKeyboardButton(text="🔮 Activar el Artefacto", callback_data="diana:story_choice_activate")],
            [InlineKeyboardButton(text="📚 Estudiar los Símbolos", callback_data="diana:story_choice_study")],
            [InlineKeyboardButton(text="🤝 Buscar Consejo de Sabios", callback_data="diana:story_choice_counsel")]
        ]
        
    elif story_progress < 50:
        # Mid game choices
        story_text += "**🌙 CAPÍTULO II: LA ALIANZA SOMBRÍA**\n\n"
        story_text += "Diana ha descubierto que no está sola. Los Guardianes Sombríos le ofrecen una alianza poderosa, pero sus intenciones no están claras.\n\n"
        story_text += "⚔️ *El líder de los Guardianes se acerca:*\n"
        story_text += "\"*El enemigo común nos une, Diana. Juntos podemos derrotar a las Fuerzas del Caos, pero debes demostrar tu lealtad.*\"\n\n"
        
        story_text += "**⚖️ DILEMA MORAL:**\n"
        story_text += "🤝 **Aceptar la Alianza**: Poder compartido, motivos cuestionables\n"
        story_text += "🛡️ **Rechazar y Ir Solo**: Independencia total, mayor dificultad\n"
        story_text += "🕵️ **Infiltrarse como Espía**: Información valiosa, riesgo extremo\n\n"
        
        story_text += "**💀 ADVERTENCIA:**\n"
        story_text += "*Los Guardianes Sombríos tienen su propia agenda. ¿Puedes confiar en ellos?*"
        
        # Mid game choices keyboard
        choice_buttons = [
            [InlineKeyboardButton(text="🤝 Formar Alianza", callback_data="diana:story_choice_alliance")],
            [InlineKeyboardButton(text="🛡️ Rechazar y Continuar Solo", callback_data="diana:story_choice_solo")],
            [InlineKeyboardButton(text="🕵️ Infiltrarse como Espía", callback_data="diana:story_choice_spy")]
        ]
        
    elif story_progress < 75:
        # Late game choices
        story_text += "**🔥 CAPÍTULO III: EL PRECIO DEL PODER**\n\n"
        story_text += "Diana se encuentra ante el Trono del Reino Perdido. Para restaurar la paz, debe hacer el sacrificio definitivo.\n\n"
        story_text += "👑 *El espíritu del último rey aparece:*\n"
        story_text += "\"*El reino puede ser salvado, pero el precio es alto. ¿Estás dispuesta a pagar el costo?*\"\n\n"
        
        story_text += "**⚡ DECISIÓN FINAL:**\n"
        story_text += "👑 **Aceptar el Trono**: Poder absoluto, sacrificar libertad\n"
        story_text += "💫 **Destruir el Trono**: Libertad para todos, caos temporal\n"
        story_text += "🔄 **Transformar el Reino**: Nueva era, consecuencias impredecibles\n\n"
        
        story_text += "**🌟 LEGADO ETERNO:**\n"
        story_text += "*Esta elección determinará cómo será recordada Diana por las generaciones futuras*"
        
        # Late game choices keyboard
        choice_buttons = [
            [InlineKeyboardButton(text="👑 Aceptar el Trono Eterno", callback_data="diana:story_choice_throne")],
            [InlineKeyboardButton(text="💫 Destruir el Sistema", callback_data="diana:story_choice_destroy")],
            [InlineKeyboardButton(text="🔄 Transformar el Reino", callback_data="diana:story_choice_transform")]
        ]
        
    else:
        # Epilogue choices
        story_text += "**⭐ ÉPÍLOGO: NUEVOS HORIZONTES**\n\n"
        story_text += "Diana ha completado su transformación épica. El reino está en paz, pero nuevas aventuras llaman desde dimensiones inexploradas.\n\n"
        story_text += "🌌 *Una nueva voz resuena desde el cosmos:*\n"
        story_text += "\"*Maestra Diana, tu historia en este reino ha terminado. Pero el multiverso está lleno de mundos que necesitan tu sabiduría.*\"\n\n"
        
        story_text += "**🚀 NUEVA AVENTURA:**\n"
        story_text += "🌌 **Explorar el Multiverso**: Aventuras infinitas\n"
        story_text += "🏛️ **Quedarse como Guardiana**: Proteger el reino\n"
        story_text += "📚 **Convertirse en Mentora**: Entrenar nuevos héroes\n\n"
        
        story_text += "**♾️ LEGADO INFINITO:**\n"
        story_text += "*Tu historia inspirará a generaciones de futuros aventureros*"
        
        # Epilogue choices keyboard
        choice_buttons = [
            [InlineKeyboardButton(text="🌌 Explorar Multiverso", callback_data="diana:story_choice_multiverse")],
            [InlineKeyboardButton(text="🏛️ Ser Guardiana Eterna", callback_data="diana:story_choice_guardian")],
            [InlineKeyboardButton(text="📚 Mentora de Héroes", callback_data="diana:story_choice_mentor")]
        ]
    
    # Add common navigation buttons
    choice_buttons.extend([
        [InlineKeyboardButton(text="📖 Ver Historia Completa", callback_data="diana:story_summary")],
        [InlineKeyboardButton(text="🔄 Repensar Decisión", callback_data="diana:story_choices")],
        [InlineKeyboardButton(text="🏠 Volver al Inicio", callback_data="diana:refresh")]
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=choice_buttons)
    
    await safe_edit_message(callback, story_text, keyboard)


# Export all handlers for easy import
__all__ = [
    'handle_progress_tracker',
    'handle_pro_dashboard', 
    'handle_explore_mode',
    'handle_start_journey',
    'handle_guided_tour',
    'handle_collection',
    'handle_story_choices'
]