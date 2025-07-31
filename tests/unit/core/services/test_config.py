"""Tests for the CentralConfig singleton."""

import os
import tempfile
import json
import pytest
from unittest.mock import patch

from src.core.services.config import CentralConfig


def test_singleton_pattern():
    """Test that CentralConfig follows the singleton pattern."""
    # Create two instances
    config1 = CentralConfig()
    config2 = CentralConfig()
    
    # They should be the same object
    assert config1 is config2


def test_default_config():
    """Test that default configuration is loaded."""
    # Reset the singleton for this test
    CentralConfig._instance = None
    
    # Create a new instance
    config = CentralConfig()
    
    # Check some default values
    assert config.get("bot.parse_mode") == "HTML"
    assert config.get("gamification.welcome_points") == 10
    assert config.get("admin.wait_time_minutes") == 15


def test_env_var_loading():
    """Test loading configuration from environment variables."""
    # Reset the singleton for this test
    CentralConfig._instance = None
    
    # Set environment variables
    with patch.dict("os.environ", {
        "BOT_TOKEN": "test-token-from-env",
        "WAIT_TIME_MINUTES": "30"
    }):
        # Create a new instance
        config = CentralConfig()
        
        # Check that environment variables were loaded
        assert config.get("bot.token") == "test-token-from-env"
        assert config.get("admin.wait_time_minutes") == 30


def test_file_loading():
    """Test loading configuration from a file."""
    # Reset the singleton for this test
    CentralConfig._instance = None
    
    # Create a temporary config file
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".json") as temp_file:
        # Write config to the file
        config_data = {
            "bot": {
                "token": "test-token-from-file",
                "parse_mode": "Markdown"
            },
            "narrative": {
                "starting_fragment": "custom_welcome"
            }
        }
        json.dump(config_data, temp_file)
        temp_file.flush()
        
        # Set CONFIG_PATH environment variable
        with patch.dict("os.environ", {"CONFIG_PATH": temp_file.name}):
            # Create a new instance
            config = CentralConfig()
            
            # Check that file configuration was loaded
            assert config.get("bot.token") == "test-token-from-file"
            assert config.get("bot.parse_mode") == "Markdown"
            assert config.get("narrative.starting_fragment") == "custom_welcome"


def test_get_with_default():
    """Test getting a configuration value with a default."""
    # Reset the singleton for this test
    CentralConfig._instance = None
    
    # Create a new instance
    config = CentralConfig()
    
    # Get a value that doesn't exist
    value = config.get("non.existent.key", "default-value")
    
    # Should return the default value
    assert value == "default-value"


def test_set_config_value():
    """Test setting a configuration value."""
    # Reset the singleton for this test
    CentralConfig._instance = None
    
    # Create a new instance
    config = CentralConfig()
    
    # Set a value
    config.set("custom.key", "custom-value")
    
    # Get the value
    value = config.get("custom.key")
    
    # Should return the set value
    assert value == "custom-value"


def test_set_nested_config_value():
    """Test setting a nested configuration value."""
    # Reset the singleton for this test
    CentralConfig._instance = None
    
    # Create a new instance
    config = CentralConfig()
    
    # Set a nested value
    config.set("custom.nested.key", "nested-value")
    
    # Get the value
    value = config.get("custom.nested.key")
    
    # Should return the set value
    assert value == "nested-value"
    
    # The parent structure should have been created
    assert "nested" in config._config["custom"]


def test_get_all():
    """Test getting the entire configuration."""
    # Reset the singleton for this test
    CentralConfig._instance = None
    
    # Create a new instance
    config = CentralConfig()
    
    # Set a custom value
    config.set("custom.key", "custom-value")
    
    # Get all configuration
    all_config = config.get_all()
    
    # Should include default and custom values
    assert all_config["bot"]["parse_mode"] == "HTML"
    assert all_config["custom"]["key"] == "custom-value"
    
    # Should be a copy, not the original
    all_config["custom"]["key"] = "modified-value"
    assert config.get("custom.key") == "custom-value"