"""Tests for REST API endpoints."""
import pytest
import json
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from api.rest_server import app


@pytest.fixture
def client():
    """Create test client for FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_analyze_call_tool():
    """Mock analyze_call_tool."""
    with patch('api.rest_server.analyze_call_tool') as mock:
        yield mock


@pytest.fixture
def mock_rep_insights_tool():
    """Mock get_rep_insights_tool."""
    with patch('api.rest_server.get_rep_insights_tool') as mock:
        yield mock


@pytest.fixture
def mock_search_calls_tool():
    """Mock search_calls_tool."""
    with patch('api.rest_server.search_calls_tool') as mock:
        yield mock


@pytest.fixture
def sample_call_analysis():
    """Sample call analysis response."""
    return {
        'call_id': 'call-123',
        'rep_analyzed': {
            'email': 'test@example.com',
            'name': 'Test Rep',
        },
        'scores': {
            'overall': 85,
            'discovery': 80,
            'engagement': 85,
            'objection_handling': 85,
            'product_knowledge': 90,
        },
        'strengths': ['Strong discovery', 'Good engagement'],
        'areas_for_improvement': ['Better objection handling'],
        'coaching_notes': 'Great call overall',
        'action_items': ['Follow up next week'],
    }


class TestHealthCheck:
    """Tests for health check endpoint."""

    def test_health_check(self, client):
        """Test health check returns 200."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'ok'
        assert 'service' in data


class TestAnalyzeCallEndpoint:
    """Tests for analyze_call endpoint."""

    def test_analyze_call_success(self, client, mock_analyze_call_tool, sample_call_analysis):
        """Test successful call analysis."""
        mock_analyze_call_tool.return_value = sample_call_analysis

        response = client.post(
            '/tools/analyze_call',
            json={'call_id': 'call-123'}
        )

        assert response.status_code == 200
        data = response.json()
        assert data['call_id'] == 'call-123'
        assert 'scores' in data

    def test_analyze_call_with_dimensions(self, client, mock_analyze_call_tool, sample_call_analysis):
        """Test analysis with specific dimensions."""
        mock_analyze_call_tool.return_value = sample_call_analysis

        response = client.post(
            '/tools/analyze_call',
            json={
                'call_id': 'call-123',
                'dimensions': ['discovery', 'engagement']
            }
        )

        assert response.status_code == 200

    def test_analyze_call_missing_call_id(self, client):
        """Test validation of required call_id."""
        response = client.post(
            '/tools/analyze_call',
            json={}
        )

        assert response.status_code in [400, 422]

    def test_analyze_call_with_cache_control(self, client, mock_analyze_call_tool, sample_call_analysis):
        """Test cache control options."""
        mock_analyze_call_tool.return_value = sample_call_analysis

        response = client.post(
            '/tools/analyze_call',
            json={
                'call_id': 'call-123',
                'use_cache': False,
                'force_reanalysis': True
            }
        )

        assert response.status_code == 200

    def test_analyze_call_transcript_snippets(self, client, mock_analyze_call_tool):
        """Test including transcript snippets."""
        mock_analyze_call_tool.return_value = {
            'call_id': 'call-123',
            'snippets': [
                {'text': 'Sample quote', 'timestamp': 120}
            ]
        }

        response = client.post(
            '/tools/analyze_call',
            json={
                'call_id': 'call-123',
                'include_transcript_snippets': True
            }
        )

        assert response.status_code == 200


class TestRepInsightsEndpoint:
    """Tests for rep insights endpoint."""

    def test_get_rep_insights_success(self, client, mock_rep_insights_tool):
        """Test successful rep insights retrieval."""
        mock_rep_insights_tool.return_value = {
            'rep_info': {
                'email': 'sarah@example.com',
                'name': 'Sarah Johnson',
                'calls_analyzed': 15,
            },
            'score_trends': [],
            'skill_gaps': [],
            'coaching_plan': [],
        }

        response = client.post(
            '/tools/rep_insights',
            json={'rep_email': 'sarah@example.com'}
        )

        assert response.status_code == 200

    def test_get_rep_insights_with_time_period(self, client, mock_rep_insights_tool):
        """Test rep insights with specific time period."""
        mock_rep_insights_tool.return_value = {}

        response = client.post(
            '/tools/rep_insights',
            json={
                'rep_email': 'sarah@example.com',
                'time_period': 'last_quarter'
            }
        )

        assert response.status_code == 200

    def test_get_rep_insights_with_product_filter(self, client, mock_rep_insights_tool):
        """Test rep insights with product filter."""
        mock_rep_insights_tool.return_value = {}

        response = client.post(
            '/tools/rep_insights',
            json={
                'rep_email': 'sarah@example.com',
                'product_filter': 'prefect'
            }
        )

        assert response.status_code == 200

    def test_get_rep_insights_missing_email(self, client):
        """Test validation of required email."""
        response = client.post(
            '/tools/rep_insights',
            json={}
        )

        assert response.status_code in [400, 422]


