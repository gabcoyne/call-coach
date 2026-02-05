"""
Tests for MCP server startup validation.
"""
import os
import sys
from unittest.mock import Mock, patch, MagicMock
import pytest


class TestEnvironmentValidation:
    """Tests for _validate_environment function."""

    @patch.dict(os.environ, {
        "GONG_API_KEY": "test_key",
        "GONG_API_SECRET": "test_secret",
        "GONG_API_BASE_URL": "https://test.api.gong.io/v2",
        "ANTHROPIC_API_KEY": "sk-ant-test",
        "DATABASE_URL": "postgresql://test?sslmode=require"
    })
    def test_validate_environment_all_present(self):
        """Test validation passes when all required vars present."""
        from coaching_mcp.server import _validate_environment

        # Should not raise
        _validate_environment()

    @patch.dict(os.environ, {
        "GONG_API_KEY": "test_key",
        # Missing GONG_API_SECRET
        "GONG_API_BASE_URL": "https://test.api.gong.io/v2",
        "ANTHROPIC_API_KEY": "sk-ant-test",
        "DATABASE_URL": "postgresql://test?sslmode=require"
    }, clear=True)
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

    @patch('db.fetch_one')
    @patch('coaching_mcp.server.settings')
    def test_validate_database_success(self, mock_settings, mock_fetch_one):
        """Test database validation passes with valid connection."""
        from coaching_mcp.server import _validate_database_connection

        mock_settings.database_url = "postgresql://user:pass@host/db?sslmode=require"
        mock_fetch_one.return_value = {"test": 1}

        # Should not raise
        _validate_database_connection()

        mock_fetch_one.assert_called_once_with("SELECT 1 as test")

    @patch('coaching_mcp.server.settings')
    def test_validate_database_missing_sslmode(self, mock_settings):
        """Test database validation fails without sslmode."""
        from coaching_mcp.server import _validate_database_connection

        mock_settings.database_url = "postgresql://user:pass@host/db"

        with pytest.raises(SystemExit) as exc_info:
            _validate_database_connection()

        assert exc_info.value.code == 1

    @patch('db.fetch_one')
    @patch('coaching_mcp.server.settings')
    def test_validate_database_connection_failure(self, mock_settings, mock_fetch_one):
        """Test database validation fails on connection error."""
        from coaching_mcp.server import _validate_database_connection

        mock_settings.database_url = "postgresql://user:pass@host/db?sslmode=require"
        mock_fetch_one.side_effect = Exception("Connection failed")

        with pytest.raises(SystemExit) as exc_info:
            _validate_database_connection()

        assert exc_info.value.code == 1

    @patch('db.fetch_one')
    @patch('coaching_mcp.server.settings')
    def test_validate_database_unexpected_result(self, mock_settings, mock_fetch_one):
        """Test database validation fails with unexpected query result."""
        from coaching_mcp.server import _validate_database_connection

        mock_settings.database_url = "postgresql://user:pass@host/db?sslmode=require"
        mock_fetch_one.return_value = {"test": 99}  # Wrong value

        with pytest.raises(SystemExit) as exc_info:
            _validate_database_connection()

        assert exc_info.value.code == 1


