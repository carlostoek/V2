"""Handler para el canje de tokens de suscripción."""

import logging
from aiogram import types
from aiogram.filters import CommandStart, Regexp
import re

from src.modules.token.tokeneitor import Tokeneitor


logger = logging.getLogger(__name__)


async def handle_token_redemption(
    message: types.Message, 
    command: types.BotCommand,
    tokeneitor: Tokeneitor
):
    """
    Maneja el canje de tokens de suscripción a través del comando /start.
    
    Si el comando contiene un token, verifica su validez y procesa el canje.
    De lo contrario, delega a otro handler para el mensaje de bienvenida estándar.
    
    Args:
        message: Mensaje del usuario
        command: Comando recibido
        tokeneitor: Servicio Tokeneitor para verificación de tokens
    """
    # Extraer token del comando
    args = command.args
    token_match = re.match(r"token_([a-zA-Z0-9_-]+)", args) if args else None
    
    if not token_match:
        # Si no hay token, este handler no debe procesar el mensaje
        return None
    
    token = token_match.group(1)
    user_id = message.from_user.id
    
    logger.info(f"Usuario {user_id} intentando canjear token: {token}")
    
    # Verificar token
    result = await tokeneitor.verify_token(token, user_id)
    
    if not result:
        # Token inválido
        await message.answer(
            "❌ <b>Token Inválido</b>\n\n"
            "El token que intentas canjear no es válido, ya ha sido utilizado o ha expirado.\n"
            "Por favor, contacta con el administrador del canal para obtener un nuevo enlace.",
            parse_mode="HTML"
        )
        return True  # Indicar que el mensaje fue procesado
    
    # Token válido, procesar canje
    channel_id = result["channel_id"]
    channel_name = result["name"]
    expiry_date = result["expiry_date"].strftime("%d/%m/%Y")
    
    # Aquí se generaría una invitación nativa de Telegram al canal
    # Esto normalmente requiere permisos de administrador del bot en el canal
    # y se implementaría usando el método create_chat_invite_link de Bot API
    
    # Por ahora, simulamos el proceso con un mensaje informativo
    await message.answer(
        "✅ <b>¡Token Canjeado Exitosamente!</b>\n\n"
        f"Has obtenido acceso VIP al canal <b>{channel_name}</b>.\n"
        f"Tu membresía expira el: <b>{expiry_date}</b>\n\n"
        "En unos momentos recibirás un enlace de invitación al canal.",
        parse_mode="HTML"
    )
    
    # Simular envío de invitación
    # En una implementación real, se generaría y enviaría una invitación real al canal
    await message.answer(
        f"🔗 <b>Invitación al Canal</b>\n\n"
        f"Aquí tienes tu enlace de invitación para unirte a <b>{channel_name}</b>:\n\n"
        f"https://t.me/+AbCdEfGhIjKlMnOp\n\n"  # Enlace de ejemplo
        f"Este enlace te permitirá acceder al canal con tu membresía VIP.",
        parse_mode="HTML"
    )
    
    return True  # Indicar que el mensaje fue procesado


def register_token_handlers(dp, tokeneitor):
    """Registra los handlers para canje de tokens."""
    # Solo capturar comandos /start que contengan tokens (formato: /start token_xxxxx)
    dp.message.register(
        lambda message, command: handle_token_redemption(message, command, tokeneitor),
        CommandStart(deep_link=True)  # Solo comandos /start con parámetros
    )