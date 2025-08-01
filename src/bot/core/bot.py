"""Configuración del bot."""

from aiogram import Bot
from aiogram.types import BotCommand

from ..config.constants import COMMANDS
from ...utils.sexy_logger import log

async def setup_bot(bot: Bot) -> None:
    """Configura el bot."""
    with log.section("CONFIGURACIÓN DEL BOT", "🤖"):
        # Establecer comandos
        commands = [
            BotCommand(command=command, description=description)
            for command, description in COMMANDS.items()
        ]
        
        await bot.set_my_commands(commands)
        log.startup(f"Comandos del bot configurados: {len(commands)} comandos disponibles")
        
        # Obtener información del bot
        bot_info = await bot.get_me()
        log.success(
            f"Bot @{bot_info.username} inicializado correctamente"
        )
        log.info(f"ID: {bot_info.id} | Grupos: {'✅' if bot_info.can_join_groups else '❌'} | Leer mensajes: {'✅' if bot_info.can_read_all_group_messages else '❌'}")