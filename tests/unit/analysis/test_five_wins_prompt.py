"""
Tests for Five Wins Prompt - Unified Coaching Analysis

Tests that the prompt:
1. Produces valid JSON output structure
2. Contains no methodology jargon (except in negative instructions)
3. Includes required fields for each win
4. Adapts to call type
"""

import pytest

from analysis.prompts.five_wins_prompt import analyze_five_wins_prompt


class TestFiveWinsPrompt:
    """Test suite for Five Wins unified prompt."""

    def test_prompt_structure(self):
        """Test that prompt generates correct message structure."""
        messages = analyze_five_wins_prompt(
            transcript="Rep: Hello. Customer: Hi, we're evaluating data orchestration tools.",
            call_type="discovery",
        )

        assert len(messages) == 1
        assert messages[0]["role"] == "user"
        assert len(messages[0]["content"]) == 2

        # System prompt should have cache control
        system_content = messages[0]["content"][0]
        assert system_content["type"] == "text"
        assert "cache_control" in system_content

        # User prompt should contain transcript
        user_content = messages[0]["content"][1]
        assert "evaluating data orchestration" in user_content["text"]

    def test_no_methodology_jargon_in_active_instructions(self):
        """Test that methodology names only appear in 'do not use' instructions."""
        messages = analyze_five_wins_prompt(
            transcript="Rep: Let me understand your needs.",
            call_type="discovery",
        )

        system_text = messages[0]["content"][0]["text"]
        lines = system_text.split("\n")

        jargon_terms = ["spiced", "challenger", "sandler", "meddic", "spin selling"]
        problematic_lines = []

        for line_num, line in enumerate(lines):
            line_lower = line.lower()

            # Skip lines that are instructions about NOT using jargon
            if any(
                x in line_lower
                for x in ["never mention", "do not", "methodology jargon", "never use"]
            ):
                continue

            # Check for jargon in active instructions
            for jargon in jargon_terms:
                if jargon in line_lower:
                    problematic_lines.append((line_num, line[:80], jargon))

        assert (
            not problematic_lines
        ), f"Found methodology jargon in active instructions: {problematic_lines}"

    def test_contains_five_wins_definitions(self):
        """Test that all five wins are defined in the prompt."""
        messages = analyze_five_wins_prompt(
            transcript="Test transcript",
            call_type="discovery",
        )

        system_text = messages[0]["content"][0]["text"]

        # Check all wins are defined
        required_wins = [
            "Business Win",
            "Technical Win",
            "Security Win",
            "Commercial Win",
            "Legal Win",
        ]

        for win in required_wins:
            assert win in system_text, f"Missing win definition: {win}"

    def test_contains_json_schema(self):
        """Test that prompt includes JSON output schema."""
        messages = analyze_five_wins_prompt(
            transcript="Test transcript",
            call_type="discovery",
        )

        system_text = messages[0]["content"][0]["text"]

        # Check for key schema elements
        assert "five_wins_evaluation" in system_text
        assert "narrative" in system_text
        assert "primary_action" in system_text
        assert "wins_addressed" in system_text
        assert "wins_missed" in system_text

    def test_call_type_affects_primary_win(self):
        """Test that call type determines primary win focus."""
        discovery_messages = analyze_five_wins_prompt(
            transcript="Test",
            call_type="discovery",
        )
        demo_messages = analyze_five_wins_prompt(
            transcript="Test",
            call_type="demo",
        )

        discovery_text = discovery_messages[0]["content"][0]["text"]
        demo_text = demo_messages[0]["content"][0]["text"]

        # Discovery should focus on Business Win
        assert "Primary Win to Advance: Business Win" in discovery_text

        # Demo should focus on Technical Win
        assert "Primary Win to Advance: Technical Win" in demo_text

    def test_call_metadata_included(self):
        """Test that call metadata is included when provided."""
        messages = analyze_five_wins_prompt(
            transcript="Test transcript",
            call_type="discovery",
            call_metadata={
                "title": "Acme Corp Discovery Call",
                "duration_seconds": 1800,
            },
        )

        user_text = messages[0]["content"][1]["text"]

        assert "Acme Corp Discovery Call" in user_text
        assert "30 minutes" in user_text  # 1800 seconds = 30 minutes

    def test_weights_sum_to_100(self):
        """Test that win weights mentioned in prompt sum to 100."""
        messages = analyze_five_wins_prompt(
            transcript="Test",
            call_type="discovery",
        )

        system_text = messages[0]["content"][0]["text"]

        # Extract percentages from win headers
        import re

        percentages = re.findall(r"(\d+)%\)", system_text)
        total = sum(int(p) for p in percentages[:5])  # First 5 should be the wins

        assert total == 100, f"Win weights sum to {total}, expected 100"

    def test_score_ranges_in_schema(self):
        """Test that JSON schema specifies correct score ranges."""
        messages = analyze_five_wins_prompt(
            transcript="Test",
            call_type="discovery",
        )

        system_text = messages[0]["content"][0]["text"]

        # Check score ranges match weights
        assert "<0-35>" in system_text  # Business
        assert "<0-25>" in system_text  # Technical
        assert "<0-15>" in system_text  # Security (appears twice for security and commercial)
        assert "<0-10>" in system_text  # Legal


class TestFiveWinsPromptCallTypes:
    """Test prompt behavior for different call types."""

    @pytest.mark.parametrize(
        "call_type,expected_primary",
        [
            ("discovery", "Business Win"),
            ("technical_deep_dive", "Technical Win"),
            ("demo", "Technical Win"),
            ("poc_kickoff", "Technical Win"),
            ("architecture_review", "Security Win"),
            ("executive_presentation", "Business Win"),
            ("negotiation", "Commercial Win"),
        ],
    )
    def test_primary_win_by_call_type(self, call_type, expected_primary):
        """Test that each call type maps to correct primary win."""
        messages = analyze_five_wins_prompt(
            transcript="Test",
            call_type=call_type,
        )

        system_text = messages[0]["content"][0]["text"]
        assert f"Primary Win to Advance: {expected_primary}" in system_text
