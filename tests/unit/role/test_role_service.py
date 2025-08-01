"""Tests para el servicio de roles."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from src.bot.services.role import RoleService, RoleType
from src.bot.database.models.user import User


@pytest.fixture
def role_service():
    """Fixture para el servicio de roles."""
    return RoleService()


@pytest.fixture
def mock_session():
    """Mock para la sesión de base de datos."""
    return AsyncMock()


@pytest.fixture
def sample_admin_user():
    """Usuario administrador de ejemplo."""
    user = MagicMock(spec=User)
    user.id = 123456789
    user.username = "admin_user"
    user.first_name = "Admin"
    user.is_admin = True
    user.is_vip = False
    user.vip_expires_at = None
    return user


@pytest.fixture
def sample_vip_user():
    """Usuario VIP de ejemplo."""
    user = MagicMock(spec=User)
    user.id = 987654321
    user.username = "vip_user"
    user.first_name = "VIP User"
    user.is_admin = False
    user.is_vip = True
    user.vip_expires_at = datetime.now() + timedelta(days=30)
    return user


@pytest.fixture
def sample_free_user():
    """Usuario gratuito de ejemplo."""
    user = MagicMock(spec=User)
    user.id = 555666777
    user.username = "free_user"
    user.first_name = "Free User"
    user.is_admin = False
    user.is_vip = False
    user.vip_expires_at = None
    return user


@pytest.mark.asyncio
async def test_get_user_role_admin_by_config(role_service, mock_session):
    """Test que verifica detección de administrador por configuración."""
    user_id = 123456789
    
    with patch('src.bot.services.role.settings.admin_ids', {user_id}):
        role = await role_service.get_user_role(mock_session, user_id)
        assert role == RoleType.ADMIN


@pytest.mark.asyncio
async def test_get_user_role_admin_by_database(role_service, mock_session, sample_admin_user):
    """Test que verifica detección de administrador por base de datos."""
    user_id = sample_admin_user.id
    
    # Mock para que no sea admin por configuración
    with patch('src.bot.services.role.settings.admin_ids', set()):
        # Mock para get_by_id
        role_service.get_by_id = AsyncMock(return_value=sample_admin_user)
        
        role = await role_service.get_user_role(mock_session, user_id)
        assert role == RoleType.ADMIN


@pytest.mark.asyncio
async def test_get_user_role_vip_active(role_service, mock_session, sample_vip_user):
    """Test que verifica detección de usuario VIP activo."""
    user_id = sample_vip_user.id
    
    with patch('src.bot.services.role.settings.admin_ids', set()):
        role_service.get_by_id = AsyncMock(return_value=sample_vip_user)
        role_service.is_vip_active = AsyncMock(return_value=True)
        
        role = await role_service.get_user_role(mock_session, user_id)
        assert role == RoleType.VIP


@pytest.mark.asyncio
async def test_get_user_role_free(role_service, mock_session, sample_free_user):
    """Test que verifica detección de usuario gratuito."""
    user_id = sample_free_user.id
    
    with patch('src.bot.services.role.settings.admin_ids', set()):
        role_service.get_by_id = AsyncMock(return_value=sample_free_user)
        role_service.is_vip_active = AsyncMock(return_value=False)
        
        role = await role_service.get_user_role(mock_session, user_id)
        assert role == RoleType.FREE


@pytest.mark.asyncio
async def test_is_vip_active_with_valid_expiration(role_service, mock_session):
    """Test que verifica VIP activo con fecha de expiración válida."""
    user_id = 123
    
    # Usuario VIP con expiración futura
    user = MagicMock()
    user.is_vip = True
    user.vip_expires_at = datetime.now() + timedelta(days=10)
    
    role_service.get_by_id = AsyncMock(return_value=user)
    
    result = await role_service.is_vip_active(mock_session, user_id)
    assert result == True


@pytest.mark.asyncio
async def test_is_vip_active_with_expired_date(role_service, mock_session):
    """Test que verifica VIP expirado."""
    user_id = 123
    
    # Usuario VIP con expiración pasada
    user = MagicMock()
    user.is_vip = True
    user.vip_expires_at = datetime.now() - timedelta(days=1)
    
    role_service.get_by_id = AsyncMock(return_value=user)
    role_service.revoke_vip_status = AsyncMock(return_value=True)
    
    result = await role_service.is_vip_active(mock_session, user_id)
    assert result == False
    
    # Debe haber llamado a revoke_vip_status
    role_service.revoke_vip_status.assert_called_once_with(mock_session, user_id)


@pytest.mark.asyncio
async def test_grant_vip_status(role_service, mock_session):
    """Test que verifica otorgamiento de estado VIP."""
    user_id = 123
    duration_days = 30
    granted_by = 456
    
    # Usuario existente
    user = MagicMock()
    user.id = user_id
    
    role_service.get_by_id = AsyncMock(return_value=user)
    role_service.is_admin = AsyncMock(return_value=True)
    
    result = await role_service.grant_vip_status(
        mock_session, user_id, duration_days, granted_by
    )
    
    assert result == True
    assert user.is_vip == True
    assert user.vip_expires_at is not None


@pytest.mark.asyncio
async def test_get_user_permissions_admin(role_service, mock_session):
    """Test que verifica permisos de administrador."""
    user_id = 123
    
    role_service.get_user_role = AsyncMock(return_value=RoleType.ADMIN)
    
    permissions = await role_service.get_user_permissions(mock_session, user_id)
    
    # Administradores deben tener todos los permisos
    assert permissions["can_access_admin_panel"] == True
    assert permissions["can_manage_users"] == True
    assert permissions["can_manage_channels"] == True
    assert permissions["can_access_vip_channels"] == True


@pytest.mark.asyncio
async def test_get_user_permissions_vip(role_service, mock_session):
    """Test que verifica permisos de usuario VIP."""
    user_id = 123
    
    role_service.get_user_role = AsyncMock(return_value=RoleType.VIP)
    
    permissions = await role_service.get_user_permissions(mock_session, user_id)
    
    # VIP debe tener permisos específicos
    assert permissions["can_access_vip_channels"] == True
    assert permissions["can_access_vip_content"] == True
    assert permissions["can_participate_auctions"] == True
    
    # Pero no permisos de administración
    assert permissions["can_access_admin_panel"] == False
    assert permissions["can_manage_users"] == False


@pytest.mark.asyncio
async def test_get_user_permissions_free(role_service, mock_session):
    """Test que verifica permisos de usuario gratuito."""
    user_id = 123
    
    role_service.get_user_role = AsyncMock(return_value=RoleType.FREE)
    
    permissions = await role_service.get_user_permissions(mock_session, user_id)
    
    # Usuario gratuito debe tener permisos básicos
    assert permissions["can_use_bot"] == True
    assert permissions["can_access_free_channels"] == True
    assert permissions["can_earn_points"] == True
    
    # Pero no permisos premium
    assert permissions["can_access_vip_channels"] == False
    assert permissions["can_access_admin_panel"] == False


@pytest.mark.asyncio
async def test_check_permission(role_service, mock_session):
    """Test que verifica verificación de permisos específicos."""
    user_id = 123
    permission = "can_manage_users"
    
    role_service.get_user_permissions = AsyncMock(return_value={
        "can_manage_users": True,
        "can_access_admin_panel": False
    })
    
    # Verificar permiso que tiene
    result = await role_service.check_permission(mock_session, user_id, permission)
    assert result == True
    
    # Verificar permiso que no tiene
    result = await role_service.check_permission(mock_session, user_id, "can_access_admin_panel")
    assert result == False


@pytest.mark.asyncio
async def test_sync_admin_from_config(role_service, mock_session):
    """Test que verifica sincronización de administrador desde configuración."""
    user_id = 123456789
    user_data = {
        "username": "test_admin",
        "first_name": "Test Admin"
    }
    
    with patch('src.bot.services.role.settings.admin_ids', {user_id}):
        # Usuario no existe en base de datos
        role_service.get_by_id = AsyncMock(return_value=None)
        role_service.create = AsyncMock(return_value=MagicMock())
        
        await role_service.sync_admin_from_config(mock_session, user_id, user_data)
        
        # Debe haber creado el usuario como admin
        role_service.create.assert_called_once()
        created_user_data = role_service.create.call_args[0][1]
        assert created_user_data["is_admin"] == True
        assert created_user_data["id"] == user_id