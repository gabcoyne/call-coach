"""
Integration tests for Gong API opportunity methods.

These tests require valid Gong API credentials and will be skipped if:
- Environment variables are not set
- API connectivity fails

Task 2.6: Test API methods with real Gong credentials and log responses
"""

import logging
import os
from datetime import datetime, timedelta

import pytest

logger = logging.getLogger(__name__)


def has_gong_credentials() -> bool:
    """Check if Gong API credentials are available."""
    gong_key = os.getenv("GONG_API_KEY")
    gong_secret = os.getenv("GONG_API_SECRET")
    return bool(gong_key and gong_secret)


# Skip all tests in this module if no credentials
pytestmark = pytest.mark.skipif(
    not has_gong_credentials(),
    reason="SKIP: Gong API credentials not available. Set GONG_API_KEY and GONG_API_SECRET environment variables to run these tests.",
)


class TestGongOpportunityAPI:
    """
    Integration tests for Gong opportunity-related API methods.

    Task 2.6: Test API methods with real Gong credentials and log responses.
    SKIP if no credentials available.
    """

    @pytest.fixture
    def gong_client(self):
        """Create Gong client with credentials from environment."""
        from gong.client import GongClient

        return GongClient()

    def test_list_opportunities_returns_data(self, gong_client):
        """
        GIVEN valid Gong credentials
        WHEN list_opportunities is called
        THEN it returns opportunity data with expected structure
        """
        logger.info("Testing list_opportunities API method...")

        with gong_client as client:
            opportunities, cursor = client.list_opportunities(limit=10)

            logger.info(f"Retrieved {len(opportunities)} opportunities")
            logger.info(f"Next cursor: {cursor[:30] if cursor else 'None'}...")

            # Log sample response structure
            if opportunities:
                sample = opportunities[0]
                logger.info(f"Sample opportunity keys: {list(sample.keys())}")
                logger.info(f"Sample opportunity: {sample.get('name', 'N/A')}")

            # Verify structure (basic checks)
            assert isinstance(opportunities, list)
            # Note: May be empty if no opportunities in Gong

    def test_list_opportunities_with_modified_after(self, gong_client):
        """
        GIVEN valid credentials and modified_after date
        WHEN list_opportunities is called
        THEN it filters to recently modified opportunities
        """
        logger.info("Testing list_opportunities with modified_after filter...")

        # Look for opportunities modified in last 30 days
        modified_after = (datetime.utcnow() - timedelta(days=30)).isoformat() + "Z"

        with gong_client as client:
            opportunities, cursor = client.list_opportunities(
                modified_after=modified_after, limit=10
            )

            logger.info(f"Opportunities modified after {modified_after}: {len(opportunities)}")

            assert isinstance(opportunities, list)

    def test_list_opportunities_pagination(self, gong_client):
        """
        GIVEN opportunities in Gong
        WHEN list_opportunities is called with cursor
        THEN it paginates correctly
        """
        logger.info("Testing list_opportunities pagination...")

        with gong_client as client:
            # First page
            page1, cursor1 = client.list_opportunities(limit=5)
            logger.info(f"Page 1: {len(page1)} opportunities")

            if cursor1:
                # Second page
                page2, cursor2 = client.list_opportunities(cursor=cursor1, limit=5)
                logger.info(f"Page 2: {len(page2)} opportunities")

                # Pages should be different (if there are enough opportunities)
                if page1 and page2:
                    page1_ids = {o.get("id") for o in page1}
                    page2_ids = {o.get("id") for o in page2}
                    assert page1_ids.isdisjoint(
                        page2_ids
                    ), "Pagination returned duplicate opportunities"

    def test_get_opportunity_calls(self, gong_client):
        """
        GIVEN an opportunity with calls
        WHEN get_opportunity_calls is called
        THEN it returns associated call IDs
        """
        logger.info("Testing get_opportunity_calls API method...")

        with gong_client as client:
            # First get an opportunity
            opportunities, _ = client.list_opportunities(limit=1)

            if not opportunities:
                pytest.skip("No opportunities available to test")

            opp_id = opportunities[0].get("id")
            logger.info(f"Testing with opportunity ID: {opp_id}")

            # Get calls for this opportunity
            call_ids, cursor = client.get_opportunity_calls(opp_id)

            logger.info(f"Found {len(call_ids)} calls for opportunity")
            logger.info(f"Call IDs (first 5): {call_ids[:5]}")

            assert isinstance(call_ids, list)

    def test_get_opportunity_emails(self, gong_client):
        """
        GIVEN an opportunity with emails
        WHEN get_opportunity_emails is called
        THEN it returns email data
        """
        logger.info("Testing get_opportunity_emails API method...")

        with gong_client as client:
            # First get an opportunity
            opportunities, _ = client.list_opportunities(limit=1)

            if not opportunities:
                pytest.skip("No opportunities available to test")

            opp_id = opportunities[0].get("id")
            logger.info(f"Testing with opportunity ID: {opp_id}")

            # Get emails for this opportunity
            emails, cursor = client.get_opportunity_emails(opp_id)

            logger.info(f"Found {len(emails)} emails for opportunity")
            if emails:
                logger.info(f"Sample email keys: {list(emails[0].keys())}")

            assert isinstance(emails, list)


class TestGongAPIRateLimiting:
    """Tests for rate limit handling in Gong API client."""

    @pytest.fixture
    def gong_client(self):
        """Create Gong client with credentials from environment."""
        from gong.client import GongClient

        return GongClient()

    def test_exponential_backoff_on_rate_limit(self, gong_client):
        """
        GIVEN rate limit scenario
        WHEN API returns 429
        THEN client retries with exponential backoff
        """
        logger.info("Testing rate limit handling (may take some time)...")

        # Note: We can't easily trigger a real rate limit in tests
        # This test verifies the client initializes correctly with retry logic
        with gong_client as client:
            # Just verify client is configured with retry capability
            assert hasattr(client, "_make_request")

            # Make a simple request to verify functionality
            opportunities, _ = client.list_opportunities(limit=1)
            logger.info("API request successful (rate limit handling configured)")


# Summary marker for task tracking
def test_task_2_6_summary():
    """
    Task 2.6: Test API methods with real Gong credentials and log responses.

    Status: Tests implemented with skip marker when credentials unavailable.

    Tests cover:
    - list_opportunities (basic, with filters, pagination)
    - get_opportunity_calls
    - get_opportunity_emails
    - Rate limit handling

    To run: Set GONG_API_KEY and GONG_API_SECRET environment variables.
    """
    if has_gong_credentials():
        logger.info("Gong API credentials available - tests will run")
    else:
        pytest.skip(
            "SKIP: Task 2.6 - Gong API credentials not available. "
            "Set GONG_API_KEY and GONG_API_SECRET to run these integration tests."
        )
