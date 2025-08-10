"""
Keyboard principal para navegación de gamificación.
Proporciona acceso rápido a todas las funcionalidades de gamificación.
"""

from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

class GamificationKeyboard:
    """
    Keyboard principal para el sistema de gamificación.
    Centraliza la navegación entre todas las funcionalidades de juego.
    """
    
    @staticmethod
    def main_menu(user_points: float = 0, user_level: int = 1, show_premium: bool = False) -> types.InlineKeyboardMarkup:
        """
        Crea el keyboard principal de gamificación.
        
        Args:
            user_points: Puntos actuales del usuario.
            user_level: Nivel actual del usuario.
            show_premium: Si mostrar opciones premium.
            
        Returns:
            Keyboard con opciones principales de gamificación.
        """
        keyboard = InlineKeyboardBuilder()
        
        # Fila 1: Recompensas y Tienda
        keyboard.button(text="🎁 Regalo Diario", callback_data="gamification:daily_reward")
        keyboard.button(text="🛍️ Tienda", callback_data="shop:main")
        
        # Fila 2: Trivia y Misiones
        keyboard.button(text="🧠 Trivia", callback_data="trivia:main")
        keyboard.button(text="🎯 Misiones", callback_data="main_menu:missions")
        
        # Fila 3: Progreso y Perfil
        keyboard.button(text="📊 Mi Progreso", callback_data="gamification:progress")
        keyboard.button(text="🏆 Logros", callback_data="gamification:achievements")
        
        # Fila 4: Opciones adicionales
        if user_level >= 5 or show_premium:
            keyboard.button(text="⭐ Zona VIP", callback_data="gamification:vip_zone")
        
        keyboard.button(text="⚙️ Configuración", callback_data="gamification:settings")
        
        # Fila 5: Navegación
        keyboard.button(text="⬅️ Menú Principal", callback_data="main_menu")
        
        # Ajustar layout
        if user_level >= 5 or show_premium:
            keyboard.adjust(2, 2, 2, 2, 1)
        else:
            keyboard.adjust(2, 2, 2, 1, 1)
        
        return keyboard.as_markup()
    
    @staticmethod
    def quick_actions(can_claim_daily: bool = True, has_active_missions: bool = False) -> types.InlineKeyboardMarkup:
        """
        Crea un keyboard compacto con acciones rápidas.
        
        Args:
            can_claim_daily: Si puede reclamar regalo diario.
            has_active_missions: Si tiene misiones activas.
            
        Returns:
            Keyboard compacto con acciones principales.
        """
        keyboard = InlineKeyboardBuilder()
        
        # Acciones rápidas basadas en estado
        if can_claim_daily:
            keyboard.button(text="🎁 ¡Reclamar Regalo!", callback_data="gamification:daily_reward")
        
        if has_active_missions:
            keyboard.button(text="🎯 Continuar Misiones", callback_data="main_menu:missions")
        
        # Siempre disponibles
        keyboard.button(text="🧠 Trivia Rápida", callback_data="trivia:main")
        keyboard.button(text="🛍️ Tienda", callback_data="shop:main")
        
        keyboard.adjust(1, 2)
        return keyboard.as_markup()
    
    @staticmethod
    def progress_menu() -> types.InlineKeyboardMarkup:
        """
        Crea keyboard para el menú de progreso.
        
        Returns:
            Keyboard con opciones de progreso.
        """
        keyboard = InlineKeyboardBuilder()
        
        keyboard.button(text="📊 Estadísticas Generales", callback_data="gamification:stats:general")
        keyboard.button(text="💰 Historial de Besitos", callback_data="gamification:stats:points")
        keyboard.button(text="🎯 Progreso de Misiones", callback_data="gamification:stats:missions")
        keyboard.button(text="🧠 Estadísticas de Trivia", callback_data="trivia:stats")
        keyboard.button(text="🏆 Mis Logros", callback_data="gamification:achievements")
        keyboard.button(text="⬅️ Volver", callback_data="gamification:main")
        
        keyboard.adjust(1, 2, 1, 1, 1)
        return keyboard.as_markup()
    
    @staticmethod
    def achievements_menu() -> types.InlineKeyboardMarkup:
        """
        Crea keyboard para el menú de logros.
        
        Returns:
            Keyboard con opciones de logros.
        """
        keyboard = InlineKeyboardBuilder()
        
        keyboard.button(text="✅ Logros Completados", callback_data="gamification:achievements:completed")
        keyboard.button(text="🔄 Logros En Progreso", callback_data="gamification:achievements:progress")
        keyboard.button(text="🔒 Logros Bloqueados", callback_data="gamification:achievements:locked")
        keyboard.button(text="🏅 Logros Especiales", callback_data="gamification:achievements:special")
        keyboard.button(text="⬅️ Volver", callback_data="gamification:main")
        
        keyboard.adjust(2, 2, 1)
        return keyboard.as_markup()
    
    @staticmethod
    def vip_zone_menu() -> types.InlineKeyboardMarkup:
        """
        Crea keyboard para la zona VIP.
        
        Returns:
            Keyboard con opciones VIP.
        """
        keyboard = InlineKeyboardBuilder()
        
        keyboard.button(text="💎 Contenido Exclusivo", callback_data="shop:category:especial:0")
        keyboard.button(text="⚡ Multiplicadores Premium", callback_data="shop:category:beneficios:0")
        keyboard.button(text="👑 Trivia Experto", callback_data="trivia:level:experto")
        keyboard.button(text="🎁 Recompensas VIP", callback_data="gamification:vip:rewards")
        keyboard.button(text="📈 Estadísticas Avanzadas", callback_data="gamification:vip:stats")
        keyboard.button(text="⬅️ Volver", callback_data="gamification:main")
        
        keyboard.adjust(2, 1, 2, 1)
        return keyboard.as_markup()
    
    @staticmethod
    def settings_menu() -> types.InlineKeyboardMarkup:
        """
        Crea keyboard para configuraciones de gamificación.
        
        Returns:
            Keyboard con opciones de configuración.
        """
        keyboard = InlineKeyboardBuilder()
        
        keyboard.button(text="🔔 Notificaciones", callback_data="gamification:settings:notifications")
        keyboard.button(text="🎯 Dificultad Trivia", callback_data="gamification:settings:trivia_difficulty")
        keyboard.button(text="📊 Privacidad Stats", callback_data="gamification:settings:privacy")
        keyboard.button(text="🎨 Tema Visual", callback_data="gamification:settings:theme")
        keyboard.button(text="🔄 Resetear Progreso", callback_data="gamification:settings:reset")
        keyboard.button(text="⬅️ Volver", callback_data="gamification:main")
        
        keyboard.adjust(2, 2, 1, 1)
        return keyboard.as_markup()
    
    @staticmethod
    def confirmation(action: str, item_name: str = "") -> types.InlineKeyboardMarkup:
        """
        Crea keyboard de confirmación para acciones importantes.
        
        Args:
            action: Acción a confirmar.
            item_name: Nombre del item si aplica.
            
        Returns:
            Keyboard de confirmación.
        """
        keyboard = InlineKeyboardBuilder()
        
        keyboard.button(text="✅ Confirmar", callback_data=f"gamification:confirm:{action}")
        keyboard.button(text="❌ Cancelar", callback_data=f"gamification:cancel:{action}")
        
        keyboard.adjust(2)
        return keyboard.as_markup()
    
    @staticmethod
    def back_to_gamification() -> types.InlineKeyboardMarkup:
        """
        Crea un keyboard simple para volver al menú principal de gamificación.
        
        Returns:
            Keyboard con botón de volver.
        """
        keyboard = InlineKeyboardBuilder()
        keyboard.button(text="⬅️ Volver a Gamificación", callback_data="gamification:main")
        return keyboard.as_markup()
    
    @staticmethod
    def level_up_celebration(new_level: int, rewards: dict) -> types.InlineKeyboardMarkup:
        """
        Crea keyboard especial para celebrar subida de nivel.
        
        Args:
            new_level: Nuevo nivel alcanzado.
            rewards: Recompensas obtenidas.
            
        Returns:
            Keyboard de celebración.
        """
        keyboard = InlineKeyboardBuilder()
        
        keyboard.button(text="🎉 ¡Ver Recompensas!", callback_data=f"gamification:level_rewards:{new_level}")
        keyboard.button(text="🛍️ Explorar Tienda", callback_data="shop:main")
        keyboard.button(text="🎯 Nuevas Misiones", callback_data="main_menu:missions")
        keyboard.button(text="📊 Ver Mi Progreso", callback_data="gamification:progress")
        
        keyboard.adjust(1, 2, 1)
        return keyboard.as_markup()
    
    @staticmethod
    def daily_streak_celebration(streak_days: int, next_milestone: int) -> types.InlineKeyboardMarkup:
        """
        Crea keyboard para celebrar rachas diarias.
        
        Args:
            streak_days: Días de racha actual.
            next_milestone: Próximo hito de racha.
            
        Returns:
            Keyboard de celebración de racha.
        """
        keyboard = InlineKeyboardBuilder()
        
        if streak_days >= 7:
            keyboard.button(text="🎁 Bonus Especial", callback_data="gamification:streak_bonus")
        
        keyboard.button(text="📈 Ver Progreso de Racha", callback_data="gamification:streak_progress")
        keyboard.button(text="🎯 Completar Misiones", callback_data="main_menu:missions")
        keyboard.button(text="🧠 Responder Trivia", callback_data="trivia:main")
        keyboard.button(text="⬅️ Continuar", callback_data="main_menu")
        
        if streak_days >= 7:
            keyboard.adjust(1, 1, 2, 1)
        else:
            keyboard.adjust(1, 2, 1)
        
        return keyboard.as_markup()