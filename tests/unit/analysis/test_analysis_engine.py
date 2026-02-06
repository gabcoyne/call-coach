"""
TDD Unit Tests for Analysis Engine - Wave 2

These tests cover:
- 2.1: Prompt generation for each coaching dimension
- 2.2: Claude API call with mocked response
- 2.3: Cache hit prevents API call
- 2.4: Cache miss triggers API call
- 2.5: Malformed Claude response error handling
"""

import json
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from analysis.engine import (
    _generate_prompt_for_dimension,
    _run_claude_analysis,
    get_or_create_coaching_session,
)
from db.models import CoachingDimension

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def sample_call_id():
    """Sample call UUID."""
    return str(uuid4())


@pytest.fixture
def sample_rep_id():
    """Sample rep UUID."""
    return uuid4()


@pytest.fixture
def sample_transcript():
    """Sample call transcript for testing."""
    return """Speaker 1: Hi John, thanks for joining the discovery call today.
Speaker 2: Of course, happy to be here.
Speaker 1: Let me start by understanding your current data pipeline setup.
Speaker 2: We're currently using batch jobs with Airflow, but it's getting complex.
Speaker 1: I understand. Can you help me quantify the impact of that complexity?
Speaker 2: Well, we have 2 engineers spending about 40% of their time on maintenance.
Speaker 1: So that's roughly $400K per year in engineering time. What happens if this doesn't get resolved?
Speaker 2: We'll miss our Q3 launch deadline, which puts $2M in revenue at risk.
Speaker 1: That's a significant business impact. Have you considered workflow orchestration tools?
Speaker 2: We've looked at a few options, but weren't sure about the security requirements.
Speaker 1: Let me walk you through how Prefect could help with both the technical and security aspects."""


@pytest.fixture
def sample_rubric():
    """Sample rubric for testing."""
    return {
        "name": "Discovery Quality Rubric",
        "version": "v2.0",
        "category": "discovery",
        "criteria": {
            "question_quality": {
                "weight": 35,
                "description": "Quality and effectiveness of questions asked",
            },
            "active_listening": {
                "weight": 25,
                "description": "Evidence of active listening and engagement",
            },
            "five_wins_coverage": {
                "weight": 30,
                "elements": {
                    "business_win": "Business case and ROI discussion",
                    "technical_win": "Technical requirements and fit",
                    "security_win": "Security and compliance needs",
                    "commercial_win": "Pricing and contract terms",
                    "legal_win": "Legal and procurement process",
                },
            },
        },
        "scoring_guide": {
            "90-100": "Exceptional discovery with deep insights",
            "75-89": "Strong discovery with good coverage",
            "60-74": "Adequate discovery with some gaps",
            "0-59": "Weak discovery needing significant improvement",
        },
        "role_rubric": {
            "role_name": "Account Executive",
            "description": "Focused on business outcomes and deal progression",
        },
        "evaluated_as_role": "ae",
    }


@pytest.fixture
def sample_call_metadata():
    """Sample call metadata."""
    return {
        "title": "Discovery Call - Acme Corp",
        "duration_seconds": 1800,
        "scheduled_at": "2024-01-15T10:00:00Z",
    }


@pytest.fixture
def sample_knowledge_base():
    """Sample knowledge base for product_knowledge dimension."""
    return """## PREFECT CLOUD - Core Features
Workflow orchestration platform for data pipelines.
Features: Dynamic DAG generation, observability, scheduling.

## PREFECT CLOUD - Pricing
Starting at $450/month for Team plan.
Enterprise pricing based on scale and requirements."""


@pytest.fixture
def sample_analysis_result():
    """Sample Claude API analysis result."""
    return {
        "score": 85,
        "strengths": [
            "Excellent impact quantification: $400K engineering cost + $2M revenue risk",
            "Identified critical event: Q3 launch deadline",
            "Good progression from technical to business impact",
        ],
        "areas_for_improvement": [
            "Could explore more decision-making stakeholders",
            "Security win needs deeper discovery",
        ],
        "specific_examples": {
            "good": [
                {
                    "quote": "Can you help me quantify the impact of that complexity?",
                    "timestamp": 45,
                    "analysis": "Strong impact quantification question",
                }
            ],
            "needs_work": [
                {
                    "quote": "Have you considered workflow orchestration tools?",
                    "timestamp": 120,
                    "analysis": "Premature solution presentation before full qualification",
                }
            ],
        },
        "action_items": [
            "Dig deeper into security requirements before next call",
            "Map complete decision-making process including infosec stakeholders",
        ],
        "five_wins_coverage": {
            "business_win": {"covered": True, "score": 90},
            "technical_win": {"covered": True, "score": 80},
            "security_win": {"covered": True, "score": 60},
            "commercial_win": {"covered": False, "score": 0},
            "legal_win": {"covered": False, "score": 0},
            "wins_count": 3,
            "overall_assessment": "Strong business and technical discovery, needs commercial and legal coverage",
        },
    }


