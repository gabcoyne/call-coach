"""
Configuration management using Pydantic Settings.
Loads configuration from environment variables with validation.
"""

from pathlib import Path

from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def find_project_root() -> Path:
    """
    Find project root by walking up from this file looking for .git or pyproject.toml.
    Falls back to 3 levels up if markers not found.
    """
    current = Path(__file__).resolve()
    for parent in [current] + list(current.parents):
        if (parent / ".git").exists() or (parent / "pyproject.toml").exists():
            return parent
    # Fallback: 3 levels up from coaching_mcp/shared/config.py
    return current.parent.parent.parent


PROJECT_ROOT = find_project_root()
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE) if ENV_FILE.exists() else None,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Gong API
    gong_api_key: str = Field(..., description="Gong API access key")
    gong_api_secret: str = Field(..., description="Gong API secret key (JWT token)")
    gong_webhook_secret: str = Field(..., description="Secret for validating webhook signatures")
    gong_api_base_url: str = Field(
        default="https://us-79647.api.gong.io/v2",
        description="Base URL for Gong API (tenant-specific)",
    )

    # Claude API
    anthropic_api_key: str = Field(..., description="Anthropic API key for Claude")

    # Database (Neon Postgres)
    database_url: PostgresDsn = Field(..., description="PostgreSQL connection string")
    database_pool_min_size: int = Field(default=5, description="Min connection pool size")
    database_pool_max_size: int = Field(default=20, description="Max connection pool size")

    # Analysis settings
    enable_caching: bool = Field(default=True, description="Enable intelligent caching")
    cache_ttl_days: int = Field(default=90, description="Cache TTL in days")
    max_chunk_size_tokens: int = Field(default=80000, description="Max tokens per transcript chunk")
    chunk_overlap_percentage: int = Field(
        default=20, description="Overlap between chunks as percentage"
    )

    # Prefect/Horizon
    prefect_api_url: str | None = Field(default=None, description="Prefect Cloud API URL")
    prefect_api_key: str | None = Field(default=None, description="Prefect Cloud API key")

    # Notifications
    slack_webhook_url: str | None = Field(
        default=None, description="Slack webhook URL for notifications"
    )

    # Webhook endpoint (FastAPI)
    webhook_host: str = Field(default="0.0.0.0", description="Webhook server host")
    webhook_port: int = Field(default=8000, description="Webhook server port")

    # MCP Server
    mcp_server_host: str = Field(default="localhost", description="MCP server host")
    mcp_server_port: int = Field(default=3000, description="MCP server port")

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")

    @field_validator("database_url")
    def validate_database_url(cls, v: PostgresDsn) -> str:
        """Convert PostgresDsn to string and validate SSL requirement."""
        url_str = str(v)
        if "sslmode" not in url_str:
            # Neon requires SSL, add it if missing
            url_str += "?sslmode=require" if "?" not in url_str else "&sslmode=require"
        return url_str

    @field_validator("chunk_overlap_percentage")
    def validate_overlap_percentage(cls, v: int) -> int:
        """Ensure overlap percentage is reasonable."""
        if not 0 <= v <= 50:
            raise ValueError("chunk_overlap_percentage must be between 0 and 50")
        return v


# Global settings instance
settings = Settings()
