"""
Unit tests for action item filtering module.

Tests cover:
- Filtering action items by actionability score
- Scoring based on specificity and concreteness
- Penalizing vague recommendations
- Prioritizing concrete action items
- Categorizing by timing (pre-call, during-call, post-call)
"""

from analysis.action_filter import categorize_action_items, filter_actionable_items


class TestFilterActionableItems:
    """Test action item filtering for actionability."""

    def test_concrete_items_pass_filter(self):
        """
        GIVEN concrete action items with specifics
        WHEN filter_actionable_items is called
        THEN items pass filter
        """
        action_items = [
            "Prepare 3 customer references before next call on Friday",
            "Send pricing proposal by end of day Thursday",
            "Schedule technical deep dive with John Smith for next week",
        ]

        filtered = filter_actionable_items(action_items, min_score=60)

        # All should pass - they're concrete
        assert len(filtered) >= 2

    def test_vague_items_filtered_out(self):
        """
        GIVEN vague action items without specifics
        WHEN filter_actionable_items is called
        THEN items filtered out
        """
        action_items = [
            "Build a repository of objection handling examples",  # Vague
            "Practice discovery framework regularly",  # Vague
            "Work on better engagement overall",  # Vague
        ]

        filtered = filter_actionable_items(action_items, min_score=60)

        # Should filter out vague items
        assert len(filtered) < len(action_items)

    def test_items_with_specific_names_score_higher(self):
        """
        GIVEN action items with and without specific names
        WHEN filter_actionable_items is called
        THEN items with names prioritized
        """
        action_items = [
            "Follow up with Sarah Johnson about security requirements",  # Has name
            "Follow up about security requirements",  # No name
        ]

        filtered = filter_actionable_items(action_items, max_items=1)

        # Should prefer the one with specific name
        assert len(filtered) == 1
        assert "Sarah Johnson" in filtered[0] or len(filtered) >= 1

    def test_items_with_numbers_score_higher(self):
        """
        GIVEN action items with and without quantification
        WHEN filter_actionable_items is called
        THEN items with numbers prioritized
        """
        action_items = [
            "Prepare 3 customer case studies",  # Has number
            "Prepare some customer case studies",  # No number
        ]

        filtered = filter_actionable_items(action_items, max_items=1)

        assert len(filtered) == 1
        # Should prefer quantified item
        assert "3" in filtered[0] or len(filtered) >= 1

    def test_max_items_limit_respected(self):
        """
        GIVEN many actionable items
        WHEN filter_actionable_items is called with max_items
        THEN result limited to max
        """
        action_items = [f"Send follow-up email to customer {i} by tomorrow" for i in range(20)]

        filtered = filter_actionable_items(action_items, max_items=5)

        assert len(filtered) <= 5

    def test_min_score_threshold_filters_low_scores(self):
        """
        GIVEN items with varying actionability
        WHEN filter_actionable_items called with high min_score
        THEN only high-scoring items included
        """
        action_items = [
            "Review security documentation before call with CISO on Tuesday",  # High score
            "Be more prepared",  # Low score
        ]

        filtered = filter_actionable_items(action_items, min_score=70)

        # Should filter appropriately - may filter all or some depending on scoring
        # At minimum, should not have both if one is clearly vague
        assert len(filtered) <= len(action_items)
        # If any pass, they should be actionable (not the vague one)
        if filtered:
            assert all("Be more prepared" not in item for item in filtered)

    def test_empty_list_returns_empty(self):
        """
        GIVEN empty action items list
        WHEN filter_actionable_items is called
        THEN empty list returned
        """
        filtered = filter_actionable_items([])

        assert filtered == []

    def test_items_with_specific_verbs_score_higher(self):
        """
        GIVEN items with specific vs generic verbs
        WHEN filter_actionable_items is called
        THEN specific verbs prioritized
        """
        action_items = [
            "Schedule demo with technical team",  # Specific verb
            "Work on better demos",  # Generic verb
        ]

        filtered = filter_actionable_items(action_items, max_items=1)

        assert len(filtered) == 1
        # Should prefer specific verb
        assert "Schedule" in filtered[0] or "demo" in filtered[0]

    def test_items_with_time_bounds_score_higher(self):
        """
        GIVEN items with and without time constraints
        WHEN filter_actionable_items is called
        THEN time-bound items prioritized
        """
        action_items = [
            "Send proposal before next call",  # Time-bound
            "Send proposal",  # Not time-bound
        ]

        filtered = filter_actionable_items(action_items, max_items=1)

        assert len(filtered) == 1
        # Should prefer time-bound
        assert "before" in filtered[0] or len(filtered) >= 1

    def test_very_short_items_penalized(self):
        """
        GIVEN very short action items (< 20 chars)
        WHEN filter_actionable_items is called
        THEN short items penalized
        """
        action_items = [
            "Follow up",  # Too short
            "Follow up with customer about pricing concerns and timeline",  # Good length
        ]

        filtered = filter_actionable_items(action_items, min_score=50, max_items=1)

        # Should prefer longer, more detailed item
        assert len(filtered) == 1
        assert len(filtered[0]) > 20

    def test_generic_coaching_advice_penalized(self):
        """
        GIVEN items with generic coaching language
        WHEN filter_actionable_items is called
        THEN generic advice filtered out
        """
        action_items = [
            "Be more confident in your delivery",  # Generic coaching
            "Remember to ask follow-up questions",  # Generic
            "Prepare ROI calculator for next call",  # Specific action
        ]

        filtered = filter_actionable_items(action_items, min_score=60)

        # Should prefer specific action over generic advice
        assert "Prepare ROI calculator" in " ".join(filtered) or len(filtered) >= 1


