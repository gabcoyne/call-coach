"""
Tests for rubric modules.

Verifies rubric definitions are valid and sum to 100 points.
"""

import pytest

from analysis.rubrics import (
    DISCOVERY_RUBRIC,
    ENGAGEMENT_RUBRIC,
    FIVE_WINS_RUBRIC,
    OBJECTION_HANDLING_RUBRIC,
    PRODUCT_KNOWLEDGE_RUBRIC,
    get_rubric_for_dimension,
)


def test_discovery_rubric_structure():
    """Test discovery rubric has correct structure."""
    assert isinstance(DISCOVERY_RUBRIC, dict)
    assert len(DISCOVERY_RUBRIC) == 8  # 8 criteria

    # Verify each criterion has required fields
    for criterion in DISCOVERY_RUBRIC.values():
        assert "name" in criterion
        assert "description" in criterion
        assert "max_score" in criterion
        assert "criteria" in criterion
        assert isinstance(criterion["criteria"], list)
        assert len(criterion["criteria"]) > 0


def test_discovery_rubric_totals_100():
    """Test discovery rubric scores sum to 100."""
    total = sum(criterion["max_score"] for criterion in DISCOVERY_RUBRIC.values())
    assert total == 100, f"Discovery rubric must total 100 points, got {total}"


def test_discovery_rubric_criteria():
    """Test discovery rubric has expected criteria."""
    expected_criteria = {
        "opening_questions",
        "situation_exploration",
        "pain_identification",
        "impact_quantification",
        "critical_event",
        "decision_process",
        "budget_exploration",
        "success_criteria",
    }
    assert set(DISCOVERY_RUBRIC.keys()) == expected_criteria


def test_engagement_rubric_structure():
    """Test engagement rubric has correct structure."""
    assert isinstance(ENGAGEMENT_RUBRIC, dict)
    assert len(ENGAGEMENT_RUBRIC) == 7  # 7 criteria

    # Verify each criterion has required fields
    for criterion in ENGAGEMENT_RUBRIC.values():
        assert "name" in criterion
        assert "description" in criterion
        assert "max_score" in criterion
        assert "criteria" in criterion
        assert isinstance(criterion["criteria"], list)
        assert len(criterion["criteria"]) > 0


def test_engagement_rubric_totals_100():
    """Test engagement rubric scores sum to 100."""
    total = sum(criterion["max_score"] for criterion in ENGAGEMENT_RUBRIC.values())
    assert total == 100, f"Engagement rubric must total 100 points, got {total}"


def test_engagement_rubric_criteria():
    """Test engagement rubric has expected criteria."""
    expected_criteria = {
        "talk_listen_ratio",
        "active_listening",
        "rapport_building",
        "energy_enthusiasm",
        "empathy_validation",
        "customer_centricity",
        "engagement_checks",
    }
    assert set(ENGAGEMENT_RUBRIC.keys()) == expected_criteria


def test_get_rubric_for_dimension_discovery():
    """Test get_rubric_for_dimension returns discovery rubric."""
    rubric = get_rubric_for_dimension("discovery")
    assert rubric == DISCOVERY_RUBRIC


def test_get_rubric_for_dimension_engagement():
    """Test get_rubric_for_dimension returns engagement rubric."""
    rubric = get_rubric_for_dimension("engagement")
    assert rubric == ENGAGEMENT_RUBRIC


def test_get_rubric_for_dimension_invalid():
    """Test get_rubric_for_dimension raises error for invalid dimension."""
    with pytest.raises(ValueError) as exc_info:
        get_rubric_for_dimension("invalid_dimension")

    assert "No rubric defined for dimension 'invalid_dimension'" in str(exc_info.value)
    assert "Available:" in str(exc_info.value)


def test_get_rubric_for_dimension_case_sensitive():
    """Test get_rubric_for_dimension is case-sensitive."""
    with pytest.raises(ValueError):
        get_rubric_for_dimension("Discovery")  # Should be lowercase


def test_rubric_criterion_types():
    """Test rubric criteria have correct types."""
    for criterion in DISCOVERY_RUBRIC.values():
        assert isinstance(criterion["name"], str)
        assert isinstance(criterion["description"], str)
        assert isinstance(criterion["max_score"], int)
        assert criterion["max_score"] > 0
        assert isinstance(criterion["criteria"], list)
        assert all(isinstance(c, str) for c in criterion["criteria"])

    for criterion in ENGAGEMENT_RUBRIC.values():
        assert isinstance(criterion["name"], str)
        assert isinstance(criterion["description"], str)
        assert isinstance(criterion["max_score"], int)
        assert criterion["max_score"] > 0
        assert isinstance(criterion["criteria"], list)
        assert all(isinstance(c, str) for c in criterion["criteria"])


