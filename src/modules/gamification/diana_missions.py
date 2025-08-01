"""
Diana Validation Missions

Este módulo define misiones específicas para el sistema de validación Diana.
Estas misiones se integran con el sistema de gamificación existente.
"""

from typing import Dict, List, Any
from src.bot.database.models.gamification import MissionTypeEnum

# Definiciones de misiones Diana para insertar en la base de datos
DIANA_VALIDATION_MISSIONS = [
    {
        "key": "diana_validation_first_reaction",
        "title": "Primera Impresión",
        "description": "Demuestra tu capacidad de reacción rápida ante Diana. Reacciona a un mensaje en menos de 5 segundos.",
        "mission_type": MissionTypeEnum.ONE_TIME,
        "category": "diana_validation",
        "requirements": {
            "min_level": 1,
            "max_attempts": 3
        },
        "level_required": 1,
        "is_vip_only": False,
        "objectives": [
            {
                "id": "quick_reaction",
                "type": "diana_validation_completed",
                "required": 1,
                "description": "Completa la validación de reacción rápida (nivel 1→2)",
                "context": ["level_1_to_2"]
            }
        ],
        "time_limit_hours": 24,
        "points_reward": 50.0,
        "item_rewards": {
            "badges": ["quick_thinker"],
            "items": ["reaction_certificate"]
        },
        "achievement_key": "diana_first_validation",
        "is_active": True
    },
    
    {
        "key": "diana_validation_keen_observer",
        "title": "Observador Perspicaz",
        "description": "Demuestra tu capacidad de observación explorando al menos 5 fragmentos narrativos y completando la validación de observación.",
        "mission_type": MissionTypeEnum.ONE_TIME,
        "category": "diana_validation",
        "requirements": {
            "min_level": 2,
            "prerequisite_missions": ["diana_validation_first_reaction"]
        },
        "level_required": 2,
        "is_vip_only": False,
        "objectives": [
            {
                "id": "narrative_exploration",
                "type": "narrative_progression",
                "required": 5,
                "description": "Explora 5 fragmentos narrativos diferentes"
            },
            {
                "id": "observation_validation",
                "type": "diana_validation_completed",
                "required": 1,
                "description": "Completa la validación de observación (nivel 2→3)",
                "context": ["level_2_to_3"]
            }
        ],
        "time_limit_hours": 48,
        "points_reward": 75.0,
        "item_rewards": {
            "badges": ["keen_observer"],
            "items": ["observation_lens", "exploration_map"]
        },
        "achievement_key": "diana_observer_validation",
        "is_active": True
    },
    
    {
        "key": "diana_validation_desire_profile",
        "title": "Perfil de Deseo",
        "description": "Completa tu perfil de deseo respondiendo honestamente a las preguntas de Diana para acceder al nivel VIP.",
        "mission_type": MissionTypeEnum.ONE_TIME,
        "category": "diana_validation",
        "requirements": {
            "min_level": 3,
            "prerequisite_missions": ["diana_validation_keen_observer"]
        },
        "level_required": 3,
        "is_vip_only": False,
        "objectives": [
            {
                "id": "profile_completion",
                "type": "diana_validation_completed",
                "required": 1,
                "description": "Completa la validación de perfil de deseo (nivel 3→VIP)",
                "context": ["level_3_to_vip"]
            }
        ],
        "time_limit_hours": 72,
        "points_reward": 100.0,
        "item_rewards": {
            "badges": ["desire_explorer"],
            "items": ["vip_invitation", "desire_crystal"],
            "special_rewards": ["vip_discount_10"]
        },
        "achievement_key": "diana_desire_validation",
        "is_active": True
    },
    
    {
        "key": "diana_validation_empathy_master",
        "title": "Maestro de la Empatía",
        "description": "Demuestra tu comprensión emocional profunda respondiendo con empatía genuina a la vulnerabilidad de Diana.",
        "mission_type": MissionTypeEnum.ONE_TIME,
        "category": "diana_validation",
        "requirements": {
            "min_level": 5,
            "is_vip": True
        },
        "level_required": 5,
        "is_vip_only": True,
        "objectives": [
            {
                "id": "empathy_responses",
                "type": "narrative_validation_progress",
                "required": 3,
                "description": "Responde empáticamente a 3 momentos de vulnerabilidad de Diana"
            },
            {
                "id": "empathy_validation",
                "type": "diana_validation_completed",
                "required": 1,
                "description": "Completa la validación de empatía (nivel 5→6)",
                "context": ["level_5_to_6"]
            }
        ],
        "time_limit_hours": 96,
        "points_reward": 150.0,
        "item_rewards": {
            "badges": ["empathy_master", "inner_circle"],
            "items": ["empathy_crown", "heart_key"],
            "special_rewards": ["inner_circle_access"]
        },
        "achievement_key": "diana_empathy_validation",
        "is_active": True
    },
    
    # Misiones repetibles/diarias
    {
        "key": "diana_daily_interaction",
        "title": "Interacción Diaria con Diana",
        "description": "Interactúa con Diana diariamente para mantener tu conexión emocional.",
        "mission_type": MissionTypeEnum.DAILY,
        "category": "diana_daily",
        "requirements": {
            "min_level": 1
        },
        "level_required": 1,
        "is_vip_only": False,
        "objectives": [
            {
                "id": "daily_reactions",
                "type": "reactions",
                "required": 3,
                "description": "Reacciona a 3 mensajes de Diana"
            },
            {
                "id": "narrative_progress",
                "type": "narrative_progress",
                "required": 1,
                "description": "Avanza en al menos 1 fragmento narrativo"
            }
        ],
        "time_limit_hours": 24,
        "points_reward": 15.0,
        "item_rewards": {
            "items": ["daily_affection"]
        },
        "is_active": True
    },
    
    {
        "key": "diana_validation_retry_champion",
        "title": "Campeón de la Perseverancia",
        "description": "No te rindas ante los desafíos. Intenta validaciones hasta lograr el éxito.",
        "mission_type": MissionTypeEnum.WEEKLY,
        "category": "diana_validation",
        "requirements": {
            "min_level": 1
        },
        "level_required": 1,
        "is_vip_only": False,
        "objectives": [
            {
                "id": "validation_attempts",
                "type": "diana_validation_attempt",
                "required": 5,
                "description": "Intenta 5 validaciones Diana (exitosas o fallidas)"
            },
            {
                "id": "successful_validations",
                "type": "diana_validation_completed",
                "required": 2,
                "description": "Completa exitosamente 2 validaciones Diana"
            }
        ],
        "time_limit_hours": 168,  # 1 semana
        "points_reward": 40.0,
        "item_rewards": {
            "badges": ["persistent"],
            "items": ["retry_token"]
        },
        "is_active": True
    }
]