# ============================================================================
# Test 2.1: Prompt Generation for Each Dimension
# ============================================================================


class TestGeneratePromptForDimension:
    """Test prompt generation for each coaching dimension."""

    def test_generate_prompt_discovery(
        self, sample_transcript, sample_rubric, sample_call_metadata
    ):
        """Test that discovery prompt is correctly formatted with all required components."""
        messages = _generate_prompt_for_dimension(
            dimension=CoachingDimension.DISCOVERY,
            transcript=sample_transcript,
            rubric=sample_rubric,
            call_metadata=sample_call_metadata,
        )

        # Verify message structure
        assert isinstance(messages, list)
        assert len(messages) == 1
        assert messages[0]["role"] == "user"
        assert "content" in messages[0]

        # Verify content contains required elements
        content = messages[0]["content"]
        assert isinstance(content, list)
        assert len(content) >= 1

        # First content block should have cache control for system prompt
        system_block = content[0]
        assert system_block["type"] == "text"
        assert "cache_control" in system_block
        assert system_block["cache_control"]["type"] == "ephemeral"

        # Verify key elements in system prompt
        system_text = system_block["text"]
        assert "Discovery Quality Rubric" in system_text or "discovery" in system_text.lower()
        assert sample_rubric["version"] in system_text
        assert "SPICED" in system_text or "5 Wins" in system_text or "MEDDIC" in system_text
        assert "JSON" in system_text  # Should specify JSON output format

        # Verify transcript is included
        user_block = content[1] if len(content) > 1 else content[0]
        user_text = user_block["text"]
        assert sample_transcript in user_text

        # Verify call metadata context
        assert sample_call_metadata["title"] in user_text

    def test_generate_prompt_engagement(
        self, sample_transcript, sample_rubric, sample_call_metadata
    ):
        """Test that engagement prompt is correctly formatted."""
        # Update rubric for engagement dimension
        engagement_rubric = {**sample_rubric, "category": "engagement"}

        messages = _generate_prompt_for_dimension(
            dimension=CoachingDimension.ENGAGEMENT,
            transcript=sample_transcript,
            rubric=engagement_rubric,
            call_metadata=sample_call_metadata,
        )

        assert isinstance(messages, list)
        assert len(messages) == 1
        assert messages[0]["role"] == "user"

        # Verify content structure
        content = messages[0]["content"]
        system_text = content[0]["text"]
        assert "engagement" in system_text.lower()
        assert sample_rubric["version"] in system_text

    def test_generate_prompt_objection_handling(
        self, sample_transcript, sample_rubric, sample_call_metadata
    ):
        """Test that objection_handling prompt is correctly formatted."""
        objection_rubric = {**sample_rubric, "category": "objection_handling"}

        messages = _generate_prompt_for_dimension(
            dimension=CoachingDimension.OBJECTION_HANDLING,
            transcript=sample_transcript,
            rubric=objection_rubric,
            call_metadata=sample_call_metadata,
        )

        assert isinstance(messages, list)
        content = messages[0]["content"]
        system_text = content[0]["text"]
        assert "objection" in system_text.lower()

    def test_generate_prompt_product_knowledge_requires_kb(
        self, sample_transcript, sample_rubric, sample_call_metadata, sample_knowledge_base
    ):
        """Test that product_knowledge prompt requires knowledge base and includes it."""
        product_rubric = {**sample_rubric, "category": "product_knowledge"}

        messages = _generate_prompt_for_dimension(
            dimension=CoachingDimension.PRODUCT_KNOWLEDGE,
            transcript=sample_transcript,
            rubric=product_rubric,
            knowledge_base=sample_knowledge_base,
            call_metadata=sample_call_metadata,
        )

        assert isinstance(messages, list)
        content = messages[0]["content"]
        system_text = content[0]["text"]

        # Verify knowledge base is included in prompt
        assert "PREFECT CLOUD" in system_text or sample_knowledge_base in system_text

    def test_generate_prompt_product_knowledge_without_kb_raises_error(
        self, sample_transcript, sample_rubric, sample_call_metadata
    ):
        """Test that product_knowledge prompt raises error if knowledge base is missing."""
        product_rubric = {**sample_rubric, "category": "product_knowledge"}

        with pytest.raises(ValueError, match="Knowledge base required"):
            _generate_prompt_for_dimension(
                dimension=CoachingDimension.PRODUCT_KNOWLEDGE,
                transcript=sample_transcript,
                rubric=product_rubric,
                knowledge_base=None,
                call_metadata=sample_call_metadata,
            )

    def test_generate_prompt_includes_role_context(
        self, sample_transcript, sample_rubric, sample_call_metadata
    ):
        """Test that prompts include role-specific context when available."""
        messages = _generate_prompt_for_dimension(
            dimension=CoachingDimension.DISCOVERY,
            transcript=sample_transcript,
            rubric=sample_rubric,
            call_metadata=sample_call_metadata,
        )

        content = messages[0]["content"]
        system_text = content[0]["text"]

        # Verify role context is included
        assert "Account Executive" in system_text
        assert "ROLE-SPECIFIC EVALUATION CONTEXT" in system_text