def test_rubric_max_scores_reasonable():
    """Test rubric max scores are reasonable (5-20 points each)."""
    for criterion in DISCOVERY_RUBRIC.values():
        assert 5 <= criterion["max_score"] <= 20, (
            f"Discovery criterion max_score should be 5-20, "
            f"got {criterion['max_score']} for {criterion['name']}"
        )

    for criterion in ENGAGEMENT_RUBRIC.values():
        assert 5 <= criterion["max_score"] <= 20, (
            f"Engagement criterion max_score should be 5-20, "
            f"got {criterion['max_score']} for {criterion['name']}"
        )


# Five Wins Rubric Tests


def test_five_wins_rubric_structure():
    """Test Five Wins rubric has correct structure."""
    assert isinstance(FIVE_WINS_RUBRIC, dict)
    assert len(FIVE_WINS_RUBRIC) == 5  # 5 wins

    # Verify each win has required fields
    for win in FIVE_WINS_RUBRIC.values():
        assert "name" in win
        assert "description" in win
        assert "max_score" in win
        assert "criteria" in win
        assert isinstance(win["criteria"], list)
        assert len(win["criteria"]) > 0


def test_five_wins_rubric_totals_100():
    """Test Five Wins rubric scores sum to 100."""
    total = sum(win["max_score"] for win in FIVE_WINS_RUBRIC.values())
    assert total == 100, f"Five Wins rubric must total 100 points, got {total}"


def test_five_wins_rubric_wins():
    """Test Five Wins rubric has expected wins."""
    expected_wins = {
        "business_win",
        "technical_win",
        "security_win",
        "commercial_win",
        "legal_win",
    }
    assert set(FIVE_WINS_RUBRIC.keys()) == expected_wins


def test_five_wins_importance_ordering():
    """Test Five Wins are ordered by importance (business > technical > others)."""
    assert FIVE_WINS_RUBRIC["business_win"]["max_score"] == 35  # Most important
    assert FIVE_WINS_RUBRIC["technical_win"]["max_score"] == 25  # Second
    assert FIVE_WINS_RUBRIC["security_win"]["max_score"] == 15
    assert FIVE_WINS_RUBRIC["commercial_win"]["max_score"] == 15
    assert FIVE_WINS_RUBRIC["legal_win"]["max_score"] == 10  # Least points


def test_get_rubric_for_dimension_five_wins():
    """Test get_rubric_for_dimension returns Five Wins rubric."""
    rubric = get_rubric_for_dimension("five_wins")
    assert rubric == FIVE_WINS_RUBRIC


def test_five_wins_rubric_types():
    """Test Five Wins rubric criteria have correct types."""
    for win in FIVE_WINS_RUBRIC.values():
        assert isinstance(win["name"], str)
        assert isinstance(win["description"], str)
        assert isinstance(win["max_score"], int)
        assert win["max_score"] > 0
        assert isinstance(win["criteria"], list)
        assert all(isinstance(c, str) for c in win["criteria"])


# Product Knowledge Rubric Tests


def test_product_knowledge_rubric_structure():
    """Test Product Knowledge rubric has correct structure."""
    assert isinstance(PRODUCT_KNOWLEDGE_RUBRIC, dict)
    assert len(PRODUCT_KNOWLEDGE_RUBRIC) == 7  # 7 criteria

    # Verify each criterion has required fields
    for criterion in PRODUCT_KNOWLEDGE_RUBRIC.values():
        assert "name" in criterion
        assert "description" in criterion
        assert "max_score" in criterion
        assert "criteria" in criterion
        assert isinstance(criterion["criteria"], list)
        assert len(criterion["criteria"]) > 0


def test_product_knowledge_rubric_totals_100():
    """Test Product Knowledge rubric scores sum to 100."""
    total = sum(criterion["max_score"] for criterion in PRODUCT_KNOWLEDGE_RUBRIC.values())
    assert total == 100, f"Product Knowledge rubric must total 100 points, got {total}"


