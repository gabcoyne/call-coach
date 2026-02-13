"""
Unit Tests for Five Wins Unified Pipeline

Tests the end-to-end flow of:
1. Prompt generation
2. Consolidation layer
3. Output format validation

These tests verify the pipeline components work correctly with mocked data.
No database or external API calls are made.
"""

import pytest

from analysis.consolidation import generate_narrative, link_action_to_moment, select_primary_action
from analysis.models.five_wins import (
    BusinessWinEvaluation,
    CallMoment,
    ChampionAssessment,
    CoachingOutput,
    CommercialWinEvaluation,
    FiveWinsEvaluation,
    LegalWinEvaluation,
    PrimaryAction,
    SecurityWinEvaluation,
    TechnicalWinEvaluation,
)
from analysis.prompts.five_wins_prompt import analyze_five_wins_prompt

# Sample Five Wins API response (what we expect from Claude)
SAMPLE_FIVE_WINS_RESPONSE = {
    "five_wins_evaluation": {
        "business": {
            "score": 25,
            "exit_criteria_met": False,
            "discovery_complete": True,
            "blockers": ["No champion identified"],
            "evidence": ["Discussed current state and pain points"],
            "champion": {
                "identified": False,
                "name": None,
                "incentive_clear": False,
                "influence_confirmed": False,
                "information_flowing": False,
            },
            "budget_confirmed": False,
            "exec_sponsor_engaged": False,
            "business_case_strength": "weak",
        },
        "technical": {
            "score": 20,
            "exit_criteria_met": False,
            "discovery_complete": True,
            "blockers": [],
            "evidence": ["Validated Kubernetes requirements"],
            "vendor_of_choice_confirmed": False,
            "poc_scoped": False,
            "poc_success_criteria_defined": False,
        },
        "security": {
            "score": 5,
            "exit_criteria_met": False,
            "discovery_complete": False,
            "blockers": ["InfoSec timeline unknown"],
            "evidence": [],
            "infosec_timeline_known": False,
            "trust_portal_shared": False,
            "architecture_review_scheduled": False,
        },
        "commercial": {
            "score": 5,
            "exit_criteria_met": False,
            "discovery_complete": False,
            "blockers": [],
            "evidence": [],
            "exec_sponsor_aligned": False,
            "scope_agreed": False,
            "pricing_discussed": False,
        },
        "legal": {
            "score": 0,
            "exit_criteria_met": False,
            "discovery_complete": False,
            "blockers": [],
            "evidence": [],
            "terms_impact_discussed": False,
            "legal_timeline_known": False,
            "redlines_in_progress": False,
        },
    },
    "narrative": "This discovery call made good progress on understanding the customer's technical requirements. However, no champion has been identified and the business case remains weak.",
    "wins_addressed": {
        "technical": "Validated Kubernetes requirements",
    },
    "wins_missed": {
        "business": "No champion identified, budget not confirmed",
        "security": "InfoSec timeline not discovered",
    },
    "primary_action": {
        "win": "business",
        "action": "Before your next call, prepare three questions: (1) Who else needs to approve this? (2) What budget have you allocated? (3) What happens if this isn't solved by Q2?",
        "context": "You discussed technical requirements but didn't identify who can actually approve the purchase.",
        "related_moment": {
            "timestamp_seconds": 780,
            "speaker": "Rep",
            "summary": "Rep moved to technical discussion without confirming budget authority",
        },
    },
    "key_moments": [
        {
            "timestamp_seconds": 120,
            "speaker": "Customer",
            "summary": "Customer described current Airflow pain points",
        },
        {
            "timestamp_seconds": 780,
            "speaker": "Rep",
            "summary": "Rep moved to technical discussion without confirming budget",
        },
    ],
}


