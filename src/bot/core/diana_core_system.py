"""
🏛️ DIANA CORE SYSTEM - Punto de entrada unificado
================================================

Orquesta la interacción entre todos los sistemas principales:
1. Master System (Interfaz de usuario)
2. Admin Master (Administración)
3. Services Integration (Conexión a servicios)
"""

from typing import Dict, Any
from .diana_master_system import DianaMasterInterface
from .diana_admin_master import DianaAdminMaster
from .diana_admin_services_integration import DianaAdminServicesIntegration

class DianaCoreSystem:
    def __init__(self, services: Dict[str, Any]):
        # Capa de integración compartida
        self.services_integration = DianaAdminServicesIntegration(services)
        
        # Sistemas principales
        self.master_system = DianaMasterInterface(
            services, 
            self.services_integration
        )
        self.admin_system = DianaAdminMaster(
            services,
            self.services_integration
        )
        
    async def get_system_health(self):
        """Obtiene estado de todos los sistemas"""
        return {
            'services': await self.services_integration.check_all_services_health(),
            'admin_system': True,
            'master_system': True
        }

def initialize_diana_core(dp, services: Dict[str, Any]):
    """Inicializa todo el ecosistema Diana"""
    core = DianaCoreSystem(services)
    
    # Registra routers
    dp.include_router(core.master_system.router)
    dp.include_router(core.admin_system.router)
    
    return core
