"""
Datos de ejemplo para el sistema de trivia de gamificación.
Incluye preguntas de 4 niveles de dificultad con temática relacionada a Diana.
"""

# Configuración de niveles de trivia
TRIVIA_LEVELS = {
    "basico": {
        "name": "🟢 Básico",
        "emoji": "🟢",
        "reward": 5,
        "description": "Preguntas básicas sobre Diana y la historia",
        "timer_seconds": 30,
        "level_required": 1,
        "color": "#4CAF50"
    },
    "intermedio": {
        "name": "🟡 Intermedio", 
        "emoji": "🟡",
        "reward": 10,
        "description": "Preguntas sobre detalles de la narrativa",
        "timer_seconds": 25,
        "level_required": 2,
        "color": "#FFC107"
    },
    "avanzado": {
        "name": "🟠 Avanzado",
        "emoji": "🟠", 
        "reward": 20,
        "description": "Preguntas complejas y detalles ocultos",
        "timer_seconds": 20,
        "level_required": 4,
        "color": "#FF9800"
    },
    "experto": {
        "name": "🔴 Experto",
        "emoji": "🔴",
        "reward": 50,
        "description": "Solo para verdaderos conocedores de Diana",
        "timer_seconds": 15,
        "level_required": 6,
        "color": "#F44336"
    }
}

