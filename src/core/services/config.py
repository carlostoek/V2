"""
Central configuration management for Diana Bot V2.
Provides a singleton for accessing configuration from various sources.
"""

import os
import json
from typing import Any, Dict, Optional
import structlog
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = structlog.get_logger()

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    bot_token: str = "default-token"  # Provide default for tests
    use_sqlite: Optional[str] = None
    database_url: Optional[str] = None

# Only initialize if not in test environment
settings = None
if "pytest" not in os.environ.get("_", ""):
    try:
        settings = Settings()
    except Exception:
        # Fallback for test environments
        settings = Settings(bot_token="test-token")

class CentralConfig:
    """
    Singleton configuration manager that centralizes all configuration.
    Loads config from environment variables, files, and supports runtime overrides.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            logger.info("Initializing CentralConfig singleton")
            cls._instance = super(CentralConfig, cls).__new__(cls)
            cls._instance._config = {}
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self) -> None:
        """
        Loads configuration from multiple sources in order of precedence:
        1. Default values
        2. Config files
        3. Environment variables
        """
        # Load default configuration
        self._load_defaults()
        
        # Load from config files
        self._load_from_files()
        
        # Override with environment variables
        self._load_from_env()
        
        logger.info("Configuration loaded", config_keys=list(self._config.keys()))
    
    def _load_defaults(self) -> None:
        """Loads default configuration values."""
        self._config = {
            "bot": {
                "token": settings.bot_token if hasattr(settings, 'bot_token') else "",
                "parse_mode": "HTML",
                "timeout": 30
            },
            "db": {
                "url": "sqlite+aiosqlite:///:memory:",
                "create_tables": False,
                "pool_size": 5,
                "max_overflow": 10
            },
            "narrative": {
                "starting_fragment": "welcome_1",
                "vip_fragments_enabled": True
            },
            "gamification": {
                "welcome_points": 10,
                "reaction_points": 5,
                "daily_mission_limit": 3
            },
            "admin": {
                "wait_time_minutes": 15
            },
            "emotional": {
                "initial_state": "Enigmática"
            }
        }
    
    def _load_from_files(self) -> None:
        """Loads configuration from JSON files."""
        config_paths = [
            os.path.join(os.getcwd(), "config.json"),
            os.path.join(os.getcwd(), "config", "config.json"),
            os.getenv("CONFIG_PATH", "")
        ]
        
        for path in config_paths:
            if path and os.path.exists(path):
                try:
                    with open(path, "r") as f:
                        file_config = json.load(f)
                        self._merge_config(file_config)
                    logger.info(f"Loaded configuration from {path}")
                except Exception as e:
                    logger.error(f"Error loading config from {path}", error=str(e))
    
    def _load_from_env(self) -> None:
        """Loads configuration from environment variables."""
        # Bot configuration
        if token := os.getenv("BOT_TOKEN"):
            self._config["bot"]["token"] = token
        
        # Database configuration
        if db_url := os.getenv("DATABASE_URL"):
            self._config["db"]["url"] = db_url
        
        if create_tables := os.getenv("CREATE_TABLES"):
            self._config["db"]["create_tables"] = create_tables.lower() in ("true", "1", "yes")
        
        # Admin configuration
        if wait_time := os.getenv("WAIT_TIME_MINUTES"):
            try:
                self._config["admin"]["wait_time_minutes"] = int(wait_time)
            except ValueError:
                pass
        
        # Other environment variables can be added here
    
    def _merge_config(self, new_config: Dict[str, Any]) -> None:
        """
        Recursively merges new configuration into existing configuration.
        
        Args:
            new_config: New configuration to merge.
        """
        for key, value in new_config.items():
            if isinstance(value, dict) and key in self._config and isinstance(self._config[key], dict):
                self._merge_config(value)
            else:
                self._config[key] = value
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Gets a configuration value by key path.
        
        Args:
            key_path: Dot-separated path to the configuration value.
            default: Default value to return if the key doesn't exist.
        
        Returns:
            The configuration value or default if not found.
        """
        keys = key_path.split(".")
        value = self._config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any) -> None:
        """
        Sets a configuration value by key path.
        
        Args:
            key_path: Dot-separated path to the configuration value.
            value: Value to set.
        """
        keys = key_path.split(".")
        config = self._config
        
        # Navigate to the last parent
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        # Set the value
        config[keys[-1]] = value
        logger.debug(f"Set config {key_path} = {value}")
    
    def get_all(self) -> Dict[str, Any]:
        """
        Gets the entire configuration.
        
        Returns:
            A copy of the entire configuration dictionary.
        """
        return self._config.copy()