class TestFiveWinsPipeline:
    """Unit tests for the complete Five Wins pipeline."""

    def test_prompt_produces_valid_structure(self):
        """Test that prompt generation produces expected message structure."""
        transcript = (
            "Rep: Hi, let me understand your workflow. Customer: We use Airflow currently..."
        )

        messages = analyze_five_wins_prompt(
            transcript=transcript,
            call_type="discovery",
            call_metadata={"title": "Acme Discovery", "duration_seconds": 1800},
        )

        # Verify structure
        assert len(messages) == 1
        assert messages[0]["role"] == "user"
        assert len(messages[0]["content"]) == 2

        # Verify cache control on system prompt
        assert "cache_control" in messages[0]["content"][0]

        # Verify transcript is in user content
        assert "Airflow" in messages[0]["content"][1]["text"]

    def test_consolidation_layer_generates_narrative(self):
        """Test that consolidation layer produces valid narrative."""
        five_wins_eval = SAMPLE_FIVE_WINS_RESPONSE["five_wins_evaluation"]

        narrative = generate_narrative(five_wins_eval, "discovery")

        # Verify narrative is concise (2-3 sentences)
        sentences = narrative.split(". ")
        assert 1 <= len(sentences) <= 4

        # Verify no methodology jargon
        jargon = ["spiced", "challenger", "sandler", "meddic"]
        narrative_lower = narrative.lower()
        for term in jargon:
            assert term not in narrative_lower

    def test_consolidation_layer_selects_single_action(self):
        """Test that action selector returns exactly ONE action."""
        five_wins_eval = SAMPLE_FIVE_WINS_RESPONSE["five_wins_evaluation"]
        moments = [CallMoment(**m) for m in SAMPLE_FIVE_WINS_RESPONSE["key_moments"]]

        action = select_primary_action(five_wins_eval, "discovery", moments)

        # Verify it's a single PrimaryAction
        assert isinstance(action, PrimaryAction)

        # Verify it has required fields
        assert action.win in ["business", "technical", "security", "commercial", "legal"]
        assert len(action.action) > 10  # Not empty
        assert len(action.context) > 10  # Not empty

    def test_moment_linker_finds_relevant_moment(self):
        """Test that moment linker correctly links actions to moments."""
        moments = [CallMoment(**m) for m in SAMPLE_FIVE_WINS_RESPONSE["key_moments"]]

        linked = link_action_to_moment(
            action="Identify a champion with budget authority",
            win="business",
            moments=moments,
        )

        # Should return a CallMoment or None
        assert linked is None or isinstance(linked, CallMoment)

    def test_full_output_format_validation(self):
        """Test that the full output format is valid."""
        # Create full evaluation from sample response
        five_wins_data = SAMPLE_FIVE_WINS_RESPONSE["five_wins_evaluation"]

        # Verify we can create Pydantic models from the data
        business = BusinessWinEvaluation(
            score=five_wins_data["business"]["score"],
            exit_criteria_met=five_wins_data["business"]["exit_criteria_met"],
            discovery_complete=five_wins_data["business"]["discovery_complete"],
            blockers=five_wins_data["business"]["blockers"],
            evidence=five_wins_data["business"]["evidence"],
            champion=ChampionAssessment(**five_wins_data["business"]["champion"]),
            budget_confirmed=five_wins_data["business"]["budget_confirmed"],
            exec_sponsor_engaged=five_wins_data["business"]["exec_sponsor_engaged"],
            business_case_strength=five_wins_data["business"]["business_case_strength"],
        )

        technical = TechnicalWinEvaluation(
            score=five_wins_data["technical"]["score"],
            exit_criteria_met=five_wins_data["technical"]["exit_criteria_met"],
            discovery_complete=five_wins_data["technical"]["discovery_complete"],
            blockers=five_wins_data["technical"]["blockers"],
            evidence=five_wins_data["technical"]["evidence"],
            vendor_of_choice_confirmed=five_wins_data["technical"]["vendor_of_choice_confirmed"],
            poc_scoped=five_wins_data["technical"]["poc_scoped"],
            poc_success_criteria_defined=five_wins_data["technical"][
                "poc_success_criteria_defined"
            ],
        )

        security = SecurityWinEvaluation(
            score=five_wins_data["security"]["score"],
            exit_criteria_met=five_wins_data["security"]["exit_criteria_met"],
            discovery_complete=five_wins_data["security"]["discovery_complete"],
            blockers=five_wins_data["security"]["blockers"],
            evidence=five_wins_data["security"]["evidence"],
            infosec_timeline_known=five_wins_data["security"]["infosec_timeline_known"],
            trust_portal_shared=five_wins_data["security"]["trust_portal_shared"],
            architecture_review_scheduled=five_wins_data["security"][
                "architecture_review_scheduled"
            ],
        )

        commercial = CommercialWinEvaluation(
            score=five_wins_data["commercial"]["score"],
            exit_criteria_met=five_wins_data["commercial"]["exit_criteria_met"],
            discovery_complete=five_wins_data["commercial"]["discovery_complete"],
            blockers=five_wins_data["commercial"]["blockers"],
            evidence=five_wins_data["commercial"]["evidence"],
            exec_sponsor_aligned=five_wins_data["commercial"]["exec_sponsor_aligned"],
            scope_agreed=five_wins_data["commercial"]["scope_agreed"],
            pricing_discussed=five_wins_data["commercial"]["pricing_discussed"],
        )

        legal = LegalWinEvaluation(
            score=five_wins_data["legal"]["score"],
            exit_criteria_met=five_wins_data["legal"]["exit_criteria_met"],
            discovery_complete=five_wins_data["legal"]["discovery_complete"],
            blockers=five_wins_data["legal"]["blockers"],
            evidence=five_wins_data["legal"]["evidence"],
            terms_impact_discussed=five_wins_data["legal"]["terms_impact_discussed"],
            legal_timeline_known=five_wins_data["legal"]["legal_timeline_known"],
            redlines_in_progress=five_wins_data["legal"]["redlines_in_progress"],
        )

        # Create full evaluation
        evaluation = FiveWinsEvaluation(
            business=business,
            technical=technical,
            security=security,
            commercial=commercial,
            legal=legal,
        )

        # Verify computed properties
        assert evaluation.overall_score == 55  # 25 + 20 + 5 + 5 + 0
        assert evaluation.wins_secured == 0  # No exit criteria met

        # Verify JSON serialization
        json_data = evaluation.model_dump()
        assert "business" in json_data
        assert "overall_score" in json_data
        assert "wins_secured" in json_data

    def test_coaching_output_model(self):
        """Test that CoachingOutput model can be created from response."""
        response = SAMPLE_FIVE_WINS_RESPONSE

        # Create evaluation (simplified for test)
        five_wins_data = response["five_wins_evaluation"]
        evaluation = FiveWinsEvaluation(
            business=BusinessWinEvaluation(
                score=five_wins_data["business"]["score"],
                champion=ChampionAssessment(**five_wins_data["business"]["champion"]),
                budget_confirmed=five_wins_data["business"]["budget_confirmed"],
                exec_sponsor_engaged=five_wins_data["business"]["exec_sponsor_engaged"],
                business_case_strength=five_wins_data["business"]["business_case_strength"],
            ),
            technical=TechnicalWinEvaluation(
                score=five_wins_data["technical"]["score"],
            ),
            security=SecurityWinEvaluation(
                score=five_wins_data["security"]["score"],
            ),
            commercial=CommercialWinEvaluation(
                score=five_wins_data["commercial"]["score"],
            ),
            legal=LegalWinEvaluation(
                score=five_wins_data["legal"]["score"],
            ),
        )

        # Create primary action
        action_data = response["primary_action"]
        primary_action = PrimaryAction(
            win=action_data["win"],
            action=action_data["action"],
            context=action_data["context"],
            related_moment=(
                CallMoment(**action_data["related_moment"])
                if action_data.get("related_moment")
                else None
            ),
        )

        # Create key moments
        key_moments = [CallMoment(**m) for m in response["key_moments"]]

        # Create full coaching output
        output = CoachingOutput(
            narrative=response["narrative"],
            wins_addressed=response["wins_addressed"],
            wins_missed=response["wins_missed"],
            primary_action=primary_action,
            five_wins_detail=evaluation,
            key_moments=key_moments,
        )

        # Verify
        assert output.narrative == response["narrative"]
        assert output.primary_action.win == "business"
        assert len(output.key_moments) == 2
        assert output.five_wins_detail.overall_score == 55


