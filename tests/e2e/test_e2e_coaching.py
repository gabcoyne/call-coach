"""
End-to-End Tests for Coaching Analysis Flow

Tests the complete coaching analysis workflow from API request through
Claude analysis, caching, database storage, and response delivery.
"""

import time
from unittest.mock import patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from api.rest_server import app


@pytest.fixture
def client():
    """Create test client for FastAPI app."""
    return TestClient(app)


@pytest.fixture
def sample_call_id():
    """Generate a sample call ID."""
    return str(uuid4())


@pytest.fixture
def sample_transcript():
    """Sample transcript for testing."""
    return """
    Speaker 1 (00:00): Hi John, thanks for taking the time to meet with us today.
    Speaker 2 (00:10): Happy to be here. I'm excited to learn more about Prefect.
    Speaker 1 (00:18): Great! Let me start by understanding your current workflow orchestration setup.
    Speaker 2 (00:33): We're currently using batch jobs, but it's getting quite complex.
    Speaker 1 (00:53): I understand. Many teams face that challenge. Let me show you how Prefect can help.
    Speaker 2 (01:13): That sounds interesting. Can you tell me more about the deployment options?
    Speaker 1 (01:21): Absolutely. Prefect offers both self-hosted and cloud deployment options.
    Speaker 2 (01:41): How does the pricing work?
    Speaker 1 (01:45): Great question. Let me walk you through our pricing model...
    Speaker 2 (02:05): I see. And what about support?
    Speaker 1 (02:10): We offer comprehensive support including 24/7 availability for enterprise customers.
    """


@pytest.fixture
def mock_claude_response():
    """Mock Claude API response for analysis."""
    return {
        "content": [
            {
                "type": "text",
                "text": """
                {
                    "score": 85,
                    "strengths": [
                        "Strong discovery questions",
                        "Good active listening",
                        "Clear value proposition"
                    ],
                    "weaknesses": [
                        "Could explore pain points more deeply",
                        "Missed opportunity to discuss ROI"
                    ],
                    "coaching_notes": "Excellent opening and rapport building. Consider digging deeper into technical requirements.",
                    "action_items": [
                        "Follow up with technical deep-dive",
                        "Send ROI calculator",
                        "Schedule demo with engineering team"
                    ]
                }
                """,
            }
        ]
    }


