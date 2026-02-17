"""
Unit tests for opportunity-related database queries.

Tests cover:
- upsert_opportunity
- upsert_email
- link_call_to_opportunity
- get_opportunity
- get_opportunity_timeline
- search_opportunities
- get/update sync_status
- opportunity_analysis_cache functions
"""

import json
from datetime import datetime
from typing import Any
from unittest.mock import patch
from uuid import uuid4

import pytest


class TestOpportunityQueries:
    """Tests for opportunity database queries."""

    @pytest.fixture
    def sample_opportunity_data(self) -> dict[str, Any]:
        """Sample opportunity data for testing."""
        return {
            "gong_opportunity_id": "gong-opp-123",
            "name": "Acme Corp Enterprise Deal",
            "account_name": "Acme Corporation",
            "owner_email": "sarah@prefect.io",
            "stage": "Negotiation",
            "close_date": "2024-03-15",
            "amount": 150000.0,
            "health_score": 75,
            "metadata": json.dumps({"source": "inbound", "product": "cloud"}),
        }

    @pytest.fixture
    def sample_email_data(self) -> dict[str, Any]:
        """Sample email data for testing."""
        return {
            "gong_email_id": "gong-email-456",
            "opportunity_id": str(uuid4()),
            "subject": "Follow-up on Prefect Demo",
            "sender_email": "sarah@prefect.io",
            "recipients": ["john@acme.com", "jane@acme.com"],
            "sent_at": "2024-02-10T14:30:00Z",
            "body_snippet": "Thank you for joining our demo today. As discussed...",
            "metadata": json.dumps({"thread_id": "thread-123"}),
        }

    @patch("db.queries.execute_query")
    @patch("db.queries.fetch_one")
    def test_upsert_opportunity_creates_new_record(
        self, mock_fetch_one, mock_execute, sample_opportunity_data
    ):
        """
        GIVEN new opportunity data
        WHEN upsert_opportunity is called
        THEN it inserts the record and returns the ID
        """
        from db.queries import upsert_opportunity

        expected_id = str(uuid4())
        mock_fetch_one.return_value = {"id": expected_id}

        result = upsert_opportunity(sample_opportunity_data)

        assert result == expected_id
        mock_execute.assert_called_once()
        # Verify the SQL contains upsert logic
        call_args = mock_execute.call_args[0][0]
        assert "INSERT INTO opportunities" in call_args
        assert "ON CONFLICT (gong_opportunity_id) DO UPDATE" in call_args

    @patch("db.queries.execute_query")
    @patch("db.queries.fetch_one")
    def test_upsert_opportunity_updates_existing(
        self, mock_fetch_one, mock_execute, sample_opportunity_data
    ):
        """
        GIVEN opportunity data with existing gong_opportunity_id
        WHEN upsert_opportunity is called
        THEN it updates the existing record
        """
        from db.queries import upsert_opportunity

        existing_id = str(uuid4())
        mock_fetch_one.return_value = {"id": existing_id}

        # Call twice with same gong_opportunity_id
        result1 = upsert_opportunity(sample_opportunity_data)
        result2 = upsert_opportunity(sample_opportunity_data)

        assert result1 == existing_id
        assert result2 == existing_id

    @patch("db.queries.execute_query")
    @patch("db.queries.fetch_one")
    def test_upsert_email_creates_record(self, mock_fetch_one, mock_execute, sample_email_data):
        """
        GIVEN new email data
        WHEN upsert_email is called
        THEN it inserts the email record
        """
        from db.queries import upsert_email

        expected_id = str(uuid4())
        mock_fetch_one.return_value = {"id": expected_id}

        result = upsert_email(sample_email_data)

        assert result == expected_id
        mock_execute.assert_called_once()
        call_args = mock_execute.call_args[0][0]
        assert "INSERT INTO emails" in call_args
        assert "ON CONFLICT (gong_email_id) DO UPDATE" in call_args

    @patch("db.queries.execute_query")
    def test_link_call_to_opportunity(self, mock_execute):
        """
        GIVEN call_id and opportunity_id
        WHEN link_call_to_opportunity is called
        THEN it creates junction record
        """
        from db.queries import link_call_to_opportunity

        call_id = str(uuid4())
        opp_id = str(uuid4())

        link_call_to_opportunity(call_id, opp_id)

        mock_execute.assert_called_once()
        call_args = mock_execute.call_args[0][0]
        assert "INSERT INTO call_opportunities" in call_args
        assert "ON CONFLICT" in call_args  # Should handle duplicates

    @patch("db.queries.fetch_one")
    def test_get_opportunity_returns_counts(self, mock_fetch_one):
        """
        GIVEN an opportunity ID
        WHEN get_opportunity is called
        THEN it returns opportunity with call_count and email_count
        """
        from db.queries import get_opportunity

        opp_id = str(uuid4())
        mock_fetch_one.return_value = {
            "id": opp_id,
            "name": "Test Opportunity",
            "call_count": 5,
            "email_count": 12,
        }

        result = get_opportunity(opp_id)

        assert result is not None
        assert result["call_count"] == 5
        assert result["email_count"] == 12

    @patch("db.queries.fetch_one")
    def test_get_opportunity_returns_none_for_missing(self, mock_fetch_one):
        """
        GIVEN a nonexistent opportunity ID
        WHEN get_opportunity is called
        THEN it returns None
        """
        from db.queries import get_opportunity

        mock_fetch_one.return_value = None

        result = get_opportunity("nonexistent-id")

        assert result is None

    @patch("db.queries.fetch_all")
    def test_get_opportunity_timeline_returns_chronological_items(self, mock_fetch_all):
        """
        GIVEN an opportunity with calls and emails
        WHEN get_opportunity_timeline is called
        THEN it returns items sorted by timestamp
        """
        from db.queries import get_opportunity_timeline

        opp_id = str(uuid4())
        mock_fetch_all.return_value = [
            {"item_type": "call", "id": str(uuid4()), "timestamp": "2024-02-10"},
            {"item_type": "email", "id": str(uuid4()), "timestamp": "2024-02-09"},
            {"item_type": "call", "id": str(uuid4()), "timestamp": "2024-02-08"},
        ]

        result = get_opportunity_timeline(opp_id, limit=10, offset=0)

        assert len(result) == 3
        assert result[0]["item_type"] == "call"
        assert result[1]["item_type"] == "email"

    @patch("db.queries.fetch_all")
    def test_get_opportunity_timeline_respects_pagination(self, mock_fetch_all):
        """
        GIVEN an opportunity with many items
        WHEN get_opportunity_timeline is called with pagination
        THEN it respects limit and offset
        """
        from db.queries import get_opportunity_timeline

        opp_id = str(uuid4())
        mock_fetch_all.return_value = [
            {"item_type": "call", "id": str(uuid4())},
        ]

        get_opportunity_timeline(opp_id, limit=5, offset=10)

        # Verify query includes pagination
        call_args = mock_fetch_all.call_args[0]
        query = call_args[0]
        assert "LIMIT" in query
        assert "OFFSET" in query

    @patch("db.queries.fetch_all")
    @patch("db.queries.fetch_one")
    def test_search_opportunities_with_owner_filter(self, mock_fetch_one, mock_fetch_all):
        """
        GIVEN owner email filter
        WHEN search_opportunities is called
        THEN it filters by owner
        """
        from db.queries import search_opportunities

        mock_fetch_one.return_value = {"total": 2}
        mock_fetch_all.return_value = [
            {"id": str(uuid4()), "owner_email": "sarah@prefect.io"},
            {"id": str(uuid4()), "owner_email": "sarah@prefect.io"},
        ]

        opps, total = search_opportunities(filters={"owner": "sarah@prefect.io"})

        assert len(opps) == 2
        assert total == 2

    @patch("db.queries.fetch_all")
    @patch("db.queries.fetch_one")
    def test_search_opportunities_with_stage_filter(self, mock_fetch_one, mock_fetch_all):
        """
        GIVEN stage filter (single or list)
        WHEN search_opportunities is called
        THEN it filters by stage
        """
        from db.queries import search_opportunities

        mock_fetch_one.return_value = {"total": 1}
        mock_fetch_all.return_value = [
            {"id": str(uuid4()), "stage": "Closed Won"},
        ]

        # Single stage
        opps, _ = search_opportunities(filters={"stage": "Closed Won"})
        assert len(opps) == 1

        # Multiple stages
        opps, _ = search_opportunities(filters={"stage": ["Closed Won", "Negotiation"]})
        assert len(opps) == 1

    @patch("db.queries.fetch_all")
    @patch("db.queries.fetch_one")
    def test_search_opportunities_with_health_score_range(self, mock_fetch_one, mock_fetch_all):
        """
        GIVEN health score min/max filters
        WHEN search_opportunities is called
        THEN it filters by range
        """
        from db.queries import search_opportunities

        mock_fetch_one.return_value = {"total": 3}
        mock_fetch_all.return_value = [
            {"id": str(uuid4()), "health_score": 50},
            {"id": str(uuid4()), "health_score": 60},
            {"id": str(uuid4()), "health_score": 70},
        ]

        opps, _ = search_opportunities(filters={"health_score_min": 40, "health_score_max": 80})

        assert len(opps) == 3

    @patch("db.queries.fetch_all")
    @patch("db.queries.fetch_one")
    def test_search_opportunities_with_text_search(self, mock_fetch_one, mock_fetch_all):
        """
        GIVEN search text
        WHEN search_opportunities is called
        THEN it searches name and account_name
        """
        from db.queries import search_opportunities

        mock_fetch_one.return_value = {"total": 1}
        mock_fetch_all.return_value = [
            {"id": str(uuid4()), "name": "Acme Deal", "account_name": "Acme Corp"},
        ]

        opps, _ = search_opportunities(filters={"search": "Acme"})

        assert len(opps) == 1
        # Verify query uses ILIKE for search
        call_args = mock_fetch_all.call_args[0]
        query = call_args[0]
        assert "ILIKE" in query

    @patch("db.queries.fetch_all")
    @patch("db.queries.fetch_one")
    def test_search_opportunities_sorting(self, mock_fetch_one, mock_fetch_all):
        """
        GIVEN sort field and direction
        WHEN search_opportunities is called
        THEN it sorts correctly
        """
        from db.queries import search_opportunities

        mock_fetch_one.return_value = {"total": 2}
        mock_fetch_all.return_value = []

        # Test valid sort field
        search_opportunities(sort="close_date", sort_dir="ASC")

        call_args = mock_fetch_all.call_args[0]
        query = call_args[0]
        assert "ORDER BY o.close_date ASC" in query

        # Test invalid sort field defaults to updated_at
        search_opportunities(sort="invalid_field", sort_dir="DESC")
        call_args = mock_fetch_all.call_args[0]
        query = call_args[0]
        assert "ORDER BY o.updated_at DESC" in query

    @patch("db.queries.fetch_one")
    def test_get_sync_status(self, mock_fetch_one):
        """
        GIVEN entity type
        WHEN get_sync_status is called
        THEN it returns sync status
        """
        from db.queries import get_sync_status

        mock_fetch_one.return_value = {
            "entity_type": "opportunities",
            "last_sync_timestamp": datetime.now(),
            "last_sync_status": "success",
        }

        result = get_sync_status("opportunities")

        assert result is not None
        assert result["entity_type"] == "opportunities"
        assert result["last_sync_status"] == "success"

    @patch("db.queries.execute_query")
    def test_update_sync_status(self, mock_execute):
        """
        GIVEN sync completion data
        WHEN update_sync_status is called
        THEN it upserts the status
        """
        from db.queries import update_sync_status

        update_sync_status(
            entity_type="opportunities",
            status="success",
            items_synced=50,
            errors_count=2,
            error_details={"failed_ids": ["id1", "id2"]},
        )

        mock_execute.assert_called_once()
        call_args = mock_execute.call_args[0]
        query = call_args[0]
        assert "INSERT INTO sync_status" in query
        assert "ON CONFLICT (entity_type) DO UPDATE" in query


