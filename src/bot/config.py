"""
Configuración de la aplicación Diana Bot V2.
Configuración simplificada con SQLite por defecto para desarrollo.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class BotSettings(BaseSettings):
    """Configuración del bot con valores por defecto para desarrollo."""
    
    # Base de datos
    USE_SQLITE: bool = True
    DATABASE_URL: Optional[str] = None
    CREATE_TABLES: bool = True
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Bot
    BOT_TOKEN: str = "test-token"
    
    # Desarrollo
    DEBUG: bool = True
    INJECT_TEST_DATA: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Instancia global de configuración
settings = BotSettings()

# Si estamos en desarrollo/testing, usar SQLite
if settings.USE_SQLITE or not settings.DATABASE_URL:
    settings.USE_SQLITE = True
    if not settings.DATABASE_URL:
        # Crear archivo de base de datos en directorio del bot
        db_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            'diana_bot.db'
        )
        settings.DATABASE_URL = f"sqlite+aiosqlite:///{db_path}"