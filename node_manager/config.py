"""
Configuration management for Node Manager.
"""

import os


class Config:
    """Configuration class that reads from environment variables."""

    # Flask settings
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    DEBUG = os.environ.get("FLASK_DEBUG", "False").lower() == "true"

    # Database
    DATABASE_PATH = os.environ.get("DATABASE_PATH", "/oxidized_config/nodes.db")

    # Oxidized settings
    OXIDIZED_API_URL = os.environ.get("OXIDIZED_API_URL", "http://oxidized:8888")
    OXIDIZED_USER = os.environ.get("OXIDIZED_USER", "admin")
    OXIDIZED_PASSWORD = os.environ.get("OXIDIZED_PASSWORD", "admin")

    # Config file path (for Oxidized)
    CONFIG_FILE = os.environ.get("CONFIG_FILE", "/oxidized_config/nodes.csv")

    # Docker settings
    DOCKER_SOCKET = os.environ.get("DOCKER_SOCKET", "/var/run/docker.sock")
    OXIDIZED_CONTAINER_NAME = os.environ.get("OXIDIZED_CONTAINER_NAME", "oxidized")

    # Sync interval (seconds)
    DEFAULT_SYNC_INTERVAL = int(os.environ.get("OXIDIZED_SYNC_INTERVAL", "3600"))

    # Model file
    MODELS_FILE = os.environ.get("MODELS_FILE", "/oxidized_config/enabled_models.json")

    @classmethod
    def to_dict(cls):
        """Convert config to dictionary."""
        return {
            key: getattr(cls, key)
            for key in dir(cls)
            if not key.startswith("_") and not callable(getattr(cls, key))
        }


# Global config instance
config = Config
