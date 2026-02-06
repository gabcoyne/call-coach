"""Common test fixtures and mock factories."""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

# Call and Transcript Fixtures


@pytest.fixture
def mock_call_data():
    """Mock call data structure."""
    return {
        "id": str(uuid4()),
        "title": "Discovery Call - Acme Corp",
        "scheduled": datetime.now().isoformat() + "Z",
        "started": (datetime.now() + timedelta(seconds=5)).isoformat() + "Z",
        "duration": 3600,
        "direction": "outbound",
        "system": "zoom",
        "scope": "external",
        "participants": [
            {
                "speaker_id": "speaker-1",
                "name": "Sarah Johnson",
                "email": "sarah@example.com",
                "title": "Sales Engineer",
                "is_internal": True,
                "talk_time_seconds": 1800,
            },
            {
                "speaker_id": "speaker-2",
                "name": "John Smith",
                "email": "john@acme.com",
                "title": "VP Engineering",
                "is_internal": False,
                "talk_time_seconds": 1500,
            },
        ],
    }


@pytest.fixture
def mock_transcript_data():
    """Mock transcript data."""
    return {
        "call_id": "call-123",
        "segments": [
            {
                "speaker_id": "speaker-1",
                "start_time": 0,
                "duration": 10,
                "text": "Hi John, thanks for taking the time to meet with us.",
                "sentiment": "positive",
            },
            {
                "speaker_id": "speaker-2",
                "start_time": 10,
                "duration": 8,
                "text": "Happy to be here. I am excited to learn more about Prefect.",
                "sentiment": "positive",
            },
            {
                "speaker_id": "speaker-1",
                "start_time": 18,
                "duration": 15,
                "text": "Great! Let me start by understanding your current workflow setup.",
                "sentiment": "neutral",
            },
            {
                "speaker_id": "speaker-2",
                "start_time": 33,
                "duration": 20,
                "text": "We are currently using batch jobs, but it is getting quite complex.",
                "sentiment": "neutral",
            },
            {
                "speaker_id": "speaker-1",
                "start_time": 53,
                "duration": 12,
                "text": "I understand. Have you considered using a workflow orchestration tool?",
                "sentiment": "neutral",
            },
        ],
    }


# Analysis Fixtures


@pytest.fixture
def mock_analysis_result():
    """Mock coaching analysis result."""
    return {
        "call_id": "call-123",
        "rep_analyzed": {
            "email": "sarah@example.com",
            "name": "Sarah Johnson",
        },
        "scores": {
            "overall": 85,
            "discovery": 80,
            "engagement": 85,
            "objection_handling": 85,
            "product_knowledge": 90,
        },
        "strengths": [
            "Excellent discovery questions",
            "Strong engagement and rapport",
            "Clear value proposition",
        ],
        "areas_for_improvement": [
            "Could summarize needs better",
            "Minor gap on competitive positioning",
        ],
        "coaching_notes": "Strong performance overall. Focus on summarizing customer needs before diving into solution.",
        "transcript_snippets": [
            {
                "text": "Let me start by understanding your current workflow setup.",
                "timestamp": 18,
                "speaker": "Sarah Johnson",
            },
        ],
        "action_items": [
            "Review best practices for needs summary",
            "Prepare competitive positioning talking points",
            "Schedule follow-up call for deep dive",
        ],
        "analyzed_at": datetime.now().isoformat() + "Z",
    }


@pytest.fixture
def mock_coaching_session():
    """Mock coaching session data."""
    return {
        "session_id": str(uuid4()),
        "call_id": "call-123",
        "dimension": "discovery",
        "score": 85,
        "rubric_version": "v1",
        "transcript_hash": "hash-abc123",
        "analysis": {
            "strengths": [],
            "improvements": [],
        },
        "created_at": datetime.now().isoformat() + "Z",
        "cached_at": datetime.now().isoformat() + "Z",
    }


# Rep Fixtures


@pytest.fixture
def mock_rep_data():
    """Mock rep/user data."""
    return {
        "id": str(uuid4()),
        "email": "sarah@example.com",
        "name": "Sarah Johnson",
        "team": "Enterprise Sales",
        "title": "Sales Engineer",
        "manager_email": "manager@example.com",
        "quota": 500000,
        "created_at": (datetime.now() - timedelta(days=365)).isoformat() + "Z",
    }


@pytest.fixture
def mock_rep_insights():
    """Mock rep insights data."""
    return {
        "rep_info": {
            "email": "sarah@example.com",
            "name": "Sarah Johnson",
            "calls_analyzed": 15,
            "average_score": 82,
            "trend": "improving",
        },
        "score_trends": [
            {
                "date": (datetime.now() - timedelta(days=7)).date().isoformat(),
                "average": 80,
            },
            {
                "date": (datetime.now() - timedelta(days=3)).date().isoformat(),
                "average": 82,
            },
        ],
        "skill_gaps": [
            {
                "area": "objection_handling",
                "current_score": 72,
                "target_score": 85,
                "priority": "high",
            },
        ],
        "coaching_plan": [
            {
                "focus": "Objection Handling",
                "duration": "2 weeks",
                "actions": ["Review common objections", "Practice responses"],
            },
        ],
    }


