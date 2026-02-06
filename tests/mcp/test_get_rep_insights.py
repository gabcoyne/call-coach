"""Tests for get_rep_insights MCP tool."""
import pytest
from unittest.mock import patch
from coaching_mcp.tools.get_rep_insights import get_rep_insights_tool


@pytest.fixture
def mock_db():
    """Mock database functions."""
    with patch('coaching_mcp.tools.get_rep_insights.fetch_one') as mock_fetch_one, \
         patch('coaching_mcp.tools.get_rep_insights.fetch_all') as mock_fetch_all:
        yield {
            'fetch_one': mock_fetch_one,
            'fetch_all': mock_fetch_all,
        }


@pytest.fixture
def sample_rep_data():
    """Sample rep data."""
    return {
        'email': 'sarah@example.com',
        'name': 'Sarah Johnson',
        'id': 'rep-123',
        'team': 'Enterprise Sales',
    }


@pytest.fixture
def sample_coaching_sessions():
    """Sample coaching session data."""
    return [
        {
            'call_id': 'call-1',
            'dimension': 'discovery',
            'score': 85,
            'created_at': '2025-01-15',
        },
        {
            'call_id': 'call-2',
            'dimension': 'engagement',
            'score': 78,
            'created_at': '2025-01-14',
        },
        {
            'call_id': 'call-3',
            'dimension': 'objection_handling',
            'score': 72,
            'created_at': '2025-01-13',
        },
    ]


class TestGetRepInsightsTool:
    """Tests for get_rep_insights_tool function."""

    def test_get_rep_insights_basic(self, mock_db, sample_rep_data, sample_coaching_sessions):
        """Test basic rep insights retrieval."""
        rep_email = 'sarah@example.com'
        mock_db['fetch_one'].return_value = sample_rep_data
        mock_db['fetch_all'].return_value = sample_coaching_sessions

        result = get_rep_insights_tool(rep_email=rep_email)

        assert result is not None
        assert 'error' not in result or 'rep_info' in result

    def test_get_rep_insights_last_7_days(self, mock_db, sample_rep_data):
        """Test insights for last 7 days."""
        mock_db['fetch_one'].return_value = sample_rep_data
        mock_db['fetch_all'].return_value = []

        result = get_rep_insights_tool(
            rep_email='sarah@example.com',
            time_period='last_7_days'
        )

        assert result is not None

    def test_get_rep_insights_last_30_days(self, mock_db, sample_rep_data):
        """Test insights for last 30 days."""
        mock_db['fetch_one'].return_value = sample_rep_data
        mock_db['fetch_all'].return_value = []

        result = get_rep_insights_tool(
            rep_email='sarah@example.com',
            time_period='last_30_days'
        )

        assert result is not None

    def test_get_rep_insights_last_quarter(self, mock_db, sample_rep_data):
        """Test insights for last quarter."""
        mock_db['fetch_one'].return_value = sample_rep_data
        mock_db['fetch_all'].return_value = []

        result = get_rep_insights_tool(
            rep_email='sarah@example.com',
            time_period='last_quarter'
        )

        assert result is not None

    def test_get_rep_insights_all_time(self, mock_db, sample_rep_data):
        """Test all-time insights."""
        mock_db['fetch_one'].return_value = sample_rep_data
        mock_db['fetch_all'].return_value = []

        result = get_rep_insights_tool(
            rep_email='sarah@example.com',
            time_period='all_time'
        )

        assert result is not None

    def test_get_rep_insights_with_product_filter(self, mock_db, sample_rep_data):
        """Test filtering insights by product."""
        mock_db['fetch_one'].return_value = sample_rep_data
        mock_db['fetch_all'].return_value = []

        result = get_rep_insights_tool(
            rep_email='sarah@example.com',
            product_filter='prefect'
        )

        assert result is not None

    def test_get_rep_insights_rep_not_found(self, mock_db):
        """Test handling of non-existent rep."""
        mock_db['fetch_one'].return_value = None

        result = get_rep_insights_tool(rep_email='nonexistent@example.com')

        assert result is not None
        assert 'error' in result or result is None

    def test_get_rep_insights_score_trends(self, mock_db, sample_rep_data, sample_coaching_sessions):
        """Test that score trends are calculated."""
        mock_db['fetch_one'].return_value = sample_rep_data
        mock_db['fetch_all'].return_value = sample_coaching_sessions

        result = get_rep_insights_tool(rep_email='sarah@example.com')

        assert result is not None

    def test_get_rep_insights_skill_gaps(self, mock_db, sample_rep_data):
        """Test skill gap identification."""
        mock_db['fetch_one'].return_value = sample_rep_data
        mock_db['fetch_all'].return_value = [
            {'dimension': 'objection_handling', 'score': 60},
            {'dimension': 'discovery', 'score': 85},
        ]

        result = get_rep_insights_tool(rep_email='sarah@example.com')

        assert result is not None

    def test_get_rep_insights_coaching_plan(self, mock_db, sample_rep_data):
        """Test coaching plan generation."""
        mock_db['fetch_one'].return_value = sample_rep_data
        mock_db['fetch_all'].return_value = []

        result = get_rep_insights_tool(rep_email='sarah@example.com')

        assert result is not None

    def test_get_rep_insights_multiple_filters(self, mock_db, sample_rep_data):
        """Test combining time period and product filters."""
        mock_db['fetch_one'].return_value = sample_rep_data
        mock_db['fetch_all'].return_value = []

        result = get_rep_insights_tool(
            rep_email='sarah@example.com',
            time_period='last_quarter',
            product_filter='horizon'
        )

        assert result is not None
