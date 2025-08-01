"""Handler para obtener información del usuario."""

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

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
    
    info_text = f"""
🆔 **Tu información de Telegram:**

📱 **ID**: `{user.id}`
👤 **Nombre**: {user.first_name}
"""
    
    if user.last_name:
        info_text += f"📝 **Apellido**: {user.last_name}\n"
    
    if user.username:
        info_text += f"🏷️ **Username**: @{user.username}\n"
    
    if user.language_code:
        info_text += f"🌐 **Idioma**: {user.language_code}\n"
    
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