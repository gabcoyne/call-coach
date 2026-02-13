#!/usr/bin/env python
"""
Migration Script for Five Wins Unified Pipeline

This script manages the transition from the legacy analysis pipeline
to the Five Wins Unified pipeline.

Usage:
    # Check current status
    uv run python scripts/migrate_to_five_wins.py status

    # Enable A/B testing at 10%
    uv run python scripts/migrate_to_five_wins.py enable-ab-test --percentage 10

    # Enable unified pipeline for all calls
    uv run python scripts/migrate_to_five_wins.py enable

    # Rollback to legacy pipeline
    uv run python scripts/migrate_to_five_wins.py rollback

    # View A/B test results
    uv run python scripts/migrate_to_five_wins.py ab-summary
"""

import argparse
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def get_current_status() -> dict:
    """Get current pipeline configuration status."""
    from coaching_mcp.shared import settings

    return {
        "use_five_wins_unified": settings.use_five_wins_unified,
        "ab_testing_enabled": os.getenv("FIVE_WINS_AB_TESTING_ENABLED", "false").lower() == "true",
        "rollout_percentage": int(os.getenv("FIVE_WINS_UNIFIED_ROLLOUT_PCT", "0")),
        "unified_enabled_globally": os.getenv("FIVE_WINS_UNIFIED_ENABLED", "false").lower()
        == "true",
    }


def print_status():
    """Print current pipeline configuration."""
    status = get_current_status()

    print("\n=== Five Wins Pipeline Status ===\n")
    print(f"Settings.use_five_wins_unified: {status['use_five_wins_unified']}")
    print(f"FIVE_WINS_UNIFIED_ENABLED:      {status['unified_enabled_globally']}")
    print(f"FIVE_WINS_AB_TESTING_ENABLED:   {status['ab_testing_enabled']}")
    print(f"FIVE_WINS_UNIFIED_ROLLOUT_PCT:  {status['rollout_percentage']}%")

    print("\n--- Current Behavior ---")
    if status["unified_enabled_globally"] or status["use_five_wins_unified"]:
        print("✅ Unified pipeline is ACTIVE for all calls")
    elif status["ab_testing_enabled"]:
        print(f"🔄 A/B testing is active at {status['rollout_percentage']}% rollout")
    else:
        print("⬜ Legacy pipeline is active for all calls")

    print()


def enable_ab_test(percentage: int):
    """Enable A/B testing with specified percentage."""
    if not 1 <= percentage <= 100:
        print(f"Error: Percentage must be between 1 and 100, got {percentage}")
        sys.exit(1)

    print(f"\n=== Enabling A/B Testing at {percentage}% ===\n")
    print("To enable A/B testing, set the following environment variables:\n")
    print("  export FIVE_WINS_AB_TESTING_ENABLED=true")
    print(f"  export FIVE_WINS_UNIFIED_ROLLOUT_PCT={percentage}")
    print("  export FIVE_WINS_UNIFIED_ENABLED=false")
    print()
    print("For Horizon deployment, add these to your environment configuration.")
    print()

    # Validate the pipeline before recommending
    _validate_pipeline()


def enable_unified():
    """Enable unified pipeline for all calls."""
    print("\n=== Enabling Unified Pipeline ===\n")
    print("To enable the unified pipeline for ALL calls, set:\n")
    print("  export FIVE_WINS_UNIFIED_ENABLED=true")
    print()
    print("Or set USE_FIVE_WINS_UNIFIED=true in your .env file.")
    print()

    # Validate the pipeline before recommending
    _validate_pipeline()


def rollback():
    """Rollback to legacy pipeline."""
    print("\n=== Rolling Back to Legacy Pipeline ===\n")
    print("To disable the unified pipeline, set:\n")
    print("  export FIVE_WINS_UNIFIED_ENABLED=false")
    print("  export FIVE_WINS_AB_TESTING_ENABLED=false")
    print("  export FIVE_WINS_UNIFIED_ROLLOUT_PCT=0")
    print()
    print("Or set USE_FIVE_WINS_UNIFIED=false in your .env file.")
    print()