class TestSearchCallsEndpoint:
    """Tests for search calls endpoint."""

    def test_search_calls_no_filters(self, client, mock_search_calls_tool):
        """Test searching without filters."""
        mock_search_calls_tool.return_value = [
            {
                'id': 'call-1',
                'title': 'Discovery Call',
                'overall_score': 85,
            }
        ]

        response = client.post('/tools/search_calls', json={})

        assert response.status_code == 200

    def test_search_calls_with_filters(self, client, mock_search_calls_tool):
        """Test searching with multiple filters."""
        mock_search_calls_tool.return_value = []

        response = client.post(
            '/tools/search_calls',
            json={
                'rep_email': 'sarah@example.com',
                'product': 'prefect',
                'min_score': 75,
                'max_score': 95
            }
        )

        assert response.status_code == 200

    def test_search_calls_by_date_range(self, client, mock_search_calls_tool):
        """Test filtering by date range."""
        mock_search_calls_tool.return_value = []

        response = client.post(
            '/tools/search_calls',
            json={
                'date_range': {
                    'start': '2025-01-01',
                    'end': '2025-01-31'
                }
            }
        )

        assert response.status_code == 200

    def test_search_calls_by_objection(self, client, mock_search_calls_tool):
        """Test filtering by objection type."""
        mock_search_calls_tool.return_value = []

        response = client.post(
            '/tools/search_calls',
            json={'has_objection_type': 'pricing'}
        )

        assert response.status_code == 200

    def test_search_calls_limit(self, client, mock_search_calls_tool):
        """Test result limit."""
        mock_search_calls_tool.return_value = []

        response = client.post(
            '/tools/search_calls',
            json={'limit': 10}
        )

        assert response.status_code == 200


class TestAnalyzeOpportunityEndpoint:
    """Tests for analyze opportunity endpoint."""

    def test_analyze_opportunity_success(self, client):
        """Test successful opportunity analysis."""
        with patch('api.rest_server.queries.get_opportunity') as mock_get:
            mock_get.return_value = {
                'id': 'opp-123',
                'name': 'Acme Corp Deal',
                'account_name': 'Acme Corp',
                'owner_email': 'rep@example.com',
                'stage': 'negotiation',
            }

            with patch('api.rest_server.analyze_opportunity_patterns') as mock_patterns:
                mock_patterns.return_value = {}

                with patch('api.rest_server.identify_recurring_themes') as mock_themes:
                    mock_themes.return_value = {}

                    with patch('api.rest_server.analyze_objection_progression') as mock_obj:
                        mock_obj.return_value = {}

                        with patch('api.rest_server.assess_relationship_strength') as mock_rel:
                            mock_rel.return_value = {}

                            with patch('api.rest_server.generate_coaching_recommendations') as mock_rec:
                                mock_rec.return_value = {}

                                response = client.post(
                                    '/tools/analyze_opportunity',
                                    json={'opportunity_id': 'opp-123'}
                                )

                                assert response.status_code == 200


class TestErrorHandling:
    """Tests for error handling."""

    def test_analyze_call_api_error(self, client, mock_analyze_call_tool):
        """Test handling of API errors."""
        mock_analyze_call_tool.side_effect = Exception('API Error')

        response = client.post(
            '/tools/analyze_call',
            json={'call_id': 'call-123'}
        )

        assert response.status_code >= 400

    def test_invalid_json(self, client):
        """Test handling of invalid JSON."""
        response = client.post(
            '/tools/analyze_call',
            data='invalid json',
            headers={'Content-Type': 'application/json'}
        )

        assert response.status_code >= 400
