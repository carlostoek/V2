"""
Keyboards específicos para el sistema de trivia.
Maneja la selección de niveles, respuestas y navegación de trivia.
"""

from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Dict, Any

class TriviaKeyboard:
    """
    Keyboards especializados para el sistema de trivia.
    """
    
    @staticmethod
    def level_selection(available_levels: List[Dict[str, Any]], user_stats: Dict[str, Dict] = None) -> types.InlineKeyboardMarkup:
        """
        Crea keyboard para seleccionar nivel de trivia.
        
        Args:
            available_levels: Niveles disponibles para el usuario.
            user_stats: Estadísticas del usuario por nivel.
            
        Returns:
            Keyboard con niveles disponibles.
        """
        keyboard = InlineKeyboardBuilder()
        user_stats = user_stats or {}
        
        for level_data in available_levels:
            level_key = level_data["key"]
            level_info = level_data["info"]
            question_count = level_data["question_count"]
            
            # Estadísticas del nivel si existen
            level_stats = user_stats.get(level_key, {})
            answered = level_stats.get("answered", 0)
            correct = level_stats.get("correct", 0)
            
            # Crear texto del botón
            accuracy_text = ""
            if answered > 0:
                accuracy = (correct / answered) * 100
                accuracy_text = f" ({accuracy:.0f}%)"
            
            button_text = (
                f"{level_info['emoji']} {level_info['name']} "
                f"(+{level_info['reward']} 💰){accuracy_text}"
            )
            
            keyboard.button(
                text=button_text,
                callback_data=f"trivia:level:{level_key}"
            )
        
        # Botones adicionales
        keyboard.button(text="📊 Ver Estadísticas", callback_data="trivia:stats")
        keyboard.button(text="🏆 Ranking", callback_data="trivia:ranking")
        keyboard.button(text="⬅️ Menú Principal", callback_data="main_menu")
        
        keyboard.adjust(1)  # Un nivel por fila
        return keyboard.as_markup()
    
    @staticmethod
    def question_options(question: Dict[str, Any], session_id: str, show_timer: bool = True) -> types.InlineKeyboardMarkup:
        """
        Crea keyboard con las opciones de respuesta para una pregunta.
        
        Args:
            question: Datos de la pregunta.
            session_id: ID de la sesión activa.
            show_timer: Si mostrar información de timer.
            
        Returns:
            Keyboard con opciones de respuesta.
        """
        keyboard = InlineKeyboardBuilder()
        
        # Opciones de respuesta
        for i, option in enumerate(question["options"]):
            # Usar letras (A, B, C, D) para mejor UX
            letter = chr(65 + i)  # A=65, B=66, etc.
            button_text = f"{letter}) {option}"
            
            keyboard.button(
                text=button_text,
                callback_data=f"trivia:answer:{session_id}:{i}"
            )
        
        keyboard.adjust(1)  # Una opción por fila para mejor lectura
        return keyboard.as_markup()
    
    @staticmethod
    def post_answer(
        is_correct: bool, 
        level: str, 
        reward: int, 
        can_continue: bool = True, 
        show_explanation: bool = True
    ) -> types.InlineKeyboardMarkup:
        """
        Crea keyboard para después de responder una pregunta.
        
        Args:
            is_correct: Si la respuesta fue correcta.
            level: Nivel de la pregunta.
            reward: Puntos obtenidos.
            can_continue: Si puede continuar respondiendo.
            show_explanation: Si se mostró explicación.
            
        Returns:
            Keyboard post-respuesta.
        """
        keyboard = InlineKeyboardBuilder()
        
        if can_continue:
            # Obtener info del nivel para el emoji
            level_emojis = {
                "basico": "🟢",
                "intermedio": "🟡", 
                "avanzado": "🟠",
                "experto": "🔴"
            }
            level_emoji = level_emojis.get(level, "🧠")
            
            keyboard.button(
                text=f"🧠 Otra Pregunta {level_emoji}",
                callback_data=f"trivia:next:{level}"
            )
        
        # Opciones siempre disponibles
        keyboard.button(text="📊 Ver Estadísticas", callback_data="trivia:stats")
        
        if is_correct:
            keyboard.button(text="🎉 Celebrar", callback_data="trivia:celebrate")
        else:
            keyboard.button(text="💪 Intentar Otro Nivel", callback_data="trivia:main")
        
        # Navegación
        keyboard.button(text="🔄 Cambiar Nivel", callback_data="trivia:main")
        keyboard.button(text="⬅️ Menú Principal", callback_data="main_menu")
        
        # Ajustar layout
        if can_continue:
            keyboard.adjust(1, 2, 2)
        else:
            keyboard.adjust(2, 2)
        
        return keyboard.as_markup()
    
    @staticmethod
    def statistics_menu(stats: Dict[str, Dict]) -> types.InlineKeyboardMarkup:
        """
        Crea keyboard para el menú de estadísticas de trivia.
        
        Args:
            stats: Estadísticas del usuario.
            
        Returns:
            Keyboard con opciones de estadísticas.
        """
        keyboard = InlineKeyboardBuilder()
        
        # Estadísticas por nivel
        for level_key in ["basico", "intermedio", "avanzado", "experto"]:
            if level_key in stats:
                level_names = {
                    "basico": "🟢 Básico",
                    "intermedio": "🟡 Intermedio",
                    "avanzado": "🟠 Avanzado",
                    "experto": "🔴 Experto"
                }
                level_name = level_names.get(level_key, level_key.title())
                
                keyboard.button(
                    text=f"📊 {level_name}",
                    callback_data=f"trivia:stats:{level_key}"
                )
        
        # Opciones adicionales
        keyboard.button(text="📈 Progreso General", callback_data="trivia:stats:general")
        keyboard.button(text="🏆 Mejores Rachas", callback_data="trivia:stats:streaks")
        keyboard.button(text="⏰ Tiempos de Respuesta", callback_data="trivia:stats:timing")
        
        # Navegación
        keyboard.button(text="🧠 Responder Preguntas", callback_data="trivia:main")
        keyboard.button(text="⬅️ Menú Principal", callback_data="main_menu")
        
        keyboard.adjust(2, 2, 1, 2)
        return keyboard.as_markup()
    
    @staticmethod
    def level_stats_detail(level: str, stats: Dict[str, Any]) -> types.InlineKeyboardMarkup:
        """
        Crea keyboard para estadísticas detalladas de un nivel.
        
        Args:
            level: Nivel específico.
            stats: Estadísticas del nivel.
            
        Returns:
            Keyboard con detalles del nivel.
        """
        keyboard = InlineKeyboardBuilder()
        
        # Acciones específicas del nivel
        level_emojis = {
            "basico": "🟢",
            "intermedio": "🟡",
            "avanzado": "🟠", 
            "experto": "🔴"
        }
        level_emoji = level_emojis.get(level, "🧠")
        
        keyboard.button(
            text=f"🧠 Practicar {level_emoji}",
            callback_data=f"trivia:level:{level}"
        )
        keyboard.button(
            text="🎯 Mejorar Record",
            callback_data=f"trivia:improve:{level}"
        )
        
        # Navegación
        keyboard.button(text="📊 Todas las Stats", callback_data="trivia:stats")
        keyboard.button(text="⬅️ Volver", callback_data="trivia:stats")
        
        keyboard.adjust(2, 2)
        return keyboard.as_markup()
    
    @staticmethod
    def ranking_menu(user_rank: int = None) -> types.InlineKeyboardMarkup:
        """
        Crea keyboard para el sistema de ranking.
        
        Args:
            user_rank: Posición actual del usuario.
            
        Returns:
            Keyboard con opciones de ranking.
        """
        keyboard = InlineKeyboardBuilder()
        
        # Diferentes vistas del ranking
        keyboard.button(text="🏆 Top 10 Global", callback_data="trivia:ranking:global")
        keyboard.button(text="📅 Ranking Mensual", callback_data="trivia:ranking:monthly")
        keyboard.button(text="⚡ Mejores Tiempos", callback_data="trivia:ranking:speed")
        keyboard.button(text="🔥 Mejores Rachas", callback_data="trivia:ranking:streaks")
        
        # Mi posición
        if user_rank:
            keyboard.button(
                text=f"📍 Mi Posición (#{user_rank})",
                callback_data="trivia:ranking:my_position"
            )
        
        # Navegación
        keyboard.button(text="🧠 Subir en Ranking", callback_data="trivia:main")
        keyboard.button(text="⬅️ Volver", callback_data="trivia:main")
        
        keyboard.adjust(2, 2, 1, 2)
        return keyboard.as_markup()
    
    @staticmethod
    def daily_challenge() -> types.InlineKeyboardMarkup:
        """
        Crea keyboard para desafío diario de trivia.
        
        Returns:
            Keyboard con opciones de desafío.
        """
        keyboard = InlineKeyboardBuilder()
        
        keyboard.button(text="⚡ Desafío Rápido", callback_data="trivia:challenge:quick")
        keyboard.button(text="🧠 Desafío Experto", callback_data="trivia:challenge:expert")
        keyboard.button(text="🏆 Desafío Ranking", callback_data="trivia:challenge:ranking")
        
        # Recompensas especiales
        keyboard.button(text="🎁 Recompensas del Día", callback_data="trivia:challenge:rewards")
        
        # Navegación
        keyboard.button(text="📊 Ver Mi Progreso", callback_data="trivia:challenge:progress")
        keyboard.button(text="⬅️ Trivia Normal", callback_data="trivia:main")
        
        keyboard.adjust(1, 2, 2)
        return keyboard.as_markup()
    
    @staticmethod
    def timeout_options(level: str, session_expired: bool = True) -> types.InlineKeyboardMarkup:
        """
        Crea keyboard cuando se agota el tiempo de una pregunta.
        
        Args:
            level: Nivel de la pregunta que expiró.
            session_expired: Si la sesión expiró.
            
        Returns:
            Keyboard para después del timeout.
        """
        keyboard = InlineKeyboardBuilder()
        
        if session_expired:
            keyboard.button(text="⏰ Se acabó el tiempo", callback_data="trivia:timeout_info")
        
        # Opciones de recuperación
        level_emojis = {
            "basico": "🟢",
            "intermedio": "🟡",
            "avanzado": "🟠",
            "experto": "🔴"
        }
        level_emoji = level_emojis.get(level, "🧠")
        
        keyboard.button(
            text=f"🔄 Intentar Otra {level_emoji}",
            callback_data=f"trivia:level:{level}"
        )
        keyboard.button(text="📉 Nivel Más Fácil", callback_data="trivia:easier_level")
        keyboard.button(text="💪 Practicar Más", callback_data="trivia:practice_mode")
        
        # Navegación
        keyboard.button(text="📊 Ver Consejos", callback_data="trivia:tips")
        keyboard.button(text="⬅️ Menú Principal", callback_data="main_menu")
        
        keyboard.adjust(1, 1, 2, 2)
        return keyboard.as_markup()
    
    @staticmethod
    def celebration(achievement: str, reward: int) -> types.InlineKeyboardMarkup:
        """
        Crea keyboard especial para celebraciones en trivia.
        
        Args:
            achievement: Tipo de logro conseguido.
            reward: Recompensa obtenida.
            
        Returns:
            Keyboard de celebración.
        """
        keyboard = InlineKeyboardBuilder()
        
        # Acciones de celebración
        keyboard.button(text="🎊 ¡Compartir Logro!", callback_data=f"trivia:share:{achievement}")
        keyboard.button(text="🏆 Ver Mis Logros", callback_data="gamification:achievements")
        
        # Continuar jugando
        keyboard.button(text="🚀 Seguir Mejorando", callback_data="trivia:main")
        keyboard.button(text="💎 Usar en Tienda", callback_data="shop:main")
        
        # Navegación
        keyboard.button(text="⬅️ Continuar", callback_data="main_menu")
        
        keyboard.adjust(2, 2, 1)
        return keyboard.as_markup()
    
    @staticmethod
    def practice_mode(level: str) -> types.InlineKeyboardMarkup:
        """
        Crea keyboard para modo práctica.
        
        Args:
            level: Nivel de práctica.
            
        Returns:
            Keyboard con opciones de práctica.
        """
        keyboard = InlineKeyboardBuilder()
        
        # Tipos de práctica
        keyboard.button(text="⚡ Práctica Rápida", callback_data=f"trivia:practice:quick:{level}")
        keyboard.button(text="🧠 Práctica Intensiva", callback_data=f"trivia:practice:intensive:{level}")
        keyboard.button(text="📚 Repasar Errores", callback_data=f"trivia:practice:review:{level}")
        
        # Configuraciones
        keyboard.button(text="⚙️ Configurar Práctica", callback_data=f"trivia:practice:settings:{level}")
        
        # Navegación
        keyboard.button(text="🔄 Volver a Trivia", callback_data="trivia:main")
        keyboard.button(text="⬅️ Menú Principal", callback_data="main_menu")
        
        keyboard.adjust(1, 2, 2)
        return keyboard.as_markup()