import asyncio
import os

from src.core.event_bus import EventBus
from src.bot.config.settings import settings
from src.infrastructure.telegram.adapter import TelegramAdapter
from src.modules.gamification.service import GamificationService
from src.modules.narrative.service import NarrativeService
from src.modules.user.service import UserService
from src.modules.admin.service import AdminService
from src.bot.core.diana_master_system import DianaMasterInterface, set_diana_master_instance
from src.bot.database.engine import init_db
from src.utils.sexy_logger import log


async def main():
    """Punto de entrada principal de la aplicación V2."""
    # Banner de inicio increíble
    log.banner(
        "🎭 BOT DIANA V2 - SISTEMA NARRATIVO",
        f"Ambiente: {os.getenv('ENVIRONMENT', 'DESARROLLO')} | Versión: 2.0.0"
    )
    
    with log.section("INICIALIZACIÓN DE BASE DE DATOS", "🗄️"):
        log.database("Inicializando esquema de base de datos...", operation="init_schema")
        await init_db()
        log.success("✅ Base de datos inicializada correctamente")
    
    with log.section("CONFIGURACIÓN DE SERVICIOS", "⚙️"):
        log.startup("Configurando Event Bus...")
        event_bus = EventBus()

        # Instanciar servicios
        log.startup("Inicializando servicios principales...")
        user_service = UserService(event_bus)
        gamification_service = GamificationService(event_bus)
        narrative_service = NarrativeService(event_bus)
        admin_service = AdminService(event_bus)

        # Conectar servicios al bus
        log.startup("Conectando servicios al Event Bus...")
        await user_service.setup()
        await gamification_service.setup()
        await narrative_service.setup()
        await admin_service.setup()
        log.success("✅ Todos los servicios conectados al Event Bus")

    with log.section("INICIALIZACIÓN DE DIANA MASTER SYSTEM", "🎭"):
        log.startup("Creando diccionario de servicios para DMS...")
        services = {
            'gamification': gamification_service,
            'narrative': narrative_service,
            'user': user_service,
            'admin': admin_service,
            'event_bus': event_bus
        }
        log.success("✅ Diccionario de servicios creado")

        log.startup("Inicializando Diana Master Interface...")
        diana_interface = DianaMasterInterface(services)
        set_diana_master_instance(diana_interface)
        log.success("✅ Diana Master Interface inicializada y configurada globalmente")

    with log.section("INICIALIZACIÓN DE TELEGRAM", "📱"):
        log.startup("Configurando adaptador de Telegram...")
        adapter = TelegramAdapter(
            bot_token=settings.BOT_TOKEN, 
            event_bus=event_bus, 
            gamification_service=gamification_service,
            admin_service=admin_service,
            narrative_service=narrative_service,
            user_service=user_service,
            diana_interface=diana_interface
        )
        
        log.startup("Iniciando Bot de Telegram...")
        
        await adapter.start()
        log.success("✅ Bot Diana iniciado y en funcionamiento")
    
    # Resumen final con métricas
    log.summary("🏆 INICIALIZACIÓN COMPLETADA")

if __name__ == "__main__":
    asyncio.run(main())
