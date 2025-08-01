"""Test environment setup for DianaBot V2.

This module sets up the necessary environment variables and configuration
for running tests without requiring actual production credentials.
"""

import os
import sys
from pathlib import Path


def setup_test_environment():
    """Set up test environment variables before importing any application modules."""
    
    # Set test environment variables
    test_env_vars = {
        "BOT_TOKEN": "test_token_12345:ABCDEF_test_token_for_unit_tests",
        "DATABASE_URL": "sqlite+aiosqlite:///:memory:",
        "USE_SQLITE": "True",
        "DATABASE_ECHO": "False",
        "CREATE_TABLES": "True",
        "ADMIN_USER_IDS": "123456789,987654321",
        "VIP_CHANNEL_ID": "-1001234567890",
        "FREE_CHANNEL_ID": "-1001234567891",
        "ENABLE_ANALYTICS": "False",
        "ENABLE_BACKGROUND_TASKS": "False",
        "ENABLE_EMOTIONAL_SYSTEM": "True",
        "LOG_LEVEL": "DEBUG",
        "TASK_SCHEDULER_TIMEZONE": "UTC",
        # Add any other required environment variables here
    }
    
    # Only set if not already set (allows override)
    for key, value in test_env_vars.items():
        if key not in os.environ:
            os.environ[key] = value


def reset_settings_singleton():
    """Reset the settings singleton for clean test state."""
    # Clear any cached settings modules
    modules_to_clear = []
    for module_name in sys.modules.keys():
        if 'settings' in module_name or 'config' in module_name:
            modules_to_clear.append(module_name)
    
    for module_name in modules_to_clear:
        if module_name in sys.modules:
            del sys.modules[module_name]


if __name__ == "__main__":
    # This can be run directly to verify test environment setup
    setup_test_environment()
    print("Test environment variables set:")
    for key in ["BOT_TOKEN", "DATABASE_URL", "USE_SQLITE"]:
        print(f"  {key}: {os.environ.get(key, 'NOT SET')}")