def test_product_knowledge_rubric_criteria():
    """Test Product Knowledge rubric has expected criteria."""
    expected_criteria = {
        "solution_positioning",
        "feature_knowledge",
        "technical_depth",
        "demo_execution",
        "competitive_awareness",
        "use_case_examples",
        "limits_and_gaps",
    }
    assert set(PRODUCT_KNOWLEDGE_RUBRIC.keys()) == expected_criteria


def test_get_rubric_for_dimension_product_knowledge():
    """Test get_rubric_for_dimension returns Product Knowledge rubric."""
    rubric = get_rubric_for_dimension("product_knowledge")
    assert rubric == PRODUCT_KNOWLEDGE_RUBRIC


def test_product_knowledge_rubric_types():
    """Test Product Knowledge rubric criteria have correct types."""
    for criterion in PRODUCT_KNOWLEDGE_RUBRIC.values():
        assert isinstance(criterion["name"], str)
        assert isinstance(criterion["description"], str)
        assert isinstance(criterion["max_score"], int)
        assert criterion["max_score"] > 0
        assert isinstance(criterion["criteria"], list)
        assert all(isinstance(c, str) for c in criterion["criteria"])


def test_product_knowledge_importance_ordering():
    """Test Product Knowledge top criteria have reasonable scores."""
    # Solution positioning and feature knowledge should be highest
    assert PRODUCT_KNOWLEDGE_RUBRIC["solution_positioning"]["max_score"] == 20
    assert PRODUCT_KNOWLEDGE_RUBRIC["feature_knowledge"]["max_score"] == 20

    # All criteria should be between 10-20 points
    for criterion in PRODUCT_KNOWLEDGE_RUBRIC.values():
        assert 10 <= criterion["max_score"] <= 20, (
            f"Product Knowledge criterion max_score should be 10-20, "
            f"got {criterion['max_score']} for {criterion['name']}"
        )


# Objection Handling Rubric Tests


def test_objection_handling_rubric_structure():
    """Test Objection Handling rubric has correct structure."""
    assert isinstance(OBJECTION_HANDLING_RUBRIC, dict)
    assert len(OBJECTION_HANDLING_RUBRIC) == 6  # 6 criteria

    # Verify each criterion has required fields
    for criterion in OBJECTION_HANDLING_RUBRIC.values():
        assert "name" in criterion
        assert "description" in criterion
        assert "max_score" in criterion
        assert "criteria" in criterion
        assert isinstance(criterion["criteria"], list)
        assert len(criterion["criteria"]) > 0


def test_objection_handling_rubric_totals_100():
    """Test Objection Handling rubric scores sum to 100."""
    total = sum(criterion["max_score"] for criterion in OBJECTION_HANDLING_RUBRIC.values())
    assert total == 100, f"Objection Handling rubric must total 100 points, got {total}"


def test_objection_handling_rubric_criteria():
    """Test Objection Handling rubric has expected criteria."""
    expected_criteria = {
        "objection_identification",
        "understanding_root_cause",
        "empathy_and_validation",
        "reframing_response",
        "confirmation_and_resolution",
        "handling_difficult_objections",
    }
    assert set(OBJECTION_HANDLING_RUBRIC.keys()) == expected_criteria


def test_get_rubric_for_dimension_objection_handling():
    """Test get_rubric_for_dimension returns Objection Handling rubric."""
    rubric = get_rubric_for_dimension("objection_handling")
    assert rubric == OBJECTION_HANDLING_RUBRIC


def test_objection_handling_rubric_types():
    """Test Objection Handling rubric criteria have correct types."""
    for criterion in OBJECTION_HANDLING_RUBRIC.values():
        assert isinstance(criterion["name"], str)
        assert isinstance(criterion["description"], str)
        assert isinstance(criterion["max_score"], int)
        assert criterion["max_score"] > 0
        assert isinstance(criterion["criteria"], list)
        assert all(isinstance(c, str) for c in criterion["criteria"])


def test_objection_handling_importance_ordering():
    """Test Objection Handling top criterion is reframing_response."""
    assert OBJECTION_HANDLING_RUBRIC["reframing_response"]["max_score"] == 25  # Most important
    assert OBJECTION_HANDLING_RUBRIC["understanding_root_cause"]["max_score"] == 20

    # All criteria should be between 10-25 points
    for criterion in OBJECTION_HANDLING_RUBRIC.values():
        assert 10 <= criterion["max_score"] <= 25, (
            f"Objection Handling criterion max_score should be 10-25, "
            f"got {criterion['max_score']} for {criterion['name']}"
        )