# Base de datos de preguntas por nivel
TRIVIA_QUESTIONS = {
    "basico": [
        {
            "id": "basic_1",
            "question": "¿Cuál es el nombre del bot que te está hablando?",
            "options": ["Diana", "Ana", "Luna", "Sofia"],
            "correct": 0,
            "explanation": "¡Correcto! Soy Diana, tu compañera en esta aventura."
        },
        {
            "id": "basic_2", 
            "question": "¿Cómo se llaman los puntos en el sistema de gamificación?",
            "options": ["Monedas", "Besitos", "Estrellas", "Corazones"],
            "correct": 1,
            "explanation": "¡Exacto! Los 'besitos' son la moneda de nuestro mundo."
        },
        {
            "id": "basic_3",
            "question": "¿Qué comando usas para ver tus misiones?",
            "options": ["/tareas", "/misiones", "/objetivos", "/trabajos"],
            "correct": 1,
            "explanation": "¡Correcto! Con /misiones puedes ver todo tu progreso."
        },
        {
            "id": "basic_4",
            "question": "¿Cuántas categorías tiene la tienda principal?",
            "options": ["3", "4", "5", "6"],
            "correct": 1,
            "explanation": "¡Bien! Son 4 categorías: Contenido Especial, Recompensas, Narrativa y Beneficios."
        },
        {
            "id": "basic_5",
            "question": "¿Qué emoji representa el contenido especial en la tienda?",
            "options": ["💋", "🎁", "🔓", "⭐"],
            "correct": 0,
            "explanation": "¡Perfecto! 💋 representa el contenido más íntimo de Diana."
        },
        {
            "id": "basic_6",
            "question": "¿Cada cuánto tiempo puedes reclamar tu regalo diario?",
            "options": ["12 horas", "24 horas", "48 horas", "72 horas"],
            "correct": 1,
            "explanation": "¡Correcto! Una vez cada 24 horas para mantener tu racha."
        },
        {
            "id": "basic_7",
            "question": "¿Qué sucede si mantienes una racha de regalos diarios?",
            "options": ["Nada especial", "Más besitos", "Descuentos", "Items gratis"],
            "correct": 1,
            "explanation": "¡Sí! Mientras más días consecutivos, más besitos recibes."
        },
        {
            "id": "basic_8",
            "question": "¿Cuál es la rareza más alta de los items de la tienda?",
            "options": ["Legendario", "Épico", "Mítico", "Divino"],
            "correct": 2,
            "explanation": "¡Exacto! Los items Míticos son los más raros y valiosos."
        }
    ],
    
    "intermedio": [
        {
            "id": "inter_1",
            "question": "¿Qué tipo de multiplicador puedes comprar para 24 horas?",
            "options": ["x1.5", "x2.0", "x3.0", "x5.0"],
            "correct": 1,
            "explanation": "¡Correcto! El multiplicador x2 por 24 horas es muy popular."
        },
        {
            "id": "inter_2",
            "question": "¿Cuál es el multiplicador más poderoso disponible en la tienda?",
            "options": ["x3", "x4", "x5", "x10"],
            "correct": 2,
            "explanation": "¡Sí! El Mega Multiplicador x5 es intenso pero dura solo 2 horas."
        },
        {
            "id": "inter_3",
            "question": "¿Qué nivel necesitas para acceder a contenido avanzado?",
            "options": ["Nivel 2", "Nivel 3", "Nivel 4", "Nivel 5"],
            "correct": 2,
            "explanation": "A partir del nivel 4 se desbloquea contenido más sofisticado."
        },
        {
            "id": "inter_4",
            "question": "¿Cuántos días consecutivos necesitas para el multiplicador máximo de regalos?",
            "options": ["7 días", "14 días", "21 días", "30 días"],
            "correct": 3,
            "explanation": "¡Exacto! A los 30 días consecutivos alcanzas el multiplicador x2.0."
        },
        {
            "id": "inter_5",
            "question": "¿Qué pasa si no reclamas tu regalo por más de 48 horas?",
            "options": ["Nada", "Pierdes 1 día de racha", "Se reinicia tu racha", "Pierdes besitos"],
            "correct": 2,
            "explanation": "¡Correcto! Si pasas más de 48 horas, tu racha se reinicia."
        },
        {
            "id": "inter_6",
            "question": "¿Cuál es el item más caro en la categoría de Contenido Especial?",
            "options": ["Video Personal", "Sesión Fotográfica", "Colección Completa", "Audio Íntimo"],
            "correct": 2,
            "explanation": "¡Bien! La Colección Completa Premium vale 500 besitos."
        },
        {
            "id": "inter_7",
            "question": "¿Qué beneficio especial ofrecen los packs de la tienda?",
            "options": ["Más contenido", "Descuentos", "Acceso VIP", "Multiplicadores extras"],
            "correct": 1,
            "explanation": "¡Correcto! Los packs incluyen descuentos del 25-30%."
        },
        {
            "id": "inter_8",
            "question": "¿Cuántas horas dura el acceso VIP temporal?",
            "options": ["24 horas", "48 horas", "72 horas", "96 horas"],
            "correct": 2,
            "explanation": "¡Sí! Son 3 días completos (72 horas) de acceso VIP."
        }
    ],
    
    "avanzado": [
        {
            "id": "adv_1",
            "question": "¿Cuál es la fórmula exacta para calcular niveles basados en puntos?",
            "options": ["nivel = puntos/100", "nivel = 1 + sqrt(puntos/100)", "nivel = log(puntos)", "nivel = puntos^0.5"],
            "correct": 1,
            "explanation": "¡Impresionante! Conoces la fórmula: nivel = 1 + raíz cuadrada(puntos/100)."
        },
        {
            "id": "adv_2",
            "question": "¿Qué evento desencadena la validación de logros Diana?",
            "options": ["Subir de nivel", "Completar misiones", "Validación narrativa", "Comprar items"],
            "correct": 2,
            "explanation": "¡Exacto! Las validaciones narrativas activan el sistema Diana de logros especiales."
        },
        {
            "id": "adv_3",
            "question": "¿Cuál es el bonus máximo por racha en las recompensas diarias?",
            "options": ["30 besitos", "40 besitos", "50 besitos", "60 besitos"],
            "correct": 2,
            "explanation": "¡Correcto! El bonus máximo por racha es de 50 besitos adicionales."
        },
        {
            "id": "adv_4",
            "question": "¿Qué tipo de misiones se refrescan automáticamente al completarse?",
            "options": ["Misiones de historia", "Misiones diarias", "Misiones de evento", "Misiones VIP"],
            "correct": 1,
            "explanation": "¡Bien! Las misiones diarias se regeneran automáticamente para mantener el engagement."
        },
        {
            "id": "adv_5",
            "question": "¿Cuántos objetivos simultáneos puede rastrear una misión compleja?",
            "options": ["1 objetivo", "Hasta 3", "Hasta 5", "Ilimitados"],
            "correct": 3,
            "explanation": "¡Impresionante! El sistema permite objetivos múltiples complejos por misión."
        },
        {
            "id": "adv_6",
            "question": "¿Qué patrón arquitectónico usa el Event Bus para la gamificación?",
            "options": ["Observer", "Factory", "Singleton", "Strategy"],
            "correct": 0,
            "explanation": "¡Excelente conocimiento técnico! Usa el patrón Observer para eventos."
        },
        {
            "id": "adv_7",
            "question": "¿Cuál es el multiplicador de score mínimo en validaciones Diana?",
            "options": ["0.3x", "0.5x", "0.7x", "1.0x"],
            "correct": 1,
            "explanation": "¡Correcto! El multiplicador mínimo es 0.5x para asegurar siempre alguna recompensa."
        },
        {
            "id": "adv_8",
            "question": "¿Qué tipo de caché usa el GamificationService?",
            "options": ["Redis", "Memcached", "En memoria", "Base de datos"],
            "correct": 2,
            "explanation": "¡Exacto! Usa caché en memoria para optimizar el acceso a puntos y misiones."
        }
    ],
    
    "experto": [
        {
            "id": "exp_1",
            "question": "¿Cuántos microsegundos tiene el timeout por defecto del Event Bus?",
            "options": ["10000", "120000", "600000", "No tiene timeout"],
            "correct": 1,
            "explanation": "¡Increíble nivel de conocimiento! Son 120,000ms = 2 minutos por defecto."
        },
        {
            "id": "exp_2",
            "question": "¿Qué método específico valida la integridad de las recompensas de logros?",
            "options": ["_check_rewards", "_validate_achievement", "_check_level_achievements", "_verify_integrity"],
            "correct": 2,
            "explanation": "¡Perfecto! El método _check_level_achievements valida la integridad completa."
        },
        {
            "id": "exp_3",
            "question": "¿Cuál es la estructura exacta del completion_data para logros Diana?",
            "options": ["{type, score}", "{validation_type, score}", "{user_id, type}", "{score, reward}"],
            "correct": 1,
            "explanation": "¡Maestría absoluta! Es {validation_type, score} para tracking completo."
        },
        {
            "id": "exp_4",
            "question": "¿Qué algoritmo usa la paginación de la tienda para optimizar memoria?",
            "options": ["Lazy loading", "Slice indexing", "Cursor pagination", "Offset limiting"],
            "correct": 1,
            "explanation": "¡Brillante! Usa slice indexing con start_idx y end_idx para eficiencia."
        },
        {
            "id": "exp_5",
            "question": "¿Cuál es el nombre exacto de la tabla de constraints para UserMission?",
            "options": ["uix_user_mission", "idx_user_mission", "uc_user_mission", "pk_user_mission"],
            "correct": 0,
            "explanation": "¡Excepcional! La constraint se llama exactamente 'uix_user_mission'."
        },
        {
            "id": "exp_6",
            "question": "¿Qué tipo de JSON validation usa el campo objectives en Mission?",
            "options": ["JSONSchema", "Nativa SQLAlchemy", "Custom validator", "No validation"],
            "correct": 1,
            "explanation": "¡Perfecto! Usa la validación nativa de JSON de SQLAlchemy sin esquemas externos."
        },
        {
            "id": "exp_7",
            "question": "¿Cuántos SELECT statements ejecuta get_user_missions() en el peor caso?",
            "options": ["1 query", "2 queries", "3 queries", "Variable según data"],
            "correct": 1,
            "explanation": "¡Análisis perfecto! Ejecuta exactamente 2 queries: usuario + misiones con join."
        },
        {
            "id": "exp_8",
            "question": "¿Qué patron de cleanup usa points_history para evitar memory leaks?",
            "options": ["FIFO queue", "TTL expiration", "Size limiting", "No cleanup"],
            "correct": 2,
            "explanation": "¡Conocimiento profundo! Aunque no está implementado aún, size limiting sería el patrón ideal."
        }
    ]
}