class TestOpportunityAnalysisCache:
    """Tests for opportunity analysis cache functions."""

    @patch("db.queries.fetch_one")
    def test_get_opportunity_analysis_cache_hit(self, mock_fetch_one):
        """
        GIVEN a cached analysis
        WHEN get_opportunity_analysis_cache is called
        THEN it returns the cached result
        """
        from db.queries import get_opportunity_analysis_cache

        cache_key = "abc123"
        mock_fetch_one.return_value = {
            "cache_key": cache_key,
            "analysis_result": {"patterns": "test"},
            "cached_at": datetime.now(),
        }

        result = get_opportunity_analysis_cache(cache_key)

        assert result is not None
        assert result["cache_key"] == cache_key

    @patch("db.queries.fetch_one")
    def test_get_opportunity_analysis_cache_miss(self, mock_fetch_one):
        """
        GIVEN no cached analysis
        WHEN get_opportunity_analysis_cache is called
        THEN it returns None
        """
        from db.queries import get_opportunity_analysis_cache

        mock_fetch_one.return_value = None

        result = get_opportunity_analysis_cache("nonexistent")

        assert result is None

    @patch("db.queries.execute_query")
    def test_set_opportunity_analysis_cache(self, mock_execute):
        """
        GIVEN analysis result
        WHEN set_opportunity_analysis_cache is called
        THEN it stores the result
        """
        from db.queries import set_opportunity_analysis_cache

        set_opportunity_analysis_cache(
            cache_key="abc123",
            opportunity_id=str(uuid4()),
            analysis_type="patterns",
            analysis_result={"test": "data"},
        )

        mock_execute.assert_called_once()
        call_args = mock_execute.call_args[0]
        query = call_args[0]
        assert "INSERT INTO opportunity_analysis_cache" in query
        assert "ON CONFLICT (cache_key) DO UPDATE" in query

    @patch("db.queries.execute_query")
    def test_invalidate_opportunity_cache(self, mock_execute):
        """
        GIVEN opportunity ID
        WHEN invalidate_opportunity_cache is called
        THEN it deletes all cached analyses
        """
        from db.queries import invalidate_opportunity_cache

        opp_id = str(uuid4())
        invalidate_opportunity_cache(opp_id)

        mock_execute.assert_called_once()
        call_args = mock_execute.call_args[0]
        query = call_args[0]
        assert "DELETE FROM opportunity_analysis_cache" in query
        assert "opportunity_id" in query