# Database Mock Fixtures


@pytest.fixture
def mock_db_fetch_one():
    """Create a mock fetch_one function."""
    mock = MagicMock()
    return mock


@pytest.fixture
def mock_db_fetch_all():
    """Create a mock fetch_all function."""
    mock = MagicMock()
    return mock


@pytest.fixture
def mock_anthropic_client():
    """Create a mock Anthropic client."""
    mock = MagicMock()
    mock.messages.create.return_value = MagicMock(
        content=[MagicMock(text='{"scores": {"discovery": 85}}')]
    )
    return mock


# API Request/Response Fixtures


@pytest.fixture
def analyze_call_request():
    """Mock analyze call API request."""
    return {
        "call_id": "call-123",
        "dimensions": ["discovery", "engagement"],
        "use_cache": True,
        "include_transcript_snippets": True,
    }


@pytest.fixture
def rep_insights_request():
    """Mock rep insights API request."""
    return {
        "rep_email": "sarah@example.com",
        "time_period": "last_30_days",
        "product_filter": "prefect",
    }


@pytest.fixture
def search_calls_request():
    """Mock search calls API request."""
    return {
        "rep_email": "sarah@example.com",
        "product": "prefect",
        "min_score": 75,
        "max_score": 95,
        "limit": 20,
    }


# Opportunity Fixtures


@pytest.fixture
def mock_opportunity_data():
    """Mock opportunity/deal data."""
    return {
        "id": str(uuid4()),
        "name": "Acme Corp - Enterprise Platform",
        "account_name": "Acme Corporation",
        "account_id": str(uuid4()),
        "owner_email": "sarah@example.com",
        "owner_name": "Sarah Johnson",
        "stage": "negotiation",
        "probability": 85,
        "amount": 250000,
        "close_date": (datetime.now() + timedelta(days=30)).date().isoformat(),
        "created_at": (datetime.now() - timedelta(days=60)).isoformat() + "Z",
    }


@pytest.fixture
def mock_opportunity_analysis():
    """Mock opportunity coaching analysis."""
    return {
        "opportunity": {
            "id": str(uuid4()),
            "name": "Acme Corp Deal",
            "account": "Acme Corp",
            "owner": "sarah@example.com",
            "stage": "negotiation",
        },
        "patterns": {
            "top_dimensions": ["discovery", "engagement"],
            "average_score": 82,
            "trend": "improving",
        },
        "themes": [
            "Strong discovery process across calls",
            "Effective relationship building",
            "Need for better objection handling",
        ],
        "objections": [
            {
                "type": "pricing",
                "occurrences": 3,
                "resolution_rate": 66,
            },
        ],
        "relationship": {
            "strength": "strong",
            "trust_level": "high",
            "engagement_level": "active",
        },
        "recommendations": [
            "Continue strong discovery approach",
            "Prepare competitive positioning for final negotiations",
            "Schedule executive sponsor call for close",
        ],
    }


# Search Results Fixtures


@pytest.fixture
def mock_search_results():
    """Mock call search results."""
    return [
        {
            "id": "call-1",
            "title": "Discovery Call - Acme Corp",
            "rep_email": "sarah@example.com",
            "product": "prefect",
            "call_type": "discovery",
            "overall_score": 85,
            "started": (datetime.now() - timedelta(days=5)).isoformat() + "Z",
            "duration": 3600,
        },
        {
            "id": "call-2",
            "title": "Demo - TechCorp",
            "rep_email": "john@example.com",
            "product": "horizon",
            "call_type": "demo",
            "overall_score": 72,
            "started": (datetime.now() - timedelta(days=3)).isoformat() + "Z",
            "duration": 2700,
        },
    ]


# Event/Webhook Fixtures


@pytest.fixture
def mock_gong_webhook():
    """Mock Gong webhook payload."""
    return {
        "event": "call.completed",
        "resource_type": "call",
        "resource_id": "call-123",
        "timestamp": datetime.now().isoformat() + "Z",
        "data": {
            "status": "completed",
            "processing_status": "ready",
            "call_duration": 3600,
        },
    }


# Async Fixtures


@pytest.fixture
async def mock_async_fetch():
    """Create a mock async fetch function."""
    mock = AsyncMock()
    return mock


@pytest.fixture
async def mock_async_anthropic():
    """Create a mock async Anthropic client."""
    mock = AsyncMock()
    mock.messages.create = AsyncMock(
        return_value=MagicMock(content=[MagicMock(text='{"scores": {"discovery": 85}}')])
    )
    return mock