# Logros específicos para validaciones Diana
DIANA_VALIDATION_ACHIEVEMENTS = [
    {
        "key": "diana_first_validation",
        "name": "Primera Validación Diana",
        "description": "Completaste tu primera validación con Diana exitosamente.",
        "criteria": {
            "type": "diana_validation",
            "validation_type": "level_1_to_2",
            "min_score": 0.7
        },
        "points_reward": 25.0,
        "item_rewards": {
            "badges": ["diana_initiate"]
        },
        "category": "diana_validation",
        "difficulty": 1,
        "is_hidden": False,
        "is_milestone": True
    },
    
    {
        "key": "diana_observer_validation",
        "name": "Observador Certificado",
        "description": "Diana reconoce tu capacidad de observación y análisis.",
        "criteria": {
            "type": "diana_validation",
            "validation_type": "level_2_to_3",
            "min_score": 0.8
        },
        "points_reward": 40.0,
        "item_rewards": {
            "badges": ["certified_observer"]
        },
        "category": "diana_validation",
        "difficulty": 2,
        "is_hidden": False,
        "is_milestone": True
    },
    
    {
        "key": "diana_desire_validation",
        "name": "Explorador del Deseo",
        "description": "Has demostrado comprensión profunda de tus propios deseos.",
        "criteria": {
            "type": "diana_validation",
            "validation_type": "level_3_to_vip",
            "min_score": 0.75
        },
        "points_reward": 60.0,
        "item_rewards": {
            "badges": ["desire_explorer"],
            "special": ["vip_early_access"]
        },
        "category": "diana_validation",
        "difficulty": 3,
        "is_hidden": False,
        "is_milestone": True
    },
    
    {
        "key": "diana_empathy_validation",
        "name": "Maestro de la Empatía",
        "description": "Has alcanzado el más alto nivel de comprensión emocional con Diana.",
        "criteria": {
            "type": "diana_validation",
            "validation_type": "level_5_to_6",
            "min_score": 0.9
        },
        "points_reward": 100.0,
        "item_rewards": {
            "badges": ["empathy_master", "inner_circle_member"],
            "special": ["exclusive_content_access"]
        },
        "category": "diana_validation",
        "difficulty": 5,
        "is_hidden": False,
        "is_milestone": True
    },
    
    {
        "key": "diana_perfect_validator",
        "name": "Validador Perfecto",
        "description": "Has logrado puntuaciones perfectas en múltiples validaciones Diana.",
        "criteria": {
            "type": "diana_validation",
            "validation_type": "any",
            "min_score": 1.0,
            "required_count": 3
        },
        "points_reward": 200.0,
        "item_rewards": {
            "badges": ["perfect_validator"],
            "special": ["diana_personal_message"]
        },
        "category": "diana_validation",
        "difficulty": 5,
        "is_hidden": True,  # Logro secreto
        "is_milestone": True
    },
    
    {
        "key": "diana_persistent_challenger",
        "name": "Desafiante Persistente",
        "description": "Has demostrado perseverancia intentando validaciones múltiples veces.",
        "criteria": {
            "type": "diana_validation_attempts",
            "min_attempts": 10,
            "success_rate": 0.6  # Al menos 60% de éxito
        },
        "points_reward": 50.0,
        "item_rewards": {
            "badges": ["persistent_challenger"]
        },
        "category": "diana_validation",
        "difficulty": 2,
        "is_hidden": False,
        "is_milestone": False
    }
]


