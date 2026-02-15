"""
Unit tests for moment extraction module.

Tests cover:
- Extracting key moments from dimension details
- Scoring moment impact based on multiple factors
- Deduplication of nearby timestamps
- Limiting output to top N moments
- Formatting timestamps as MM:SS
"""

import pytest

from analysis.moment_extractor import extract_key_moments, format_timestamp


@pytest.fixture
def sample_dimension_details():
    """Sample dimension analysis with specific examples."""
    return {
        "discovery": {
            "score": 85,
            "strengths": ["Good questions", "Active listening"],
            "specific_examples": {
                "good": [
                    {
                        "timestamp": 125,
                        "quote": "Can you quantify the business impact?",
                        "analysis": "Strong impact quantification question",
                    },
                    {
                        "timestamp": 240,
                        "quote": "Who else is involved in this decision?",
                        "analysis": "Identified key stakeholders",
                    },
                ],
                "needs_work": [
                    {
                        "timestamp": 320,
                        "quote": "Let me show you our product",
                        "analysis": "Premature solution presentation before full qualification",
                    }
                ],
            },
        },
        "product_knowledge": {
            "score": 78,
            "strengths": ["Technical accuracy"],
            "specific_examples": {
                "good": [
                    {
                        "timestamp": 450,
                        "quote": "Prefect handles dynamic DAG generation",
                        "analysis": "Accurate technical explanation",
                    }
                ],
                "needs_work": [],
            },
        },
    }


class TestExtractKeyMoments:
    """Test key moment extraction."""

    def test_extract_moments_from_multiple_dimensions(self, sample_dimension_details):
        """
        GIVEN dimension details with specific examples
        WHEN extract_key_moments is called
        THEN it returns moments from all dimensions
        """
        moments = extract_key_moments(sample_dimension_details)

        # Should extract moments from both discovery and product_knowledge
        assert len(moments) > 0
        assert any(m["dimension"] == "discovery" for m in moments)
        assert any(m["dimension"] == "product_knowledge" for m in moments)

    def test_moments_include_required_fields(self, sample_dimension_details):
        """
        GIVEN valid dimension details
        WHEN extract_key_moments is called
        THEN each moment has timestamp, moment_type, summary, dimension
        """
        moments = extract_key_moments(sample_dimension_details)

        for moment in moments:
            assert "timestamp" in moment
            assert "moment_type" in moment
            assert "summary" in moment
            assert "dimension" in moment
            assert moment["moment_type"] in ["strength", "improvement"]

    def test_moments_sorted_chronologically(self, sample_dimension_details):
        """
        GIVEN moments from various timestamps
        WHEN extract_key_moments is called
        THEN moments are sorted by timestamp (ascending)
        """
        moments = extract_key_moments(sample_dimension_details)

        timestamps = [m["timestamp"] for m in moments]
        assert timestamps == sorted(timestamps)

    def test_limit_parameter_caps_results(self, sample_dimension_details):
        """
        GIVEN many potential moments
        WHEN extract_key_moments is called with limit=2
        THEN only top 2 moments returned
        """
        moments = extract_key_moments(sample_dimension_details, limit=2)

        assert len(moments) <= 2

    def test_deduplication_removes_nearby_moments(self):
        """
        GIVEN multiple moments within 30 seconds
        WHEN extract_key_moments is called
        THEN only highest-scored moment kept
        """
        dimension_details = {
            "discovery": {
                "specific_examples": {
                    "good": [
                        {
                            "timestamp": 100,
                            "analysis": "First question",
                        },
                        {
                            "timestamp": 110,  # Within 30s of previous
                            "analysis": "Second question",
                        },
                        {
                            "timestamp": 200,  # Far enough away
                            "analysis": "Third question",
                        },
                    ],
                    "needs_work": [],
                }
            }
        }

        moments = extract_key_moments(dimension_details)

        # Should deduplicate first two, keep third
        assert len(moments) <= 2
        timestamps = [m["timestamp"] for m in moments]
        # Should not have both 100 and 110
        assert not (100 in timestamps and 110 in timestamps)

    def test_empty_dimension_details_returns_empty_list(self):
        """
        GIVEN empty dimension details
        WHEN extract_key_moments is called
        THEN empty list returned
        """
        moments = extract_key_moments({})

        assert moments == []

    def test_missing_specific_examples_returns_empty_list(self):
        """
        GIVEN dimension details without specific_examples
        WHEN extract_key_moments is called
        THEN empty list returned
        """
        dimension_details = {
            "discovery": {
                "score": 85,
                "strengths": ["Good questions"],
                # No specific_examples
            }
        }

        moments = extract_key_moments(dimension_details)

        assert moments == []

    def test_moments_without_timestamp_excluded(self):
        """
        GIVEN examples missing timestamp field
        WHEN extract_key_moments is called
        THEN those examples excluded from results
        """
        dimension_details = {
            "discovery": {
                "specific_examples": {
                    "good": [
                        {
                            "quote": "No timestamp here",
                            "analysis": "This should be excluded",
                        },
                        {
                            "timestamp": 100,
                            "analysis": "This should be included",
                        },
                    ],
                    "needs_work": [],
                }
            }
        }

        moments = extract_key_moments(dimension_details)

        # Should only include the one with timestamp
        assert len(moments) == 1
        assert moments[0]["timestamp"] == 100

    def test_long_quotes_truncated_in_summary(self):
        """
        GIVEN example with very long quote
        WHEN extract_key_moments is called
        THEN quote truncated with ellipsis
        """
        dimension_details = {
            "discovery": {
                "specific_examples": {
                    "good": [
                        {
                            "timestamp": 100,
                            "quote": "This is a very long quote " * 20,  # 500+ chars
                        }
                    ],
                    "needs_work": [],
                }
            }
        }

        moments = extract_key_moments(dimension_details)

        assert len(moments) == 1
        assert len(moments[0]["summary"]) <= 150
        assert moments[0]["summary"].endswith("...")

    def test_dimension_weights_affect_selection(self):
        """
        GIVEN moments from different dimensions
        WHEN extract_key_moments is called with low limit
        THEN higher-weighted dimensions (discovery) preferred
        """
        dimension_details = {
            "discovery": {  # Weight 4
                "specific_examples": {
                    "good": [{"timestamp": 100, "analysis": "Discovery moment"}],
                    "needs_work": [],
                }
            },
            "engagement": {  # Weight 1
                "specific_examples": {
                    "good": [{"timestamp": 200, "analysis": "Engagement moment"}],
                    "needs_work": [],
                }
            },
        }

        moments = extract_key_moments(dimension_details, limit=1)

        # With limit=1, should prefer discovery (higher weight)
        assert len(moments) == 1
        assert moments[0]["dimension"] == "discovery"


class TestFormatTimestamp:
    """Test timestamp formatting."""

    def test_format_seconds_as_mm_ss(self):
        """
        GIVEN timestamp in seconds
        WHEN format_timestamp is called
        THEN returns MM:SS format
        """
        assert format_timestamp(125) == "2:05"
        assert format_timestamp(0) == "0:00"
        assert format_timestamp(3661) == "61:01"

    def test_format_single_digit_seconds_padded(self):
        """
        GIVEN seconds < 10
        WHEN format_timestamp is called
        THEN seconds padded with leading zero
        """
        assert format_timestamp(65) == "1:05"
        assert format_timestamp(9) == "0:09"

    def test_format_minutes_no_padding(self):
        """
        GIVEN minutes > 9
        WHEN format_timestamp is called
        THEN minutes not padded
        """
        assert format_timestamp(600) == "10:00"
        assert format_timestamp(3599) == "59:59"
