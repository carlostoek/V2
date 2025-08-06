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

async def create_default_fragments():
    """Crea fragmentos narrativos por defecto si no existen."""
    try:
        async for session in get_session():
            # Verificar si default_welcome existe
            existing = await session.execute(
                select(StoryFragment).where(StoryFragment.key == "default_welcome")
            )
            if not existing.scalar_one_or_none():
                fragment = StoryFragment(
                    key="default_welcome",
                    title="Bienvenida",
                    character="Diana",
                    text="¡Bienvenido! Soy Diana, tu asistente.",
                    tags=[],
                    reward_besitos=0.0,
                    level_required=1
                )
                session.add(fragment)
                await session.commit()
                logger.info("Created default_welcome fragment")
    except Exception as e:
        logger.error(f"Error creating default fragments: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(create_default_fragments())