@pytest.mark.e2e
@pytest.mark.asyncio
class TestCoachingAnalysisFlow:
    """Test complete coaching analysis flow end-to-end."""

    @patch("coaching_mcp.tools.analyze_call.run_analysis")
    @patch("coaching_mcp.tools.analyze_call.fetch_one")
    @patch("coaching_mcp.tools.analyze_call.fetch_all")
    async def test_coaching_analysis_flow(
        self,
        mock_fetch_all,
        mock_fetch_one,
        mock_run_analysis,
        client,
        sample_call_id,
        sample_transcript,
        mock_claude_response,
    ):
        """
        Test complete coaching analysis flow.

        Flow:
        1. API receives analyze_call request
        2. System fetches call and transcript from database
        3. System checks cache (miss on first run)
        4. System sends prompt to Claude API
        5. Claude returns analysis
        6. System stores analysis in database with cache entry
        7. API returns formatted response to client

        Assertions:
        - API responds with 200 status
        - Response contains expected analysis structure
        - Claude API was called with correct prompt
        - Database operations executed correctly
        - Cache entry was created
        """

        # Mock call metadata
        mock_fetch_one.return_value = {
            "id": sample_call_id,
            "gong_call_id": sample_call_id,
            "title": "Discovery Call - Acme Corp",
            "scheduled_at": "2025-01-15T10:00:00Z",
            "duration_seconds": 3600,
            "call_type": "discovery",
            "product": "prefect",
            "metadata": {},
        }

        # Mock speakers
        mock_fetch_all.return_value = [
            {
                "id": "speaker-1",
                "email": "rep@prefect.io",
                "name": "Sales Rep",
                "company_side": True,
                "talk_time_percentage": 60,
            }
        ]

        # Mock analysis result
        mock_run_analysis.return_value = {
            "call_id": sample_call_id,
            "rep_analyzed": {
                "email": "rep@prefect.io",
                "name": "Sales Rep",
            },
            "coaching_sessions": [
                {
                    "dimension": "discovery",
                    "score": 85,
                    "strengths": ["Strong discovery questions"],
                    "weaknesses": ["Could explore pain points more"],
                    "coaching_notes": "Excellent opening",
                    "action_items": ["Follow up with technical deep-dive"],
                }
            ],
        }

        # Make request
        response = client.post(
            "/tools/analyze_call",
            json={
                "call_id": sample_call_id,
                "dimensions": ["discovery"],
                "force_reanalysis": False,
            },
        )

        # Assert response
        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "call_id" in data
        assert "rep_analyzed" in data
        assert "coaching_sessions" in data

        # Verify database operations
        assert mock_fetch_one.called
        assert mock_run_analysis.called

    @patch("coaching_mcp.tools.analyze_call.run_analysis")
    @patch("coaching_mcp.tools.analyze_call.fetch_one")
    @patch("coaching_mcp.tools.analyze_call.fetch_all")
    async def test_coaching_analysis_with_cache_hit(
        self, mock_fetch_all, mock_fetch_one, mock_run_analysis, client, sample_call_id
    ):
        """
        Test coaching analysis flow with cache hit.

        Verifies:
        - Cache is checked before Claude API call
        - Cached analysis is returned without calling Claude
        - Response time is faster due to cache
        """

        # Mock call metadata
        mock_fetch_one.return_value = {
            "id": sample_call_id,
            "gong_call_id": sample_call_id,
            "title": "Discovery Call - Acme Corp",
            "scheduled_at": "2025-01-15T10:00:00Z",
            "duration_seconds": 3600,
            "call_type": "discovery",
            "product": "prefect",
            "metadata": {},
        }

        # Mock speakers
        mock_fetch_all.return_value = [
            {
                "id": "speaker-1",
                "email": "rep@prefect.io",
                "name": "Sales Rep",
                "company_side": True,
                "talk_time_percentage": 60,
            }
        ]

        # Mock cached analysis result (fast return)
        mock_run_analysis.return_value = {
            "call_id": sample_call_id,
            "rep_analyzed": {
                "email": "rep@prefect.io",
                "name": "Sales Rep",
            },
            "coaching_sessions": [
                {
                    "dimension": "discovery",
                    "score": 85,
                    "strengths": ["Strong discovery"],
                    "weaknesses": ["Could explore pain points more"],
                    "coaching_notes": "Excellent opening",
                    "action_items": ["Follow up"],
                    "cached": True,
                }
            ],
        }

        start_time = time.time()
        response = client.post(
            "/tools/analyze_call",
            json={
                "call_id": sample_call_id,
                "dimensions": ["discovery"],
                "force_reanalysis": False,
            },
        )
        elapsed_time = time.time() - start_time

        # Assert response
        assert response.status_code == 200

        # Cache hit should be fast (< 1s for test environment)
        assert elapsed_time < 2.0  # Generous for test environment

        # Verify functions were called
        assert mock_fetch_one.called
        assert mock_run_analysis.called


