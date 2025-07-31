import pytest
from dependency_injector import containers

from src.bot.core.containers import ApplicationContainer
from src.modules.admin.service import AdminService
from src.modules.narrative.service import NarrativeService

@pytest.mark.asyncio
async def test_di_container_loads_correctly():
    """
    Verifica que el contenedor de DI se carga y resuelve los servicios.
    """
    container = ApplicationContainer()
    # Simular la carga de configuración
    container.core.config.from_dict({
        "bot_token": "fake-token"
    })

    # Verificar que los servicios clave se pueden resolver
    assert isinstance(container.services.admin_service(), AdminService)
    assert isinstance(container.services.narrative_service(), NarrativeService)

    # Asegurarse de que los singletons son la misma instancia
    bus1 = container.services.event_bus()
    bus2 = container.services.event_bus()
    assert bus1 is bus2

    # Limpiar el contenedor
    container.unwire()