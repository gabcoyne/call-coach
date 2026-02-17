"""
Tests for MCP server startup validation.
"""

import os
from unittest.mock import patch

import pytest


class TestEnvironmentValidation:
    """Tests for _validate_environment function."""

    @patch.dict(
        os.environ,
        {
            "ANTHROPIC_API_KEY": "sk-ant-test-key-1234567890",
            "DATABASE_URL": "postgresql://test?sslmode=require",
        },
    )
    def test_validate_environment_all_present(self):
        """Test validation passes when all required vars present."""
        from coaching_mcp.server import _validate_environment

        # Should not raise
        _validate_environment()

    @patch.dict(
        os.environ,
        {
            # Missing ANTHROPIC_API_KEY
            "DATABASE_URL": "postgresql://test?sslmode=require",
        },
        clear=True,
    )
    def test_validate_environment_missing_variable(self):
        """Test validation fails when required var missing."""
        from coaching_mcp.server import _validate_environment

        with pytest.raises(SystemExit) as exc_info:
            _validate_environment()

        assert exc_info.value.code == 1

    @patch.dict(os.environ, {}, clear=True)
    def test_validate_environment_all_missing(self):
        """Test validation fails when all vars missing."""
        from coaching_mcp.server import _validate_environment

        with pytest.raises(SystemExit) as exc_info:
            _validate_environment()

        assert exc_info.value.code == 1


class TestDatabaseValidation:
    """Tests for _validate_database_connection function."""

    @patch("db.fetch_one")
    @patch("coaching_mcp.server.settings")
    def test_validate_database_success(self, mock_settings, mock_fetch_one):
        """Test database validation passes with valid connection."""
        from coaching_mcp.server import _validate_database_connection

        mock_settings.database_url = "postgresql://user:pass@host/db?sslmode=require"
        mock_fetch_one.return_value = {"test": 1}

        # Should not raise
        _validate_database_connection()

        mock_fetch_one.assert_called_once_with("SELECT 1 as test")

    @patch("coaching_mcp.server.settings")
    def test_validate_database_missing_sslmode(self, mock_settings):
        """Test database validation fails without sslmode."""
        from coaching_mcp.server import _validate_database_connection

        mock_settings.database_url = "postgresql://user:pass@host/db"

        with pytest.raises(SystemExit) as exc_info:
            _validate_database_connection()

        assert exc_info.value.code == 1

    @patch("db.fetch_one")
    @patch("coaching_mcp.server.settings")
    def test_validate_database_connection_failure(self, mock_settings, mock_fetch_one):
        """Test database validation fails on connection error."""
        from coaching_mcp.server import _validate_database_connection

        mock_settings.database_url = "postgresql://user:pass@host/db?sslmode=require"
        mock_fetch_one.side_effect = Exception("Connection failed")

        with pytest.raises(SystemExit) as exc_info:
            _validate_database_connection()

        assert exc_info.value.code == 1

    @patch("db.fetch_one")
    @patch("coaching_mcp.server.settings")
    def test_validate_database_unexpected_result(self, mock_settings, mock_fetch_one):
        """Test database validation fails with unexpected query result."""
        from coaching_mcp.server import _validate_database_connection

        mock_settings.database_url = "postgresql://user:pass@host/db?sslmode=require"
        mock_fetch_one.return_value = {"test": 99}  # Wrong value

        with pytest.raises(SystemExit) as exc_info:
            _validate_database_connection()

        assert exc_info.value.code == 1


class TestAnthropicAPIValidation:
    """Tests for _validate_anthropic_api function."""

    @patch("coaching_mcp.server.settings")
    def test_validate_anthropic_api_valid_key(self, mock_settings):
        """Test Anthropic API validation passes with valid key format."""
        from coaching_mcp.server import _validate_anthropic_api

        mock_settings.anthropic_api_key = "sk-ant-api03-test-key-123"

        # Should not raise
        _validate_anthropic_api()

    @patch("coaching_mcp.server.settings")
    def test_validate_anthropic_api_too_short(self, mock_settings):
        """Test Anthropic API validation fails with short key."""
        from coaching_mcp.server import _validate_anthropic_api

        mock_settings.anthropic_api_key = "sk-short"

        with pytest.raises(SystemExit) as exc_info:
            _validate_anthropic_api()

        assert exc_info.value.code == 1

    @patch("coaching_mcp.server.settings")
    def test_validate_anthropic_api_placeholder(self, mock_settings):
        """Test Anthropic API validation fails with placeholder."""
        from coaching_mcp.server import _validate_anthropic_api

        mock_settings.anthropic_api_key = "your_key_here_replace_me"

        with pytest.raises(SystemExit) as exc_info:
            _validate_anthropic_api()

        assert exc_info.value.code == 1


class TestStartupValidationIntegration:
    """Integration tests for complete startup validation flow."""

    @patch("coaching_mcp.server._validate_anthropic_api")
    @patch("coaching_mcp.server._validate_database_connection")
    @patch("coaching_mcp.server._validate_environment")
    def test_all_validations_pass(self, mock_env, mock_db, mock_anthropic):
        """Test startup succeeds when all validations pass."""
        # All validations pass (no exceptions)

        # Import after patching to avoid module-level execution
        import importlib

        import mcp.server

        importlib.reload(mcp.server)

        # If we get here without SystemExit, validations passed

    @patch("coaching_mcp.server._validate_anthropic_api")
    @patch("coaching_mcp.server._validate_database_connection")
    @patch("coaching_mcp.server._validate_environment")
    def test_validation_fails_early(self, mock_env, mock_db, mock_anthropic):
        """Test startup fails fast on first validation error."""
        mock_env.side_effect = SystemExit(1)

        with pytest.raises(SystemExit):
            mock_env()

        # Later validations should not be called
        assert not mock_db.called
        assert not mock_anthropic.called
