"""
Dependency Injection Container configuration using dependency-injector.
This module provides a robust DI implementation for the Diana Bot V2 project.
"""

import os
from typing import Any, Dict
from dependency_injector import containers, providers
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from src.core.event_bus import EventBus
from src.core.interfaces.IEventBus import IEventBus
from src.modules.narrative.service import NarrativeService
from src.modules.gamification.service import GamificationService
from ..services.user import UserService
from ..services.emotional import EmotionalService
from ..services.admin import AdminService
from ..services.role import RoleService
from ..database import async_session, get_session
from src.core.services.config import CentralConfig

class CoreContainer(containers.DeclarativeContainer):
    """Core services container."""
    
    config = providers.Configuration()
    
    # Configure from environment variables
    config.bot.token.from_env("BOT_TOKEN")
    config.bot.parse_mode.from_env("PARSE_MODE", "HTML")
    config.db.url.from_env("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
    config.db.create_tables.from_env("CREATE_TABLES", "False")
    
    # Core dependencies
    central_config = providers.Singleton(CentralConfig)
    
    # Event bus - core messaging system
    event_bus = providers.Singleton(EventBus)
    
    # Database session provider
    db_session = providers.Resource(get_session)
    
    # Bot and dispatcher instances
    bot = providers.Singleton(
        Bot, 
        token=config.bot.token,
        parse_mode=ParseMode.HTML
    )
    dispatcher = providers.Singleton(Dispatcher)


from src.modules.tariff.service import TariffService
from src.modules.daily_rewards.service import DailyRewardsService
from ..services.emotional import (
    CharacterProfileService,
    RelationshipService,
    EmotionalStateService,
    EmotionalMemoryService,
    PersonalityAdaptationService
)

class ServicesContainer(containers.DeclarativeContainer):
    """Application services container."""
    
    config = providers.Configuration()
    event_bus = providers.Dependency(provided_type=IEventBus)
    db_session = providers.Dependency()
    central_config = providers.Dependency()
    
    # Emotional sub-services
    character_profile_service = providers.Factory(
        CharacterProfileService
    )
    
    emotional_state_service = providers.Factory(
        EmotionalStateService,
        character_profile_service=character_profile_service
    )
    
    personality_adaptation_service = providers.Factory(
        PersonalityAdaptationService
    )
    
    relationship_service = providers.Factory(
        RelationshipService,
        emotional_state_service=emotional_state_service,
        personality_service=personality_adaptation_service
    )
    
    emotional_memory_service = providers.Factory(
        EmotionalMemoryService
    )

    # Module services
    narrative_service = providers.Factory(
        NarrativeService,
        event_bus=event_bus
    )
    
    gamification_service = providers.Factory(
        GamificationService,
        event_bus=event_bus
    )
    
    user_service = providers.Factory(
        UserService
    )
    
    emotional_service = providers.Factory(
        EmotionalService,
        profile_service=character_profile_service,
        relationship_service=relationship_service,
        emotional_state_service=emotional_state_service,
        memory_service=emotional_memory_service,
        personality_service=personality_adaptation_service
    )
    
    admin_service = providers.Factory(
        AdminService,
        event_bus=event_bus
    )
    
    role_service = providers.Factory(
        RoleService
    )

    tariff_service = providers.Factory(
        TariffService,
        event_bus=event_bus
    )

    daily_rewards_service = providers.Factory(
        DailyRewardsService,
        gamification_service=gamification_service
    )


class ApplicationContainer(containers.DeclarativeContainer):
    """Main application container."""
    
    config = providers.Configuration()
    
    # Wire sub-containers
    core = providers.Container(
        CoreContainer,
        config=config
    )
    
    services = providers.Container(
        ServicesContainer,
        config=config,
        event_bus=core.event_bus,
        db_session=core.db_session,
        central_config=core.central_config
    )


# Create container instance for global use
container = ApplicationContainer()