def get_diana_missions_data() -> Dict[str, List[Dict[str, Any]]]:
    """
    Obtiene los datos de misiones y logros Diana para insertar en la base de datos.
    
    Returns:
        Diccionario con misiones y logros Diana
    """
    return {
        "missions": DIANA_VALIDATION_MISSIONS,
        "achievements": DIANA_VALIDATION_ACHIEVEMENTS
    }


def get_mission_by_key(mission_key: str) -> Dict[str, Any]:
    """
    Obtiene una misión específica por su clave.
    
    Args:
        mission_key: Clave de la misión
        
    Returns:
        Datos de la misión o None si no existe
    """
    for mission in DIANA_VALIDATION_MISSIONS:
        if mission["key"] == mission_key:
            return mission
    return None


def get_achievement_by_key(achievement_key: str) -> Dict[str, Any]:
    """
    Obtiene un logro específico por su clave.
    
    Args:
        achievement_key: Clave del logro
        
    Returns:
        Datos del logro o None si no existe
    """
    for achievement in DIANA_VALIDATION_ACHIEVEMENTS:
        if achievement["key"] == achievement_key:
            return achievement
    return None


def get_missions_for_level(level: int, is_vip: bool = False) -> List[Dict[str, Any]]:
    """
    Obtiene misiones disponibles para un nivel específico.
    
    Args:
        level: Nivel del usuario
        is_vip: Si el usuario es VIP
        
    Returns:
        Lista de misiones disponibles
    """
    available_missions = []
    
    for mission in DIANA_VALIDATION_MISSIONS:
        # Verificar nivel requerido
        if mission["level_required"] > level:
            continue
            
        # Verificar si es VIP only
        if mission["is_vip_only"] and not is_vip:
            continue
            
        available_missions.append(mission)
    
    return available_missions