# ============================================================================
# Test 2.2: Claude API Call with Mocked Response
# ============================================================================


class TestRunClaudeAnalysisMocked:
    """Test Claude API call with mocked Anthropic client."""

    @patch("analysis.engine.fetch_one")
    @patch("analysis.engine.fetch_all")
    @patch("analysis.engine.anthropic_client")
    @patch("analysis.engine.detect_speaker_role")
    @patch("analysis.engine.load_rubric")
    def test_run_claude_analysis_returns_parsed_json(
        self,
        mock_load_rubric,
        mock_detect_role,
        mock_anthropic,
        mock_fetch_all,
        mock_fetch_one,
        sample_call_id,
        sample_transcript,
        sample_rubric,
        sample_call_metadata,
        sample_analysis_result,
    ):
        """Test that _run_claude_analysis calls API and returns parsed result."""
        # Mock dependencies
        mock_detect_role.return_value = "ae"
        mock_load_rubric.return_value = {"role_name": "Account Executive"}
        mock_fetch_one.return_value = sample_rubric
        mock_fetch_all.return_value = []

        # Mock Claude API response
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=json.dumps(sample_analysis_result))]
        mock_response.usage = MagicMock(
            input_tokens=5000,
            output_tokens=1200,
            cache_creation_input_tokens=0,
            cache_read_input_tokens=0,
        )
        mock_anthropic.messages.create.return_value = mock_response

        # Execute
        result = _run_claude_analysis(
            call_id=sample_call_id,
            dimension=CoachingDimension.DISCOVERY,
            transcript=sample_transcript,
            call_metadata=sample_call_metadata,
        )

        # Verify API was called
        assert mock_anthropic.messages.create.called
        call_args = mock_anthropic.messages.create.call_args

        # Verify API call parameters
        assert call_args.kwargs["model"] == "claude-sonnet-4-5-20250929"
        assert call_args.kwargs["max_tokens"] == 8000
        assert call_args.kwargs["temperature"] == 0.3
        assert "messages" in call_args.kwargs

        # Verify result structure
        assert result["score"] == 85
        assert len(result["strengths"]) > 0
        assert "metadata" in result
        assert result["metadata"]["model"] == "claude-sonnet-4-5-20250929"
        assert result["metadata"]["tokens_used"] == 6200  # 5000 + 1200
        assert result["metadata"]["rubric_role"] == "ae"

    @patch("analysis.engine.fetch_one")
    @patch("analysis.engine.fetch_all")
    @patch("analysis.engine.anthropic_client")
    @patch("analysis.engine.detect_speaker_role")
    @patch("analysis.engine.load_rubric")
    def test_run_claude_analysis_handles_json_in_markdown(
        self,
        mock_load_rubric,
        mock_detect_role,
        mock_anthropic,
        mock_fetch_all,
        mock_fetch_one,
        sample_call_id,
        sample_transcript,
        sample_rubric,
        sample_call_metadata,
        sample_analysis_result,
    ):
        """Test that analysis extracts JSON from markdown code blocks."""
        # Setup mocks
        mock_detect_role.return_value = "ae"
        mock_load_rubric.return_value = {"role_name": "Account Executive"}
        mock_fetch_one.return_value = sample_rubric
        mock_fetch_all.return_value = []

        # Mock response with JSON in markdown
        json_string = json.dumps(sample_analysis_result)
        markdown_response = f"""Here's my analysis:

```json
{json_string}
```

That's the complete assessment."""

        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=markdown_response)]
        mock_response.usage = MagicMock(
            input_tokens=5000,
            output_tokens=1200,
            cache_creation_input_tokens=0,
            cache_read_input_tokens=0,
        )
        mock_anthropic.messages.create.return_value = mock_response

        # Execute
        result = _run_claude_analysis(
            call_id=sample_call_id,
            dimension=CoachingDimension.DISCOVERY,
            transcript=sample_transcript,
            call_metadata=sample_call_metadata,
        )

        # Verify result was extracted from markdown
        assert result["score"] == 85
        assert "metadata" in result

    @patch("analysis.engine.fetch_one")
    @patch("analysis.engine.fetch_all")
    @patch("analysis.engine.anthropic_client")
    @patch("analysis.engine.detect_speaker_role")
    @patch("analysis.engine.load_rubric")
    def test_run_claude_analysis_tracks_cache_tokens(
        self,
        mock_load_rubric,
        mock_detect_role,
        mock_anthropic,
        mock_fetch_all,
        mock_fetch_one,
        sample_call_id,
        sample_transcript,
        sample_rubric,
        sample_call_metadata,
        sample_analysis_result,
    ):
        """Test that cache creation and read tokens are tracked in metadata."""
        # Setup mocks
        mock_detect_role.return_value = "ae"
        mock_load_rubric.return_value = {"role_name": "Account Executive"}
        mock_fetch_one.return_value = sample_rubric
        mock_fetch_all.return_value = []

        # Mock response with cache metrics
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=json.dumps(sample_analysis_result))]
        mock_response.usage = MagicMock(
            input_tokens=500,
            output_tokens=1200,
            cache_creation_input_tokens=4500,
            cache_read_input_tokens=3000,
        )
        mock_anthropic.messages.create.return_value = mock_response

        # Execute
        result = _run_claude_analysis(
            call_id=sample_call_id,
            dimension=CoachingDimension.DISCOVERY,
            transcript=sample_transcript,
            call_metadata=sample_call_metadata,
        )

        # Verify cache metrics are tracked
        assert result["metadata"]["cache_creation_tokens"] == 4500
        assert result["metadata"]["cache_read_tokens"] == 3000
        assert result["metadata"]["input_tokens"] == 500
        assert result["metadata"]["output_tokens"] == 1200


