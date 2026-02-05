"""Pytest configuration and fixtures."""
import json
import sys
import pytest
from pathlib import Path

# Add project root to sys.path so imports resolve to our local modules first
# This ensures tests import from local mcp/ module instead of installed fastmcp package
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def sample_gong_call():
    """Sample Gong call metadata."""
    return {
        "id": "1234567890",
        "title": "Prefect Discovery Call - Acme Corp",
        "scheduled": "2025-01-15T10:00:00Z",
        "started": "2025-01-15T10:02:00Z",
        "duration": 3600,
        "direction": "outbound",
        "system": "zoom",
        "scope": "external",
        "participants": [
            {
                "speaker_id": "speaker_1",
                "name": "Sarah Johnson",
                "email": "sarah@prefect.io",
                "title": "Sales Engineer",
                "is_internal": True,
                "talk_time_seconds": 1800,
            },
            {
                "speaker_id": "speaker_2",
                "name": "John Smith",
                "email": "john@acme.com",
                "title": "Engineering Manager",
                "is_internal": False,
                "talk_time_seconds": 1500,
            },
        ],
    }


@pytest.fixture
def sample_transcript():
    """Sample transcript segments."""
    return {
        "call_id": "1234567890",
        "segments": [
            {
                "speaker_id": "speaker_1",
                "start_time": 0,
                "duration": 10,
                "text": "Hi John, thanks for taking the time to meet with us today.",
                "sentiment": "positive",
            },
            {
                "speaker_id": "speaker_2",
                "start_time": 10,
                "duration": 8,
                "text": "Happy to be here. I'm excited to learn more about Prefect.",
                "sentiment": "positive",
            },
            {
                "speaker_id": "speaker_1",
                "start_time": 18,
                "duration": 15,
                "text": "Great! Let me start by understanding your current workflow orchestration setup.",
                "sentiment": "neutral",
            },
        ],
    }


@pytest.fixture
def fixtures_dir():
    """Path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_webhook_payload():
    """Sample Gong webhook payload."""
    return {
        "event": "call.completed",
        "resource_type": "call",
        "resource_id": "1234567890",
        "call_id": "1234567890",
        "timestamp": "2025-01-15T14:30:00Z",
        "data": {
            "status": "completed",
            "processing_status": "ready",
        },
    }
