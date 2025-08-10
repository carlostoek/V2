"""
Keyboards específicos para el sistema de recompensas diarias.
Maneja la reclamación de regalos, rachas y bonificaciones.
"""

from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import Dict, Any

class DailyRewardsKeyboard:
    """
    Keyboards especializados para el sistema de recompensas diarias.
    """
    
    @staticmethod
    def claim_available(streak_days: int = 0, next_milestone: int = 3) -> types.InlineKeyboardMarkup:
        """
        Crea keyboard cuando la recompensa diaria está disponible.
        
        Args:
            streak_days: Días consecutivos de racha.
            next_milestone: Próximo hito de racha.
            
        Returns:
            Keyboard para reclamar recompensa.
        """
        keyboard = InlineKeyboardBuilder()
        
        # Botón principal de reclamación
        claim_text = "🎁 ¡Reclamar Regalo Diario!"
        if streak_days > 0:
            claim_text = f"🔥 ¡Reclamar Regalo! (Racha x{streak_days})"
        
        keyboard.button(text=claim_text, callback_data="daily_reward:claim")
        
        # Información adicional si hay racha
        if streak_days > 0:
            keyboard.button(
                text=f"📈 Ver Progreso de Racha ({streak_days} días)",
                callback_data="daily_reward:streak_progress"
            )
            
            if streak_days >= 7:
                keyboard.button(
                    text="🎊 Bonus Especial Disponible",
                    callback_data="daily_reward:special_bonus"
                )
        
        # Acciones relacionadas
        keyboard.button(text="📊 Ver Historial", callback_data="daily_reward:history")
        keyboard.button(text="💡 Consejos para Racha", callback_data="daily_reward:tips")
        
        # Navegación
        keyboard.button(text="⬅️ Menú Principal", callback_data="main_menu")
        
        # Ajustar layout según la racha
        if streak_days == 0:
            keyboard.adjust(1, 2, 1)
        elif streak_days >= 7:
            keyboard.adjust(1, 1, 1, 2, 1)
        else:
            keyboard.adjust(1, 1, 2, 1)
        
        return keyboard.as_markup()
    
    @staticmethod
    def already_claimed(time_remaining: str, next_reward: int) -> types.InlineKeyboardMarkup:
        """
        Crea keyboard cuando ya se reclamó la recompensa diaria.
        
        Args:
            time_remaining: Tiempo restante para próxima recompensa.
            next_reward: Puntos de la próxima recompensa estimada.
            
        Returns:
            Keyboard para usuario que ya reclamó.
        """
        keyboard = InlineKeyboardBuilder()
        
        # Información sobre la próxima recompensa
        keyboard.button(
            text=f"⏰ Próximo regalo en {time_remaining}",
            callback_data="daily_reward:next_info"
        )
        
        # Otras actividades para ganar besitos
        keyboard.button(text="🧠 Responder Trivia", callback_data="trivia:main")
        keyboard.button(text="🎯 Completar Misiones", callback_data="main_menu:missions")
        keyboard.button(text="🛍️ Ir a la Tienda", callback_data="shop:main")
        
        # Estadísticas y progreso
        keyboard.button(text="📊 Ver Mi Progreso", callback_data="gamification:progress")
        keyboard.button(text="🔥 Historial de Racha", callback_data="daily_reward:streak_history")
        
        # Navegación
        keyboard.button(text="⬅️ Menú Principal", callback_data="main_menu")
        
        keyboard.adjust(1, 3, 2, 1)
        return keyboard.as_markup()
    
    @staticmethod
    def reward_claimed(
        points_awarded: int, 
        streak_days: int, 
        streak_bonus: int = 0,
        next_milestone: Dict[str, Any] = None
    ) -> types.InlineKeyboardMarkup:
        """
        Crea keyboard después de reclamar exitosamente la recompensa.
        
        Args:
            points_awarded: Puntos totales otorgados.
            streak_days: Días de racha actual.
            streak_bonus: Bonus adicional por racha.
            next_milestone: Información del próximo hito.
            
        Returns:
            Keyboard post-reclamación.
        """
        keyboard = InlineKeyboardBuilder()
        
        # Celebrar el logro
        if streak_days >= 7:
            keyboard.button(text="🎉 ¡Celebrar Racha!", callback_data="daily_reward:celebrate")
        
        # Usar los besitos ganados
        keyboard.button(text="🛍️ Gastar en Tienda", callback_data="shop:main")
        keyboard.button(text="🧠 Jugar Trivia", callback_data="trivia:main")
        
        # Información sobre el próximo hito
        if next_milestone and not next_milestone.get("is_max", False):
            days_remaining = next_milestone.get("days_remaining", 0)
            multiplier = next_milestone.get("multiplier", 1.0)
            keyboard.button(
                text=f"🎯 Próximo hito: {days_remaining} días (x{multiplier})",
                callback_data="daily_reward:next_milestone_info"
            )
        
        # Ver progreso
        keyboard.button(text="📈 Ver Mi Progreso", callback_data="daily_reward:streak_progress")
        keyboard.button(text="🏆 Ver Logros", callback_data="gamification:achievements")
        
        # Navegación
        keyboard.button(text="⬅️ Menú Principal", callback_data="main_menu")
        
        # Ajustar layout dinámicamente
        buttons_layout = []
        if streak_days >= 7:
            buttons_layout.append(1)  # Celebrar
        buttons_layout.extend([2])  # Gastar/Jugar
        if next_milestone and not next_milestone.get("is_max", False):
            buttons_layout.append(1)  # Próximo hito
        buttons_layout.extend([2, 1])  # Progreso/Logros, Menú
        
        keyboard.adjust(*buttons_layout)
        return keyboard.as_markup()
    
    @staticmethod
    def streak_progress(
        current_streak: int, 
        best_streak: int = 0, 
        total_rewards: int = 0,
        milestones_reached: int = 0
    ) -> types.InlineKeyboardMarkup:
        """
        Crea keyboard para mostrar progreso detallado de racha.
        
        Args:
            current_streak: Racha actual.
            best_streak: Mejor racha histórica.
            total_rewards: Total de recompensas reclamadas.
            milestones_reached: Hitos alcanzados.
            
        Returns:
            Keyboard con detalles de progreso.
        """
        keyboard = InlineKeyboardBuilder()
        
        # Acciones motivacionales
        if current_streak < best_streak:
            keyboard.button(
                text=f"💪 Superar Record ({best_streak} días)",
                callback_data="daily_reward:beat_record"
            )
        else:
            keyboard.button(text="👑 ¡Nuevo Record!", callback_data="daily_reward:new_record")
        
        # Información detallada
        keyboard.button(text="📊 Ver Estadísticas", callback_data="daily_reward:detailed_stats")
        keyboard.button(text="📅 Calendario de Rachas", callback_data="daily_reward:calendar")
        
        # Consejos y motivación
        keyboard.button(text="💡 Consejos para Racha", callback_data="daily_reward:tips")
        keyboard.button(text="🎯 Establecer Recordatorio", callback_data="daily_reward:reminder")
        
        # Comparación social (si está habilitada)
        keyboard.button(text="👥 Comparar con Amigos", callback_data="daily_reward:social_compare")
        
        # Navegación
        keyboard.button(text="🎁 Volver a Regalos", callback_data="daily_reward:main")
        keyboard.button(text="⬅️ Menú Principal", callback_data="main_menu")
        
        keyboard.adjust(1, 2, 2, 1, 2)
        return keyboard.as_markup()
    
    @staticmethod
    def special_bonus(bonus_type: str, bonus_value: int) -> types.InlineKeyboardMarkup:
        """
        Crea keyboard para bonus especiales por rachas largas.
        
        Args:
            bonus_type: Tipo de bonus especial.
            bonus_value: Valor del bonus.
            
        Returns:
            Keyboard para bonus especial.
        """
        keyboard = InlineKeyboardBuilder()
        
        # Reclamar el bonus especial
        keyboard.button(
            text=f"🎊 ¡Reclamar Bonus! (+{bonus_value})",
            callback_data=f"daily_reward:claim_bonus:{bonus_type}"
        )
        
        # Información sobre el bonus
        keyboard.button(
            text="ℹ️ ¿Qué es este bonus?",
            callback_data=f"daily_reward:bonus_info:{bonus_type}"
        )
        
        # Compartir el logro
        keyboard.button(text="📢 Compartir Logro", callback_data="daily_reward:share_achievement")
        
        # Navegación
        keyboard.button(text="🎁 Volver a Regalos", callback_data="daily_reward:main")
        keyboard.button(text="⬅️ Menú Principal", callback_data="main_menu")
        
        keyboard.adjust(1, 1, 1, 2)
        return keyboard.as_markup()
    
    @staticmethod
    def history_view(recent_claims: list, total_earned: int) -> types.InlineKeyboardMarkup:
        """
        Crea keyboard para ver historial de recompensas diarias.
        
        Args:
            recent_claims: Lista de reclamaciones recientes.
            total_earned: Total de besitos ganados por regalos diarios.
            
        Returns:
            Keyboard con opciones de historial.
        """
        keyboard = InlineKeyboardBuilder()
        
        # Filtros de historial
        keyboard.button(text="📅 Últimos 7 días", callback_data="daily_reward:history:week")
        keyboard.button(text="📆 Último mes", callback_data="daily_reward:history:month")
        keyboard.button(text="📊 Todo el tiempo", callback_data="daily_reward:history:all")
        
        # Estadísticas detalladas
        keyboard.button(text="📈 Gráfico de Progreso", callback_data="daily_reward:chart")
        keyboard.button(text="🏆 Mejores Rachas", callback_data="daily_reward:best_streaks")
        
        # Exportar datos (para usuarios avanzados)
        keyboard.button(text="💾 Exportar Datos", callback_data="daily_reward:export")
        
        # Navegación
        keyboard.button(text="🎁 Volver a Regalos", callback_data="daily_reward:main")
        keyboard.button(text="⬅️ Menú Principal", callback_data="main_menu")
        
        keyboard.adjust(3, 2, 1, 2)
        return keyboard.as_markup()
    
    @staticmethod
    def tips_and_motivation() -> types.InlineKeyboardMarkup:
        """
        Crea keyboard con consejos para mantener rachas.
        
        Returns:
            Keyboard con consejos motivacionales.
        """
        keyboard = InlineKeyboardBuilder()
        
        # Categorías de consejos
        keyboard.button(text="⏰ Consejos de Horarios", callback_data="daily_reward:tips:timing")
        keyboard.button(text="🔔 Configurar Recordatorio", callback_data="daily_reward:tips:reminders")
        keyboard.button(text="💪 Motivación Diaria", callback_data="daily_reward:tips:motivation")
        keyboard.button(text="🎯 Estrategias de Racha", callback_data="daily_reward:tips:strategies")
        
        # Herramientas útiles
        keyboard.button(text="📱 Widget de Racha", callback_data="daily_reward:widget")
        keyboard.button(text="👥 Comunidad", callback_data="daily_reward:community")
        
        # Navegación
        keyboard.button(text="🎁 Volver a Regalos", callback_data="daily_reward:main")
        keyboard.button(text="⬅️ Menú Principal", callback_data="main_menu")
        
        keyboard.adjust(2, 2, 2, 2)
        return keyboard.as_markup()
    
    @staticmethod
    def milestone_celebration(
        milestone: int, 
        multiplier: float, 
        special_reward: str = None
    ) -> types.InlineKeyboardMarkup:
        """
        Crea keyboard especial para celebrar hitos de racha.
        
        Args:
            milestone: Hito alcanzado (días).
            multiplier: Multiplicador conseguido.
            special_reward: Recompensa especial si la hay.
            
        Returns:
            Keyboard de celebración de hito.
        """
        keyboard = InlineKeyboardBuilder()
        
        # Celebración principal
        keyboard.button(
            text=f"🎊 ¡Hito de {milestone} días alcanzado!",
            callback_data=f"daily_reward:celebrate_milestone:{milestone}"
        )
        
        # Reclamar recompensa especial si existe
        if special_reward:
            keyboard.button(
                text=f"🎁 Reclamar: {special_reward}",
                callback_data=f"daily_reward:claim_milestone_reward:{milestone}"
            )
        
        # Compartir logro
        keyboard.button(text="📢 Compartir Hito", callback_data=f"daily_reward:share_milestone:{milestone}")
        keyboard.button(text="📸 Captura de Pantalla", callback_data="daily_reward:screenshot")
        
        # Continuar el progreso
        keyboard.button(text="🚀 Próximo Objetivo", callback_data="daily_reward:next_goal")
        keyboard.button(text="📊 Ver Mi Progreso", callback_data="daily_reward:streak_progress")
        
        # Navegación
        keyboard.button(text="⬅️ Continuar", callback_data="main_menu")
        
        # Layout dinámico
        if special_reward:
            keyboard.adjust(1, 1, 2, 2, 1)
        else:
            keyboard.adjust(1, 2, 2, 1)
        
        return keyboard.as_markup()
    
    @staticmethod
    def reminder_settings() -> types.InlineKeyboardMarkup:
        """
        Crea keyboard para configurar recordatorios de recompensas diarias.
        
        Returns:
            Keyboard de configuración de recordatorios.
        """
        keyboard = InlineKeyboardBuilder()
        
        # Opciones de tiempo
        keyboard.button(text="🌅 Mañana (8:00)", callback_data="daily_reward:reminder:morning")
        keyboard.button(text="🌞 Mediodía (12:00)", callback_data="daily_reward:reminder:noon")
        keyboard.button(text="🌆 Tarde (18:00)", callback_data="daily_reward:reminder:evening")
        keyboard.button(text="🌙 Noche (21:00)", callback_data="daily_reward:reminder:night")
        
        # Configuración personalizada
        keyboard.button(text="⏰ Hora Personalizada", callback_data="daily_reward:reminder:custom")
        keyboard.button(text="🔕 Desactivar Recordatorios", callback_data="daily_reward:reminder:disable")
        
        # Tipo de recordatorio
        keyboard.button(text="📱 Notificación Simple", callback_data="daily_reward:reminder:simple")
        keyboard.button(text="🎵 Con Sonido Especial", callback_data="daily_reward:reminder:sound")
        
        # Navegación
        keyboard.button(text="⬅️ Volver", callback_data="daily_reward:tips")
        
        keyboard.adjust(2, 2, 2, 2, 1)
        return keyboard.as_markup()