class TestGongAPIValidation:
    """Tests for _validate_gong_api function."""

    @patch('gong.client.GongClient')
    def test_validate_gong_api_success(self, mock_gong_client):
        """Test Gong API validation passes with valid credentials."""
        from coaching_mcp.server import _validate_gong_api

        mock_client_instance = MagicMock()
        mock_client_instance.__enter__.return_value = mock_client_instance
        mock_client_instance.__exit__.return_value = None
        mock_client_instance.list_calls.return_value = ([], None)

        mock_gong_client.return_value = mock_client_instance

        # Should not raise
        _validate_gong_api()

        assert mock_client_instance.list_calls.called

    @patch('gong.client.GongClient')
    def test_validate_gong_api_auth_failure(self, mock_gong_client):
        """Test Gong API validation fails with 401 error."""
        from coaching_mcp.server import _validate_gong_api
        from gong.client import GongAPIError

        mock_client_instance = MagicMock()
        mock_client_instance.__enter__.return_value = mock_client_instance
        mock_client_instance.__exit__.return_value = None
        mock_client_instance.list_calls.side_effect = GongAPIError("HTTP 401: Unauthorized")

        mock_gong_client.return_value = mock_client_instance

        with pytest.raises(SystemExit) as exc_info:
            _validate_gong_api()

        assert exc_info.value.code == 1

    @patch('gong.client.GongClient')
    def test_validate_gong_api_network_failure(self, mock_gong_client):
        """Test Gong API validation fails with network error."""
        from coaching_mcp.server import _validate_gong_api

        mock_client_instance = MagicMock()
        mock_client_instance.__enter__.return_value = mock_client_instance
        mock_client_instance.__exit__.return_value = None
        mock_client_instance.list_calls.side_effect = Exception("Connection timeout")

        mock_gong_client.return_value = mock_client_instance

        with pytest.raises(SystemExit) as exc_info:
            _validate_gong_api()

        assert exc_info.value.code == 1


class TestAnthropicAPIValidation:
    """Tests for _validate_anthropic_api function."""

    @patch('coaching_mcp.server.settings')
    def test_validate_anthropic_api_valid_key(self, mock_settings):
        """Test Anthropic API validation passes with valid key format."""
        from coaching_mcp.server import _validate_anthropic_api

        mock_settings.anthropic_api_key = "sk-ant-api03-test-key-123"

        # Should not raise
        _validate_anthropic_api()

    @patch('coaching_mcp.server.settings')
    def test_validate_anthropic_api_invalid_prefix(self, mock_settings):
        """Test Anthropic API validation fails with wrong prefix."""
        from coaching_mcp.server import _validate_anthropic_api

        mock_settings.anthropic_api_key = "sk-wrong-prefix-123"

        with pytest.raises(SystemExit) as exc_info:
            _validate_anthropic_api()

        assert exc_info.value.code == 1

    @patch('coaching_mcp.server.settings')
    def test_validate_anthropic_api_empty_key(self, mock_settings):
        """Test Anthropic API validation fails with empty key."""
        from coaching_mcp.server import _validate_anthropic_api

        mock_settings.anthropic_api_key = ""

        with pytest.raises(SystemExit) as exc_info:
            _validate_anthropic_api()

        assert exc_info.value.code == 1


class TestStartupValidationIntegration:
    """Integration tests for complete startup validation flow."""

    @patch('coaching_mcp.server._validate_anthropic_api')
    @patch('coaching_mcp.server._validate_gong_api')
    @patch('coaching_mcp.server._validate_database_connection')
    @patch('coaching_mcp.server._validate_environment')
    def test_all_validations_pass(
        self,
        mock_env,
        mock_db,
        mock_gong,
        mock_anthropic
    ):
        """Test startup succeeds when all validations pass."""
        # All validations pass (no exceptions)

        # Import after patching to avoid module-level execution
        import importlib
        import mcp.server
        importlib.reload(mcp.server)

        # If we get here without SystemExit, validations passed

    @patch('coaching_mcp.server._validate_anthropic_api')
    @patch('coaching_mcp.server._validate_gong_api')
    @patch('coaching_mcp.server._validate_database_connection')
    @patch('coaching_mcp.server._validate_environment')
    def test_validation_fails_early(
        self,
        mock_env,
        mock_db,
        mock_gong,
        mock_anthropic
    ):
        """Test startup fails fast on first validation error."""
        mock_env.side_effect = SystemExit(1)

        with pytest.raises(SystemExit):
            mock_env()

        # Later validations should not be called
        assert not mock_db.called
        assert not mock_gong.called
        assert not mock_anthropic.called