def get_random_question(level: str, exclude_ids: list = None) -> dict:
    """
    Obtiene una pregunta aleatoria de un nivel específico.
    
    Args:
        level: Nivel de dificultad.
        exclude_ids: IDs de preguntas a excluir.
        
    Returns:
        Dict con la pregunta seleccionada o None si no hay disponibles.
    """
    import random
    
    if level not in TRIVIA_QUESTIONS:
        return None
    
    available_questions = TRIVIA_QUESTIONS[level]
    
    if exclude_ids:
        available_questions = [q for q in available_questions if q["id"] not in exclude_ids]
    
    if not available_questions:
        return None
    
    question = random.choice(available_questions)
    question["level"] = level
    return question

def get_level_info(level: str) -> dict:
    """
    Obtiene información sobre un nivel de trivia.
    
    Args:
        level: Nivel a consultar.
        
    Returns:
        Dict con información del nivel.
    """
    return TRIVIA_LEVELS.get(level, None)

def get_available_levels(user_level: int) -> list:
    """
    Obtiene los niveles de trivia disponibles para un usuario.
    
    Args:
        user_level: Nivel del usuario.
        
    Returns:
        Lista de niveles disponibles.
    """
    available = []
    
    for level_key, level_info in TRIVIA_LEVELS.items():
        if level_info["level_required"] <= user_level:
            available.append({
                "key": level_key,
                "info": level_info,
                "question_count": len(TRIVIA_QUESTIONS.get(level_key, []))
            })
    
    # Ordenar por level_required
    available.sort(key=lambda x: x["info"]["level_required"])
    return available

