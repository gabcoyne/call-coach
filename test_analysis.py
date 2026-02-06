"""
Quick test script for Claude API analysis integration.
Tests the analysis engine with a sample transcript.
"""

import logging

from analysis.engine import _generate_prompt_for_dimension, _run_claude_analysis
from db import fetch_one
from db.models import CoachingDimension

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def test_prompt_generation():
    """Test that prompt generation works for each dimension."""
    logger.info("Testing prompt generation for all dimensions...")

    sample_transcript = """
    Rep: Hi John, thanks for taking the time today. I know you mentioned your team
    is spending a lot of time maintaining Airflow - can you walk me through what
    that looks like day-to-day?

    Customer: Yeah, it's become a real problem. We have about 500 DAGs running, and
    our data engineers spend probably 40% of their time just debugging scheduler
    issues and handling failed jobs.

    Rep: 40% - that's significant. What impact is that having on your roadmap?

    Customer: Well, we have three major projects on hold right now because we just
    don't have the bandwidth. Our VP of Engineering is getting frustrated.

    Rep: I understand. When you think about fixing this problem, what would success
    look like for your team?

    Customer: Honestly, we just want our engineers focused on building data products
    instead of firefighting infrastructure. If we could get that 40% back, we could
    probably ship 2-3 major features per quarter instead of just 1.
    """

    call_metadata = {
        "title": "Acme Corp - Discovery Call",
        "duration_seconds": 1800,
        "call_type": "discovery",
    }

    for dimension in CoachingDimension:
        logger.info(f"\n{'='*60}")
        logger.info(f"Testing dimension: {dimension.value}")
        logger.info(f"{'='*60}")

        try:
            # Get rubric
            rubric_row = fetch_one(
                """
                SELECT name, version, category, criteria, scoring_guide, examples
                FROM coaching_rubrics
                WHERE category = %s AND active = true
                LIMIT 1
                """,
                (dimension.value,),
            )

            if not rubric_row:
                logger.warning(f"No rubric found for {dimension.value}, skipping")
                continue

            rubric = {
                "name": rubric_row["name"],
                "version": rubric_row["version"],
                "category": rubric_row["category"],
                "criteria": rubric_row["criteria"],
                "scoring_guide": rubric_row["scoring_guide"],
                "examples": rubric_row.get("examples", {}),
            }

            # Generate prompt
            knowledge_base = (
                "Sample product knowledge"
                if dimension == CoachingDimension.PRODUCT_KNOWLEDGE
                else None
            )
            messages = _generate_prompt_for_dimension(
                dimension=dimension,
                transcript=sample_transcript,
                rubric=rubric,
                knowledge_base=knowledge_base,
                call_metadata=call_metadata,
            )

            logger.info("✓ Prompt generated successfully")
            logger.info(f"  - Message count: {len(messages)}")
            logger.info(f"  - Content blocks: {len(messages[0]['content'])}")

            # Check for cache control
            has_cache_control = any("cache_control" in block for block in messages[0]["content"])
            logger.info(f"  - Has cache control: {has_cache_control}")

        except Exception as e:
            logger.error(f"✗ Failed to generate prompt: {e}")


