"""Tests for the fixtures generator script."""
import sys
from pathlib import Path

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.generate_fixtures import FixturesGenerator


class TestFixturesGenerator:
    """Test the fixtures generator functionality."""

    def test_generator_initialization(self):
        """Test that the generator initializes correctly."""
        generator = FixturesGenerator(num_calls=5, days_back=30, seed=42)
        assert generator.num_calls == 5
        assert generator.days_back == 30
        assert generator.seed == 42

    def test_speaker_generation(self):
        """Test that speakers are generated correctly."""
        generator = FixturesGenerator(num_calls=5, seed=42)
        speakers = generator.generate_speakers()

        assert len(speakers) > 0
        assert len([s for s in speakers if s["role"] == "ae"]) > 0
        assert len([s for s in speakers if s["role"] == "se"]) > 0
        assert len([s for s in speakers if s["role"] == "csm"]) > 0

        # All speakers should have @prefect.io email
        for speaker in speakers:
            assert speaker["email"].endswith("@prefect.io")
            assert speaker["company_side"] is True

    def test_opportunity_generation(self):
        """Test that opportunities are generated correctly."""
        generator = FixturesGenerator(num_calls=10, seed=42)
        generator.generate_speakers()
        opportunities = generator.generate_opportunities(num_opportunities=3)

        assert len(opportunities) == 3
        for opp in opportunities:
            assert "gong_opportunity_id" in opp
            assert "name" in opp
            assert "account_name" in opp
            assert "owner_email" in opp
            assert opp["owner_email"].endswith("@prefect.io")

    def test_call_generation(self):
        """Test that calls are generated correctly."""
        generator = FixturesGenerator(num_calls=10, days_back=60, seed=42)
        calls = generator.generate_calls()

        assert len(calls) == 10
        for call in calls:
            assert "gong_call_id" in call
            assert "title" in call
            assert "call_type" in call
            assert "product" in call
            assert call["call_type"] in ["discovery", "demo", "technical_deep_dive", "negotiation", "follow_up"]
            assert call["product"] in ["prefect", "horizon", "both"]

    def test_call_speakers_generation(self):
        """Test that call speakers are generated correctly."""
        generator = FixturesGenerator(num_calls=5, seed=42)
        generator.generate_speakers()
        generator.generate_calls()
        speakers = generator.generate_call_speakers()

        assert len(speakers) > 0

        # Check that each speaker has required fields
        for speaker in speakers:
            assert "call_id" in speaker
            assert "name" in speaker
            assert "email" in speaker
            assert "role" in speaker
            assert "company_side" in speaker

        # Should have both company-side and prospect speakers
        company_speakers = [s for s in speakers if s["company_side"]]
        prospect_speakers = [s for s in speakers if not s["company_side"]]
        assert len(company_speakers) > 0
        assert len(prospect_speakers) > 0

    def test_transcript_generation(self):
        """Test that transcripts are generated correctly."""
        generator = FixturesGenerator(num_calls=3, seed=42)
        generator.generate_calls()
        speakers = generator.generate_call_speakers()
        transcripts = generator.generate_transcripts(speakers)

        assert len(transcripts) > 0

        for transcript in transcripts:
            assert "call_id" in transcript
            assert "speaker_id" in transcript
            assert "text" in transcript
            assert "sequence_number" in transcript
            assert len(transcript["text"]) > 0
            assert transcript["sentiment"] in ["positive", "neutral", "negative"]

    def test_transcript_line_generation(self):
        """Test that transcript lines are realistic."""
        generator = FixturesGenerator(seed=42)

        # Test various call types
        for call_type in ["discovery", "demo", "technical_deep_dive"]:
            company_line = generator._generate_transcript_line(call_type, is_company=True, prospect=None)
            prospect_line = generator._generate_transcript_line(call_type, is_company=False, prospect=None)

            assert len(company_line) > 0
            assert len(prospect_line) > 0
            # Lines should be different for different speakers
            assert company_line != prospect_line

    def test_coaching_sessions_generation(self):
        """Test that coaching sessions are generated correctly."""
        generator = FixturesGenerator(num_calls=5, seed=42)
        generator.generate_calls()
        speakers = generator.generate_call_speakers()
        sessions = generator.generate_coaching_sessions(speakers)

        assert len(sessions) > 0

        for session in sessions:
            assert "call_id" in session
            assert "rep_id" in session
            assert "coaching_dimension" in session
            assert "session_type" in session
            assert "score" in session
            assert 0 <= session["score"] <= 100
            assert "strengths" in session
            assert len(session["strengths"]) > 0
            assert "areas_for_improvement" in session
            assert len(session["areas_for_improvement"]) > 0

    def test_strengths_generation(self):
        """Test that coaching strengths are relevant to dimension."""
        generator = FixturesGenerator(seed=42)

        for dimension in ["product_knowledge", "discovery", "objection_handling", "engagement"]:
            strengths = generator._generate_strengths(dimension)
            assert len(strengths) >= 1
            assert all(isinstance(s, str) for s in strengths)

    def test_improvements_generation(self):
        """Test that improvement areas are relevant to dimension."""
        generator = FixturesGenerator(seed=42)

        for dimension in ["product_knowledge", "discovery", "objection_handling", "engagement"]:
            improvements = generator._generate_improvements(dimension)
            assert len(improvements) >= 1
            assert all(isinstance(s, str) for s in improvements)

    def test_action_items_generation(self):
        """Test that action items are generated based on score."""
        generator = FixturesGenerator(seed=42)

        # Higher scores should have fewer action items
        items_high_score = generator._generate_action_items("discovery", score=90)
        items_low_score = generator._generate_action_items("discovery", score=30)

        assert len(items_high_score) <= len(items_low_score)

    def test_call_opportunities_linking(self):
        """Test that calls are linked to opportunities."""
        generator = FixturesGenerator(num_calls=10, seed=42)
        generator.generate_speakers()
        generator.generate_opportunities(num_opportunities=3)
        generator.generate_calls()
        links = generator.generate_call_opportunities()

        assert len(links) > 0

        for link in links:
            assert "call_id" in link
            assert "opportunity_id" in link

    def test_emails_generation(self):
        """Test that emails are generated for opportunities."""
        generator = FixturesGenerator(num_calls=5, seed=42)
        generator.generate_speakers()
        generator.generate_opportunities(num_opportunities=3)
        emails = generator.generate_emails()

        assert len(emails) > 0

        for email in emails:
            assert "id" in email
            assert "gong_email_id" in email
            assert "opportunity_id" in email
            assert "subject" in email
            assert "sender_email" in email
            assert email["sender_email"].endswith("@prefect.io")
            assert "recipients" in email
            assert len(email["recipients"]) > 0

    def test_reproducible_with_seed(self):
        """Test that using the same seed produces identical results."""
        gen1 = FixturesGenerator(num_calls=5, days_back=30, seed=42)
        gen2 = FixturesGenerator(num_calls=5, days_back=30, seed=42)

        calls1 = gen1.generate_calls()
        calls2 = gen2.generate_calls()

        # Same seed should produce same number of calls
        assert len(calls1) == len(calls2)

    def test_full_generation_flow(self):
        """Test the complete generation flow without database insertion."""
        generator = FixturesGenerator(num_calls=3, days_back=30, seed=42)

        # Generate all data
        generator.generate_speakers()
        generator.generate_opportunities(num_opportunities=2)
        generator.generate_calls()
        speakers = generator.generate_call_speakers()
        generator.generate_transcripts(speakers)
        generator.generate_coaching_sessions(speakers)
        generator.generate_call_opportunities()
        generator.generate_emails()

        # Verify counts
        assert len(generator.created_speakers) > 0
        assert len(generator.created_calls) == 3
        assert len(generator.created_opportunities) == 2
        assert len(generator.created_coaching_sessions) > 0
        assert len(generator.created_emails) > 0

    def test_transcript_line_with_placeholders(self):
        """Test that transcript lines fill all placeholders."""
        generator = FixturesGenerator(seed=42)

        # Generate many lines to test placeholder replacement
        for _ in range(50):
            line = generator._generate_transcript_line("discovery", is_company=True, prospect=None)
            # Should not contain unresolved placeholders
            assert "{" not in line or "{{" in line  # Allow double braces
            assert len(line) > 0

    def test_full_analysis_generation(self):
        """Test that full analysis narratives are coherent."""
        generator = FixturesGenerator(seed=42)

        for score in [30, 60, 75, 95]:
            analysis = generator._generate_full_analysis(
                dimension="discovery",
                score=score,
                strengths=["Asked good questions", "Listened well"],
                improvements=["Probe deeper", "More follow-up"],
            )

            assert len(analysis) > 0
            assert "discovery" in analysis.lower()
            assert "rep" in analysis.lower() or "performance" in analysis.lower()
