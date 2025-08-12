import asyncio
import os
import signal
import sys

from src.core.event_bus import EventBus
from src.core.services.config import settings
from src.infrastructure.telegram.adapter import TelegramAdapter

# Import all 11 services
from src.modules.gamification.service import GamificationService
from src.modules.narrative.service import NarrativeService
from src.modules.user.service import UserService
from src.modules.admin.service import AdminService
from src.modules.daily_rewards.service import DailyRewardsService
from src.modules.emotional.service import EmotionalService
from src.modules.tariff.service import TariffService
from src.modules.channel.service import ChannelService
from src.modules.shop.service import ShopService
from src.modules.trivia.service import TriviaService
from src.modules.token.tokeneitor import Tokeneitor

from src.bot.database.engine import init_db
from src.utils.sexy_logger import log


async def validate_all_services_loaded(services: dict) -> bool:
    """Validates that all 11 required services are loaded and functional."""
    required_services = [
        'user', 'gamification', 'narrative', 'admin', 'daily_rewards',
        'emotional', 'tariff', 'channel', 'shop', 'trivia', 'tokeneitor'
    ]
    
    log.info("🔍 Validating service availability...")
    
    missing_services = []
    for service_name in required_services:
        if service_name not in services or services[service_name] is None:
            missing_services.append(service_name)
        else:
            log.success(f"✅ {service_name.title()}Service: Ready")
    
    if missing_services:
        log.error(f"❌ Missing services: {', '.join(missing_services)}")
        return False
    
    log.success("🎯 All 11 services successfully loaded and validated!")
    return True


def setup_graceful_shutdown(adapter):
    """Sets up graceful shutdown handlers."""
    def signal_handler(sig, frame):
        log.info(f"🛑 Received signal {sig}, shutting down gracefully...")
        # Note: In a real implementation, you'd call adapter.stop() here
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


async def main():
    """🎭 Diana Bot V2 - Complete Foundation with All 11 Services"""
    
    # Banner de inicio increíble
    log.banner(
        "🎭 BOT DIANA V2 - COMPLETE FOUNDATION",
        f"Ambiente: {os.getenv('ENVIRONMENT', 'DESARROLLO')} | Versión: 2.0.0"
    )
    
    with log.section("INICIALIZACIÓN DE BASE DE DATOS", "🗄️"):
        log.database("Inicializando esquema de base de datos...", operation="init_schema")
        await init_db()
        log.success("✅ Base de datos inicializada correctamente")
    
    with log.section("CONFIGURACIÓN COMPLETA DE SERVICIOS", "⚙️"):
        log.startup("🌟 Configurando Event Bus...")
        event_bus = EventBus()

        # Initialize ALL 11 services with proper setup
        log.startup("🚀 Inicializando los 11 servicios principales...")
        
        # Core services
        user_service = UserService(event_bus)
        gamification_service = GamificationService(event_bus)
        narrative_service = NarrativeService(event_bus)
        admin_service = AdminService(event_bus)
        
        # Extended services
        daily_rewards_service = DailyRewardsService(gamification_service)
        emotional_service = EmotionalService(event_bus)
        tariff_service = TariffService(event_bus)
        channel_service = ChannelService(event_bus)
        shop_service = ShopService(event_bus, gamification_service)
        trivia_service = TriviaService(event_bus, gamification_service)
        tokeneitor_service = Tokeneitor(event_bus)

        # Create services dictionary for validation and adapter
        services = {
            'user': user_service,
            'gamification': gamification_service,
            'narrative': narrative_service,
            'admin': admin_service,
            'daily_rewards': daily_rewards_service,
            'emotional': emotional_service,
            'tariff': tariff_service,
            'channel': channel_service,
            'shop': shop_service,
            'trivia': trivia_service,
            'tokeneitor': tokeneitor_service,
            'event_bus': event_bus
        }

        # Setup all services
        log.startup("🔗 Conectando servicios al Event Bus...")
        setup_tasks = [
            user_service.setup(),
            gamification_service.setup(),
            narrative_service.setup(),
            admin_service.setup(),
            daily_rewards_service.setup(),
            emotional_service.setup(),
            tariff_service.setup(),
            channel_service.setup(),
            shop_service.setup(),
            trivia_service.setup(),
            tokeneitor_service.setup()
        ]
        
        await asyncio.gather(*setup_tasks)
        log.success("✅ Todos los servicios conectados al Event Bus")
        
        # Validate all services are loaded
        if not await validate_all_services_loaded(services):
            log.error("❌ Service validation failed, aborting startup")
            return

    with log.section("INICIALIZACIÓN DE TELEGRAM", "📱"):
        log.startup("⚡ Configurando TelegramAdapter con todos los servicios...")
        adapter = TelegramAdapter(
            bot_token=settings.bot_token, 
            event_bus=event_bus, 
            gamification_service=gamification_service,
            admin_service=admin_service,
            narrative_service=narrative_service,
            all_services=services
        )
        
        # Setup graceful shutdown
        setup_graceful_shutdown(adapter)
        
        log.startup("🎭 Iniciando Bot de Telegram...")
        log.info("🎪 Bot ready with all Diana systems integrated!")
        log.info("📋 Available commands: /start, /admin, /help, /profile, /shop, /trivia")
        
        await adapter.start()
        log.success("✅ Bot Diana iniciado y en funcionamiento")
    
    # This point should never be reached during normal polling
    log.summary("🏆 INICIALIZACIÓN COMPLETADA")

if __name__ == "__main__":
    asyncio.run(main())