def test_claude_analysis():
    """Test actual Claude API call with discovery dimension."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing actual Claude API call (discovery dimension)")
    logger.info("=" * 60)

    sample_transcript = """
    Rep: Hi Sarah, thanks for joining today. I reviewed your responses from the form -
    it sounds like your team is spending a lot of cycles on Airflow maintenance.
    Can you paint a picture of what that looks like week to week?

    Customer: Yeah, it's gotten pretty bad. We have about 800 workflows across
    different business units. Our platform team - which is 5 engineers - probably
    spends 50-60% of their time just keeping things running. Scheduler crashes,
    debugging failed DAGs, managing infrastructure upgrades.

    Rep: Wow, 50-60% on maintenance for a 5-person team. That's basically 2.5-3
    full-time engineers just firefighting. What are they not able to work on
    because of that?

    Customer: Great question. We have a whole backlog of strategic initiatives.
    Real-time data pipelines, ML feature engineering, data quality framework.
    Our CTO has been asking about these for 6 months and we keep pushing them out.

    Rep: Got it. When you think about fixing this problem - either with Prefect
    or another solution - what metrics would tell you it's working?

    Customer: I'd want to see our maintenance time drop to under 20%. And we should
    be able to ship at least 2 major initiatives per quarter. Right now we're lucky
    to ship 1.

    Rep: That makes sense. Walk me through your evaluation process - who else needs
    to be involved in a decision like this?

    Customer: Well, I own the budget for the data platform. But I'd want buy-in from
    our InfoSec team - we're SOC 2 compliant so they'll need to review any new tools.
    And our VP of Engineering will want to understand the business case.

    Rep: Makes sense. What's your timeline looking like for making a decision?

    Customer: We're planning our Q2 roadmap in about 3 weeks. If we can get through
    security review and build a solid business case, I'd want to start migrating
    some workloads in Q2.
    """

    call_metadata = {
        "title": "DataCo - Discovery Call with Sarah Chen",
        "duration_seconds": 2100,
        "call_type": "discovery",
    }

    try:
        result = _run_claude_analysis(
            dimension=CoachingDimension.DISCOVERY,
            transcript=sample_transcript,
            call_metadata=call_metadata,
        )

        logger.info("✓ Claude API call successful!")
        logger.info(f"\n{'='*60}")
        logger.info("ANALYSIS RESULTS:")
        logger.info(f"{'='*60}")
        logger.info(f"Score: {result.get('score')}/100")
        logger.info(f"\nStrengths ({len(result.get('strengths', []))}):")
        for strength in result.get("strengths", [])[:3]:
            logger.info(f"  - {strength}")

        logger.info(f"\nAreas for Improvement ({len(result.get('areas_for_improvement', []))}):")
        for area in result.get("areas_for_improvement", [])[:3]:
            logger.info(f"  - {area}")

        logger.info(f"\nAction Items ({len(result.get('action_items', []))}):")
        for item in result.get("action_items", [])[:3]:
            logger.info(f"  - {item}")

        # Token usage
        metadata = result.get("metadata", {})
        logger.info(f"\n{'='*60}")
        logger.info("TOKEN USAGE:")
        logger.info(f"{'='*60}")
        logger.info(f"Model: {metadata.get('model')}")
        logger.info(f"Total tokens: {metadata.get('tokens_used')}")
        logger.info(f"Input tokens: {metadata.get('input_tokens')}")
        logger.info(f"Output tokens: {metadata.get('output_tokens')}")
        logger.info(f"Cache creation tokens: {metadata.get('cache_creation_tokens')}")
        logger.info(f"Cache read tokens: {metadata.get('cache_read_tokens')}")

        # 5 Wins coverage
        if "five_wins_coverage" in result:
            wins = result["five_wins_coverage"]
            logger.info(f"\n{'='*60}")
            logger.info("5 WINS COVERAGE:")
            logger.info(f"{'='*60}")
            logger.info(f"Wins count: {wins.get('wins_count')}/5")
            for win_name, win_data in wins.items():
                if win_name not in ["wins_count", "overall_assessment"] and isinstance(
                    win_data, dict
                ):
                    covered = "✓" if win_data.get("covered") else "✗"
                    score = win_data.get("score", 0)
                    logger.info(f"{covered} {win_name}: {score}/100")

        return result

    except Exception as e:
        logger.error(f"✗ Claude API call failed: {e}")
        raise


if __name__ == "__main__":
    # Test prompt generation first
    test_prompt_generation()

    # Then test actual Claude API call
    # NOTE: This will consume API tokens!
    user_input = input("\n\nTest actual Claude API call? This will use API tokens. (y/N): ")
    if user_input.lower() == "y":
        test_claude_analysis()
    else:
        logger.info("Skipping actual API call test.")