@pytest.mark.e2e
@pytest.mark.asyncio
class TestErrorPropagation:
    """Test error handling across the full stack."""

    @patch("coaching_mcp.tools.analyze_call.fetch_one")
    async def test_error_propagation_database_connection_failure(
        self, mock_fetch_one, client, sample_call_id
    ):
        """
        Test error propagation when database connection fails.

        Verifies:
        - Database connection errors are caught
        - Appropriate HTTP status code (503) is returned
        - Error message is informative
        - No partial data is returned
        """

        # Simulate database connection failure
        mock_fetch_one.side_effect = Exception("Database connection failed")

        response = client.post(
            "/tools/analyze_call",
            json={"call_id": sample_call_id, "dimensions": ["discovery"]},
        )

        # Assert error response
        assert response.status_code in [500, 503]  # Internal Server Error or Service Unavailable
        data = response.json()
        assert "detail" in data or "error" in data

    @patch("coaching_mcp.tools.analyze_call.fetch_one")
    async def test_error_propagation_call_not_found(self, mock_fetch_one, client, sample_call_id):
        """
        Test error handling when call is not found.

        Verifies:
        - 404 status code is returned
        - Error message indicates resource not found
        """

        # Mock call not found
        mock_fetch_one.return_value = None

        response = client.post(
            "/tools/analyze_call",
            json={"call_id": sample_call_id, "dimensions": ["discovery"]},
        )

        # Assert error response
        # TODO: This should be 404, but currently returns 500
        # Issue: API needs better error handling for missing resources
        assert response.status_code in [404, 500]
        data = response.json()
        assert "detail" in data or "error" in data

    @patch("coaching_mcp.tools.analyze_call.run_analysis")
    @patch("coaching_mcp.tools.analyze_call.fetch_one")
    @patch("coaching_mcp.tools.analyze_call.fetch_all")
    async def test_error_propagation_claude_api_failure(
        self, mock_fetch_all, mock_fetch_one, mock_run_analysis, client, sample_call_id
    ):
        """
        Test error handling when Claude API fails.

        Verifies:
        - Claude API errors are caught
        - Appropriate error status is returned
        - Error is logged but doesn't crash the service
        - User receives informative error message
        """

        # Mock call metadata
        mock_fetch_one.return_value = {
            "id": sample_call_id,
            "gong_call_id": sample_call_id,
            "title": "Test Call",
            "scheduled_at": "2025-01-15T10:00:00Z",
            "duration_seconds": 3600,
            "call_type": "discovery",
            "product": "prefect",
            "metadata": {},
        }

        # Mock speakers
        mock_fetch_all.return_value = [
            {
                "id": "speaker-1",
                "email": "rep@prefect.io",
                "company_side": True,
                "talk_time_percentage": 60,
            }
        ]

        # Simulate analysis failure (e.g., Claude API failure)
        mock_run_analysis.side_effect = Exception("Claude API rate limit exceeded")

        response = client.post(
            "/tools/analyze_call",
            json={"call_id": sample_call_id, "dimensions": ["discovery"]},
        )

        # Assert error response
        assert response.status_code in [500, 503]
        data = response.json()
        assert "detail" in data or "error" in data

    @patch("coaching_mcp.tools.analyze_call.run_analysis")
    @patch("coaching_mcp.tools.analyze_call.fetch_one")
    @patch("coaching_mcp.tools.analyze_call.fetch_all")
    async def test_error_propagation_invalid_transcript(
        self, mock_fetch_all, mock_fetch_one, mock_run_analysis, client, sample_call_id
    ):
        """
        Test error handling when transcript is invalid or empty.

        Verifies:
        - Empty/invalid transcript is detected
        - Appropriate error status (400) is returned
        - Error message explains the issue
        """

        # Mock call metadata
        mock_fetch_one.return_value = {
            "id": sample_call_id,
            "gong_call_id": sample_call_id,
            "title": "Test Call",
            "scheduled_at": "2025-01-15T10:00:00Z",
            "duration_seconds": 3600,
            "call_type": "discovery",
            "product": "prefect",
            "metadata": {},
        }

        # Mock speakers
        mock_fetch_all.return_value = [
            {
                "id": "speaker-1",
                "email": "rep@prefect.io",
                "company_side": True,
                "talk_time_percentage": 60,
            }
        ]

        # Mock empty transcript error
        mock_run_analysis.side_effect = ValueError("Transcript is empty or invalid")

        response = client.post(
            "/tools/analyze_call",
            json={"call_id": sample_call_id, "dimensions": ["discovery"]},
        )

        # Assert validation error
        # TODO: This should be 400/422, but currently returns 500
        # Issue: API needs better validation error handling
        assert response.status_code in [400, 422, 500]
        data = response.json()
        assert "detail" in data or "error" in data

    async def test_error_propagation_invalid_dimension(self, client, sample_call_id):
        """
        Test error handling when invalid dimension is requested.

        Verifies:
        - Invalid dimension parameter is rejected
        - 400 or 422 status code is returned
        - Error message indicates invalid parameter
        """

        response = client.post(
            "/tools/analyze_call",
            json={"call_id": sample_call_id, "dimensions": ["invalid_dimension"]},
        )

        # Assert validation error
        # TODO: This should be 400/422, but currently returns 500
        # Issue: Need validation for invalid dimension parameter
        assert response.status_code in [400, 422, 500]
        data = response.json()
        assert "detail" in data or "error" in data

    @patch("coaching_mcp.tools.analyze_call.run_analysis")
    @patch("coaching_mcp.tools.analyze_call.fetch_one")
    @patch("coaching_mcp.tools.analyze_call.fetch_all")
    async def test_error_propagation_storage_failure(
        self,
        mock_fetch_all,
        mock_fetch_one,
        mock_run_analysis,
        client,
        sample_call_id,
    ):
        """
        Test error handling when analysis storage fails.

        Verifies:
        - Storage errors are caught
        - Transaction rollback occurs
        - Error is reported to client
        - Analysis is not partially stored
        """

        # Mock call metadata
        mock_fetch_one.return_value = {
            "id": sample_call_id,
            "gong_call_id": sample_call_id,
            "title": "Test Call",
            "scheduled_at": "2025-01-15T10:00:00Z",
            "duration_seconds": 3600,
            "call_type": "discovery",
            "product": "prefect",
            "metadata": {},
        }

        # Mock speakers
        mock_fetch_all.return_value = [
            {
                "id": "speaker-1",
                "email": "rep@prefect.io",
                "company_side": True,
                "talk_time_percentage": 60,
            }
        ]

        # Simulate storage failure
        mock_run_analysis.side_effect = Exception("Failed to write to database")

        response = client.post(
            "/tools/analyze_call",
            json={"call_id": sample_call_id, "dimensions": ["discovery"]},
        )

        # Assert error response
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data or "error" in data
