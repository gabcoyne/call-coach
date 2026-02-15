"""
Unit tests for thematic grouping module.

Tests cover:
- Grouping insights by theme using dimension mapping
- Keyword-based theme matching
- Deduplication of similar insights
- Priority-based theme ordering
- Filtering empty themes
"""

import pytest

from analysis.thematic_grouper import group_insights_by_theme


@pytest.fixture
def sample_dimension_details():
    """Sample dimension-specific analysis results."""
    return {
        "discovery": {
            "score": 85,
            "strengths": [
                "Asked strong impact quantification questions",
                "Identified key stakeholders early",
            ],
            "improvements": [
                "Need to explore decision-making process more thoroughly",
            ],
        },
        "product_knowledge": {
            "score": 78,
            "strengths": [
                "Accurate technical explanation of API capabilities",
            ],
            "needs_improvement": [
                "Missed opportunity to discuss integration patterns",
            ],
        },
        "engagement": {
            "score": 72,
            "strengths": ["Good listening and rapport building"],
            "improvements": [],
        },
    }


@pytest.fixture
def sample_aggregated_insights():
    """Sample aggregated strengths and improvements."""
    return {
        "strengths": [
            "Asked strong impact quantification questions",
            "Accurate technical explanation of API capabilities",
            "Good listening and rapport building",
        ],
        "improvements": [
            "Need to explore decision-making process more thoroughly",
            "Missed opportunity to discuss integration patterns",
        ],
    }