def show_ab_summary(days: int = 7):
    """Show A/B test summary."""
    print(f"\n=== A/B Test Summary (Last {days} Days) ===\n")

    try:
        from analysis.ab_testing import get_ab_test_summary

        summary = get_ab_test_summary(days)

        if "error" in summary:
            print(f"Error retrieving summary: {summary['error']}")
            return

        if not summary.get("pipelines"):
            print("No A/B test data found. Enable A/B testing to start collecting data.")
            return

        # Print comparison table
        pipelines = summary["pipelines"]

        print(f"{'Metric':<25} {'Legacy':<15} {'Unified':<15}")
        print("-" * 55)

        metrics = [
            ("Call Count", "call_count"),
            ("Avg Score", "avg_score"),
            ("Avg Wins Secured", "avg_wins_secured"),
            ("Avg Action Items", "avg_action_items"),
            ("Avg Tokens", "avg_tokens"),
            ("Avg Duration (ms)", "avg_duration_ms"),
            ("Narrative Rate (%)", "narrative_rate"),
            ("Primary Action Rate (%)", "primary_action_rate"),
        ]

        legacy = pipelines.get("legacy", {})
        unified = pipelines.get("unified", {})

        for label, key in metrics:
            legacy_val = legacy.get(key, "N/A")
            unified_val = unified.get(key, "N/A")
            print(f"{label:<25} {str(legacy_val):<15} {str(unified_val):<15}")

        print()

    except ImportError as e:
        print(f"Could not import ab_testing module: {e}")
        print("Make sure you're running from the project root.")


def _validate_pipeline():
    """Validate that the Five Wins Unified pipeline is working."""
    print("Validating pipeline components...")

    try:
        # Import all required modules
        from analysis.consolidation import generate_narrative, select_primary_action
        from analysis.prompts.five_wins_prompt import analyze_five_wins_prompt

        print("  ✓ Prompt module imported")
        print("  ✓ Consolidation layer imported")
        print("  ✓ Pydantic models imported")
        print("  ✓ Rubric definitions imported")

        # Test prompt generation
        messages = analyze_five_wins_prompt(
            transcript="Test transcript",
            call_type="discovery",
        )
        assert len(messages) == 1, "Prompt should produce 1 message"
        print("  ✓ Prompt generation working")

        # Test consolidation layer
        test_eval = {
            "business": {"score": 50, "blockers": []},
            "technical": {"score": 40, "blockers": []},
            "security": {"score": 30, "blockers": []},
            "commercial": {"score": 20, "blockers": []},
            "legal": {"score": 10, "blockers": []},
        }
        narrative = generate_narrative(test_eval, "discovery")
        assert len(narrative) > 0, "Narrative should not be empty"
        print("  ✓ Narrative generation working")

        action = select_primary_action(test_eval, "discovery", [])
        assert action.win in ["business", "technical", "security", "commercial", "legal"]
        print("  ✓ Action selection working")

        print("\n✅ All validations passed! Pipeline is ready for deployment.\n")

    except Exception as e:
        print(f"\n❌ Validation failed: {e}")
        print("Fix the issues above before enabling the unified pipeline.\n")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Manage Five Wins Unified Pipeline migration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # status command
    subparsers.add_parser("status", help="Show current pipeline configuration")

    # enable-ab-test command
    ab_parser = subparsers.add_parser("enable-ab-test", help="Enable A/B testing")
    ab_parser.add_argument(
        "--percentage",
        "-p",
        type=int,
        default=10,
        help="Percentage of calls to route to unified pipeline (default: 10)",
    )

    # enable command
    subparsers.add_parser("enable", help="Enable unified pipeline for all calls")

    # rollback command
    subparsers.add_parser("rollback", help="Rollback to legacy pipeline")

    # ab-summary command
    summary_parser = subparsers.add_parser("ab-summary", help="Show A/B test summary")
    summary_parser.add_argument(
        "--days", "-d", type=int, default=7, help="Number of days to look back (default: 7)"
    )

    # validate command
    subparsers.add_parser("validate", help="Validate pipeline components")

    args = parser.parse_args()

    if args.command == "status":
        print_status()
    elif args.command == "enable-ab-test":
        enable_ab_test(args.percentage)
    elif args.command == "enable":
        enable_unified()
    elif args.command == "rollback":
        rollback()
    elif args.command == "ab-summary":
        show_ab_summary(args.days)
    elif args.command == "validate":
        _validate_pipeline()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