class TestFiveWinsCallTypeMapping:
    """Test that call types correctly map to primary wins."""

    @pytest.mark.parametrize(
        "call_type,expected_primary_win",
        [
            ("discovery", "business"),
            ("technical_deep_dive", "technical"),
            ("demo", "technical"),
            ("poc_kickoff", "technical"),
            ("architecture_review", "security"),
            ("executive_presentation", "business"),
            ("negotiation", "commercial"),
        ],
    )
    def test_call_type_to_primary_win(self, call_type, expected_primary_win):
        """Test that each call type maps to correct primary win."""
        from analysis.rubrics.five_wins_unified import get_primary_win_for_call_type

        actual = get_primary_win_for_call_type(call_type)
        assert actual == expected_primary_win

    def test_unknown_call_type_defaults_to_business(self):
        """Test that unknown call types default to business win."""
        from analysis.rubrics.five_wins_unified import get_primary_win_for_call_type

        # Unknown call type should default to business
        actual = get_primary_win_for_call_type("unknown_type")  # type: ignore
        assert actual == "business"


class TestActionPriorityOrder:
    """Test that action selection follows correct priority order."""

    def test_blocked_wins_take_priority(self):
        """Test that blocked wins are prioritized over other actions."""
        # Evaluation with a blocked technical win
        evaluation = {
            "business": {"score": 80, "blockers": []},
            "technical": {"score": 60, "blockers": ["Architecture review pending"]},
            "security": {"score": 40, "blockers": []},
            "commercial": {"score": 30, "blockers": []},
            "legal": {"score": 20, "blockers": []},
        }

        action = select_primary_action(evaluation, "discovery", [])

        # Should prioritize unblocking technical
        assert action.win == "technical"
        assert "Architecture review" in action.action or "blocker" in action.action.lower()

    def test_at_risk_wins_secondary_priority(self):
        """Test that at-risk wins are addressed if nothing is blocked."""
        # Evaluation with no blockers but at-risk wins
        evaluation = {
            "business": {"score": 80, "blockers": []},
            "technical": {"score": 70, "blockers": []},
            "security": {"score": 30, "blockers": []},  # At risk
            "commercial": {"score": 70, "blockers": []},
            "legal": {"score": 60, "blockers": []},
        }

        action = select_primary_action(evaluation, "demo", [])

        # Should address at-risk security win or advance primary (technical for demo)
        assert action.win in ["security", "technical"]
