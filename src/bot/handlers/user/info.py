"""Handler para obtener información del usuario."""

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession

from ...services.role import RoleService

info_router = Router()

@info_router.message(Command("id", "myid", "info"))
async def get_user_info(message: Message):
    """
    Comando para obtener información del usuario.
    
    Útil para que los administradores obtengan su ID de Telegram.
    """
    user = message.from_user
    if not user:
        await message.answer("❌ Error: No se pudo obtener información del usuario")
        return
    
    # Obtener información de rol si está disponible
    user_role = getattr(message, 'user_role', 'free')
    user_permissions = getattr(message, 'user_permissions', {})
    
    info_text = f"""
🆔 **Tu información de Telegram:**

📱 **ID**: `{user.id}`
👤 **Nombre**: {user.first_name}
👑 **Rol actual**: {user_role.upper()}
"""
    
    if user.last_name:
        info_text += f"📝 **Apellido**: {user.last_name}\n"
    
    if user.username:
        info_text += f"🏷️ **Username**: @{user.username}\n"
    
    if user.language_code:
        info_text += f"🌐 **Idioma**: {user.language_code}\n"
    
    # Mostrar permisos principales
    info_text += f"\n🔐 **Permisos principales**:\n"
    key_permissions = [
        ("can_access_admin_panel", "Panel de administración"),
        ("can_access_vip_channels", "Canales VIP"),
        ("can_access_vip_content", "Contenido VIP"),
        ("can_manage_users", "Gestionar usuarios")
    ]
    
    for perm_key, perm_name in key_permissions:
        has_perm = user_permissions.get(perm_key, False)
        icon = "✅" if has_perm else "❌"
        info_text += f"• {icon} {perm_name}\n"
    
    info_text += f"""
🤖 **Para hacerte administrador**, agrega tu ID a la variable de entorno:
```
ADMIN_USER_IDS={user.id}
```

Si hay otros administradores, sepáralos con comas:
```
ADMIN_USER_IDS={user.id},123456789,987654321
```
"""
    
    await message.answer(info_text, parse_mode="Markdown")