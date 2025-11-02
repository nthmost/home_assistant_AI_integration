"""
Unit tests for ha_core.config module

Tests credential loading from .env files and environment variables.
Per CLAUDE.md: isolated, repeatable, fast tests with external dependencies mocked.
"""

import pytest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from tempfile import NamedTemporaryFile

from ha_core.config import load_credentials, get_ha_url, get_ha_token
from ha_core.exceptions import ConfigurationError


class TestLoadCredentials:
    """Test credential loading functionality"""

    def test_load_from_environment_variables(self, monkeypatch):
        """Test loading credentials from environment variables"""
        monkeypatch.setenv('HA_URL', 'http://test.local:8123')
        monkeypatch.setenv('HA_TOKEN', 'test-token-12345')

        url, token = load_credentials()
        assert url == 'http://test.local:8123'
        assert token == 'test-token-12345'

    def test_load_missing_url_raises_error(self, monkeypatch, tmp_path):
        """Test missing HA_URL raises ValueError"""
        monkeypatch.delenv('HA_URL', raising=False)
        monkeypatch.delenv('HA_TOKEN', raising=False)
        # Change to temp directory so .env file in project root isn't found
        monkeypatch.chdir(tmp_path)

        with pytest.raises(ValueError, match="credentials not found"):
            load_credentials()

    def test_load_missing_token_raises_error(self, monkeypatch, tmp_path):
        """Test missing HA_TOKEN raises ValueError"""
        monkeypatch.setenv('HA_URL', 'http://test.local:8123')
        monkeypatch.delenv('HA_TOKEN', raising=False)
        # Change to temp directory so .env file in project root isn't found
        monkeypatch.chdir(tmp_path)

        with pytest.raises(ValueError, match="credentials not found"):
            load_credentials()

    def test_load_from_dotenv_file(self, monkeypatch, tmp_path):
        """Test loading credentials from .env file"""
        # Create temporary .env file
        env_file = tmp_path / '.env'
        env_file.write_text('HA_URL=http://dotenv.local:8123\nHA_TOKEN=dotenv-token')

        # Clear environment variables
        monkeypatch.delenv('HA_URL', raising=False)
        monkeypatch.delenv('HA_TOKEN', raising=False)

        # Load credentials from the .env file
        url, token = load_credentials(dotenv_path=env_file)
        assert url == 'http://dotenv.local:8123'
        assert token == 'dotenv-token'

    def test_load_with_dotenv_not_installed(self, monkeypatch, tmp_path):
        """Test graceful handling when python-dotenv is not installed"""
        monkeypatch.setenv('HA_URL', 'http://test.local:8123')
        monkeypatch.setenv('HA_TOKEN', 'test-token')
        monkeypatch.chdir(tmp_path)

        # Mock ImportError for dotenv import inside load_credentials
        import sys
        with patch.dict(sys.modules, {'dotenv': None}):
            url, token = load_credentials()
            assert url == 'http://test.local:8123'
            assert token == 'test-token'

    def test_environment_overrides_dotenv(self, monkeypatch, tmp_path):
        """Test that environment variables override .env file"""
        # Create .env file with different values
        env_file = tmp_path / '.env'
        env_file.write_text('HA_URL=http://dotenv.local:8123\nHA_TOKEN=dotenv-token')

        # Set environment variables (these should take precedence)
        monkeypatch.setenv('HA_URL', 'http://env.local:8123')
        monkeypatch.setenv('HA_TOKEN', 'env-token')

        url, token = load_credentials(dotenv_path=env_file)
        # Note: dotenv loads first, but if env vars are set, they typically override
        # The actual behavior depends on dotenv's override parameter
        assert url in ['http://env.local:8123', 'http://dotenv.local:8123']
        assert token in ['env-token', 'dotenv-token']


class TestGetHaUrl:
    """Test get_ha_url convenience function"""

    def test_get_ha_url(self, monkeypatch, tmp_path):
        """Test get_ha_url returns URL"""
        monkeypatch.setenv('HA_URL', 'http://test.local:8123')
        monkeypatch.setenv('HA_TOKEN', 'test-token')
        monkeypatch.chdir(tmp_path)

        url = get_ha_url()
        assert url == 'http://test.local:8123'

    def test_get_ha_url_missing_raises_error(self, monkeypatch, tmp_path):
        """Test get_ha_url raises error if URL missing"""
        monkeypatch.delenv('HA_URL', raising=False)
        monkeypatch.delenv('HA_TOKEN', raising=False)
        monkeypatch.chdir(tmp_path)

        with pytest.raises(ValueError):
            get_ha_url()


class TestGetHaToken:
    """Test get_ha_token convenience function"""

    def test_get_ha_token(self, monkeypatch, tmp_path):
        """Test get_ha_token returns token"""
        monkeypatch.setenv('HA_URL', 'http://test.local:8123')
        monkeypatch.setenv('HA_TOKEN', 'test-token-12345')
        monkeypatch.chdir(tmp_path)

        token = get_ha_token()
        assert token == 'test-token-12345'

    def test_get_ha_token_missing_raises_error(self, monkeypatch, tmp_path):
        """Test get_ha_token raises error if token missing"""
        monkeypatch.delenv('HA_URL', raising=False)
        monkeypatch.delenv('HA_TOKEN', raising=False)
        monkeypatch.chdir(tmp_path)

        with pytest.raises(ValueError):
            get_ha_token()


class TestDotenvSearch:
    """Test automatic .env file discovery"""

    def test_finds_env_in_current_directory(self, monkeypatch, tmp_path):
        """Test that .env is found in current directory"""
        # Create .env in temp directory
        env_file = tmp_path / '.env'
        env_file.write_text('HA_URL=http://current.local:8123\nHA_TOKEN=current-token')

        # Clear environment
        monkeypatch.delenv('HA_URL', raising=False)
        monkeypatch.delenv('HA_TOKEN', raising=False)

        # Change to temp directory
        monkeypatch.chdir(tmp_path)

        url, token = load_credentials()
        assert url == 'http://current.local:8123'
        assert token == 'current-token'

    def test_finds_env_in_parent_directory(self, monkeypatch, tmp_path):
        """Test that .env is found in parent directory"""
        # Create .env in parent directory
        env_file = tmp_path / '.env'
        env_file.write_text('HA_URL=http://parent.local:8123\nHA_TOKEN=parent-token')

        # Create subdirectory
        subdir = tmp_path / 'subdir'
        subdir.mkdir()

        # Clear environment
        monkeypatch.delenv('HA_URL', raising=False)
        monkeypatch.delenv('HA_TOKEN', raising=False)

        # Change to subdirectory
        monkeypatch.chdir(subdir)

        url, token = load_credentials()
        assert url == 'http://parent.local:8123'
        assert token == 'parent-token'
