import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.core.event_bus import EventBus
from src.modules.admin.service import AdminService
from src.bot.database.models import Tariff
from src.bot.database.base import Base

@pytest.fixture
async def db_session() -> AsyncSession:
    """Crea una sesión de base de datos en memoria para los tests."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        yield session

@pytest.fixture
async def admin_service(db_session: AsyncSession) -> AdminService:
    """Crea una instancia del AdminService para los tests."""
    return AdminService(EventBus(), db_session)

@pytest.mark.asyncio
async def test_create_tariff(admin_service: AdminService):
    """Verifica que se puede crear una tarifa correctamente."""
    tariff = await admin_service.create_tariff("Test Tariff", 10.0, 30)
    assert tariff.name == "Test Tariff"
    assert tariff.price == 10.0
    assert tariff.duration_days == 30
    assert tariff.id is not None

@pytest.mark.asyncio
async def test_get_tariff(admin_service: AdminService):
    """Verifica que se puede recuperar una tarifa por su ID."""
    tariff = await admin_service.create_tariff("Test Tariff", 10.0, 30)
    retrieved_tariff = await admin_service.get_tariff(tariff.id)
    assert retrieved_tariff is not None
    assert retrieved_tariff.id == tariff.id

@pytest.mark.asyncio
async def test_get_all_tariffs(admin_service: AdminService):
    """Verifica que se pueden recuperar todas las tarifas."""
    await admin_service.create_tariff("Test Tariff 1", 10.0, 30)
    await admin_service.create_tariff("Test Tariff 2", 20.0, 60)
    all_tariffs = await admin_service.get_all_tariffs()
    assert len(all_tariffs) == 2

@pytest.mark.asyncio
async def test_delete_tariff(admin_service: AdminService):
    """Verifica que se puede eliminar una tarifa."""
    tariff = await admin_service.create_tariff("Test Tariff", 10.0, 30)
    assert await admin_service.delete_tariff(tariff.id) is True
    assert await admin_service.get_tariff(tariff.id) is None

@pytest.mark.asyncio
async def test_delete_nonexistent_tariff(admin_service: AdminService):
    """Verifica que eliminar una tarifa no existente devuelve False."""
    assert await admin_service.delete_tariff(999) is False