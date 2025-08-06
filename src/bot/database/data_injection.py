"""
Sistema de inyección de datos iniciales para desarrollo y testing.
Crea usuarios, puntos, fragmentos narrativos y otros datos necesarios.
"""

import logging
from datetime import datetime, timedelta
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .models.user import User
from .models.gamification import UserPoints, Mission, MissionTypeEnum
from .models.narrative import StoryFragment, NarrativeChoice, UserNarrativeState
from .engine import get_session

logger = logging.getLogger(__name__)

# Datos de prueba para usuarios
TEST_USERS = [
    {"id": 12345, "username": "test_user", "first_name": "Test", "is_vip": False},
    {"id": 67890, "username": "vip_user", "first_name": "VIP User", "is_vip": True},
    {"id": 11111, "username": "diana_test", "first_name": "Diana", "is_vip": False},
]

# Fragmentos narrativos básicos para testing
TEST_STORY_FRAGMENTS = [
    {
        "key": "welcome_1",
        "title": "Bienvenida de Diana",
        "character": "Diana",
        "text": "¡Hola! Soy Diana, tu asistente personal. Estoy aquí para acompañarte en esta aventura.",
        "tags": ["welcome", "introduction"],
        "reward_besitos": 10.0,
        "level_required": 1
    },
    {
        "key": "daily_greeting",
        "title": "Saludo Diario",
        "character": "Diana",
        "text": "¡Buenos días! ¿Cómo te encuentras hoy? Tengo algunas actividades preparadas para ti.",
        "tags": ["daily", "greeting"],
        "reward_besitos": 5.0,
        "level_required": 1
    },
    {
        "key": "trivia_intro",
        "title": "Introducción a Trivia",
        "character": "Diana",
        "text": "¡Es hora de poner a prueba tus conocimientos! ¿Estás listo para un desafío?",
        "tags": ["trivia", "challenge"],
        "reward_besitos": 15.0,
        "level_required": 1
    }
]

# Misiones básicas para testing (siguiendo estructura del modelo Mission)
TEST_MISSIONS = [
    {
        "key": "daily_login",
        "title": "Saludo Diario",
        "description": "Inicia sesión y saluda a Diana",
        "mission_type": "DAILY",
        "category": "social",
        "objectives": {"login": 1},
        "points_reward": 10.0,
        "requirements": {},
        "level_required": 1,
        "is_vip_only": False,
        "is_active": True
    },
    {
        "key": "daily_trivia",
        "title": "Trivia Diaria",
        "description": "Responde correctamente una pregunta de trivia",
        "mission_type": "DAILY",
        "category": "knowledge",
        "objectives": {"correct_answers": 1},
        "points_reward": 50.0,
        "requirements": {},
        "level_required": 1,
        "is_vip_only": False,
        "is_active": True
    },
    {
        "key": "first_steps",
        "title": "Primeros Pasos",
        "description": "Completa tu primera interacción con Diana",
        "mission_type": "ONE_TIME",
        "category": "onboarding",
        "objectives": {"interactions": 1},
        "points_reward": 25.0,
        "requirements": {},
        "level_required": 1,
        "is_vip_only": False,
        "is_active": True
    }
]

async def inject_test_users(session: AsyncSession) -> None:
    """Inyecta usuarios de prueba si no existen."""
    try:
        for user_data in TEST_USERS:
            # Verificar si el usuario ya existe
            result = await session.execute(
                select(User).where(User.id == user_data["id"])
            )
            existing_user = result.scalar_one_or_none()
            
            if not existing_user:
                user = User(
                    id=user_data["id"],
                    username=user_data["username"],
                    first_name=user_data["first_name"],
                    is_vip=user_data["is_vip"],
                    is_active=True
                )
                session.add(user)
                
                # Crear puntos iniciales para el usuario
                user_points = UserPoints(
                    user_id=user_data["id"],
                    current_points=100.0 if user_data["is_vip"] else 50.0,
                    total_earned=100.0 if user_data["is_vip"] else 50.0,
                    points_from_messages=10.0,
                    points_from_reactions=5.0,
                    points_from_missions=20.0,
                    points_from_dailygift=15.0,
                    active_multipliers={},
                    points_history=[]
                )
                session.add(user_points)
                
                logger.info(f"Created test user: {user_data['username']} (ID: {user_data['id']})")
            else:
                logger.debug(f"Test user already exists: {user_data['username']} (ID: {user_data['id']})")
                
    except Exception as e:
        logger.error(f"Error injecting test users: {e}")
        raise

