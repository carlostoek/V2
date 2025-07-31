import pytest
import os
import sys
from typing import AsyncGenerator, List, Any
from aiogram import Bot
from aiogram.methods import TelegramMethod, GetMe
from aiogram.types import User

# Configurar variables de entorno para los tests
os.environ["BOT_TOKEN"] = "8426456639:AAHgA6kNgAUxT1l3EZJNKlwoE4xdcytbMLw"
os.environ["DATABASE_URL"] = "postgresql+asyncpg://test:test@localhost:5432/testdb"

class MockedBot(Bot):
    """Bot mockeado para interceptar llamadas a la API en tests."""
    def __init__(self, **kwargs):
        super().__init__(token="8426456639:AAHgA6kNgAUxT1l3EZJNKlwoE4xdcytbMLw", **kwargs)
        self.requests: List[TelegramMethod] = []

    async def __call__(self, method: TelegramMethod, **kwargs) -> Any:
        self.requests.append(method)
        if isinstance(method, GetMe):
            return User(id=self.id, is_bot=True, first_name="Test Bot", username="test_bot")
        return True # Simula una respuesta exitosa de la API

@pytest.fixture
async def mocked_bot() -> AsyncGenerator[MockedBot, None]:
    yield MockedBot()