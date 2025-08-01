"""Tareas de mantenimiento para el sistema de roles."""

import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession

from ..services.role import RoleService
from ..database.engine import get_session

logger = structlog.get_logger()

async def check_vip_expirations():
    """Tarea programada para verificar expiraciones VIP."""
    logger.info("Ejecutando verificación de expiraciones VIP...")
    
    role_service = RoleService()
    
    try:
        async for session in get_session():
            expired_users = await role_service.check_vip_expiration(session)
            
            if expired_users:
                logger.info(f"VIP expirado para {len(expired_users)} usuarios", user_ids=expired_users)
                
                # Aquí se podrían enviar notificaciones a los usuarios
                # o publicar eventos para que otros servicios reaccionen
                
            else:
                logger.info("No se encontraron usuarios VIP expirados")
                
    except Exception as e:
        logger.error(f"Error en verificación de expiraciones VIP: {e}")

async def sync_admin_roles():
    """Tarea programada para sincronizar roles de administrador."""
    logger.info("Ejecutando sincronización de roles de administrador...")
    
    role_service = RoleService()
    
    try:
        async for session in get_session():
            # Obtener estadísticas antes
            stats_before = await role_service.get_role_statistics(session)
            
            # Aquí se podría implementar lógica adicional de sincronización
            # Por ejemplo, verificar que todos los admin_ids de configuración
            # estén marcados como admin en la base de datos
            
            # Obtener estadísticas después
            stats_after = await role_service.get_role_statistics(session)
            
            logger.info(
                "Sincronización de roles completada",
                admins_before=stats_before['admins'],
                admins_after=stats_after['admins']
            )
            
    except Exception as e:
        logger.error(f"Error en sincronización de roles: {e}")

def schedule_role_maintenance_tasks(scheduler: AsyncIOScheduler):
    """Programa las tareas de mantenimiento de roles."""
    
    # Verificar expiraciones VIP cada hora
    scheduler.add_job(
        check_vip_expirations,
        "interval",
        hours=1,
        id="check_vip_expirations",
        replace_existing=True,
    )
    
    # Sincronizar roles de administrador cada 6 horas
    scheduler.add_job(
        sync_admin_roles,
        "interval",
        hours=6,
        id="sync_admin_roles",
        replace_existing=True,
    )
    
    logger.info("Tareas de mantenimiento de roles programadas")