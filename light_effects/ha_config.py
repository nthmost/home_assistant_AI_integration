"""
Home Assistant Configuration Loader
Loads credentials from .env file or environment variables
"""

import os
from pathlib import Path
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


def load_credentials(dotenv_path: Optional[Path] = None) -> Tuple[str, str]:
    """
    Load Home Assistant credentials from .env file or environment variables

    Args:
        dotenv_path: Optional path to .env file. If None, searches parent directories.

    Returns:
        Tuple of (url, token)

    Raises:
        ValueError: If credentials are not found
    """
    try:
        from dotenv import load_dotenv
    except ImportError:
        logger.warning("python-dotenv not installed, using environment variables only")
        load_dotenv = None

    # If dotenv is available, try to load .env file
    if load_dotenv:
        if dotenv_path is None:
            # Search for .env in current directory and parent directories
            current = Path.cwd()
            for parent in [current] + list(current.parents):
                env_file = parent / '.env'
                if env_file.exists():
                    dotenv_path = env_file
                    logger.debug(f"Found .env file at: {dotenv_path}")
                    break

        if dotenv_path and Path(dotenv_path).exists():
            load_dotenv(dotenv_path)
            logger.debug(f"Loaded credentials from {dotenv_path}")
        else:
            logger.debug("No .env file found, using environment variables")

    # Get credentials from environment
    url = os.getenv('HA_URL')
    token = os.getenv('HA_TOKEN')

    if not url or not token:
        error_msg = """
Home Assistant credentials not found!

Method 1 (recommended): Create a .env file in the project root:
    HA_URL=http://homeassistant.local:8123
    HA_TOKEN=your-long-lived-access-token

Method 2: Set environment variables:
    export HA_URL="http://homeassistant.local:8123"
    export HA_TOKEN="your-long-lived-access-token"

Get a long-lived token from Home Assistant:
    Profile (bottom left) -> Security -> Long-Lived Access Tokens
"""
        raise ValueError(error_msg)

    return url, token


def get_ha_url() -> str:
    """Get Home Assistant URL from environment"""
    url, _ = load_credentials()
    return url


def get_ha_token() -> str:
    """Get Home Assistant access token from environment"""
    _, token = load_credentials()
    return token