def calculate_trivia_bonus(level: str, time_taken: int, timer_seconds: int) -> int:
    """
    Calcula bonus por velocidad en trivia.
    
    Args:
        level: Nivel de la pregunta.
        time_taken: Tiempo que tomó responder (segundos).
        timer_seconds: Tiempo máximo disponible.
        
    Returns:
        Bonus adicional por velocidad.
    """
    if time_taken >= timer_seconds:
        return 0
    
    level_info = TRIVIA_LEVELS.get(level)
    if not level_info:
        return 0
    
    # Calcular porcentaje de tiempo restante
    time_remaining = timer_seconds - time_taken
    speed_percentage = (time_remaining / timer_seconds) * 100
    
    # Bonus basado en velocidad y dificultad
    base_reward = level_info["reward"]
    bonus_multiplier = speed_percentage / 100  # 0.0 a 1.0
    
    # Bonus máximo es 50% de la recompensa base
    max_bonus = int(base_reward * 0.5)
    bonus = int(max_bonus * bonus_multiplier)
    
    return bonus

def format_trivia_stats(level_stats: dict) -> str:
    """
    Formatea estadísticas de trivia para mostrar.
    
    Args:
        level_stats: Estadísticas por nivel.
        
    Returns:
        String formateado con estadísticas.
    """
    if not level_stats:
        return "📊 Aún no tienes estadísticas de trivia.\n¡Responde algunas preguntas para empezar!"
    
    text = "📊 **Tus Estadísticas de Trivia**\n\n"
    
    total_questions = sum(stats.get("answered", 0) for stats in level_stats.values())
    total_correct = sum(stats.get("correct", 0) for stats in level_stats.values())
    
    if total_questions > 0:
        overall_accuracy = (total_correct / total_questions) * 100
        text += f"🎯 **Precisión General:** {overall_accuracy:.1f}% ({total_correct}/{total_questions})\n\n"
    
    for level_key in ["basico", "intermedio", "avanzado", "experto"]:
        if level_key in level_stats:
            level_info = TRIVIA_LEVELS[level_key]
            stats = level_stats[level_key]
            
            answered = stats.get("answered", 0)
            correct = stats.get("correct", 0)
            accuracy = (correct / answered * 100) if answered > 0 else 0
            
            text += f"{level_info['emoji']} **{level_info['name'].split(' ', 1)[1]}**\n"
            text += f"   Respondidas: {answered} | Correctas: {correct} | Precisión: {accuracy:.1f}%\n"
    
    return text