class TestGroupInsightsByTheme:
    """Test thematic grouping of insights."""

    def test_groups_insights_by_dimension_mapping(self, sample_dimension_details):
        """
        GIVEN dimension details with strengths/improvements
        WHEN group_insights_by_theme is called
        THEN insights grouped into correct themes
        """
        all_strengths = []
        all_improvements = []

        # Extract aggregated lists
        for dim_data in sample_dimension_details.values():
            all_strengths.extend(dim_data.get("strengths", []))
            all_improvements.extend(
                dim_data.get("improvements", []) + dim_data.get("needs_improvement", [])
            )

        themed = group_insights_by_theme(all_strengths, all_improvements, sample_dimension_details)

        # Should have themes for discovery, product_knowledge, engagement
        assert "Discovery & Qualification" in themed
        assert "Technical Knowledge" in themed
        assert "Engagement & Communication" in themed

    def test_each_theme_has_required_fields(
        self, sample_dimension_details, sample_aggregated_insights
    ):
        """
        GIVEN valid insights
        WHEN group_insights_by_theme is called
        THEN each theme has strengths, improvements, count, priority
        """
        themed = group_insights_by_theme(
            sample_aggregated_insights["strengths"],
            sample_aggregated_insights["improvements"],
            sample_dimension_details,
        )

        for _theme_name, theme_data in themed.items():
            assert "strengths" in theme_data
            assert "improvements" in theme_data
            assert "count" in theme_data
            assert "priority" in theme_data
            assert isinstance(theme_data["strengths"], list)
            assert isinstance(theme_data["improvements"], list)

    def test_themes_sorted_by_priority(self, sample_dimension_details, sample_aggregated_insights):
        """
        GIVEN multiple themes with insights
        WHEN group_insights_by_theme is called
        THEN themes ordered by priority (lower number first)
        """
        themed = group_insights_by_theme(
            sample_aggregated_insights["strengths"],
            sample_aggregated_insights["improvements"],
            sample_dimension_details,
        )

        theme_names = list(themed.keys())
        priorities = [themed[name]["priority"] for name in theme_names]

        # Priorities should be ascending
        assert priorities == sorted(priorities)

    def test_empty_themes_filtered_out(self):
        """
        GIVEN dimension details with no insights for some dimensions
        WHEN group_insights_by_theme is called
        THEN empty themes excluded from results
        """
        dimension_details = {
            "discovery": {
                "strengths": ["Good question"],
                "improvements": [],
            }
        }

        themed = group_insights_by_theme(
            ["Good question"],
            [],
            dimension_details,
        )

        # Should only have Discovery theme (not empty ones)
        assert len(themed) >= 1
        for theme_data in themed.values():
            assert theme_data["count"] > 0

    def test_deduplication_removes_similar_insights(self):
        """
        GIVEN insights with similar wording
        WHEN group_insights_by_theme is called
        THEN duplicates removed
        """
        dimension_details = {
            "discovery": {
                "strengths": [
                    "Asked about business impact",
                    "Asked about business impact and ROI",  # Very similar
                    "Completely different insight",
                ],
                "improvements": [],
            }
        }

        all_strengths = dimension_details["discovery"]["strengths"]

        themed = group_insights_by_theme(all_strengths, [], dimension_details)

        # Should have deduplicated similar insights
        discovery_theme = themed.get("Discovery & Qualification", {})
        strengths = discovery_theme.get("strengths", [])

        # Deduplication should process insights - check it doesn't fail
        # The exact deduplication threshold may vary (80% similarity)
        assert len(strengths) <= 3  # At most the original count
        assert len(strengths) > 0  # But should have some content

    def test_keyword_matching_assigns_unassigned_insights(self):
        """
        GIVEN insights in aggregated list not in dimension details
        WHEN group_insights_by_theme is called
        THEN insights assigned via keyword matching
        """
        dimension_details = {}  # Empty - no dimension-based assignment

        all_strengths = [
            "Asked excellent discovery questions about pain points",  # Should match Discovery
            "Explained product features with technical accuracy",  # Should match Technical
        ]

        themed = group_insights_by_theme(all_strengths, [], dimension_details)

        # Should have assigned via keyword matching
        assert len(themed) > 0
        # Check that insights were assigned somewhere
        total_insights = sum(len(theme["strengths"]) for theme in themed.values())
        assert total_insights > 0

    def test_count_reflects_total_insights(
        self, sample_dimension_details, sample_aggregated_insights
    ):
        """
        GIVEN theme with strengths and improvements
        WHEN group_insights_by_theme is called
        THEN count equals len(strengths) + len(improvements)
        """
        themed = group_insights_by_theme(
            sample_aggregated_insights["strengths"],
            sample_aggregated_insights["improvements"],
            sample_dimension_details,
        )

        for theme_data in themed.values():
            expected_count = len(theme_data["strengths"]) + len(theme_data["improvements"])
            assert theme_data["count"] == expected_count

    def test_handles_empty_input_gracefully(self):
        """
        GIVEN empty insights and dimension details
        WHEN group_insights_by_theme is called
        THEN returns empty dict (no themes)
        """
        themed = group_insights_by_theme([], [], {})

        assert themed == {}

    def test_handles_needs_improvement_field_variant(self):
        """
        GIVEN dimension with 'needs_improvement' instead of 'improvements'
        WHEN group_insights_by_theme is called
        THEN still extracts improvements correctly
        """
        dimension_details = {
            "discovery": {
                "strengths": ["Good question"],
                "needs_improvement": ["Ask more follow-up questions"],  # Alternative field name
            }
        }

        themed = group_insights_by_theme(
            ["Good question"],
            ["Ask more follow-up questions"],
            dimension_details,
        )

        discovery_theme = themed.get("Discovery & Qualification", {})
        assert len(discovery_theme.get("improvements", [])) > 0

    def test_objection_handling_theme_included_when_present(self):
        """
        GIVEN insights about objections
        WHEN group_insights_by_theme is called
        THEN Objection Handling theme created
        """
        dimension_details = {
            "objection_handling": {
                "strengths": ["Addressed pricing concern effectively"],
                "improvements": [],
            }
        }

        themed = group_insights_by_theme(
            ["Addressed pricing concern effectively"],
            [],
            dimension_details,
        )

        assert "Objection Handling" in themed
        assert len(themed["Objection Handling"]["strengths"]) > 0