# ============================================================================
# Test 2.3: Cache Hit Prevents API Call
# ============================================================================


class TestCacheHitPreventsApiCall:
    """Test that cache hit prevents Claude API call."""

    @patch("analysis.engine.get_cached_analysis")
    @patch("analysis.engine.get_active_rubric_version")
    @patch("analysis.engine.generate_transcript_hash")
    @patch("analysis.engine.anthropic_client")
    def test_cache_hit_returns_cached_result_without_api_call(
        self,
        mock_anthropic,
        mock_hash,
        mock_rubric_version,
        mock_get_cached,
        sample_call_id,
        sample_rep_id,
        sample_transcript,
    ):
        """Test that cached analysis is returned without calling Claude API."""
        # Setup cache hit
        cached_session = {
            "id": "cached-session-123",
            "call_id": sample_call_id,
            "rep_id": str(sample_rep_id),
            "coaching_dimension": "discovery",
            "score": 90,
            "strengths": ["Excellent discovery"],
            "cache_key": "cache123",
            "transcript_hash": "hash123",
            "rubric_version": "v2.0",
        }

        mock_hash.return_value = "hash123"
        mock_rubric_version.return_value = "v2.0"
        mock_get_cached.return_value = cached_session

        # Execute
        result = get_or_create_coaching_session(
            call_id=uuid4(),
            rep_id=sample_rep_id,
            dimension=CoachingDimension.DISCOVERY,
            transcript=sample_transcript,
            force_reanalysis=False,
        )

        # Verify cache was checked
        assert mock_get_cached.called

        # Verify API was NOT called
        assert not mock_anthropic.messages.create.called

        # Verify cached result was returned
        assert result["id"] == "cached-session-123"
        assert result["score"] == 90

    @patch("analysis.engine.get_cached_analysis")
    @patch("analysis.engine.get_active_rubric_version")
    @patch("analysis.engine.generate_transcript_hash")
    @patch("analysis.engine.settings")
    def test_cache_disabled_always_runs_analysis(
        self,
        mock_settings,
        mock_hash,
        mock_rubric_version,
        mock_get_cached,
        sample_call_id,
        sample_rep_id,
        sample_transcript,
    ):
        """Test that analysis runs when caching is disabled, even if cache exists."""
        # Disable caching
        mock_settings.enable_caching = False

        mock_hash.return_value = "hash123"
        mock_rubric_version.return_value = "v2.0"
        mock_get_cached.return_value = {"id": "should-not-use-this"}

        with (
            patch("analysis.engine.fetch_one") as mock_fetch,
            patch("analysis.engine._run_claude_analysis") as mock_claude,
            patch("analysis.engine.store_analysis_with_cache") as mock_store,
        ):
            mock_fetch.return_value = {"id": sample_call_id, "title": "Test"}
            mock_claude.return_value = {"score": 75}
            mock_store.return_value = "new-session-id"

            result = get_or_create_coaching_session(
                call_id=uuid4(),
                rep_id=sample_rep_id,
                dimension=CoachingDimension.DISCOVERY,
                transcript=sample_transcript,
                force_reanalysis=False,
            )

            # Verify cache check was skipped
            assert not mock_get_cached.called

            # Verify analysis ran
            assert mock_claude.called


