"""
Script para pruebas manuales de los handlers implementados.

Este script instancia y configura los handlers de usuario para poder
ser probados manualmente sin necesidad de ejecutar todo el bot.

Uso:
python -m tests.integration.run_manual_test
"""

import asyncio
import sys
import os
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage

# Configurar variables de entorno para pruebas
os.environ["BOT_TOKEN"] = "test_token"
os.environ["DATABASE_URL"] = "postgresql+asyncpg://test:test@localhost:5432/testdb"

# Importar módulos necesarios
from src.core.event_bus import EventBus
from src.modules.gamification.service import GamificationService
from src.modules.admin.service import AdminService
from src.bot.handlers.user import register_user_handlers

class MockMessage(types.Message):
    """Mensaje simulado para pruebas."""
    def __init__(self, text):
        self.text = text
        self.from_user = types.User(id=123, is_bot=False, first_name="Test User")
        self.chat = types.Chat(id=123, type="private")

    async def answer(self, text, reply_markup=None):
        """Simula la respuesta a un mensaje."""
        print("\n=== Bot Response ===")
        print(text)
        if reply_markup:
            print("\n=== Keyboard ===")
            for row in reply_markup.inline_keyboard:
                for button in row:
                    print(f"[{button.text}] -> {button.callback_data}")
        print("===================\n")

async def test_handlers():
    """Ejecuta pruebas manuales de los handlers implementados."""
    # Configurar componentes
    event_bus = EventBus()
    gamification_service = GamificationService(event_bus)
    admin_service = AdminService(event_bus)
    
    await gamification_service.setup()
    await admin_service.setup()
    
    # Configurar dispatcher
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Registrar handlers
    register_user_handlers(dp, event_bus, gamification_service, admin_service)
    
    print("=== Test de Handlers de Usuario ===")
    print("Simulando comandos... \n")
    
    # Simular comando /start
    message = MockMessage("/start")
    command = types.BotCommand(command="start", description="Iniciar bot")
    await dp.message.handlers[0].callback(message, command)
    
    # Simular comando /help
    message = MockMessage("/help")
    await dp.message.handlers[1].callback(message)
    
    # Simular comando /profile
    message = MockMessage("/profile")
    await dp.message.handlers[2].callback(message)
    
    print("\n=== Pruebas Completadas ===")

if __name__ == "__main__":
    try:
        asyncio.run(test_handlers())
    except Exception as e:
        print(f"Error durante la prueba: {e}")
        sys.exit(1)