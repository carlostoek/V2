"""Servicio de trivias diarias."""

import structlog
import asyncio
import random
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from ..gamification.service import GamificationService
from ...core.interfaces.ICoreService import ICoreService

logger = structlog.get_logger()

class TriviaType(Enum):
    """Tipos de trivia disponibles."""
    DAILY = "daily"
    SPECIAL = "special"
    VIP = "vip"
    CHALLENGE = "challenge"

class DifficultyLevel(Enum):
    """Niveles de dificultad."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"

@dataclass
class TriviaQuestion:
    """Representa una pregunta de trivia."""
    id: str
    question: str
    options: List[str]
    correct_answer: int  # Índice de la respuesta correcta
    difficulty: DifficultyLevel
    category: str
    explanation: str
    points_reward: int
    vip_only: bool = False
    image_url: Optional[str] = None
    
@dataclass
class TriviaSession:
    """Representa una sesión de trivia de un usuario."""
    user_id: int
    question_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    selected_answer: Optional[int] = None
    is_correct: Optional[bool] = None
    points_earned: int = 0
    trivia_type: TriviaType = TriviaType.DAILY

class TriviaService(ICoreService):
    """Servicio para gestionar trivias diarias y especiales."""
    
    def __init__(self, gamification_service: GamificationService):
        self.gamification_service = gamification_service
        self._questions = self._initialize_questions()
        self._active_sessions = {}  # user_id -> TriviaSession
        self._daily_completions = {}  # user_id -> date
        self._user_stats = {}  # user_id -> stats dict
        
    def _initialize_questions(self) -> Dict[str, TriviaQuestion]:
        """Inicializa el banco de preguntas de trivia."""
        questions = {
            # === PREGUNTAS FÁCILES ===
            "easy_1": TriviaQuestion(
                id="easy_1",
                question="¿Cuál es el nombre de la moneda virtual del bot?",
                options=["Puntos", "Besitos", "Créditos", "Tokens"],
                correct_answer=1,
                difficulty=DifficultyLevel.EASY,
                category="Bot",
                explanation="Los 'besitos' son la moneda virtual que puedes ganar y usar en la tienda.",
                points_reward=10
            ),
            "easy_2": TriviaQuestion(
                id="easy_2",
                question="¿Cómo puedes obtener más besitos?",
                options=["Solo comprando", "Reaccionando a mensajes", "Enviando spam", "No se puede"],
                correct_answer=1,
                difficulty=DifficultyLevel.EASY,
                category="Bot",
                explanation="Puedes ganar besitos reaccionando a mensajes, completando misiones y participando en actividades.",
                points_reward=10
            ),
            "easy_3": TriviaQuestion(
                id="easy_3",
                question="¿Qué significa VIP en el contexto del bot?",
                options=["Very Important Player", "Virtual Interactive Person", "Verified Internal Profile", "Visual Interface Program"],
                correct_answer=0,
                difficulty=DifficultyLevel.EASY,
                category="Bot",
                explanation="VIP significa 'Very Important Player' y otorga acceso a contenido exclusivo.",
                points_reward=10
            ),
            
            # === PREGUNTAS MEDIAS ===
            "medium_1": TriviaQuestion(
                id="medium_1",
                question="¿Cuál es la capital de Australia?",
                options=["Sydney", "Melbourne", "Canberra", "Perth"],
                correct_answer=2,
                difficulty=DifficultyLevel.MEDIUM,
                category="Geografía",
                explanation="Canberra es la capital de Australia, aunque Sydney y Melbourne son más conocidas.",
                points_reward=25
            ),
            "medium_2": TriviaQuestion(
                id="medium_2",
                question="¿En qué año se lanzó el primer iPhone?",
                options=["2006", "2007", "2008", "2009"],
                correct_answer=1,
                difficulty=DifficultyLevel.MEDIUM,
                category="Tecnología",
                explanation="El primer iPhone fue presentado por Steve Jobs en enero de 2007.",
                points_reward=25
            ),
            "medium_3": TriviaQuestion(
                id="medium_3",
                question="¿Cuál es el elemento químico más abundante en el universo?",
                options=["Oxígeno", "Carbono", "Hidrógeno", "Helio"],
                correct_answer=2,
                difficulty=DifficultyLevel.MEDIUM,
                category="Ciencia",
                explanation="El hidrógeno representa aproximadamente el 75% de la materia normal del universo.",
                points_reward=25
            ),
            
            # === PREGUNTAS DIFÍCILES ===
            "hard_1": TriviaQuestion(
                id="hard_1",
                question="¿Quién escribió 'Cien años de soledad'?",
                options=["Mario Vargas Llosa", "Gabriel García Márquez", "Isabel Allende", "Julio Cortázar"],
                correct_answer=1,
                difficulty=DifficultyLevel.HARD,
                category="Literatura",
                explanation="Gabriel García Márquez escribió esta obra maestra del realismo mágico en 1967.",
                points_reward=50
            ),
            "hard_2": TriviaQuestion(
                id="hard_2",
                question="¿Cuál es la constante de Planck aproximadamente?",
                options=["6.626 × 10⁻³⁴ J⋅s", "3.14159", "2.718", "9.81 m/s²"],
                correct_answer=0,
                difficulty=DifficultyLevel.HARD,
                category="Física",
                explanation="La constante de Planck es fundamental en la mecánica cuántica.",
                points_reward=50
            ),
            
            # === PREGUNTAS VIP ===
            "vip_1": TriviaQuestion(
                id="vip_1",
                question="¿Cuál es el secreto mejor guardado de Diana?",
                options=["Su verdadero nombre", "Su lugar de origen", "Su poder especial", "Su misión"],
                correct_answer=2,
                difficulty=DifficultyLevel.EXPERT,
                category="Diana Lore",
                explanation="El poder especial de Diana es lo que la hace única y misteriosa.",
                points_reward=100,
                vip_only=True
            ),
            "vip_2": TriviaQuestion(
                id="vip_2",
                question="¿Qué evento cambió para siempre el destino de Diana?",
                options=["Un encuentro nocturno", "Una traición", "Un descubrimiento", "Una elección"],
                correct_answer=0,
                difficulty=DifficultyLevel.EXPERT,
                category="Diana Lore",
                explanation="El encuentro nocturno marcó el inicio de la verdadera historia de Diana.",
                points_reward=100,
                vip_only=True
            )
        }
        
        logger.info(f"Banco de trivias inicializado con {len(questions)} preguntas")
        return questions
    
    async def get_daily_question(self, user_id: int) -> Optional[TriviaQuestion]:
        """
        Obtiene la pregunta diaria para un usuario.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Pregunta diaria o None si ya la completó
        """
        today = datetime.now().date()
        
        # Verificar si ya completó la trivia de hoy
        if user_id in self._daily_completions:
            last_completion = self._daily_completions[user_id]
            if last_completion == today:
                return None
        
        # Obtener estadísticas del usuario para determinar dificultad
        user_stats = await self.gamification_service.get_user_stats(user_id)
        user_level = user_stats.get('level', 0)
        is_vip = user_stats.get('is_vip', False)
        
        # Determinar pool de preguntas disponibles
        available_questions = []
        
        for question in self._questions.values():
            # Filtrar por acceso VIP
            if question.vip_only and not is_vip:
                continue
                
            # Ajustar dificultad según nivel del usuario
            if user_level < 5 and question.difficulty != DifficultyLevel.EASY:
                continue
            elif user_level < 15 and question.difficulty == DifficultyLevel.EXPERT:
                continue
                
            available_questions.append(question)
        
        if not available_questions:
            return None
            
        # Seleccionar pregunta aleatoria
        question = random.choice(available_questions)
        
        logger.info(f"Pregunta diaria asignada a usuario {user_id}: {question.id}")
        return question
    
    async def start_trivia_session(self, user_id: int, question_id: str) -> TriviaSession:
        """
        Inicia una nueva sesión de trivia.
        
        Args:
            user_id: ID del usuario
            question_id: ID de la pregunta
            
        Returns:
            Sesión de trivia iniciada
        """
        session = TriviaSession(
            user_id=user_id,
            question_id=question_id,
            start_time=datetime.now()
        )
        
        self._active_sessions[user_id] = session
        
        logger.debug(f"Sesión de trivia iniciada para usuario {user_id}")
        return session
    
    async def submit_answer(
        self, 
        user_id: int, 
        selected_answer: int
    ) -> Dict[str, Any]:
        """
        Procesa la respuesta de un usuario.
        
        Args:
            user_id: ID del usuario
            selected_answer: Índice de la respuesta seleccionada
            
        Returns:
            Resultado de la respuesta
        """
        # Verificar que hay una sesión activa
        if user_id not in self._active_sessions:
            return {
                "success": False,
                "reason": "No hay sesión de trivia activa"
            }
        
        session = self._active_sessions[user_id]
        question = self._questions.get(session.question_id)
        
        if not question:
            return {
                "success": False,
                "reason": "Pregunta no encontrada"
            }
        
        # Procesar respuesta
        session.selected_answer = selected_answer
        session.end_time = datetime.now()
        session.is_correct = (selected_answer == question.correct_answer)
        
        # Calcular puntos
        if session.is_correct:
            # Bonificación por velocidad (respuesta en menos de 30 segundos)
            response_time = (session.end_time - session.start_time).total_seconds()
            speed_bonus = 1.5 if response_time < 30 else 1.0
            
            session.points_earned = int(question.points_reward * speed_bonus)
            
            # Otorgar puntos
            await self.gamification_service.add_points(
                user_id, 
                session.points_earned
            )
            
            # Registrar completación diaria
            today = datetime.now().date()
            self._daily_completions[user_id] = today
        
        # Actualizar estadísticas del usuario
        await self._update_user_stats(user_id, session.is_correct, question.difficulty)
        
        # Limpiar sesión activa
        del self._active_sessions[user_id]
        
        result = {
            "success": True,
            "is_correct": session.is_correct,
            "correct_answer": question.correct_answer,
            "explanation": question.explanation,
            "points_earned": session.points_earned,
            "response_time": response_time if 'response_time' in locals() else 0
        }
        
        logger.info(
            f"Usuario {user_id} respondió trivia {question.id}: "
            f"{'correcto' if session.is_correct else 'incorrecto'} "
            f"({session.points_earned} puntos)"
        )
        
        return result
    
    async def get_user_trivia_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Obtiene las estadísticas de trivia de un usuario.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Estadísticas del usuario
        """
        stats = self._user_stats.get(user_id, {
            "total_answered": 0,
            "correct_answers": 0,
            "total_points_earned": 0,
            "accuracy_rate": 0.0,
            "daily_streak": 0,
            "best_category": None,
            "difficulty_breakdown": {
                "easy": {"answered": 0, "correct": 0},
                "medium": {"answered": 0, "correct": 0},
                "hard": {"answered": 0, "correct": 0},
                "expert": {"answered": 0, "correct": 0}
            }
        })
        
        return stats
    
    async def can_answer_daily(self, user_id: int) -> bool:
        """
        Verifica si un usuario puede responder la trivia diaria.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            True si puede responder, False si ya la completó hoy
        """
        today = datetime.now().date()
        
        if user_id in self._daily_completions:
            return self._daily_completions[user_id] != today
            
        return True
    
    async def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtiene el ranking de usuarios en trivias.
        
        Args:
            limit: Número máximo de usuarios a retornar
            
        Returns:
            Lista ordenada de usuarios con sus estadísticas
        """
        leaderboard = []
        
        for user_id, stats in self._user_stats.items():
            leaderboard.append({
                "user_id": user_id,
                "total_points": stats["total_points_earned"],
                "accuracy": stats["accuracy_rate"],
                "total_answered": stats["total_answered"],
                "daily_streak": stats["daily_streak"]
            })
        
        # Ordenar por puntos totales, luego por precisión
        leaderboard.sort(
            key=lambda x: (x["total_points"], x["accuracy"]), 
            reverse=True
        )
        
        return leaderboard[:limit]
    
    async def create_custom_question(
        self,
        question: str,
        options: List[str],
        correct_answer: int,
        category: str,
        difficulty: DifficultyLevel,
        explanation: str,
        points_reward: int,
        vip_only: bool = False
    ) -> str:
        """
        Crea una pregunta personalizada (para administradores).
        
        Args:
            question: Texto de la pregunta
            options: Lista de opciones
            correct_answer: Índice de la respuesta correcta
            category: Categoría de la pregunta
            difficulty: Nivel de dificultad
            explanation: Explicación de la respuesta
            points_reward: Puntos que otorga
            vip_only: Si es solo para VIP
            
        Returns:
            ID de la pregunta creada
        """
        question_id = f"custom_{len(self._questions)}_{datetime.now().timestamp()}"
        
        custom_question = TriviaQuestion(
            id=question_id,
            question=question,
            options=options,
            correct_answer=correct_answer,
            difficulty=difficulty,
            category=category,
            explanation=explanation,
            points_reward=points_reward,
            vip_only=vip_only
        )
        
        self._questions[question_id] = custom_question
        
        logger.info(f"Pregunta personalizada creada: {question_id}")
        return question_id
    
    async def _update_user_stats(
        self, 
        user_id: int, 
        is_correct: bool, 
        difficulty: DifficultyLevel
    ) -> None:
        """Actualiza las estadísticas del usuario."""
        if user_id not in self._user_stats:
            self._user_stats[user_id] = {
                "total_answered": 0,
                "correct_answers": 0,
                "total_points_earned": 0,
                "accuracy_rate": 0.0,
                "daily_streak": 0,
                "best_category": None,
                "difficulty_breakdown": {
                    "easy": {"answered": 0, "correct": 0},
                    "medium": {"answered": 0, "correct": 0},
                    "hard": {"answered": 0, "correct": 0},
                    "expert": {"answered": 0, "correct": 0}
                }
            }
        
        stats = self._user_stats[user_id]
        
        # Actualizar contadores generales
        stats["total_answered"] += 1
        if is_correct:
            stats["correct_answers"] += 1
        
        # Calcular tasa de precisión
        stats["accuracy_rate"] = (
            stats["correct_answers"] / stats["total_answered"] * 100
        )
        
        # Actualizar por dificultad
        difficulty_key = difficulty.value
        if difficulty_key in stats["difficulty_breakdown"]:
            stats["difficulty_breakdown"][difficulty_key]["answered"] += 1
            if is_correct:
                stats["difficulty_breakdown"][difficulty_key]["correct"] += 1
        
        # Actualizar racha diaria (simplificado)
        if is_correct:
            stats["daily_streak"] += 1
        else:
            stats["daily_streak"] = 0
    
    async def get_question_by_id(self, question_id: str) -> Optional[TriviaQuestion]:
        """Obtiene una pregunta por su ID."""
        return self._questions.get(question_id)
    
    async def get_active_session(self, user_id: int) -> Optional[TriviaSession]:
        """Obtiene la sesión activa de un usuario."""
        return self._active_sessions.get(user_id)
    
    async def cleanup_expired_sessions(self) -> None:
        """Limpia sesiones expiradas (más de 5 minutos sin responder)."""
        current_time = datetime.now()
        expired_users = []
        
        for user_id, session in self._active_sessions.items():
            if (current_time - session.start_time).total_seconds() > 300:  # 5 minutos
                expired_users.append(user_id)
        
        for user_id in expired_users:
            del self._active_sessions[user_id]
            logger.debug(f"Sesión de trivia expirada para usuario {user_id}")
    
    # Método para ejecutar limpieza periódica
    async def start_cleanup_task(self) -> None:
        """Inicia la tarea de limpieza periódica."""
        while True:
            await asyncio.sleep(300)  # Cada 5 minutos
            await self.cleanup_expired_sessions()