# ============================================================================
# Test 2.4: Cache Miss Triggers API Call
# ============================================================================


class TestCacheMissTriggersApiCall:
    """Test that cache miss triggers Claude API call and stores result."""

    @patch("analysis.engine.get_cached_analysis")
    @patch("analysis.engine.get_active_rubric_version")
    @patch("analysis.engine.generate_transcript_hash")
    @patch("analysis.engine.fetch_one")
    @patch("analysis.engine._run_claude_analysis")
    @patch("analysis.engine.store_analysis_with_cache")
    def test_cache_miss_calls_api_and_stores_result(
        self,
        mock_store,
        mock_claude,
        mock_fetch,
        mock_hash,
        mock_rubric_version,
        mock_get_cached,
        sample_call_id,
        sample_rep_id,
        sample_transcript,
        sample_analysis_result,
    ):
        """Test that cache miss triggers new analysis and stores result."""
        # Setup cache miss
        mock_get_cached.return_value = None
        mock_hash.return_value = "hash123"
        mock_rubric_version.return_value = "v2.0"

        # Setup analysis mocks
        mock_fetch.return_value = {"id": sample_call_id, "title": "Discovery Call"}
        mock_claude.return_value = sample_analysis_result
        mock_store.return_value = "new-session-123"

        # Mock the final fetch for the stored session
        stored_session = {
            "id": "new-session-123",
            "call_id": sample_call_id,
            "score": 85,
            "cache_key": "cache123",
        }

        # Set up fetch_one to return different values for different calls
        def fetch_side_effect(query, params):
            if "coaching_sessions" in query and "id = %s" in query:
                return stored_session
            return {"id": sample_call_id, "title": "Discovery Call"}

        mock_fetch.side_effect = fetch_side_effect

        # Execute
        result = get_or_create_coaching_session(
            call_id=uuid4(),
            rep_id=sample_rep_id,
            dimension=CoachingDimension.DISCOVERY,
            transcript=sample_transcript,
            force_reanalysis=False,
        )

        # Verify cache was checked
        assert mock_get_cached.called

        # Verify API was called (cache miss)
        assert mock_claude.called

        # Verify result was stored
        assert mock_store.called
        store_call = mock_store.call_args
        assert store_call.kwargs["dimension"] == CoachingDimension.DISCOVERY
        assert store_call.kwargs["transcript_hash"] == "hash123"
        assert store_call.kwargs["rubric_version"] == "v2.0"
        assert store_call.kwargs["analysis_result"] == sample_analysis_result

        # Verify new session was returned
        assert result["id"] == "new-session-123"

    @patch("analysis.engine.get_cached_analysis")
    @patch("analysis.engine.get_active_rubric_version")
    @patch("analysis.engine.generate_transcript_hash")
    @patch("analysis.engine.fetch_one")
    @patch("analysis.engine._run_claude_analysis")
    @patch("analysis.engine.store_analysis_with_cache")
    def test_force_reanalysis_bypasses_cache(
        self,
        mock_store,
        mock_claude,
        mock_fetch,
        mock_hash,
        mock_rubric_version,
        mock_get_cached,
        sample_call_id,
        sample_rep_id,
        sample_transcript,
        sample_analysis_result,
    ):
        """Test that force_reanalysis=True bypasses cache even if it exists."""
        # Setup cache that should be ignored
        mock_get_cached.return_value = {"id": "old-cached-session", "score": 80}
        mock_hash.return_value = "hash123"
        mock_rubric_version.return_value = "v2.0"

        # Setup analysis mocks
        mock_fetch.return_value = {"id": sample_call_id, "title": "Discovery Call"}
        mock_claude.return_value = sample_analysis_result
        mock_store.return_value = "forced-session-123"

        # Mock final fetch
        def fetch_side_effect(query, params):
            if "coaching_sessions" in query and "id = %s" in query:
                return {"id": "forced-session-123", "score": 85}
            return {"id": sample_call_id, "title": "Discovery Call"}

        mock_fetch.side_effect = fetch_side_effect

        # Execute with force_reanalysis=True
        result = get_or_create_coaching_session(
            call_id=uuid4(),
            rep_id=sample_rep_id,
            dimension=CoachingDimension.DISCOVERY,
            transcript=sample_transcript,
            force_reanalysis=True,
        )

        # Verify cache was NOT checked (bypassed)
        assert not mock_get_cached.called

        # Verify API was called despite potential cache
        assert mock_claude.called

        # Verify new result was stored
        assert mock_store.called

        # Verify new session was returned, not cached one
        assert result["id"] == "forced-session-123"


