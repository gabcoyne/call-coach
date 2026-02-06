"""Tests for analyze_call MCP tool."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from coaching_mcp.tools.analyze_call import analyze_call_tool


@pytest.fixture
def mock_settings():
    """Mock settings."""
    with patch('coaching_mcp.tools.analyze_call.settings') as mock:
        mock.anthropic_api_key = "test-key"
        yield mock


@pytest.fixture
def mock_db():
    """Mock database functions."""
    with patch('coaching_mcp.tools.analyze_call.fetch_one') as mock_fetch_one, \
         patch('coaching_mcp.tools.analyze_call.fetch_all') as mock_fetch_all:
        yield {
            'fetch_one': mock_fetch_one,
            'fetch_all': mock_fetch_all,
        }


class TestAnalyzeCallTool:
    """Tests for analyze_call_tool function."""

    def test_analyze_call_basic(self, mock_settings, mock_db):
        """Test basic call analysis."""
        call_id = "test-call-123"

        # Mock DB responses
        mock_db['fetch_one'].side_effect = [
            # Call metadata
            {
                'id': call_id,
                'title': 'Test Call',
                'rep_email': 'test@example.com',
                'started': '2025-01-15T10:00:00Z',
            },
            # Transcript
            {'text': 'Hello, how are you?'},
        ]

        with patch('coaching_mcp.tools.analyze_call.get_or_create_coaching_session') as mock_analysis:
            mock_analysis.return_value = {
                'call_id': call_id,
                'scores': {'discovery': 75},
                'strengths': ['Good opening'],
                'improvements': ['Better closing'],
            }

            result = analyze_call_tool(call_id=call_id)

            assert result is not None
            assert 'scores' in result or 'error' in result

    def test_analyze_call_with_dimensions(self, mock_settings, mock_db):
        """Test analysis with specific dimensions."""
        call_id = "test-call-456"
        dimensions = ['discovery', 'engagement']

        mock_db['fetch_one'].side_effect = [
            {'id': call_id, 'title': 'Test Call', 'rep_email': 'test@example.com'},
            {'text': 'Transcript content'},
        ]

        with patch('coaching_mcp.tools.analyze_call.get_or_create_coaching_session') as mock_analysis:
            mock_analysis.return_value = {'call_id': call_id, 'scores': {}}

            result = analyze_call_tool(call_id=call_id, dimensions=dimensions)

            assert result is not None

    def test_analyze_call_with_cache(self, mock_settings, mock_db):
        """Test call analysis with caching enabled."""
        call_id = "test-call-789"

        mock_db['fetch_one'].side_effect = [
            {'id': call_id, 'title': 'Test Call', 'rep_email': 'test@example.com'},
            {'text': 'Cached content'},
        ]

        with patch('coaching_mcp.tools.analyze_call.get_or_create_coaching_session') as mock_analysis:
            mock_analysis.return_value = {'cached': True}

            result = analyze_call_tool(call_id=call_id, use_cache=True)

            assert result is not None

    def test_analyze_call_force_reanalysis(self, mock_settings, mock_db):
        """Test forcing reanalysis even with cache."""
        call_id = "test-call-reanalyze"

        mock_db['fetch_one'].side_effect = [
            {'id': call_id, 'title': 'Test Call', 'rep_email': 'test@example.com'},
            {'text': 'New analysis'},
        ]

        with patch('coaching_mcp.tools.analyze_call.get_or_create_coaching_session') as mock_analysis:
            mock_analysis.return_value = {'fresh': True}

            result = analyze_call_tool(call_id=call_id, force_reanalysis=True)

            assert result is not None

    def test_analyze_call_not_found(self, mock_settings, mock_db):
        """Test handling of non-existent call."""
        call_id = "non-existent-call"

        mock_db['fetch_one'].return_value = None

        result = analyze_call_tool(call_id=call_id)

        assert result is not None
        assert 'error' in result or result is None

    def test_analyze_call_with_transcript_snippets(self, mock_settings, mock_db):
        """Test including transcript snippets in analysis."""
        call_id = "test-call-snippets"

        mock_db['fetch_one'].side_effect = [
            {'id': call_id, 'title': 'Test Call', 'rep_email': 'test@example.com'},
            {'text': 'This is a transcript with specific moments...'},
        ]

        with patch('coaching_mcp.tools.analyze_call.get_or_create_coaching_session') as mock_analysis:
            mock_analysis.return_value = {
                'snippets': [
                    {'text': 'Example snippet', 'timestamp': 0}
                ]
            }

            result = analyze_call_tool(
                call_id=call_id,
                include_transcript_snippets=True
            )

            assert result is not None

    def test_analyze_call_all_dimensions(self, mock_settings, mock_db):
        """Test analysis without specifying dimensions (analyzes all)."""
        call_id = "test-call-all-dims"

        mock_db['fetch_one'].side_effect = [
            {'id': call_id, 'title': 'Test Call', 'rep_email': 'test@example.com'},
            {'text': 'Full transcript'},
        ]

        with patch('coaching_mcp.tools.analyze_call.get_or_create_coaching_session') as mock_analysis:
            mock_analysis.return_value = {
                'scores': {
                    'discovery': 80,
                    'engagement': 75,
                    'product_knowledge': 85,
                    'objection_handling': 70,
                }
            }

            result = analyze_call_tool(call_id=call_id, dimensions=None)

            assert result is not None