async def inject_test_story_fragments(session: AsyncSession) -> None:
    """Inyecta fragmentos narrativos de prueba si no existen."""
    try:
        for fragment_data in TEST_STORY_FRAGMENTS:
            # Verificar si el fragmento ya existe
            result = await session.execute(
                select(StoryFragment).where(StoryFragment.key == fragment_data["key"])
            )
            existing_fragment = result.scalar_one_or_none()
            
            if not existing_fragment:
                fragment = StoryFragment(
                    key=fragment_data["key"],
                    title=fragment_data["title"],
                    character=fragment_data["character"],
                    text=fragment_data["text"],
                    tags=fragment_data["tags"],
                    reward_besitos=fragment_data["reward_besitos"],
                    level_required=fragment_data["level_required"],
                    reward_items={},
                    unlock_achievements=[]
                )
                session.add(fragment)
                logger.info(f"Created test story fragment: {fragment_data['key']}")
            else:
                logger.debug(f"Test story fragment already exists: {fragment_data['key']}")
                
    except Exception as e:
        logger.error(f"Error injecting test story fragments: {e}")
        raise

async def inject_test_missions(session: AsyncSession) -> None:
    """Inyecta misiones de prueba si no existen."""
    try:
        for mission_data in TEST_MISSIONS:
            # Verificar si la misión ya existe
            result = await session.execute(
                select(Mission).where(Mission.key == mission_data["key"])
            )
            existing_mission = result.scalar_one_or_none()
            
            if not existing_mission:
                mission = Mission(
                    key=mission_data["key"],
                    title=mission_data["title"],
                    description=mission_data["description"],
                    mission_type=getattr(MissionTypeEnum, mission_data["mission_type"]),
                    category=mission_data["category"],
                    objectives=mission_data["objectives"],
                    points_reward=mission_data["points_reward"],
                    requirements=mission_data["requirements"],
                    level_required=mission_data["level_required"],
                    is_vip_only=mission_data["is_vip_only"],
                    is_active=mission_data["is_active"],
                    item_rewards={}
                )
                session.add(mission)
                logger.info(f"Created test mission: {mission_data['key']}")
            else:
                logger.debug(f"Test mission already exists: {mission_data['key']}")
                
    except Exception as e:
        logger.error(f"Error injecting test missions: {e}")
        raise

async def inject_user_narrative_states(session: AsyncSession) -> None:
    """Inyecta estados narrativos iniciales para usuarios de prueba."""
    try:
        for user_data in TEST_USERS:
            user_id = user_data["id"]
            
            # Verificar si ya existe un estado narrativo para este usuario
            result = await session.execute(
                select(UserNarrativeState).where(UserNarrativeState.user_id == user_id)
            )
            existing_state = result.scalar_one_or_none()
            
            if not existing_state:
                narrative_state = UserNarrativeState(
                    user_id=user_id,
                    current_fragment_key="welcome_1",
                    visited_fragments=["welcome_1"],
                    decisions_made={},
                    narrative_items={},
                    narrative_variables={"first_visit": True}
                )
                session.add(narrative_state)
                logger.info(f"Created narrative state for user: {user_id}")
            else:
                logger.debug(f"Narrative state already exists for user: {user_id}")
                
    except Exception as e:
        logger.error(f"Error injecting user narrative states: {e}")
        raise

async def inject_all_test_data() -> None:
    """
    Función principal que inyecta todos los datos de prueba.
    Se ejecuta automáticamente cuando se inicializa la base de datos.
    """
    logger.info("Starting test data injection...")
    
    try:
        async for session in get_session():
            # Inyectar datos en orden de dependencias
            await inject_test_users(session)
            await inject_test_story_fragments(session)
            await inject_test_missions(session)
            await inject_user_narrative_states(session)
            
            # Confirmar transacción
            await session.commit()
            
            logger.info("✅ All test data injected successfully!")
            break  # Solo necesitamos una sesión
            
    except Exception as e:
        logger.error(f"❌ Error during test data injection: {e}")
        raise

async def clear_all_test_data() -> None:
    """Limpia todos los datos de prueba (útil para testing)."""
    logger.warning("Clearing all test data...")
    
    try:
        async for session in get_session():
            # Eliminar en orden inverso de dependencias
            for user_data in TEST_USERS:
                user_id = user_data["id"]
                
                # Eliminar estado narrativo
                await session.execute(
                    select(UserNarrativeState).where(UserNarrativeState.user_id == user_id)
                ).delete()
                
                # Eliminar puntos de usuario
                await session.execute(
                    select(UserPoints).where(UserPoints.user_id == user_id)
                ).delete()
                
                # Eliminar usuario
                await session.execute(
                    select(User).where(User.id == user_id)
                ).delete()
            
            # Eliminar fragmentos y misiones
            for fragment_data in TEST_STORY_FRAGMENTS:
                await session.execute(
                    select(StoryFragment).where(StoryFragment.key == fragment_data["key"])
                ).delete()
                
            for mission_data in TEST_MISSIONS:
                await session.execute(
                    select(Mission).where(Mission.key == mission_data["key"])
                ).delete()
                
            await session.commit()
            logger.warning("All test data cleared!")
            break
            
    except Exception as e:
        logger.error(f"Error clearing test data: {e}")
        raise