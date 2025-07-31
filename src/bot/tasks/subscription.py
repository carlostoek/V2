"""Tareas relacionadas con suscripciones."""
import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.modules.admin.service import AdminService

logger = structlog.get_logger()

async def check_expiring_subscriptions(admin_service: AdminService):
    """Verifica las suscripciones que están a punto de expirar."""
    logger.info("Ejecutando tarea de verificación de suscripciones expirando...")
    expiring_subs = admin_service.get_expiring_subscriptions(1)
    if expiring_subs:
        logger.info(f"Suscripciones expirando encontradas: {len(expiring_subs)}")
        for sub in expiring_subs:
            logger.info(f"  - Usuario: {sub['user_id']}, Tarifa: {sub['tariff_id']}, Expira: {sub['expires_at']}")
            # Aquí iría la lógica para enviar un mensaje al usuario
    else:
        logger.info("No se encontraron suscripciones expirando.")

def schedule_subscription_tasks(scheduler: AsyncIOScheduler, admin_service: AdminService):
    """Programa las tareas relacionadas con suscripciones."""
    scheduler.add_job(
        check_expiring_subscriptions,
        "interval",
        days=1,
        args=[admin_service],
        id="check_expiring_subscriptions",
        replace_existing=True,
    )
    logger.info("Tarea de verificación de suscripciones programada.")