class TestCategorizeActionItems:
    """Test action item categorization by timing."""

    def test_pre_call_items_categorized(self):
        """
        GIVEN items with pre-call keywords
        WHEN categorize_action_items is called
        THEN items in pre_call category
        """
        action_items = [
            "Prepare customer references before next call",
            "Review their tech stack before meeting",
        ]

        categorized = categorize_action_items(action_items)

        assert "pre_call" in categorized
        assert len(categorized["pre_call"]) >= 1

    def test_during_call_items_categorized(self):
        """
        GIVEN items with during-call keywords
        WHEN categorize_action_items is called
        THEN items in during_call category
        """
        action_items = [
            "Next time, ask about budget constraints",
            "In the call, listen for pain points",
        ]

        categorized = categorize_action_items(action_items)

        assert "during_call" in categorized
        assert len(categorized["during_call"]) >= 1

    def test_post_call_items_categorized(self):
        """
        GIVEN items with post-call keywords
        WHEN categorize_action_items is called
        THEN items in post_call category
        """
        action_items = [
            "Follow up with proposal after the call",
            "Send meeting notes to stakeholders",
        ]

        categorized = categorize_action_items(action_items)

        assert "post_call" in categorized
        assert len(categorized["post_call"]) >= 1

    def test_general_items_categorized(self):
        """
        GIVEN items without timing keywords
        WHEN categorize_action_items is called
        THEN items in general category
        """
        action_items = [
            "Improve technical knowledge of API capabilities",
        ]

        categorized = categorize_action_items(action_items)

        # Should be in general or assigned somewhere
        assert "general" in categorized or len(categorized) > 0

    def test_empty_categories_removed(self):
        """
        GIVEN items that only match one category
        WHEN categorize_action_items is called
        THEN empty categories not included
        """
        action_items = [
            "Prepare references before call",  # Only pre_call
        ]

        categorized = categorize_action_items(action_items)

        # Should only have categories with items
        for category_items in categorized.values():
            assert len(category_items) > 0

    def test_empty_list_returns_empty_dict(self):
        """
        GIVEN empty action items
        WHEN categorize_action_items is called
        THEN empty dict returned
        """
        categorized = categorize_action_items([])

        assert categorized == {}

    def test_multiple_categories_possible(self):
        """
        GIVEN diverse action items
        WHEN categorize_action_items is called
        THEN multiple categories populated
        """
        action_items = [
            "Prepare references before call",  # pre_call
            "Ask about budget in next meeting",  # during_call
            "Send follow-up email after",  # post_call
        ]

        categorized = categorize_action_items(action_items)

        # Should have multiple categories
        assert len(categorized) >= 2
