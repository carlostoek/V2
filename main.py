import asyncio
import os

from src.core.event_bus import EventBus
from src.core.services.config import settings
from src.infrastructure.telegram.adapter import TelegramAdapter
from src.modules.gamification.service import GamificationService
from src.modules.narrative.service import NarrativeService
from src.modules.user.service import UserService
from src.modules.admin.service import AdminService
from src.bot.database.engine import init_db
from src.utils.sexy_logger import log
from src.bot.core.diana_master_system import DianaMasterInterface, AdaptiveContextEngine


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
        log.startup("Configurando contenedor de dependencias...")
        from src.bot.core.containers import ApplicationContainer
        
        container = ApplicationContainer()
        container.config.from_env() # Cargar configuración desde variables de entorno
        
        event_bus = container.core.event_bus()
        
        # Obtener servicios del contenedor
        log.startup("Obteniendo servicios del contenedor de dependencias...")
        user_service = container.services.user_service()
        gamification_service = container.services.gamification_service()
        narrative_service = container.services.narrative_service()
        admin_service = container.services.admin_service()
        
        services = {
            "user": user_service,
            "gamification": gamification_service,
            "narrative": narrative_service,
            "admin": admin_service,
            "emotional": container.services.emotional_service(),
            "role": container.services.role_service(),
            "tariff": container.services.tariff_service(),
            "daily_rewards": container.services.daily_rewards_service(),
        }

        # Conectar servicios al bus (si tienen método setup)
        log.startup("Conectando servicios al Event Bus (si aplica)...")
        # Check if service has a setup method before calling it
        if hasattr(user_service, 'setup'): await user_service.setup()
        if hasattr(gamification_service, 'setup'): await gamification_service.setup()
        if hasattr(narrative_service, 'setup'): await narrative_service.setup()
        if hasattr(admin_service, 'setup'): await admin_service.setup()
        if hasattr(services["emotional"], 'setup'): await services["emotional"].setup()
        if hasattr(services["role"], 'setup'): await services["role"].setup()
        if hasattr(services["tariff"], 'setup'): await services["tariff"].setup()
        if hasattr(services["daily_rewards"], 'setup'): await services["daily_rewards"].setup()
        log.success("✅ Servicios configurados y conectados al Event Bus")
        log.success("✅ Todos los servicios conectados al Event Bus")

    with log.section("INICIALIZACIÓN DE DIANA MASTER SYSTEM", "🤖"):
        log.startup("Creando instancia de Diana Master System...")
        diana_interface = DianaMasterInterface(services)
        log.success("✅ Diana Master System instanciado")

    with log.section("INICIALIZACIÓN DE TELEGRAM", "📱"):
        log.startup("Configurando adaptador de Telegram...")
        adapter = TelegramAdapter(
            bot_token=settings.BOT_TOKEN,
            event_bus=event_bus,
            diana_interface=diana_interface,
            services=services # Pass the entire services dictionary
        )
        
        log.startup("Iniciando Bot de Telegram...")
        
        await adapter.start()
        log.success("✅ Bot Diana iniciado y en funcionamiento")
    
    # Resumen final con métricas
    log.summary("🏆 INICIALIZACIÓN COMPLETADA")

if __name__ == "__main__":
    asyncio.run(main())
