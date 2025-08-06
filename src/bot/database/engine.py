"""Configuración del motor de base de datos."""

import logging
import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import select

from ..config import settings
from .base import Base
from .models import User, StoryFragment, NarrativeChoice, Achievement, Mission, UserPoints, UserNarrativeState, UserAchievement, UserMission # Importa todos los modelos para que estén disponibles para create_all

# Configurar el logger
logger = logging.getLogger(__name__)

# Crear el motor de base de datos
if settings.USE_SQLITE:
    # Usar SQLite para desarrollo
    # Usamos una base de datos en memoria para que se reinicie en cada inicio del bot
    sqlite_url = "sqlite+aiosqlite:///file::memory:?cache=shared"
    logger.info(f"Usando SQLite en memoria: {sqlite_url}")
    
    engine = create_async_engine(
        sqlite_url,
        echo=settings.DATABASE_ECHO,
        future=True,
        poolclass=NullPool # No usar pool para SQLite en memoria
    )
else:
    # Usar PostgreSQL para producción
    engine = create_async_engine(
        str(settings.DATABASE_URL),
        echo=settings.DATABASE_ECHO,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
        future=True,
    )

# Crear el fabricador de sesiones
async_session = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

async def load_sample_data(session: AsyncSession) -> None:
    """Carga datos de prueba en la base de datos."""
    logger.info("Cargando datos de prueba...")

    # Crear un usuario de prueba si no existe
    user = await session.execute(select(User).filter_by(id=123456789)).scalar_one_or_none()
    if not user:
        user = User(
            id=123456789,
            username="testuser",
            first_name="Test",
            last_name="User",
            language_code="es",
            is_admin=True,
            level=1,
            experience_points=0
        )
        session.add(user)
        await session.flush() # Para que el user.id esté disponible para relaciones

        # Inicializar UserPoints para el usuario
        user_points = UserPoints(user_id=user.id, current_points=100.0)
        session.add(user_points)

        # Inicializar UserNarrativeState para el usuario
        user_narrative_state = UserNarrativeState(user_id=user.id)
        session.add(user_narrative_state)

    # Crear un fragmento de historia de prueba
    story_fragment = await session.execute(select(StoryFragment).filter_by(key="intro_fragment")).scalar_one_or_none()
    if not story_fragment:
        story_fragment = StoryFragment(
            key="intro_fragment",
            title="El Inicio",
            character="Diana",
            text="Bienvenido a tu aventura. ¿Qué quieres hacer?",
            tags=["introduccion"],
            level_required=1
        )
        session.add(story_fragment)
        await session.flush()

        # Crear una opción narrativa de prueba
        narrative_choice = NarrativeChoice(
            fragment_key=story_fragment.key,
            text="Explorar",
            target_fragment_key="explore_fragment"
        )
        session.add(narrative_choice)

    # Crear un logro de prueba
    achievement = await session.execute(select(Achievement).filter_by(key="first_step")).scalar_one_or_none()
    if not achievement:
        achievement = Achievement(
            key="first_step",
            name="Primer Paso",
            description="Has dado tu primer paso en la aventura.",
            criteria={"type": "user_level", "value": 1},
            points_reward=10.0,
            category="general"
        )
        session.add(achievement)

    # Crear una misión de prueba
    mission = await session.execute(select(Mission).filter_by(key="welcome_mission")).scalar_one_or_none()
    if not mission:
        mission = Mission(
            key="welcome_mission",
            title="Misión de Bienvenida",
            description="Completa tu primera interacción con Diana.",
            mission_type="ONE_TIME",
            category="tutorial",
            objectives={"interactions": 1},
            points_reward=20.0
        )
        session.add(mission)

    await session.commit()
    logger.info("Datos de prueba cargados exitosamente.")

async def init_db() -> None:
    """Inicializar la base de datos."""
    async with engine.begin() as conn:
        # Crear tablas si está configurado para hacerlo
        # En desarrollo usamos CREATE_TABLES=True, en producción usamos migraciones
        if settings.CREATE_TABLES:
            logger.info("Creating database tables from models...")
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
            
            # Cargar datos de prueba solo si las tablas fueron creadas (primer inicio)
            async with async_session() as session:
                await load_sample_data(session)
        logger.info("Database initialized successfully")

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Devuelve una sesión de base de datos."""
    async with async_session() as session:
        try:
            yield session
        except Exception as e:
            logger.exception(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()