# ============================================================================
# Test 2.5: Malformed Claude Response Error Handling
# ============================================================================


class TestMalformedResponseError:
    """Test error handling for malformed Claude API responses."""

    @patch("analysis.engine.fetch_one")
    @patch("analysis.engine.fetch_all")
    @patch("analysis.engine.anthropic_client")
    @patch("analysis.engine.detect_speaker_role")
    @patch("analysis.engine.load_rubric")
    def test_malformed_json_raises_value_error(
        self,
        mock_load_rubric,
        mock_detect_role,
        mock_anthropic,
        mock_fetch_all,
        mock_fetch_one,
        sample_call_id,
        sample_transcript,
        sample_rubric,
        sample_call_metadata,
    ):
        """Test that malformed JSON response raises descriptive error."""
        # Setup mocks
        mock_detect_role.return_value = "ae"
        mock_load_rubric.return_value = {"role_name": "Account Executive"}
        mock_fetch_one.return_value = sample_rubric
        mock_fetch_all.return_value = []

        # Mock response with invalid JSON
        invalid_json = '{"score": 85, "strengths": [incomplete json'
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=invalid_json)]
        mock_response.usage = MagicMock(
            input_tokens=5000,
            output_tokens=1200,
            cache_creation_input_tokens=0,
            cache_read_input_tokens=0,
        )
        mock_anthropic.messages.create.return_value = mock_response

        # Execute and verify error
        with pytest.raises(ValueError) as exc_info:
            _run_claude_analysis(
                call_id=sample_call_id,
                dimension=CoachingDimension.DISCOVERY,
                transcript=sample_transcript,
                call_metadata=sample_call_metadata,
            )

        # Verify error message is descriptive
        error_message = str(exc_info.value)
        assert "malformed" in error_message.lower() or "JSON" in error_message

    @patch("analysis.engine.fetch_one")
    @patch("analysis.engine.fetch_all")
    @patch("analysis.engine.anthropic_client")
    @patch("analysis.engine.detect_speaker_role")
    @patch("analysis.engine.load_rubric")
    def test_non_json_response_without_code_block_raises_error(
        self,
        mock_load_rubric,
        mock_detect_role,
        mock_anthropic,
        mock_fetch_all,
        mock_fetch_one,
        sample_call_id,
        sample_transcript,
        sample_rubric,
        sample_call_metadata,
    ):
        """Test that non-JSON response without markdown code block raises error."""
        # Setup mocks
        mock_detect_role.return_value = "ae"
        mock_load_rubric.return_value = {"role_name": "Account Executive"}
        mock_fetch_one.return_value = sample_rubric
        mock_fetch_all.return_value = []

        # Mock response with plain text (no JSON)
        plain_text_response = "This is a great discovery call with excellent questioning."
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=plain_text_response)]
        mock_response.usage = MagicMock(
            input_tokens=5000,
            output_tokens=1200,
            cache_creation_input_tokens=0,
            cache_read_input_tokens=0,
        )
        mock_anthropic.messages.create.return_value = mock_response

        # Execute and verify error
        with pytest.raises(ValueError) as exc_info:
            _run_claude_analysis(
                call_id=sample_call_id,
                dimension=CoachingDimension.DISCOVERY,
                transcript=sample_transcript,
                call_metadata=sample_call_metadata,
            )

        # Verify error message mentions JSON
        error_message = str(exc_info.value)
        assert "JSON" in error_message

    @patch("analysis.engine.fetch_one")
    @patch("analysis.engine.fetch_all")
    @patch("analysis.engine.anthropic_client")
    @patch("analysis.engine.detect_speaker_role")
    @patch("analysis.engine.load_rubric")
    def test_malformed_json_in_markdown_raises_error(
        self,
        mock_load_rubric,
        mock_detect_role,
        mock_anthropic,
        mock_fetch_all,
        mock_fetch_one,
        sample_call_id,
        sample_transcript,
        sample_rubric,
        sample_call_metadata,
    ):
        """Test that malformed JSON inside markdown code block raises error."""
        # Setup mocks
        mock_detect_role.return_value = "ae"
        mock_load_rubric.return_value = {"role_name": "Account Executive"}
        mock_fetch_one.return_value = sample_rubric
        mock_fetch_all.return_value = []

        # Mock response with malformed JSON in markdown
        malformed_markdown = """Here's the analysis:

```json
{"score": 85, "strengths": [incomplete
```

Hope that helps!"""
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=malformed_markdown)]
        mock_response.usage = MagicMock(
            input_tokens=5000,
            output_tokens=1200,
            cache_creation_input_tokens=0,
            cache_read_input_tokens=0,
        )
        mock_anthropic.messages.create.return_value = mock_response

        # Execute and verify error
        with pytest.raises(ValueError) as exc_info:
            _run_claude_analysis(
                call_id=sample_call_id,
                dimension=CoachingDimension.DISCOVERY,
                transcript=sample_transcript,
                call_metadata=sample_call_metadata,
            )

        # Verify error mentions malformed JSON
        error_message = str(exc_info.value)
        assert "malformed" in error_message.lower() or "JSON" in error_message

    @patch("analysis.engine.fetch_one")
    @patch("analysis.engine.fetch_all")
    @patch("analysis.engine.anthropic_client")
    @patch("analysis.engine.detect_speaker_role")
    @patch("analysis.engine.load_rubric")
    def test_api_error_is_propagated(
        self,
        mock_load_rubric,
        mock_detect_role,
        mock_anthropic,
        mock_fetch_all,
        mock_fetch_one,
        sample_call_id,
        sample_transcript,
        sample_rubric,
        sample_call_metadata,
    ):
        """Test that Claude API errors are properly propagated."""
        # Setup mocks
        mock_detect_role.return_value = "ae"
        mock_load_rubric.return_value = {"role_name": "Account Executive"}
        mock_fetch_one.return_value = sample_rubric
        mock_fetch_all.return_value = []

        # Mock API error
        mock_anthropic.messages.create.side_effect = Exception("API rate limit exceeded")

        # Execute and verify error is raised
        with pytest.raises(Exception) as exc_info:
            _run_claude_analysis(
                call_id=sample_call_id,
                dimension=CoachingDimension.DISCOVERY,
                transcript=sample_transcript,
                call_metadata=sample_call_metadata,
            )

        assert "rate limit" in str(exc_info.value).lower()
