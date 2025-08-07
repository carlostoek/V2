"""Configuración del motor de base de datos."""

import logging
import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from ..config import settings
from .base import Base
from .models import *  # Importa todos los modelos para que estén disponibles para create_all

# Configurar el logger
logger = logging.getLogger(__name__)

# Crear el motor de base de datos
if settings.USE_SQLITE:
    # Usar SQLite para desarrollo
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bot.db')
    # Asegúrate de que el directorio existe
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    sqlite_url = f"sqlite+aiosqlite:///{db_path}"
    logger.info(f"Usando SQLite en {db_path}")
    
    engine = create_async_engine(
        sqlite_url,
        echo=settings.DATABASE_ECHO,
        future=True,
        # SQLite no soporta pool_size ni max_overflow
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

async def init_db() -> None:
    """Inicializar la base de datos."""
    async with engine.begin() as conn:
        # Crear tablas si está configurado para hacerlo
        # En desarrollo usamos CREATE_TABLES=True, en producción usamos migraciones
        if settings.CREATE_TABLES:
            logger.info("Creating database tables from models...")
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
            
            # Inyectar datos de prueba si está habilitado
            if hasattr(settings, 'INJECT_TEST_DATA') and settings.INJECT_TEST_DATA:
                logger.info("Injecting test data...")
                # from .data_injection import inject_all_test_data  # Temporarily disabled
                # await inject_all_test_data()
            elif hasattr(settings, 'USE_SQLITE') and settings.USE_SQLITE:
                # Por defecto inyectar datos en SQLite para desarrollo
                logger.info("Injecting test data for SQLite development...")
                # from .data_injection import inject_all_test_data  # Temporarily disabled
                # await inject_all_test_data()
                
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